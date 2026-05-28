---
name: probast-quality-assessment-for-prediction-model-studies
description: Assess bias in medical prediction model studies using PROBAST tool. Use when user wants to evaluate the quality or risk of bias of a medical paper (text or PDF).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# PROBAST Quality Assessment

This skill evaluates the risk of bias in medical prediction model studies using the PROBAST (Prediction model Risk Of Bias ASsessment Tool) framework. It analyzes the full text of a paper across four domains: Participants, Predictors, Outcome, and Analysis.

## When to Use

- Use this skill when you need assess bias in medical prediction model studies using probast tool. use when user wants to evaluate the quality or risk of bias of a medical paper (text or pdf) in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `probast-quality-assessment for prediction model studies` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Assess bias in medical prediction model studies using PROBAST tool. Use when user wants to evaluate the quality or risk of bias of a medical paper (text or PDF).
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/probast-quality-assessment-for-prediction-model-studies"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

To perform the assessment, follow this sequence of operations using the prompts defined in `references/probast_prompts.md`.

### Step 1: Extract Metadata
Extract the first author and year from the paper.
- **Prompt**: Use "1. Metadata Extraction" from `references/probast_prompts.md`.

### Step 2: Assess Risk Domains (Parallel)
Assess the risk of bias for each of the four domains. For each domain, use the corresponding prompt to generate a risk rating (Low/High/Unclear) and detailed reasoning.

- **Domain 1 (Participants)**: Use "2. Domain 1: Participants" from `references/probast_prompts.md`.
- **Domain 2 (Predictors)**: Use "3. Domain 2: Predictors" from `references/probast_prompts.md`.
- **Domain 3 (Outcome)**: Use "4. Domain 3: Outcome" from `references/probast_prompts.md`.
- **Domain 4 (Analysis)**: Use "5. Domain 4: Analysis" from `references/probast_prompts.md`.

### Step 3: Determine Overall Risk
Combine the risk ratings from the four domains to determine the overall risk of bias.
- **Input**: The risk ratings (Low/High/Unclear) from Domains 1-4.
- **Prompt**: Use "6. Overall Risk Assessment" from `references/probast_prompts.md`.

### Step 4: Format Output
Generate a final JSON report containing the risk ratings for all domains and the overall assessment.
- **Input**: The results from Steps 1-3.
- **Prompt**: Use "7. JSON Extraction" from `references/probast_prompts.md`.
- **Output Format**: A JSON object matching the `study_risk_of_bias_schema`.

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:
