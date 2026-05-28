---
name: bib-formatter
description: Convert reference lists and in-text citations between RIS, BibTeX, plain text, and CSL-JSON, triggered when you need to unify bibliography/citation styles before journal submission or compare before/after formatting differences.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a bibliography in **RIS/BibTeX/plain text/CSL-JSON** and must reformat it to a journal style (e.g., **NEJM**, **The Lancet**, **Nature**) before submission.
- You need to switch **in-text citation formatting** (e.g., generating formatted citations for specific cite keys/IDs).
- You are consolidating references from multiple sources and want a **single consistent output style**.
- You want a **before/after comparison** to verify formatting changes and spot missing metadata.
- You need to validate and repair incomplete entries (missing authors, year, journal, pages, DOI/URL) prior to final export.

## Key Features

- Supports input formats: **RIS**, **BibTeX**, **plain text**, **CSL-JSON**.
- Outputs bibliography entries compatible with **CSL styles** (including NEJM/Lancet/Nature or any custom `.csl`).
- Journal-name driven style selection with **automatic CSL retrieval** (exact match preferred; download first, then search fallback).
- Batch conversion via `scripts/format_bibliography.py`.
- In-text citation generation mode for specified cite keys/IDs.
- Produces a **Markdown Before/After table** (minimum 2 examples) for quick review.
- Detects entries that cannot be reliably parsed and requests missing fields.

## Dependencies

- Python **3.10+**
- Citation Style Language (CSL) style files (`.csl`) for target formatting (e.g., `styles/nature.csl`, `styles/the-lancet.csl`, `styles/new-england-journal-of-medicine.csl`)

## Example Usage

### 1) Auto-retrieve a journal style (recommended)

```bash
python scripts/format_bibliography.py \
  --input refs.bib \
  --input-format bibtex \
  --journal "Nature"
```

### 2) Use a local CSL style file for bibliography formatting

```bash
python scripts/format_bibliography.py \
  --input refs.bib \
  --input-format bibtex \
  --style "styles/nature.csl" \
  --output formatted.txt
```

### 3) RIS input example

```bash
python scripts/format_bibliography.py \
  --input refs.ris \
  --input-format ris \
  --style "styles/the-lancet.csl"
```

### 4) In-text citations mode (format citations for specific IDs)

```bash
python scripts/format_bibliography.py \
  --input refs.json \
  --input-format csljson \
  --style "styles/new-england-journal-of-medicine.csl" \
  --mode citations \
  --cite-keys "ITEM-1,ITEM-2"
```

## Implementation Details

- **Workflow**
  1. Collect input text/files and identify the input format: `ris | bibtex | plain | csljson`.
  2. Choose the target style by either:
     - providing `--journal "<Journal Name>"` (auto-retrieval; exact match prioritized; download first, then search), or
     - providing `--style "<path/to/style.csl>"` (local CSL file).
  3. Run batch conversion using `scripts/format_bibliography.py`.
  4. Validate completeness of critical fields and rerun after fixing missing metadata:
     - author(s), year, title, journal/container title, volume/issue, pages, DOI/URL.
  5. After formatting, append a **Markdown comparison table** with at least **two** Before/After examples.

- **Input parsing and field mapping**
  - Refer to `references/input-formats.md` for parsing rules, field mapping, and format-specific details.

- **Output requirements**
  - All instructions/prompts shown to the user must be **in Chinese**.
  - Clearly state the **target CSL style** and the **source input format**.
  - For entries that cannot be reliably parsed, prompt in Chinese and list the missing fields that must be completed.
  - Always include a **Markdown Before/After comparison table** (≥ 2 examples) at the end.

- **Quality checklist**
  - Output matches the target journal style (NEJM/Lancet/Nature/custom CSL).
  - Required metadata is complete: author, year, journal, volume/issue/pages, DOI/URL.
  - Sorting, punctuation, and capitalization follow the CSL style rules.