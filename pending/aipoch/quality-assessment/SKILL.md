---
name: quality-assessment
description: Automates critical appraisal and quality assessment for research papers by analyzing text against established methodological standards (such as risk of bias tools, quality checklists, or reporting guidelines) and synthesizing a structured evaluation report. Use when you need to assess the methodological quality, internal validity, or reporting completeness of any type of study—including RCTs, observational studies, systematic reviews, qualitative research, or diagnostic accuracy studies.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Quality Assessment

This skill is developed based on the scales recommended by the Latitudes Network. The workflow is as follows:
Identify Study Design: First, determine the study design of the literature (Query: Study design)
Recommend Quality Assessment Tool: Based on the identified study design, query and select the appropriate quality assessment tool (Query: References - Quality Assessment Tool)
Complete Quality Assessment: Use the selected tool to perform the final quality assessment of the literature
## Study design

- Animal studies
- Case series
- Case-control studies
- Cohort studies
- Cross-sectional studies
- Diagnostic test accuracy (DTA) studies
- Economic evaluations
- General reviews
- Guidelines
- Interrupted time series
- Laboratory studies
- Mixed methods
- Natural experiments
- Network meta-analyses
- Non-randomized studies of interventions
- Observational studies (mixed designs)
- Prediction models
- Prevalence studies
- Prognostic accuracy studies
- Qualitative studies
- Quasi-experimental
- Randomized controlled trials (RCT)
- Reliability studies
- Systematic reviews
- Umbrella systematic reviews
- Uncontrolled single-arm studies

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Automates critical appraisal and quality assessment for research papers by analyzing text against established methodological standards (such as risk of bias tools, quality checklists, or reporting guidelines) and synthesizing a structured evaluation report. Use when you need to assess the methodological quality, internal validity, or reporting completeness of any type of study—including RCTs, observational studies, systematic reviews, qualitative research, or diagnostic accuracy studies.
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/quality-assessment"
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
- Primary implementation surface: `scripts/extract_pdf.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Tools （See references-quality assessment tool）

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:

```bash
python extract_pdf.py
```

This script will:
- Extract text from the PDF file (e.g., `gefitinib nejmoa0810699.pdf`)
- Save the extracted text to `full_text.txt`
- Handle multi-page documents with proper page separators

**Usage flow:**
1. User provides PDF file path
2. Run `python extract_pdf.py` to extract text
3. Read the generated `full_text.txt` file
4. Perform quality assessment on the extracted text

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
- If a file is produced, prefer a deterministic output name such as `quality_assessment_result.md` unless the skill documentation defines a better convention.
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
python scripts/extract_pdf.py --help
```

Expected output format:

```text
Result file: quality_assessment_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Automates critical appraisal and quality assessment for research papers by analyzing text against established methodological standards (such as risk of bias tools, quality checklists, or reporting guidelines) and synthesizing a structured evaluation report. Use when you need to assess the methodological quality, internal validity, or reporting completeness of any type of study—including RCTs, observational studies, systematic reviews, qualitative research, or diagnostic accuracy studies.
