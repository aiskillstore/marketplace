# Specialized Modality Models

This document introduces models in scvi-tools designed for specialized single-cell data modalities.

## MethylVI / MethylANVI (Methylation Analysis)

**Purpose**: For single-cell bisulfite sequencing (scBS-seq) data analysis of DNA methylation.

**Core Features**:
- Modeling methylation patterns at single-cell resolution
- Handling sparsity in methylation data
- Batch correction for methylation experiments
- Label transfer for cell type annotation (MethylANVI)

**Applicable Scenarios**:
- Analyzing scBS-seq or similar methylation data
- Studying DNA methylation patterns across cell types
- Integrating methylation data across batches
- Cell type annotation based on methylation profiles

**Data Requirements**:
- Methylation count matrix (methylated reads vs. total reads per CpG site)
- Format: cells × CpG sites, containing methylation proportions or counts

### MethylVI (Unsupervised)

**Basic Usage**:
```python
import scvi

# Setup methylation data
scvi.model.METHYLVI.setup_anndata(
    adata,
    layer="methylation_counts",  # Methylation data
    batch_key="batch"
)

model = scvi.model.METHYLVI(adata)
model.train()

# Get latent representation
latent = model.get_latent_representation()

# Get normalized methylation values
normalized_meth = model.get_normalized_methylation()
```

### MethylANVI (Semi-supervised with Cell Types)

**Basic Usage**:
```python
# Setup with cell type labels
scvi.model.METHYLANVI.setup_anndata(
    adata,
    layer="methylation_counts",
    batch_key="batch",
    labels_key="cell_type",
    unlabeled_category="Unknown"
)

model = scvi.model.METHYLANVI(adata)
model.train()

# Predict cell types
predictions = model.predict()
```

**Key Parameters**:
- `n_latent`: Latent dimension
- `region_factors`: Modeling region-specific effects

**Application Cases**:
- Epigenetic heterogeneity analysis
- Cell type identification via methylation
- Integration with gene expression data (independent analysis)
- Differential methylation analysis

## CytoVI (Flow and Mass Cytometry)

**Purpose**: Batch correction and integration of flow cytometry and mass cytometry (CyTOF) data.

**Core Features**:
- Handling antibody-based protein measurements
- Correcting batch effects in cytometry data
- Supporting integration across experiments
- Designed specifically for high-dimensional protein panels

**Applicable Scenarios**:
- Analyzing flow cytometry or CyTOF data
- Integrating cytometry experiments across batches
- Batch correction of protein panels
- Integrating cytometry data across studies

**Data Requirements**:
- Protein expression matrix (cells × proteins)
- Flow cytometry or CyTOF measurements
- Batch/experiment annotations

**Basic Usage**:
```python
scvi.model.CYTOVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein_expression",
    batch_key="batch"
)

model = scvi.model.CYTOVI(adata)
model.train()

# Get batch-corrected representation
latent = model.get_latent_representation()

# Get normalized protein values
normalized = model.get_normalized_expression()
```

**Key Parameters**:
- `n_latent`: Latent space dimension
- `n_layers`: Network depth

**Typical Workflow**:
```python
import scanpy as sc

# 1. Load cytometry data
adata = sc.read_h5ad("cytof_data.h5ad")

# 2. Train CytoVI
scvi.model.CYTOVI.setup_anndata(
    adata,
    protein_expression_obsm_key="protein",
    batch_key="experiment"
)
model = scvi.model.CYTOVI(adata)
model.train()

# 3. Get batch-corrected values
latent = model.get_latent_representation()
adata.obsm["X_CytoVI"] = latent

# 4. Downstream analysis
sc.pp.neighbors(adata, use_rep="X_CytoVI")
sc.tl.umap(adata)
sc.tl.leiden(adata)

# 5. Visualize batch correction effect
sc.pl.umap(adata, color=["batch", "leiden"])
```

## SysVI (System-level Integration)

**Purpose**: Batch effect correction focused on preserving biological variation.

**Core Features**:
- Specialized batch integration method
- Preserving biological signals while removing technical effects
- Designed for large-scale integration studies

**Applicable Scenarios**:
- Large-scale multi-batch integration
- Need to preserve subtle biological variation
- System-level analysis across multiple studies

**Basic Usage**:
```python
scvi.model.SYSVI.setup_anndata(
    adata,
    layer="counts",
    batch_key="batch"
)

model = scvi.model.SYSVI(adata)
model.train()

latent = model.get_latent_representation()
```

## Decipher (Trajectory Inference)

**Purpose**: Trajectory inference and pseudotime analysis of single-cell data.

**Core Features**:
- Learning cell trajectories and differentiation paths
- Pseudotime estimation
- Accounting for uncertainty in trajectory structure
- Compatible with scVI embeddings

**Applicable Scenarios**:
- Studying cell differentiation
- Time-series or developmental datasets
- Understanding cell state transitions
- Identifying branching points in development

**Basic Usage**:
```python
# Usually used after obtaining embeddings from scVI
scvi_model = scvi.model.SCVI(adata)
scvi_model.train()

# Trajectory analysis using Decipher
scvi.model.DECIPHER.setup_anndata(adata)
decipher_model = scvi.model.DECIPHER(adata, scvi_model)
decipher_model.train()

# Get pseudotime
pseudotime = decipher_model.get_pseudotime()
adata.obs["pseudotime"] = pseudotime
```

**Visualization**:
```python
import scanpy as sc

# Plot pseudotime on UMAP
sc.pl.umap(adata, color="pseudotime", cmap="viridis")

# Gene expression along pseudotime
sc.pl.scatter(adata, x="pseudotime", y="gene_of_interest")
```

