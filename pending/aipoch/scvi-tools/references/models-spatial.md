# Spatial Transcriptomics Models

This document covers the models in scvi-tools used for analyzing spatially resolved transcriptomics data.

## DestVI (Deconvolution of Spatial Transcriptomics using Variational Inference)

**Purpose**: Multi-resolution deconvolution of spatial transcriptomics using single-cell reference data.

**Key Features**:
- Estimate cell-type proportions at each spatial location
- Deconvolution using single-cell RNA-seq reference data
- Multi-resolution approach (global and local patterns)
- Accounts for spatial correlation
- Provides uncertainty quantification

**Use Cases**:
- Deconvolving Visium or similar spatial transcriptomics
- Having scRNA-seq reference data with cell-type labels
- Wanting to map cell types to spatial locations
- Interested in the spatial organization of cell types
- Need probabilistic estimates of cell-type abundance

**Data Requirements**:
- **Spatial Data**: Visium or similar spot-based measurements (target data)
- **Single-cell Reference**: scRNA-seq with cell-type annotations
- Both datasets should share genes

**Basic Usage**:
```python
import scvi

# Step 1: Train scVI on single-cell reference data
scvi.model.SCVI.setup_anndata(sc_adata, layer="counts")
sc_model = scvi.model.SCVI(sc_adata)
sc_model.train()

# Step 2: Set up spatial data
scvi.model.DESTVI.setup_anndata(
    spatial_adata,
    layer="counts"
)

# Step 3: Train DestVI using the reference data
model = scvi.model.DESTVI.from_rna_model(
    spatial_adata,
    sc_model,
    cell_type_key="cell_type"  # Cell-type labels in reference data
)
model.train(max_epochs=2500)

# Step 4: Get cell-type proportions
proportions = model.get_proportions()
spatial_adata.obsm["proportions"] = proportions

# Step 5: Get expression for specific cell types
# Gene expression specific to each cell type at each spot
ct_expression = model.get_scale_for_ct("T cells")
```

**Key Parameters**:
- `amortization`: Amortization strategy ("both", "latent", "proportion")
- `n_latent`: Latent dimension (inherited from scVI model)

**Outputs**:
- `get_proportions()`: Cell-type proportions per spot
- `get_scale_for_ct(cell_type)`: Expression patterns for specific cell types
- `get_gamma()`: Proportion-specific gene expression scaling

**Visualization**:
```python
import scanpy as sc
import matplotlib.pyplot as plt

# Visualize specific cell-type proportions spatially
sc.pl.spatial(
    spatial_adata,
    color="T cells",  # If proportions are added to .obs
    spot_size=150
)

# Or use obsm directly
for ct in cell_types:
    plt.figure()
    sc.pl.spatial(
        spatial_adata,
        color=spatial_adata.obsm["proportions"][ct],
        title=f"{ct} proportions"
    )
```

## Stereoscope

**Purpose**: Cell-type deconvolution of spatial transcriptomics using a probabilistic model.

**Key Features**:
- Reference-based deconvolution
- Probabilistic framework for cell-type proportions
- Applicable to various spatial technologies
- Handles gene selection and normalization

**Use Cases**:
- Similar to DestVI but with a simpler approach
- Deconvolving spatial data using reference data
- Faster alternative for basic deconvolution tasks

**Basic Usage**:
```python
scvi.model.STEREOSCOPE.setup_anndata(
    sc_adata,
    labels_key="cell_type",
    layer="counts"
)

# Train on reference data
ref_model = scvi.model.STEREOSCOPE(sc_adata)
ref_model.train()

# Set up spatial data
scvi.model.STEREOSCOPE.setup_anndata(spatial_adata, layer="counts")

# Transfer to spatial data
spatial_model = scvi.model.STEREOSCOPE.from_reference_model(
    spatial_adata,
    ref_model
)
spatial_model.train()

# Get proportions
proportions = spatial_model.get_proportions()
```

## Tangram

**Purpose**: Spatial mapping and integration of single-cell data to spatial locations.

