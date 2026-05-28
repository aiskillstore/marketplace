---
name: pdf-processor
description: Perform basic local PDF operations (merge, split, extract pages/text/tables, create) when users request offline PDF processing without external services.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use
- You need to merge multiple PDFs into a single document offline.
- You need to split a PDF into per-page files for review, annotation, or distribution.
- You need to extract a specific page range (e.g., `1-3,5`) into a new PDF.
- You need to extract selectable text from a PDF into a `.txt` file without using any cloud API.
- You need to extract tables from PDFs into CSV files locally.

## Key Features
- **Merge PDFs**: Combine multiple input PDFs into one output PDF.
- **Split PDFs**: Export each page as an individual PDF.
- **Extract Pages**: Create a new PDF from selected pages using a page-range expression.
- **Extract Text**: Export extracted text to a plain text file.
- **Extract Tables**: Export detected tables to CSV files (may produce empty CSVs on pages without tables).
- **Create PDF**: Generate a simple PDF from a text file.
- **Local-only execution**: No network access, no external APIs, no credentials.

## Dependencies
- **Python**: 3.9+

Install Python dependencies:
```bash
pip install -r scripts/requirements.txt
```

## Example Usage
> More examples may be available in `references/examples.md`.

### Merge PDFs
```bash
python scripts/pdf_tool.py \
  --operation merge \
  --inputs "a.pdf" "b.pdf" \
  --output "out.pdf"
```

### Split a PDF into single-page PDFs
```bash
python scripts/pdf_tool.py \
  --operation split \
  --inputs "input.pdf" \
  --output "out_dir"
```

### Extract specific pages into a new PDF
```bash
python scripts/pdf_tool.py \
  --operation extract-pages \
  --inputs "input.pdf" \
  --pages "1-3,5" \
  --output "extracted.pdf"
```

### Extract text to a `.txt` file
```bash
python scripts/pdf_tool.py \
  --operation extract-text \
  --inputs "input.pdf" \
  --output "output.txt"
```

### Extract tables to CSV files
```bash
python scripts/pdf_tool.py \
  --operation extract-tables \
  --inputs "input.pdf" \
  --output "tables_out_dir"
```

### Create a PDF from a text file
```bash
python scripts/pdf_tool.py \
  --operation create \
  --inputs "input.txt" \
  --output "created.pdf"
```

## Implementation Details
- **Execution model**: Local CLI tool/script (`scripts/pdf_tool.py`) that reads from provided input paths and writes only to the specified output path.
- **Supported operations**:
  - `merge`: Concatenates PDFs in the order provided via `--inputs`.
  - `split`: Writes one PDF per page (output is typically a directory path).
  - `extract-pages`: Uses `--pages` to select pages and writes a new PDF.
  - `extract-text`: Extracts selectable text; pages with no extractable text may yield empty lines.
  - `extract-tables`: Attempts table detection/extraction; pages without tables may produce empty CSV outputs.
  - `create`: Produces a simple PDF from a text input.
- **Page range format**: `--pages "1-3,5"` where page numbering starts at **1**.
- **Failure handling**:
  - Invalid or out-of-range pages in `--pages` are ignored.
  - Text extraction preserves structure minimally; no OCR is performed.
  - Table extraction quality depends on the PDF's structure; complex layouts may not reconstruct well.
- **Security constraints**:
  - No network calls.
  - No external services.
  - Reads only specified input files and writes only to the specified output location.
- **Success criteria**:
  - Output file(s) exist at the specified location.
  - Page counts and ordering match the requested operation.
  - No writes occur outside the specified output path.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `pdf_processor_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/pdf_tool.py --help
```

Expected output format:

```text
Result file: pdf_processor_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
