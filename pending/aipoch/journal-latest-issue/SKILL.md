---
name: journal-latest-issue
description: Retrieve the latest journal issue's table of contents and abstracts from URL/DOI/PMID/RSS/TOC sources, then generate Chinese key points locally (no external translation APIs) when a new issue needs quick review and archiving.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/journal_digest.py --help
```

## When to Use
- You want the latest issue table of contents (TOC) for one or more journals for quick scanning.
- You need a structured digest (title/DOI/abstract) plus **Chinese key points** for internal reading notes without using external translation services.
- You want to export results to **Markdown** and **CSV** for review, sharing, or archiving.
- You have an RSS feed or TOC URL and want a repeatable pipeline to pull the newest issue content.
- You need a batch mode (JSON input) to process multiple journals in one run.

## Key Features
- Fetches the latest issue TOC and (optionally) abstracts by crawling **public web pages** only.
- Supports multiple input sources: **journal name**, **RSS**, **TOC URL**, and batch **JSON** configuration.
- Generates **Chinese key points locally** based on title + abstract (no external translation APIs); keeps the original English abstract for verification.
- Outputs:
  - `output.md` (human-readable digest grouped by journal/issue)
  - `output.csv` (structured table for downstream processing)
- Safety controls:
  - Domain allowlist by default; optional override via `--allow-all`
  - Built-in timeout/retry behavior (implementation-dependent)

## Dependencies
- Python **3.x**
- Python standard library only (no third-party packages required)

## Example Usage
### 1) Single journal (optionally provide RSS/TOC)
```bash
python scripts/journal_digest.py --journal "Nature" --rss "https://example.com/rss"
```

### 2) Batch mode via JSON
Create `input.json`:
```json
{
  "journals": [
    { "name": "Nature", "rss": "https://...", "toc": "https://..." }
  ]
}
```

Run:
```bash
python scripts/journal_digest.py --json input.json
```

### 3) Common optional flags
```bash
python scripts/journal_digest.py \
  --journal "Nature" \
  --max-items 20 \
  --fetch-abstracts
```

## Implementation Details
### Inputs
Supported CLI inputs:
- `--journal`: Journal name (repeatable)
- `--rss`: RSS/TOC feed URL (optional)
- `--toc`: Table of Contents page URL (optional)
- `--json`: Batch input file (JSON)

Batch JSON format:
```json
{
  "journals": [
    { "name": "Journal Name", "rss": "https://...", "toc": "https://..." }
  ]
}
```

Optional parameters:
- `--allow-all`: Allow crawling non-whitelisted domains (must be explicitly enabled)
- `--max-items`: Maximum number of items to output (default: 20; set to `0` for unlimited)
- `--fetch-abstracts`: Additionally crawl abstracts from article landing pages (slower)

### Source selection logic
- If `--rss` or `--toc` is provided, the skill prioritizes those sources to identify the latest issue content.
- If neither is provided, the skill may attempt built-in source hints for common journals (e.g., known RSS endpoints). For best accuracy, prefer providing RSS/TOC (and/or stable identifiers such as ISSN if supported by your setup).

### Chinese key points generation (no external translation APIs)
- The skill does **not** call external translation services.
- It produces Chinese key points as a brief outline derived from the **English title and abstract**.
- The original English abstract is retained in outputs for manual review and validation.

### Outputs
- `output.md`: Latest issue directory and generated key points, grouped by journal/issue.
- `output.csv`: Tabular export (e.g., Title / DOI / Abstract / Chinese Key Points).

### Security and compliance notes
- Network access is limited to crawling **public** pages.
- A domain allowlist is enforced by default; use `--allow-all` only when you explicitly accept the risk of crawling unknown domains.
- Timeout/retry mechanisms are used to improve robustness (exact values depend on the implementation).

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
- If a file is produced, prefer a deterministic output name such as `journal_latest_issue_result.md` unless the skill documentation defines a better convention.
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
python scripts/journal_digest.py --help
```

Expected output format:

```text
Result file: journal_latest_issue_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
