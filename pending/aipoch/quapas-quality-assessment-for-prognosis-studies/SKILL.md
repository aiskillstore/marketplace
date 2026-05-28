---
name: quapas-quality-assessment-for-prognosis-studies
description: Evaluates bias in medical literature (prognosis studies) using QUAPAS criteria. Use when the user wants to assess the quality or risk of bias of a medical paper text.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# QUAPAS Bias Evaluator

## When to Use

- Use this skill when you need evaluates bias in medical literature (prognosis studies) using quapas criteria. use when the user wants to assess the quality or risk of bias of a medical paper text in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `quapas-quality-assessment for prognosis studies` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Evaluates bias in medical literature (prognosis studies) using QUAPAS criteria. Use when the user wants to assess the quality or risk of bias of a medical paper text.
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/quapas-quality-assessment-for-prognosis-studies"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Description
This skill evaluates the risk of bias in prognosis studies using the Quality of Prognosis Studies (QUAPAS) tool. It analyzes 5 domains: Participants, Index Test, Outcome, Flow and Timing, and Analysis.

## Workflow

1.  **Input**: The user provides the full text of a medical paper.

2.  **Study Extraction**:
    - Extract the first author's name and year (e.g., "Wang, 2018").

3.  **Domain Analysis**:
    For each of the 5 domains, analyze the text using the questions defined in `references/quapas_prompts.md`.
    - **Domain 1**: Participants
    - **Domain 2**: Index Test
    - **Domain 3**: Outcome
    - **Domain 4**: Flow and Timing
    - **Domain 5**: Analysis

4.  **Risk of Bias (ROB) Assessment**:
    For each domain, determine the Risk of Bias (Low, High, Unclear) based on the answers to the signaling questions:
    - If **all** answers are "Yes" -> **Low Risk**.
    - If **any** answer is "No" -> **High Risk**.
    - If information is missing -> **Unclear**.

5.  **Overall Judgment**:
    Determine the overall risk of bias for the study based on the domain results.
    - If most domains are Low Risk -> Low Overall Bias.
    - If key domains are High Risk -> High Overall Bias.

6.  **Final Output**:
    Generate a JSON object strictly following the schema below:
    ```json
    {
      "study": "Author, Year",
      "D1": "Low|High|Unclear",
      "D2": "Low|High|Unclear",
      "D3": "Low|High|Unclear",
      "D4": "Low|High|Unclear",
      "D5": "Low|High|Unclear",
      "overall": "Low|High|Unclear"
    }
    ```

## References
- See [references/quapas_prompts.md](references/quapas_prompts.md) for detailed signaling questions and prompt logic.

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:
