---
name: literature-statistics
description: Generate statistics for publication-year and journal distributions from local references or PDFs; use when you need standardized Year/Journal tables and a summary without any network access.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use
- You have a batch of references and need a **publication year distribution** table (counts and percentages).
- You need a **journal distribution** table (Top N optional) for a literature review or report appendix.
- Your input is **pasted citations** (BibTeX/RIS/EndNote/plain text/mixed) and you want quick aggregation.
- Your input is **local reference files** (`.bib/.ris/.txt/.csv`) and you want consistent, standardized output.
- You have a **local PDF folder** and want to extract year/journal signals (best-effort) and summarize them.

## Key Features
- Supports multiple input types: pasted text, local reference files, and local PDF directories (via script).
- Extracts **Year** and **Journal** using format-specific parsing rules (BibTeX/RIS/plain text/PDF).
- Produces two standardized tables:
  - **Year distribution**: `year, count, percent`
  - **Journal distribution**: `journal title, count, percent`
- Provides a summary including totals and unknown-field counts (unknown year / unknown journal).
- Conservative extraction: does **not** guess when metadata is unclear; ambiguous items are counted as `unknown`.
- Local-only operation: no network calls, no external APIs, no credential usage.

## Dependencies
- Python **3.9+**
- Python packages (pinned by your project file):
  - `pip install -r scripts/requirements.txt`

## Example Usage
### 1) Process a local PDF directory
```bash
python scripts/process_pdfs.py --input-dir "./pdfs" --output "./literature_stats.md"
```

### 2) Process a local reference file (example pattern)
If your repository provides a CLI entry or script for reference files, run it similarly to the PDF script. For example:
```bash
python scripts/process_references.py --input "./refs/library.bib" --output "./literature_stats.md"
```

### 3) Expected output format (Markdown)
```md
## Summary
- Total processed: 120
- Unknown year: 7
- Unknown journal: 15

## Year Distribution
| Year | Count | Percent |
|------|-------|---------|
| 2023 | 18    | 15.0%   |
| 2022 | 22    | 18.3%   |
| ...  | ...   | ...     |

## Journal Distribution
| Journal | Count | Percent |
|---------|-------|---------|
| Journal of X | 9 | 7.5% |
| ...         | ... | ... |
```

For additional examples, see: `references/examples.md`.

## Implementation Details
### Processing Pipeline
1. Detect input type: pasted text / file path / PDF directory.
2. Read content from pasted text or local files.
3. Split into individual citations using format cues:
   - BibTeX entries
   - RIS records
   - blank-line separation for plain text/mixed inputs
4. Extract `year` and `journal` using the parsing rules below.
5. Normalize journal names using the normalization rules below.
6. Aggregate counts and compute percentages.
7. Output:
   - Table 1: Year distribution
   - Table 2: Journal distribution
   - Summary: totals + unknown counts
8. For PDF directories, use:
   ```bash
   python scripts/process_pdfs.py --input-dir "<pdf_dir>" --output "<output_md>"
   ```

### Parsing Rules
#### BibTeX
- **Year**: `year` field
- **Journal**: `journal` field

#### RIS
- **Year**: `PY` or `Y1` (use the first 4-digit year)
- **Journal**: first non-empty value among `JO` / `JF` / `T2`

#### Plain Text / Mixed Citations
- **Year**: first 4-digit year in the range **1900-2099** found near the end of the citation
- **Journal**: infer only when patterns are unambiguous (e.g., `Journal Name. 2022;` or `Journal Name, 2022`); otherwise set to `unknown`

#### PDF Directory (Script-Based)
- **Year**: prefer PDF metadata; otherwise use the first 4-digit year found on the first page
- **Journal**: prefer PDF metadata; otherwise scan first-page lines containing keywords such as:
  - `Journal`, `Proceedings`, `Transactions`
  If unclear, set to `unknown`.

### Journal Normalization Rules
- Trim leading/trailing whitespace.
- Collapse multiple spaces into a single space.
- Remove trailing periods and commas.
- If casing is inconsistent, convert to **Title Case**; otherwise keep original casing.
- Do **not** expand abbreviations or infer aliases.

### Failure Handling and Safety Constraints
- Do not guess missing/unclear year or journal values.
- Count ambiguous entries as `unknown` and report the totals in the summary.
- No network access; no external APIs; no credentials.
- Do not read files outside the user-provided paths.

### Sorting and Reporting Requirements
- Tables are sorted by:
  1) `count` descending  
  2) then by `name` ascending (year or journal title)
- Always report:
  - total processed count
  - unknown year count
  - unknown journal count

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
- If a file is produced, prefer a deterministic output name such as `literature_statistics_result.md` unless the skill documentation defines a better convention.
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
python scripts/process_pdfs.py --help
```

Expected output format:

```text
Result file: literature_statistics_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
