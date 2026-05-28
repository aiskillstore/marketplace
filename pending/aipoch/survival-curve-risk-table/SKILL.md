---
name: survival-curve-risk-table
description: Analyze data with `survival-curve-risk-table` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Survival Curve Risk Table Generator

## When to Use

- Use this skill when the task needs Automatically align and add "Number at risk" table below Kaplan-Meier.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Analyze data with `survival-curve-risk-table` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `lifelines`: `unspecified`. Declared in `requirements.txt`.
- `matplotlib`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `pandas`: `unspecified`. Declared in `requirements.txt`.
- `pil`: `unspecified`. Declared in `requirements.txt`.
- `pillow`: `unspecified`. Declared in `requirements.txt`.
- `seaborn`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/survival-curve-risk-table"
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

## Function Overview

Automatically add "Number at risk" tables to Kaplan-Meier survival curves that meet clinical oncology journal standards. Automatically align time points and generate publication-quality combined figures.

## Usage Trigger Conditions

- Need to add number at risk tables to KM survival curves
- Generate survival plots that meet journal requirements such as NEJM, Lancet, JCO
- Risk tables needed in clinical trial reports
- Medical paper chart standardization before submission
- Precise alignment of risk tables with survival curve time axis

## Core Functions

### 1. Automatic Number at Risk Calculation
- Automatically calculate number at risk at each time point from survival data
- Support right-censored data processing
- Count remaining observed subjects by group
- Automatic handling of censoring events

### 2. Journal Standard Formats
- **NEJM Standard**: Clean time axis, groups arranged horizontally
- **Lancet Standard**: Complete statistical information, vertical alignment
- **JCO Standard**: Censoring symbols marked, group comparison
- Support custom journal templates

### 3. Precise Alignment
- Time axis precisely aligned with curve X-axis
- Automatic adjustment of table spacing and font size
- Responsive layout adapts to different image sizes
- Support horizontal/vertical layouts

### 4. Output Formats
- High-quality PNG/JPEG images
- PDF vector graphics
- SVG editable format
- PowerPoint embeddable format

## Usage

### Example 1: Basic Risk Table Generation

```text

# Example invocation: python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --output risk_table.png
```

### Example 2: Specify Journal Style

```text

# Example invocation: python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col status \
    --group-col arm \
    --style NEJM \
    --time-points 0,6,12,18,24,30,36 \
    --output figure_1a.pdf
```

### Example 3: Combined Figure Generation (Curve + Risk Table)

```text

# Example invocation: python scripts/main.py \
    --input survival_data.csv \
    --time-col months \
    --event-col death \
    --group-col group \
    --km-plot km_curve.png \
    --combine \
    --output combined_figure.png
```

### Example 4: Batch Generate Multi-Timepoint Tables

```text

# Example invocation: python scripts/main.py \
    --input survival_data.csv \
    --time-col time \
    --event-col event \
    --group-col treatment \
    --time-points 0,12,24,36,48,60 \
    --format both \
    --output-dir ./output/
```

### Example 5: Using Existing Survival Data (Python API)

```python
from scripts.main import RiskTableGenerator

# Initialize generator
generator = RiskTableGenerator(
    style="JCO",
    time_points=[0, 6, 12, 18, 24, 30],
    figure_size=(8, 6)
)

# Load survival data
generator.load_data(
    df=survival_df,
    time_col="time",
    event_col="event",
    group_col="treatment_arm"
)

# Generate risk table
generator.generate_risk_table(
    output_path="risk_table.png",
    show_censored=True
)

# Generate combined figure (KM curve + risk table)
generator.generate_combined_plot(
    km_plot_path="km_curve.png",
    output_path="combined_figure.pdf"
)
```

## Input Data Format

### CSV Format Example

```csv
time,event,treatment_arm
0,0,Experimental
3.2,1,Experimental
5.1,0,Experimental
12.3,1,Control
18.7,0,Control
24.0,1,Experimental
...
```

### Required Columns

| Column Name | Description | Type |
|------|------|------|
| time | Follow-up time (months) | Numeric |
| event | Event occurrence flag | 0=Censored, 1=Event |
| group | Treatment group (optional) | Text/Categorical |

### Supported Data Formats

- CSV (.csv)
- Excel (.xlsx, .xls)
- SAS (.sas7bdat)
- RData (.rda, .rds)
- Python pickle (.pkl)

## Journal Style Configuration

### NEJM Style

```json
{
  "style": "NEJM",
  "font_family": "Helvetica",
  "font_size": 8,
  "time_points": [0, 6, 12, 18, 24, 30, 36],
  "table_height": 0.15,
  "show_grid": false,
  "separator_lines": true
}
```

### Lancet Style

