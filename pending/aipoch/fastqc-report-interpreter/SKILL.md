---
name: fastqc-report-interpreter
description: Use when analyzing FASTQC quality reports from sequencing data, identifying quality issues in NGS datasets, or troubleshooting sequencing problems. Interprets quality metrics and provides actionable recommendations for RNA-seq, DNA-seq, and ChIP-seq data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# FASTQC Report Interpreter

Analyze FASTQC quality control reports for Next-Generation Sequencing (NGS) data to assess data quality and identify issues.

## When to Use

- Use this skill when the task needs Use when analyzing FASTQC quality reports from sequencing data, identifying quality issues in NGS datasets, or troubleshooting sequencing problems. Interprets quality metrics and provides actionable recommendations for RNA-seq, DNA-seq, and ChIP-seq data.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when analyzing FASTQC quality reports from sequencing data, identifying quality issues in NGS datasets, or troubleshooting sequencing problems. Interprets quality metrics and provides actionable recommendations for RNA-seq, DNA-seq, and ChIP-seq data.
- Packaged executable path(s): `scripts/main.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Data Analytics/fastqc-report-interpreter"
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
from scripts.fastqc_interpreter import FASTQCInterpreter

interpreter = FASTQCInterpreter()

# Analyze report
analysis = interpreter.analyze("sample_fastqc.html")
print(f"Overall Quality: {analysis.quality_status}")
print(f"Issues Found: {analysis.issues}")
```

## Core Capabilities

### 1. Quality Metrics Analysis

```python
metrics = interpreter.parse_metrics("fastqc_data.txt")
```

**Key Metrics:**
| Metric | Good | Warning | Fail |
|--------|------|---------|------|
| Per base sequence quality | Q > 28 | Q 20-28 | Q < 20 |
| Per sequence quality scores | Peak at Q30 | Peak Q20-30 | Peak < Q20 |
| Per base N content | < 5% | 5-20% | > 20% |
| Sequence duplication | < 20% | 20-50% | > 50% |
| Adapter content | < 5% | 5-10% | > 10% |

### 2. Issue Diagnosis

```python
issues = interpreter.diagnose_issues(metrics)
for issue in issues:
    print(f"{issue.severity}: {issue.description}")
    print(f"Recommendation: {issue.recommendation}")
```

**Common Issues:**

**Low Quality at Read Ends**
- **Cause**: Phasing effects, reagent depletion
- **Solution**: Trim last 10-20 bases

**Adapter Contamination**
- **Cause**: Incomplete adapter removal
- **Solution**: Re-run cutadapt/Trimmomatic with stricter parameters

**High Duplication**
- **Cause**: PCR over-amplification, low input
- **Solution**: Use deduplication; consider library prep optimization

**Per Base Sequence Content Bias**
- **Cause**: Adapter dimers, non-random priming
- **Solution**: Check for adapter contamination; randomize primers

### 3. Batch Analysis

```python
batch_results = interpreter.analyze_batch(
    fastqc_files=["sample1_fastqc.html", "sample2_fastqc.html", ...],
    output_summary="batch_summary.csv"
)
```

### 4. Recommendation Generation

```python
recommendations = interpreter.get_recommendations(
    analysis,
    application="rna_seq",  # or "dna_seq", "chip_seq"
    quality_threshold="high"
)
```

**Application-Specific Thresholds:**
- **RNA-seq**: Acceptable duplication up to 40% (transcript abundance)
- **DNA-seq**: Strict quality requirements (variant calling)
- **ChIP-seq**: Moderate quality, focus on enrichment metrics

## CLI Usage

```text

# Analyze single report
python scripts/fastqc_interpreter.py --input sample_fastqc.html

# Batch analysis
python scripts/fastqc_interpreter.py --batch "*fastqc.html" --output report.pdf

# With custom thresholds
python scripts/fastqc_interpreter.py --input fastqc.html --application rna_seq
```

## Output Interpretation

**PASS (Green)**: Proceed with analysis
**WARNING (Yellow)**: Review but likely acceptable
**FAIL (Red)**: Requires action before downstream analysis

## Troubleshooting Guide

See `references/troubleshooting.md` for:
- Platform-specific issues (Illumina, PacBio, Oxford Nanopore)
- Library prep problem diagnosis
- Downstream analysis impact assessment

---

**Skill ID**: 205 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `fastqc-report-interpreter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `fastqc-report-interpreter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
