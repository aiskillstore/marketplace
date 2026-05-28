---
name: molecular-review-workflow
description: "Generates academic reviews for molecules in diseases using PubMed research. Invoke when user needs biomedical literature review with Vancouver citation format."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generates academic reviews for molecules in diseases using PubMed research. Invoke when user needs biomedical literature review with Vancouver citation format.".
- Packaged executable path(s): `scripts/pubmed_api.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Biopython library for PubMed API access
- NCBI API credentials (NCBI_EMAIL and NCBI_API_KEY environment variables)

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Academic Writing/molecular-review-workflow"
python -m py_compile scripts/pubmed_api.py
python scripts/pubmed_api.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/pubmed_api.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/pubmed_api.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Molecular Review Workflow

This skill generates comprehensive academic reviews for specific molecules in disease contexts using PubMed research literature.

## Inputs

- **disease**: Disease name (required)
- **molecule**: Molecule name (required)

## Workflow Process

1. **Input Translation**: Translates disease and molecule names to English
2. **Search Term Generation**: Creates optimized PubMed search queries
3. **PubMed Search**: Executes iterative PubMed searches using NCBI Entrez API
4. **Result Processing**: Converts and formats search results
5. **Review Generation**: Creates academic review with Vancouver citation format

## Quality Rules

- Citation numbering must start from 1 and increment sequentially
- Citation numbers must match reference list entries
- Review content must cover the molecule's role in the specified disease
- Vancouver citation format must be used

## Usage

Set environment variables:
```bash
export NCBI_EMAIL="your-email@example.com"
export NCBI_API_KEY="your-ncbi-api-key"
```

Then invoke the skill with disease and molecule parameters.

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
- If a file is produced, prefer a deterministic output name such as `molecular_review_workflow_result.md` unless the skill documentation defines a better convention.
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
python scripts/pubmed_api.py --help
```

Expected output format:

```text
Result file: molecular_review_workflow_result.md
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
