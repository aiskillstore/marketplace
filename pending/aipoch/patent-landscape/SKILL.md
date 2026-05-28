---
name: patent-landscape
description: Use when analyzing biotech patent landscapes, identifying white spaces in pharmaceutical IP, tracking competitor patents, or assessing freedom to operate for drug development. Provides comprehensive patent analysis and strategic insights for life sciences innovation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Biotech Patent Landscape Analyzer

Analyze biotech and pharmaceutical patent landscapes to identify opportunities, assess competition, and guide R&D strategy.

## When to Use

- Use this skill when the task needs Use when analyzing biotech patent landscapes, identifying white spaces in pharmaceutical IP, tracking competitor patents, or assessing freedom to operate for drug development. Provides comprehensive patent analysis and strategic insights for life sciences innovation.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when analyzing biotech patent landscapes, identifying white spaces in pharmaceutical IP, tracking competitor patents, or assessing freedom to operate for drug development. Provides comprehensive patent analysis and strategic insights for life sciences innovation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/patent-landscape"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.patent_landscape import PatentLandscapeAnalyzer

analyzer = PatentLandscapeAnalyzer()

# Analyze therapeutic area
landscape = analyzer.analyze(
    therapeutic_area="CAR-T cell therapy",
    date_range="2020-2024",
    assignees=["Novartis", "Kite Pharma", "Juno Therapeutics"]
)
```

## Core Capabilities

### 1. Patent Search & Analysis

```python
results = analyzer.search_patents(
    keywords=["CRISPR", "gene editing", "therapeutic"],
    classification="C12N15/113",  # IPC class
    jurisdictions=["US", "EP", "WO"]
)
```

**Search Strategies:**
- **Keyword-based**: Technical terms + synonyms
- **Classification-based**: IPC/CPC codes
- **Citation-based**: Forward/backward citations
- **Assignee-based**: Company portfolios

### 2. White Space Analysis

```python
opportunities = analyzer.identify_white_spaces(
    technology="Antibody-drug conjugates",
    target_diseases=["breast cancer", "lung cancer"],
    existing_claims=landscape
)
```

**White Space Opportunities:**
- Underserved disease indications
- Novel combination therapies
- Alternative delivery mechanisms
- Geographical gaps (emerging markets)

### 3. Competitor Intelligence

```python
competitors = analyzer.analyze_competitors(
    companies=["Pfizer", "Moderna", "BioNTech"],
    focus_area="mRNA vaccines"
)
```

**Competitor Metrics:**
| Metric | Description |
|--------|-------------|
| Portfolio size | Total active patents |
| Filing velocity | Recent filing trends |
| Geographic coverage | Jurisdiction strategy |
| Technology focus | Core vs. peripheral areas |
| Partnership patterns | Collaboration trends |

### 4. Freedom to Operate (FTO) Assessment

```python
fto = analyzer.assess_fto(
    product_concept="Bispecific antibody targeting PD-1 and CTLA-4",
    jurisdictions=["US", "EU", "Japan"]
)
```

**FTO Analysis Steps:**
1. Identify relevant patent claims
2. Map claims to product features
3. Assess validity of blocking patents
4. Design around options
5. Licensing recommendations

## CLI Usage

```text

# Generate patent landscape report
python scripts/patent_landscape.py \
  --query "immuno-oncology checkpoint inhibitors" \
  --output landscape_report.pdf \
  --format comprehensive

# Quick FTO check
python scripts/patent_landscape.py \
  --fto "product_description.txt" \
  --jurisdictions US EP JP
```

## Data Sources

- USPTO (United States)
- EPO (Europe)
- WIPO (Global)
- JPO (Japan)
- CNIPA (China)

## References

- `references/ipc-classifications.md` - IPC/CPC codes for biotech
- `references/patent-search-strategies.md` - Advanced search techniques
- `examples/landscape-reports/` - Sample reports

---

**Skill ID**: 204 | **Version**: 1.0 | **License**: MIT

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `patent-landscape` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `patent-landscape` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
