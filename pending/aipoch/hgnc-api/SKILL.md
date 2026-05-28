---
name: hgnc-api
description: Access the HGNC (HUGO Gene Nomenclature Committee) database to search for and retrieve gene information including symbols, names, IDs, and other metadata.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# HGNC API Skill

Access the HGNC database to retrieve standardized gene nomenclature and associated resources.

## When to Use

- Use this skill when you need access the hgnc (hugo gene nomenclature committee) database to search for and retrieve gene information including symbols, names, ids, and other metadata in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/hgnc.py` is the most direct path to complete the request.
- Use this skill when you need the `hgnc-api` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Access the HGNC (HUGO Gene Nomenclature Committee) database to search for and retrieve gene information including symbols, names, IDs, and other metadata.
- Packaged executable path(s): `scripts/hgnc.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/hgnc-api"
python -m py_compile scripts/hgnc.py
python scripts/hgnc.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/hgnc.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/hgnc.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Tools

### fetch
Retrieve detailed gene records from HGNC.

- **term** (string): The identifier to look up (e.g., "BRAF", "HGNC:1097").
- **field** (string, optional): The field to query against. Defaults to "symbol".

**Command:**
```bash
python scripts/hgnc.py fetch "{term}" --field "{field}"
```

### search
Search for genes using keywords or identifiers. Returns hgnc_id, symbol, and score.

- **term** (string): The search query.
- **field** (string, optional): Specific field to search in.

**Command:**
```bash
python scripts/hgnc.py search "{term}" --field "{field}"
```

### get_info
Get service status and metadata.

**Command:**
```bash
python scripts/hgnc.py info
```
