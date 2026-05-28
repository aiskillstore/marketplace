# ATAC-seq and Chromatin Accessibility Models

This document introduces the models in scvi-tools for analyzing single-cell ATAC-seq and chromatin accessibility data.

## PeakVI

**Purpose**: Analysis and integration of single-cell ATAC-seq data using peak counts.

**Core Features**:
- Variational Autoencoder (VAE) specifically designed for scATAC-seq peak data.
- Learns low-dimensional representations of chromatin accessibility.
- Performs batch correction across samples.
- Supports differential accessibility testing.
- Integrates multiple ATAC-seq datasets.

**Use Cases**:
- Analyzing scATAC-seq peak count matrices.
- Integrating multiple ATAC-seq experiments.
- Batch correction of chromatin accessibility data.
- Dimensionality reduction for ATAC-seq.
- Differential accessibility analysis between cell types or conditions.

**Data Requirements**:
- Peak count matrix (cells × peaks).
- Binarized or count-based peak accessibility data.
- Batch/sample annotations (optional, for batch correction).

**Basic Usage**:
```python
import scvi

# Prepare data (peaks should be stored in adata.X)
# Optional: filter peaks
sc.pp.filter_genes(adata, min_cells=3)

# Set up data
scvi.model.PEAKVI.setup_anndata(
    adata,
    batch_key="batch"
)

# Train the model
model = scvi.model.PEAKVI(adata)
model.train()

# Get latent representation (batch-corrected)
latent = model.get_latent_representation()
adata.obsm["X_PeakVI"] = latent

# Differential accessibility analysis
da_results = model.differential_accessibility(
    groupby="cell_type",
    group1="TypeA",
    group2="TypeB"
)
```

**Key Parameters**:
- `n_latent`: Dimension of the latent space (default: 10).
- `n_hidden`: Number of nodes per hidden layer (default: 128).
- `n_layers`: Number of hidden layers (default: 1).
- `region_factors`: Whether to learn region-specific factors (default: True).
- `latent_distribution`: Distribution of the latent space ("normal" or "ln").

**Outputs**:
- `get_latent_representation()`: Low-dimensional embeddings of cells.
- `get_accessibility_estimates()`: Normalized accessibility estimates.
- `differential_accessibility()`: Statistical testing for differential peaks.
- `get_region_factors()`: Peak-specific scaling factors.

**Best Practices**:
1. Filter out low-quality peaks (peaks present in very few cells).
2. Include batch information if integrating multiple samples.
3. Use latent representations for clustering and UMAP visualization.
4. For datasets with large technical biases, consider using `region_factors=True`.
5. Store latent embeddings in `adata.obsm` for downstream analysis using scanpy.

## PoissonVI

**Purpose**: Quantitative analysis of scATAC-seq fragment counts (more detailed than peak counts).

**Core Features**:
- Directly models fragment counts (not just the presence/absence of peaks).
- Uses Poisson distribution for count data.
- Captures quantitative differences in accessibility.
- Supports refined analysis of chromatin states.

**Use Cases**:
- Analyzing fragment-level ATAC-seq data.
- Requires quantitative accessibility measurements.
- Higher resolution analysis than binarized peak calling.
- Studying continuous processes in chromatin accessibility.

**Data Requirements**:
- Fragment count matrix (cells × genomic regions).
- Count data (non-binarized).

**Basic Usage**:
```python
scvi.model.POISSONVI.setup_anndata(
    adata,
    batch_key="batch"
)

model = scvi.model.POISSONVI(adata)
model.train()

# Get results
latent = model.get_latent_representation()
accessibility = model.get_accessibility_estimates()
```

**Main Differences from PeakVI**:
- **PeakVI**: Best for standard peak count matrices, faster.
- **PoissonVI**: Best for quantitative fragment counts, providing more detailed results.

**When to Choose PoissonVI over PeakVI**:
- Processing fragment counts instead of identified peaks.
- Need to capture quantitative differences.
- High-quality, high-coverage data.
- Interested in subtle accessibility changes.

## scBasset

**Purpose**: Deep learning analysis method for scATAC-seq with interpretability and motif analysis capabilities.

**Core Features**:
- Convolutional Neural Network (CNN) architecture for sequence-based analysis.
- Models raw DNA sequences rather than just peak counts.
- Supports motif discovery and transcription factor (TF) binding prediction.
- Provides interpretable feature importance.
- Performs batch correction.

**Use Cases**:
- Integrating DNA sequence information.
- Interested in TF motif analysis.
- Need interpretable models (which sequences drive accessibility).
- Analyzing regulatory elements and TF binding sites.
- Predicting accessibility from sequence alone.

**Data Requirements**:
- Peak sequences (extracted from the genome).
- Peak accessibility matrix.
- Reference genome (for sequence extraction).

