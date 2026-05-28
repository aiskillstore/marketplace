---
name: survival-analysis-km
description: Kaplan-Meier survival analysis tool for clinical and biological research. Generates publication-ready survival curves with statistical tests.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Survival Analysis (Kaplan-Meier)

Kaplan-Meier survival analysis tool for clinical and biological research. Generates publication-ready survival curves with statistical tests.

## When to Use

- Use this skill when the task needs Kaplan-Meier survival analysis tool for clinical and biological research. Generates publication-ready survival curves with statistical tests.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Kaplan-Meier survival analysis tool for clinical and biological research. Generates publication-ready survival curves with statistical tests.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `lifelines`: Core survival analysis library
- `matplotlib`, `seaborn`: Visualization
- `pandas`, `numpy`: Data handling
- `scipy`: Statistical tests

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/survival-analysis-km"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py

# Example invocation: python scripts/main.py --help

# Example invocation: python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features

- **Kaplan-Meier Curve Generation**: Publication-quality survival plots with confidence intervals
- **Statistical Tests**: Log-rank test, Wilcoxon test, Peto-Peto test
- **Hazard Ratios**: Cox proportional hazards regression with 95% CI
- **Summary Statistics**: Median survival time, restricted mean survival time (RMST)
- **Multi-group Analysis**: Supports 2+ comparison groups
- **Risk Tables**: Optional at-risk table below curves

## Usage

### Python Script

```text

# Example invocation: python scripts/main.py --input data.csv --time time_col --event event_col --group group_col --output results/
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--input` | Input CSV file path | Yes |
| `--time` | Column name for survival time | Yes |
| `--event` | Column name for event indicator (1=event, 0=censored) | Yes |
| `--group` | Column name for grouping variable | Optional |
| `--output` | Output directory for results | Yes |
| `--conf-level` | Confidence level (default: 0.95) | Optional |
| `--risk-table` | Include risk table in plot | Optional |

### Input Format

CSV with columns:
- **Time column**: Numeric, time to event or censoring
- **Event column**: Binary (1 = event occurred, 0 = censored/right-censored)
- **Group column**: Categorical variable for stratification

Example:
```csv
patient_id,time_months,death,treatment_group
P001,24.5,1,Drug_A
P002,36.2,0,Drug_A
P003,18.7,1,Placebo
```

### Output Files

- `km_curve.png`: Kaplan-Meier survival curve
- `km_curve.pdf`: Vector version for publications
- `survival_stats.csv`: Statistical summary (median survival, confidence intervals)
- `hazard_ratios.csv`: Cox regression results with HR and 95% CI
- `logrank_test.csv**: Pairwise comparison p-values
- `report.txt**: Human-readable summary report

## Technical Details

### Statistical Methods

1. **Kaplan-Meier Estimator**: Non-parametric maximum likelihood estimate of survival function
   - Product-limit estimator: Ŝ(t) = Π(tᵢ≤t) (1 - dᵢ/nᵢ)
   - Greenwood's formula for variance estimation

2. **Log-Rank Test**: Most widely used test for comparing survival curves
   - Null hypothesis: No difference between groups
   - Weighted by number at risk at each event time

3. **Cox Proportional Hazards**: Semi-parametric regression model
   - h(t|X) = h₀(t) × exp(β₁X₁ + β₂X₂ + ...)
   - Proportional hazards assumption checked via Schoenfeld residuals

### Technical Difficulty: High ⚠️

This skill involves advanced statistical modeling. Results should be reviewed by a biostatistician, especially for:
- Proportional hazards assumption violations
- Small sample sizes (< 30 per group)
- Heavy censoring (> 50%)
- Time-varying covariates

## References

See `references/` folder for:
- Kaplan EL, Meier P (1958) original paper
- Cox DR (1972) regression models paper
- Sample datasets for testing
- Clinical reporting guidelines (ATN, CONSORT)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | str | Required | Input CSV file path |
| `--time` | str | Required | Column name for survival time |
| `--event` | str | Required |  |
| `--group` | str | Required |  |
| `--output` | str | Required | Output directory for results |
| `--conf-level` | float | 0.95 |  |
| `--risk-table` | str | Required | Include risk table in plot |
| `--figsize` | str | '10 |  |
| `--dpi` | int | 300 |  |

## Example

```text

# Basic survival curve

# Example invocation: python scripts/main.py \
  --input clinical_data.csv \
  --time overall_survival_months \
  --event death \
  --group treatment_arm \
  --output ./results/ \
  --risk-table
```

Output includes:
- Survival curves with 95% confidence bands
- Median survival: Drug A = 28.4 months (95% CI: 24.1-32.7), Placebo = 18.2 months (95% CI: 15.3-21.1)
- Log-rank test p-value: 0.0023
- Hazard ratio: 0.62 (95% CI: 0.45-0.85), p = 0.003

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `survival-analysis-km` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `survival-analysis-km` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.

## Inputs to Collect

- Required inputs: the user goal, the primary data or source file, and the requested output format.
- Optional inputs: output directory, formatting preferences, and validation constraints.
- If a required input is unavailable, return a short clarification request before continuing.

## Output Contract

- Return a short summary, the main deliverables, and any assumptions that materially affect interpretation.
- If execution is partial, label what succeeded, what failed, and the next safe recovery step.
- Keep the final answer within the documented scope of the skill.

## Validation and Safety Rules

- Validate identifiers, file paths, and user-provided parameters before execution.
- Do not fabricate results, metrics, citations, or downstream conclusions.
- Use safe fallback behavior when dependencies, credentials, or required inputs are missing.
- Surface any execution failure with a concise diagnosis and recovery path.
