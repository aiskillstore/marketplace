---
name: personal-statement
description: Use when writing medical school personal statements, residency application essays, fellowship statements, or graduate school admissions essays. Crafts compelling narratives highlighting clinical experiences, research achievements, and career motivations for healthcare education applications.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Personal Statement Writer for Medical Education

Craft compelling personal statements for medical school, residency, fellowship, and graduate school applications in healthcare fields.

## When to Use

- Use this skill when the task needs Use when writing medical school personal statements, residency application essays, fellowship statements, or graduate school admissions essays. Crafts compelling narratives highlighting clinical experiences, research achievements, and career motivations for healthcare education applications.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when writing medical school personal statements, residency application essays, fellowship statements, or graduate school admissions essays. Crafts compelling narratives highlighting clinical experiences, research achievements, and career motivations for healthcare education applications.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/personal-statement"
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
python scripts/main.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.personal_statement_writer import PersonalStatementWriter

writer = PersonalStatementWriter()

# Generate personal statement
statement = writer.write(
    program_type="medical_school",
    key_experiences=["Shadowing Dr. Smith", "Volunteer at free clinic", "Research on diabetes"],
    motivation="Helping underserved communities",
    character_limit=5300
)
```

## Core Capabilities

### 1. Structure Generation

```python
outline = writer.create_outline(
    program="residency_surgery",
    themes=["Leadership", "Technical skill", "Patient advocacy"]
)
```

**Standard Structure:**
1. **Opening Hook** (10-15%) - Captivating patient story or defining moment
2. **Clinical Experiences** (30-40%) - Specific patient encounters with reflection
3. **Research/Academic** (20-25%) - Scholarly contributions and intellectual curiosity
4. **Service/Leadership** (15-20%) - Community impact and teamwork
5. **Career Goals** (10-15%) - Clear vision for future practice

### 2. Experience Framing

```python
framed = writer.frame_experience(
    experience="Volunteered at homeless shelter",
    angle="patient_advocacy",
    program_type="family_medicine"
)
```

**STAR Method for Experiences:**
- **S**ituation: Brief context
- **T**ask: Your responsibility
- **A**ction: Specific steps you took
- **R**esult: Measurable outcome + personal reflection

### 3. Character Optimization

```python
optimized = writer.optimize_length(
    draft_statement,
    target_chars=5300,  # AMCAS limit
    min_chars=4500
)
```

**Character Limits by Program:**
| Program | Character Limit | Word Approx |
|---------|----------------|-------------|
| AMCAS (Medical School) | 5,300 | ~750 words |
| ERAS (Residency) | Varies by specialty | ~800 words |
| Fellowship | Usually 1-2 pages | ~1000 words |
| Graduate School | Varies | ~500-1000 words |

### 4. Tone Adjustment

```python
adjusted = writer.adjust_tone(
    statement,
    tone="confident_but_humble",
    avoid_cliches=True
)
```

## Common Patterns

See `references/personal-statement-examples.md` for:
- Medical School (MD/DO) Examples
- Residency Personal Statements by Specialty
- Fellowship Application Essays
- Re-applicant Strategies
- Career Changer Narratives

## Quality Checklist

**Before Writing:**
- [ ] List 3 defining patient experiences
- [ ] Identify unique aspects of your journey
- [ ] Research specific program values

**After Writing:**
- [ ] No clichés ("I want to help people", "Since I was young...")
- [ ] Specific examples throughout
- [ ] Personal reflection on every experience
- [ ] Clear connection to chosen specialty
- [ ] Within character limits
- [ ] Proofread for errors

## Common Pitfalls

❌ **Avoid**: "I have always wanted to be a doctor since childhood"
✅ **Instead**: "My decision to pursue medicine crystallized when..."

❌ **Avoid**: Listing achievements without reflection
✅ **Instead**: "This experience taught me..." + specific insight

---

**Skill ID**: 203 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `personal-statement` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `personal-statement` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
