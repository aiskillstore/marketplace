---
name: meta-title-generator
description: Generates Meta-Analysis research titles based on user keywords, utilizing PubMed search results if available, or creative generation otherwise. Use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta-Analysis Title Generator

## When to Use

- Use this skill when you need generates meta-analysis research titles based on user keywords, utilizing pubmed search results if available, or creative generation otherwise. use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/search_pubmed.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-title-generator` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates Meta-Analysis research titles based on user keywords, utilizing PubMed search results if available, or creative generation otherwise. Use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic.
- Packaged executable path(s): `scripts/search_pubmed.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/meta-title-generator"
python -m py_compile scripts/search_pubmed.py
python scripts/search_pubmed.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/search_pubmed.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/search_pubmed.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Description
This skill generates research titles for Meta-Analysis studies. It takes user-provided keywords, searches PubMed to find relevant literature, and proposes titles based on the findings. If no literature is found, it creatively generates titles based on the keywords. It outputs 5 titles in both English and Chinese.

## Usage

### 1. Search and Generate
When the user provides keywords (e.g., "lung cancer", "hypertension"), follow these steps:

1.  **Generate Search Strategy**: Convert the user's keywords into a PubMed search strategy string (English keywords combined with AND/OR).
2.  **Search PubMed**: Run `scripts/search_pubmed.py` with the search strategy.
    *   This script returns a JSON object containing the count of results and a summary of papers (if any).
3.  **Check Results**:
    *   If the result count is > 0:
        *   Analyze the papers found (provided in the script output).
        *   Generate 5 Meta-Analysis titles based on the PICOs (Participant, Intervention, Comparison, Outcome, Study design) of these papers.
    *   If the result count is 0:
        *   Generate 5 Meta-Analysis titles creatively based on the original keywords.
4.  **Format Output**:
    *   Present the titles in a specific JSON format containing "Title1" to "Title5", each with "English" and "Chinese" fields.
    *   Ensure titles are strictly for Meta-Analysis (not clinical trials).
    *   Ensure interventions specify a drug or treatment method.

## Quality Rules
*   **Meta-Analysis Focus**: Titles must clearly indicate a Systematic Review and Meta-Analysis.
*   **Specific Interventions**: Do not use broad terms; specify the drug or method.
*   **Bilingual Output**: Every title must have an English and Chinese version.

## Reference Material
For detailed prompting strategies used in title generation, see [references/title_generation_prompts.md](references/title_generation_prompts.md).
