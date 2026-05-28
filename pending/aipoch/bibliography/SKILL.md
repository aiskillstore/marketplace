---
name: bibliography
description: Classifies and organizes literature by theme, method, and conclusion; use when you need to batch-read a folder of PDF/MD/DOCX/TXT files and output a structured CSV for literature reviews and annotation management.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Bibliography

## When to Use

- You are conducting a literature review and need consistent summaries plus structured metadata (theme/method/conclusion) across many papers.
- You have a mixed-format reading folder (`.pdf`, `.md`, `.docx`, `.txt`) and want a single CSV for downstream analysis (e.g., Excel, R, Python).
- You need to organize annotations by **keywords (theme)**, **experimental methods (method)**, and **key conclusions (conclusion)**.
- You want a two-step pipeline: first generate a human-readable summary Markdown, then generate a machine-friendly CSV from that Markdown.
- You need robust handling of PDFs by converting them to Markdown first (via `pdf-extract`) and then using **only Markdown content** for extraction.

## Key Features

- Batch scans an input directory for `.pdf`, `.md`, `.docx`, and `.txt` literature files.
- Converts PDFs to Markdown via `pdf-extract`, then **ignores non-Markdown artifacts** (e.g., image folders).
- Extracts and normalizes, per document:
  - Title
  - Summary (prefer original abstract)
  - Keywords (theme)
  - Experimental Methods (method names only)
  - Key Conclusions (single sentence)
  - Commentary (one-sentence, tactful evaluation)
- Produces exactly **two outputs**:
  1. A consolidated **Summary Markdown** saved under `outputs/`
  2. A single **CSV** generated from that Summary Markdown
- Enforces UTF-8 output to prevent garbled characters; fills missing fields with `"Not recognized"` instead of leaving blanks.
- Uses the CSV field order and headers defined in `assets/bibliography_template.csv`.

## Dependencies

- `pdf-extract` (version: not specified; required when PDFs are present)
- Input formats supported (no external version constraints specified):
  - PDF
  - Markdown (`.md`)
  - DOCX (`.docx`)
  - Plain text (`.txt`)

## Example Usage

### Goal
Read all literature files in a folder, generate a consolidated summary Markdown, then generate a CSV following `assets/bibliography_template.csv`.

### Inputs
- Input directory (example): `./inputs/literature/`
- Output directory: `./outputs/`
- Output CSV path (example): `./outputs/bibliography.csv`

### Expected Outputs (exactly two files)
- `./outputs/bibliography_summary.md`
- `./outputs/bibliography.csv`

### Example Summary Markdown Structure (generated first)

```md
# Bibliography Summary

## Document 1
- Title: <Title>
- Summary: <Prefer the original Abstract; if missing, use the closest equivalent section>
- Keywords: keyword1 | keyword2 | keyword3
- Experimental Methods: <method1; method2; ... (names only)>
- Key Conclusions: <one sentence covering all main points>
- Commentary: <one tactful sentence>

## Document 2
...
```

### Example CSV (generated from the Summary Markdown)

The CSV must follow the header order defined in:

- `assets/bibliography_template.csv`

Rules:
- One row per document.
- No empty cells; use `Not recognized` when extraction fails.
- Save as UTF-8.

## Implementation Details

### 1) Input Reading and Normalization

- Traverse the input directory and process files with extensions:
  - `.pdf`, `.md`, `.docx`, `.txt`

**PDF handling**
- If PDFs exist, convert them to Markdown using `pdf-extract`.
- Use only the generated `.md` content; ignore image directories or other byproducts.
- Locate `pdf-extract` as follows:
  1. First, look for a sibling skill directory containing `SKILL.md` at the same level as this skill’s parent directory.
  2. If not found, ask the user to confirm the actual `pdf-extract` path.

**DOCX handling**
- Extract body text while preserving title/paragraph order as much as possible.

**MD/TXT handling**
- Read text directly.
- If garbled characters appear or key fields cannot be recognized, attempt to detect and read using the original encoding (commonly `GB18030` / `GBK`) before extraction.

### 2) Generate the Summary Markdown First (Single Source of Truth)

Before producing the CSV, generate a consolidated Summary Markdown containing, for each document:

- **Title**
- **Summary**
  - Prefer the original **Abstract**.
  - If no “Abstract” exists, use the closest equivalent section (e.g., “Summary”, “Highlights”, or an “Objective–Method–Result–Conclusion” style segment).
- **Keywords**
- **Experimental Methods**
- **Key Conclusions**
- **Commentary**
  - Exactly one sentence.
  - Avoid harsh criticism; if the work has low value, use tactful phrasing.

This Summary Markdown must be saved with **UTF-8** encoding and stored under `outputs/`. The CSV must be generated **only** from this Markdown (not directly from raw files).

### 3) Field Extraction Rules (Theme / Method / Conclusion)

- **Keywords (theme)**
  - Prefer the original keywords from the document.
  - Separate multiple keywords with `|`.
  - If no keywords are found, generate **3–5** keyword phrases based on the abstract and append:
    - `(generated based on abstract)`
- **Experimental Methods (method)**
  - Output method names only (no long descriptions).
- **Key Conclusions (conclusion)**
  - One sentence that covers all main points.

### 4) CSV Output Constraints

- Output exactly **one** CSV file at the end.
- CSV field order and headers must match `assets/bibliography_template.csv`.
- Encoding must be **UTF-8** to avoid garbled characters.
- If any field cannot be extracted, write `Not recognized` (never leave empty).
- Only two files may be generated in total:
  1. Summary Markdown
  2. CSV
- No temporary/intermediate/auxiliary files may be left behind (including extracted text dumps, caches, logs, images, backups). If conversion/extraction requires intermediate artifacts, keep them in memory or ensure all non-target files are deleted before final output.
- Do not use PowerShell to directly write/manipulate CSV/Markdown to avoid encoding/newline issues; always generate and save using UTF-8.

### Reference

- Detailed rules and field descriptions: `references/guide.md`