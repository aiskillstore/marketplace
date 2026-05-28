---
name: blind-review-sanitizer
description: Use blind-review-sanitizer for academic writing workflows that need structured anonymization, explicit assumptions, and clear output boundaries for double-blind submission.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Blind Review Sanitizer

Structured manuscript anonymization for double-blind peer review.

## When to Use

- Use this skill when the task needs removal or review of author-identifying content in manuscripts prepared for double-blind submission.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use blind-review-sanitizer for academic writing workflows that need structured anonymization, explicit assumptions, and clear output boundaries for double-blind submission.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `docx`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/blind-review-sanitizer"
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

1. Confirm the submission target, source file type, anonymization strictness, and whether acknowledgments should be preserved.
2. Check whether the provided material is a supported file format and whether author names or known identifiers are available.
3. Use the packaged script for supported files; otherwise produce a manual anonymization checklist without claiming full sanitization.
4. Return the sanitized artifact or a verification plan that separates changes made, remaining risks, and manual review points.
5. If the request lacks a file path or enough identifiers, stop and request the minimum missing input.

## Use Cases

- Blind a manuscript before conference submission
- Review acknowledgments and self-citations for deanonymization risk
- Produce a manual anonymity checklist when automated processing is not possible

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--input`, `-i` | string | Yes | - | Input manuscript file path (`.docx`, `.md`, `.txt`) |
| `--output`, `-o` | string | No | auto-generated | Output path with blinded suffix when omitted |
| `--authors` | string | No | - | Comma-separated author names for stronger detection |
| `--keep-acknowledgments` | flag | No | false | Preserve acknowledgment section |
| `--highlight-self-cites` | flag | No | false | Highlight self-citations without replacement |

## Returns

- Sanitized manuscript file for supported formats
- Summary of removed identifiers when available
- Explicit note when manual verification is still required

## Example

`python scripts/main.py --input manuscript.md --authors "Alice Chen,Bob Smith"`

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Local Python script execution only | Medium |
| Network Access | No external API calls | Low |
| File System Access | Reads manuscript files and writes blinded output | Medium |
| Instruction Tampering | Standard prompt-guided workflow | Low |
| Data Exposure | Sensitive manuscript content remains local to workspace | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (`../`)
- [ ] Sensitive manuscript content stays within approved workspace
- [ ] Input file paths validated before processing
- [ ] Output file path reviewed before overwrite
- [ ] Error messages do not fabricate successful sanitization
- [ ] Manual review required before submission
- [ ] Metadata cleanup handled separately when needed

## Prerequisites

Optional dependency: `python-docx` is required only for `.docx` processing.

## Evaluation Criteria

### Success Metrics
- [ ] Script path parses successfully
- [ ] Help output documents supported options
- [ ] Sanitization stays within double-blind preparation scope
- [ ] Missing file or missing identifiers trigger bounded fallback

### Test Cases
1. **Basic Functionality**: Help output and script parse succeed
2. **Edge Case**: Missing file path triggers explicit stop condition
3. **Output Quality**: Remaining anonymity risks are called out clearly

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-20
- **Known Issues**: File metadata and embedded image review still require manual checks
- **Planned Improvements**:
  - Safer sample-file smoke test for richer audit coverage
  - More explicit metadata cleanup guidance

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

This skill accepts requests that match the documented purpose of `blind-review-sanitizer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `blind-review-sanitizer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
