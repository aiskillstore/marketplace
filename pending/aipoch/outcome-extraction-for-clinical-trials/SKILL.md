---
name: outcome-extraction-for-clinical-trials
description: Clinical research outcome extraction for meta-analysis. Use when users need to extract outcome measures (binary, continuous, or survival data) from clinical research papers for systematic review and meta-analysis. Handles both database lookup by PMID and real-time LLM extraction.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Clinical Outcome Extraction

Extract structured outcome data from clinical research papers for meta-analysis.

## When to Use

- Use this skill when you need clinical research outcome extraction for meta-analysis. use when users need to extract outcome measures (binary, continuous, or survival data) from clinical research papers for systematic review and meta-analysis. handles both database lookup by pmid and real-time llm extraction in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `outcome-extraction for clinical trials` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Clinical research outcome extraction for meta-analysis. Use when users need to extract outcome measures (binary, continuous, or survival data) from clinical research papers for systematic review and meta-analysis. Handles both database lookup by PMID and real-time LLM extraction.
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/outcome-extraction-for-clinical-trials"
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

## Workflow

1. **Input Processing**
   - User provides: full paper text + optional PMID
   - If PMID provided: query database first for existing results
   - If no PMID or no database match: proceed to LLM extraction

2. **Outcome Identification** (LLM)
   - Extract all outcome measures from the paper
   - Determine outcome types: binary, continuous, or survival
   - Identify measurement time points
   - Output JSON format with outcome classification

3. **Data Classification** (Code)
   - Separate outcomes into three categories:
     - `bi_outcomes`: Binary/dichotomous outcomes
     - `con_outcomes`: Continuous outcomes
     - `sur_outcomes`: Survival outcomes

4. **Data Extraction by Type**

### Binary Outcomes
Extract for each intervention group:
- Sample size (n)
- Number of events (event)

### Continuous Outcomes
Extract for each intervention group:
- Sample size (n)
- Mean (mean)
- Standard deviation (sd)

### Survival Outcomes
Extract for each intervention group:
- Sample size (n)
- Hazard ratio (HR)
- 95% Lower CI
- 95% Upper CI

5. **Output Formatting**
   - Combine all extracted data
   - Ensure consistent JSON structure
   - Convert values to strings

## Output Format

```json
[
  {
    "outcome_name": "PFS",
    "detection_time_point": "12 months",
    "groups": [
      {
        "group_name": "Treatment A",
        "sample_size": "100",
        "outcome_type": "Binary|Continuous|Survival",
        "data": [
          {"value_type": "Events|Mean|SD|HR|95%Lower CI|95%Upper CI", "value": "25"}
        ]
      }
    ]
  }
]
```

## ‼️‼️‼️See references (extraction-promots.md) for detailed JSON structures for each outcome type (binary, continuous, survival)‼️‼️‼️

## Requirements

- Extract from full text, not just abstract
- Consider ALL intervention groups in the paper
- Include ALL outcome measures of interest
- Report all data regardless of statistical significance
- Use specific group names (intervention names in English), not generic terms like "treatment group"
- Output in JSON format
- Output language: English for all field values
- If data not found: output blank space ""
