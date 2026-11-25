"""Provides JetBrains Nerd Font Mono typography and mobile-responsive CSS for Streamlit."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --font-mono: "JetBrainsMono Nerd Font", "JetBrains Mono", monospace;
    --border-subtle: #27272a;
    --surface-muted: #161618;
    --text-muted: #a1a1aa;
}

/* Apply JetBrains Mono stack without overriding Streamlit's Material icon font. */
html, body,
[data-testid="stMarkdownContainer"],
[data-testid="stCaptionContainer"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] button,
.stTextInput input,
.stSelectbox div,
.stButton button,
.stDownloadButton button,
h1, h2, h3, h4, p, li, blockquote, code, pre {
    font-family: var(--font-mono) !important;
}

/* Keep the main reading sheet narrow and comfortable on desktop. */
.block-container {
    max-width: 780px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border-subtle);
}

/* Style the TL;DR blockquote as a crisp flat callout box. */
[data-testid="stMarkdownContainer"] blockquote {
    border-left: 3px solid #e5e5e5;
    background-color: var(--surface-muted);
    padding: 0.9rem 1.1rem;
    margin: 1.1rem 0 1.5rem 0;
    border-radius: 6px;
    color: #f4f4f5;
}

[data-testid="stMarkdownContainer"] h2 {
    margin-top: 1.75rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 1.15rem;
}

[data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.65;
}

.docbrief-meta {
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
}

/* Adapt spacing, font size, and controls cleanly for mobile screens. */
@media (max-width: 768px) {
    .block-container {
        max-width: 100% !important;
        padding: 1.5rem 1rem 3rem 1rem !important;
    }

    h1 {
        font-size: 1.35rem !important;
    }

    [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.05rem !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        font-size: 0.92rem !important;
    }

    .stButton button,
    .stDownloadButton button {
        width: 100% !important;
    }
}
</style>
"""


# Return the full custom stylesheet for injection into the Streamlit app.
def get_custom_css() -> str:
    return CUSTOM_CSS
