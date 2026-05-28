---
name: volcano-plot-labeler
description: Analyze data with `volcano-plot-labeler` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Volcano Plot Labeler (ID: 148)

Automatically identify and label the Top 10 most significant genes in volcano plots using a repulsion algorithm to prevent label overlap.

## When to Use

- Use this skill when the task needs Automatically label top significant genes in volcano plots with repulsion.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Analyze data with `volcano-plot-labeler` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `matplotlib`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `pandas`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/volcano-plot-labeler"
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features

- **Smart Gene Selection**: Automatically identifies the top 10 most significant genes based on p-value and fold change
- **Repulsion Algorithm**: Uses force-directed positioning to prevent text label overlap
- **Customizable**: Configurable thresholds, label styling, and positioning options
- **Multiple Output Formats**: PNG, PDF, SVG support

## Installation

```text
pip install pandas matplotlib numpy scipy
```

## Usage

### Basic Usage

```python
from volcano_plot_labeler import label_volcano_plot
import pandas as pd

# Load your data
df = pd.read_csv('differential_expression_results.csv')

# Generate labeled volcano plot
fig = label_volcano_plot(
    df,
    log2fc_col='log2FoldChange',
    pvalue_col='padj',
    gene_col='gene_name',
    top_n=10
)
fig.savefig('volcano_plot_labeled.png', dpi=300, bbox_inches='tight')
```

### Advanced Usage

```python
from volcano_plot_labeler import label_volcano_plot

fig = label_volcano_plot(
    df,
    log2fc_col='log2FoldChange',
    pvalue_col='padj',
    gene_col='gene_name',
    top_n=10,
    pvalue_threshold=0.05,
    log2fc_threshold=1.0,
    figsize=(12, 10),
    repulsion_iterations=100,
    repulsion_force=0.05,
    label_fontsize=10,
    label_color='black',
    arrow_color='gray',
    save_path='output.png'
)
```

### Command Line Usage

```text
python scripts/main.py \
    --input data/deseq2_results.csv \
    --output volcano_labeled.png \
    --log2fc-col log2FoldChange \
    --pvalue-col padj \
    --gene-col gene_name \
    --top-n 10
```

## Input Format

Expected CSV/TSV columns:
- `log2FoldChange`: Log2 fold change values
- `padj` or `pvalue`: Adjusted p-values or raw p-values
- `gene_name`: Gene identifiers

## Algorithm

### Significance Calculation
1. Calculate `-log10(pvalue)` for all genes
2. Rank genes by combined score: `|log2FC| * -log10(pvalue)`
3. Select top N genes with highest significance

### Repulsion Algorithm
1. **Initial Placement**: Place labels at gene coordinates
2. **Force Calculation**: 
   - Repulsive force between overlapping labels
   - Spring force pulling label toward its gene point
   - Boundary forces to keep labels within plot area
3. **Iterative Optimization**: Update positions for N iterations until convergence
4. **Arrow Drawing**: Draw connecting lines from labels to gene points

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | DataFrame | - | Input data |
| `log2fc_col` | str | 'log2FoldChange' | Column name for log2 fold change |
| `pvalue_col` | str | 'padj' | Column name for p-value |
| `gene_col` | str | 'gene_name' | Column name for gene names |
| `top_n` | int | 10 | Number of top genes to label |
| `pvalue_threshold` | float | 0.05 | P-value cutoff for coloring |
| `log2fc_threshold` | float | 1.0 | Log2FC cutoff for coloring |
| `repulsion_iterations` | int | 100 | Iterations for repulsion algorithm |
| `repulsion_force` | float | 0.05 | Strength of repulsion force |
| `label_fontsize` | int | 10 | Font size for labels |
| `figsize` | tuple | (10, 10) | Figure size |

## Output

- Labeled volcano plot with:
  - Color-coded points (up/down/not significant)
  - Top 10 gene labels with leader lines
  - No overlapping text labels

## License

MIT

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

This skill accepts requests that match the documented purpose of `volcano-plot-labeler` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `volcano-plot-labeler` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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

## Inputs to Collect

- Required inputs: the user goal, the primary data or source file, and the requested output format.
- Optional inputs: output directory, formatting preferences, and validation constraints.
- If a required input is unavailable, return a short clarification request before continuing.

## Output Contract

- Return a short summary, the main deliverables, and any assumptions that materially affect interpretation.
- If execution is partial, label what succeeded, what failed, and the next safe recovery step.
- Keep the final answer within the documented scope of the skill.

## Validation and Safety Rules

- Validate identifiers, file paths, and user-provided parameters before execution.
- Do not fabricate results, metrics, citations, or downstream conclusions.
- Use safe fallback behavior when dependencies, credentials, or required inputs are missing.
- Surface any execution failure with a concise diagnosis and recovery path.
