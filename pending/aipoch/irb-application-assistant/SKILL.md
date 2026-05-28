---
name: irb-application-assistant
description: Assists researchers with Institutional Review Board (IRB) application tasks, including drafting informed consent documents, reviewing research protocols for compliance, generating application forms, and preparing submission checklists. Use when the user mentions IRB, Institutional Review Board, research ethics, human subjects research, protocol review, informed consent, or needs help preparing or reviewing an IRB application or submission.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# IRB Application Assistant

Helps researchers prepare, review, and submit Institutional Review Board (IRB) applications. Supports drafting informed consent templates, checking protocol compliance, generating application documents, and guiding researchers through the submission workflow.

## When to Use

- Use this skill when the task needs Assists researchers with Institutional Review Board (IRB) application tasks, including drafting informed consent documents, reviewing research protocols for compliance, generating application forms, and preparing submission checklists. Use when the user mentions IRB, Institutional Review Board, research ethics, human subjects research, protocol review, informed consent, or needs help preparing or reviewing an IRB application or submission.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Assists researchers with Institutional Review Board (IRB) application tasks, including drafting informed consent documents, reviewing research protocols for compliance, generating application forms, and preparing submission checklists. Use when the user mentions IRB, Institutional Review Board, research ethics, human subjects research, protocol review, informed consent, or needs help preparing or reviewing an IRB application or submission.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/irb-application-assistant"
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

```text

# Generate an informed consent template
python scripts/main.py --task consent --protocol protocol.json --output consent_form.docx

# Run a compliance check on a research protocol
python scripts/main.py --task compliance-check --protocol protocol.json --verbose

# Generate a full IRB application package
python scripts/main.py --task generate-application --config study_config.json --output irb_package/
```

## Core Capabilities

### 1. Generate Informed Consent Documents

Produces compliant informed consent forms based on study parameters such as participant population, risk level, and study type.

```text
python scripts/main.py --task consent \
  --protocol protocol.json \
  --population "adults 18+" \
  --risk-level minimal \
  --output consent_form.docx
```

### 2. Protocol Compliance Review

Checks a research protocol against IRB requirements and flags missing or non-compliant sections.

```text
python scripts/main.py --task compliance-check \
  --protocol protocol.json \
  --ruleset federal-common-rule \
  --output compliance_report.txt
```

### 3. Application Form Generation

Generates completed IRB application forms (e.g., initial review, continuing review, amendment) from structured study data.

```text
python scripts/main.py --task generate-application \
  --form-type initial-review \
  --config study_config.json \
  --output irb_application.docx
```

### 4. Submission Checklist Validation

Validates that all required documents and fields are present before submission.

```text
python scripts/main.py --task validate-submission \
  --package irb_package/ \
  --output validation_report.txt
```

## Recommended Workflow

Follow these steps for a complete IRB submission:

1. **Prepare study configuration** — Populate `study_config.json` with study title, PI details, participant population, risk level, and procedures.
2. **Run compliance check** — Use `--task compliance-check` to identify gaps in the protocol before drafting documents.
   - ⛔ **Checkpoint**: If the compliance report flags ANY errors, resolve ALL flagged items and re-run `--task compliance-check` before proceeding. Do not advance to step 3 with unresolved compliance errors.
3. **Generate consent document** — Use `--task consent` to produce a compliant informed consent form tailored to the study.
4. **Generate application forms** — Use `--task generate-application` to produce the required IRB submission forms.
5. **Validate submission package** — Use `--task validate-submission` to confirm all required documents are present and fields are complete.
   - ⛔ **Checkpoint**: If validation fails, follow this loop: review errors in `validation_report.txt` → fix each issue → re-run `--task validate-submission` → only proceed when the report shows zero blocking errors.
6. **Review and submit** — Manually review any remaining warnings in the compliance and validation reports before submitting to the IRB.

## Quality Checklist

- [ ] Protocol includes all required sections (purpose, procedures, risks, benefits, confidentiality)
- [ ] Informed consent language is at appropriate reading level for participant population
- [ ] Risk level classification is justified and documented
- [ ] All required attachments (recruitment materials, surveys, data management plan) are included
- [ ] Compliance report reviewed and all flagged items resolved
- [ ] Submission package validated with zero blocking errors

## References

- `references/guide.md` — Detailed documentation and field descriptions
- `references/examples/` — Sample protocols, consent forms, and completed applications

---

**Skill ID**: 952 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `irb-application-assistant` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `irb-application-assistant` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
