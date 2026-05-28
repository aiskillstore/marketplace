---
name: volcano-plot-script
description: Generate R/Python code for volcano plots from DEG (Differentially Expressed Genes) analysis results. Triggered when user needs visualization of gene expression data, p-value vs fold-change scatter plots, publication-ready figures for bioinformatics analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Volcano Plot Script Generator

A skill for generating publication-ready volcano plots from differential gene expression analysis results.

## When to Use

- Use this skill when the task is to Generate R/Python code for volcano plots from DEG (Differentially Expressed Genes) analysis results. Triggered when user needs visualization of gene expression data, p-value vs fold-change scatter plots, publication-ready figures for bioinformatics analysis.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate R/Python code for volcano plots from DEG (Differentially Expressed Genes) analysis results. Triggered when user needs visualization of gene expression data, p-value vs fold-change scatter plots, publication-ready figures for bioinformatics analysis.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/example_volcano.R`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/volcano-plot-script"
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
- Packaged assets: reusable files are available under `assets/`.
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

Volcano plots visualize the relationship between statistical significance (p-values) and magnitude of change (fold changes) in gene expression data. This skill generates customizable R or Python scripts for creating high-quality figures suitable for publications.

## Use Cases

- Visualize RNA-seq DEG analysis results
- Identify significantly upregulated and downregulated genes
- Highlight genes of interest (markers, pathways)
- Generate publication-quality figures for manuscripts
- Compare multiple experimental conditions

## Input Requirements

Required input data format:
- Gene identifier (gene symbol or ENSEMBL ID)
- Log2 fold change values
- Adjusted or raw p-values
- Optional: gene annotations, pathways

## Output

- Publication-ready volcano plot (PNG/PDF/SVG)
- Customizable R or Python script
- Optional: labeled significant gene lists

## Usage

```python

# Example: Run the volcano plot generator
python scripts/main.py --input deg_results.csv --output volcano_plot.png
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input` | Path to DEG results CSV/TSV | required |
| `--output` | Output plot file path | volcano_plot.png |
| `--log2fc-col` | Column name for log2 fold change | log2FoldChange |
| `--pvalue-col` | Column name for p-value | padj |
| `--gene-col` | Column name for gene IDs | gene |
| `--log2fc-thresh` | Log2 FC threshold for significance | 1.0 |
| `--pvalue-thresh` | P-value threshold | 0.05 |
| `--label-genes` | File with genes to label | None |
| `--top-n` | Label top N significant genes | 10 |
| `--color-up` | Color for upregulated genes | #E74C3C |
| `--color-down` | Color for downregulated genes | #3498DB |
| `--color-ns` | Color for non-significant genes | #95A5A6 |

## Technical Difficulty

**Medium** - Requires understanding of:
- DEG analysis concepts (fold change, p-values, FDR)
- Data visualization principles
- Matplotlib/ggplot2 plotting libraries

### Python
- pandas
- matplotlib
- seaborn
- numpy

### R
- ggplot2
- dplyr
- ggrepel (for label positioning)

## References

- [Example datasets and templates](references/)
- Best practices for volcano plot visualization
- Color schemes for accessibility

## Author

Auto-generated skill for bioinformatics visualization.

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output plots | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited (pandas, matplotlib, seaborn, numpy)

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt

# R dependencies (if using R)
install.packages(c("ggplot2", "dplyr", "ggrepel"))
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully generates executable Python/R script
- [ ] Output plot is publication-ready quality
- [ ] Correctly identifies significant genes based on thresholds
- [ ] Handles missing or malformed data gracefully
- [ ] Color scheme is accessible (colorblind-friendly)

### Test Cases
1. **Basic DEG Visualization**: Input standard DESeq2 results → Valid volcano plot
2. **Custom Thresholds**: Adjust log2FC and p-value thresholds → Correct gene classification
3. **Gene Labeling**: Specify genes to label → Labels appear correctly
4. **Large Dataset**: Input 20,000+ genes → Performance remains acceptable
5. **Malformed Data**: Input with missing values → Graceful error handling

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Add interactive plot option (Plotly)
  - Support for multiple comparison groups
  - Integration with pathway enrichment tools

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

This skill accepts requests that match the documented purpose of `volcano-plot-script` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `volcano-plot-script` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
