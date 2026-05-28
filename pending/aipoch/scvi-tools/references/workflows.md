# Common Workflows and Best Practices

This document covers common workflows, best practices, and advanced usage patterns for scvi-tools.

## Standard Analysis Workflow

### 1. Data Loading and Preparation

```python
import scvi
import scanpy as sc
import numpy as np

# Load data (requires AnnData format)
adata = sc.read_h5ad("data.h5ad")
# Or load from other formats
# adata = sc.read_10x_mtx("filtered_feature_bc_matrix/")
# adata = sc.read_csv("counts.csv")

# Basic QC metrics calculation
sc.pp.calculate_qc_metrics(adata, inplace=True)
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
```

### 2. Quality Control (QC)

```python
# Filter cells
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, max_genes=5000)

# Filter genes
sc.pp.filter_genes(adata, min_cells=3)

# Filter based on mitochondrial content
adata = adata[adata.obs['pct_counts_mt'] < 20, :]

# Remove doublets (optional, perform before training)
sc.external.pp.scrublet(adata)
adata = adata[~adata.obs['predicted_doublet'], :]
```

### 3. scvi-tools Preprocessing

```python
# IMPORTANT: scvi-tools requires RAW counts
# If you have already performed normalization, please use the raw layer or reload the data

# Save raw counts if not already saved
if 'counts' not in adata.layers:
    adata.layers['counts'] = adata.X.copy()

# Feature selection (optional but recommended)
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=4000,
    subset=False,  # Keep all genes, only mark HVGs
    batch_key="batch"  # If multiple batches exist
)

# Filter to HVGs (optional)
# adata = adata[:, adata.var['highly_variable']]
```

### 4. Registering Data with scvi-tools

```python
# Set up AnnData for scvi-tools
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",  # Use raw counts
    batch_key="batch",  # Technical batch
    categorical_covariate_keys=["donor", "condition"],
    continuous_covariate_keys=["percent_mito", "n_counts"]
)

# Check registration status
adata.uns['_scvi']['summary_stats']
```

### 5. Model Training

```python
# Create model
model = scvi.model.SCVI(
    adata,
    n_latent=30,  # Latent dimension
    n_layers=2,   # Network depth
    n_hidden=128, # Hidden layer size
    dropout_rate=0.1,
    gene_likelihood="zinb"  # Zero-inflated negative binomial
)

# Train model
model.train(
    max_epochs=400,
    batch_size=128,
    train_size=0.9,
    early_stopping=True,
    check_val_every_n_epoch=10
)

# View training history
train_history = model.history["elbo_train"]
val_history = model.history["elbo_validation"]
```

### 6. Extracting Results

```python
# Get latent representation
latent = model.get_latent_representation()
adata.obsm["X_scVI"] = latent

# Get normalized expression
normalized = model.get_normalized_expression(
    adata,
    library_size=1e4,
    n_samples=25  # Number of Monte Carlo samples
)
adata.layers["scvi_normalized"] = normalized
```

### 7. Downstream Analysis

```python
# Cluster on the scVI latent space
sc.pp.neighbors(adata, use_rep="X_scVI", n_neighbors=15)
sc.tl.umap(adata, min_dist=0.3)
sc.tl.leiden(adata, resolution=0.8, key_added="leiden")

# Visualization
sc.pl.umap(adata, color=["leiden", "batch", "cell_type"])

# Differential expression analysis
de_results = model.differential_expression(
    groupby="leiden",
    group1="0",
    group2="1",
    mode="change",
    delta=0.25
)
```

### 8. Model Persistence

```python
# Save model
model_dir = "./scvi_model/"
model.save(model_dir, overwrite=True)

# Save AnnData containing results
adata.write("analyzed_data.h5ad")

# Load model later
model = scvi.model.SCVI.load(model_dir, adata=adata)
```

## Hyperparameter Tuning

### Key Hyperparameters

**Architecture-related**:
- `n_latent`: Latent space dimension (10-50)
  - Use larger values for complex, highly heterogeneous datasets
  - Use smaller values for simple datasets or to prevent overfitting
- `n_layers`: Number of hidden layers (1-3)
  - More layers can be used for complex data, but with diminishing returns
- `n_hidden`: Number of nodes per hidden layer (64-256)
  - Scales with dataset size and complexity

**Training-related**:
- `max_epochs`: Number of training iterations (200-500)
  - Use early stopping to prevent overfitting
- `batch_size`: Samples per batch (64-256)
  - Use larger values for large datasets; use smaller values if VRAM is limited
