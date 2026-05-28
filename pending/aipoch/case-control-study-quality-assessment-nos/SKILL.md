---
name: case-control-study-quality-assessment-nos
description: Clinical Research Bias Assessment - Case-Control Study (NOS) v2.3.0. Use when you need to assess the bias of a case-control study using the Newcastle-Ottawa Scale (NOS) criteria, or when evaluating the quality of a medical paper.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Clinical Research Bias Assessment (NOS)

This skill evaluates the quality of case-control studies based on the Newcastle-Ottawa Scale (NOS).

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Clinical Research Bias Assessment - Case-Control Study (NOS) v2.3.0. Use when you need to assess the bias of a case-control study using the Newcastle-Ottawa Scale (NOS) criteria, or when evaluating the quality of a medical paper.
- Packaged executable path(s): `scripts/extract_pdf.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/Case-control-study-quality-assessment-nos"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

1.  **Extract Metadata**: Identify the study's first author and publication year.
2.  **Evaluate Criteria**: Assess the study against the three NOS domains:
    *   **Selection**: Case definition, representativeness, control selection, and definition.
    *   **Comparability**: Comparability of cases and controls (age, other factors).
    *   **Exposure**: Ascertainment of exposure, method of ascertainment, and non-response rate.
3.  **Synthesize Results**: Aggregate the evaluations into a structured JSON format.
4.  **Format Output**: Use `scripts/format_nos_table.py` to generate the final summary table.

## Detailed Workflow

### Step 1: Selection Evaluation
Evaluate the "Selection" domain using the criteria detailed in `references/nos_criteria_prompts.md`.
Ensure reasons are provided in Chinese and quote the original text.

### Step 2: Comparability Evaluation
Evaluate the "Comparability" domain.
Note: If the odds ratio is adjusted for confounders, groups are considered comparable.

### Step 3: Exposure Evaluation
Evaluate the "Exposure" domain.

### Step 4: Generate Summary Table
Run the formatting script with the aggregated JSON data:

```bash
python scripts/format_nos_table.py '<json_string>'
```

## References

*   [NOS Criteria Prompts](references/nos_criteria_prompts.md)

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `scripts/extract_pdf.py` to extract the text content before assessment:

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
- If a file is produced, prefer a deterministic output name such as `case_control_study_quality_assessment_nos_result.md` unless the skill documentation defines a better convention.
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
python scripts/extract_pdf.py --help
```

Expected output format:

```text
Result file: case_control_study_quality_assessment_nos_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
