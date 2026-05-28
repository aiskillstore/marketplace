---
name: meta-results-sensitivity-analysis
description: Generates the "Results" section for meta-analysis sensitivity analysis based on statistical tables and titles. Use when the user wants to describe sensitivity analysis results or format sensitivity tables for a meta-analysis paper.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when:
1.  The user provides a sensitivity analysis table (Leave-One-Out) and wants a textual description.
2.  The user needs to format the "Results" section for a meta-analysis paper regarding sensitivity checks.
3.  The user specifies a target language (Chinese or English) for the output.

## Key Features

- Scope-focused workflow aligned to: Generates the "Results" section for meta-analysis sensitivity analysis based on statistical tables and titles. Use when the user wants to describe sensitivity analysis results or format sensitivity tables for a meta-analysis paper.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Academic Writing/meta-results-sensitivity-analysis"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Meta Sensitivity Analysis Generator

This skill generates a descriptive "Results" section for meta-analysis sensitivity analysis. It processes statistical tables (Leave-One-Out method), generates a textual description using an LLM, and formats the output with proper table citations and legends.

## Workflow

1.  **Generate Description**: The LLM describes the sensitivity analysis table based on the meta-analysis title and outcome name.
2.  **Format Output**: A script inserts the table citation (e.g., `(Table 5)`) and formats the table with a standard legend.

## Usage

### Input Parameters

*   `title` (optional): Title of the meta-analysis.
*   `sensitivity_table` (optional): The raw statistical table data.
*   `language` (required): Output language (`Chinese` or `English`).
*   `outcome_name` (optional): Name of the outcome indicator.

### Example

```python
from scripts.format_result import format_sensitivity_result

# 1. LLM generates the description (simulated)

# description = llm.generate(prompt="Describe the sensitivity table...", context=inputs)

# 2. Script formats the final result

# final_output = format_sensitivity_result(

#     text=description,

#     table_data=inputs['sensitivity_table'],

#     language=inputs['language']

# )
```

## Quality Rules

1.  **Language**: Output must be strictly in the user-specified language.
2.  **Formatting**: Remove any JSON formatting from LLM output.
3.  **Citation**: Must insert table citation (Table 5) before the last punctuation of the description.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `meta_results_sensitivity_analysis_result.md` unless the skill documentation defines a better convention.
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

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: meta_results_sensitivity_analysis_result.md
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