```json
{
  "style": "Lancet",
  "font_family": "Times New Roman",
  "font_size": 9,
  "time_points": [0, 12, 24, 36, 48, 60],
  "table_height": 0.18,
  "show_grid": true,
  "header_bold": true
}
```

### JCO Style

```json
{
  "style": "JCO",
  "font_family": "Arial",
  "font_size": 8,
  "time_points": [0, 6, 12, 18, 24, 30],
  "table_height": 0.16,
  "show_censored": true,
  "censor_symbol": "+"
}
```

## Command Line Parameters

### Required Parameters

| Parameter | Description | Example |
|------|------|------|
| `--input` | Input data file path | `data.csv` |
| `--time-col` | Time column name | `time` |
| `--event-col` | Event column name | `event` |

### Optional Parameters

| Parameter | Description | Default Value |
|------|------|--------|
| `--group-col` | Group column name | `None` |
| `--output` | Output file path | `risk_table.png` |
| `--style` | Journal style | `NEJM` |
| `--time-points` | Time point list | Auto-calculated |
| `--format` | Output format | `png` |
| `--width` | Image width | `8` (inches) |
| `--height` | Image height | `6` (inches) |
| `--dpi` | Image resolution | `300` |
| `--font-size` | Font size | `8` |
| `--show-censored` | Show censored count | `False` |
| `--combine` | Combine with KM curve | `False` |
| `--km-plot` | KM curve image path | `None` |

## Output Format

### Standalone Risk Table
```
┌─────────────────────────────────────────────────────────┐
│  Number at risk                                         │
├─────────┬─────┬─────┬─────┬─────┬─────┬─────┬───────────┤
│ Group   │  0  │ 12  │ 24  │ 36  │ 48  │ 60  │ 72 (mo)   │
├─────────┼─────┼─────┼─────┼─────┼─────┼─────┼───────────┤
│ Exp     │ 150 │ 142 │ 128 │ 105 │  89 │  72 │  58       │
│ Control │ 148 │ 135 │ 118 │  92 │  76 │  61 │  45       │
└─────────┴─────┴─────┴─────┴─────┴─────┴─────┴───────────┘
```

### Combined Figure Layout
```
┌─────────────────────────────────────┐
│                                     │
│     Kaplan-Meier Survival Curve     │
│                                     │
│    ━━━━━━━━━  Experimental         │
│    ─ ─ ─ ─ ─  Control              │
│                                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Number at risk                      │
│ Exp    150  142  128  105   89   72 │
│ Ctrl   148  135  118   92   76   61 │
│         0   12   24   36   48   60  │
└─────────────────────────────────────┘
```

## Algorithm Description

### Number at Risk Calculation

```
For each time point t:
    For each group g:
        N_at_risk(t, g) = N_total(g) 
                          - Σ(patients with events occurring ≤ t)
                          - Σ(patients censored occurring < t)
```

### Time Point Selection Strategy

1. **Auto Mode**: Automatically select equally spaced time points based on data distribution
2. **Fixed Interval**: Select at specified intervals (e.g., every 6 months)
3. **Custom**: User-specified specific time points
4. **Event-driven**: Select based on event occurrence density

## Quality Checklist

- [ ] Time axis precisely aligned with X-axis
- [ ] Number at risk calculations correct (can manually spot-check)
- [ ] Group labels clear and readable
- [ ] Font size meets journal requirements (≥8pt)
- [ ] Image resolution ≥300 DPI
- [ ] Color contrast meets accessibility standards
- [ ] Censoring marks (if present) clearly distinguishable
- [ ] Export format meets submission requirements

## Journal-Specific Notes

### NEJM
- Minimum font size 8pt
- Recommended time unit: months
- Fixed spacing between risk table and curve

### Lancet
- Minimum font size 9pt
- Support multi-group display (max 4 groups)
- Table grid lines optional

### JCO
- Need to label censoring information
- Support risk table + censoring table double-layer structure
- Recommend labeling median follow-up time

## FAQ

### Q: How are time points automatically determined?
A: Default uses quantiles in the data (0%, 25%, 50%, 75%, 100%) or fixed intervals (e.g., every 12 months)

### Q: How to handle multiple groups?
A: Automatically detect group column, support up to 6 groups. Exceeding automatically uses pagination or reduced font

### Q: Can it work with KM curves generated by Python/R?
A: Yes, supports importing external KM curve images for combination

## Dependency Requirements

```
numpy >= 1.20.0
pandas >= 1.3.0
matplotlib >= 3.4.0
seaborn >= 0.11.0
lifelines >= 0.27.0  (optional, for survival analysis)
Pillow >= 8.0.0      (image processing)
```

## Related Tools

- lifelines: Python survival analysis library
- survminer: R survival curve visualization
- ggsurvplot: ggplot2 survival plot extension

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

This skill accepts requests that match the documented purpose of `survival-curve-risk-table` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `survival-curve-risk-table` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
