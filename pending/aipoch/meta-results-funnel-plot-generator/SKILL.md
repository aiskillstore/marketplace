---
name: meta-results-funnel-plot-generator
description: Generates a Meta-analysis results section description for funnel plots, including statistical tables (Egger's, Begg's, Trim & Fill) and figure legends. Supports English and Chinese outputs. Use when user provides a funnel plot image and statistics and wants a formatted report.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta-Analysis Funnel Plot Generator

This skill generates a standardized meta-analysis result section based on a funnel plot image, statistical data, and a title. It orchestrates LLM generation for descriptions and tables, then uses a Python script to assemble the final report.

## When to Use

- Use this skill when you need generates a meta-analysis results section description for funnel plots, including statistical tables (egger's, begg's, trim & fill) and figure legends. supports english and chinese outputs. use when user provides a funnel plot image and statistics and wants a formatted report in a reproducible workflow.
- Use this skill when a academic writing task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/main.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-results-funnel-plot-generator` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates a Meta-analysis results section description for funnel plots, including statistical tables (Egger's, Begg's, Trim & Fill) and figure legends. Supports English and Chinese outputs. Use when user provides a funnel plot image and statistics and wants a formatted report.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Academic Writing/meta-results-funnel-plot-generator"
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

## Usage

Trigger this skill when the user provides:
1.  **Funnel Plot Image**: The visual plot.
2.  **Statistics**: Text containing statistical data (Egger's test, Begg's test, Trim & Fill).
3.  **Title/Outcome**: Context for the analysis.
4.  **Language**: "Chinese" or "English".

## Workflow

1.  **Generate Description**: Use LLM to describe the funnel plot (symmetry, outliers) based on the image and stats.
2.  **Generate Tables**: Use LLM to format the provided statistics into three specific Markdown tables:
    *   Egger's test (Bias assessment)
    *   Begg's test
    *   Trim and Fill method
3.  **Assemble Report**: Run `scripts/main.py` to:
    *   Clean LLM outputs (remove markdown fences).
* Insert figure reference "(Figure 3)" or "(Figure 3)" into the description.    *   Combine Description, Image Placeholder, Figure Legend, and Tables into the final output.

## Quality Rules

*   **Language**: Output must match the requested language (Chinese/English).
*   **Structure**: The final output must strictly follow the order: Description -> Figure -> Legend -> Tables.
*   **Formatting**: Tables must be standard Markdown.

## Reference

See [prompts.md](references/prompts.md) for the LLM prompts used in this workflow.
