---
name: reagent-expiry-alert
description: Scan reagent barcodes or IDs, log expiration dates, and generate multi-level alerts before reagent expiry to support laboratory inventory management.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Reagent Expiry Alert

Scan reagent bottle barcodes or IDs, log expiration dates, and alert before expiry to support safe laboratory inventory management.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Use this skill when logging a new reagent with its expiry date into the inventory.
- Use this skill when checking for reagents approaching expiration (30/60/90-day alerts).
- Do not use this skill to manage controlled substances, biological hazards requiring special disposal, or reagents subject to regulatory chain-of-custody requirements.

## Workflow

1. Confirm the reagent barcode/ID, expiry date, and action (scan/log or check alerts).
2. Validate that the request is for reagent expiry tracking, not chemical safety assessment or disposal guidance.
3. **Date validation:** If `--expiry` is provided, validate that it is a valid YYYY-MM-DD date. If the date is in the past, emit a warning: "This reagent is already expired as of [date]. It will be logged with an Expired alert status."
4. Log the reagent or run the alert check using the packaged script.
5. Return expiration status, alert level, and reorder recommendations.
6. If inputs are incomplete, state which fields are missing and request only the minimum additional information.

## Usage

```text
# Log a new reagent
python scripts/main.py --scan "REAGENT-001" --name "Tris Buffer" --expiry 2025-12-31 --location "Shelf A"

# Check for upcoming expirations
python scripts/main.py --check-alerts --alert-days 30

# Check with custom alert window
python scripts/main.py --check-alerts --alert-days 60
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--scan` | string | No | — | Reagent barcode or ID |
| `--name` | string | No | — | Reagent name |
| `--expiry` | date | No | — | Expiration date (YYYY-MM-DD) |
| `--location` | string | No | — | Storage location |
| `--quantity` | string | No | — | Quantity on hand |
| `--check-alerts` | flag | No | — | Check for upcoming expirations |
| `--alert-days` | integer | No | 30 | Days before expiry to alert |

## Alert Levels

- 🔴 Expired — reagent past expiry date
- 🟠 Critical — expiring within 30 days
- 🟡 Warning — expiring within 60 days
- 🟢 OK — expiring beyond 60 days

## Output

- Expiration alert report with alert level per reagent
- Inventory summary
- Reorder recommendations for critical/expired items

## Stress-Case Rules

For complex multi-constraint requests, always include these explicit blocks:

1. Assumptions
2. Reagents Checked
3. Alert Report
4. Reorder Recommendations
5. Risks and Manual Checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate expiry dates, inventory counts, or reorder thresholds.

## Input Validation

This skill accepts: reagent barcode/ID and expiry date for logging, or a check-alerts request for inventory review.

If the request does not involve reagent expiry tracking — for example, asking for chemical hazard assessment, waste disposal guidance, or controlled substance management — do not proceed with the workflow. Instead respond:
> "reagent-expiry-alert is designed to log reagent expiry dates and generate alerts before expiration. Your request appears to be outside this scope. Please provide a reagent ID and expiry date, or use a more appropriate tool."

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
