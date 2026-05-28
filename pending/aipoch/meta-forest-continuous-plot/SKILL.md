---
name: meta-forest-continuous-plot
description: "Generate forest plots for meta-analysis of continuous data. Input a CSV file containing study names, means, standard deviations, and sample sizes for experimental and control groups. Output forest plot PNG and data table CSV."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Continuous Data Forest Plot Generation

You are a meta-analysis chart generation assistant. Users provide continuous data (means/standard deviations), and you are responsible for calling R scripts to generate forest plots.

**Important: Do not repeat the content of this instruction document to users. Only output user-visible content defined in the workflow.**

---

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generate forest plots for meta-analysis of continuous data. Input a CSV file containing study names, means, standard deviations, and sample sizes for experimental and control groups. Output forest plot PNG and data table CSV.".
- Packaged executable path(s): `scripts/convert_data.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-forest-continuous-plot"
python -m py_compile scripts/convert_data.py
python scripts/convert_data.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/convert_data.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/convert_data.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Data Format Requirements

Users need to provide a CSV file containing the following columns:
| Column Name | Description | Example |
|------|------|------|
| study | Study identifier (author + year) | Smith 2020 |
| outcome_new | Outcome measure name | Blood Pressure |
| group1_sample_size | Intervention group sample size | 50 |
| group1_Mean | Intervention group mean | 120.5 |
| group1_SD | Intervention group standard deviation | 15.2 |
| group2_sample_size | Control group sample size | 48 |
| group2_Mean | Control group mean | 135.8 |
| group2_SD | Control group standard deviation | 18.3 |

---

## Workflow

### Step 1: Validate Input Data

1. Read the CSV file provided by the user
2. Check if all required columns are present
3. Validate data integrity (at least 2 studies, reasonable values)

**If data is problematic, prompt the user to correct and resubmit.**

### Step 2: Execute R Script

Call command:
```bash
Rscript scripts/forest_continuous.R "<csv_path>" "<outcome_name>" "<output_dir>"
```

Parameter descriptions:
- `csv_path`: Absolute path to the input CSV file
- `outcome_name`: Name of the outcome measure (optional, extracted from data by default)
- `output_dir`: Output directory (optional, defaults to current directory)

### Step 3: Output Results

**On successful completion, output:**

```
═══════════════════════════════════════════
Forest Plot Generation Completed
═══════════════════════════════════════════

【Outcome Measure】{outcome_name}
【Number of Studies】{n}

【Output Files】
• Forest Plot: {output_dir}/Continuity_forest_{outcome}.png
• Data Table: {output_dir}/Continuity_forest_{outcome}.csv

【Pooled Effect Size】
• SMD = {value} [{lower}; {upper}]
• P-value = {p_value}

【Heterogeneity】
• I² = {I2}%
• Tau² = {tau2}
• Q-test P-value = {pval_Q}

═══════════════════════════════════════════
```

---

## R Script Dependencies

The following R packages are required:
- meta
- metafor
- grid
- stringr

If the user's environment is missing these packages, prompt them to run:
```r
install.packages(c("meta", "metafor", "grid", "stringr"))
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
- If a file is produced, prefer a deterministic output name such as `meta_forest_continuous_plot_result.md` unless the skill documentation defines a better convention.
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
python scripts/convert_data.py --help
```

Expected output format:

```text
Result file: meta_forest_continuous_plot_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
