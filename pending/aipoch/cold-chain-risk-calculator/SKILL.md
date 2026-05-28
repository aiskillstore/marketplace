---
name: cold-chain-risk-calculator
description: Calculate temperature excursion risks for cold chain transport. Assesses route risk, packaging suitability, and monitoring requirements for biological samples and pharmaceuticals requiring controlled-temperature shipping.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Cold Chain Risk Calculator

Assess temperature excursion risk for cold chain transport routes. Evaluates packaging type, transit duration, and route conditions to produce a structured JSON risk score and mitigation recommendations.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Evaluating shipping risk for biological samples, vaccines, or temperature-sensitive pharmaceuticals
- Selecting appropriate packaging (dry ice, liquid nitrogen, gel packs) for a given route and duration
- Generating risk documentation for regulatory or QA purposes

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback template:** If `scripts/main.py` fails or required inputs are absent, report: (a) which parameter is missing, (b) what partial assessment is still possible, (c) the manual risk-scoring approach.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--route`, `-r` | string | Yes | Transport route description (e.g., "NYC-Boston") |
| `--duration`, `-d` | int | Yes | Transport duration in hours (must be > 0) |
| `--packaging`, `-p` | string | No | Packaging type: `dry-ice`, `liquid-nitrogen`, `gel-packs` (default: `dry-ice`) |
| `--output`, `-o` | string | No | Output JSON file path (default: stdout) |

## Usage

```text
python scripts/main.py --route "NYC-Boston" --duration 48 --packaging dry-ice
python scripts/main.py --route "LAX-London" --duration 120 --packaging liquid-nitrogen --output risk_report.json
```

## Output Format

The script outputs a structured JSON object:

```json
{
  "route": "NYC-Boston",
  "duration_hours": 48,
  "packaging": "dry-ice",
  "risk_score": 19.2,
  "risk_level": "Medium",
  "mitigation_recommendations": [
    "Add temperature logger to shipment",
    "Pre-condition dry ice 2h before packing",
    "Notify recipient of expected arrival window"
  ]
}
```

The `mitigation_recommendations` field is always present and contains at least one actionable item. Recommendations are generated based on risk level and packaging type.

## Risk Model

Risk score = `duration_hours × 0.5 × packaging_factor`

| Packaging | Factor | Notes |
|-----------|--------|-------|
| `dry-ice` | 0.8 | Standard for -70°C samples |
| `liquid-nitrogen` | 0.6 | Best for cryogenic samples |
| `gel-packs` | 1.2 | Suitable for 2–8°C only |

Risk levels: Low (< 15), Medium (15–30), High (> 30)

**Model limitations:** The formula does not account for route complexity, number of transit legs, or ambient temperature variability. A 120-hour international flight may score lower than a 48-hour domestic route due to packaging factor alone. Document these assumptions in every response.

## Features

- Route risk assessment based on duration and packaging type
- Structured JSON output with risk score, level, and mitigation recommendations
- Input validation: rejects negative or zero duration (exit code 1)
- Mitigation action list generated per risk level and packaging type

## Output Requirements

Every response must make these explicit:

- Objective and deliverable
- Inputs used and assumptions introduced (ambient temperature assumed standard; no transit-leg complexity modeled)
- Workflow or decision path taken
- Core result: risk score, risk level, and mitigation recommendations
- Constraints, risks, caveats (e.g., model does not account for route complexity or number of transit legs)
- Unresolved items and next-step checks

## Input Validation

This skill accepts: cold chain transport scenarios defined by a route, duration, and optional packaging type.

If the request does not involve temperature-controlled shipping risk — for example, asking to track a shipment in real time, calculate drug dosing, or assess non-temperature logistics — do not proceed. Instead respond:

> "`cold-chain-risk-calculator` is designed to assess temperature excursion risk for cold chain transport. Your request appears to be outside this scope. Please provide a route, duration, and packaging type, or use a more appropriate tool for your task."

## Error Handling

- If `--duration` is ≤ 0, print `Error: --duration must be a positive integer (hours).` to stderr and exit with code 1.
- If `--packaging` is not one of `dry-ice`, `liquid-nitrogen`, `gel-packs`, reject with a clear error listing valid options.
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
