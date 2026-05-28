# Multimodal and Multi-omics Integration Models

This document covers the models in scvi-tools used for the joint analysis of multimodal data.

## totalVI (Total Variational Inference)

**Purpose**: Joint analysis of CITE-seq data (simultaneous measurement of RNA and proteins from the same cells).

**Core Features**:
- Jointly models gene expression and protein abundance
- Learns a shared low-dimensional representation
- Supports protein information imputation from RNA data
- Simultaneous differential expression analysis for both modalities
- Handles batch effects in both RNA and protein layers

**Applicable Scenarios**:
- Analyzing CITE-seq or REAP-seq data
- Joint measurement of RNA + cell surface proteins
- Imputing missing protein data
- Integrating protein and RNA information
- Multi-batch CITE-seq data integration

**Data Requirements**:
- Gene expression data in `.X` or a specific layer of an AnnData object
- Protein measurements in `.obsm["protein_expression"]`
- The same cells are measured for both modalities

**Basic Usage**:
```python
import scvi

# Setup data - specify RNA and protein layers
scvi.model.TOTALVI.setup_anndata(
    adata,
    layer="counts",  # RNA counts
    protein_expression_obsm_key="protein_expression",  # Protein counts
    batch_key="batch"
)

# Train model
model = scvi.model.TOTALVI(adata)
model.train()

# Get joint latent representation
latent = model.get_latent_representation()

# Get normalized values for both modalities
rna_normalized = model.get_normalized_expression()
protein_normalized = model.get_normalized_expression(
    transform_batch="batch1",
    protein_expression=True
)

# Differential expression analysis (applicable to RNA and protein)
rna_de = model.differential_expression(groupby="cell_type")
protein_de = model.differential_expression(
    groupby="cell_type",
    protein_expression=True
)
```

**Key Parameters**:
- `n_latent`: Latent space dimension (default: 20)
- `n_layers_encoder`: Number of encoder layers (default: 1)
- `n_layers_decoder`: Number of decoder layers (default: 1)
- `protein_dispersion`: Protein dispersion handling ("protein" or "protein-batch")
- `empirical_protein_background_prior`: Whether to use an empirical background prior for proteins

**Advanced Features**:

**Protein Imputation**:
```python
# Impute missing proteins for RNA-only cells
# (Applicable for mapping RNA-seq to CITE-seq reference datasets)
protein_foreground = model.get_protein_foreground_probability()
imputed_proteins = model.get_normalized_expression(
    protein_expression=True,
    n_samples=25
)
```

**Denoising**:
```python
# Get denoised counts for both modalities
denoised_rna = model.get_normalized_expression(n_samples=25)
denoised_protein = model.get_normalized_expression(
    protein_expression=True,
    n_samples=25
)
```

**Best Practices**:
1. For datasets containing ambient protein, use the empirical protein background prior.
2. For heterogeneous protein data, consider using protein-specific dispersion.
3. Use the joint latent space for clustering (performs better than using RNA only).
4. Validate protein imputation effects using known markers.
5. Check protein quality control (QC) metrics before training.

## MultiVI (Multi-modal Variational Inference)

**Purpose**: Integrating paired and unpaired multi-omics data (e.g., RNA + ATAC, including paired and unpaired cells).

**Core Features**:
- Handles paired data (same cells) and unpaired data (different cells)
- Integrates multiple modalities: RNA, ATAC, protein, etc.
- Missing modality imputation
- Learns shared representations across modalities
- Flexible integration strategies

**Applicable Scenarios**:
- 10x Multiome data (paired RNA + ATAC)
- Integrating independent RNA-seq and ATAC-seq experiments
- Some cells have dual modalities, while others have only one
- Cross-modality imputation tasks

**Data Requirements**:
- AnnData containing multimodal information
- Modality indicator (recording which measurements each cell has)
- Can handle:
  - All cells have dual modalities (fully paired)
  - Mix of paired and unpaired cells
  - Fully unpaired datasets

**Basic Usage**:
```python
# Prepare data with modality information
# adata.X should contain all features (genes + peaks)
# adata.var["modality"] indicates "Gene" or "Peak"
# adata.obs["modality"] indicates the modality each cell belongs to

scvi.model.MULTIVI.setup_anndata(
    adata,
    batch_key="batch",
    modality_key="modality"  # Column indicating cell modality
)

model = scvi.model.MULTIVI(adata)
model.train()

# Get joint latent representation
latent = model.get_latent_representation()

# Impute missing modality
# Example: Predict ATAC for RNA-only cells
imputed_accessibility = model.get_accessibility_estimates(
    indices=rna_only_indices
)

# Get normalized expression/accessibility
rna_normalized = model.get_normalized_expression()
atac_normalized = model.get_accessibility_estimates()
```

**Key Parameters**:
- `n_genes`: Number of gene features
- `n_regions`: Number of accessibility regions
- `n_latent`: Latent space dimension (default: 20)

**Integration Scenarios**:

**Scenario 1: Fully Paired (10x Multiome)**:
```python
# All cells have RNA and ATAC
# Unified modality key: "paired"
adata.obs["modality"] = "paired"
```

**Scenario 2: Partially Paired**:
```python
# Some cells have both, some RNA only, some ATAC only
adata.obs["modality"] = ["RNA+ATAC", "RNA", "ATAC", ...]
```