## peRegLM (Peak Regulatory Linear Model)

**Purpose**: Linking chromatin accessibility to gene expression for regulatory analysis.

**Core Features**:
- Linking ATAC-seq peaks to gene expression
- Identifying regulatory relationships
- Applicable to paired multiome data

**Applicable Scenarios**:
- Multiome data (RNA + ATAC from the same cells)
- Understanding gene regulation
- Linking peaks to target genes
- Regulatory network construction

**Basic Usage**:
```python
# Requires paired RNA + ATAC data
scvi.model.PEREGLM.setup_anndata(
    multiome_adata,
    rna_layer="counts",
    atac_layer="atac_counts"
)

model = scvi.model.PEREGLM(multiome_adata)
model.train()

# Get peak-gene links
peak_gene_links = model.get_regulatory_links()
```

## Model-Specific Best Practices

### MethylVI/MethylANVI
1. **Sparsity**: Methylation data is inherently sparse; the model accounts for this.
2. **CpG Selection**: Filter CpG sites with extremely low coverage.
3. **Biological Interpretation**: Consider genomic context (promoters, enhancers).
4. **Integration**: For multiomics, analyze separately first and then integrate results.

### CytoVI
1. **Protein Quality Control (QC)**: Remove low-quality or uninformative proteins.
2. **Compensation**: Ensure proper fluorescence compensation before analysis.
3. **Batch Design**: Include biological and technical replicates.
4. **Controls**: Use control samples to validate batch correction effects.

### SysVI
1. **Sample Size**: Designed for large-scale integration.
2. **Batch Definition**: Carefully define the batch structure.
3. **Biological Validation**: Verify that biological signals are preserved.

### Decipher
1. **Starting Point**: Define the trajectory starting cells if known.
2. **Branching**: Specify the expected number of branches.
3. **Validation**: Validate pseudotime using known markers.
4. **Integration**: Works well with scVI embeddings.

## Integration with Other Models

Many specialized models can be used in combination:

**Methylation + Expression**:
```python
# Analyze separately, then integrate
methylvi_model = scvi.model.METHYLVI(meth_adata)
scvi_model = scvi.model.SCVI(rna_adata)

# Integrate results at the analysis level
# For example, correlating methylation and expression patterns
```

**Cytometry + CITE-seq**:
```python
# Use CytoVI for flow/CyTOF
cyto_model = scvi.model.CYTOVI(cyto_adata)

# Use totalVI for CITE-seq
cite_model = scvi.model.TOTALVI(cite_adata)

# Compare protein measurements across platforms
```

**ATAC + RNA (Multiome)**:
```python
# Use MultiVI for joint analysis
multivi_model = scvi.model.MULTIVI(multiome_adata)

# Use peRegLM for regulatory links
pereglm_model = scvi.model.PEREGLM(multiome_adata)
```

## Choosing a Specialized Model

### Decision Tree

1. **What is the data modality?**
   - Methylation → MethylVI/MethylANVI
   - Flow/CyTOF → CytoVI
   - Trajectory → Decipher
   - Multi-batch integration → SysVI
   - Regulatory links → peRegLM

2. **Are there labels?**
   - Yes → MethylANVI (Methylation)
   - No → MethylVI (Methylation)

3. **What is the primary goal?**
   - Batch correction → CytoVI, SysVI
   - Trajectory/Pseudotime → Decipher
   - Peak-gene links → peRegLM
   - Methylation patterns → MethylVI/ANVI

## Example: Complete Methylation Analysis

```python
import scvi
import scanpy as sc

# 1. Load methylation data
meth_adata = sc.read_h5ad("methylation_data.h5ad")

# 2. QC: Filter low-coverage CpG sites
sc.pp.filter_genes(meth_adata, min_cells=10)

# 3. Setup MethylVI
scvi.model.METHYLVI.setup_anndata(
    meth_adata,
    layer="methylation",
    batch_key="batch"
)

# 4. Train model
model = scvi.model.METHYLVI(meth_adata, n_latent=15)
model.train(max_epochs=400)

# 5. Get latent representation
latent = model.get_latent_representation()
meth_adata.obsm["X_MethylVI"] = latent

# 6. Clustering
sc.pp.neighbors(meth_adata, use_rep="X_MethylVI")
sc.tl.umap(meth_adata)
sc.tl.leiden(meth_adata)

# 7. Differential methylation
dm_results = model.differential_methylation(
    groupby="leiden",
    group1="0",
    group2="1"
)

# 8. Save
model.save("methylvi_model")
meth_adata.write("methylation_analyzed.h5ad")
```

## External Tool Integration

Some specialized models are provided as external packages:

**SOLO** (Doublet detection):
```python
from scvi.external import SOLO

solo = SOLO.from_scvi_model(scvi_model)
solo.train()
doublets = solo.predict()
```

**scArches** (Reference mapping):
```python
from scvi.external import SCARCHES

# Used for transfer learning and mapping query samples to reference samples
```

These external tools extend the functionality of scvi-tools in specific scenarios.

## Summary Table

| Model | Data Type | Primary Use | Supervised? |
|-------|-----------|-------------|-------------|
| MethylVI | Methylation | Unsupervised analysis | No |
| MethylANVI | Methylation | Cell type annotation | Semi-supervised |
| CytoVI | Flow Cytometry | Batch correction | No |
| SysVI | scRNA-seq | Large-scale integration | No |
| Decipher | scRNA-seq | Trajectory inference | No |
| peRegLM | Multiome | Peak-gene links | No |
| SOLO | scRNA-seq | Doublet detection | Semi-supervised |