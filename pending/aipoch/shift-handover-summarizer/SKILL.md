---
name: shift-handover-summarizer
description: Generate structured shift handover summaries from EHR records, highlighting critical events, vital sign changes, and pending tasks for incoming clinical staff.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Shift Handover Summarizer

Generate structured shift handover summaries from EHR updates, highlighting critical events that occurred during the shift.

> **Clinical Disclaimer:** This tool generates summaries for handover support only. All clinical decisions must be verified by qualified medical staff. Patient data must comply with applicable data protection regulations (e.g., HIPAA).

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Use this skill when generating a structured handover summary from EHR records at the end of a clinical shift.
- Use this skill when prioritizing patients by event severity for incoming staff.
- Do not use this skill as a substitute for direct clinical handover, real-time patient assessment, or emergency triage.

## Workflow

1. Confirm the patient records file, shift start/end times, and optional department filter.
2. Validate that the input records are within the declared shift time range.
3. **Timezone validation:** If `--shift-start` or `--shift-end` lacks a timezone offset (e.g., `2026-02-06T00:00:00` without `Z` or `+HH:MM`), emit a warning: "Shift times appear to lack a timezone offset. Assuming UTC. Specify timezone explicitly (e.g., `2026-02-06T00:00:00+08:00`) to avoid incorrect event filtering."
4. Run the summarizer script or apply the manual extraction path.
5. Return a structured summary with patients ranked by priority, key events, and pending tasks.
6. If inputs are incomplete, state exactly which fields are missing and request only the minimum additional information.

## Usage

```text
python scripts/main.py \
  --records data/shift_records.json \
  --shift-start "2026-02-06T00:00:00Z" \
  --shift-end "2026-02-06T08:00:00Z" \
  --department "Cardiology" \
  --output summary.json
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--records` | file path | Yes | JSON file of EHR records for the shift |
| `--shift-start` | ISO 8601 | Yes | Shift start time |
| `--shift-end` | ISO 8601 | Yes | Shift end time |
| `--department` | string | No | Department filter |
| `--output` | file path | No | Output file path (default: stdout) |
| `--no-vitals` | flag | No | Exclude vital signs summary |

## Event Priority Levels

| Priority | Event Type |
|----------|-----------|
| High | Resuscitation, deterioration, serious complications, abnormal vitals |
| Medium | New symptoms, abnormal findings, medication adjustments, special procedures |
| Low | Routine treatment, condition improvement, daily care |

## Output

- Shift summary with total patients and critical patient count
- Per-patient priority ranking, key events, vitals summary, medication summary, and pending tasks
- Plain-text handover narrative

## Scope Boundaries

- This skill processes structured EHR records; it does not access live hospital systems.
- Event classification is based on preset thresholds and keywords; adjust thresholds for department-specific needs.
- This skill does not replace direct verbal handover or physician sign-off.

## Stress-Case Rules

For complex multi-constraint requests, always include these explicit blocks:

1. Assumptions
2. Shift Period and Inputs Used
3. Summary Output
4. Critical Flags
5. Risks and Manual Checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate patient data, clinical events, or execution outcomes.

## Input Validation

This skill accepts: a structured EHR records file with shift start and end times for handover summary generation.

If the request does not involve shift handover summary generation from EHR records — for example, asking for real-time patient monitoring, clinical diagnosis, or direct treatment recommendations — do not proceed with the workflow. Instead respond:
> "shift-handover-summarizer is designed to generate structured handover summaries from EHR records. Your request appears to be outside this scope. Please provide a records file and shift times, or use a more appropriate clinical tool."

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