- `lr`: Learning rate (default 0.001, usually works well)

**Model-specific**:
- `gene_likelihood`: Distribution model ("zinb", "nb", "poisson")
  - "zinb" is suitable for sparse data with zero-inflation characteristics
  - "nb" is suitable for data with lower sparsity
- `dispersion`: Gene or gene-batch specificity
  - "gene" for simple scenarios, "gene-batch" for complex batch effects

### Hyperparameter Search Example

```python
from scvi.model import SCVI

# Define search space
latent_dims = [10, 20, 30]
n_layers_options = [1, 2]

best_score = float('-inf')
best_params = None

for n_latent in latent_dims:
    for n_layers in n_layers_options:
        model = SCVI(
            adata,
            n_latent=n_latent,
            n_layers=n_layers
        )
        model.train(max_epochs=200)

        # Evaluate on validation set
        val_elbo = model.history["elbo_validation"][-1]

        if val_elbo > best_score:
            best_score = val_elbo
            best_params = {"n_latent": n_latent, "n_layers": n_layers}

print(f"Best params: {best_params}")
```

### Hyperparameter Optimization with Optuna

```python
import optuna

def objective(trial):
    n_latent = trial.suggest_int("n_latent", 10, 50)
    n_layers = trial.suggest_int("n_layers", 1, 3)
    n_hidden = trial.suggest_categorical("n_hidden", [64, 128, 256])

    model = scvi.model.SCVI(
        adata,
        n_latent=n_latent,
        n_layers=n_layers,
        n_hidden=n_hidden
    )

    model.train(max_epochs=200, early_stopping=True)
    return model.history["elbo_validation"][-1]

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=20)

print(f"Best parameters: {study.best_params}")
```

## GPU Acceleration

### Enabling GPU Training

```python
# Automatic GPU detection
model = scvi.model.SCVI(adata)
model.train(accelerator="auto")  # Uses GPU if available

# Force GPU usage
model.train(accelerator="gpu")

# Multi-GPU training
model.train(accelerator="gpu", devices=2)

# Check if GPU is being used
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
```

### GPU Memory Management

```python
# If OOM (Out of Memory) occurs, reduce batch size
model.train(batch_size=64)  # instead of the default 128

# Mixed precision training (saves memory)
model.train(precision=16)

# Clear cache between different runs
import torch
torch.cuda.empty_cache()
```

## Batch Integration Strategies

### Strategy 1: Simple Batch Key

```python
# Used for standard batch correction
scvi.model.SCVI.setup_anndata(adata, batch_key="batch")
model = scvi.model.SCVI(adata)
```

### Strategy 2: Multiple Covariates

```python
# Correct for multiple technical factors
scvi.model.SCVI.setup_anndata(
    adata,
    batch_key="sequencing_batch",
    categorical_covariate_keys=["donor", "tissue"],
    continuous_covariate_keys=["percent_mito"]
)
```

### Strategy 3: Hierarchical Batches

```python
# When batches have a hierarchical structure
# e.g., samples within research projects
adata.obs["batch_hierarchy"] = (
    adata.obs["study"].astype(str) + "_" +
    adata.obs["sample"].astype(str)
)

scvi.model.SCVI.setup_anndata(adata, batch_key="batch_hierarchy")
```

## Reference Mapping (scArches)

### Training a Reference Model

```python
# Train on reference dataset
scvi.model.SCVI.setup_anndata(ref_adata, batch_key="batch")
ref_model = scvi.model.SCVI(ref_adata)
ref_model.train()

# Save reference model
ref_model.save("reference_model")
```

### Mapping Query Data to a Reference Model

```python
# Load reference model
ref_model = scvi.model.SCVI.load("reference_model", adata=ref_adata)

# Set up query data with the same parameters
scvi.model.SCVI.setup_anndata(query_adata, batch_key="batch")

# Transfer learning
query_model = scvi.model.SCVI.load_query_data(
    query_adata,
    "reference_model"
)

# Fine-tune on query data (optional)
query_model.train(max_epochs=200)

# Get query data embeddings
query_latent = query_model.get_latent_representation()

# Label transfer using KNN
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=15)
knn.fit(ref_model.get_latent_representation(), ref_adata.obs["cell_type"])
query_adata.obs["predicted_cell_type"] = knn.predict(query_latent)
```

## Model Minification

Reducing model size for faster inference:

