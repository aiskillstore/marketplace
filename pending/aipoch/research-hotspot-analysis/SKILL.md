---
name: research-hotspot-analysis
description: Analyzes research hotspots and recommends literature based on a disease or topic. Use when the user wants to identify current research trends, hot topics, or get literature recommendations for a specific medical field or disease.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Research Hotspot Analysis

## When to Use

- Use this skill when you need analyzes research hotspots and recommends literature based on a disease or topic. use when the user wants to identify current research trends, hot topics, or get literature recommendations for a specific medical field or disease in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/analysis_ops.py` is the most direct path to complete the request.
- Use this skill when you need the `research-hotspot-analysis` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Analyzes research hotspots and recommends literature based on a disease or topic. Use when the user wants to identify current research trends, hot topics, or get literature recommendations for a specific medical field or disease.
- Packaged executable path(s): `scripts/analysis_ops.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/research-hotspot-analysis"
python -m py_compile scripts/analysis_ops.py
python scripts/analysis_ops.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/analysis_ops.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/analysis_ops.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Description
This skill analyzes research hotspots for a given disease or topic by searching recent literature, calculating keyword frequencies, clustering topics, and recommending high-impact papers.

## Usage
1.  **Input**: The user provides a disease name or research topic (e.g., "Lung Cancer", "Diabetes").
2.  **Process**:
    *   Searches for recent literature (PMIDs) using the internal literature database.
    *   Analyzes MESH terms to calculate word frequency and identify top keywords.
    *   Uses LLM to cluster keywords into "Hotspot Topics".
    *   Matches specific PMIDs to each topic.
    *   Fetches full details (PMC) for top-ranked papers (by JIF/Availability).
    *   Generates a comprehensive report with an introduction and detailed hotspot analysis.
3.  **Output**: A Markdown report containing the research overview and specific paper recommendations per hotspot.

## Workflow

1.  **Search Literature**: Use `scripts/analysis_ops.py` (`search_pubmed`) to find relevant PMIDs and fetch details.
2.  **Analyze Keywords**: Use `scripts/analysis_ops.py` (`word_frequency`) on the `medline_texts` output from Step 1 to find top MESH terms.
3.  **Identify Topics**: Use LLM with `references/prompt_templates.md` (Hotspot Analysis) to group keywords into topics.
4.  **Match Evidence**: Use `scripts/analysis_ops.py` (`match_keywords`) with `documents` from Step 1 to map PMIDs to topics.
5.  **Fetch Details**: For each topic, select top papers using `scripts/analysis_ops.py` (`sort_by_jif_and_select`) and fetch details using `fetchPMCArticleDetails`.
6.  **Generate Report**: Synthesize the findings into a final report using LLM.

## Tools
*   `fetchPMCArticleDetails`: Get article details.
*   `fetchPubmedArticleDetails`: Get PubMed details.

## Scripts
*   `scripts/analysis_ops.py`: Contains helper functions for PubMed search, frequency analysis, keyword matching, and result formatting.

## References
*   `references/prompt_templates.md`: Contains the system prompts for LLM analysis.
