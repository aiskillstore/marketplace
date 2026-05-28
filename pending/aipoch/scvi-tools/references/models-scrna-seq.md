# Single-Cell RNA-seq Models

This document introduces the core models in scvi-tools for analyzing single-cell RNA sequencing (scRNA-seq) data.

## scVI (Single-Cell Variational Inference)

**Purpose**: Unsupervised analysis, dimensionality reduction, and batch effect correction of single-cell RNA-seq data.

**Key Features**:
- Deep generative model based on Variational Autoencoders (VAE).
- Learns low-dimensional latent representations capturing biological variation.
- Automatically corrects for batch effects and technical covariates.
- Supports estimation of normalized gene expression.
- Supports differential expression analysis.

**Use Cases**:
- Preliminary exploration and dimensionality reduction of scRNA-seq datasets.
- Integration of data across multiple batches or studies.
- Generation of batch-corrected expression matrices.
- Probabilistic differential expression analysis.

**Basic Usage**:
```python
import scvi

# Setup data
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch"
)

# Train model
model = scvi.model.SCVI(adata, n_latent=30)
model.train()

# Extract results
latent = model.get_latent_representation()
normalized = model.get_normalized_expression()
```

**Key Parameters**:
- `n_latent`: Dimension of the latent space (default: 10).
- `n_layers`: Number of hidden layers (default: 1).
- `n_hidden`: Number of nodes per hidden layer (default: 128).
- `dropout_rate`: Dropout rate for the neural network (default: 0.1).
- `dispersion`: Gene-specific or cell-specific dispersion ("gene" or "gene-batch").
- `gene_likelihood`: Distribution model for the data ("zinb", "nb", "poisson").

**Outputs**:
- `get_latent_representation()`: Batch-corrected low-dimensional embedding.
- `get_normalized_expression()`: Denoised and normalized expression values.
- `differential_expression()`: Probabilistic differential expression (DE) detection between groups.
- `get_feature_correlation_matrix()`: Estimation of gene-gene correlations.

## scANVI (Single-Cell ANnotation using Variational Inference)

**Purpose**: Semi-supervised cell type annotation and integration using labeled and unlabeled cells.

**Key Features**:
- Extends scVI with cell type label information.
- Leverages partially labeled datasets for annotation transfer.
- Simultaneously performs batch correction and cell type prediction.
- Supports query-to-reference mapping.

**Use Cases**:
- Annotating new datasets using reference labels.
- Transferring knowledge from well-annotated datasets to unlabeled ones.
- Joint analysis of labeled and unlabeled cells.
- Building cell type classifiers with uncertainty quantification.

**Basic Usage**:
```python
# Option 1: Train from scratch
scvi.model.SCANVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    labels_key="cell_type",
    unlabeled_category="Unknown"
)
model = scvi.model.SCANVI(adata)
model.train()

# Option 2: Initialize from a pre-trained scVI model
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()
scanvi_model = scvi.model.SCANVI.from_scvi_model(
    scvi_model,
    unlabeled_category="Unknown"
)
scanvi_model.train()

# Predict cell types
predictions = scanvi_model.predict()
```

**Key Parameters**:
- `labels_key`: Column name in `adata.obs` containing cell type labels.
- `unlabeled_category`: Label name for unannotated cells.
- Also supports all scVI parameters.

**Outputs**:
- `predict()`: Cell type predictions for all cells.
- `predict_proba()`: Prediction probabilities.
- `get_latent_representation()`: Cell-type-aware latent space.

## AUTOZI

**Purpose**: Automatically identify and model zero-inflated genes in scRNA-seq data.

**Key Features**:
- Distinguishes biological zeros from technical dropouts.
- Learns which genes exhibit zero-inflation characteristics.
- Provides gene-specific zero-inflation probabilities.
- Improves downstream analysis by accounting for technical dropouts.

**Use Cases**:
- Detecting which genes are affected by technical dropouts.
- Improving imputation and normalization for sparse datasets.
- Understanding the extent of zero-inflation in the data.

**Basic Usage**:
```python
scvi.model.AUTOZI.setup_anndata(adata, layer="counts")
model = scvi.model.AUTOZI(adata)
model.train()

# Get zero-inflation probabilities for each gene
zi_probs = model.get_alphas_betas()
```

## VeloVI

**Purpose**: RNA velocity analysis using Variational Autoencoders.

**Key Features**:
- Joint modeling of spliced and unspliced RNA counts.
- Probabilistic estimation of RNA velocity.
- Accounts for technical noise and batch effects.
- Provides uncertainty quantification for velocity estimates.

**Use Cases**:
- Inferring cellular dynamics and differentiation trajectories.
- Analyzing spliced/unspliced count data.
- RNA velocity analysis with batch correction.

**Basic Usage**:
```python
import scvelo as scv

# Prepare velocity data
scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata)

# Train VeloVI
scvi.model.VELOVI.setup_anndata(adata, spliced_layer="Ms", unspliced_layer="Mu")
model = scvi.model.VELOVI(adata)
model.train()

# Get velocity estimates
latent_time = model.get_latent_time()
velocities = model.get_velocity()
```

## contrastiveVI

**Purpose**: Isolating perturbation-specific variation from background biological variation.

**Key Features**:
- Separates shared variation (common across conditions) from target-specific variation.
- Suitable for intervention studies (drug treatment, gene interference).
- Identifies condition-specific gene programs.
- Supports discovery of perturbation-specific effects.

**Use Cases**:
- Analyzing intervention experiments (drug screening, CRISPR, etc.).
- Identifying genes that specifically respond to treatment.
- Isolating treatment effects from background variation.
- Comparing differences between control and treatment groups.

**Basic Usage**:
```python
scvi.model.CONTRASTIVEVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch",
    categorical_covariate_keys=["condition"]  # Control vs Treatment
)

model = scvi.model.CONTRASTIVEVI(
    adata,
    n_latent=10,        # Shared variation
    n_latent_target=5   # Target-specific variation
)
model.train()

# Extract representations
shared = model.get_latent_representation(representation="shared")
target_specific = model.get_latent_representation(representation="target")
```

## CellAssign

**Purpose**: Cell type annotation based on known marker genes.

**Key Features**:
- Utilizes prior knowledge of cell type marker genes.
- Probabilistic assignment of cell types.
- Handles overlap and ambiguity in marker genes.
- Provides soft assignments including uncertainty.

**Use Cases**:
- Annotating cells using known marker genes.
- Leveraging existing biological knowledge for classification.
- Situations where only a marker gene list is available without a reference dataset.

**Basic Usage**:
```python
# Create marker gene matrix (cell types x genes)
marker_gene_mat = pd.DataFrame({
    "CD4 T cells": [1, 1, 0, 0],  # CD3D, CD4, CD8A, CD19
    "CD8 T cells": [1, 0, 1, 0],
    "B cells": [0, 0, 0, 1]
}, index=["CD3D", "CD4", "CD8A", "CD19"])

scvi.model.CELLASSIGN.setup_anndata(adata, layer="counts")
model = scvi.model.CELLASSIGN(adata, marker_gene_mat)
model.train()

predictions = model.predict()
```

## Solo (Doublet Detection)

**Purpose**: Identifying doublets (droplets containing two or more cells) in scRNA-seq data.

**Key Features**:
- Semi-supervised doublet detection using scVI embeddings.
- Simulates artificial doublets for training.
- Provides doublet probability scores.
- Can be applied to any scVI model.

**Use Cases**:
- Quality control of scRNA-seq datasets.
- Removing doublets before downstream analysis.
- Assessing doublet rates in the data.

**Basic Usage**:
```python
# First train an scVI model
scvi.model.SCVI.setup_anndata(adata, layer="counts")
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()

# Train Solo for doublet detection
solo_model = scvi.external.SOLO.from_scvi_model(scvi_model)
solo_model.train()

# Predict doublets
predictions = solo_model.predict()
doublet_scores = predictions["doublet"]
adata.obs["doublet_score"] = doublet_scores
```

## Amortized LDA (Topic Modeling)

**Purpose**: Topic modeling of gene expression using Latent Dirichlet Allocation.

**Key Features**:
- Discovers gene expression programs (topics).
- Employs amortized variational inference for scalability.
- Each cell is treated as a mixture of multiple topics.
- Each topic is a probability distribution over genes.

**Use Cases**:
- Discovering gene programs or expression modules.
- Understanding the compositional structure of expression profiles.
- As an alternative dimensionality reduction method.
- Interpretable decomposition of expression patterns.

**Basic Usage**:
```python
scvi.model.AMORTIZEDLDA.setup_anndata(adata, layer="counts")
model = scvi.model.AMORTIZEDLDA(adata, n_topics=10)
model.train()

# Get topic proportions for each cell
topic_proportions = model.get_latent_representation()

# Get gene loadings for each topic
topic_gene_loadings = model.get_topic_distribution()
```

## Model Selection Guide

**Choose scVI when**:
- Starting unsupervised analysis.
- Batch correction and integration are needed.
- Normalized expression and differential expression analysis are required.

**Choose scANVI when**:
- You have partially labeled cells for training.
- Cell type annotation is needed.
- You want to transfer labels from a reference set to a query set.

**Choose AUTOZI when**:
- Concerned about the impact of technical dropouts.
- Need to identify zero-inflated genes.
- Working with very sparse datasets.

**Choose VeloVI when**:
- You have spliced/unspliced count data.
- Interested in cellular dynamics.
- Need RNA velocity analysis with batch correction.

**Choose contrastiveVI when**:
- Analyzing intervention experiments.
- Need to isolate treatment effects.
- Want to identify condition-specific gene programs.

**Choose CellAssign when**:
- You have a list of marker genes.
- Want probabilistic annotation based on marker genes.
- No reference dataset is available.

**Choose Solo when**:
- Need to detect doublets.
- Already using scVI for analysis.
- Want to obtain probabilistic doublet scores.