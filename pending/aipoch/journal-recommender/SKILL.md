---
name: journal-recommender
description: Recommend academic journals based on manuscript topic, abstract, and impact factor expectations. Use when the user wants to find suitable journals for their research manuscript, especially when they provide a topic, abstract, and target Impact Factor.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Journal Recommender

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Recommend academic journals based on manuscript topic, abstract, and impact factor expectations. Use when the user wants to find suitable journals for their research manuscript, especially when they provide a topic, abstract, and target Impact Factor.
- Packaged executable path(s): `scripts/journal_ranker.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Others/journal-recommender"
python -m py_compile scripts/journal_ranker.py
python scripts/journal_ranker.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/journal_ranker.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Overview` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/journal_ranker.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Overview
This skill analyzes a research manuscript (topic, abstract, and optional full text) to extract key information (keywords, field, workload, innovation) and recommends journals in three categories: Sprint (High), Robust (Match), and Safe (Low).

## Workflow

1.  **Assess Manuscript**:
    *   Analyze the provided `topic` and `abstract`.
    *   Extract keywords and determine the specific research field.
    *   Evaluate the workload and innovation of the study.
    *   Estimate the manuscript's potential Impact Factor (IF).

2.  **Recommend Journals**:
    *   Based on the assessment and the user's `target_if`, search for and recommend journals.
    *   Categorize recommendations into:
        *   **Sprint Journals**: IF slightly higher than target (max +5).
        *   **Robust Journals**: IF matches the target and assessment.
        *   **Safe Journals**: IF lower than target, ensuring high acceptance chance.
    *   Ensure at least 5 journals per category.
    *   **Constraint**: Do not recommend journals from the CAS warning list.

## Usage

### Inputs
*   `topic` (Required): The title or topic of the manuscript.
*   `abstract` (Required): The abstract of the manuscript.
*   `target_if` (Required): The expected Impact Factor (number).
*   `manuscript` (Optional): Full text of the manuscript.
*   `article_type` (Default: "research article"): Type of the article.

### Deterministic Operations
*   **Sorting**: The recommended journals are sorted by Impact Factor in descending order using `scripts/journal_ranker.py`.

## Quality Rules
*   **IF Sorting**: Journals must be strictly sorted by IF.
*   **Safety**: No CAS warning journals are allowed.
*   **Quantity**: Minimum 5 journals per category.

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
- If a file is produced, prefer a deterministic output name such as `journal_recommender_result.md` unless the skill documentation defines a better convention.
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
python scripts/journal_ranker.py --help
```

Expected output format:

```text
Result file: journal_recommender_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
