---
name: clinic-sample-size
description: "Unified tool for calculating sample sizes for Diagnostic, Efficacy, Etiology, and Prognosis clinical studies. Supports various statistical methods (Sensitivity/Specificity, Log-rank, Chi-square, EPV, etc.)."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- **Smart Inference**: If specific statistical parameters (e.g., standard deviation, error margins) are not provided, the tool infers reasonable defaults based on the study type and mode (e.g., assumes medium effect size for t-tests, standard alpha/beta levels).
- **Metadata Support**: Allows attaching study names and outcome measures to the final report.
- **Multilingual Reports**: Generates detailed Markdown reports in Chinese.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Others/clinic-sample-size"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/calculators.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Clinic Sample Size Calculator

This skill integrates sample size calculations for four major types of clinical research: Diagnostic, Efficacy, Etiology, and Prognosis.

## Output

The calculation results are saved as **Markdown files** in the `output/` directory by default. The file path is returned in the JSON output.
You can specify a custom output directory using `--output_dir`.

## Usage

The skill is executed via the `scripts/main.py` script. The first argument specifies the study type: `diagnostic`, `efficacy`, `etiology`, or `prognosis`.

### Optional Metadata
You can add study information to the report using:
- `--study_name <name>`: Name of the study.
- `--outcome <name>`: Primary outcome measure.

### 1. Diagnostic Studies
Calculates sample size for sensitivity/specificity, AUC, Kappa, or multivariable models.

**Example: Sensitivity/Specificity (Full Params)**
```bash
python scripts/main.py --study_name "New Biomarker Study" --outcome "Sensitivity > 0.8" diagnostic sens_spec --se 0.8 --sp 0.9 --error 0.05 --prev 0.3 --dropout 0.1
```

**Example: Sensitivity/Specificity (Smart Inference)**
```bash

# Only providing study name/outcome, tool infers se=0.85, sp=0.90, prev=0.5, etc.
python scripts/main.py --study_name "Screening Test" --outcome "Diagnosis" diagnostic sens_spec
```

### 2. Efficacy Studies
Calculates sample size for randomized controlled trials (RCTs) or single-arm studies.
**Input**: JSON string or file.

**Example: Two-arm General (Smart Inference)**
```bash

# Infers MeanT=0.5, MeanC=0 (Medium effect size), St=1, Sc=1
python scripts/main.py --study_name "Drug Trial" --outcome "Pain Score" efficacy --input '{"study_type": "general", "design": "two"}'
```

### 3. Etiology Studies
Calculates sample size for cohort/case-control studies.

**Example: Categorical (Smart Inference)**
```bash

# Infers Pt=0.2, Pc=0.1 (RR=2.0)
python scripts/main.py --study_name "Risk Factor Study" etiology --mode categorical
```

### 4. Prognosis Studies
Calculates sample size for prediction models or prognostic factors.

**Example: Prediction Model (EPV)**
```bash

# Infers P=0.1 (Event rate), training_rate=0.7
python scripts/main.py prognosis epv --variables_number 10
```

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
- If a file is produced, prefer a deterministic output name such as `clinic_sample_size_result.md` unless the skill documentation defines a better convention.
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
python scripts/calculators.py --help
```

Expected output format:

```text
Result file: clinic_sample_size_result.md
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
