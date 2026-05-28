---
name: research-article-weekly
description: Generates a weekly academic literature report based on keywords using PubMed. Use when the user wants to track recent research progress on a specific topic, automatically retrieving, classifying, and summarizing relevant papers from the last 7 days.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Research Article Weekly

This skill generates a weekly report of academic literature for a given keyword. It searches PubMed for articles published in the last 7 days, classifies them into generic research categories (Fundamental, Applied, Methodology, Review, Other), and produces a summarized report. This tool is domain-agnostic and adapts to any research field indexed in PubMed.

## When to Use

- Use this skill when you need generates a weekly academic literature report based on keywords using pubmed. use when the user wants to track recent research progress on a specific topic, automatically retrieving, classifying, and summarizing relevant papers from the last 7 days in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/pubmed_search.py` is the most direct path to complete the request.
- Use this skill when you need the `research-article-weekly` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates a weekly academic literature report based on keywords using PubMed. Use when the user wants to track recent research progress on a specific topic, automatically retrieving, classifying, and summarizing relevant papers from the last 7 days.
- Packaged executable path(s): `scripts/pubmed_search.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/research-article-weekly"
python -m py_compile scripts/pubmed_search.py
python scripts/pubmed_search.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/pubmed_search.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/pubmed_search.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Inputs

- `keywords`: The search term(s) for the literature (e.g., "lung cancer", "CRISPR", "machine learning", "climate change").

## Workflow

1.  **Search & Generate Draft Report**:
    The skill executes the bundled Python script to search PubMed and generate a draft Markdown report using rule-based classification. This provides an immediate, usable output even without LLM processing.
    
    ```bash
    python scripts/pubmed_search.py --keywords "{keywords}" --days 7 --limit 20 --format markdown
    ```

2.  **Refine Report (Optional - AI Enhanced)**:
    If an AI environment is available, the Agent can take the raw JSON output (by running with `--format json`) or the draft Markdown report and refine it using the advanced logic below for better summarization and topic extraction.

    **Classification Logic (for AI Refinement):**
    For each retrieved article (Title + Abstract), classify it using the following logic:

    **System Prompt:**
    > Act as a versatile research analyst. Your task is to categorize the research article based on its title and abstract in relation to the user's keyword: "{keywords}".
    >
    > **Research Types:**
    > 1. **Fundamental Research**: Theoretical studies, mechanisms, basic science, discovery, or foundational work.
    > 2. **Applied Research**: Practical applications, clinical trials, engineering implementations, case studies, or field deployments.
    > 3. **Methodology & Tools**: New algorithms, techniques, software, instruments, or experimental frameworks.
    > 4. **Review & Survey**: Literature reviews, meta-analyses, systematic reviews, or perspectives.
    > 5. **Other**: Education, policy, news, editorials, or papers that do not fit the above.
    > 6. **Irrelevant**: Not related to the keyword.
    >
    > **Task:**
    > 1. Assign the most appropriate **Research Type** from the list above.
    > 2. Extract a specific **Topic Tag** (1-3 words) representing the core subject (e.g., "Deep Learning", "Gene Editing", "Market Analysis").
    >
    > **Output Format:**
    > Return a valid JSON object: `{"type": "Research Type Name", "topic": "Topic Tag"}`. Do not output anything else.

3.  **Generate Final Report (for AI Refinement)**:
    Group the articles by their assigned **Research Type**. For each type that contains articles, generate a summary section.

    **System Prompt:**
    > Act as a comprehensive research summarizer compiling a "Weekly Research Update".
    >
    > **Input:** A list of research papers (Title, Journal, Abstract, Topic Tag) belonging to the Research Type: "{category}".
    >
    > **Task:** Write a concise, engaging summary for this research type.
    > - **Synthesize**: Group papers with similar **Topic Tags** and summarize their collective contribution.
    > - **Highlight**: Identify the most significant findings or innovations.
    > - **Tone**: Professional, objective, and adapted to the specific domain of the papers (e.g., formal for physics, analytical for social science). Avoid generic "excitement" unless warranted by a major breakthrough.
    > - **Reference**: List the papers with their Titles and Journals.
    >
    > **Format:**
    > ### {Category Name}
    > [General Summary Paragraph highlighting key themes]
    >
    > **Key Updates:**
    > - **[Topic Tag]**: [Summary of findings from related papers]. *Refs: [Title] (Journal)*
    > - ...
    >
    > (If a paper stands alone, list it individually)

4.  **Final Output**:
    Combine all sections into a single Markdown document titled "Weekly Research Report: {keywords}". Add a brief "Executive Summary" at the top highlighting the distribution of papers (e.g., "This week saw a focus on Applied Research in [Topic]...").

## Quality Rules

- **Source**: Must use real data returned from the `pubmed_search.py` script. Do not hallucinate papers.
- **Coverage**: Ensure all retrieved and relevant papers are included in the report.
- **Tone**: Objective, informative, and structured. Avoid overly sensational language.
- **Error Handling**: If the script returns no results, output "No significant research articles found for '{keywords}' in the last 7 days."
