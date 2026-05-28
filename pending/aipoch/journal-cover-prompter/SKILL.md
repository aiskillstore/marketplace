---
name: journal-cover-prompter
description: Use when creating journal cover images, generating scientific artwork prompts, or designing graphical abstracts. Creates detailed prompts for AI image generators to produce publication-quality scientific visuals.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Journal Cover Image Prompter

Generate detailed prompts for creating scientific journal cover images and graphical abstracts using AI image generators.

## When to Use

- Use this skill when the task needs Use when creating journal cover images, generating scientific artwork prompts, or designing graphical abstracts. Creates detailed prompts for AI image generators to produce publication-quality scientific visuals.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when creating journal cover images, generating scientific artwork prompts, or designing graphical abstracts. Creates detailed prompts for AI image generators to produce publication-quality scientific visuals.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/journal-cover-prompter"
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
from scripts.cover_prompter import CoverPrompter

prompter = CoverPrompter()

# Generate prompt
prompt = prompter.create_prompt(
    research_topic="CRISPR gene editing",
    visual_style="photorealistic",
    mood="hopeful",
    key_elements=["DNA strands", "molecular scissors", "cells"]
)
```

## Core Capabilities

### 1. Prompt Generation

```python
prompt = prompter.generate(
    subject="cancer immunotherapy",
    style="scientific illustration",
    color_scheme="blue_gradient",
    complexity="high"
)
```

**Prompt Structure:**
- Subject description
- Artistic style
- Color palette
- Lighting and mood
- Technical specifications

### 2. Style Selection

```python
style_guide = prompter.select_style(
    journal_type="nature",
    subject_matter="molecular_biology"
)
```

**Journal Styles:**
- Nature: Dramatic, artistic
- Cell: Clean, molecular focus
- Science: Conceptual, broad appeal
- Medical journals: Clinical, professional

### 3. Technical Specs

```python
specs = prompter.get_specs(
    journal="Nature",
    cover_type="front"
)

# Returns dimensions, resolution, color mode
```

## CLI Usage

```text
python scripts/cover_prompter.py \
  --topic "neuroscience synaptic transmission" \
  --style artistic \
  --output prompt.txt
```

---

**Skill ID**: 211 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `journal-cover-prompter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `journal-cover-prompter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
