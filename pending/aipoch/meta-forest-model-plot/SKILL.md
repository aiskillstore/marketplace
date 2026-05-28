---
name: meta-forest-model-plot
description: "Generate forest plots for meta-analysis of survival data. Input is a CSV file containing study names, HR and 95% confidence intervals, output forest plot PNG and data table CSV. Supports both R and Python scripts."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generate forest plots for meta-analysis of survival data. Input is a CSV file containing study names, HR and 95% confidence intervals, output forest plot PNG and data table CSV. Supports both R and Python scripts.".
- Packaged executable path(s): `scripts/forest_survival.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-forest-model-plot"
python -m py_compile scripts/forest_survival.py
python scripts/forest_survival.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/forest_survival.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/forest_survival.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## Data Format Requirements

Users need to provide a CSV file with the following columns:
| Column Name | Description | Example |
|------|------|------|
| study | Study name (author + year) | Smith 2020 |
| outcome_new | Outcome indicator name | Overall Survival |
| group1_HR | Hazard Ratio | 0.85 |
| group1_95%Lower CI or group1_95.Lower.CI | 95% Confidence Interval Lower Bound | 0.72 |
| group1_95%Upper CI or group1_95.Upper.CI | 95% Confidence Interval Upper Bound | 1.01 |

**Note**: HR, Lower CI, and Upper CI must all be positive numbers.

---

## Workflow

### Step 1: Validate Input Data

1. Read the CSV file provided by the user
2. Check if necessary columns exist (supports two column name formats)
3. Validate data integrity (at least 2 studies, HR and CI are positive numbers)

**If there are data issues, prompt the user to correct and resubmit.**

### Step 2: Execute Script (R or Python)

#### Option A: Using R Script (Recommended)

Command:
```bash
Rscript scripts/forest_survival.R "<csv_path>" "<outcome_name>" "<output_dir>"
```

#### Option B: Using Python Script (Backup)

Command:
```bash
python scripts/forest_survival.py "<csv_path>" "<outcome_name>" "<output_dir>"
```

**Parameter Description** (same for both scripts):
- `csv_path`: Absolute path to the input CSV file
- `outcome_name`: Outcome indicator name (optional, default extracted from data)
- `output_dir`: Output directory (optional, default is current directory)

### Step 3: Output Results

**Upon successful execution**:

```
═══════════════════════════════════════════
Forest Plot Generation Complete
═══════════════════════════════════════════

【Outcome Indicator】{outcome_name}
【Included Studies】{n} studies

【Output Files】
• Forest Plot: {output_dir}/Survival_forest_{outcome}.png
• Data Table: {output_dir}/Survival_forest_{outcome}.csv

【Pooled Effect Size】
• HR = {value} [{lower}; {upper}]
• P value = {p_value}

【Heterogeneity】
• I² = {I2}%
• Tau² = {tau2}
• Q test P value = {pval_Q}

═══════════════════════════════════════════
```

---

## Script Dependencies

### R Script Dependencies

Install the following R packages:
- meta
- metafor
- grid
- stringr

If the user's environment is missing these packages, prompt them to run:
```r
install.packages(c("meta", "metafor", "grid", "stringr"))
```

### Python Script Dependencies

Install the following Python packages (Python 3.7+ recommended):
- pandas
- numpy
- matplotlib
- scipy

If the user's environment is missing these packages, prompt them to run:
```bash
pip install pandas numpy matplotlib scipy
```

Or in a virtual environment:
```bash
python -m pip install pandas numpy matplotlib scipy
```


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
- If a file is produced, prefer a deterministic output name such as `meta_forest_model_plot_result.md` unless the skill documentation defines a better convention.
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
python scripts/forest_survival.py --help
```

Expected output format:

```text
Result file: meta_forest_model_plot_result.md
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
