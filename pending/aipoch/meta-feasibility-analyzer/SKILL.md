---
name: meta-feasibility-analyzer
description: Analyzes the feasibility of a proposed Meta-analysis topic by searching for existing Meta-analyses and Clinical Trials on PubMed/ClinicalTrials.gov. Use when you need to evaluate if a topic is viable for a new Meta-analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta Feasibility Analyzer

This skill evaluates the feasibility of conducting a new Meta-analysis on a given topic (title). It checks for existing Meta-analyses and available Clinical Trials to determine if there is a gap or sufficient new evidence.

## When to Use

- Use this skill when you need analyzes the feasibility of a proposed meta-analysis topic by searching for existing meta-analyses and clinical trials on pubmed/clinicaltrials.gov. use when you need to evaluate if a topic is viable for a new meta-analysis in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/feasibility_ops.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-feasibility-analyzer` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Analyzes the feasibility of a proposed Meta-analysis topic by searching for existing Meta-analyses and Clinical Trials on PubMed/ClinicalTrials.gov. Use when you need to evaluate if a topic is viable for a new Meta-analysis.
- Packaged executable path(s): `scripts/feasibility_ops.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-feasibility-analyzer"
python -m py_compile scripts/feasibility_ops.py
python scripts/feasibility_ops.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/feasibility_ops.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/feasibility_ops.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

Follow these steps to perform the analysis.

### 1. Generate Search Query

First, analyze the user's proposed title to generate a valid PubMed search query.

**Prompt for LLM:**
```text
Role: Medical Search Expert
Task: Extract keywords from the following title and create a PubMed search query.
Title: "{{input_the_title}}"

Rules:
1. Extract keywords (Disease, Intervention, Outcome).
2. Convert to standard MeSH terms if possible.
3. Combine with AND/OR.
4. Enclose the final query in braces {}.
5. Do NOT include "meta analysis" in the query.

Example Output:
{(ovarian cancer) AND (chemotherapy) AND (bevacizumab)}
```

### 2. Extract Query String

Run the extraction script to get the clean query string.

```bash
python scripts/feasibility_ops.py extract --text "{{llm_output}}"
```

Store the output as `{{search_query}}`.

### 3. Search Clinical Trials

Search for Clinical Trials via the PubMed API.

```bash
python scripts/feasibility_ops.py search --query "{{search_query}}" --type clinical
```

Store the result JSON as `{{clinical_json}}`.

### 4. Process Clinical Results

Format the clinical trial results and check the count.

```bash
python scripts/feasibility_ops.py clinical --json '{{clinical_json}}' --query "{{search_query}}"
```

Parse the output JSON to get:
- `clinical_count`: Number of trials found.
- `clinical_summary`: Formatted summary string.

### 5. Feasibility Check (Stage 1)

**If `clinical_count` == 0:**
- The topic is **NOT FEASIBLE** due to lack of primary studies.
- Output: "⚠️ Sorry, no relevant clinical studies found for this title. This topic is likely not feasible."
- **STOP**.

**If `clinical_count` > 0:**
- Proceed to Step 6.

### 6. Search Meta-Analyses

Search for existing Meta-analyses via the PubMed API using the same query.

```bash
python scripts/feasibility_ops.py search --query "{{search_query}}" --type meta
```

Store the result JSON as `{{meta_json}}`.

### 7. Process Meta Results

Format the meta-analysis results.

```bash
python scripts/feasibility_ops.py meta --json '{{meta_json}}'
```

Parse the output JSON to get:
- `meta_summary`: Formatted summary string.

### 8. Final Feasibility Analysis

Analyze the results to determine final feasibility.

**Prompt for LLM:**
```text
Role: Clinical Research Expert
Task: Assess Meta-analysis feasibility.

Input:
Title: "{{input_the_title}}"
Existing Meta-Analyses:
{{meta_summary}}

Existing Clinical Trials:
{{clinical_summary}}

Logic:
1. If NO existing Meta-analyses + YES Clinical Trials -> ✅ FEASIBLE.
2. If YES existing Meta-analyses:
   - Check the dates. Are there new Clinical Trials published AFTER the latest Meta-analysis?
   - If YES new trials -> ✅ FEASIBLE (Update is possible).
   - If NO new trials -> ⚠️ NOT FEASIBLE (Already covered).

Output Format:
"{{input_the_title}}"
[Conclusion: ✅ Feasible / ⚠️ Not Feasible]
Reason: [Explain based on the logic above]
```

### 9. Output

Present the final analysis to the user.
