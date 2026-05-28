---
name: heatmap-beautifier
description: Professional beautification tool for gene expression heatmaps, automatically adds clustering trees, color annotation tracks, and intelligently optimizes label layout.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Heatmap Beautifier

ID: 147

Professional beautification tool for gene expression heatmaps, automatically adds clustering trees, color annotation tracks, and intelligently optimizes label layout.

## When to Use

- Use this skill when the task needs Professional beautification tool for gene expression heatmaps, automatically adds clustering trees, color annotation tracks, and intelligently optimizes label layout.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Professional beautification tool for gene expression heatmaps, automatically adds clustering trees, color annotation tracks, and intelligently optimizes label layout.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `matplotlib`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `pandas`: `unspecified`. Declared in `requirements.txt`.
- `seaborn`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/heatmap-beautifier"
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

- **Automatic Clustering**: Automatically adds row/column clustering trees based on hierarchical clustering
- **Annotation Tracks**: Supports multiple color annotation tracks (sample grouping, gene classification, etc.)
- **Smart Labels**: Automatically calculates optimal font size to avoid row/column label overlap
- **Flexible Color Schemes**: Built-in multiple professional scientific research color schemes
- **Export Options**: Supports PDF, PNG, SVG, and other formats

## Dependency Installation

```text
pip install seaborn matplotlib scipy pandas numpy
```

## Usage

### Basic Usage

```python
from skills.heatmap_beautifier.scripts.main import HeatmapBeautifier

# Initialize
hb = HeatmapBeautifier()

# Load data and generate heatmap
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap.pdf"
)
```

### Heatmap with Annotation Tracks

```python
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap_annotated.pdf",
    # Row annotations (gene classification)
    row_annotations={
        "Gene Type": gene_type_dict,  # {"gene1": "Kinase", "gene2": "Transcription Factor", ...}
        "Pathway": pathway_dict
    },
    # Column annotations (sample grouping)
    col_annotations={
        "Condition": condition_dict,  # {"sample1": "Control", "sample2": "Treatment", ...}
        "Time": time_dict
    },
    # Custom colors
    annotation_colors={
        "Condition": {"Control": "#2ecc71", "Treatment": "#e74c3c"},
        "Gene Type": {"Kinase": "#3498db", "Transcription Factor": "#9b59b6"}
    }
)
```

### Full Parameter Example

```python
hb.create_heatmap(
    data_path="expression_matrix.csv",
    output_path="output/heatmap.pdf",
    title="Gene Expression Heatmap",
    cmap="RdBu_r",                    # Color map
    center=0,                         # Color center value
    vmin=-2, vmax=2,                  # Value range
    row_cluster=True,                 # Row clustering
    col_cluster=True,                 # Column clustering
    standard_scale=None,              # Standardization: "row", "col", None
    z_score=None,                     # Z-score: 0 (row), 1 (col), None
    # Label optimization
    max_row_label_fontsize=10,
    max_col_label_fontsize=10,
    rotate_col_labels=45,             # Column label rotation angle
    hide_row_labels=False,
    hide_col_labels=False,
    # Size
    figsize=(12, 10),
    dpi=300
)
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--data-path`, `-d` | string | - | Yes | Path to input data file (CSV) |
| `--output-path`, `-o` | string | heatmap.png | No | Output file path |
| `--title` | string | Gene Expression Heatmap | No | Heatmap title |
| `--cmap` | string | RdBu_r | No | Color map |
| `--center` | float | 0 | No | Color center value |
| `--vmin` | float | -2 | No | Minimum value for color scale |
| `--vmax` | float | 2 | No | Maximum value for color scale |
| `--row-cluster` | bool | true | No | Enable row clustering |
| `--col-cluster` | bool | true | No | Enable column clustering |
| `--standard-scale` | string | None | No | Standardization: row, col, None |
| `--z-score` | int | None | No | Z-score: 0 (row), 1 (col), None |
| `--figsize` | tuple | (12, 10) | No | Figure size (width, height) |
| `--dpi` | int | 300 | No | Resolution (dots per inch) |
| `--format` | string | pdf | No | Output format (pdf, png, svg) |

## Input Data Format

### Expression Matrix (CSV)

```csv
,sample1,sample2,sample3,sample4
Gene_A,2.5,-1.2,0.8,-0.5
Gene_B,-0.8,1.5,-2.1,0.3
Gene_C,1.2,0.5,-0.7,1.8
...
```

- First column: Gene names (row index)
- First row: Sample names (column names)
- Data: Expression values (e.g., log2 fold change, TPM, FPKM, etc.)

### Annotation File Format

Annotation dictionary format: `{item_name: category_value}`

Example:
```python
condition_dict = {
    "sample1": "Control",
    "sample2": "Control", 
    "sample3": "Treatment",
    "sample4": "Treatment"
}
```

## Color Schemes

Built-in color schemes:
- `"RdBu_r"` - Red-Blue (classic differential expression)
- `"viridis"` - Yellow-Purple (continuous data)
- `"RdYlBu_r"` - Red-Yellow-Blue
- `"coolwarm"` - Cool-Warm
- `"seismic"` - Seismic
- `"bwr"` - Blue-White-Red

## Command Line Usage

```text

# Basic usage
python -m skills.heatmap_beautifier.scripts.main \
    --input expression_matrix.csv \
    --output heatmap.pdf

# With clustering and annotations
python -m skills.heatmap_beautifier.scripts.main \
    --input expression_matrix.csv \
    --output heatmap.pdf \
    --row-cluster \
    --col-cluster \
    --row-annotations row_annot.json \
    --col-annotations col_annot.json \
    --title "Gene Expression"
```

## Output Description

Generated heatmap includes:
1. **Main Heatmap**: Expression matrix visualization
2. **Left Clustering Tree**: Row (gene) hierarchical clustering
3. **Top Clustering Tree**: Column (sample) hierarchical clustering  
4. **Left Annotation Bar**: Row annotations (e.g., gene types)
5. **Top Annotation Bar**: Column annotations (e.g., sample groups)
6. **Color Scale**: Color bar corresponding to expression values

## Notes

1. **Data Preprocessing**: It is recommended to perform log2 transformation or standardization on data first
2. **Memory Usage**: Large datasets (>5000 rows) may take longer
3. **Label Visibility**: When there are too many rows/columns, some labels will be automatically hidden
4. **Clustering Distance**: Default uses Euclidean distance and Ward method

## Author

Bioinformatics Visualization Team

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

This skill accepts requests that match the documented purpose of `heatmap-beautifier` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `heatmap-beautifier` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
