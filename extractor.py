"""Extracts readable text and basic metadata from uploaded files and URLs."""

from dataclasses import dataclass
import io
from pathlib import Path
import re
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
import docx
import httpx
import pymupdf

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".markdown", ".csv"}
WORDS_PER_MINUTE = 220


class ExtractionError(Exception):
    """Raised when a document or URL cannot be fetched or parsed."""


@dataclass(frozen=True)
class DocumentData:
    title: str
    source: str
    text: str
    pages: int | None
    words: int
    read_minutes: int


# Normalize whitespace, verify non-empty content, and compute reading stats.
def _build_document(
    title: str, source: str, raw_text: str, pages: int | None = None
) -> DocumentData:
    cleaned = re.sub(r"\n{3,}", "\n\n", raw_text).strip()
    if not cleaned:
        raise ExtractionError(
            "Document appears empty or scanned (no readable text found)."
        )
    words = len(cleaned.split())
    read_minutes = max(1, round(words / WORDS_PER_MINUTE))
    return DocumentData(
        title=title,
        source=source,
        text=cleaned,
        pages=pages,
        words=words,
        read_minutes=read_minutes,
    )


# Extract text across all pages of an in-memory PDF document.
def _extract_pdf(data: bytes) -> tuple[str, int]:
    try:
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            page_count = len(pdf)
            chunks = [page.get_text("text").strip() for page in pdf]
    except Exception as exc:
        raise ExtractionError(f"Could not read PDF file: {exc}") from exc
    return "\n\n".join(c for c in chunks if c), page_count


# Extract paragraphs and table cells from an in-memory DOCX file.
def _extract_docx(data: bytes) -> str:
    try:
        document = docx.Document(io.BytesIO(data))
    except Exception as exc:
        raise ExtractionError(f"Could not read DOCX file: {exc}") from exc

    parts = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                parts.append(" | ".join(cells))
    return "\n\n".join(parts)


# Strip scripts, styles, and navigation chrome from HTML to keep main readable text.
def _extract_html(data: bytes, fallback_title: str) -> tuple[str, str]:
    soup = BeautifulSoup(data, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else fallback_title

    for tag in soup(["script", "style", "noscript", "nav", "header", "footer", "aside"]):
        tag.decompose()

    container = soup.find("article") or soup.find("main") or soup.body or soup
    lines = [line.strip() for line in container.get_text("\n").splitlines() if line.strip()]
    return title or fallback_title, "\n".join(lines)


# Route uploaded file bytes to the appropriate parser by extension.
def extract_from_bytes(
    filename: str, data: bytes, source: str = "upload"
) -> DocumentData:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(
            f"Unsupported file format '{ext or 'unknown'}'. Use PDF, DOCX, TXT, or MD."
        )

    if ext == ".pdf":
        text, pages = _extract_pdf(data)
        return _build_document(filename, source, text, pages=pages)
    if ext == ".docx":
        text = _extract_docx(data)
        return _build_document(filename, source, text)

    text = data.decode("utf-8", errors="replace")
    return _build_document(filename, source, text)


# Fetch an HTTP(S) URL and extract text from remote PDFs, DOCX files, or web pages.
def extract_from_url(
    url: str, timeout: float = 15.0, max_bytes: int = 20 * 1024 * 1024
) -> DocumentData:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ExtractionError("Enter a valid http:// or https:// URL.")

    try:
        response = httpx.get(
            url.strip(),
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "docbrief/1.0"},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ExtractionError(f"Failed to fetch URL: {exc}") from exc

    content = response.content
    if len(content) > max_bytes:
        raise ExtractionError(
            f"Remote file is too large (limit: {max_bytes // (1024 * 1024)} MB)."
        )

    content_type = response.headers.get("content-type", "").lower()
    path_name = unquote(Path(parsed.path).name) or parsed.netloc

    # Detect remote binary document types before falling back to HTML or plain text.
    if "application/pdf" in content_type or path_name.lower().endswith(".pdf"):
        text, pages = _extract_pdf(content)
        return _build_document(path_name, url.strip(), text, pages=pages)

    if (
        "wordprocessingml" in content_type
        or path_name.lower().endswith(".docx")
    ):
        text = _extract_docx(content)
        return _build_document(path_name, url.strip(), text)

    if "text/html" in content_type or "application/xhtml" in content_type:
        title, text = _extract_html(content, fallback_title=path_name)
        return _build_document(title, url.strip(), text)

    text = content.decode("utf-8", errors="replace")
    return _build_document(path_name, url.strip(), text)
