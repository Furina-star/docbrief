"""Unit tests for document and URL text extraction."""

import io
from unittest.mock import Mock, patch

import docx
import pymupdf
import pytest

from extractor import DocumentData, ExtractionError, extract_from_bytes, extract_from_url


# Build an in-memory PDF with optional text for testing PDF extraction.
def _make_pdf_bytes(text: str = "") -> bytes:
    pdf = pymupdf.open()
    page = pdf.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = pdf.tobytes()
    pdf.close()
    return data


# Build an in-memory DOCX containing both a paragraph and a table.
def _make_docx_bytes(paragraph: str, cell_text: str) -> bytes:
    document = docx.Document()
    document.add_paragraph(paragraph)
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = cell_text
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


# Verify plain text files are decoded and word stats are calculated.
def test_extract_txt_bytes():
    raw = b"Neural networks learn layered representations from raw data."
    doc = extract_from_bytes("notes.txt", raw)

    assert isinstance(doc, DocumentData)
    assert doc.title == "notes.txt"
    assert "Neural networks" in doc.text
    assert doc.pages is None
    assert doc.words == 8
    assert doc.read_minutes == 1


# Verify PDF extraction reads page text and reports page count.
def test_extract_pdf_bytes():
    pdf_bytes = _make_pdf_bytes("Attention is all you need for sequence modeling.")
    doc = extract_from_bytes("paper.pdf", pdf_bytes)

    assert doc.title == "paper.pdf"
    assert "Attention is all you need" in doc.text
    assert doc.pages == 1
    assert doc.words >= 7


# Verify blank or scanned image-only PDFs raise a helpful ExtractionError.
def test_extract_empty_pdf_raises():
    blank_pdf = _make_pdf_bytes("")

    with pytest.raises(ExtractionError, match="(?i)empty|scanned|no readable text"):
        extract_from_bytes("scan.pdf", blank_pdf)


# Verify DOCX extraction captures both body paragraphs and table cells.
def test_extract_docx_bytes():
    docx_bytes = _make_docx_bytes("Quarterly revenue grew 18 percent.", "Region: APAC")
    doc = extract_from_bytes("report.docx", docx_bytes)

    assert "Quarterly revenue grew 18 percent." in doc.text
    assert "Region: APAC" in doc.text
    assert doc.pages is None


# Verify unsupported file extensions are rejected cleanly.
def test_extract_unsupported_extension_raises():
    with pytest.raises(ExtractionError, match="(?i)unsupported"):
        extract_from_bytes("archive.zip", b"PK\x03\x04")


# Verify non-HTTP(S) URLs are rejected to block local file reads.
def test_extract_url_rejects_non_http_scheme():
    with pytest.raises(ExtractionError, match="(?i)http"):
        extract_from_url("file:///etc/passwd")


# Verify HTML pages strip scripts and navigation while keeping main article text.
def test_extract_url_html_strips_noise():
    html = (
        "<html><head><title>Fast Python</title><script>alert(1)</script></head>"
        "<body><nav>Home About</nav>"
        "<article><h1>Fast Python</h1><p>Keep modules small and clear.</p></article>"
        "<footer>Copyright</footer></body></html>"
    ).encode("utf-8")
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "text/html; charset=utf-8"}
    response.content = html
    response.raise_for_status = Mock()

    with patch("extractor.httpx.get", return_value=response):
        doc = extract_from_url("https://example.com/fast-python")

    assert doc.title == "Fast Python"
    assert "Keep modules small and clear." in doc.text
    assert "alert(1)" not in doc.text
    assert "Home About" not in doc.text


# Verify URLs serving PDF content route through the PDF extractor.
def test_extract_url_remote_pdf():
    pdf_bytes = _make_pdf_bytes("Remote PDF content with citation [1].")
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "application/pdf"}
    response.content = pdf_bytes
    response.raise_for_status = Mock()

    with patch("extractor.httpx.get", return_value=response):
        doc = extract_from_url("https://example.com/files/study.pdf")

    assert doc.title == "study.pdf"
    assert "Remote PDF content" in doc.text
    assert doc.pages == 1


# Verify oversized remote responses are rejected before parsing.
def test_extract_url_oversized_raises():
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "text/plain"}
    response.content = b"a" * 100
    response.raise_for_status = Mock()

    with patch("extractor.httpx.get", return_value=response):
        with pytest.raises(ExtractionError, match="(?i)too large|size"):
            extract_from_url("https://example.com/huge.txt", max_bytes=50)
