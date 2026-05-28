---
name: systematic-review-screener
description: Automated abstract screening tool for systematic literature reviews with PRISMA workflow support.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Systematic Review Screener

Automated abstract screening tool for systematic literature reviews with PRISMA workflow support.

## When to Use

- Use this skill when the task needs Automated abstract screening tool for systematic literature reviews with PRISMA workflow support.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Automated abstract screening tool for systematic literature reviews with PRISMA workflow support.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `yaml`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/systematic-review-screener"
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
python scripts/main.py -h
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

This skill screens academic abstracts against predefined inclusion/exclusion criteria, generating PRISMA-compliant outputs with decision rationale and confidence scores.

**Technical Difficulty: High** ⚠️ Manual verification recommended for final inclusion decisions.

## Features

- **Multi-format Input**: PubMed MEDLINE, EndNote XML, CSV/TSV
- **Criteria Matching**: Configurable inclusion/exclusion rules
- **Confidence Scoring**: 0-100% confidence for each decision
- **Conflict Detection**: Flags abstracts requiring human review
- **PRISMA Export**: Flow diagram data and screening log
- **Batch Processing**: Handles large reference sets efficiently

## Usage

### Basic Screening

```python

# Run with default settings
python scripts/main.py --input references.csv --criteria criteria.yaml
```

### With PRISMA Export

```python
python scripts/main.py --input references.xml --criteria criteria.yaml \
  --output results/ --prisma --format excel
```

### Confidence Threshold

```python
python scripts/main.py --input refs.txt --criteria criteria.yaml \
  --threshold 0.8 --conflict-only
```

## Input Formats

### 1. CSV/TSV
Required columns: `title`, `abstract` (optional: `authors`, `year`, `doi`, `pmid`)

```csv
title,abstract,authors,year
title,abstract,authors,year
```

### 2. PubMed MEDLINE
Standard .txt export from PubMed search.

### 3. EndNote XML
Export from EndNote with abstracts included.

## Criteria File (YAML)

See `references/criteria_template.yaml` for complete example:

```yaml
study_type:
  include:
    - "randomized controlled trial"
    - "systematic review"
  exclude:
    - "case report"
    - "letter"
    - "editorial"

population:
  include_keywords:
    - "adults"
    - "elderly"
  exclude_keywords:
    - "pediatric"
    - "children"

intervention:
  required:
    - "drug therapy"
    - "medication"

language:
  allowed: ["English"]
  
year_range:
  min: 2010
  max: 2024

confidence_threshold: 0.75
```

## Output Files

| File | Description |
|------|-------------|
| `screened_included.csv` | Records passing all criteria |
| `screened_excluded.csv` | Records failing one or more criteria |
| `conflicts.csv` | Low-confidence decisions requiring review |
| `prisma_data.json` | PRISMA flow diagram counts |
| `screening_log.json` | Full decision trail with rationale |

## PRISMA Workflow Support

Generates structured data for PRISMA 2020 flow diagram:

```json
{
  "identification": {
    "database_results": 1250,
    "register_results": 45,
    "other_sources": 12
  },
  "screening": {
    "records_screened": 1307,
    "records_excluded": 1150,
    "full_text_assessed": 157,
    "full_text_excluded": 89
  },
  "included": {
    "qualitative_synthesis": 68,
    "quantitative_synthesis": 42
  }
}
```

## Configuration

### Environment Variables
```text
export SCREENING_THRESHOLD=0.75  # Default confidence threshold
export BATCH_SIZE=100             # Records per batch
export MAX_WORKERS=4              # Parallel processing workers
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input file path | Required |
| `--criteria` | Criteria YAML path | Required |
| `--output` | Output directory | `./output` |
| `--format` | Output format: csv/excel/json | csv |
| `--threshold` | Confidence threshold | 0.75 |
| `--prisma` | Generate PRISMA data | False |
| `--conflict-only` | Export only conflicts | False |
| `--batch-size` | Processing batch size | 100 |

## Decision Algorithm

1. **Keyword Matching**: Exact and fuzzy keyword matching against title/abstract
2. **Inclusion Scoring**: Points for each inclusion criterion matched
3. **Exclusion Check**: Immediate exclusion if exclusion criterion detected
4. **Confidence Calculation**: Weighted score based on keyword presence and clarity
5. **Conflict Flagging**: Records with confidence < threshold flagged for manual review

## Limitations

- **Not for Final Decisions**: Tool provides recommendations; human review required for inclusion
- **Language Dependent**: Optimized for English abstracts
- **Structured Abstracts**: Performs better on structured abstracts (Background/Methods/Results/Conclusion)
- **Domain Specific**: Criteria must be tailored to research question

## References

- `references/criteria_template.yaml` - Complete criteria configuration example
- `references/prisma_2020_checklist.pdf` - PRISMA 2020 reporting guidelines
- `references/sample_references.csv` - Example input format

## Version

Version: 1.0.0  
Last Updated: 2026-02-05  
Classification: Research Tool - Requires Human Verification

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

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

This skill accepts requests that match the documented purpose of `systematic-review-screener` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `systematic-review-screener` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
