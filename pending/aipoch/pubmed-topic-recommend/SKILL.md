---
name: pubmed-topic-recommend
description: Generate ~5 actionable research topic recommendations by querying PubMed E-utilities; use when a user provides a research direction/constraints and needs evidence-backed topic ideas quickly.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a broad research direction (e.g., "immunotherapy biomarkers") and need **5 concrete, literature-grounded topic options** to choose from.
- You need **research direction suggestions** after a quick PubMed scan, with each suggestion tied to recent papers.
- You want **topic selection based on PubMed literature** under constraints (time range, publication type, population, method preference).
- You must propose **actionable topics with a clear gap/opportunity statement**, supported by at least 1-2 cited articles.
- You need to iteratively refine a PubMed query (keywords/MeSH, inclusion/exclusion terms) until results are sufficient for topic generation.

## Key Features

- Uses the **official PubMed E-utilities** interface for literature retrieval.
- Builds PubMed queries with:
  - keyword groups (`OR`) and exclusions (`NOT`)
  - field restrictions (e.g., Title/Abstract) and/or MeSH terms
  - date bounds via `mindate` / `maxdate`
  - optional publication-type constraints (e.g., review, meta-analysis, clinical trial)
- Produces **JSON output** containing:
  - the final search query
  - retrieved literature metadata
  - ~5 topic recommendations, each with a title, justification, and supporting citations
- Encourages evidence-consistent topic generation:
  - avoids drifting beyond retrieved themes
  - reduces redundancy across topics
  - includes a one-sentence "gap/opportunity" per topic

## Dependencies

- Python 3.10+ (recommended)
- PubMed E-utilities (NCBI) HTTP API (no local installation required)

## Example Usage

1) Configure parameters at the top of:

- `scripts/run_topic_recommendation.py`

Typical configuration items to set (names may vary by implementation):

- keywords / MeSH terms (prefer English)
- exclusion terms
- time range (`mindate`, `maxdate`)
- publication types (optional)
- desired number of topics (default: ~5)

2) Run:

```bash
python scripts/run_topic_recommendation.py
```

3) Output:

- A JSON file or JSON printed to stdout (implementation-dependent), containing:
  - `query`: the PubMed query string used
  - `papers`: a list of retrieved records (titles/years/etc.)
  - `topics`: ~5 topic suggestions with justification and supporting literature (at least 1-2 cited titles/years each)

## Implementation Details

- **Input collection (recommended fields)**
  - Research direction / subject area (prefer English keywords; if provided in Chinese, convert to English keywords or MeSH to reduce retrieval bias)
  - Topic goals/constraints (innovation vs. application, method preference, target population)
  - Inclusion keywords and exclusion terms (support multiple `OR` groups and `NOT` groups)
  - Time range and article types (e.g., review, meta-analysis, clinical trial)
  - Optional journal/subject preferences
  - Output count (default: 5)

- **Query construction**
  - Combine synonyms with `OR`, apply exclusions with `NOT`.
  - Use field tags (e.g., Title/Abstract) and/or MeSH terms to control precision.
  - Use `mindate` / `maxdate` to constrain publication dates.
  - Add publication-type filters when needed.
  - If results are too few: broaden date range, relax field restrictions, or add synonyms.

- **Retrieval**
  - Uses PubMed E-utilities; API and query syntax reference: `references/pubmed_api.md`.

- **Topic generation rules**
  - Topics must align with retrieved literature themes (evidence-consistent).
  - Avoid near-duplicate topics; cover distinct sub-directions or methodological paths.
  - Each topic includes:
    - a clear title
    - a justification grounded in retrieved papers
    - at least 1-2 supporting citations (title + year)
    - a one-sentence "research gap/opportunity" statement

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `pubmed_topic_recommend_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/run_topic_recommendation.py --help
```

Expected output format:

```text
Result file: pubmed_topic_recommend_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Generate ~5 actionable research topic recommendations by querying PubMed E-utilities; use when a user provides a research direction/constraints and needs evidence-backed topic ideas quickly.
