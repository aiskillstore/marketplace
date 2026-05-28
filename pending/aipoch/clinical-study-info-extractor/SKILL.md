---
name: clinical-study-info-extractor
description: Batch extracts and verifies structured information (PMID, title, abstract, methodology, results, etc.) from clinical research literature using PMIDs. Use when the user wants to extract details from specific PMIDs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Clinical Study Info Extractor

This skill extracts structured information from clinical study literature based on provided PMIDs. It performs a search, parses the results, and uses LLM extraction with strict quality rules to produce a consolidated Markdown table.

## When to Use

- Use this skill when you need batch extracts and verifies structured information (pmid, title, abstract, methodology, results, etc.) from clinical research literature using pmids. use when the user wants to extract details from specific pmids in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/utils.py` is the most direct path to complete the request.
- Use this skill when you need the `clinical-study-info-extractor` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Batch extracts and verifies structured information (PMID, title, abstract, methodology, results, etc.) from clinical research literature using PMIDs. Use when the user wants to extract details from specific PMIDs.
- Packaged executable path(s): `scripts/utils.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/clinical-study-info-extractor"
python -m py_compile scripts/utils.py
python scripts/utils.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/utils.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/utils.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

1.  **Input Normalization**: Splits and cleans the input string of PMIDs.
2.  **Literature Search**: Queries the PubMed API directly to fetch document details.
3.  **Information Extraction**: Iterates through documents to extract fields (Title, Year, Journal, Abstract, DOI, Type, Population, Sample Size, Intervention, Results, Conclusion).
4.  **Verification**: Enforces quality rules (e.g., sample size only for research articles).
5.  **Output Formatting**: Aggregates results into a Chinese Markdown table.

## Usage

When you have a list of PMIDs and need structured details:

1.  **Normalize Input**:
    Use `scripts/utils.py` with `normalize_pmids` to parse the input string.

2.  **Search & Process**:
    Use `scripts/utils.py` with `fetch_pubmed_data` to query PubMed and get a list of document JSON strings.

3.  **Extract & Verify**:
    For each document, use the prompts defined in `references/extraction_rules.md` to extract and verify information.
    - Step 1: Extraction
    - Step 2: Verification

4.  **Format Output**:
    Use `scripts/utils.py` with `format_table` to generate the final Markdown table.

## Quality Rules

See `references/extraction_rules.md` for detailed extraction logic and constraints.
- **Article Type**: Must be one of Research, Meta-analysis, Case Report, Review.
- **Sample Size**: Numeric only, empty for non-research.
- **Intervention**: Single column, "None" if not mentioned.
- **Language**: All Chinese except Journal Name.