**Key Features**:
- Map single cells to spatial coordinates
- Learn optimal transport between single-cell and spatial data
- Gene imputation for spatial locations
- Cell-type mapping

**Use Cases**:
- Mapping cells from scRNA-seq to spatial locations
- Imputing unmeasured genes in spatial data
- Understanding spatial organization at single-cell resolution
- Integrating scRNA-seq and spatial transcriptomics

**Data Requirements**:
- Annotated single-cell RNA-seq data
- Spatial transcriptomics data
- Shared genes between modalities

**Basic Usage**:
```python
import tangram as tg

# Map cells to spatial locations
ad_map = tg.map_cells_to_space(
    adata_sc=sc_adata,
    adata_sp=spatial_adata,
    mode="cells",  # Or use "clusters" for cell-type mapping
    density_prior="rna_count_based"
)

# Get mapping matrix (cells × spots)
mapping = ad_map.X

# Project cell annotations to space
tg.project_cell_annotations(
    ad_map,
    spatial_adata,
    annotation="cell_type"
)

# Impute genes in spatial data
genes_to_impute = ["CD3D", "CD8A", "CD4"]
tg.project_genes(ad_map, spatial_adata, genes=genes_to_impute)
```

**Visualization**:
```python
# Visualize projected cell-type mapping
sc.pl.spatial(
    spatial_adata,
    color="cell_type_projected",
    spot_size=100
)
```

## gimVI (Generative Integrated Models for Variational Inference)

**Purpose**: Cross-modal imputation between spatial and single-cell data.

**Key Features**:
- Joint model for spatial and single-cell data
- Impute missing genes in spatial data
- Supports cross-dataset queries
- Learns shared representations

**Use Cases**:
- Imputing unmeasured genes in spatial data
- Joint analysis of spatial and single-cell datasets
- Mapping between modalities

**Basic Usage**:
```python
# Concatenate datasets
combined_adata = sc.concat([sc_adata, spatial_adata])

scvi.model.GIMVI.setup_anndata(
    combined_adata,
    layer="counts"
)

model = scvi.model.GIMVI(combined_adata)
model.train()

# Impute genes in spatial data
imputed = model.get_imputed_values(spatial_indices)
```

## scVIVA (Spatial Variational Inference Variation Analysis)

**Purpose**: Analyze cell-environment relationships in spatial data.

**Key Features**:
- Model cell neighborhoods and environments
- Identify environment-related gene expression
- Accounts for spatial correlation structures
- Cell-cell interaction analysis

**Use Cases**:
- Understanding how spatial context affects cells
- Identifying microenvironment-specific gene programs
- Cell-cell interaction studies
- Microenvironment analysis

**Data Requirements**:
- Spatial transcriptomics data with coordinates
- Cell-type annotations (optional)

**Basic Usage**:
```python
scvi.model.SCVIVA.setup_anndata(
    spatial_adata,
    layer="counts",
    spatial_key="spatial"  # Coordinates in .obsm
)

model = scvi.model.SCVIVA(spatial_adata)
model.train()

# Get environment representations
env_latent = model.get_environment_representation()

# Identify environment-specific genes
env_genes = model.get_environment_specific_genes()
```

## ResolVI

**Purpose**: Handling spatial transcriptomics noise through resolution-aware modeling.

**Key Features**:
- Accounts for spatial resolution effects
- Denoises spatial data
- Multi-scale analysis
- Improves downstream analysis quality

**Use Cases**:
- Noisy spatial data
- Multiple spatial resolutions
- Denoising required before analysis
- Improving data quality

**Basic Usage**:
```python
scvi.model.RESOLVI.setup_anndata(
    spatial_adata,
    layer="counts",
    spatial_key="spatial"
)

model = scvi.model.RESOLVI(spatial_adata)
model.train()

# Get denoised expression
denoised = model.get_denoised_expression()
```

## Spatial Transcriptomics Model Selection

### DestVI
**Selection Advice**:
- Needs detailed deconvolution with reference data
- High-quality scRNA-seq reference available
- Multi-resolution analysis desired
- Uncertainty quantification needed

