---
name: anki-card-creator
description: Use anki-card-creator for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries for study-card generation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Anki Card Creator

Structured flashcard generation for medical study content.

## When to Use

- Use this skill when the task needs structured Anki-style cards from medical notes, textbook excerpts, lecture summaries, or Q&A study material.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use anki-card-creator for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries for study-card generation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `argparse`: `unspecified`. Declared in `requirements.txt`.
- `re`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/anki-card-creator"
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

1. Confirm the study objective, learner level, card format, and content source before drafting cards.
2. Check whether the material is already in Q/A form, needs manual restructuring, or is too incomplete for safe conversion.
3. Use the packaged script when the input matches supported arguments; otherwise produce a manual card plan without fabricating content.
4. Return cards or a card blueprint with assumptions, tagging guidance, and validation notes.
5. If required content is missing, stop and request only the minimum additional input.

## Use Cases

- Convert lecture notes into atomic recall cards
- Turn drug summaries into mechanism and adverse-effect cards
- Prepare anatomy cards with structure, location, and function blocks

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--input`, `-i` | string | No | - | Input text file containing Q/A pairs |
| `--output`, `-o` | string | No | `anki_cards.txt` | Output TSV file for Anki import |
| `--drug` | flag | No | false | Create a drug card from structured fields |
| `--anatomy` | flag | No | false | Create an anatomy card from structured fields |
| `--name` | string | No | - | Drug or structure name |
| `--mechanism` | string | No | - | Mechanism of action |
| `--indications` | string | No | - | Clinical indications |
| `--side-effects` | string | No | - | Side effects |
| `--location` | string | No | - | Anatomical location |
| `--function` | string | No | - | Anatomical function |

## Returns

- Anki-importable TSV output
- Card fronts and backs aligned to a single learning target
- Clear note when input is incomplete or too ambiguous for safe conversion

## Example

`Q: What is the mechanism of metformin?`

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Local Python script execution only | Medium |
| Network Access | No external API calls | Low |
| File System Access | Reads local input files and writes output deck | Medium |
| Instruction Tampering | Standard prompt-guided workflow | Low |
| Data Exposure | Output remains in workspace unless shared by user | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (`../`)
- [ ] Output does not expose sensitive information not present in input
- [ ] Prompt injection protections in place
- [ ] Input file paths validated before execution
- [ ] Output directory restricted to workspace
- [ ] Error messages kept concise and non-deceptive
- [ ] Dependencies reviewed before broader deployment

## Prerequisites

No additional Python packages required for the packaged entry point.

## Evaluation Criteria

### Success Metrics
- [ ] Script path parses successfully
- [ ] Card structure is atomic and importable
- [ ] Output stays within provided study source
- [ ] Missing data triggers explicit fallback behavior

### Test Cases
1. **Basic Functionality**: Help output and script parse succeed
2. **Edge Case**: Missing structured fields triggers bounded fallback
3. **Output Quality**: Cards remain concise and non-duplicative

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-20
- **Known Issues**: Raw prose still requires manual curation before import at scale
- **Planned Improvements**:
  - Safer direct-text parsing for non-file inputs
  - More explicit tag presets by subject

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

This skill accepts requests that match the documented purpose of `anki-card-creator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `anki-card-creator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
