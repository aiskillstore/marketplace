---
name: date-calculator
description: Calculate medical date windows including gestational age, estimated delivery dates, and follow-up visit scheduling. Produces structured JSON output for clinical research and trial coordination workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Date Calculator

Calculate medical date windows for clinical research: gestational age from LMP, estimated delivery dates, and follow-up visit scheduling with configurable window sizes.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Computing gestational age and estimated delivery date from last menstrual period
- Scheduling follow-up visit windows for clinical trials
- Generating date ranges for protocol-defined visit windows

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Note on group parameter:** If `--group` is not provided, log-rank test and Cox regression are skipped. Single-arm KM only. An informational note will be included in the output.

**Fallback template:** If `scripts/main.py` fails or a required parameter is absent, report: (a) which parameter is missing, (b) what partial calculation is still valid, (c) the manual formula for the requested calculation type.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--type`, `-t` | string | Yes | Calculation type: `gestational` or `followup` |
| `--date`, `-d` | string | Yes | Reference date in `YYYY-MM-DD` format |
| `--weeks` | int | No | Follow-up interval in weeks (default: 4; must be ≥ 1) |
| `--window-days` | int | No | Visit window size in days (default: 7) |
| `--timezone` | string | No | Timezone for calculation (default: UTC) |
| `--output`, `-o` | string | No | Output JSON file path (default: stdout) |

## Usage

```text
# Gestational age from LMP
python scripts/main.py --type gestational --date 2024-01-15

# 4-week follow-up window
python scripts/main.py --type followup --date 2024-03-01

# Custom 6-week follow-up with ±5-day window
python scripts/main.py --type followup --date 2024-03-01 --weeks 6 --window-days 5
```

## Output Format

**Gestational:**
```json
{
  "lmp_date": "2024-01-15",
  "gestational_age": "12 weeks 3 days",
  "gestational_age_days": 87,
  "estimated_delivery_date": "2024-10-21",
  "calculation_date": "2024-04-12",
  "warning": "LMP date is in the future; gestational age calculated from today may be negative or unexpected"
}
```

**Follow-up:**
```json
{
  "start_date": "2024-03-01",
  "followup_weeks": 4,
  "window_start": "2024-03-29",
  "window_end": "2024-04-05",
  "window_range": "2024-03-29 to 2024-04-05"
}
```

## Output Requirements

Every response must make these explicit:

- Objective and deliverable
- Inputs used and assumptions introduced
- Workflow or decision path taken
- Core result: calculated dates and windows
- Constraints, risks, caveats (e.g., timezone assumptions, calendar edge cases)
- Unresolved items and next-step checks

## Input Validation

This skill accepts: medical date calculation requests specifying a calculation type (`gestational` or `followup`) and a reference date in `YYYY-MM-DD` format.

If the request does not involve medical date window calculation — for example, asking to schedule general appointments, perform time-zone conversions unrelated to clinical dates, or calculate non-medical intervals — do not proceed. Instead respond:

> "`date-calculator` is designed to calculate medical date windows for clinical research. Your request appears to be outside this scope. Please provide a calculation type and reference date, or use a more appropriate tool for your task."

**Validation rules:**
- Date must be in `YYYY-MM-DD` format; invalid formats are rejected with exit code 1.
- If LMP date is in the future, a `warning` field is included in the output.
- `--weeks` must be ≥ 1; zero or negative values are rejected with a clear error message.
- `--timezone` defaults to UTC; use pytz timezone names (e.g., `America/New_York`).

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Response Template

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks
