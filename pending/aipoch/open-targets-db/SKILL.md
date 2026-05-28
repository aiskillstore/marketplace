---
name: open-targets-db
description: Query the Open Targets Platform to retrieve targets, diseases, or evidence records when you need target-disease association data and evidence-based scores for therapeutic discovery.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a disease (e.g., an EFO ID) and want to discover and prioritize candidate therapeutic targets.
- You have a target (e.g., an Ensembl gene ID) and need to review associated diseases and supporting evidence.
- You need evidence-level details (e.g., GWAS, ClinVar, ChEMBL) to justify or audit a target-disease association.
- You want to compare association strength across targets/diseases using Open Targets evidence scoring.
- You are building a pipeline that programmatically fetches curated target-disease associations from Open Targets.

## Key Features

- **Entity querying** by type: `target`, `disease`, or `evidence`.
- **Target discovery** for diseases using Open Targets associations.
- **Association scoring** based on Open Targets evidence aggregation (harmonic-sum style aggregation across evidence sources).
- **Evidence retrieval** from integrated sources such as GWAS, ClinVar, ChEMBL, pathways, and other curated datasets.
- **Field selection** to request only specific fields (optional) for smaller payloads.

## Dependencies

- Python `>=3.8`
- `requests >=2.25`

## Example Usage

Run a target query by Ensembl ID (example: **BRAF** `ENSG00000157764`):

```bash
python scripts/query_opentargets.py --id "ENSG00000157764" --type target
```

Optional: request specific fields (if supported by your script/API wrapper):

```bash
python scripts/query_opentargets.py \
  --id "ENSG00000157764" \
  --type target \
  --fields "approvedSymbol,biotype,tractability"
```

## Implementation Details

- **Inputs**
  - `query_type` (required, `string`): Entity type to query. Supported values: `target`, `disease`, `evidence`.
  - `id` (required, `string`): Entity identifier (e.g., Ensembl ID for targets, EFO ID for diseases).
  - `fields` (optional, `array`): A list of fields to retrieve to limit the response payload.

- **Outputs**
  - `data` (`json`): The parsed response returned by the Open Targets API for the requested entity.

- **Scoring model (conceptual)**
  - Open Targets aggregates evidence across multiple evidence sources (genetics, drugs/chemistry, pathways, literature/curation, etc.).
  - Association scores are computed by combining evidence contributions; the platform commonly uses harmonic-sum style aggregation to prevent any single evidence type from dominating while still rewarding multiple independent evidence lines.

- **Reference**
  - See `references/api_reference.md` for API details, available fields, and entity schemas.

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

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `open_targets_db_result.md` unless the skill documentation defines a better convention.
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

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/query_opentargets.py --help
```

Expected output format:

```text
Result file: open_targets_db_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Query the Open Targets Platform to retrieve targets, diseases, or evidence records when you need target-disease association data and evidence-based scores for therapeutic discovery.
