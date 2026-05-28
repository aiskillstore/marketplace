---
name: reagent-substitute-scout
description: Find validated alternative reagents based on literature citation data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Skill: Reagent Substitute Scout (ID: 108)

## When to Use

- Use this skill when the task needs Find validated alternative reagents based on literature citation data.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Find validated alternative reagents based on literature citation data.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python >= 3.8
- requests >= 2.25.0
- pandas >= 1.3.0
- rdkit >= 2021.03.1 (chemical structure analysis)
- biopython >= 1.79 (NCBI API)

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/reagent-substitute-scout"
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

## Description

When specific reagents are discontinued or out of stock, find validated alternatives based on literature citation data.

This Skill analyzes reagent usage data from scientific literature to identify alternative reagents that have been repeatedly validated and widely cited, helping researchers quickly find reliable alternatives when the original reagent is unavailable.

## Features

- 🔍 **Reagent Identification**: Parse reagent names, CAS numbers, molecular formulas, and other multi-dimensional information
- 📚 **Literature Analysis**: Based on citation data from PubMed, Google Scholar, and other databases
- ✅ **Validation Scoring**: Calculate usage frequency, success rate, and reliability scores for alternatives
- 🔄 **Similarity Matching**: Find similar reagents based on chemical structure and functional characteristics
- 📊 **Report Generation**: Output structured alternative solution reports

## Usage

### Basic Usage

```text

# Query alternatives for a specific reagent
python skills/reagent-substitute-scout/scripts/main.py --reagent "TRIzol Reagent"

# Query by CAS number
python skills/reagent-substitute-scout/scripts/main.py --cas "15596-18-2"

# Query by molecular formula
python skills/reagent-substitute-scout/scripts/main.py --formula "C17H34N2O6P"
```

### Advanced Options

```text

# Specify output format
python skills/reagent-substitute-scout/scripts/main.py --reagent "TRIzol" --format json

# Limit result count
python skills/reagent-substitute-scout/scripts/main.py --reagent "TRIzol" --limit 10

# Specify application field filter
python skills/reagent-substitute-scout/scripts/main.py --reagent "TRIzol" --field "RNA extraction"

# Include detailed literature citations
python skills/reagent-substitute-scout/scripts/main.py --reagent "TRIzol" --verbose
```

## Configuration

Configuration file path: `~/.config/reagent-substitute-scout/config.json`

```json
{
  "data_sources": {
    "pubmed": {
      "enabled": true,
      "api_key": "your_ncbi_api_key"
    },
    "google_scholar": {
      "enabled": true,
      "api_key": "your_scholar_api_key"
    },
    "chembl": {
      "enabled": true
    },
    "pubchem": {
      "enabled": true
    }
  },
  "scoring": {
    "citation_weight": 0.4,
    "recency_weight": 0.3,
    "similarity_weight": 0.3,
    "min_citations": 5
  },
  "output": {
    "default_format": "table",
    "default_limit": 5
  }
}
```

## Output Format

### Table Format (Default)

```
┌────────────────────────┬─────────────┬────────────┬──────────────┬─────────────┐
│ Substitute             │ CAS         │ Similarity │ Citation     │ Reliability │
├────────────────────────┼─────────────┼────────────┼──────────────┼─────────────┤
│ QIAzol Lysis Reagent   │ 104888-69-9 │ 0.92       │ 2,341        │ ★★★★★      │
│ TRI Reagent            │ 93249-88-8  │ 0.89       │ 1,876        │ ★★★★★      │
│ RNAzol RT              │ 105697-57-2 │ 0.85       │ 892          │ ★★★★☆      │
└────────────────────────┴─────────────┴────────────┴──────────────┴─────────────┘
```

### JSON Format

```json
{
  "query": {
    "reagent": "TRIzol Reagent",
    "cas": "15596-18-2"
  },
  "results": [
    {
      "name": "QIAzol Lysis Reagent",
      "cas": "104888-69-9",
      "molecular_formula": "C17H34N2O6P",
      "similarity_score": 0.92,
      "citation_count": 2341,
      "reliability_score": 4.8,
      "validated_applications": ["RNA extraction", "tissue homogenization"],
      "literature_evidence": [
        {
          "pmid": "30212345",
          "title": "Comparison of RNA extraction methods",
          "year": 2019,
          "citation_count": 156
        }
      ]
    }
  ]
}
```

## Data Sources

1. **PubMed/NCBI** - Biomedical literature database
2. **Google Scholar** - Academic citation data
3. **ChEMBL** - Bioactivity data
4. **PubChem** - Chemical structure information
5. **Local Cache** - Historical query results and offline data

## Scoring Algorithm

Alternative scoring is based on the following dimensions:

```
Total Score = Citation Score × 0.4 + Recency Score × 0.3 + Similarity Score × 0.3

Where:
- Citation Score = log(citation count of this alternative) / log(max citation count)
- Recency Score = Proportion of citations in the last 5 years
- Similarity Score = Chemical structure similarity + functional characteristic match
```

## Installation

```text

# Install dependencies
pip install -r skills/reagent-substitute-scout/requirements.txt

# Configure API keys
cp skills/reagent-substitute-scout/config.example.json ~/.config/reagent-substitute-scout/config.json

# Edit configuration file and fill in API keys
```

## Limitations

- Literature data completeness depends on database API availability
- Chemical structure similarity calculation requires RDKit support
- Some specialized reagents may lack sufficient public literature data
- It is recommended to combine with actual laboratory conditions to verify alternatives

## Version History

- v1.0.0 (2025-02-06) - Initial version, supports basic query and scoring functions

## Author

OpenClaw Skill Development

## License

MIT

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

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

This skill accepts requests that match the documented purpose of `reagent-substitute-scout` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `reagent-substitute-scout` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
