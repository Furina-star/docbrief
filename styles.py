"""Provides JetBrains Nerd Font Mono typography, light/dark themes, and mobile CSS."""

DARK_VARS = """
    --bg: #0f0f10;
    --surface: #161618;
    --term-bg: #111113;
    --term-bar: #1b1b1f;
    --text: #ececee;
    --text-muted: #a1a1aa;
    --border-subtle: #27272a;
    --accent: #e5e5e5;
    --btn-bg: #e5e5e5;
    --btn-text: #0f0f10;
    --btn-hover: #ffffff;
"""

LIGHT_VARS = """
    --bg: #fafafa;
    --surface: #f0f0f2;
    --term-bg: #f4f4f5;
    --term-bar: #e4e4e7;
    --text: #18181b;
    --text-muted: #52525b;
    --border-subtle: #d4d4d8;
    --accent: #18181b;
    --btn-bg: #18181b;
    --btn-text: #fafafa;
    --btn-hover: #27272a;
"""

# Light mode only: repaint Streamlit's built-in widgets, which otherwise keep the dark base theme.
LIGHT_OVERRIDES = """
[data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Header, toolbar, and sidebar open/close icons. */
[data-testid="stHeader"] button,
[data-testid="stHeader"] a,
[data-testid="stHeader"] span,
[data-testid="stToolbar"] *,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] *,
[data-testid="stSidebarCollapsedControl"] *,
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] * {
    color: var(--text) !important;
}

/* Error messages: readable dark red text on a soft red panel. */
[data-testid="stAlertContainer"] {
    background-color: #fdecec !important;
    border: 1px solid #f5c2c2 !important;
}

[data-testid="stAlertContainer"] p,
[data-testid="stAlertContainer"] span,
[data-testid="stAlertContainer"] div {
    color: #8f1d1d !important;
}

/* Radio buttons: dark ring for the selected option, outlined circle otherwise. */
[data-testid="stRadioOption"] > div > div:first-child {
    background-color: var(--bg) !important;
    border: 1px solid var(--text-muted) !important;
}

[data-testid="stRadioOption"] > div > div:first-child > div {
    background-color: var(--bg) !important;
}

[data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* Toggle switch: dark track when on, grey track when off. */
[data-testid="stCheckbox"] label > div:first-of-type {
    background-color: var(--border-subtle) !important;
}

[data-testid="stCheckbox"] label > div:first-of-type > div {
    background-color: #ffffff !important;
}

[data-testid="stCheckbox"][data-selected="true"] label > div:first-of-type {
    background-color: var(--accent) !important;
}

/* Dividers. */
hr {
    border-color: var(--border-subtle) !important;
}

/* Uploaded file chip. */
[data-testid="stFileChip"] {
    background-color: var(--bg) !important;
    border: 1px solid var(--border-subtle) !important;
}

[data-testid="stFileChip"] > div:first-child {
    background-color: var(--term-bar) !important;
}

[data-testid="stFileChip"],
[data-testid="stFileChip"] *,
[data-testid="stFileChipName"] {
    color: var(--text) !important;
}

[data-testid="stFileChipDeleteBtn"] *,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploaderDropzone"] span {
    color: var(--text-muted) !important;
}

/* Expanders ("Bag of words", "Extracted source text"). */
[data-testid="stExpander"] details {
    border-color: var(--border-subtle) !important;
    background-color: var(--bg) !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:hover,
[data-testid="stExpander"] summary:focus {
    background-color: var(--surface) !important;
    color: var(--text) !important;
}

[data-testid="stExpander"] summary *,
[data-testid="stText"],
[data-testid="stText"] * {
    color: var(--text) !important;
}

[data-testid="stExpanderDetails"] {
    border-color: var(--border-subtle) !important;
}

/* URL text box. */
[data-baseweb="input"],
[data-baseweb="base-input"] {
    background-color: var(--bg) !important;
    border-color: var(--border-subtle) !important;
}

.stTextInput input::placeholder {
    color: var(--text-muted) !important;
}

/* Inline code and code blocks inside the brief. */
[data-testid="stMarkdownContainer"] code,
[data-testid="stMarkdownContainer"] pre,
[data-testid="stCode"] pre {
    background-color: var(--term-bg) !important;
    color: var(--text) !important;
}

/* Loading spinner text. */
[data-testid="stSpinner"] * {
    color: var(--text-muted) !important;
}
"""

CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {{
    --font-mono: "JetBrainsMono Nerd Font", "JetBrains Mono", monospace;
    {theme_vars}
}}

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
h1, h2, h3, h4, p, li, blockquote, code, pre {{
    font-family: var(--font-mono) !important;
}}

/* Apply active theme surfaces and text across the main sheet and sidebar. */
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
}}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border-subtle);
    color: var(--text) !important;
}}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{
    color: var(--text);
}}

[data-testid="stCaptionContainer"] p {{
    color: var(--text-muted) !important;
}}

.stTextInput input,
[data-testid="stFileUploaderDropzone"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    border-color: var(--border-subtle) !important;
}}

/* Keep primary action button text crisp and legible in both themes. */
button[kind="primary"],
button[kind="primary"] p,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] p {{
    background-color: var(--btn-bg) !important;
    border-color: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    font-weight: 600 !important;
}}

button[kind="primary"]:hover,
button[kind="primary"]:hover p,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover p {{
    background-color: var(--btn-hover) !important;
    border-color: var(--btn-hover) !important;
    color: var(--btn-text) !important;
}}

button[kind="secondary"],
[data-testid="stBaseButton-secondary"],
.stDownloadButton button {{
    background-color: var(--surface) !important;
    border-color: var(--border-subtle) !important;
    color: var(--text) !important;
}}

/* Keep the main reading sheet narrow and comfortable on desktop. */
.block-container {{
    max-width: 780px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}}

/* Style the TL;DR blockquote as a sharp TUI panel with a top-border legend. */
[data-testid="stMarkdownContainer"] blockquote {{
    position: relative;
    border: 1px solid var(--border-subtle);
    border-left: 1px solid var(--border-subtle);
    border-radius: 0;
    background-color: var(--bg);
    padding: 1.15rem 1.2rem 1rem 1.2rem;
    margin: 1.4rem 0 1.6rem 0;
    overflow: visible;
    color: var(--text);
}}

[data-testid="stMarkdownContainer"] blockquote::before {{
    content: "[ TL;DR ]";
    position: absolute;
    top: -0.68rem;
    left: 0.85rem;
    background-color: var(--bg);
    padding: 0 0.45rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: var(--accent);
}}

[data-testid="stMarkdownContainer"] blockquote p {{
    margin: 0;
}}

[data-testid="stMarkdownContainer"] blockquote strong {{
    color: var(--accent);
}}

[data-testid="stMarkdownContainer"] h2 {{
    margin-top: 1.75rem;
    padding-bottom: 0.35rem;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 1.15rem;
}}

/* Style the keyword frequency table with the same sharp, bordered TUI look. */
[data-testid="stMarkdownContainer"] table {{
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--border-subtle);
    font-size: 0.88rem;
}}

[data-testid="stMarkdownContainer"] th,
[data-testid="stMarkdownContainer"] td {{
    border: 1px solid var(--border-subtle) !important;
    padding: 0.35rem 0.7rem;
    color: var(--text);
    background-color: var(--bg);
}}

[data-testid="stMarkdownContainer"] th {{
    color: var(--accent);
    font-weight: 600;
    background-color: var(--surface);
}}

[data-testid="stMarkdownContainer"] {{
    overflow-wrap: anywhere;
    word-break: break-word;
    line-height: 1.65;
}}

.docbrief-meta {{
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-bottom: 1.25rem;
}}

/* Adapt spacing, font size, and controls cleanly for mobile screens. */
@media (max-width: 768px) {{
    .block-container {{
        max-width: 100% !important;
        padding: 1.5rem 1rem 3rem 1rem !important;
    }}

    h1 {{
        font-size: 1.35rem !important;
    }}

    [data-testid="stMarkdownContainer"] h2 {{
        font-size: 1.05rem !important;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        font-size: 0.92rem !important;
    }}

    .stButton button,
    .stDownloadButton button {{
        width: 100% !important;
    }}
}}
{light_overrides}
</style>
"""


# Return the full custom stylesheet for either dark (default) or light mode.
def get_custom_css(light_mode: bool = False) -> str:
    theme_vars = LIGHT_VARS if light_mode else DARK_VARS
    light_overrides = LIGHT_OVERRIDES if light_mode else ""
    return CSS_TEMPLATE.format(theme_vars=theme_vars, light_overrides=light_overrides)
