---
name: crossref-database
description: Access CrossRef metadata for scholarly works; use when you need to resolve a DOI or search CrossRef to retrieve bibliographic details, citation/reference counts, or funder information for research and citation management.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/query_crossref.py --help
```

## When to Use

- You have a DOI and need authoritative bibliographic metadata (title, authors, venue, publication date).
- You need to search CrossRef by keywords (title/author/topic) to find candidate works and their DOIs.
- You want to retrieve reference counts and cited-by counts for quick impact/context checks.
- You need to verify or enrich citation records across publishers for citation management workflows.
- You want to identify funder information associated with a publication.

## Key Features

- **DOI Resolution**: Resolve a DOI to CrossRef metadata and canonical URLs.
- **Work Search**: Query CrossRef by free-text keywords (e.g., title, author, subject).
- **Metadata Lookup**: Retrieve titles, authors, publication dates, journal/container information, etc.
- **Citation Metrics**: Fetch `reference-count` and `is-referenced-by-count` (cited-by).
- **Funder Extraction**: Identify funding organizations recorded in CrossRef metadata.

## Dependencies

- `habanero` (recommended: `>=1.2.0`)

Install:

```bash
pip install "habanero>=1.2.0"
```

## Example Usage

### 1) Resolve a DOI

```bash
python scripts/query_crossref.py --doi "10.1371/journal.pone.0029797"
```

### 2) Search for works (keyword query)

```bash
python scripts/query_crossref.py --query "climate change" --limit 5
```

## Implementation Details

- **Data Source**: CrossRef REST API via the Python `habanero` client.
- **Inputs**
  - `--doi`: A DOI string to resolve to a single work record.
  - `--query`: A free-text query used to search works (e.g., title/author keywords).
  - `--limit`: Maximum number of results to return for searches.
- **Returned Fields (typical)**
  - Bibliographic: `title`, `author`, `issued`/publication date, `container-title` (journal/venue), `publisher`.
  - Identifiers/links: `DOI`, `URL`.
  - Counts: `reference-count`, `is-referenced-by-count`.
  - Funding: `funder` entries when available.
- **Notes**
  - Availability of citation counts and funder data depends on what publishers deposit into CrossRef; some records may omit these fields.
  - Search results are ranked by CrossRef relevance; refine queries and limits as needed for higher precision.

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
- If a file is produced, prefer a deterministic output name such as `crossref_database_result.md` unless the skill documentation defines a better convention.
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
python scripts/query_crossref.py --help
```

Expected output format:

```text
Result file: crossref_database_result.md
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
