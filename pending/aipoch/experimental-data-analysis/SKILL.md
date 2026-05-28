---
name: experimental-data-analysis
description: Statistical analysis and reporting for experimental datasets; use when you need to interpret experimental results, test significance (t-tests/ANOVA), or generate reproducible reports.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have experimental results in CSV form and need a reproducible end-to-end analysis workflow (clean → test → report).
- You need to compare two conditions (independent or paired) and determine statistical significance with effect sizes.
- You need to compare 3+ groups (one-way) or multiple factors (multi-way) using ANOVA and post-hoc multiple comparisons.
- You must validate assumptions (normality, homogeneity of variance) and document them in a report.
- You need standardized run outputs (timestamped run directories) for traceability and auditing.

## Key Features

- Reproducible, run-based execution that writes all artifacts into `outputs/runs/<timestamp>/`.
- Data preparation guidance: missing values, outliers, and variable type identification (continuous/categorical; grouping factors).
- Descriptive statistics: means, standard deviations, confidence intervals, and grouped summary tables.
- Inferential testing:
  - t-tests (independent/paired) and non-parametric alternatives when assumptions fail.
  - ANOVA (one-way and multi-way) with post-hoc testing (e.g., Tukey).
- Reporting outputs: test statistics, p-values, effect sizes, tables, charts, and explicit assumption notes.
- Reference materials for method selection and reporting templates:
  - `references/stats-method-selection.md`
  - `references/reporting-template.md`

## Dependencies

- Python 3.10+
- pandas >= 2.0
- numpy >= 1.24
- scipy >= 1.10

## Example Usage

The workflow is run-directory based. Initialize a new run, then analyze using the latest run by default.

```bash
# 1) Initialize a new run directory with sample inputs/config
python scripts/init_run.py

# 2) Run analysis (uses the latest outputs/runs/<timestamp>/ by default)
python scripts/analyze_experiment.py
```

Expected directory conventions:

- A new run directory is created at: `outputs/runs/<timestamp>/`
- Configuration file location: `outputs/runs/<timestamp>/config.json`
- All intermediate and final artifacts (config, inputs, outputs, figures, tables) must be written inside the run directory.
- Writing outside the run directory is prohibited.

## Implementation Details

### Reproducible Run Management

- Before each execution, run:
  - `scripts/init_run.py` to create `outputs/runs/<timestamp>/` and populate initial inputs/config.
- Analysis scripts default to the latest run directory under `outputs/runs/` unless explicitly overridden (if supported by the script).

### Analysis Pipeline

1. **Data Preparation**
   - Handle missing values (e.g., drop, impute, or flag) according to the experimental design.
   - Detect and treat outliers (e.g., robust rules, domain thresholds), documenting any exclusions.
   - Identify variable roles:
     - Outcome variable(s): typically continuous measurements.
     - Grouping factors: categorical condition labels (treatment/control, timepoint, genotype, etc.).

2. **Descriptive Statistics**
   - Compute summary metrics per group:
     - Mean, standard deviation, and confidence intervals (commonly 95% CI).
   - Produce grouped summary tables suitable for reporting.

3. **Inferential Statistics**
   - **Two-group comparisons**
     - Use an independent t-test for separate groups.
     - Use a paired t-test for repeated measures / matched pairs.
     - If assumptions are violated, switch to an appropriate non-parametric alternative.
   - **Multi-group / multi-factor comparisons**
     - Use one-way ANOVA for a single factor with 3+ levels.
     - Use multi-way ANOVA when multiple factors are present.
   - **Multiple comparisons**
     - Apply post-hoc procedures (e.g., Tukey) after ANOVA when needed.
     - Define and document the multiple-comparison control strategy.

4. **Assumption Checks and Reporting Standards**
   - Validate and report:
     - Normality (per group or model residuals, as appropriate).
     - Homogeneity of variance.
   - Report, at minimum:
     - Test statistic, degrees of freedom (if applicable), p-value.
     - Effect size(s) and confidence intervals where applicable.
   - Retain analysis code and random seeds to ensure reproducibility.