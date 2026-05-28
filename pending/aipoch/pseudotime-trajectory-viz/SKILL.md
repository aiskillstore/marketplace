---
name: pseudotime-trajectory-viz
description: Analyze data with `pseudotime-trajectory-viz` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Pseudotime Trajectory Visualization

Visualize single-cell developmental trajectories showing cellular differentiation processes using pseudotime analysis.

## When to Use

- Use this skill when the task needs Visualize single-cell developmental trajectories showing cellular differentiation processes using pseudotime analysis.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Analyze data with `pseudotime-trajectory-viz` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.9+
- `scanpy>=1.9.0` - Single-cell analysis framework
- `scvelo>=0.2.5` - RNA velocity analysis
- `palantir` - Trajectory inference and pseudotime
- `scikit-learn` - Dimensionality reduction and clustering
- `matplotlib>=3.5.0` - Plotting
- `seaborn` - Statistical visualization
- `pandas`, `numpy` - Data manipulation
- `anndata` - Single-cell data structure

Optional:
- `slingshot` (R) via `rpy2` - Alternative trajectory method

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/pseudotime-trajectory-viz"
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan." --format json
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Function

- Infer developmental trajectories from single-cell RNA-seq data
- Calculate pseudotime values representing cellular differentiation progress
- Visualize trajectory trees and lineage branching
- Overlay gene expression dynamics along pseudotime
- Identify lineage-specific marker genes
- Generate publication-ready trajectory plots

## Technical Difficulty

**High** - Requires understanding of single-cell analysis, dimensionality reduction, trajectory inference algorithms, and Python visualization libraries.

## Usage

```text

# Basic trajectory analysis from AnnData file
python scripts/main.py --input data.h5ad --output ./results

# Specify starting cells and lineage inference method
python scripts/main.py --input data.h5ad --start-cell stem_cell_cluster --method diffusion --output ./results

# Visualize specific gene expression along trajectories
python scripts/main.py --input data.h5ad --genes SOX2,OCT4,NANOG --plot-genes --output ./results

# Full analysis with custom parameters
python scripts/main.py --input data.h5ad \
    --embedding umap \
    --method slingshot \
    --start-cell-type progenitor \
    --n-lineages 3 \
    --genes MARKER1,MARKER2,MARKER3 \
    --output ./results \
    --format pdf
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` | path | required | Input AnnData (.h5ad) file path |
| `--output` | path | ./trajectory_output | Output directory for results |
| `--embedding` | enum | umap | Embedding for visualization: `umap`, `tsne`, `pca`, `diffmap` |
| `--method` | enum | diffusion | Trajectory inference: `diffusion`, `slingshot`, `paga`, `palantir` |
| `--start-cell` | string | auto | Root cell ID or cluster name for trajectory origin |
| `--start-cell-type` | string | - | Cell type annotation to use as starting point |
| `--n-lineages` | int | auto | Number of expected lineage branches |
| `--cluster-key` | string | leiden | AnnData obs key for cell clusters |
| `--cell-type-key` | string | cell_type | AnnData obs key for cell type annotations |
| `--genes` | string | - | Comma-separated gene names to plot along pseudotime |
| `--plot-genes` | flag | false | Generate gene expression heatmaps along trajectories |
| `--plot-branch` | flag | true | Show lineage branch probabilities |
| `--format` | enum | png | Output format: `png`, `pdf`, `svg` |
| `--dpi` | int | 300 | Figure resolution |
| `--n-pcs` | int | 30 | Number of principal components for analysis |
| `--n-neighbors` | int | 15 | Number of neighbors for graph construction |
| `--diffmap-components` | int | 5 | Number of diffusion components to compute |

## Input Format

Required AnnData (.h5ad) structure:
```
AnnData object with n_obs × n_vars = n_cells × n_genes
    obs: 'leiden', 'cell_type'  # Cluster and cell type annotations
    var: 'highly_variable'       # Highly variable gene marker
    obsm: 'X_umap', 'X_pca'      # Pre-computed embeddings (optional)
    layers: 'spliced', 'unspliced'  # For RNA velocity (optional)
```

