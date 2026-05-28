---
name: radiology-image-quiz
description: Use when creating radiology educational quizzes, preparing board exam questions, or studying medical imaging cases. Generates interactive quizzes with X-ray, CT, MRI, and ultrasound images for medical education.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Radiology Image Quiz Generator

Create educational quizzes using radiology images (X-ray, CT, MRI, ultrasound) for medical students, residents, and board exam preparation.

## When to Use

- Use this skill when the task needs Use when creating radiology educational quizzes, preparing board exam questions, or studying medical imaging cases. Generates interactive quizzes with X-ray, CT, MRI, and ultrasound images for medical education.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when creating radiology educational quizzes, preparing board exam questions, or studying medical imaging cases. Generates interactive quizzes with X-ray, CT, MRI, and ultrasound images for medical education.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/radiology-image-quiz"
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

## Quick Start

```python
from scripts.radiology_quiz import RadiologyQuiz

quiz = RadiologyQuiz()

# Generate quiz
questions = quiz.generate(
    modality="chest_xray",
    difficulty="intermediate",
    topic="pulmonary_pathology",
    num_questions=10
)
```

## Core Capabilities

### 1. Quiz Generation

```python
quiz = quiz.create(
    images=["case1.png", "case2.png"],
    question_type="multiple_choice",
    include_findings=True,
    include_differential=True
)
```

**Question Types:**
- Multiple choice (single best answer)
- Select all that apply
- Fill in the blank
- Open-ended interpretation

### 2. Case Creation

```python
case = quiz.create_case(
    image_path="ct_scan.png",
    diagnosis="Pulmonary embolism",
    findings=["Filling defect in pulmonary artery", "Right heart strain"],
    clinical_history="Sudden onset dyspnea"
)
```

### 3. Difficulty Calibration

```python
quiz = quiz.set_difficulty(
    level="resident",  # medical_student, resident, fellow, attending
    include_rare_findings=False
)
```

## CLI Usage

```text
python scripts/radiology_quiz.py \
  --modality ct \
  --topic emergency \
  --num 20 \
  --output quiz.pdf
```

---

**Skill ID**: 212 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `radiology-image-quiz` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `radiology-image-quiz` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
