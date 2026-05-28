---
name: meta-results-forest-plot-analyzer
description: Analyzes forest plots for meta-analysis, generating detailed descriptions and formatting figure legends in Chinese or English. Use when the user wants to interpret a forest plot image, describe its statistical significance (heterogeneity, p-value), and format the output with specific figure legends.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Analyzes forest plots for meta-analysis, generating detailed descriptions and formatting figure legends in Chinese or English. Use when the user wants to interpret a forest plot image, describe its statistical significance (heterogeneity, p-value), and format the output with specific figure legends.
- Packaged executable path(s): `scripts/format_result.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Academic Writing/meta-results-forest-plot-analyzer"
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
python scripts/validate_skill.py --help
```

## Usage

1.  **Analyze Image**: The skill first uses a Vision LLM to describe the forest plot.
2.  **Format Output**: The skill then runs a script to insert citation markers and append figure legends.

## Workflow

### 1. Image Analysis (Vision LLM)

The model analyzes the provided forest plot image along with optional metadata (title, statistics, outcome name).

**Prompt Guidelines:**
*   Describe the forest plot in detail (>300 words).
*   Include heterogeneity (I²), P-value, and effect sizes.
*   Mention the number of studies and sample sizes if visible.
*   Conclude on the statistical significance.
*   **Language**: Strictly follow the requested language (Chinese or English).

### 2. Output Formatting (Script)

Run `scripts/format_result.py` to finalize the text.

**Formatting Rules:**
*   **Citation**: Inserts `(Figure 2)` before the last punctuation mark of the description.
*   **Header**: Adds `**Forest Plot**` (English) .
*   **Footer**: Appends a placeholder for the image and the figure legend:
    *   English: `**Figure 2 Forest plot of the pooled effect size**`

## Examples

**User Input:**
> "Analyze this forest plot. Title: 'Effect of X on Y'. Statistics: I2=50%. Language: English."

**Process:**
1.  LLM generates description: "... The heterogeneity was moderate (I²=50%). .. The results were significant."
2.  Script formats it:
    > **Forest Plot**
    >
    > ... The results were significant(Figure 2).
    >
    > {insert your image here}
    >
    > **Figure 2 Forest plot of the pooled effect size**

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
- If a file is produced, prefer a deterministic output name such as `meta_results_forest_plot_analyzer_result.md` unless the skill documentation defines a better convention.
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
Result file: meta_results_forest_plot_analyzer_result.md
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
