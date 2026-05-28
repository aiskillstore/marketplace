---
name: target-novelty-scorer
description: Score the novelty of biological targets through literature mining and.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Target Novelty Scorer

ID: 177

## When to Use

- Use this skill when the task needs Score the novelty of biological targets through literature mining and.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Score the novelty of biological targets through literature mining and.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.9+
- requests
- pandas
- biopython (Entrez API)
- numpy

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/target-novelty-scorer"
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

Score the novelty of biological targets based on literature mining. By analyzing literature in academic databases such as PubMed and PubMed Central, assess the research popularity, uniqueness, and innovation potential of target molecules in the research field.

## Features

- 🔬 **Literature Retrieval**: Automatically retrieve literature related to targets from PubMed and other databases
- 📊 **Novelty Scoring**: Calculate target novelty score based on multi-dimensional indicators (0-100)
- 📈 **Trend Analysis**: Analyze temporal trends in target research
- 🧬 **Cross-validation**: Verify current research status of targets by combining multiple databases
- 📝 **Report Generation**: Generate detailed novelty analysis reports

## Scoring Criteria

1. **Research Heat (0-25 points)**: Number of related publications and citations in recent years
2. **Uniqueness (0-25 points)**: Distinction from known popular targets
3. **Research Depth (0-20 points)**: Progress of preclinical/clinical research
4. **Collaboration Network (0-15 points)**: Diversity of research institutions/teams
5. **Temporal Trend (0-15 points)**: Research growth trends in recent years

## Usage

### Basic Usage

```text
cd /Users/z04030865/.openclaw/workspace/skills/target-novelty-scorer
python scripts/main.py --target "PD-L1"
```

### Advanced Options

```text
python scripts/main.py \
  --target "BRCA1" \
  --db pubmed \
  --years 10 \
  --output report.json \
  --format json
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--target` | string | required | Target molecule name or gene symbol |
| `--db` | string | pubmed | Data source (pubmed, pmc, all) |
| `--years` | int | 5 | Analysis year range |
| `--output` | string | stdout | Output file path |
| `--format` | string | text | Output format (text, json, csv) |
| `--verbose` | flag | false | Verbose output |

## Output Format

### JSON Output

```json
{
  "target": "PD-L1",
  "novelty_score": 72.5,
  "confidence": 0.85,
  "breakdown": {
    "research_heat": 18.5,
    "uniqueness": 20.0,
    "research_depth": 15.2,
    "collaboration": 12.0,
    "trend": 6.8
  },
  "metadata": {
    "total_papers": 15234,
    "recent_papers": 3421,
    "clinical_trials": 89,
    "analysis_date": "2026-02-06"
  },
  "interpretation": "This target has moderate novelty, with moderate research heat in recent years..."
}
```

## API Requirements

- NCBI API Key (for PubMed retrieval)
- Optional: Europe PMC API

## Installation

```text
pip install -r requirements.txt
```

## License

MIT License - Part of OpenClaw Bioinformatics Skills Collection

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

This skill accepts requests that match the documented purpose of `target-novelty-scorer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `target-novelty-scorer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
