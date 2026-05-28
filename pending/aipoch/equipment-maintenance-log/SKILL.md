---
name: equipment-maintenance-log
description: Track lab equipment calibration dates and send maintenance reminders for pipettes, balances, centrifuges, and other instruments. Validates date formats and supports update/delete operations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Equipment Maintenance Log

Track calibration dates for pipettes, balances, centrifuges and send maintenance reminders.

## Quick Check

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --add "Pipette P100" --calibration-date 2024-01-15 --interval 12
```

## When to Use

- Track lab equipment calibration schedules
- Check for overdue or upcoming maintenance
- Generate maintenance reminder reports
- Maintain compliance records for audits

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--add` | string | * | Equipment name to add |
| `--calibration-date` | string | * | Last calibration date (YYYY-MM-DD format required) |
| `--interval` | int | * | Calibration interval in months |
| `--location` | string | No | Equipment location |
| `--update` | string | ** | Equipment name to update calibration date |
| `--delete` | string | ** | Equipment name to remove from log |
| `--check` | flag | ** | Check for upcoming maintenance |
| `--list` | flag | ** | List all equipment |
| `--report` | flag | ** | Generate compliance report (JSON) |

\* Required when adding or updating equipment
\** Alternative operations (mutually exclusive with --add)

> **Date validation:** `--calibration-date` must be in YYYY-MM-DD format. Invalid dates (e.g., 2024-13-45) are rejected at input time with a clear error message. The script validates the date before storing it.

## Usage

```bash
# Add equipment
python scripts/main.py --add "Pipette P100" --calibration-date 2024-01-15 --interval 12

# Add with location
python scripts/main.py --add "Balance XS205" --calibration-date 2024-03-01 --interval 6 --location "Lab 3B"

# Check maintenance status
python scripts/main.py --check

# List all equipment
python scripts/main.py --list

# Update calibration date after servicing
python scripts/main.py --update "Pipette P100" --calibration-date 2025-01-15

# Remove decommissioned equipment
python scripts/main.py --delete "Balance XS205"

# Generate compliance report
python scripts/main.py --report
```

## Output

- Maintenance schedule with next due dates
- Overdue alerts (past calibration date)
- Upcoming reminders (30/60/90 days)
- Compliance report (JSON) with equipment name, location, last calibration date, interval, next due date, and status

## Compliance Report Format

```json
{
  "generated": "2025-01-15",
  "equipment": [
    {
      "name": "Pipette P100",
      "location": "Lab 3B",
      "last_calibration": "2024-01-15",
      "interval_months": 12,
      "next_due": "2025-01-15",
      "status": "DUE"
    }
  ],
  "summary": {
    "total": 1,
    "overdue": 0,
    "due_30_days": 1,
    "compliant": 0
  }
}
```

## Stress-Case Rules

For complex multi-constraint requests, always include these blocks:

1. Assumptions
2. Hard Constraints
3. Maintenance Check Path
4. Compliance Risks
5. Unresolved Items

## Input Validation

This skill accepts requests involving lab equipment calibration tracking, maintenance scheduling, and reminder generation.

If the user's request does not involve equipment maintenance logging — for example, asking to order supplies, write SOPs, or manage personnel schedules — do not proceed with the workflow. Instead respond:
> "equipment-maintenance-log is designed to track lab equipment calibration dates and maintenance schedules. Your request appears to be outside this scope. Please provide equipment name and calibration details, or use a more appropriate tool for your task."

## Output Requirements

Every final response must include:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If `--add` is used without `--calibration-date` or `--interval`, report exactly which fields are missing before proceeding.
- If `--calibration-date` is not in YYYY-MM-DD format, reject with: "Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)."
- If `--update` or `--delete` references an equipment name not in the log, report "Equipment not found" and list available names.
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
