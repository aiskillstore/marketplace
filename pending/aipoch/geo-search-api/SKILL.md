---
name: geo-search-api
description: Search for gene expression DataSets and Profiles in the NCBI GEO database. Use this skill when the user wants to find microarray, RNA-seq, or other genomic data by keywords, organism, author, or specific fields.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# GEO Search API

This skill allows searching the NCBI Gene Expression Omnibus (GEO) database.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Search for gene expression DataSets and Profiles in the NCBI GEO database. Use this skill when the user wants to find microarray, RNA-seq, or other genomic data by keywords, organism, author, or specific fields.
- Packaged executable path(s): `scripts/search_geo.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/geo-search-api"
python -m py_compile scripts/search_geo.py
python scripts/search_geo.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/search_geo.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/search_geo.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

The skill provides a Python script to execute searches against the NCBI Entrez API.

### Script: `scripts/search_geo.py`

Use this script to perform searches.

**Arguments:**

*   `query`: (Required) The main search terms (e.g., "breast cancer", "GSE12345").
*   `--filters`: (Optional) JSON string of field-specific filters.
    *   Example: `'{"Organism": "Homo sapiens", "Author": "Smith"}'`
    *   See `references/query_fields.json` for supported fields.
*   `--db`: (Optional) Target database. `gds` (DataSets/Series) or `geoprofiles`. Default: `gds`.
*   `--limit`: (Optional) Maximum number of results. Default: 10.
*   `--email`: (Optional) User email (recommended for NCBI E-utilities).
*   `--api_key`: (Optional) NCBI API Key (recommended for higher rate limits).

**Example:**

```bash
python scripts/search_geo.py "diabetes" --filters '{"Organism": "Mus musculus", "DataSet Type": "expression profiling by array"}' --limit 5
```

## Query Construction

Queries are constructed by combining the main `query` term with any provided `filters` using the AND operator.
Field aliases (e.g., `ORGN` for `Organism`) are handled automatically by the NCBI API, but using full names from `references/query_fields.json` is recommended for clarity.

## References

*   [query_fields.json](references/query_fields.json): List of valid search fields and their aliases.

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
- If a file is produced, prefer a deterministic output name such as `geo_search_api_result.md` unless the skill documentation defines a better convention.
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
python scripts/search_geo.py --help
```

Expected output format:

```text
Result file: geo_search_api_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
