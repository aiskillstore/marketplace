---
name: biorxiv-database
description: Search, retrieve metadata, and download PDFs for bioRxiv preprints; use when you need to discover biology preprints by keywords/authors/date ranges and programmatically fetch their details.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to find recent bioRxiv preprints for a topic (e.g., "CRISPR") within a specific time window (last N days).
- You want to build a literature monitoring pipeline that periodically searches bioRxiv and collects results.
- You need structured preprint metadata (title, abstract, DOI, authors) for downstream analysis or indexing.
- You want to automatically download full-text PDFs for a set of preprints identified by DOI.
- You need a simple CLI tool to quickly query bioRxiv without writing additional code.

## Key Features

- Keyword-based search with a configurable lookback window (days).
- Structured metadata retrieval in JSON-like dictionaries (e.g., Title, Abstract, DOI, Authors).
- PDF download by DOI to a local file path.
- Scriptable Python API via `BioRxivSearcher`.
- Command-line interface for quick searches.

## Dependencies

- Python 3.8+
- `requests>=2.25.0`

## Example Usage

### Install

```bash
pip install requests
```

### Python (end-to-end)

```python
from scripts.biorxiv_search import BioRxivSearcher

def main():
    searcher = BioRxivSearcher()

    # 1) Search for papers (e.g., "CRISPR" in the last 30 days)
    papers = searcher.search_by_keywords(["CRISPR"], days_back=30)
    print(f"Found {len(papers)} papers")

    # 2) Print basic metadata and download the first PDF (if available)
    if papers:
        first = papers[0]
        print("First result:")
        print(f"  Title: {first.get('title')}")
        print(f"  DOI:   {first.get('doi')}")
        print(f"  Authors: {first.get('authors')}")

        out_path = "paper.pdf"
        print(f"Downloading PDF to: {out_path}")
        searcher.download_pdf(first["doi"], out_path)

if __name__ == "__main__":
    main()
```

### CLI

```bash
python scripts/biorxiv_search.py "CRISPR" 30
```

## Implementation Details

- **Core entry point**: `BioRxivSearcher` in `scripts/biorxiv_search.py`.
- **Search parameters**:
  - `keywords`: list of strings used to match relevant preprints.
  - `days_back`: integer lookback window; the search is constrained to items within the last `days_back` days.
- **Returned data shape**: search results are returned as a list of dictionaries containing key fields such as `title`, `abstract`, `doi`, and `authors` (exact keys depend on the API response mapping).
- **PDF download**:
  - Uses the DOI from a search result to resolve and fetch the corresponding PDF.
  - Writes the downloaded content to the provided output file path.
- **API reference**: See `references/api_reference.md` for endpoint/field details and response formats.

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
- If a file is produced, prefer a deterministic output name such as `biorxiv_database_result.md` unless the skill documentation defines a better convention.
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
python scripts/biorxiv_search.py --help
```

Expected output format:

```text
Result file: biorxiv_database_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
