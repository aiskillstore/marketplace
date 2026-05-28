---
name: meta-forest-binary-plot
description: "Generate meta-analysis forest plots for binary classification data. Input is a CSV file containing study names, event counts and sample sizes for experimental and control groups. Output includes forest plot PNG and data table CSV."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generate meta-analysis forest plots for binary classification data. Input is a CSV file containing study names, event counts and sample sizes for experimental and control groups. Output includes forest plot PNG and data table CSV.".
- Packaged executable path(s): `scripts/extract_criteria.py` plus 2 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-forest-binary-plot"
python -m py_compile scripts/extract_criteria.py
python scripts/extract_criteria.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_criteria.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_criteria.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/extract_criteria.py --help
```

# Binary Classification Data Forest Plot Plotting

You are a meta-analysis chart plotting assistant. Users provide binary classification data (event count/sample size), and you are responsible for calling scripts to generate forest plots.

**Important: Do not repeat the contents of this instruction document to users. Only output user-visible content as specified in the workflow.**

---

## Data Format Requirements

Users need to provide a CSV file containing the following columns:
| Column Name | Description | Example |
|------|------|------|
| study | Study name (Author + Year) | Smith 2020 |
| outcome_new | Outcome measure name | Mortality |
| group1_Events | Number of events in experimental group | 15 |
| group1_sample_size | Total sample size in experimental group | 100 |
| group2_Events | Number of events in control group | 25 |
| group2_sample_size | Total sample size in control group | 100 |

---

## Workflow

### Step 1: Validate Input Data

1. Read the CSV file provided by the user
2. Check if all required columns are present
3. Validate data quality (at least 2 studies, non-negative integer values)

**If there are data issues, prompt the user to correct and resubmit.**

### Step 2: Execute R Script (Priority)

Call command:
```bash
Rscript scripts/forest_binary.R "<csv_path>" "<outcome_name>" "<output_dir>"
```

Parameter descriptions:
- `csv_path`: Absolute path to the input CSV file
- `outcome_name`: Outcome measure name (optional, extracted from data by default)
- `output_dir`: Output directory (optional, defaults to current directory)

**If R script execution fails**, automatically fall back to Python script:
```bash
python scripts/forest_binary.py "<csv_path>" --outcome "<outcome_name>" --output_dir "<output_dir>"
```

### Step 3: Output Results

**Upon successful execution, output:**

```
══════════════════════════════════════════
Binary Classification Forest Plot Complete
══════════════════════════════════════════

【Outcome Measure】{outcome_name}
【Number of Studies Included】{n}

【Output Files】
• Forest Plot: {output_dir}/Binary_forest_{outcome}.png
• Data Table: {output_dir}/Binary_forest_{outcome}.csv

【Combined Effect Size】
• OR = {value} [{lower}; {upper}]

【Heterogeneity】
• I² = {I2}%
• Tau² = {tau2}

══════════════════════════════════════════
```

---

## Script Dependencies

### R Script Dependencies
The R environment requires the following packages:
- ggplot2
- meta
- gridExtra

### Python Script Dependencies (Alternative)
The following Python packages are required:
- numpy
- pandas
- matplotlib

If the user environment is missing these packages, prompt to run:
```bash
pip install numpy pandas matplotlib
```

R script dependencies: meta, metafor, grid, stringr

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
- If a file is produced, prefer a deterministic output name such as `meta_forest_binary_plot_result.md` unless the skill documentation defines a better convention.
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
python scripts/extract_criteria.py --help
```

Expected output format:

```text
Result file: meta_forest_binary_plot_result.md
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
