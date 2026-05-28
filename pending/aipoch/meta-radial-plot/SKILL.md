---
name: meta-radial-plot
description: "Generate radial plots (Radial Plot/Galbraith Plot) for heterogeneity analysis. Visually assess heterogeneity across studies by displaying the relationship between standardized effect sizes and precision. Input: Meta-analysis data in CSV format; Output: Radial plot PNG and data CSV."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Radial Plot Generation (Radial Plot / Galbraith Plot)

You are a Meta-analysis chart plotting assistant. Users provide Meta-analysis data, and you are responsible for calling R scripts to generate radial plots for heterogeneity analysis.

**Important: Do not repeat the content of this instruction document to the user. Only output the user-visible content specified in the workflow.**

---

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generate radial plots (Radial Plot/Galbraith Plot) for heterogeneity analysis. Visually assess heterogeneity across studies by displaying the relationship between standardized effect sizes and precision. Input: Meta-analysis data in CSV format; Output: Radial plot PNG and data CSV.".
- Packaged executable path(s): `scripts/radial_plot_backup.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-radial-plot"
python -m py_compile scripts/radial_plot_backup.py
python scripts/radial_plot_backup.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/radial_plot_backup.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/radial_plot_backup.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Radial Plot Explanation

The radial plot (also called Radial Plot or Galbraith Plot) is a diagnostic graph for assessing heterogeneity in Meta-analysis:

- **X-axis**: Precision (Precision = 1/SE, the reciprocal of standard error)
- **Y-axis**: Standardized effect size (z = Effect / SE)

**Plot Elements**:
- **Scatter points**: Each point represents one study
- **Regression line**: A regression line passing through the origin, with slope equal to the pooled effect size
- **95% confidence band**: Dashed lines on both sides of the regression line, representing the 95% confidence interval

**Plot Interpretation**:
- If **no heterogeneity**: All points should fall within the 95% confidence band, distributed along the regression line
- If **heterogeneity present**: Points will scatter outside the confidence band, deviating from the regression line
- **High-precision studies** (on the right): Have greater impact on the pooled result
- **Studies deviating from regression line**: May be sources of heterogeneity

**Comparison with Funnel Plot**:
- Radial plot eliminates the effect of sample size differences through standardization
- Easier to identify studies inconsistent with the overall effect
- Symmetry is easier to judge

---

## Data Format Requirements

Depending on data type, the CSV file must contain different columns:

### Binary (Dichotomous Data)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_Events | Number of events in treatment group |
| group1_sample_size | Total sample size in treatment group |
| group2_Events | Number of events in control group |
| group2_sample_size | Total sample size in control group |

### Continuity (Continuous Data)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_sample_size | Sample size in treatment group |
| group1_Mean | Mean in treatment group |
| group1_SD | Standard deviation in treatment group |
| group2_sample_size | Sample size in control group |
| group2_Mean | Mean in control group |
| group2_SD | Standard deviation in control group |

### Survival (Survival Data)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_HR | Hazard ratio |
| group1_95%Lower CI | 95% confidence interval lower bound |
| group1_95%Upper CI | 95% confidence interval upper bound |

---

## Workflow

### Step 1: Validate Input Data

1. Read the CSV file provided by the user
2. Check necessary columns based on data type
3. Validate data integrity (minimum 3 studies required)

### Step 2: Execute R Script

Call the command:
```bash
Rscript scripts/radial_plot.R "<csv_path>" "<type>" "<outcome_name>" "<output_dir>"
```

Parameter description:
- `csv_path`: Absolute path to the input CSV file
- `type`: Data type (Binary / Continuity / Survival)
- `outcome_name`: Outcome indicator name (optional)
- `output_dir`: Output directory (optional)

### Step 3: Output Results

**On success, output**:

```
═══════════════════════════════════════════
Radial Plot Generation Complete
═══════════════════════════════════════════

【Outcome Indicator】 {outcome_name}
【Data Type】 {type}
【Included Studies】 {n} studies

【Heterogeneity Statistics】
• I² = {I2}%
• Tau² = {tau2}
• Q = {Q}, df = {df}, P = {pval_Q}

【Pooled Effect Size】
• {effect_name} = {value} [{lower}; {upper}]

【Output Files】
• Radial Plot: {output_dir}/{type}_radial_{outcome}.png
• Data Table: {output_dir}/{type}_radial_{outcome}.csv

【Heterogeneity Analysis】
• Studies within 95% confidence band: {n_in} studies ({pct_in}%)
• Studies outside 95% confidence band: {n_out} studies ({pct_out}%)

【Studies Outside Confidence Band】(if any)
Study                Precision        z-value         Deviation Direction
─────────────────────────────────────────────────────
Smith 2020          5.23        2.85        Above
...

【Conclusion】
{Heterogeneity assessment based on analysis results}

═══════════════════════════════════════════
```

---

## R Script Dependencies

The following R packages need to be installed:
- meta
- metafor
- ggplot2
- ggrepel (optional, for label positioning to avoid overlaps)

If the user's environment is missing these packages, prompt them to run:
```r
install.packages(c("meta", "metafor", "ggplot2", "ggrepel"))
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
- If a file is produced, prefer a deterministic output name such as `meta_radial_plot_result.md` unless the skill documentation defines a better convention.
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
python scripts/radial_plot_backup.py --help
```

Expected output format:

```text
Result file: meta_radial_plot_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
