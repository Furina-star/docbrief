"""Streams structured document summaries from the Google Gemini API."""

from collections.abc import Iterator

from google import genai
from google.genai import types

from extractor import DocumentData

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


# Stream Markdown analysis chunks from Google Gemini for the given document.
def stream_analysis(
    doc: DocumentData, api_key: str, model: str = DEFAULT_MODEL
) -> Iterator[str]:
    cleaned_key = api_key.strip()
    if not cleaned_key:
        raise AnalysisError(
            "Missing Gemini API key. Add GEMINI_API_KEY to .env or paste it in the sidebar."
        )

    client = genai.Client(
        api_key=cleaned_key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
    )

    try:
        response = client.models.generate_content_stream(
            model=model,
            contents=build_prompt(doc),
            config=config,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as exc:
        message = str(exc)
        lower = message.lower()
        if "429" in lower or "quota" in lower or "resource_exhausted" in lower:
            raise AnalysisError(
                "Gemini free-tier rate limit reached. Wait a moment or switch to gemini-3.5-flash-lite."
            ) from exc
        if "503" in lower or "unavailable" in lower:
            raise AnalysisError(
                "Gemini is temporarily busy (503). Retry in a few seconds or switch to gemini-3.5-flash-lite."
            ) from exc
        if "401" in lower or "403" in lower or "api_key_invalid" in lower or "api key" in lower:
            raise AnalysisError(
                "Gemini API key was rejected. Check that your key is valid in Google AI Studio."
            ) from exc
        raise AnalysisError(f"Gemini request failed: {message}") from exc
