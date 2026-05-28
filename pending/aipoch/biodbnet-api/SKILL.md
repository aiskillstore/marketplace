---
name: biodbnet-api
description: Access bioDBnet REST services for biological identifier conversion, pathway retrieval, and ortholog mapping. Use when you need to convert gene/protein IDs, find pathways, or retrieve biological annotations via bioDBnet.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# bioDBnet API Skill

This skill provides access to bioDBnet (biological Database network) REST web services. It allows for integrating biological data from multiple databases, converting identifiers, and retrieving pathway or ortholog information.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Access bioDBnet REST services for biological identifier conversion, pathway retrieval, and ortholog mapping. Use when you need to convert gene/protein IDs, find pathways, or retrieve biological annotations via bioDBnet.
- Packaged executable path(s): `scripts/biodbnet_client.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Others/biodbnet-api"
python -m py_compile scripts/biodbnet_client.py
python scripts/biodbnet_client.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/biodbnet_client.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/biodbnet_client.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

The core functionality is provided by the `scripts/biodbnet_client.py` script. This script handles the HTTP requests to the bioDBnet API.

### Common Operations

1.  **ID Conversion (db2db)**: Convert identifiers (e.g., Gene Symbol to Affy ID).
2.  **Pathway Retrieval (getPathways)**: Get signaling pathways for a taxon.
3.  **Orthologs (dbOrtho)**: Find orthologs between species.
4.  **Annotations (dbAnnot)**: Retrieve annotations for genes/proteins.

## Commands

To use the API, execute the python script with the appropriate method and parameters.

```bash
python scripts/biodbnet_client.py --method <method_name> --params <json_params>
```

See `references/api_methods.md` for a complete list of supported methods and their parameters.

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
- If a file is produced, prefer a deterministic output name such as `biodbnet_api_result.md` unless the skill documentation defines a better convention.
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
python scripts/biodbnet_client.py --help
```

Expected output format:

```text
Result file: biodbnet_api_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
