---
name: spatial-transcriptomics-mapper
description: Map spatial transcriptomics data from 10x Genomics Visium/Xenium onto.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Spatial Transcriptomics Mapper (ID: 196)

## When to Use

- Use this skill when the task is to Map spatial transcriptomics data from 10x Genomics Visium/Xenium onto.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Map spatial transcriptomics data from 10x Genomics Visium/Xenium onto.
- Packaged executable path(s): `scripts/__init__.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `h5py`: `unspecified`. Declared in `requirements.txt`.
- `matplotlib`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `pandas`: `unspecified`. Declared in `requirements.txt`.
- `pil`: `unspecified`. Declared in `requirements.txt`.
- `pyarrow`: `unspecified`. Declared in `requirements.txt`.
- `scanpy`: `unspecified`. Declared in `requirements.txt`.
- `seaborn`: `unspecified`. Declared in `requirements.txt`.
- `squidpy`: `unspecified`. Declared in `requirements.txt`.
- `tifffile`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/spatial-transcriptomics-mapper"
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
- Primary implementation surface: `scripts/__init__.py` with additional helper scripts under `scripts/`.
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

Spatial Transcriptomics analysis tool for processing 10x Genomics Visium or Xenium data, projecting gene expression data back onto tissue section images to draw "gene-space" distribution maps. Supports gene expression visualization, spatial clustering analysis, and morphological feature correlation.

## Features

- **Visium Data Processing**: Supports Space Ranger output (filtered_feature_bc_matrix.h5, spatial/tissue_positions_list.csv, spatial/tissue_lowres_image.png)
- **Xenium Data Processing**: Supports Xenium Explorer output (.h5, transcripts.parquet, nucleus_boundaries.parquet)
- **Gene Expression Mapping**: Projects expression of specified genes onto tissue images
- **Spatial Clustering Visualization**: Displays spatial distribution of Seurat/Scanpy clustering results
- **Multi-gene Joint Analysis**: Supports combined visualization of multiple genes
- **High-resolution Output**: Supports high-resolution image export

## Installation

```text

# Required dependencies
pip install scanpy squidpy matplotlib seaborn pillow numpy pandas h5py

# Optional: For Xenium data processing
pip install pyarrow dask

# Optional: For advanced image processing
pip install opencv-python scikit-image
```

## Quick Start - Test Data

Generate sample Visium data to test the tool:

```text

# Generate test data
python scripts/generate_test_data.py \
  --platform visium \
  --output ./test_data/visium_sample \
  --n-spots 500 \
  --n-genes 1000

# Run analysis on test data
python scripts/main.py \
  --platform visium \
  --data-dir ./test_data/visium_sample \
  --gene GENE_0000 \
  --output ./test_output/
```

## Usage

### Basic - Visium Data

```text
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/spaceranger/outs/ \
  --gene PIK3CA \
  --output ./output/
```

### Basic - Xenium Data

```text
python scripts/main.py \
  --platform xenium \
  --data-dir /path/to/xenium/outs/ \
  --gene PIK3CA \
  --output ./output/
```

### Multiple Genes

```text
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --genes PIK3CA,PTEN,EGFR \
  --mode overlay \
  --output ./output/
```

### With Clustering Results

```text
python scripts/main.py \
  --platform visium \
  --data-dir /path/to/data/ \
  --cluster-file ./clusters.csv \
  --output ./output/
