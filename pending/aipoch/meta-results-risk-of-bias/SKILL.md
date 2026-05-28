---
name: meta-results-risk-of-bias
description: Generates the "Risk of Bias" results section for a meta-analysis based on assessment tables and statistics. Use when the user wants to draft the risk of bias analysis text from provided data tables.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates the "Risk of Bias" results section for a meta-analysis based on assessment tables and statistics. Use when the user wants to draft the risk of bias analysis text from provided data tables.
- Packaged executable path(s): `scripts/format_result.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Academic Writing/meta-results-risk-of-bias"
python -m py_compile scripts/format_result.py
python scripts/format_result.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/format_result.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/format_result.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/format_result.py --help
```

# Risk of Bias Results Generator

This skill generates a professional, academic "Risk of Bias" results section for a meta-analysis. It analyzes the provided statistics and detailed assessment table, drafts the text using a clinical expert persona, and automatically formats the output with necessary figure citations.

## When to Use This Skill

Use this skill when the user provides:
1.  **Title**: The title of the meta-analysis.
2.  **Language**: Target language (Chinese or English).
3.  **Statistics**: A summary table of bias risk assessment.
4.  **Detailed Assessment Table**: Detailed scores for each study across domains (D1-D5).

And asks for:
-   A draft of the "Results" section regarding risk of bias.
-   An analysis of the bias risk.

## Workflow

1.  **Draft Text**: Analyze the input tables and draft an academic summary (>300 words).
    -   Summarize overall risk (High, Some concerns, Low).
    -   Analyze each domain (D1-D5) specifically.
    -   Use specific numbers from the statistics table.
2.  **Format Output**: Automatically insert the figure citation `(Figure 1)` before the last punctuation and append the figure caption.

## Usage Instructions

### 1. Draft the Content

Use the following prompt to generate the initial text:

**Role**: Clinical Medical Expert

**Task**: Write an academic "Results" section based on the following inputs:
-   **Title**: {{title}}
-   **Detailed Assessment Table**: {{Detailed_Assessment_Table}}
-   **Statistics**: {{statistics}}

**Requirements**:
1.  Explicitly state the total number of studies evaluated.
2.  First, summarize the **Overall bias risk** (High, Some concerns, Low).
3.  Then, **analyze each domain (D1-D5)** specifically.
4.  Use **specific numbers** from the statistics table.
5.  Maintain a professional, objective, academic style.
6.  Length: >300 words.
7.  Language: {{language}}

### 2. Format the Result

Run the formatting script to insert the figure citation and caption.

```bash
python scripts/format_result.py --text "<generated_text>" --language "{{language}}"
```

## Tools and Scripts

-   `scripts/format_result.py`: Inserts `(Figure 1)` and appends the figure placeholder and caption.

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
- If a file is produced, prefer a deterministic output name such as `meta_results_risk_of_bias_result.md` unless the skill documentation defines a better convention.
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
python scripts/format_result.py --help
```

Expected output format:

```text
Result file: meta_results_risk_of_bias_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
