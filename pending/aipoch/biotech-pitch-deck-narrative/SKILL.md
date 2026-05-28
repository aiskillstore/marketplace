---
name: biotech-pitch-deck-narrative
description: Use biotech-pitch-deck-narrative for academic writing workflows that need structured investor-facing storytelling, explicit assumptions, and clear output boundaries.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Biotech Pitch Deck Narrative

Structured biotech fundraising narrative design with explicit scope limits.

## When to Use

- Use this skill when the task needs a biotech pitch narrative, investor-facing section rewrite, or fundraising story structure grounded in available scientific and business inputs.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use biotech-pitch-deck-narrative for academic writing workflows that need structured investor-facing storytelling, explicit assumptions, and clear output boundaries.
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
cd "20260318/scientific-skills/Academic Writing/biotech-pitch-deck-narrative"
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

1. Confirm the financing stage, investor audience, available evidence, and non-negotiable claim boundaries.
2. Check whether the request is for a full narrative, a single section rewrite, or high-level messaging guidance.
3. Use the packaged script for supported stage and audience framing; otherwise provide a manual narrative scaffold without inventing data.
4. Return a structured deck narrative that separates assumptions, value claims, evidence status, and open diligence gaps.
5. If scientific support or market context is missing, stop and request the minimum additional inputs.

## Use Cases

- Seed deck messaging for platform biotech companies
- Rewriting a science-heavy section for generalist investors
- Preparing a risk-aware investor Q&A scaffold

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--stage` | string | No | `seed` | Financing stage (`pre-seed`, `seed`, `series-a`, `series-b`, `series-c`, `ipo`) |
| `--audience` | string | No | `generalist-vc` | Target investor audience |
| `--input` | string | No | - | Input deck or source file path |
| `--output` | string | No | `optimized_narrative.json` | Output file path |

## Returns

- Investor-facing narrative scaffold
- Stage- and audience-aware positioning cues
- Explicit note where evidence is missing or claims require validation

## Example

`python scripts/main.py --stage series-a --audience biotech-specialist`

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Local Python script execution only | Medium |
| Network Access | No external API calls | Low |
| File System Access | Optional local file input and JSON output | Medium |
| Instruction Tampering | Standard prompt-guided workflow | Low |
| Data Exposure | Sensitive fundraising content remains in workspace | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (`../`)
- [ ] Claims are tied to supplied evidence, not invented data
- [ ] Regulatory and clinical statements remain bounded
- [ ] Output path reviewed before overwrite
- [ ] Error handling does not imply completed diligence
- [ ] Market-sizing claims require user-supplied assumptions
- [ ] Legal and scientific review remains mandatory

## Prerequisites

No additional Python packages required for the packaged entry point.

## Evaluation Criteria

### Success Metrics
- [ ] Script path parses successfully
- [ ] Help output documents supported framing options
- [ ] Narrative remains within supplied scientific and commercial evidence
- [ ] Missing data triggers explicit assumption or stop conditions

### Test Cases
1. **Basic Functionality**: Help output and script parse succeed
2. **Edge Case**: Missing evidence triggers bounded fallback
3. **Output Quality**: Claims, risks, and diligence gaps stay clearly separated

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-20
- **Known Issues**: Live market validation and competitive diligence still require external review
- **Planned Improvements**:
  - Safer section-level examples for audit coverage
  - More explicit investor Q&A output modes

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

This skill accepts requests that match the documented purpose of `biotech-pitch-deck-narrative` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `biotech-pitch-deck-narrative` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
