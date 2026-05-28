---
name: translational-gap-analyzer
description: Assess translational gaps between preclinical models and human diseases.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Translational Gap Analyzer

**ID**: 209

## When to Use

- Use this skill when the task needs Assess translational gaps between preclinical models and human diseases.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Assess translational gaps between preclinical models and human diseases.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- Built-in libraries: argparse, json, sys

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/translational-gap-analyzer"
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

Assesses the "translational gap" between basic research models (such as mice, zebrafish, cell lines) and human diseases, providing early warning of clinical translation failure risks. This system helps researchers identify potential translational barriers in preclinical research and improve clinical trial success rates through multi-dimensional analysis.

## Capabilities

- Evaluates anatomical/physiological differences between models and humans
- Analyzes pathological similarity of disease models
- Identifies interspecies differences in molecular pathways
- Evaluates pharmacokinetic differences
- Provides early warning of clinical trial failure risk factors
- Provides improvement recommendations to increase translation success rates

## Usage

```text

# Full assessment report
python scripts/main.py --model <model_type> --disease <disease_name> --full

# Quick risk assessment
python scripts/main.py --model <model_type> --disease <disease_name> --quick

# Compare multiple models
python scripts/main.py --models mouse,rat,primate --disease <disease_name> --compare

# Specify focus areas
python scripts/main.py --model mouse --disease "Alzheimer's" --focus metabolism,immune
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--model` | Model type (mouse, rat, zebrafish, cell_line, organoid, primate) | Yes (unless --models) |
| `--models` | Multi-model comparison mode, comma-separated | No |
| `--disease` | Disease name or MeSH ID | Yes |
| `--focus` | Focus areas, comma-separated (anatomy, physiology, metabolism, immune, genetics, behavior) | No |
| `--full` | Generate full assessment report | No |
| `--quick` | Quick risk assessment mode | No |
| `--compare` | Multi-model comparison mode | No |
| `--output` | Output file path | No |
| `--format` | Output format (json, markdown, table) | No |

## Example Output

```json
{
  "model": "mouse",
  "disease": "Alzheimer's Disease",
  "overall_gap_score": 6.8,
  "risk_level": "HIGH",
  "dimensions": {
    "genetics": {"score": 8.5, "concerns": ["APOE4 differences", "Different tau pathology patterns"]},
    "physiology": {"score": 7.0, "concerns": ["Brain structure differences", "Lifespan differences"]},
    "metabolism": {"score": 6.5, "concerns": ["Significant drug metabolism differences"]},
    "immune": {"score": 5.5, "concerns": ["Microglia functional differences", "Different neuroinflammation patterns"]},
    "behavior": {"score": 6.0, "concerns": ["Limitations in cognitive assessment methods"]}
  },
  "clinical_failure_predictors": [
    "Immune-related mechanism research may not translate",
    "Drug clearance rate differences may lead to inappropriate dosing"
  ],
  "recommendations": [
    "Consider using humanized mouse models",
    "Add non-human primate validation experiments",
    "Focus on peripheral immune and central immune interactions"
  ]
}
```

## Model Types

### Common Models

| Model | Applicable Scenarios | Typical Gaps |
|------|----------|----------|
| mouse | Genetic manipulation, basic research | Immune, metabolism, brain structure |
| rat | Behavioral studies, cardiovascular | Cognition, drug metabolism |
| zebrafish | Development, high-throughput screening | Anatomy, physiology |
| cell_line | Molecular mechanisms | Microenvironment, systemic |
| organoid | Human-specific research | Maturity, vascularization |
| primate | Preclinical validation | Cost, ethics |

## Gap Scoring System

- **0-3**: Low gap, good translation prospects
- **4-6**: Moderate gap, requires additional validation
- **7-8**: High gap, significant translation risks exist
- **9-10**: Extremely high gap, low translation likelihood

## Files

- `SKILL.md` - This file
- `scripts/main.py` - Main analysis script

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

This skill accepts requests that match the documented purpose of `translational-gap-analyzer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `translational-gap-analyzer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
