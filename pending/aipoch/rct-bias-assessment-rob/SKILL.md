---
name: rct-bias-assessment-rob
description: "Automates Risk of Bias 2 (ROB2) assessment for RCT papers by analyzing text against specific domains and synthesizing a report. Use when you need to assess the quality of a clinical trial paper or evaluate risk of bias."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# RCT Bias Assessment (ROB2)

This skill assesses the risk of bias in Randomized Controlled Trials (RCTs) using the ROB2 tool. It analyzes the text for specific domains (Randomization, Deviations, Missing Data, Measurement, Reported Result) and synthesizes an overall judgement.

## When to Use

- Use this skill when you need automates risk of bias 2 (rob2) assessment for rct papers by analyzing text against specific domains and synthesizing a report. use when you need to assess the quality of a clinical trial paper or evaluate risk of bias in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/assess_rob2.py` is the most direct path to complete the request.
- Use this skill when you need the `rct-bias-assessment-rob2` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Automates Risk of Bias 2 (ROB2) assessment for RCT papers by analyzing text against specific domains and synthesizing a report. Use when you need to assess the quality of a clinical trial paper or evaluate risk of bias.
- Packaged executable path(s): `scripts/assess_rob2.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/rct-bias-assessment-rob2"
python -m py_compile scripts/assess_rob2.py
python scripts/assess_rob2.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/assess_rob2.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/assess_rob2.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

1.  **Input**: Provide the full text or relevant sections of the RCT paper.
2.  **Process**:
    *   The skill extracts the Study Reference (Author, Year).
    *   It assesses each of the 5 ROB2 domains in parallel (conceptually) or sequentially.
    *   It synthesizes an overall risk judgement.
    *   It outputs a JSON-structured summary and a detailed report.

## Domain Assessment Guidelines

Refer to [rob2_guidelines.md](references/rob2_guidelines.md) for the detailed questions and logic for each domain.

### Workflow Steps

1.  **Extract Study Info**: Identify the first author and year (e.g., "Wang, 2018").
2.  **Assess Domains**:
    *   **Domain 1 (Randomization)**: Check allocation sequence and concealment.
    *   **Domain 2 (Deviations)**: Check blinding and protocol deviations.
    *   **Domain 3 (Missing Data)**: Check attrition and ITT analysis.
    *   **Domain 4 (Measurement)**: Check outcome measurement appropriateness.
    *   **Domain 5 (Reported Result)**: Check for selective reporting.
3.  **Synthesize**: Determine the Overall Risk of Bias based on the domain results.
    *   **High**: Any domain is High.
    *   **Some concerns**: No High, but at least one Some concerns.
    *   **Low**: All domains are Low.

## Output Format

The final output should be a JSON object compatible with the following schema:

```json
{
  "Study": "Author, Year",
  "D1": "Low/Some concerns/High",
  "D2": "Low/Some concerns/High",
  "D3": "Low/Some concerns/High",
  "D4": "Low/Some concerns/High",
  "D5": "Low/Some concerns/High",
  "Overall": "Low/Some concerns/High"
}
```

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:

```bash
python extract_pdf.py
```

This script will:
- Extract text from the PDF file (e.g., `gefitinib nejmoa0810699.pdf`)
- Save the extracted text to `full_text.txt`
- Handle multi-page documents with proper page separators

**Usage flow:**
1. User provides PDF file path
2. Run `python extract_pdf.py` to extract text
3. Read the generated `full_text.txt` file
4. Perform ROB2 assessment on the extracted text

### Text Cleaning

Use `scripts/assess_rob2.py` to clean the text output if needed (removing markdown code blocks) or to validate the JSON structure.

```python
from scripts.assess_rob2 import clean_text

# usage
cleaned_json = clean_text(llm_output)
```

