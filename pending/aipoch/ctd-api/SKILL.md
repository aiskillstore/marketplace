---
name: ctd-api
description: "Accesses Comparative Toxicogenomics Database (CTD) for chemical, gene, disease, and pathway interaction data. Invoke when user needs to query CTD, retrieve toxicogenomics data, or investigate chemical-disease relationships."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Comparative Toxicogenomics Database (CTD) API

This skill allows you to query the Comparative Toxicogenomics Database (CTD) using the Batch Query API. You can retrieve curated and inferred associations between chemicals, diseases, genes, pathways, and phenotypes.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Accesses Comparative Toxicogenomics Database (CTD) for chemical, gene, disease, and pathway interaction data. Invoke when user needs to query CTD, retrieve toxicogenomics data, or investigate chemical-disease relationships.".
- Packaged executable path(s): `scripts/query_ctd.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/ctd-api"
python -m py_compile scripts/query_ctd.py
python scripts/query_ctd.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/query_ctd.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/query_ctd.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Capabilities

### 1. Batch Query
Retrieve data for a list of terms.

**Script:** `scripts/query_ctd.py`

**Usage:**

```bash
python scripts/query_ctd.py --inputType <type> --inputTerms <term1> <term2> ... --report <report_type> [--format <format>]
```

**Parameters:**

- `inputType`: `chem`, `disease`, `gene`, `go`, `pathway`, `phenotype`, `reference`
- `inputTerms`: List of identifiers (MeSH IDs, NCBI Gene IDs, etc.) or names.
- `report`: The type of data to retrieve (e.g., `genes_curated`, `diseases_curated`). See `references/ctd_api_docs.md` for valid combinations.
- `format`: `json` (default), `tsv`, `csv`, `xml`.

### 2. Direct Link Generation
To generate a URL for a specific entity (no script needed, just text generation):

- **Chemical**: `https://ctdbase.org/detail.go?type=chem&acc={ID}`
- **Disease**: `https://ctdbase.org/detail.go?type=disease&acc={ID}`
- **Gene**: `https://ctdbase.org/detail.go?type=gene&acc={ID}`
- **GO Term**: `https://ctdbase.org/detail.go?type=go&acc={ID}`
- **Pathway**: `https://ctdbase.org/detail.go?type=pathway&acc={ID}`

## Examples

**Get curated genes associated with a chemical (e.g., Mercury):**

```bash
python scripts/query_ctd.py --inputType chem --inputTerms "Mercury" --report genes_curated --format json
```

**Get diseases associated with a gene (e.g., APP):**

```bash
python scripts/query_ctd.py --inputType gene --inputTerms "APP" --report diseases_curated
```

## References

See `references/ctd_api_docs.md` for a complete list of valid `inputType` and `report` combinations.

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
- If a file is produced, prefer a deterministic output name such as `ctd_api_result.md` unless the skill documentation defines a better convention.
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
python scripts/query_ctd.py --help
```

Expected output format:

```text
Result file: ctd_api_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
