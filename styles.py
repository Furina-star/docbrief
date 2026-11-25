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
</style>
"""


# Return the full custom stylesheet for either dark (default) or light mode.
def get_custom_css(light_mode: bool = False) -> str:
    theme_vars = LIGHT_VARS if light_mode else DARK_VARS
    return CSS_TEMPLATE.format(theme_vars=theme_vars)
