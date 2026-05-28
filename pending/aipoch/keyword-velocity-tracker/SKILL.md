---
name: keyword-velocity-tracker
description: Calculate literature growth velocity and acceleration to assess research.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Skill: Keyword Velocity Tracker

## When to Use

- Use this skill when the task needs Calculate literature growth velocity and acceleration to assess research.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Calculate literature growth velocity and acceleration to assess research.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python >= 3.8
- numpy
- scipy

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/keyword-velocity-tracker"
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
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Metadata
- **ID**: 201
- **Name**: Keyword Velocity Tracker
- **Type**: Analysis Tool
- **Version**: 1.0.0

## Description
Calculate the literature growth rate and acceleration of specific keywords to determine the development stage of academic research fields. By analyzing changes in literature volume over different time periods, provide field popularity trends and lifecycle analysis.

## Functions

### Core Functions
1. **Literature Growth Rate Calculation** - Calculate keyword literature growth rate over different time periods
2. **Growth Acceleration Analysis** - Identify trends of literature growth acceleration or deceleration
3. **Field Development Stage Judgment** - Determine field stage based on growth curve characteristics
4. **Trend Prediction** - Predict future development trends based on historical data

### Stage Judgment Criteria
- **Embryonic Stage**: Low base, slow growth
- **Growth Stage**: Growth rate continues to rise (acceleration is positive)
- **Mature Stage**: Growth rate is stable or declining
- **Decline Stage**: Growth rate is negative

## Input

### Required Parameters
| Parameter | Type | Description |
|------|------|------|
| `keyword` | string | Keyword to analyze |
| `data` | array | Time series literature data, format: `[{"year": 2020, "count": 100}, ...]` |

### Optional Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `time_window` | int | 3 | Time window for calculating growth rate (years) |
| `smoothing` | boolean | true | Whether to smooth the data |
| `predict_years` | int | 3 | Number of future years to predict |

## Output

### Return Value
```json
{
  "keyword": "artificial intelligence",
  "analysis_period": {"start": 2015, "end": 2023},
  "current_velocity": 0.35,
  "current_acceleration": -0.05,
  "stage": "mature",
  "stage_confidence": 0.85,
  "trend": "stable",
  "velocity_series": [
    {"year": 2016, "velocity": 0.20, "acceleration": null},
    {"year": 2017, "velocity": 0.25, "acceleration": 0.05},
    ...
  ],
  "prediction": {
    "2024": {"estimated_count": 1850, "confidence": 0.80},
    "2025": {"estimated_count": 1980, "confidence": 0.70},
    "2026": {"estimated_count": 2100, "confidence": 0.60}
  },
  "insights": [
    "Field has entered mature stage, growth slowing",
    "Recent slight deceleration trend, needs attention"
  ]
}
```

### Stage Definitions
- `current_velocity`: Current annual growth rate (0-1)
- `current_acceleration`: Current acceleration (growth rate change rate)
- `stage`: Field development stage (embryonic/growth/mature/decline)
- `stage_confidence`: Stage judgment confidence (0-1)
- `trend`: Trend direction (growth/stable/decline)

## Usage Examples

### Command Line
```text
python scripts/main.py --keyword "artificial intelligence" --data-file data.json
```

### Python API
```python
from skills.keyword_velocity_tracker.scripts.main import KeywordVelocityTracker

tracker = KeywordVelocityTracker()
result = tracker.analyze(
    keyword="artificial intelligence",
    data=[
        {"year": 2019, "count": 500},
        {"year": 2020, "count": 650},
        {"year": 2021, "count": 900},
        {"year": 2022, "count": 1100},
        {"year": 2023, "count": 1250}
    ]
)
```

## Configuration

### Environment Variables
| Variable | Description | Default |
|------|------|--------|
| `KVT_SMOOTHING_FACTOR` | Smoothing coefficient | 0.3 |
| `KVT_MIN_CONFIDENCE` | Minimum confidence threshold | 0.7 |

## Algorithm Description

### Growth Rate Calculation
```
velocity(t) = (count(t) - count(t-1)) / count(t-1)
```

### Acceleration Calculation
```
acceleration(t) = velocity(t) - velocity(t-1)
```

### Stage Judgment Logic
1. Average growth rate in last 3 years < 0.1 → Embryonic/Decline stage
2. Acceleration > 0 and growth rate > 0.2 → Growth stage
3. Growth rate stable (fluctuation < 0.1) → Mature stage
4. Growth rate < 0 → Decline stage

## Version History
- 1.0.0 (2024-02-06): Initial version, basic growth rate and acceleration calculation

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

This skill accepts requests that match the documented purpose of `keyword-velocity-tracker` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `keyword-velocity-tracker` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

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
