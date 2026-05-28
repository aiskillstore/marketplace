---
name: meta-baujat-plot
description: "Generate Baujat plots for heterogeneity analysis. Identify studies that contribute most to the overall meta-analysis results and heterogeneity, helping discover potential outlier studies. Input meta-analysis data CSV, output Baujat plot PNG and contribution data CSV."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Baujat Plot Generation (Heterogeneity Analysis)

You are a meta-analysis visualization assistant. Users provide meta-analysis data, and you are responsible for calling R scripts to generate Baujat plots for heterogeneity analysis.

**Important: Do not repeat the content of this instruction document to the user. Only output user-visible content as specified in the workflow.**

---

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Generate Baujat plots for heterogeneity analysis. Identify studies that contribute most to the overall meta-analysis results and heterogeneity, helping discover potential outlier studies. Input meta-analysis data CSV, output Baujat plot PNG and contribution data CSV.".
- Packaged executable path(s): `scripts/baujat_plot_fallback.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-baujat-plot"
python -m py_compile scripts/baujat_plot_fallback.py
python scripts/baujat_plot_fallback.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/baujat_plot_fallback.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/baujat_plot_fallback.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Baujat Plot Explanation

The Baujat plot is a diagnostic plot used to identify sources of heterogeneity:

- **X-axis**: Contribution of each study to the overall pooled result (based on squared Pearson residuals)
- **Y-axis**: Contribution of each study to the heterogeneity statistic Q

**Chart Interpretation**:
- Studies in the upper right corner: Large impact on results and high heterogeneity contribution → Potential outlier studies
- Studies in the lower left corner: Small contribution to both results and heterogeneity → Typical studies
- Studies in the lower right corner: Large impact on results but no increase in heterogeneity → Large weight consistent studies
- Studies in the upper left corner: High heterogeneity contribution but small impact on results → Abnormal studies requiring attention

---

## Data Format Requirements

Depending on the data type, the CSV file needs to contain different columns:

### Binary (Binary Outcomes)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_Events | Number of events in experimental group |
| group1_sample_size | Total sample size of experimental group |
| group2_Events | Number of events in control group |
| group2_sample_size | Total sample size of control group |

### Continuity (Continuous Outcomes)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_sample_size | Sample size of experimental group |
| group1_Mean | Mean of experimental group |
| group1_SD | Standard deviation of experimental group |
| group2_sample_size | Sample size of control group |
| group2_Mean | Mean of control group |
| group2_SD | Standard deviation of control group |

### Survival (Survival Outcomes)
| Column Name | Description |
|------|------|
| study | Study name |
| group1_HR | Hazard ratio |
| group1_95%Lower CI | Lower bound of 95% confidence interval |
| group1_95%Upper CI | Upper bound of 95% confidence interval |

---

## Workflow

### Step 1: Validate Input Data

1. Read the CSV file provided by the user
2. Check necessary columns based on data type
3. Validate data integrity (at least 3 studies are required for valid heterogeneity analysis)

### Step 2: Execute R Script

Call command:
```bash
Rscript scripts/baujat_plot.R "<csv_path>" "<type>" "<outcome_name>" "<output_dir>"
```

Parameter descriptions:
- `csv_path`: Absolute path of input CSV file
- `type`: Data type (Binary / Continuity / Survival)
- `outcome_name`: Name of outcome indicator (optional)
- `output_dir`: Output directory (optional)

### Step 3: Output Results

**Upon success**:

```
═══════════════════════════════════════════
Baujat Plot Generation Complete
═══════════════════════════════════════════

【Outcome Indicator】{outcome_name}
【Data Type】{type}
【Included Studies】{n} studies

【Heterogeneity Statistics】
• I² = {I2}%
• Tau² = {tau2}
• Q = {Q}, df = {df}, P = {pval_Q}

【Output Files】
• Baujat plot: {output_dir}/{type}_baujat_{outcome}.png
• Contribution data: {output_dir}/{type}_baujat_{outcome}.csv

【Heterogeneity Contribution Ranking】(sorted by Q contribution in descending order)
Rank  Study                Result Contribution   Q Contribution   Judgment
─────────────────────────────────────────────────────
1     Smith 2020          0.85       3.42       ⚠️ Outlier
2     Jones 2021          0.32       1.15       Normal
...

【Recommendations】
{Recommendations based on analysis results}

═══════════════════════════════════════════
```

---

## R Script Dependencies

The following R packages need to be installed:
- meta
- metafor
- ggplot2
- ggrepel (for label overlap avoidance)

If the user environment lacks these packages, suggest running:
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
- If a file is produced, prefer a deterministic output name such as `meta_baujat_plot_result.md` unless the skill documentation defines a better convention.
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
python scripts/baujat_plot_fallback.py --help
```

Expected output format:

```text
Result file: meta_baujat_plot_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