```

## Input File Structure

### Visium (Space Ranger output)
```
outs/
├── filtered_feature_bc_matrix.h5    # Gene expression matrix
├── raw_feature_bc_matrix.h5         # Raw counts (optional)
├── spatial/
│   ├── tissue_positions_list.csv    # Spot positions
│   ├── tissue_lowres_image.png      # Low-res H&E image
│   ├── tissue_hires_image.png       # High-res H&E image
│   └── scalefactors_json.json       # Scale factors
└── web_summary.html
```

### Xenium
```
outs/
├── cell_feature_matrix.h5           # Cell x gene matrix
├── transcripts.parquet              # Transcript coordinates
├── nucleus_boundaries.parquet       # Cell boundaries
├── cell_boundaries.parquet
├── morphology_focus.ome.tif         # Morphology image
└── experiment.xenium
```

## Output Files

- `{gene}_spatial_map.png`: Single gene spatial expression map
- `{gene}_heatmap.png`: Gene expression heatmap
- `multi_gene_overlay.png`: Multi-gene overlay map (if using --mode overlay)
- `cluster_spatial_map.png`: Cluster spatial distribution map
- `combined_report.html`: Comprehensive HTML report

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--platform` | str | required | Platform type: visium or xenium |
| `--data-dir` | str | required | Data directory path |
| `--gene` | str | optional | Single gene name |
| `--genes` | list | optional | Multiple genes, comma-separated |
| `--mode` | str | single | Mode: single/overlay/multi |
| `--cluster-file` | str | optional | Clustering result CSV file path |
| `--output` | str | ./output | Output directory |
| `--dpi` | int | 300 | Output image DPI |
| `--cmap` | str | viridis | Color map scheme |
| `--spot-size` | float | 1.0 | Visium spot size factor |
| `--alpha` | float | 0.8 | Transparency (0-1) |
| `--min-count` | int | 0 | Minimum expression filter |
| --crop | str | optional | Crop region (x1,y1,x2,y2) |

## Examples

### Example 1: Single Gene Visualization
```text
python scripts/main.py \
  --platform visium \
  --data-dir ./visium_sample/outs/ \
  --gene EPCAM \
  --cmap Reds \
  --output ./results/
```

### Example 2: Tumor Marker Combination
```text
python scripts/main.py \
  --platform visium \
  --data-dir ./breast_cancer/outs/ \
  --genes PIK3CA,ERBB2,ESR1,PGR \
  --mode multi \
  --cmap plasma \
  --output ./tumor_markers/
```

### Example 3: Xenium Subcellular Resolution
```text
python scripts/main.py \
  --platform xenium \
  --data-dir ./xenium_lung/outs/ \
  --genes SFTPB,SFTPC,SCGB1A1 \
  --dpi 600 \
  --output ./xenium_results/
```

### Example 4: Spatial Clustering Visualization
```text
python scripts/main.py \
  --platform visium \
  --data-dir ./sample/outs/ \
  --cluster-file ./seurat_clusters.csv \
  --output ./clusters/
```

## API Usage

```python
from skills.spatial_transcriptomics_mapper.scripts.main import SpatialMapper

# Initialize
mapper = SpatialMapper(
    platform="visium",
    data_dir="/path/to/data",
    output_dir="./output"
)

# Load data
mapper.load_data()

# Plot single gene
mapper.plot_gene_spatial(
    gene="PIK3CA",
    cmap="viridis",
    save_path="./output/pik3ca.png"
)

# Plot multiple genes
mapper.plot_multi_genes(
    genes=["PIK3CA", "PTEN", "EGFR"],
    mode="grid",
    save_path="./output/multi.png"
)

# Get spatial statistics
stats = mapper.get_spatial_stats(gene="PIK3CA")
```

## Notes

- Visium data uses low-resolution images by default to improve processing speed, can use --hires parameter to enable high resolution
- For large Xenium datasets, it is recommended to use --crop parameter to specify region of interest
- Color map reference: https://matplotlib.org/stable/tutorials/colors/colormaps.html
- For large samples, consider using --downsample parameter to reduce resolution

## References

- 10x Genomics Visium: https://www.10xgenomics.com/products/spatial-gene-expression
- 10x Genomics Xenium: https://www.10xgenomics.com/platforms/xenium
- Scanpy: https://scanpy.readthedocs.io/
- Squidpy: https://squidpy.readthedocs.io/

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

This skill accepts requests that match the documented purpose of `spatial-transcriptomics-mapper` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `spatial-transcriptomics-mapper` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
