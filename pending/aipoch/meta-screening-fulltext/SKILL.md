---
name: meta-screening-fulltext
description: Screen full-text papers against inclusion/exclusion criteria, with optional PubMed metadata check using PMID. Use when the user needs to evaluate a paper for a meta-analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Paper Screening (Full Text + PubMed)

This skill screens a medical paper to determine if it should be included in a meta-analysis based on PICO criteria. It can optionally fetch metadata (Title/Abstract) from PubMed if a PMID is provided.

## When to Use

- Use this skill when you need screen full-text papers against inclusion/exclusion criteria, with optional pubmed metadata check using pmid. use when the user needs to evaluate a paper for a meta-analysis in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/extract_pdf.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-screening-fulltext` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Screen full-text papers against inclusion/exclusion criteria, with optional PubMed metadata check using PMID. Use when the user needs to evaluate a paper for a meta-analysis.
- Packaged executable path(s): `scripts/extract_pdf.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-screening-fulltext"
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

1.  **Analyze Inputs**:
    *   `input_paper`: Full text of the paper.
    *   `inclu_exclu_criterion`: Inclusion/Exclusion criteria.
    *   `input_pmid` (Optional): PMID of the paper.

2.  **Check PubMed (Optional)**:
    *   If `input_pmid` is provided, run `scripts/query_pubmed.py` to fetch Title and Abstract.
    *   Command: `python scripts/query_pubmed.py "<input_pmid>"`

3.  **Screen Paper**:
    *   **Scenario A: PubMed Hit**: If the script returns metadata, compare the criteria against this data (Title + Abstract).
    *   **Scenario B: No PubMed Data**: Compare the criteria against `input_paper` (full text).
    *   Use the appropriate prompt from `references/screening_prompts.md`.

4.  **Format Output**:
    *   Ensure the output is a JSON object with `Result` ("Include" or "Exclude") and `Reason`.
    *   If "Exclude", the reason must be one of the standard exclusion categories (Wrong population, etc.).

## Quality Rules

*   **Evidence-Based**: Decisions must be based strictly on the provided text or retrieved metadata.
*   **Structured Output**: Final output must always be parseable JSON.
*   **Exclusion Reasons**: Must use standard terminology: "Wrong population", "Wrong intervention", "Wrong comparator", "Wrong outcomes", "Wrong study design".

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:
