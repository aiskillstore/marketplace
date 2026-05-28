---
name: scvi-tools
description: Deep generative models for single-cell omics; use when you need probabilistic batch correction (scVI), transfer learning, uncertainty-aware differential expression, or multimodal integration (totalVI/MultiVI).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use **scvi-tools** when you need probabilistic, model-based single-cell analysis beyond standard pipelines (e.g., beyond typical Scanpy workflows), such as:

1. **Batch correction and dataset integration** for scRNA-seq using a probabilistic latent space (e.g., scVI).
2. **Transfer learning / semi-supervised annotation** when you have partial labels or want to map new data onto a reference (e.g., scANVI).
3. **Uncertainty-aware differential expression** where effect sizes and posterior uncertainty matter (Bayesian DE).
4. **Multimodal integration** across RNA+protein (CITE-seq) or RNA+ATAC (multiome), including paired/unpaired settings (e.g., totalVI, MultiVI).
5. **Specialized modalities** such as ATAC-seq, spatial transcriptomics deconvolution/mapping, doublet detection, methylation, or RNA velocity.

## Key Features

- **Unified model API**: `setup_anndata(...) → Model(adata) → train() → get_*()` across model families.
- **Probabilistic latent representations** for integration, denoising, and downstream clustering/visualization.
- **Explicit covariate handling** (batch, donor, technical factors) via `setup_anndata`.
- **Bayesian differential expression** with posterior-based hypothesis testing and effect-size thresholds.
- **Multi-omics models** for joint learning across modalities (RNA/protein, RNA/ATAC; paired or unpaired).
- **AnnData-first integration** with the Scanpy ecosystem for downstream neighbors/UMAP/clustering.
- **GPU acceleration** via PyTorch (when available).

Model catalogs by modality (for reference):
- scRNA-seq: `references/models-scrna-seq.md` (scVI, scANVI, AUTOZI, VeloVI, contrastiveVI, …)
- ATAC-seq: `references/models-atac-seq.md` (PeakVI, PoissonVI, scBasset, …)
- Multimodal: `references/models-multimodal.md` (totalVI, MultiVI, MrVI, …)
- Spatial: `references/models-spatial.md` (DestVI, Stereoscope, Tangram, scVIVA, …)
- Specialized: `references/models-specialized.md` (Solo, CellAssign, MethylVI/MethylANVI, CytoVI, …)

## Dependencies

- `scvi-tools` (latest compatible with your environment)
- `python>=3.9`
- `pytorch>=2.0`
- `pytorch-lightning>=2.0` (or `lightning` depending on scvi-tools version)
- `anndata>=0.8`
- `scanpy>=1.9`

Installation example:

```bash
uv pip install scvi-tools
# Optional GPU extras (package extra name may vary by platform/version)
uv pip install "scvi-tools[cuda]"
```

## Example Usage

A complete runnable example using **scVI** for batch correction + latent embedding, then Scanpy for neighbors/UMAP/clustering:

```python
import scanpy as sc
import scvi

# 1) Load example data (AnnData)
adata = scvi.data.heart_cell_atlas_subsampled()

# 2) Minimal preprocessing (keep raw counts available)
sc.pp.filter_genes(adata, min_counts=3)
sc.pp.highly_variable_genes(adata, n_top_genes=1200)

# 3) Register AnnData for scVI (raw counts + covariates)
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",                 # raw counts layer (not log-normalized)
    batch_key="batch",              # batch column in adata.obs
    categorical_covariate_keys=["donor"],
    continuous_covariate_keys=["percent_mito"],
)

# 4) Train model
model = scvi.model.SCVI(adata)
model.train()

# 5) Extract outputs
adata.obsm["X_scVI"] = model.get_latent_representation()
adata.layers["scvi_normalized"] = model.get_normalized_expression(library_size=1e4)

# 6) Downstream analysis with Scanpy
sc.pp.neighbors(adata, use_rep="X_scVI")
sc.tl.umap(adata)
sc.tl.leiden(adata)

# Optional: uncertainty-aware differential expression
de = model.differential_expression(
    groupby="cell_type",
    group1="TypeA",
    group2="TypeB",
    mode="change",
    delta=0.25,
)
print(de.head())
```

Model persistence:

```python
model.save("./scvi_model", overwrite=True)
model2 = scvi.model.SCVI.load("./scvi_model", adata=adata)
```

## Implementation Details

- **Core approach**: deep generative modeling with **variational inference** (typically VAE-style architectures) to learn a latent representation and a likelihood model for counts.
- **Data requirements**: models generally expect **raw counts** (not log-normalized values). Provide counts via `layer="counts"` or ensure `adata.X` contains counts.
- **Covariate registration**: technical factors (e.g., `batch_key`, donor, QC metrics) are incorporated through `setup_anndata`, enabling the model to learn representations that reduce unwanted variation.
- **Training loop**: `train()` performs amortized inference using neural networks shared across cells; GPU acceleration is used automatically when configured.
- **Latent space usage**: `get_latent_representation()` returns batch-corrected embeddings suitable for neighbors/UMAP/clustering in Scanpy.
- **Differential expression**: `differential_expression(...)` performs posterior-based comparisons; parameters like:
  - `mode="change"`: composite hypothesis testing on changes
  - `delta`: minimum effect size threshold  
  help control practical significance and uncertainty-aware decisions.  
  See `references/differential-expression.md` for interpretation guidance.
- **Model selection by modality**: choose the model family based on data type (e.g., scVI/scANVI for scRNA-seq, totalVI for CITE-seq, MultiVI for RNA+ATAC, DestVI for spatial deconvolution). For details, see the corresponding `references/models-*.md` files.
- **Theory background**: variational inference, amortized inference, and probabilistic modeling foundations are summarized in `references/theoretical-foundations.md`.