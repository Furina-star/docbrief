"""Streamlit web interface for uploading or fetching documents and streaming briefs."""

import os
from pathlib import Path
import re

from dotenv import load_dotenv
import streamlit as st

from analyzer import AVAILABLE_MODELS, DEFAULT_MODEL, AnalysisError, stream_analysis
from extractor import DocumentData, ExtractionError, extract_from_bytes, extract_from_url
from keywords import bag_of_words_text, keywords_markdown, tfidf_markdown
from styles import get_custom_css

load_dotenv()


# Read a setting from Streamlit secrets first, then fall back to environment variables.
def _get_setting(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    except Exception:
        pass
    return os.getenv(name, default).strip()


# Cache file parsing so Streamlit reruns do not re-parse the same upload.
@st.cache_data(show_spinner=False)
def _load_uploaded_file(filename: str, raw_bytes: bytes) -> DocumentData:
    return extract_from_bytes(filename, raw_bytes)


# Cache URL fetching and extraction so reruns do not re-download remote pages.
@st.cache_data(show_spinner=False)
def _load_url(url: str) -> DocumentData:
    return extract_from_url(url)


# Format compact document metadata for display in the header and sidebar.
def _format_stats(doc: DocumentData) -> str:
    parts = []
    if doc.pages is not None:
        unit = "pg" if doc.pages == 1 else "pgs"
        parts.append(f"{doc.pages} {unit}")
    parts.append(f"{doc.words:,} words")
    parts.append(f"~{doc.read_minutes} min read")
    return " · ".join(parts)


# Build a clean filename for downloading the generated Markdown brief.
def _export_filename(title: str) -> str:
    stem = Path(title).stem or "document"
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-").lower()
    return f"{safe or 'document'}-brief.md"


# Render the sidebar controls and return the user's current input selections.
def _render_sidebar() -> tuple[str, object, str, bool, bool]:
    with st.sidebar:
        st.markdown("### Docbrief")
        st.caption("TL;DR, summary, key terms & citations.")

        mode = st.radio(
            "Input source",
            ["Upload", "URL"],
            horizontal=True,
            label_visibility="collapsed",
        )

        uploaded_file = None
        url_input = ""
        if mode == "Upload":
            uploaded_file = st.file_uploader(
                "Drop a document",
                type=["pdf", "docx", "txt", "md", "markdown", "csv"],
                label_visibility="collapsed",
            )
        else:
            url_input = st.text_input(
                "Document or article URL",
                placeholder="https://example.com/document.pdf",
                label_visibility="collapsed",
            )

        analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

        current_doc: DocumentData | None = st.session_state.get("doc")
        if current_doc is not None:
            st.divider()
            st.caption(_format_stats(current_doc))

        st.divider()
        light_mode = st.toggle("Light mode", value=False)

    return mode, uploaded_file, url_input, analyze_clicked, light_mode


# Render the reading sheet header, Markdown brief, download button, and raw text toggle.
def _render_result(doc: DocumentData, markdown_output: str) -> None:
    st.markdown(f"# {doc.title}")
    st.markdown(
        f'<div class="docbrief-meta">{_format_stats(doc)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(markdown_output)
    _render_keywords_and_export(doc, markdown_output)


# Render the keyword frequency and TF-IDF tables, download button, and source/bag-of-words toggles.
def _render_keywords_and_export(doc: DocumentData, markdown_output: str) -> None:
    keywords_md = "\n\n".join(
        section for section in (keywords_markdown(doc.text), tfidf_markdown(doc.text)) if section
    )
    if keywords_md:
        st.markdown(keywords_md)
    st.divider()
    export = f"# {doc.title}\n\n{markdown_output}\n"
    if keywords_md:
        export += f"\n{keywords_md}\n"
    st.download_button(
        "Download .md",
        data=export,
        file_name=_export_filename(doc.title),
        mime="text/markdown",
    )
    if keywords_md:
        with st.expander("Bag of words"):
            st.text(bag_of_words_text(doc.text))
    with st.expander("Extracted source text"):
        st.text(doc.text)


# Entry point for configuring the Streamlit page and handling analysis runs.
def main() -> None:
    st.set_page_config(
        page_title="Docbrief",
        page_icon="📄",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    mode, uploaded_file, url_input, analyze_clicked, light_mode = _render_sidebar()
    st.markdown(get_custom_css(light_mode=light_mode), unsafe_allow_html=True)
    api_key = _get_setting("GEMINI_API_KEY")
    configured_model = _get_setting("GEMINI_MODEL", DEFAULT_MODEL)
    model = configured_model if configured_model in AVAILABLE_MODELS else DEFAULT_MODEL

    if analyze_clicked:
        try:
            with st.spinner("Reading document..."):
                if mode == "Upload":
                    if uploaded_file is None:
                        raise ExtractionError("Upload a PDF, DOCX, TXT, or MD file first.")
                    doc = _load_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
                else:
                    if not url_input.strip():
                        raise ExtractionError("Paste a URL first.")
                    doc = _load_url(url_input.strip())

            st.markdown(f"# {doc.title}")
            st.markdown(
                f'<div class="docbrief-meta">{_format_stats(doc)}</div>',
                unsafe_allow_html=True,
            )
            result = st.write_stream(stream_analysis(doc, api_key=api_key, model=model))
            st.session_state["doc"] = doc
            st.session_state["result"] = result
            _render_keywords_and_export(doc, result)
            return
        except (ExtractionError, AnalysisError) as exc:
            st.error(str(exc))
            return

    if "doc" in st.session_state and "result" in st.session_state:
        _render_result(st.session_state["doc"], st.session_state["result"])
    else:
        st.markdown("# Docbrief")
        st.markdown(
            "Upload a **PDF, DOCX, TXT, or Markdown** file or paste a **URL** "
            "in the sidebar to get a TL;DR, summary, key terms, and citations."
        )
        st.caption(
            "On mobile, tap the top-left arrow to open the sidebar."
        )


if __name__ == "__main__":
    main()