**Scenario 3: Fully Unpaired**:
```python
# Independent RNA and ATAC experiments
adata.obs["modality"] = ["RNA"] * n_rna + ["ATAC"] * n_atac
```

**Advanced Use Cases**:

**Cross-modality Prediction**:
```python
# Predict peaks from gene expression
accessibility_from_rna = model.get_accessibility_estimates(
    indices=rna_only_cells
)

# Predict genes from accessibility
expression_from_atac = model.get_normalized_expression(
    indices=atac_only_cells
)
```

**Modality-specific Analysis**:
```python
# Analyze by modality separately
rna_subset = adata[adata.obs["modality"].str.contains("RNA")]
atac_subset = adata[adata.obs["modality"].str.contains("ATAC")]
```

## MrVI (Multi-resolution Variational Inference)

**Purpose**: Multi-sample analysis considering sample-specific differences and shared differences.

**Core Features**:
- Analyzes multiple samples/conditions simultaneously
- Decomposes variation into:
  - Shared variation (common across samples)
  - Sample-specific variation
- Supports sample-level comparison
- Identifies sample-specific cell states

**Applicable Scenarios**:
- Comparing multiple biological samples or conditions
- Identifying sample-specific vs. shared cell states
- Disease vs. healthy sample comparison
- Understanding inter-sample heterogeneity
- Multi-donor studies

**Basic Usage**:
```python
scvi.model.MRVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    sample_key="sample"  # Key: Define biological samples
)

model = scvi.model.MRVI(adata, n_latent=10, n_latent_sample=5)
model.train()

# Get representations
shared_latent = model.get_latent_representation()  # Shared across samples
sample_specific = model.get_sample_specific_representation()

# Sample distance matrix
sample_distances = model.get_sample_distances()
```

**Key Parameters**:
- `n_latent`: Dimension of shared latent space
- `n_latent_sample`: Dimension of sample-specific space
- `sample_key`: Column name defining biological samples

**Analysis Workflow**:
```python
# 1. Identify shared cell types across samples
sc.pp.neighbors(adata, use_rep="X_MrVI_shared")
sc.tl.umap(adata)
sc.tl.leiden(adata, key_added="shared_clusters")

# 2. Analyze sample-specific variation
sample_repr = model.get_sample_specific_representation()

# 3. Compare samples
distances = model.get_sample_distances()

# 4. Find sample-enriched genes
de_results = model.differential_expression(
    groupby="sample",
    group1="Disease",
    group2="Healthy"
)
```

**Use Cases**:
- **Multi-donor studies**: Separate donor effects from cell type variation
- **Disease studies**: Identify disease-specific vs. shared biological features
- **Time series**: Separate temporal changes from stable variation
- **Batch + Biology**: Deconstruct technical bias and biological variation

## totalVI vs. MultiVI vs. MrVI: How to choose?

### totalVI
**Best for**: CITE-seq (RNA + Protein in the same cells)
- Paired measurements
- Single modality type per feature
- Focus: Protein imputation, joint analysis

### MultiVI
**Best for**: Multimodal (RNA + ATAC, etc.)
- Paired, unpaired, or mixed
- Different feature types
- Focus: Cross-modality integration and imputation

### MrVI
**Best for**: Multi-sample RNA-seq
- Single modality (RNA)
- Multiple biological samples
- Focus: Sample-level variation decomposition

## Integration Best Practices

### For CITE-seq (totalVI)
1. **Protein QC**: Remove low-quality antibodies
2. **Background Subtraction**: Use empirical background priors
3. **Joint Clustering**: Use the joint latent space instead of RNA only
4. **Validation**: Check known markers in both modalities

### For Multiome/Multimodal (MultiVI)
1. **Feature Filtering**: Filter genes and peaks independently
2. **Balance Modalities**: Ensure each modality has reasonable representation
3. **Modality Weights**: Consider if one modality dominates the other
4. **Imputation Validation**: Carefully validate imputed values

### For Multi-sample (MrVI)
1. **Sample Definition**: Carefully define biological samples
2. **Sample Size**: Ensure sufficient cell counts per sample
3. **Covariate Handling**: Correctly distinguish between batch and sample
4. **Interpretation**: Distinguish technical variation from biological variation

## Full Example: CITE-seq Analysis with totalVI

```python
import scvi
import scanpy as sc

# 1. Load CITE-seq data
adata = sc.read_h5ad("cite_seq.h5ad")

# 2. QC and filtering
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.highly_variable_genes(adata, n_top_genes=4000)

# Protein QC
protein_counts = adata.obsm["protein_expression"]
# Remove low-quality proteins

# 3. Setup totalVI
scvi.model.TOTALVI.setup_anndata(
    adata,
    layer="counts",
    protein_expression_obsm_key="protein_expression",
    batch_key="batch"
)

# 4. Train
model = scvi.model.TOTALVI(adata, n_latent=20)
model.train(max_epochs=400)

# 5. Extract joint representation
latent = model.get_latent_representation()
adata.obsm["X_totalVI"] = latent

# 6. Cluster on joint space
sc.pp.neighbors(adata, use_rep="X_totalVI")
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)

# 7. Differential expression analysis for both modalities
rna_de = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1"
)

protein_de = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1",
    protein_expression=True
)

# 8. Save model
model.save("totalvi_model")
```