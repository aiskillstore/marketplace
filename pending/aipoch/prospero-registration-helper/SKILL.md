---
name: prospero-registration-helper
description: Assists researchers in generating PROSPERO registration content for meta-analyses from a title and optional protocol. Use when the user wants to draft a PROSPERO registration form.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# PROSPERO Registration Helper

This skill helps researchers draft a PROSPERO registration form for a meta-analysis. It generates the required fields based on a study title and an optional protocol.

## When to Use

- Use this skill when you need assists researchers in generating prospero registration content for meta-analyses from a title and optional protocol. use when the user wants to draft a prospero registration form in a reproducible workflow.
- Use this skill when a protocol design task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/date_utils.py` is the most direct path to complete the request.
- Use this skill when you need the `prospero-registration-helper` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Assists researchers in generating PROSPERO registration content for meta-analyses from a title and optional protocol. Use when the user wants to draft a PROSPERO registration form.
- Packaged executable path(s): `scripts/date_utils.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Protocol Design/prospero-registration-helper"
python -m py_compile scripts/date_utils.py
python scripts/date_utils.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/date_utils.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/date_utils.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

To generate the registration draft, follow these steps:

1.  **Analyze Input**:
    *   Identify the **Title** of the review.
    *   Check if a **Protocol** text is provided.

2.  **Calculate Timeline**:
    *   Run `scripts/date_utils.py` to obtain the *Start Date* (today) and *Anticipated Completion Date* (today + 28 days).

3.  **Generate Content**:
    *   Use the prompts in `references/prompt_templates.md` to generate the registration sections.
    *   **Step 3.1: Basic Details**: Use the "Review Title and Basic Details" prompt. Extract PICO (Population, Intervention, Comparison, Outcome) from the title.
    *   **Step 3.2: Eligibility Criteria**: Use the "Eligibility Criteria" prompt.
    *   **Step 3.3: Timeline & Methods**: Use the "Timeline and Methods" prompt. Fill in the dates calculated in Step 2.

## Quality Rules

*   **Language**: All generated content **must be in English**.
*   **Placeholder Handling**:
    *   **Keep `{}`**: Content inside curly braces `{}` (e.g., `{Select the country...}`) must be preserved exactly as is. These often represent dropdown options in the PROSPERO system.
    *   **Fill `<>`**: Content inside angle brackets `<>` must be replaced with your AI-generated analysis based on the input title and protocol.
*   **PICO Extraction**: Ensure PICO elements are clearly identified and used to inform the search strategy and eligibility criteria.

## Tools

### Date Utility

Use this script to get the standard timeline dates.

```python
python scripts/date_utils.py
```
