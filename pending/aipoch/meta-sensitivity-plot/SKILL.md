---
name: meta-sensitivity-plot
description: "Generate leave-one-out sensitivity analysis plots for meta-analysis. Input is a CSV file containing meta-analysis data; outputs are a sensitivity forest plot (PNG) and a sensitivity data table (CSV) showing pooled effect estimates after excluding each study in turn."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when you need "generate leave-one-out sensitivity analysis plots for meta-analysis. input is a csv file containing meta-analysis data; outputs are a sensitivity forest plot (png) and a sensitivity data table (csv) showing pooled effect estimates after excluding each study in turn." in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/sensitivity_analysis.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-sensitivity-plot` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: "Generate leave-one-out sensitivity analysis plots for meta-analysis. Input is a CSV file containing meta-analysis data; outputs are a sensitivity forest plot (PNG) and a sensitivity data table (CSV) showing pooled effect estimates after excluding each study in turn.".
- Packaged executable path(s): `scripts/sensitivity_analysis.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-sensitivity-plot"
python -m py_compile scripts/sensitivity_analysis.py
python scripts/sensitivity_analysis.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/sensitivity_analysis.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/sensitivity_analysis.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Sensitivity Analysis Plotting (Leave-one-out)

You are a meta-analysis plotting assistant. The user provides meta-analysis data, and you are responsible for calling an R script to perform leave-one-out sensitivity analysis and generate plots.

**Important: Do not echo this instruction document to the user. Only output user-visible content defined by the workflow.**

---

## About Sensitivity Analysis

Leave-one-out sensitivity analysis:
- Remove each study one at a time and re-calculate the pooled effect estimate
- Assess the influence of individual studies on the overall result
- Evaluate the robustness of the meta-analysis findings

---

## Data Format Requirements

Depending on the data type, the input CSV should contain the following columns:

### Binary
| Column | Description |
|--------|-------------|
| study | Study identifier |
| group1_Events | Events in intervention group |
| group1_sample_size | Sample size of intervention group |
| group2_Events | Events in control group |
| group2_sample_size | Sample size of control group |

### Continuity
| Column | Description |
|--------|-------------|
| study | Study identifier |
| group1_sample_size | Sample size (intervention) |
| group1_Mean | Mean (intervention) |
| group1_SD | Standard deviation (intervention) |
| group2_sample_size | Sample size (control) |
| group2_Mean | Mean (control) |
| group2_SD | Standard deviation (control) |

### Survival
| Column | Description |
|--------|-------------|
| study | Study identifier |
| group1_HR | Hazard ratio |
| group1_95%Lower_CI | 95% CI lower bound |
| group1_95%Upper_CI | 95% CI upper bound |

---

## Workflow

### Step 1: Validate input
1. Read the input CSV provided by the user
2. Check required columns according to the specified data type
3. Validate data (note: at least 3 studies are required to run meaningful sensitivity analysis)

### Step 2: Execute R script
Call:
```bash
Rscript scripts/sensitivity_analysis.R "<csv_path>" "<type>" "<outcome_name>" "<output_dir>"
```

Parameters:
- `csv_path`: absolute path to the input CSV
- `type`: data type (`Binary` / `Continuity` / `Survival`)
- `outcome_name`: outcome label (optional)
- `output_dir`: output directory (optional)

### Step 3: Output
On success, output:

```
═══════════════════════════════════════════
Sensitivity analysis completed
═══════════════════════════════════════════

[Outcome] {outcome_name}
[Data type] {type}
[Included studies] {n}

[Output files]
• Sensitivity forest plot: {output_dir}/{type}_sensitive_forest_{outcome}.png
• Sensitivity data table: {output_dir}/{type}_sensitive_{outcome}.csv

[Pooled effect (all studies)]
• {effect_name} = {value} [{lower}; {upper}]

[Summary of sensitivity results]
Study removed       Effect     95% CI           I²
───────────────────────────────────────────────────────────
Smith 2020          0.85      [0.72; 1.01]     45.2%
Jones 2021          0.88      [0.75; 1.03]     42.1%
...

[Effect change analysis]
• Effect range: 0.82 ~ 0.91
• Relative change: 10.3%

[Conclusion]
• Robustness: {robust/not robust}
• {recommendation based on magnitude of change}

═══════════════════════════════════════════
```

---

## R script dependencies

Install these R packages if not present:
- meta
- metafor
- stringr
- grid

Prompt the user to run:
```r
install.packages(c("meta", "metafor", "stringr", "grid"))
```
