---
name: meta-abstract-screener
description: Screens research papers based on title/abstract and inclusion criteria, providing a structured Yes/No/Maybe decision. Use when you need to filter literature for meta-analysis or systematic reviews.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Abstract Screener

This skill helps screen research papers by analyzing their titles and abstracts against specific inclusion/exclusion criteria. It follows a rigorous two-step process to ensure consistency and strictly excludes systematic reviews/meta-analyses unless otherwise specified.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Screens research papers based on title/abstract and inclusion criteria, providing a structured Yes/No/Maybe decision. Use when you need to filter literature for meta-analysis or systematic reviews.
- Packaged executable path(s): `scripts/screen_paper.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-abstract-screener"
python -m py_compile scripts/screen_paper.py
python scripts/screen_paper.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/screen_paper.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/screen_paper.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

To screen a paper, follow this process:

1.  **Analysis Phase**
    *   Read the **Paper Title and Abstract** and the **Inclusion/Exclusion Criteria**.
    *   Apply the screening logic defined in `references/screening_prompts.md` (Step 1).
    *   **Note**: Be particularly vigilant about excluding other "Systematic Reviews" or "Meta-analyses".

2.  **Formatting Phase**
    *   Take the conclusion from the Analysis Phase.
    *   Format it into a JSON object using the schema defined in `references/screening_prompts.md` (Step 2).
    *   The output must contain strictly `Result` and `Reason`.

3.  **Validation (Optional)**
    *   If you need to verify the output format programmatically, use the included script:
        ```bash
        python scripts/screen_paper.py '<json_output>'
        ```

## Resources

*   **Prompts**: `references/screening_prompts.md` - Contains the detailed role definitions and logic for the LLM.
*   **Validation**: `scripts/screen_paper.py` - Ensures the output JSON matches the required schema.

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
- If a file is produced, prefer a deterministic output name such as `meta_abstract_screener_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/screen_paper.py --help
```

Expected output format:

```text
Result file: meta_abstract_screener_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
