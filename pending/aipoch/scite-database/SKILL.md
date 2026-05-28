---
name: scite-database
description: Access Scite.ai Smart Citations to classify how a paper is cited (supporting, contrasting, mentioning) and assess scientific claims; use it when you need to evaluate a paper’s reliability or its acceptance in the literature.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Scite Database Skill

This skill provides access to Scite.ai **Smart Citations** data. Given a paper DOI, it summarizes how the paper is cited by others—specifically whether citations are **supporting**, **contrasting**, or **mentioning**—to help you evaluate the strength and reception of scientific claims.

## When to Use

- Use this skill when you need access scite.ai smart citations to classify how a paper is cited (supporting, contrasting, mentioning) and assess scientific claims; use it when you need to evaluate a paper’s reliability or its acceptance in the literature in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/scite_client.py` is the most direct path to complete the request.
- Use this skill when you need the `scite-database` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Access Scite.ai Smart Citations to classify how a paper is cited (supporting, contrasting, mentioning) and assess scientific claims; use it when you need to evaluate a paper’s reliability or its acceptance in the literature.
- Packaged executable path(s): `scripts/scite_client.py` plus 3 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/scite-database"
python -m py_compile scripts/scite_client.py
python scripts/scite_client.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/scite_client.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/scite_client.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to:

1. **Assess claim reliability**: determine whether a paper is mostly supported or frequently contradicted by later work.
2. **Prioritize reading in a literature review**: quickly gauge consensus and controversy around a key DOI.
3. **Fact-check scientific statements**: validate whether a claim is broadly supported in subsequent citations.
4. **Compare competing papers**: contrast citation sentiment profiles across multiple DOIs.
5. **Screen sources for downstream use**: decide whether a paper is suitable to cite in reports, reviews, or product decisions.

## 2. Key Features

- **Citation classification counts**: returns totals for *supporting*, *contrasting*, and *mentioning* citations for a given DOI.
- **Summary output formats**: supports human-readable text output and machine-readable JSON output.
- **Basic venue/journal metadata (when available)**: returns limited publication/venue information if provided by the endpoint.

## 3. Dependencies

- **Python**: 3.9+
- **requests**: 2.x

## 4. Example Usage

### Run from CLI (text output)

```bash
python scripts/scite_client.py "10.1038/nature12345"
```

Example output:

```text
--- Scite Analysis for 10.1038/nature12345 ---
Total Citations: 45
Supporting:      12
Contrasting:     1
Mentioning:      32
```

### Run from CLI (JSON output)

```bash
python scripts/scite_client.py "10.1038/nature12345" --format json
```

Example JSON (shape may vary by endpoint response):

```json
{
  "doi": "10.1038/nature12345",
  "total_citations": 45,
  "supporting": 12,
  "contrasting": 1,
  "mentioning": 32
}
```

## 5. Implementation Details

- **Primary entry point**: `scripts/scite_client.py`
- **Input**: a single DOI string (e.g., `10.1038/nature12345`)
- **Core logic**:
  - Calls a public Scite endpoint for the DOI.
  - Parses the response to extract citation classification counts:
    - `supporting`
    - `contrasting`
    - `mentioning`
  - Computes/prints `total_citations` as the sum of the above (or uses the API-provided total when available).
- **Output modes**:
  - Default: formatted text summary for quick inspection.
  - `--format json`: emits a JSON object suitable for pipelines and automated checks.
- **Limitations / notes**:
  - Uses **public Scite API endpoints**; availability and response fields may change.
  - **Citation snippets (context text)** may require authentication and are not configured by default; this skill focuses on **aggregate counts** rather than full citation contexts.
