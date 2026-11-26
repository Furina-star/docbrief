"""Unit tests for the Gemini streaming document analyzer."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from analyzer import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    AnalysisError,
    build_prompt,
    stream_analysis,
)
from extractor import DocumentData


# Create a small sample document fixture for analyzer tests.
def _sample_doc() -> DocumentData:
    return DocumentData(
        title="transformer_notes.pdf",
        source="upload",
        text="Self-attention relates different positions of a single sequence [1].",
        pages=2,
        words=10,
        read_minutes=1,
    )


# Verify the prompt embeds the document title and body text.
def test_build_prompt_includes_title_and_text():
    doc = _sample_doc()
    prompt = build_prompt(doc)

    assert "transformer_notes.pdf" in prompt
    assert "Self-attention relates different positions" in prompt


# Verify missing or blank API keys raise an actionable AnalysisError.
def test_stream_analysis_requires_api_key():
    doc = _sample_doc()

    with pytest.raises(AnalysisError, match="(?i)not configured"):
        list(stream_analysis(doc, api_key="   "))


# Verify streaming yields only non-empty text chunks from the Gemini response.
def test_stream_analysis_yields_text_chunks():
    doc = _sample_doc()
    fake_chunks = [
        SimpleNamespace(text="> **TL;DR:** "),
        SimpleNamespace(text=None),
        SimpleNamespace(text="Self-attention links tokens."),
    ]
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = iter(fake_chunks)

    with patch("analyzer.genai.Client", return_value=mock_client):
        chunks = list(stream_analysis(doc, api_key="test-key", model=DEFAULT_MODEL))

    assert chunks == ["> **TL;DR:** ", "Self-attention links tokens."]
    assert DEFAULT_MODEL in AVAILABLE_MODELS


# Verify rate limit errors from Gemini are wrapped with a clear message.
def test_stream_analysis_wraps_rate_limit_error():
    doc = _sample_doc()
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.side_effect = RuntimeError(
        "429 RESOURCE_EXHAUSTED: quota exceeded"
    )

    with patch("analyzer.genai.Client", return_value=mock_client):
        with pytest.raises(AnalysisError, match="(?i)too many requests"):
            list(stream_analysis(doc, api_key="test-key"))


# Verify non-auth INVALID_ARGUMENT errors are not misreported as bad API keys.
def test_stream_analysis_does_not_misclassify_invalid_argument_as_auth():
    doc = _sample_doc()
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.side_effect = RuntimeError(
        "400 INVALID_ARGUMENT: bad request payload"
    )

    with patch("analyzer.genai.Client", return_value=mock_client):
        with pytest.raises(AnalysisError, match="(?i)could not analyze"):
            list(stream_analysis(doc, api_key="test-key"))


# Verify a rate-limited model falls back to the next available model.
def test_stream_analysis_falls_back_to_other_model_on_rate_limit():
    doc = _sample_doc()
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.side_effect = [
        RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded"),
        iter([SimpleNamespace(text="> **TL;DR:** From the fallback model.")]),
    ]

    with patch("analyzer.genai.Client", return_value=mock_client):
        chunks = list(stream_analysis(doc, api_key="test-key", model=DEFAULT_MODEL))

    assert chunks == ["> **TL;DR:** From the fallback model."]
    called_models = [
        call.kwargs["model"]
        for call in mock_client.models.generate_content_stream.call_args_list
    ]
    assert called_models == [DEFAULT_MODEL, "gemini-3.5-flash-lite"]


# Verify non-retryable errors fail immediately without trying another model.
def test_stream_analysis_does_not_fall_back_on_non_retryable_error():
    doc = _sample_doc()
    mock_client = MagicMock()
    mock_client.models.generate_content_stream.side_effect = RuntimeError(
        "400 INVALID_ARGUMENT: bad request payload"
    )

    with patch("analyzer.genai.Client", return_value=mock_client):
        with pytest.raises(AnalysisError, match="(?i)could not analyze"):
            list(stream_analysis(doc, api_key="test-key"))

    assert mock_client.models.generate_content_stream.call_count == 1


# Verify a failure after text was already streamed is reported instead of switching models.
def test_stream_analysis_does_not_fall_back_mid_stream():
    doc = _sample_doc()

    def broken_stream():
        yield SimpleNamespace(text="> **TL;DR:** Partial")
        raise RuntimeError("503 UNAVAILABLE")

    mock_client = MagicMock()
    mock_client.models.generate_content_stream.return_value = broken_stream()

    with patch("analyzer.genai.Client", return_value=mock_client):
        with pytest.raises(AnalysisError, match="(?i)temporarily busy"):
            list(stream_analysis(doc, api_key="test-key"))

    assert mock_client.models.generate_content_stream.call_count == 1
