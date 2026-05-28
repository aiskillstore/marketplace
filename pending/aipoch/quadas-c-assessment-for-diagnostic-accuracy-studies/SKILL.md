---
name: quadas-c-assessment-for-diagnostic-accuracy-studies
description: Automated bias assessment for diagnostic accuracy studies using QUADAS-C criteria. Requires full text input.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# QUADAS-C Assessment Skill

This skill automates the risk of bias assessment for diagnostic accuracy studies comparing two or more index tests (QUADAS-C).

## When to Use

- Use this skill when you need automated bias assessment for diagnostic accuracy studies using quadas-c criteria. requires full text input in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `quadas-c-assessment for diagnostic accuracy studies` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Automated bias assessment for diagnostic accuracy studies using QUADAS-C criteria. Requires full text input.
- Packaged executable path(s): `scripts/extract_pdf.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/quadas-c-assessment-for-diagnostic-accuracy-studies"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## When to Use This Skill

Use this skill when:
1.  You have the full text of a clinical research paper.
2.  You need to assess the risk of bias using the QUADAS-C tool.
3.  The study compares at least two diagnostic methods.

## Usage

The skill processes the paper through the following steps:
1.  **Extraction**: Identifies diagnostic methods compared in the study.
2.  **Assessment**: For each method, runs a QUADAS-2 assessment.
3.  **Signaling Questions**: Answers specific QUADAS-C signaling questions for 4 domains:
    -   Patient Selection
    -   Index Test
    -   Reference Standard
    -   Flow and Timing
4.  **Risk of Bias**: Determines "Low", "High", or "Unclear" risk for each domain.
5.  **Reporting**: Generates a structured JSON report.

## Execution

To run the assessment, use the provided Python script. You can pass the paper text as a command-line argument or via a file.

```bash

# Example: Process a text file containing the paper
python scripts/quadas_c.py --file "path/to/paper.txt"
```

## Output Format

The output is a JSON object with the following structure:

```json
{
  "P": "Low/High/Unclear",
  "I": "Low/High/Unclear",
  "R": "Low/High/Unclear",
  "FT": "Low/High/Unclear"
}
```

## Reference

See `references/prompts.md` for the specific signaling questions and risk of bias criteria used in the LLM prompts.

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:
