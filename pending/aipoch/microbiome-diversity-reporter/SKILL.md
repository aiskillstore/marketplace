---
name: microbiome-diversity-reporter
description: Interpret Alpha and Beta diversity metrics from 16S rRNA sequencing results.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Microbiome Diversity Reporter

---

## When to Use

- Use this skill when the task needs Interpret Alpha and Beta diversity metrics from 16S rRNA sequencing results.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Interpret Alpha and Beta diversity metrics from 16S rRNA sequencing results.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- numpy
- pandas
- scipy
- scikit-bio
- matplotlib
- seaborn
- plotly (for interactive charts)

---

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/microbiome-diversity-reporter"
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
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

This tool is used to analyze and interpret diversity metrics in microbiome 16S rRNA sequencing data, including:

- **Alpha Diversity**: Species diversity within a single sample
- **Beta Diversity**: Species composition differences between samples

---

## Usage

### Command Line

```text

# Analyze Alpha diversity for a single sample
python scripts/main.py --input otu_table.tsv --metric shannon --output alpha_report.html

# Analyze Beta diversity (PCoA)
python scripts/main.py --input otu_table.tsv --beta --metadata metadata.tsv --output beta_report.html

# Generate full report (Alpha + Beta)
python scripts/main.py --input otu_table.tsv --full --metadata metadata.tsv --output diversity_report.html
```

### Parameter Description

| Parameter | Description | Required |
|------|------|------|
| `--input` | OTU/ASV table path (TSV format) | Yes |
| `--metadata` | Sample metadata (TSV format) | Required for Beta diversity |
| `--metric` | Alpha diversity metric: shannon, simpson, chao1, observed_otus | No (default: shannon) |
| `--alpha` | Calculate Alpha diversity only | No |
| `--beta` | Calculate Beta diversity only | No |
| `--full` | Generate full report (Alpha + Beta) | No |
| `--output` | Output report path | No (default: stdout) |
| `--format` | Output format: html, json, markdown | No (default: html) |

---

## Input Format

### OTU Table (TSV)
```
#OTU ID	Sample1	Sample2	Sample3
OTU_1	100	50	200
OTU_2	50	100	0
OTU_3	25	25	50
```

### Metadata (TSV)
```
SampleID	Group	Age	Gender
Sample1	Control	25	M
Sample2	Treatment	30	F
Sample3	Treatment	28	M
```

---

## Output

Generates HTML/JSON/Markdown reports containing:

1. **Alpha Diversity Results**
   - Diversity index values
   - Rarefaction curves
   - Box plots (by group)

2. **Beta Diversity Results**
   - PCoA scatter plots
   - NMDS plots
   - Distance matrix heatmaps
   - PERMANOVA statistical tests

3. **Statistical Summary**
   - Sample information statistics
   - Species richness
   - Diversity index distribution

---

## Example Output

```json
{
  "alpha_diversity": {
    "shannon": {
      "Sample1": 2.45,
      "Sample2": 1.89,
      "Sample3": 2.12
    },
    "statistics": {
      "mean": 2.15,
      "std": 0.28
    }
  },
  "beta_diversity": {
    "method": "braycurtis",
    "pcoa": {
      "variance_explained": [0.45, 0.25, 0.15]
    }
  }
}
```

---

## References

1. Shannon, C.E. (1948) A mathematical theory of communication
2. Simpson, E.H. (1949) Measurement of diversity
3. Chao, A. (1984) Non-parametric estimation of classes
4. Lozupone et al. (2005) UniFrac: a phylogenetic metric

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

This skill accepts requests that match the documented purpose of `microbiome-diversity-reporter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `microbiome-diversity-reporter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
