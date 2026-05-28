---
name: tone-adjuster
description: Use when converting medical text between academic and patient-friendly tones, translating medical jargon for patients, adapting research papers for public audiences, or rewriting clinical notes for patient handouts. Maintains medical accuracy while adjusting readability level.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Medical Tone Adjuster

Convert medical text between academic rigor and patient-friendly language while preserving clinical accuracy.

## When to Use

- Use this skill when the task needs Use when converting medical text between academic and patient-friendly tones, translating medical jargon for patients, adapting research papers for public audiences, or rewriting clinical notes for patient handouts. Maintains medical accuracy while adjusting readability level.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when converting medical text between academic and patient-friendly tones, translating medical jargon for patients, adapting research papers for public audiences, or rewriting clinical notes for patient handouts. Maintains medical accuracy while adjusting readability level.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/tone-adjuster"
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
python scripts/main.py demo
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.tone_adjuster import ToneAdjuster

adjuster = ToneAdjuster()

# Academic → Patient-friendly
patient_text = adjuster.convert(
    text="The patient presents with acute myocardial infarction...",
    target_tone="patient-friendly"
)

# Patient-friendly → Academic
academic_text = adjuster.convert(
    text="I had a heart attack...",
    target_tone="academic"
)
```

## Core Capabilities

### 1. Academic to Patient-Friendly

```python
adjuster = ToneAdjuster()
result = adjuster.to_patient_friendly(
    "The patient exhibits tachycardia with irregular rhythm
     consistent with atrial fibrillation",
    reading_level="8th_grade"
)
```

**Conversion Rules:**
- Replace medical terms with common equivalents
- Shorten sentence length (aim for <15 words)
- Use active voice
- Remove unnecessary qualifiers

**Examples:**

| Academic | Patient-Friendly |
|----------|------------------|
| Myocardial infarction | Heart attack |
| Tachycardia | Fast heartbeat |
| Hypertension | High blood pressure |
| Benign prostatic hyperplasia | Enlarged prostate (non-cancerous) |
| Idiopathic | Unknown cause |

### 2. Patient-Friendly to Academic

```python
result = adjuster.to_academic(
    "My stomach hurts after eating spicy food",
    add_citations=True
)

# Output: "The patient reports postprandial abdominal pain

#          exacerbated by capsaicin-containing foods"
```

### 3. Reading Level Assessment

```python
metrics = adjuster.assess_reading_level(text)
print(f"Grade level: {metrics.grade_level}")
print(f"Medical terms: {metrics.jargon_count}")
print(f"Recommendations: {metrics.suggestions}")
```

**Reading Levels:**
- **5th-6th Grade**: Young patients, general public
- **8th Grade**: Most adult patients
- **12th Grade**: Educated lay audiences
- **College**: Healthcare professionals

### 4. Jargon Translation

```python
translations = adjuster.translate_jargon(
    text="Patient presents with dyspnea and orthopnea...",
    show_alternatives=True
)
```

**Common Medical Terms Dictionary:**

```json
{
  "dyspnea": {
    "patient_friendly": "shortness of breath",
    "explanation": "feeling like you can't get enough air"
  },
  "orthopnea": {
    "patient_friendly": "trouble breathing when lying down",
    "explanation": "need to prop up with pillows to breathe"
  }
}
```

## CLI Usage

```text

# Convert file
python scripts/tone_adjuster.py \
  --input clinical_note.txt \
  --direction academic-to-patient \
  --output patient_handout.txt

# Assess reading level
python scripts/tone_adjuster.py \
  --assess readme.txt \
  --target-grade 8
```

## Best Practices

**When Converting to Patient-Friendly:**
- ✅ Use "you" and "your" when appropriate
- ✅ Define terms in parentheses on first use
- ✅ Use analogies for complex concepts
- ✅ Keep paragraphs to 2-3 sentences

**When Converting to Academic:**
- ✅ Use precise medical terminology
- ✅ Include anatomical locations
- ✅ Specify temporal relationships
- ✅ Add objective measurements

## Common Pitfalls

❌ **Don't**: "Your heart has a problem"
✅ **Do**: "Your heart muscle shows signs of reduced blood flow"

❌ **Don't**: "The medicine might make you feel bad"
✅ **Do**: "This medication may cause nausea, dizziness, or fatigue"

## Quality Checklist

- [ ] Medical accuracy preserved
- [ ] No critical information lost
- [ ] Appropriate reading level achieved
- [ ] Tone matches intended audience
- [ ] All medical terms explained or translated

---

**Skill ID**: 202 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `tone-adjuster` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `tone-adjuster` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
