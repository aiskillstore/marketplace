---
name: ebm-calculator
description: Evidence-Based Medicine diagnostic test calculator. Computes sensitivity, specificity, PPV, NPV, likelihood ratios, NNT, and pre/post-test probability from 2x2 contingency table inputs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# EBM Calculator

Compute Evidence-Based Medicine statistics from diagnostic test data: sensitivity, specificity, PPV/NPV with prevalence adjustment, likelihood ratios, NNT, and pre/post-test probability conversion.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Calculating diagnostic test performance metrics from a 2×2 contingency table
- Adjusting PPV/NPV for a specific population prevalence
- Computing NNT from control and experimental event rates
- Converting pre-test probability using a likelihood ratio

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback template:** If `scripts/main.py` fails or required inputs are absent, report: (a) which parameters are missing, (b) which metrics can still be computed from available data, (c) the manual formula for the requested mode.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--mode`, `-m` | string | No | Mode: `diagnostic`, `nnt`, `probability` (default: `diagnostic`) |
| `--tp` | int | diagnostic | True positives (must be ≥ 0) |
| `--fn` | int | diagnostic | False negatives (must be ≥ 0) |
| `--tn` | int | diagnostic | True negatives (must be ≥ 0) |
| `--fp` | int | diagnostic | False positives (must be ≥ 0) |
| `--prevalence`, `-p` | float | No | Disease prevalence 0–1 (adjusts PPV/NPV; must be in [0, 1]) |
| `--control-rate` | float | nnt | Control event rate 0–1 |
| `--experimental-rate` | float | nnt | Experimental event rate 0–1 |
| `--pretest` | float | probability | Pre-test probability 0–1 |
| `--lr` | float | probability | Likelihood ratio |
| `--output`, `-o` | string | No | Output file path (default: stdout) |

**Validation rules:**
- All confusion matrix values (tp, fn, tn, fp) must be ≥ 0; negative values are rejected with: "Confusion matrix values must be non-negative."
- Prevalence must be in [0, 1]; values outside this range are rejected with: "Prevalence must be between 0 and 1."
- The `result` variable is always initialized before `json.dumps(result)` to prevent unbound variable errors.

## Usage

```text
# Diagnostic mode
python scripts/main.py --mode diagnostic --tp 90 --fn 10 --tn 85 --fp 15 --prevalence 0.1

# NNT mode
python scripts/main.py --mode nnt --control-rate 0.3 --experimental-rate 0.2

# Pre/post-test probability
python scripts/main.py --mode probability --pretest 0.15 --lr 5.2
```

## Output Format

```json
{
  "sensitivity": 0.90,
  "specificity": 0.85,
  "ppv": 0.40,
  "npv": 0.99,
  "lr_positive": 6.0,
  "lr_negative": 0.12,
  "interpretation": "High sensitivity; PPV low due to low prevalence"
}
```

## Output Requirements

Every response must make these explicit:

- Objective and deliverable
- Inputs used and assumptions introduced
- Workflow or decision path taken
- Core result: computed EBM metrics
- Constraints, risks, caveats (e.g., prevalence assumptions, population applicability)
- Unresolved items and next-step checks

## Input Validation

This skill accepts: diagnostic test data (2×2 table values, event rates, or pre-test probability + likelihood ratio) for EBM metric calculation.

If the request does not involve EBM statistical calculation — for example, asking for clinical treatment recommendations, drug dosing, or patient-specific medical advice — do not proceed. Instead respond:

> "`ebm-calculator` is designed to compute Evidence-Based Medicine statistics from diagnostic test data. Your request appears to be outside this scope. Please provide the required numeric inputs for your chosen mode, or use a more appropriate tool for your task."

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If confusion matrix values are negative, reject with: "Confusion matrix values must be non-negative."
- If prevalence is outside [0, 1], reject with: "Prevalence must be between 0 and 1."
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
