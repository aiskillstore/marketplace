---
name: virtual-patient-roleplay
description: Simulate standardized patient encounters for medical training, supporting OSCE-style history-taking practice, communication skills rehearsal, and educational debriefing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Virtual Patient Roleplay

Structured standardized-patient simulation for medical training and clinical interview practice.

> **Educational Disclaimer:** All output is for training simulation only. This skill does not provide real clinical diagnosis, treatment selection, or emergency instructions. Faculty supervision is required for formal assessment use.

## Quick Check

```bash
python -m py_compile scripts/main.py
python -c "from scripts.main import PatientSimulator; sim=PatientSimulator('chest_pain'); print(sim.ask('Where does the pain go?')['patient_response'])"
```

## When to Use

- Use this skill for OSCE-style history-taking practice, communication skills rehearsal, or debrief planning.
- Use this skill when a learner needs to practice clinical interviewing with a simulated patient response.
- Do not use this skill for real patient triage, clinical diagnosis, treatment selection, or emergency guidance.

## Workflow

1. Confirm the training goal, scenario type, learner level, and output focus (questioning, bedside manner, or debriefing).
2. Check whether the request is for live roleplay, case setup, feedback, or post-encounter summary.
3. Use the packaged simulator for supported scenarios; otherwise provide a manual roleplay scaffold without inventing unsupported medical certainty.
4. Return the patient response or teaching artifact with assumptions, missed-question prompts, and debrief notes.
5. If the request exceeds educational scope, stop and restate the boundary explicitly.

## Usage

```text
python -c "from scripts.main import PatientSimulator; sim=PatientSimulator('chest_pain'); print(sim.ask('Where does the pain go?')['patient_response'])"
python -c "from scripts.main import PatientSimulator; sim=PatientSimulator('headache'); print(sim.ask('Did the pain start suddenly?')['patient_response'])"
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `scenario` | string | No | `chest_pain` | Scenario: `chest_pain`, `headache`, `abdominal_pain` |
| `student_question` | string | Yes (for interaction) | — | Learner question posed to the patient |
| `difficulty` | string | No | `intermediate` | Scenario difficulty level |

## Output

- Simulated patient response
- Scenario-specific cues and debrief elements
- Explicit reminder that output is educational, not clinical advice

## Scope Boundaries

- This skill supports training simulations, not real clinical triage.
- This skill does not provide diagnosis, treatment selection, or emergency instructions.
- This skill should not be used as a substitute for faculty supervision or patient care.

## Stress-Case Rules

For complex multi-constraint requests, always include these explicit blocks:

1. Training Objective
2. Scenario Assumptions
3. Roleplay Output
4. Educational Limits
5. Debrief and Next Checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate clinical certainty, real patient data, or verified diagnostic outcomes.

## Input Validation

This skill accepts: a scenario identifier and a learner question for standardized patient simulation in a medical training context.

If the request does not involve educational patient simulation — for example, asking for real clinical diagnosis, treatment recommendations, emergency triage, or non-medical roleplay — do not proceed with the workflow. Instead respond:
> "virtual-patient-roleplay is designed for medical training simulations only. Your request appears to be outside this scope. Please provide a scenario and learner question for educational practice, or use a more appropriate tool."

## References

- [references/references.md](references/references.md) — Educational standards and simulation frameworks
- [references/audit-reference.md](references/audit-reference.md) — Supported scope, audit commands, and fallback boundaries

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
