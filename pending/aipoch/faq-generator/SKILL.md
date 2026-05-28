---
name: faq-generator
description: Generates FAQ lists from complex medical policies or protocols. Trigger when user provides medical documents, policies, or protocols and requests FAQ generation, patient education materials, or simplified explanations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# FAQ Generator

Creates FAQ lists from medical documents.

## When to Use

- Use this skill when the task needs Generates FAQ lists from complex medical policies or protocols. Trigger when user provides medical documents, policies, or protocols and requests FAQ generation, patient education materials, or simplified explanations.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Generates FAQ lists from complex medical policies or protocols. Trigger when user provides medical documents, policies, or protocols and requests FAQ generation, patient education materials, or simplified explanations.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/faq-generator"
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

## Features

- Automatic Q&A generation
- Policy interpretation
- Patient-friendly language
- Structured formatting

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | Yes | Source document file path |
| `--audience`, `-a` | string | general | No | Target audience (patients, researchers, general) |
| `--output`, `-o` | string | stdout | No | Output file path |
| `--format`, `-f` | string | json | No | Output format (json, markdown, text) |

## Output Format

```json
{
  "faqs": [{"question": "", "answer": ""}],
  "topic": "string"
}
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | No scripts included | Low |
| Network Access | No external API calls | Low |
| File System Access | Read-only within workspace | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Input/output within session | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] No network requests to external services
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place

## Evaluation Criteria

### Success Metrics
- [ ] FAQ accurately represents source document content
- [ ] Language is appropriate for specified audience (patients/researchers)
- [ ] Questions cover key points of the document
- [ ] Answers are clear, concise, and medically accurate
- [ ] Format follows structured JSON schema

### Test Cases
1. **Basic FAQ Generation**: Input simple medical protocol → Output valid FAQ list
2. **Audience Adaptation**: Same input with different audiences → Appropriate tone shift
3. **Complex Document**: Input lengthy policy document → Comprehensive FAQ coverage
4. **Edge Case**: Input ambiguous content → Handles gracefully with clarifying questions

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Add support for multi-language output
  - Enhance medical terminology handling

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

This skill accepts requests that match the documented purpose of `faq-generator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `faq-generator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