**Best for**: Visium, spot-based technologies

### Stereoscope
**Selection Advice**:
- Simpler, faster deconvolution
- Basic cell-type proportion estimation
- Limited computational resources

**Best for**: Quick deconvolution tasks

### Tangram
**Selection Advice**:
- Single-cell resolution mapping
- Imputing many genes
- Interested in cell localization
- Preference for optimal transport methods

**Best for**: Detailed spatial mapping

### gimVI
**Selection Advice**:
- Bidirectional imputation
- Joint modeling of spatial and single-cell
- Cross-dataset queries

**Best for**: Integration and imputation

### scVIVA
**Selection Advice**:
- Interested in cell environment
- Cell-cell interaction analysis
- Neighborhood effects

**Best for**: Microenvironment studies

### ResolVI
**Selection Advice**:
- Focus on data quality issues
- Denoising needed
- Multi-scale analysis

**Best for**: Preprocessing of noisy data

## Full Workflow: Spatial Deconvolution using DestVI

```python
import scvi
import scanpy as sc
import squidpy as sq

# ===== Part 1: Prepare single-cell reference data =====
# Load and process scRNA-seq reference data
sc_adata = sc.read_h5ad("reference_scrna.h5ad")

# QC and filtering
sc.pp.filter_genes(sc_adata, min_cells=10)
sc.pp.highly_variable_genes(sc_adata, n_top_genes=4000)

# Train scVI on reference data
scvi.model.SCVI.setup_anndata(
    sc_adata,
    layer="counts",
    batch_key="batch"
)

sc_model = scvi.model.SCVI(sc_adata)
sc_model.train(max_epochs=400)

# ===== Part 2: Load spatial data =====
spatial_adata = sc.read_visium("path/to/visium")
spatial_adata.var_names_make_unique()

# QC spatial data
sc.pp.filter_genes(spatial_adata, min_cells=10)

# ===== Part 3: Run DestVI =====
scvi.model.DESTVI.setup_anndata(
    spatial_adata,
    layer="counts"
)

destvi_model = scvi.model.DESTVI.from_rna_model(
    spatial_adata,
    sc_model,
    cell_type_key="cell_type"
)

destvi_model.train(max_epochs=2500)

# ===== Part 4: Extract results =====
# Get proportions
proportions = destvi_model.get_proportions()
spatial_adata.obsm["proportions"] = proportions

# Add proportions to .obs for plotting
for i, ct in enumerate(sc_model.adata.obs["cell_type"].cat.categories):
    spatial_adata.obs[f"prop_{ct}"] = proportions[:, i]

# ===== Part 5: Visualization =====
# Plot specific cell types
cell_types = ["T cells", "B cells", "Macrophages"]

for ct in cell_types:
    sc.pl.spatial(
        spatial_adata,
        color=f"prop_{ct}",
        title=f"{ct} proportions",
        spot_size=150,
        cmap="viridis"
    )

# ===== Part 6: Spatial analysis =====
# Calculate spatial neighbors
sq.gr.spatial_neighbors(spatial_adata)

# Spatial autocorrelation analysis of cell types
for ct in cell_types:
    sq.gr.spatial_autocorr(
        spatial_adata,
        attr="obs",
        mode="moran",
        genes=[f"prop_{ct}"]
    )

# ===== Part 7: Save results =====
destvi_model.save("destvi_model")
spatial_adata.write("spatial_deconvolved.h5ad")
```

## Best Practices for Spatial Analysis

1. **Reference data quality**: Use high-quality, well-annotated scRNA-seq reference data.
2. **Gene overlap**: Ensure sufficient shared genes between reference and spatial data.
3. **Spatial coordinates**: Correctly register spatial coordinates in `.obsm["spatial"]`.
4. **Validation**: Use known marker genes to validate deconvolution results.
5. **Visualization**: Always visualize results spatially to check for biological plausibility.
6. **Cell-type granularity**: Consider appropriate cell-type resolution.
7. **Computational resources**: Spatial models can be memory-intensive.
8. **Quality control**: Filter low-quality spots before analysis.