---
name: lab-inventory-predictor
description: Predict depletion time of critical lab reagents based on historical usage frequency, and automatically generate purchase alerts when stock falls below safety thresholds.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Lab Inventory Predictor

Predicts reagent depletion time by analyzing historical usage frequency, and automatically generates reminders when purchases are needed.

## Input Validation

This skill accepts: lab reagent inventory data (stock levels, usage records) for the purpose of predicting depletion dates and generating purchase alerts.

If the user's request does not involve lab reagent inventory management or depletion prediction — for example, asking to analyze experimental results, manage equipment, or perform general data analysis — do not proceed with the workflow. Instead respond:
> "lab-inventory-predictor is designed to predict reagent depletion and generate purchase alerts based on usage history. Your request appears to be outside this scope. Please provide reagent inventory data, or use a more appropriate tool for your task."

Do not continue the workflow when the request is out of scope, missing the required `--action` parameter, or would require unsupported assumptions. For missing inputs, state exactly which fields are missing.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --action status
```

## Prerequisites

- **Python 3.8+ is strictly required** (uses `dataclasses` module). On Python 3.6 the script will fail at import with `ModuleNotFoundError`. Upgrade with `pyenv install 3.8` or `conda create -n lab python=3.8`.
- The script should include a version guard: `if sys.version_info < (3, 8): sys.exit('Error: Python 3.8+ required')` before the dataclasses import.
- No external dependencies (uses only standard library)

```text
pip install -r requirements.txt
```

## When to Use

- Predict when lab reagents will run out based on historical consumption data
- Generate purchase alerts before reagents deplete below safety thresholds
- Track stock levels and usage history for multiple reagents
- Generate inventory reports in text, JSON, or CSV format

## Workflow

1. **Validate input** — confirm the request is within scope before any processing.
2. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Core Capabilities

1. **Inventory Tracking** — Record current reagent stock levels
2. **Usage Frequency Analysis** — Calculate consumption rate based on experiment records
3. **Depletion Prediction** — Predict reagent depletion date based on consumption rate
4. **Purchase Alerts** — Generate alerts before reagents are about to deplete
5. **Safety Stock Alerts** — Alert when inventory falls below safety threshold

## Usage

### Command Line

```text
# View all reagent status
python scripts/main.py --action status

# Add or update reagent information
python scripts/main.py --action add-reagent \
  --name "PBS Buffer" \
  --current-stock 500 \
  --unit "ml" \
  --safety-days 7

# Record experiment consumption
python scripts/main.py --action record-usage \
  --name "PBS Buffer" \
  --amount 50 \
  --experiment "Cell Culture Experiment #2024-001"

# Get purchase alerts
python scripts/main.py --action alerts

# Generate prediction report
python scripts/main.py --action report
```

### Python API

```python
from skills.lab_inventory_predictor import InventoryPredictor

predictor = InventoryPredictor("/path/to/inventory.json")
predictor.add_reagent(name="PBS Buffer", current_stock=500, unit="ml", safety_days=7, lead_time_days=3)
predictor.record_usage("PBS Buffer", 50, "Experiment #001")
prediction = predictor.predict_depletion("PBS Buffer")
print(f"Predicted depletion time: {prediction['depletion_date']}")
alerts = predictor.get_alerts()
```

## Parameters

### Global Parameters
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--action` | string | - | Yes | Action: status, add-reagent, record-usage, alerts, report |
| `--data-file` | string | ~/.openclaw/workspace/data/lab-inventory.json | No | Path to inventory data file (must be within workspace; `../` paths rejected) |

### add-reagent Action
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--name` | string | - | Yes | Reagent name |
| `--current-stock` | float | - | Yes | Current stock quantity |
| `--unit` | string | - | Yes | Unit of measurement (ml, mg, etc.) |
| `--safety-days` | int | 7 | No | Safety buffer days |
| `--lead-time-days` | int | 3 | No | Expected delivery time |
| `--safety-stock` | float | - | No | Safety stock threshold |

### record-usage Action
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--name` | string | - | Yes | Reagent name |
| `--amount` | float | - | Yes | Amount consumed |
| `--experiment` | string | - | No | Experiment identifier |

### report Action
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--output`, `-o` | string | stdout | No | Output file path |
| `--format` | string | text | No | Output format (text, json, csv) |

## Prediction Algorithm

### Consumption Rate
```
daily_consumption = Σ(usage_amount) / days_span
```

### Depletion Date
```
days_until_depletion = current_stock / daily_consumption
depletion_date = today + days_until_depletion
```

### Purchase Alert Trigger Conditions
1. **Time-based**: When `days_until_depletion <= safety_days + lead_time_days`
2. **Stock-based**: When `current_stock <= safety_stock`

### Confidence Warning
When a reagent has **fewer than 3 usage records**, the prediction is flagged as `LOW_CONFIDENCE`. The output will include:
> "Warning: Only [N] usage records available for [reagent]. Prediction reliability is low — collect more usage data before relying on this estimate."

Each LOW_CONFIDENCE prediction must include an inline risk note adjacent to the prediction result, not only in the aggregate Risks section.

## Fallback Behavior

If `scripts/main.py` fails or required inputs are incomplete:
1. Report the exact failure point and error message.
2. State what can still be completed (e.g., status check without prediction).
3. Manual fallback: verify the inventory JSON file exists at the configured path, then re-run with `--action status` to confirm data integrity.
4. Do not fabricate execution outcomes or inventory data.

## Output Requirements

Every final response must make these items explicit when relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs (including LOW_CONFIDENCE flags for sparse data, noted inline per reagent)
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `--data-file` path contains `../` or points outside the workspace, reject with a path traversal warning.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits (include LOW_CONFIDENCE flag inline per reagent if fewer than 3 usage records)
7. Next Checks

For stress/multi-constraint requests, also include:
- Constraints checklist (compliance, performance, error paths)
- Unresolved items with explicit blocking reasons

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
