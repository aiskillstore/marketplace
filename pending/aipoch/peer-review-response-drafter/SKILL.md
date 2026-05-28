---
name: peer-review-response-drafter
description: Assist in drafting professional peer review response letters. Trigger.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Peer Review Response Drafter

Assist researchers in crafting professional, polite, and effective responses to peer reviewer comments for academic journal submissions.

## When to Use

- Use this skill when the task needs Assist in drafting professional peer review response letters. Trigger.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Assist in drafting professional peer review response letters. Trigger.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `enum`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/peer-review-response-drafter"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Overview` above for related details.

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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Overview

This skill parses reviewer comments, drafts structured responses, and adjusts tone to ensure:
- Professional and courteous language
- Clear point-by-point addressing of concerns
- Constructive framing of disagreements
- Consistent academic writing style

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Input Format

Accept multiple input formats:
- Copy-pasted reviewer comments
- PDF extracted text
- Structured JSON with comment IDs
- Markdown with sections

## Output Format

Returns a complete response letter with:
- Proper salutation and closing
- Numbered responses matching reviewer comments
- Inline citations to manuscript locations
- Professional academic tone throughout

## Usage Example

```
User: Help me draft a response to these reviewer comments:

Reviewer 1:
1. The introduction should better motivate the problem
2. Figure 2 is unclear
3. Have you considered Smith et al. 2023?

My changes:
1. Added motivation paragraph
2. Redrew Figure 2 with clearer labels
3. Added citation and discussion

Journal: Nature Communications
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--interactive` | flag | No | - | **Interactive mode**: Guided wizard with prompts (uses `input()`). Recommended for first-time users or complex responses |
| `--input-file` | str | No | - | Path to reviewer comments file (automation mode) |
| `--output` | str | No | - | Output file path for response letter |
| `--tone` | str | No | "diplomatic" | Response tone: "diplomatic", "formal", or "assertive" |
| `--format` | str | No | "markdown" | Output format: "markdown", "plain_text", or "latex" |
| `--include-diff` | bool | No | true | Whether to summarize changes made |

**Usage Modes:**
- **Interactive Mode**: Use `--interactive` for guided setup with prompts (recommended for first-time users)
- **File Mode (Recommended for automation)**: Use `--input-file` with pre-prepared reviewer comments

## Technical Notes

- **Difficulty**: High - Requires understanding of academic norms, context-aware tone adjustment, and nuanced handling of criticism
- **Limitations**: Does not verify factual accuracy of responses; human review required for technical content
- **Safety**: No external API calls; processes text locally

## References

- `references/response_templates.md` - Common response patterns
- `references/tone_guide.md` - Academic tone guidelines
- `references/examples/` - Sample response letters

## Quality Checklist

Before finalizing, verify:
- [ ] Every reviewer comment has a corresponding response
- [ ] Responses are numbered/lettered consistently with comments
- [ ] All changes are referenced with page/line numbers
- [ ] Disagreements are framed constructively
- [ ] No defensive or confrontational language
- [ ] Professional tone maintained throughout

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

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

This skill accepts requests that match the documented purpose of `peer-review-response-drafter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `peer-review-response-drafter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
