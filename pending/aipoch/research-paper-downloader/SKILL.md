---
name: research-paper-downloader
description: Download academic papers from open-access sources when the user provides a DOI/arXiv ID or requests a keyword-based paper search, and return the saved PDF path.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- The user provides a DOI (e.g., `10.1038/s41586-020-2649-2`) and wants the corresponding open-access PDF.
- The user provides an arXiv ID (e.g., `1706.03762`) and wants the preprint PDF.
- The user asks to search papers by keywords (e.g., "attention mechanism") and download available open-access PDFs.
- The user requests downloading an academic/research paper and expects the tool to try multiple open-access providers automatically.
- The user needs the final local save path for the downloaded PDF(s).

## Key Features

- Multi-source open-access retrieval with priority-based fallback until a PDF is found.
- Supports three input modes:
  - DOI download
  - arXiv ID download
  - Keyword search + download (with `max_results`)
- Configurable output directory and network behavior (timeouts, retries, preferred source order).
- Clear failure modes:
  - invalid identifiers
  - no open-access location found
  - network timeouts / source unavailable
- Safe file writing: downloads are saved only under the configured output directory.
- Consistent naming convention: `{first_author}_{year}_{title}.pdf` (truncated to a maximum length).

## Dependencies

- Python `>= 3.8`
- `requests >= 2.0.0`
- Internet access (HTTPS) to the following services:
  - `api.semanticscholar.org`
  - `api.openalex.org`
  - `api.unpaywall.org`
  - `arxiv.org`
  - `pubmed.ncbi.nlm.nih.gov`
  - `api.crossref.org`

## Example Usage

### CLI (scripts/download.py)

Download by DOI:
```bash
python scripts/download.py --doi "10.1038/s41586-020-2649-2" --output "~/Downloads/ResearchPapers"
```

Download by arXiv ID:
```bash
python scripts/download.py --arxiv "1706.03762" --output "~/Downloads/ResearchPapers"
```

Search by keywords and download up to 3 results:
```bash
python scripts/download.py --search "attention mechanism" --max-results 3 --output "~/Downloads/ResearchPapers"
```

### Python (import and call)

```python
from pathlib import Path

# These functions are expected to be provided by the skill implementation (e.g., scripts/download.py or a module it exposes).
from download import download_by_doi, download_by_arxiv, search_download

output_dir = Path.home() / "Downloads" / "ResearchPapers"
output_dir.mkdir(parents=True, exist_ok=True)

# 1) Download by DOI
pdf_path = download_by_doi(doi="10.1016/j.clinimag.2022.03.004", output_dir=str(output_dir))
print("Saved to:", pdf_path)

# 2) Download by arXiv ID
pdf_path = download_by_arxiv(arxiv_id="2310.12345", output_dir=str(output_dir))
print("Saved to:", pdf_path)

# 3) Keyword search and download
pdf_paths = search_download(query="transformer attention", max_results=5, output_dir=str(output_dir))
for p in pdf_paths:
    print("Saved to:", p)
```

## Implementation Details

### Source Priority and Fallback

The downloader attempts open-access sources in priority order and stops at the first successful PDF retrieval:

1. Semantic Scholar (Open Access API) — `api.semanticscholar.org`
2. OpenAlex (Open Academic Graph) — `api.openalex.org`
3. Unpaywall (OA location finder) — `api.unpaywall.org`
4. arXiv (preprint server) — `arxiv.org`
5. PubMed (biomedical database) — `pubmed.ncbi.nlm.nih.gov`
6. Crossref (DOI registry/metadata) — `api.crossref.org`

If a source is unavailable, returns no OA link, or times out, the implementation should automatically proceed to the next source.

### Configuration (config.json)

Recommended configuration keys:

- `output_dir`: default download directory (e.g., `~/Downloads/ResearchPapers`)
- `timeout`: request timeout in seconds (recommended range: `30`-`120`)
- `max_retries`: maximum retry attempts for transient failures
- `preferred_sources`: ordered list of sources to try (overrides default priority)

### File Output Rules

- **Path restriction**: all files must be written only inside `output_dir`.
- **Default directory**: `~/Downloads/ResearchPapers` (if not overridden).
- **Filename format**: `{first_author}_{year}_{title}.pdf`
- **Maximum filename length**: 80 characters (truncate safely).
- The tool should return (or print) the full absolute path of each saved PDF.

### Error Handling Expectations

- **Invalid DOI/arXiv ID**: return a clear error and suggest correcting the identifier format.
- **No open-access version found**: report that no OA PDF is available and suggest alternatives (library access or contacting the authors).
- **Timeouts**: retry according to `max_retries`, then fall back to the next source.
- **Source unavailable**: skip to the next source and report which sources failed if all fail.

### Safety Constraints

- No paywall bypassing or restricted-content circumvention.
- No credential handling is required (sources are expected to work without API keys).
- The downloader must not execute external code; it only performs network requests and writes files to disk.

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
- If a file is produced, prefer a deterministic output name such as `research_paper_downloader_result.md` unless the skill documentation defines a better convention.
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
python scripts/download.py --help
```

Expected output format:

```text
Result file: research_paper_downloader_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
