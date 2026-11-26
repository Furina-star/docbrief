"""Streams structured document summaries from the Google Gemini API."""

from collections.abc import Iterator
import logging

from google import genai
from google.genai import types

from extractor import DocumentData

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"
AVAILABLE_MODELS = ("gemini-2.5-flash", "gemini-3.5-flash-lite")
MAX_INPUT_CHARS = 400_000

SYSTEM_INSTRUCTION = """You are a sharp, concise document reader.
Analyze the provided document and respond in clean Markdown with these exact sections in order:

1. Start immediately with a blockquote TL;DR (2-3 crisp sentences):
> **TL;DR:** ...

2. `## Summary`
A clear, well-structured breakdown of the document's core ideas, findings, or arguments.

3. `## Key Terms`
A bullet list of the most important terms, concepts, or acronyms from the document using `- **Term** — short plain definition`.

4. `## Citations`
ONLY include this section if the document actually contains citations, references, footnotes, or bibliographic sources. List them cleanly. If the document has no citations, omit the `## Citations` heading and section completely.

Do not add conversational filler, greetings, or closing remarks."""


class AnalysisError(Exception):
    """Raised when the Gemini API cannot complete document analysis."""


# Build the user prompt from extracted document metadata and bounded text.
def build_prompt(doc: DocumentData) -> str:
    body = doc.text
    if len(body) > MAX_INPUT_CHARS:
        body = body[:MAX_INPUT_CHARS] + "\n\n[Document truncated to fit context limit.]"
    return f"Document title: {doc.title}\n\n{body}"


# Return True when an error is a temporary quota or capacity limit worth retrying elsewhere.
def _is_retryable(message: str) -> bool:
    lower = message.lower()
    return any(
        marker in lower
        for marker in ("429", "quota", "resource_exhausted", "503", "unavailable")
    )


# Convert a raw Gemini exception into a user-friendly AnalysisError.
def _to_analysis_error(exc: Exception) -> AnalysisError:
    lower = str(exc).lower()
    if "429" in lower or "quota" in lower or "resource_exhausted" in lower:
        return AnalysisError(
            "Too many requests right now. Please wait a moment and try again."
        )
    if "503" in lower or "unavailable" in lower:
        return AnalysisError(
            "Service is temporarily busy. Please try again in a few seconds."
        )
    if "401" in lower or "403" in lower or "api_key_invalid" in lower or "api key" in lower:
        return AnalysisError("Service configuration error. Please try again later.")
    return AnalysisError("Could not analyze this document right now. Please try again.")


# Stream Markdown analysis from Gemini, falling back to the other model when rate limited.
def stream_analysis(
    doc: DocumentData, api_key: str, model: str = DEFAULT_MODEL
) -> Iterator[str]:
    cleaned_key = api_key.strip()
    if not cleaned_key:
        raise AnalysisError(
            "Docbrief is not configured yet. Please try again later."
        )

    client = genai.Client(
        api_key=cleaned_key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
    )
    prompt = build_prompt(doc)
    models = [model] + [m for m in AVAILABLE_MODELS if m != model]

    for index, current_model in enumerate(models):
        started = False
        try:
            response = client.models.generate_content_stream(
                model=current_model,
                contents=prompt,
                config=config,
            )
            for chunk in response:
                if chunk.text:
                    started = True
                    yield chunk.text
            return
        except Exception as exc:
            logger.error("Gemini stream failed (%s): %s", current_model, exc)
            has_fallback = index < len(models) - 1
            # Only switch models if nothing was shown yet; a half-written brief can't be resumed.
            if has_fallback and not started and _is_retryable(str(exc)):
                logger.warning("Falling back from %s to %s", current_model, models[index + 1])
                continue
            raise _to_analysis_error(exc) from exc