```python
# Train full model
model = scvi.model.SCVI(adata)
model.train()

# Minify data for deployment
minified = model.minify_adata(adata)

# Save minified version
minified.write("minified_data.h5ad")
model.save("minified_model")

# Load and use (faster)
mini_model = scvi.model.SCVI.load("minified_model", adata=minified)
```

## Memory-Efficient Data Loading

### Using AnnDataLoader

```python
from scvi.data import AnnDataLoader

# Suitable for extremely large datasets
dataloader = AnnDataLoader(
    adata,
    batch_size=128,
    shuffle=True,
    drop_last=False
)

# Custom training loop (advanced usage)
for batch in dataloader:
    # Process batch
    pass
```

### Using Backed AnnData

```python
# Suitable for data that cannot fit in memory
adata = sc.read_h5ad("huge_dataset.h5ad", backed='r')

# scvi-tools supports backed mode
scvi.model.SCVI.setup_anndata(adata)
model = scvi.model.SCVI(adata)
model.train()
```

## Model Interpretation

### Feature Importance Analysis with SHAP

```python
import shap

# Get SHAP values for better interpretability
explainer = shap.DeepExplainer(model.module, background_data)
shap_values = explainer.shap_values(test_data)

# Visualization
shap.summary_plot(shap_values, feature_names=adata.var_names)
```

### Gene Correlation Analysis

```python
# Get gene-gene correlation matrix
correlation = model.get_feature_correlation_matrix(
    adata,
    transform_batch="batch1"
)

# Visualize highly correlated genes
import seaborn as sns
sns.heatmap(correlation[:50, :50], cmap="coolwarm")
```

## Troubleshooting Common Issues

### Issue: Loss becomes NaN during training

**Causes**:
- Learning rate is too high
- Input is not normalized (raw counts must be used)
- Data quality issues

**Solutions**:
```python
# Lower the learning rate
model.train(lr=0.0001)

# Check data
assert adata.X.min() >= 0  # No negative values
assert np.isnan(adata.X).sum() == 0  # No NaNs

# Use a more stable likelihood function
model = scvi.model.SCVI(adata, gene_likelihood="nb")
```

### Issue: Poor batch correction

**Solutions**:
```python
# Enhance batch effect modeling
model = scvi.model.SCVI(
    adata,
    encode_covariates=True,  # Encode batches in the encoder
    deeply_inject_covariates=False
)

# Or try the opposite approach
model = scvi.model.SCVI(adata, deeply_inject_covariates=True)

# Use more latent dimensions
model = scvi.model.SCVI(adata, n_latent=50)
```

### Issue: Model not training (ELBO not decreasing)

**Solutions**:
```python
# Increase learning rate
model.train(lr=0.005)

# Increase network capacity
model = scvi.model.SCVI(adata, n_hidden=256, n_layers=2)

# Extend training time
model.train(max_epochs=500)
```

### Issue: Out of Memory (OOM)

**Solutions**:
```python
# Reduce batch size
model.train(batch_size=64)

# Use mixed precision
model.train(precision=16)

# Reduce model scale
model = scvi.model.SCVI(adata, n_latent=10, n_hidden=64)

# Use backed AnnData
adata = sc.read_h5ad("data.h5ad", backed='r')
```

## Performance Benchmarking

```python
import time

# Training timing
start = time.time()
model.train(max_epochs=400)
training_time = time.time() - start
print(f"Training time: {training_time:.2f}s")

# Inference timing
start = time.time()
latent = model.get_latent_representation()
inference_time = time.time() - start
print(f"Inference time: {inference_time:.2f}s")

# Memory usage
import psutil
import os
process = psutil.Process(os.getpid())
memory_gb = process.memory_info().rss / 1024**3
print(f"Memory usage: {memory_gb:.2f} GB")
```

## Summary of Best Practices

1. **Always use raw counts**: Never perform log-normalization before using scvi-tools.
2. **Feature selection**: Use Highly Variable Genes (HVGs) to improve efficiency.
3. **Batch correction**: Register all known technical covariates.
4. **Early stopping**: Utilize the validation set to prevent overfitting.
5. **Model saving**: Always save your trained models.
6. **GPU usage**: Use a GPU for large datasets (>10k cells).
7. **Hyperparameter tuning**: Start with default values and adjust as needed.
8. **Validation**: Check batch correction effects via visualization (e.g., UMAP colored by batch).
9. **Documentation**: Track all preprocessing steps.
10. **Reproducibility**: Set a random seed (`scvi.settings.seed = 0`).