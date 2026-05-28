---
name: medical-unit-converter
description: Convert medical laboratory values between units (mg/dL to mmol/L, etc.) with formula transparency and clinical reference ranges. Supports glucose, cholesterol, creatinine, and hemoglobin conversions.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Medical Unit Converter

Convert laboratory values between clinical units with formula transparency and reference range context. Supports glucose, cholesterol, creatinine, and hemoglobin.

## When to Use

- Converting glucose, cholesterol, creatinine, or hemoglobin lab values between unit systems
- Verifying unit conversions for clinical documentation or research
- Batch-converting lab result tables between mg/dL and mmol/L conventions
- Providing reference ranges alongside converted values

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Supported Conversions

| Analyte | From | To | Factor | Reference Range (target unit) |
|---------|------|----|--------|-------------------------------|
| Glucose | mg/dL | mmol/L | 0.0555 | 3.9–5.6 mmol/L (fasting) |
| Glucose | mmol/L | mg/dL | 18.018 | 70–100 mg/dL (fasting) |
| Cholesterol | mg/dL | mmol/L | 0.02586 | < 5.2 mmol/L (desirable) |
| Cholesterol | mmol/L | mg/dL | 38.67 | < 200 mg/dL (desirable) |
| Creatinine | mg/dL | μmol/L | 88.4 | 62–115 μmol/L (male) |
| Creatinine | μmol/L | mg/dL | 0.01131 | 0.7–1.3 mg/dL (male) |
| Hemoglobin | g/dL | g/L | 10 | 130–175 g/L (male) |
| Hemoglobin | g/L | g/dL | 0.1 | 13–17.5 g/dL (male) |

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--value`, `-v` | float | Yes | Numeric value to convert |
| `--from-unit` | str | Yes | Source unit (e.g., `mg_dl`, `mmol_l`, `umol_l`, `g_dl`, `g_l`) |
| `--to-unit` | str | Yes | Target unit |
| `--analyte`, `-a` | str | No | Analyte name for reference range lookup (e.g., `glucose`, `cholesterol`, `creatinine`, `hemoglobin`) |

## Output Format

```json
{
  "converted_value": 5.55,
  "formula": "100 × 0.0555",
  "from_unit": "mg_dl",
  "to_unit": "mmol_l",
  "analyte": "glucose",
  "reference_range": "3.9–5.6 mmol/L (fasting glucose)"
}
```

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --value 100 --from-unit mg_dl --to-unit mmol_l --analyte glucose
```

## Implementation Notes (for script developer)

The script must:

1. **Parse CLI args** — use argparse with `--value`, `--from-unit`, `--to-unit`, `--analyte`. Pass parsed args to `conv.convert()`. Do not hardcode demo values in `main()`.
2. **CONVERSIONS dict** — include all 8 conversion pairs above, each with `factor` and `reference_range` fields. Keys must be `(analyte, from_unit, to_unit)` tuples or equivalent nested structure.
3. **convert() method** — return a dict with `converted_value`, `formula`, `from_unit`, `to_unit`, `analyte`, `reference_range`.
4. **Unsupported pair** — if the unit pair is not in CONVERSIONS, print the supported conversions list and exit with code 1.
5. **Fallback Partial result** — when an unsupported unit pair is requested, always populate the `Partial result` field in the Fallback Template with: `"Manual formula not available for this unit pair"`.

## Input Validation

This skill accepts: numeric laboratory values with a source unit and target unit for conversion between recognized clinical measurement systems.

If the request does not involve converting a specific numeric lab value between units — for example, asking to interpret clinical results, diagnose conditions, or convert non-laboratory quantities — do not proceed. Instead respond:

> "medical-unit-converter is designed to convert medical laboratory values between unit systems. Your request appears to be outside this scope. Please provide a numeric value with source and target units, or use a more appropriate tool for your task."

## Error Handling

- If `--value`, `--from-unit`, or `--to-unit` is missing, state exactly which fields are missing and request only those.
- If the unit pair is not supported, list the supported conversions and stop.
- If `--value` is not a valid number, reject with: `Error: --value must be a numeric value.`
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point and provide the manual conversion formula as fallback.
- Do not fabricate conversion factors or reference ranges.

## Fallback Template

When execution fails or inputs are incomplete, respond with this structure:

```
FALLBACK REPORT
───────────────────────────────────────
Objective      : [restate the conversion goal]
Blocked by     : [exact missing input or error]
Partial result : [manual formula if conversion factor is known; "Manual formula not available for this unit pair" if unsupported]
Next step      : [minimum action needed to unblock]
───────────────────────────────────────
```

## Response Template

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

## Prerequisites

No additional Python packages required beyond the standard library.
