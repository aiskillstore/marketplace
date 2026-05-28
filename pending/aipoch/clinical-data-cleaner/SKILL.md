---
name: clinical-data-cleaner
description: Use when cleaning clinical trial data, preparing data for FDA/EMA submission, standardizing SDTM datasets, handling missing values in clinical studies, detecting outliers in lab results, or converting raw CRF data to CDISC format. Cleans and standardizes clinical trial data for regulatory compliance with audit trails.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Clinical Data Cleaner

Clean, validate, and standardize clinical trial data to meet CDISC SDTM standards for regulatory submissions to FDA or EMA.

## When to Use

- Use this skill when the task needs Use when cleaning clinical trial data, preparing data for FDA/EMA submission, standardizing SDTM datasets, handling missing values in clinical studies, detecting outliers in lab results, or converting raw CRF data to CDISC format. Cleans and standardizes clinical trial data for regulatory compliance with audit trails.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when cleaning clinical trial data, preparing data for FDA/EMA submission, standardizing SDTM datasets, handling missing values in clinical studies, detecting outliers in lab results, or converting raw CRF data to CDISC format. Cleans and standardizes clinical trial data for regulatory compliance with audit trails.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `pandas`: `unspecified`. Declared in `requirements.txt`.
- `scipy`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Data Analytics/clinical-data-cleaner"
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
python scripts/main.py --help
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.main import ClinicalDataCleaner

# Initialize for Demographics domain
cleaner = ClinicalDataCleaner(domain='DM')

# Clean data with default settings
cleaned = cleaner.clean(raw_data)

# Save with audit trail
cleaner.save_report('output.csv')
```

## Core Capabilities

### 1. SDTM Domain Validation

```python
cleaner = ClinicalDataCleaner(domain='DM')  # or 'LB', 'VS'
is_valid, missing = cleaner.validate_domain(data)
```

**Required Fields:**
- **DM**: STUDYID, USUBJID, SUBJID, RFSTDTC, RFENDTC, SITEID, AGE, SEX, RACE
- **LB**: STUDYID, USUBJID, LBTESTCD, LBCAT, LBORRES, LBORRESU, LBSTRESC, LBDTC
- **VS**: STUDYID, USUBJID, VSTESTCD, VSORRES, VSORRESU, VSSTRESC, VSDTC

### 2. Missing Value Handling

```python
cleaner = ClinicalDataCleaner(
    domain='DM',
    missing_strategy='median'  # mean, median, mode, forward, drop
)
cleaned = cleaner.handle_missing_values(data)
```

### 3. Outlier Detection

```python
cleaner = ClinicalDataCleaner(
    domain='LB',
    outlier_method='domain',  # iqr, zscore, domain
    outlier_action='flag'     # flag, remove, cap
)
flagged = cleaner.detect_outliers(data)
```

**Clinical Thresholds:**
| Parameter | Range | Unit |
|-----------|-------|------|
| Glucose | 50-500 | mg/dL |
| Hemoglobin | 5-20 | g/dL |
| Systolic BP | 70-220 | mmHg |

### 4. Date Standardization

```python
standardized = cleaner.standardize_dates(data)

# Converts to ISO 8601: 2023-01-15T09:30:00
```

### 5. Complete Pipeline

```python
cleaner = ClinicalDataCleaner(
    domain='DM',
    missing_strategy='median',
    outlier_method='iqr',
    outlier_action='flag'
)
cleaned_data = cleaner.clean(data)
cleaner.save_report('output.csv')
```

**Output Files:**
- `output.csv` - Cleaned SDTM data
- `output.report.json` - Audit trail for regulatory submission

## CLI Usage

```text

# Clean demographics
python scripts/main.py \
  --input dm_raw.csv \
  --domain DM \
  --output dm_clean.csv \
  --missing-strategy median \
  --outlier-method iqr \
  --outlier-action flag

# Clean lab data with clinical thresholds
python scripts/main.py \
  --input lb_raw.csv \
  --domain LB \
  --output lb_clean.csv \
  --outlier-method domain
```

## Common Patterns

See [references/common-patterns.md](references/common-patterns.md) for detailed examples:
- Regulatory Submission Preparation
- Interim Analysis Data Preparation
- Database Migration Cleanup
- External Lab Data Integration

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to:
- Validation failures
- Date parsing errors
- Memory errors with large datasets
- Outlier detection issues

## Quality Checklist

**Pre-Cleaning:**
- [ ] IACUC approval obtained (animal studies)
- [ ] Sample size adequately powered
- [ ] Randomization method documented

**Post-Cleaning:**
- [ ] Validate against CDISC SDTM IG
- [ ] Review all cleaning actions in audit trail
- [ ] Test import to analysis software

## References

- `references/sdtm_ig_guide.md` - CDISC SDTM Implementation Guide
- `references/domain_specs.json` - Domain-specific field requirements
- `references/outlier_thresholds.json` - Clinical outlier thresholds
- `references/common-patterns.md` - Detailed usage patterns
- `references/troubleshooting.md` - Problem-solving guide

---

**Skill ID**: 189 | **Version**: 2.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `clinical-data-cleaner` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `clinical-data-cleaner` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
