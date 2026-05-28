---
name: expert-interview-generator
description: Generates a full expert interview article including introduction, Q&A body, and summary based on interview questions and expert background. Use when you have interview questions and an expert profile and need a polished article.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Expert Interview Article Generator

This skill orchestrates the generation of a professional expert interview article, simulating a Dify workflow.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates a full expert interview article including introduction, Q&A body, and summary based on interview questions and expert background. Use when you have interview questions and an expert profile and need a polished article.
- Packaged executable path(s): `scripts/flow.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/expert-interview-generator"
python -m py_compile scripts/flow.py
python scripts/flow.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/flow.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/flow.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Inputs

*   `background` (Required): Expert profile (Name, Title, Affiliation, Research Direction, Achievements).
*   `question` (Required): List of interview questions.
*   `title` (Required): Article title.
*   `text1` (Optional): Existing interview draft content.

## Workflow

### Step 1: Generate Expert Introduction

Use the **Expert Introduction Prompt** in `references/prompts.md` to generate the intro section.
**Input**: `background`

### Step 2: Generate Q&A Body

Determine which generation path to use based on `text1`:

*   **Path A (With Draft)**: If `text1` is provided (not empty), use the **Body Generation (With Draft) Prompt** in `references/prompts.md`.
    *   **Inputs**: `text1`, `question`, `background`, `title`
*   **Path B (No Draft)**: If `text1` is empty, use the **Body Generation (No Draft) Prompt** in `references/prompts.md`.
    *   **Inputs**: `question`, `background`, `title`

**Constraint**: The output must be approximately 2000 words, strictly following the Q&A format defined in the prompt.

### Step 3: Generate Preface

Use the **Preface Prompt** in `references/prompts.md` to write a 150-word introduction.
**Inputs**: Generated Body (from Step 2), `title`, `background`

### Step 4: Generate Summary

Use the **Summary Prompt** in `references/prompts.md` to write a 150-word conclusion.
**Inputs**: Generated Body (from Step 2), Generated Preface (from Step 3), `background`, `title`

### Step 5: Final Assembly

Combine the generated sections into a final Markdown article using the structure below. You may use `scripts/flow.py` to handle text processing if needed, or assemble manually.

**Structure**:
1.  **Title**: `title`
2.  **Preface**: (Result from Step 3)
3.  **Expert Profile**: (Result from Step 1)
4.  **Interview Content**: (Result from Step 2)
5.  **Summary**: (Result from Step 4)

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
- If a file is produced, prefer a deterministic output name such as `expert_interview_generator_result.md` unless the skill documentation defines a better convention.
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
python scripts/flow.py --help
```

Expected output format:

```text
Result file: expert_interview_generator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
