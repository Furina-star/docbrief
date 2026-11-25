<h1 align="center">docbrief</h1>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python 3.11+">
  </a>
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/Streamlit-1.42+-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  </a>
  <a href="https://ai.google.dev/">
    <img src="https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?logo=googlegemini&logoColor=white" alt="Gemini 2.5 Flash">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  </a>
</p>

<p align="center">
  Fast Python web app that reads PDFs, DOCX files, and URLs to stream a TL;DR, summary, key terms, and citations.
</p>

## Overview

`docbrief` takes a local file or a web link, extracts the text, and streams a structured reading brief using Google's free Gemini API tier. Citations are included only when the source document actually contains them.

## Features

- **File upload & URL fetch** — supports `.pdf`, `.docx`, `.txt`, `.md`, `.csv`, remote PDF/DOCX links, and web articles.
- **Streamed output** — renders the TL;DR, summary, key terms, and conditional citations live as Gemini generates them.
- **Fast local parsing** — uses `pymupdf` for PDFs and caches parsed documents across Streamlit reruns.
- **Exportable** — download the generated brief as a `.md` file or inspect the extracted source text.
- **Clean & responsive UI** — sidebar + reading sheet layout styled in JetBrains Nerd Font Mono (with `JetBrains Mono` web fallback) for desktop and mobile.

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/Furina-star/docbrief.git
cd docbrief
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Add a free Gemini API key

Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey), then copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set `GEMINI_API_KEY` inside `.env` (you can also paste a key directly in the sidebar for the current session):

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### 4. Run the app

```bash
streamlit run app.py
```

## Project Layout

```text
docbrief/
├── app.py                  # Streamlit UI, sidebar controls, streaming output, export
├── extractor.py            # PDF, DOCX, TXT/MD, and URL text extraction
├── analyzer.py             # Gemini API prompt builder and streaming client
├── styles.py               # JetBrains Mono styling and mobile responsive CSS
├── .streamlit/config.toml  # Default dark monochrome theme and upload limit
├── tests/                  # Unit tests for extraction and analysis
├── requirements.txt
├── .env.example
└── LICENSE
```

## Running Tests

```bash
pip install pytest
pytest -v
```

## Notes

- Scanned image-only PDFs without an embedded text layer cannot be read without OCR and will return an error message.
- If you hit the free-tier rate limit on `gemini-2.5-flash`, switch to `gemini-2.5-flash-lite` in the sidebar or `.env`.

## License

MIT — see [LICENSE](LICENSE).
