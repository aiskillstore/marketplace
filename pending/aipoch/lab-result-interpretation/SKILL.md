---
name: lab-result-interpretation
description: A medical assistant tool that transforms complex biochemical laboratory test results into clear, patient-friendly explanations with safety disclaimers and severity flags.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Lab Result Interpretation

A medical assistant tool that transforms complex biochemical laboratory test results into clear, patient-friendly explanations.

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --interactive
```

## When to Use

- Use this skill to interpret biochemical lab test results and generate patient-friendly explanations.
- Use this skill to flag abnormal values with severity indicators and contextual health recommendations.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Critical values:** When any value is in the critical range, output a **Critical Findings Summary** block at the top of the response before the per-test breakdown. Sort findings by severity (critical → high → normal). Include an explicit urgent care recommendation for critical values.

## Features

- Parses various lab test formats (numeric values, units, reference ranges)
- Compares values against standard reference ranges
- Generates patient-friendly explanations
- Flags abnormal values with severity indicators (critical → high → normal order)
- Provides contextual health recommendations
- Includes mandatory medical disclaimer in all outputs

## Supported Test Types

| Category | Tests |
|----------|-------|
| **Blood Routine** | WBC, RBC, Hemoglobin, Platelets, Hematocrit |
| **Lipid Panel** | Total Cholesterol, LDL, HDL, Triglycerides |
| **Liver Function** | ALT, AST, ALP, GGT, Bilirubin, Total Protein, Albumin |
| **Kidney Function** | Creatinine, BUN, eGFR, Uric Acid |
| **Blood Sugar** | Fasting Glucose, HbA1c |
| **Thyroid** | TSH, T3, T4, FT3, FT4 |
| **Electrolytes** | Sodium, Potassium, Chloride, Calcium, Magnesium |
| **Inflammation** | CRP, ESR |

## Usage

### As Module

```python
from scripts.main import LabResultInterpreter

interpreter = LabResultInterpreter()
result = interpreter.interpret("Total Cholesterol: 5.8 mmol/L (Reference: 3.1-5.7)")
print(result.explanation)
```

### CLI

```text
python scripts/main.py --file lab_report.txt
python scripts/main.py --interactive
```

## Parameters

| Name | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| file | string | "" | No | Path to lab report file to process |
| interactive | boolean | false | No | Enable interactive mode for manual input |
| input | string | "" | No | Direct lab test input string for interpretation |

## Input Format

Accepts flexible formats:
```
Test Name: Value Unit (Reference: Min-Max)
Test Name Value Unit Ref: Min-Max
Test Name: Value (Min-Max)
```

## Output Format

```json
{
  "test_name": "Total Cholesterol",
  "value": 5.8,
  "unit": "mmol/L",
  "reference_min": 3.1,
  "reference_max": 5.7,
  "status": "high",
  "explanation": "Your total cholesterol is slightly above the normal range...",
  "severity": "mild",
  "recommendation": "Consider reducing saturated fat intake..."
}
```

## Medical Disclaimer

This tool provides educational information only and is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for interpretation of lab results. This tool does not diagnose — it only explains test meanings.

## References

- `references/lab_reference_ranges.json` — Standard reference ranges
- `references/explanation_templates.json` — Patient-friendly templates
- `references/test_metadata.json` — Test descriptions and clinical notes

## Dependencies

- Python >= 3.8 (strictly required; dataclasses module used)
- **Runtime version guard:** The script must check `sys.version_info >= (3, 8)` at startup and exit with `'Error: Python 3.8+ required'` if the check fails, before any imports.

## Prerequisites

```text
pip install -r requirements.txt
```

## Input Validation

This skill accepts: biochemical laboratory test results in standard formats (test name, value, unit, reference range) for the purpose of generating patient-friendly explanations.

If the user's request does not involve lab result interpretation — for example, asking to diagnose a condition, prescribe treatment, interpret imaging results, or perform general medical consultation — do not proceed with the workflow. Instead respond:
> "lab-result-interpretation is designed to explain biochemical lab test values in patient-friendly language. It does not diagnose conditions or replace medical advice. Your request appears to be outside this scope. Please provide lab test values with reference ranges, or consult a qualified healthcare provider."

Do not continue the workflow when the request is out of scope, missing lab values, or would require clinical diagnosis. For missing inputs, state exactly which fields are missing.

## Fallback Behavior

If `scripts/main.py` fails or required inputs are incomplete:
1. Report the exact failure point and error message.
2. State what can still be completed (e.g., partial interpretation of available values).
3. Manual fallback: use `--interactive` mode to enter values one at a time, or provide the raw value and reference range for manual comparison.
4. Do not fabricate lab values, reference ranges, or clinical interpretations.

## Boundary Enforcement

This skill explicitly does **not**:
- Diagnose medical conditions
- Recommend specific medications or dosages
- Replace consultation with a licensed healthcare provider
- Interpret imaging, pathology, or genetic test results (for imaging results, consult a radiologist report; for genetic tests, consult a genetic counselor)

Any request that would require crossing these boundaries must be declined with the medical disclaimer and a referral to appropriate professional resources.

## Output Requirements

Every final response must make these items explicit when relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- **Critical Findings Summary** (if any value is critical — placed at top, before per-test breakdown)
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs (including medical disclaimer)
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- If the `--file` path contains `../` or points outside the workspace, reject with a path traversal warning before opening the file.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. **Critical Findings Summary** (if applicable — urgent care recommendation for critical values)
6. Deliverable
7. Risks and Limits (always include medical disclaimer)
8. Next Checks

For stress/multi-constraint requests, also include:
- Constraints checklist (compliance, performance, error paths)
- Explicit boundary statement confirming no diagnosis was made
- Unresolved items with explicit blocking reasons

If the request is simple, you may compress the structure, but always keep the medical disclaimer and scope limits explicit.
