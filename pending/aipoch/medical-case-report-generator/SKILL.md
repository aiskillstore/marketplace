---
name: medical-case-report-generator
description: Generates a patient-friendly medical case report tweet from case images and disease name. Use when the user provides a medical case image and wants a structured report or tweet.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates a patient-friendly medical case report tweet from case images and disease name. Use when the user provides a medical case image and wants a structured report or tweet.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/medical-case-report-generator"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Medical Case Report Generator

## Workflow

Follow these steps to generate the report.

### 1. Image Text Extraction

**Input:** case image
**Action:**
Extract printed and handwritten medical text from the image with high accuracy.
Focus on medical terminology, numbers, and units.
Perform image enhancement, correction, and validation.

**Output:** extracted medical text

---

### 2. Patient Info Extraction

**Input:** extracted medical text
**Action:**
Extract and anonymize patient information and examination results.

Include:

* Age
* Gender
* Occupation (if available)
* Chief complaint
* Medical history
* Examination types
* Examination results
* Final confirmed diagnosis

Rules:

* Remove personal identifiers
* Do not infer missing data
* Merge duplicate tests
* Mark abnormal values
* Extract only the main diagnosis of this visit

**Output format:**

```

## Case Summary
...

## Examination Results
...

Final diagnosis: ...
```

---

### 3. Disease Content Generation

**Input:** disease name
**Action:** Generate three sections.

#### Disease Introduction

Include:

* Simple definition
* Core symptoms (≤5)
* Health risks
* Risk factors (modifiable / non-modifiable)
* Early warning signs

---

#### Treatment Options

Include:

* Guideline-based treatment strategies
* Classified by disease stage or severity
* For each method include:

  * Method name
  * Example therapies
  * Applicable patients
  * Key notes (effectiveness, duration, cost)
* Side effects and precautions
* Optional complementary therapies

---

#### Health Reminders

Include:

* Core management principle
* Daily advice:

  * Diet
  * Exercise
  * Sleep
  * Mental health
* Monitoring indicators
* Emergency warning signs

---

### 4. Encouragement Message

Generate 1-2 sentences of professional encouragement based on disease type.

Rules:

* Acute disease → emphasize medical progress and teamwork
* Chronic disease → emphasize long-term management and adaptation
* Warm but professional tone
* Group-oriented language
* End with exclamation mark

---

### 5. Title Generation

Generate 3 candidate titles.

Rules:

* Start with prefix: 【Case Report】
* 18-25 characters
* Include disease feature + patient group + awareness element
* No exaggeration or privacy exposure

---

### 6. Final Output Compilation

Combine all generated sections into a single Markdown report.

Structure:

```

## Title Options
...

## Case Summary
...

## Examination Results
...

## Disease Introduction
...

## Treatment Options
...

## Health Reminders
...

## Encouragement
...
```

---

## Notes for Integration

This skill is designed for:

* opencode skill pipelines
* medical social media automation
* research-support system case summarization modules

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `medical_case_report_generator_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: medical_case_report_generator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