**Basic Usage**:
```python
# scBasset requires sequence information
# First, extract sequences for peaks
from scbasset import utils
sequences = utils.fetch_sequences(adata, genome="hg38")

# Set up and train
scvi.model.SCBASSET.setup_anndata(
    adata,
    batch_key="batch"
)

model = scvi.model.SCBASSET(adata, sequences=sequences)
model.train()

# Get latent representation
latent = model.get_latent_representation()

# Interpret the model: which sequences/motifs are important
importance_scores = model.get_feature_importance()
```

**Key Parameters**:
- `n_latent`: Dimension of the latent space.
- `conv_layers`: Number of convolutional layers.
- `n_filters`: Number of filters per convolutional layer.
- `filter_size`: Size of the convolutional filters.

**Advanced Features**:
- **In silico mutagenesis**: Predicting how sequence changes affect accessibility.
- **Motif enrichment**: Identifying TF motifs enriched in accessible regions.
- **Batch correction**: Similar to other scvi-tools models.
- **Transfer learning**: Fine-tuning on new datasets.

**Interpretability Tools**:
```python
# Get importance scores for sequences
importance = model.get_sequence_importance(region_indices=[0, 1, 2])

# Predict accessibility for new sequences
predictions = model.predict_accessibility(new_sequences)
```

## ATAC-seq Model Selection Suggestions

### PeakVI
**Choose when**:
- Standard scATAC-seq analysis workflow.
- You have a peak count matrix (the most common format).
- Need fast, efficient batch correction.
- Want intuitive differential accessibility analysis.
- Prioritize computational efficiency.

**Advantages**:
- Fast training and inference.
- Proven track record in the scATAC-seq field.
- Easy integration with scanpy workflows.
- Robust batch correction.

### PoissonVI
**Choose when**:
- You have fragment-level count data.
- Need quantitative accessibility measurements.
- Interested in subtle differences.
- High-coverage, high-quality data.

**Advantages**:
- More detailed quantitative information.
- Better handling of gradient changes.
- Statistical model suited for counts.

### scBasset
**Choose when**:
- Want to integrate DNA sequences.
- Need biological interpretation (motifs, TFs).
- Interested in regulatory mechanisms.
- Have computational resources for training CNNs.
- Want predictive capabilities for new sequences.

**Advantages**:
- Sequence-based with biological interpretability.
- Built-in motif and TF analysis.
- Predictive modeling capabilities.
- In silico perturbation experiments.

## Workflow Example: Complete ATAC-seq Analysis

```python
import scvi
import scanpy as sc

# 1. Load and preprocess ATAC-seq data
adata = sc.read_h5ad("atac_data.h5ad")

# 2. Filter low-quality peaks
sc.pp.filter_genes(adata, min_cells=10)

# 3. Set up and train PeakVI
scvi.model.PEAKVI.setup_anndata(
    adata,
    batch_key="sample"
)

model = scvi.model.PEAKVI(adata, n_latent=20)
model.train(max_epochs=400)

# 4. Extract latent representation
latent = model.get_latent_representation()
adata.obsm["X_PeakVI"] = latent

# 5. Downstream analysis
sc.pp.neighbors(adata, use_rep="X_PeakVI")
sc.tl.umap(adata)
sc.tl.leiden(adata, key_added="clusters")

# 6. Differential accessibility analysis
da_results = model.differential_accessibility(
    groupby="clusters",
    group1="0",
    group2="1"
)

# 7. Save the model
model.save("peakvi_model")
```

## Combining with Gene Expression (RNA+ATAC)

For paired multimodal data (RNA+ATAC from the same cell), use **MultiVI** instead:

```python
# For 10x Multiome or similar paired data
scvi.model.MULTIVI.setup_anndata(
    adata,
    batch_key="sample",
    modality_key="modality"  # "RNA" or "ATAC"
)

model = scvi.model.MULTIVI(adata)
model.train()

# Get joint latent space
latent = model.get_latent_representation()
```

For more details on multimodal integration, please refer to `models-multimodal.md`.

## ATAC-seq Analysis Best Practices

1. **Quality Control**:
   - Filter out cells with extremely low or high peak counts.
   - Remove peaks present in only a very small number of cells.
   - Filter mitochondrial and sex chromosome peaks as needed.

2. **Batch Correction**:
   - Always include `batch_key` when integrating multiple samples.
   - Consider technical covariates (sequencing depth, TSS enrichment).

3. **Feature Selection**:
   - Unlike RNA-seq, all peaks are typically used.
   - For efficiency, consider filtering out extremely rare peaks.

4. **Latent Dimensions**:
   - Start with `n_latent=10-30` depending on dataset complexity.
   - Use larger values for more heterogeneous datasets.

5. **Downstream Analysis**:
   - Use latent representations for clustering and visualization.
   - Associate peaks with genes for regulatory analysis.
   - Perform motif enrichment analysis on cluster-specific peaks.

6. **Computational Considerations**:
   - ATAC-seq matrices are often very large (high number of peaks).
   - Consider downsampling peaks for initial exploration.
   - Use GPU acceleration for large datasets.