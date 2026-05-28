---
name: markitdown
description: Convert files and Office documents into clean Markdown when you need LLM-friendly, token-efficient text (e.g., for summarization, search, RAG ingestion, or dataset preparation).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Converting research papers or reports (PDF/DOCX/EPUB/HTML) into Markdown for LLM summarization, Q&A, or RAG indexing.
- Extracting tables and structured content from spreadsheets (XLSX/CSV) into Markdown for analysis or documentation.
- Turning slide decks (PPTX) into Markdown notes, including speaker notes and (optionally) AI-generated image descriptions.
- Processing images or scanned documents with OCR to obtain searchable, editable Markdown text.
- Transcribing audio (WAV/MP3) or pulling YouTube transcripts into Markdown for meeting notes, content analysis, or knowledge bases.

## Key Features

- Converts many formats to structured Markdown (PDF, DOCX, PPTX, XLSX, images, audio, HTML, CSV, JSON, XML, ZIP, EPUB, YouTube URLs, etc.).
- Produces token-efficient output suitable for LLM pipelines (summarization, chunking, embedding).
- OCR support for images/scans (when OCR dependencies are installed).
- Audio transcription support (when transcription dependencies are installed).
- Optional AI-enhanced image/slide descriptions via an OpenAI-compatible client (e.g., OpenRouter).
- Plugin system to extend format support and custom behaviors.
- Stream-based conversion API for large files.

## Dependencies

- Python: `>=3.9` (recommended)
- Package:
  - `markitdown[all]` (installs all optional format handlers)

Optional system dependencies (feature-dependent):
- Tesseract OCR: `tesseract-ocr` (for image/scanned-text OCR)

Optional external services (feature-dependent):
- Azure Document Intelligence endpoint (for enhanced PDF extraction)
- OpenAI-compatible LLM endpoint (e.g., OpenRouter) for AI image descriptions

## Example Usage

### Install

```bash
pip install 'markitdown[all]'
```

### CLI: Convert a PDF to Markdown

```bash
markitdown document.pdf -o output.md
```

### Python: Convert multiple formats (PDF/XLSX/PPTX/DOCX) and save outputs

```python
from pathlib import Path
from markitdown import MarkItDown

md = MarkItDown()

files = [
    "document.pdf",
    "spreadsheet.xlsx",
    "presentation.pptx",
    "notes.docx",
]

for path in files:
    result = md.convert(path)
    out = Path(path).with_suffix(".md")
    out.write_text(result.text_content, encoding="utf-8")
    print(f"Converted {path} -> {out}")
```

### Python: Stream conversion (useful for large files)

```python
from markitdown import MarkItDown

md = MarkItDown()

with open("large_file.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")

with open("large_file.md", "w", encoding="utf-8") as out:
    out.write(result.text_content)
```

### Python: AI-enhanced image/slide descriptions (OpenAI-compatible, e.g., OpenRouter)

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI(
    api_key="YOUR_OPENROUTER_API_KEY",
    base_url="https://openrouter.ai/api/v1",
)

md = MarkItDown(
    llm_client=client,
    llm_model="anthropic/claude-opus-4.5",
    llm_prompt="Describe this image in detail for scientific documentation.",
)

result = md.convert("presentation.pptx")
print(result.text_content)
```

## Implementation Details

- **Conversion entry points**
  - `MarkItDown().convert(path)` converts a file by path/URL and returns an object whose primary payload is `result.text_content` (Markdown).
  - `MarkItDown().convert_stream(stream, file_extension=".pdf")` converts from a binary stream; use this for large files or when data is not on disk.

- **Format handling**
  - Format support is provided by optional extras (e.g., `pdf`, `docx`, `pptx`, `xlsx`, `audio-transcription`, `youtube-transcription`) or `all`.
  - ZIP inputs are typically processed by iterating through contained files and converting each supported entry.

- **OCR**
  - For images/scanned documents, OCR is enabled when OCR tooling is available (commonly Tesseract). Ensure the OS-level OCR binary is installed and accessible in `PATH`.

- **AI image descriptions**
  - When `llm_client`, `llm_model`, and `llm_prompt` are provided, MarkItDown can request model-generated descriptions for images (including slide images), then inject those descriptions into the Markdown output.
  - Any OpenAI-compatible client can be used (e.g., OpenRouter) by setting `base_url` and `api_key`.

- **Enhanced PDF extraction (Azure Document Intelligence)**
  - When configured with a Document Intelligence endpoint, PDF extraction can be improved for complex layouts (tables, multi-column text, scanned PDFs), producing more faithful Markdown structure.

- **Plugins**
  - Plugins can be listed and enabled from the CLI (e.g., `--list-plugins`, `--use-plugins`) to extend conversion behavior or add new format handlers.