## Output Files

```
output_directory/
├── trajectory_plot.{format}          # Main trajectory visualization
├── pseudotime_distribution.{format}  # Pseudotime value distribution
├── lineage_tree.{format}             # Branching lineage structure
├── gene_expression_heatmap.{format}  # Gene dynamics heatmap (if --plot-genes)
├── gene_trends/
│   ├── {gene_name}_trend.{format}    # Individual gene expression trends
│   └── ...
├── pseudotime_values.csv             # Cell-level pseudotime values
├── lineage_assignments.csv           # Cell lineage assignments
└── analysis_report.json              # Analysis parameters and statistics
```

## Output Format Example

### analysis_report.json
```json
{
  "analysis_date": "2026-02-06T06:00:00",
  "method": "diffusion",
  "n_cells": 5000,
  "n_lineages": 3,
  "root_cell": "cell_1234",
  "pseudotime_range": [0.0, 1.0],
  "lineages": {
    "lineage_1": {
      "cell_count": 1500,
      "terminal_state": "mature_type_A",
      "mean_pseudotime": 0.75
    },
    "lineage_2": {
      "cell_count": 1200,
      "terminal_state": "mature_type_B",
      "mean_pseudotime": 0.68
    }
  }
}
```

### pseudotime_values.csv
```csv
cell_id,cluster,cell_type,pseudotime,lineage,branch_probability
cell_001,0,progenitor,0.05,lineage_1,0.95
cell_002,1,intermediate,0.42,lineage_1,0.88
...
```

## Implementation Notes

1. **Preprocessing**: Assumes input data is already normalized and log-transformed
2. **Root Detection**: If start cell not specified, uses cell cycle or marker gene expression to infer progenitors
3. **Diffusion Pseudotime**: Default method using diffusion maps for robust trajectory inference
4. **Palantir**: Used for soft lineage assignments and fate probability estimation
5. **Memory**: Large datasets (>50k cells) may require 16GB+ RAM

## Methods

### Diffusion Pseudotime (DPT)
- Uses diffusion maps to capture non-linear cell relationships
- Robust to noise and dataset size
- Good for complex branching trajectories

### Slingshot
- Principal curve-based approach
- Simultaneous inference of multiple lineages
- Requires R installation with rpy2 bridge

### PAGA (Partition-based Graph Abstraction)
- Connects clusters based on transcriptome similarity
- Provides coarse-grained trajectory overview
- Fast and scalable

### Palantir
- Diffusion-based fate probability estimation
- Soft lineage assignments
- Best for fate bias analysis

## Limitations

- Requires high-quality single-cell data with good cell type coverage
- Assumes differentiation is the main source of variation
- May not capture rare transitional states with few cells
- Circular or cyclic processes not well represented by linear pseudotime
- RNA velocity requires spliced/unspliced counts in AnnData layers

## Safety & Best Practices

- **Validate trajectories** with known marker genes and biological knowledge
- **Multiple methods** recommended for critical analyses
- **Batch effects** should be corrected before trajectory inference
- **Cell cycle** effects may confound differentiation trajectories
- **Do not overinterpret** precise pseudotime values as absolute time

## Example Workflow

```python

# Preprocess data with scanpy (before using this tool)
import scanpy as sc

adata = sc.read_h5ad('raw_data.h5ad')
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata)
sc.tl.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)
adata.write('data.h5ad')

# Then run this skill

# python scripts/main.py --input data.h5ad --start-cell-type progenitor
```

## References

- Haghverdi et al. (2016) - Diffusion pseudotime
- Street et al. (2018) - Slingshot
- Wolf et al. (2019) - PAGA
- Setty et al. (2019) - Palantir
- La Manno et al. (2018) - RNA velocity

## Version

- Created: 2026-02-06
- Status: Functional
- Version: 1.0.0

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

This skill accepts requests that match the documented purpose of `pseudotime-trajectory-viz` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `pseudotime-trajectory-viz` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
