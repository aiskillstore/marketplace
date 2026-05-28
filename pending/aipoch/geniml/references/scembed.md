# scEmbed: Single-cell Embedding Generation

## Overview

scEmbed trains Region2Vec models on single-cell ATAC-seq datasets to generate cell embeddings for clustering and analysis. It provides an unsupervised machine learning framework for representing and analyzing scATAC-seq data in a low-dimensional space.

## Applicable Scenarios

Use scEmbed when processing the following tasks:
- Single-cell ATAC-seq (scATAC-seq) data requiring clustering
- Cell type annotation tasks
- Dimensionality reduction of single-cell chromatin accessibility
- Integration with scanpy workflows for downstream analysis

## Workflow

### Step 1: Data Preparation

Input data must be in AnnData format, with `chr`, `start`, and `end` values for peaks contained in the `.var` attribute.

**Starting from raw data** (barcodes.txt, peaks.bed, matrix.mtx):

```python
import scanpy as sc
import pandas as pd
import scipy.io
import anndata

# Load data
barcodes = pd.read_csv('barcodes.txt', header=None, names=['barcode'])
peaks = pd.read_csv('peaks.bed', sep='\t', header=None,
                    names=['chr', 'start', 'end'])
matrix = scipy.io.mmread('matrix.mtx').tocsr()

# Create AnnData
adata = anndata.AnnData(X=matrix.T, obs=barcodes, var=peaks)
adata.write('scatac_data.h5ad')
```

### Step 2: Pre-tokenization

Use the gtars tool to convert genomic regions into tokens. This creates a parquet file containing tokenized cell information, which speeds up training:

```python
from geniml.io import tokenize_cells

tokenize_cells(
    adata='scatac_data.h5ad',
    universe_file='universe.bed',
    output='tokenized_cells.parquet'
)
```

**Advantages of Pre-tokenization:**
- Faster training iterations
- Reduced memory requirements
- Tokenized data can be reused for multiple training runs

### Step 3: Model Training

Train the scEmbed model using the tokenized data:

```python
from geniml.scembed import ScEmbed
from geniml.region2vec import Region2VecDataset

# Load tokenized dataset
dataset = Region2VecDataset('tokenized_cells.parquet')

# Initialize and train model
model = ScEmbed(
    embedding_dim=100,
    window_size=5,
    negative_samples=5
)

model.train(
    dataset=dataset,
    epochs=100,
    batch_size=256,
    learning_rate=0.025
)

# Save model
model.save('scembed_model/')
```

### Step 4: Generating Cell Embeddings

Use the trained model to generate embeddings for cells:

```python
from geniml.scembed import ScEmbed

# Load trained model
model = ScEmbed.from_pretrained('scembed_model/')

# Generate embeddings for AnnData object
embeddings = model.encode(adata)

# Add to AnnData for downstream analysis
adata.obsm['scembed_X'] = embeddings
```

### Step 5: Downstream Analysis

Integrate with scanpy for clustering and visualization:

```python
import scanpy as sc

# Build neighborhood graph using scEmbed embeddings
sc.pp.neighbors(adata, use_rep='scembed_X')

# Cell clustering
sc.tl.leiden(adata, resolution=0.5)

# Calculate UMAP for visualization
sc.tl.umap(adata)

# Plot results
sc.pl.umap(adata, color='leiden')
```

## Key Parameters

### Training Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `embedding_dim` | Dimension of cell embeddings | 50 - 200 |
| `window_size` | Context window size for training | 3 - 10 |
| `negative_samples` | Number of negative samples | 5 - 20 |
| `epochs` | Number of training epochs | 50 - 200 |
| `batch_size` | Training batch size | 128 - 512 |
| `learning_rate` | Initial learning rate | 0.01 - 0.05 |

### Tokenization Parameters

- **Universe file**: Reference BED file defining the genomic vocabulary
- **Overlap threshold**: Minimum overlap for matching a peak to the universe (typically 1e-9)

## Pre-trained Models

Pre-trained scEmbed models for common reference datasets are available on Hugging Face. Load them using:

```python
from geniml.scembed import ScEmbed

# Load pre-trained model
model = ScEmbed.from_pretrained('databio/scembed-pbmc-10k')

# Generate embeddings
embeddings = model.encode(adata)
```

## Best Practices

- **Data Quality**: Use filtered peak-barcode matrices instead of raw counts.
- **Pre-tokenization**: Always perform pre-tokenization to improve training efficiency.
- **Parameter Tuning**: Adjust `embedding_dim` and `epochs` based on the dataset size.
- **Validation**: Use known cell type markers to validate clustering quality.
- **Integration**: Combine with scanpy for comprehensive single-cell analysis.
- **Model Sharing**: Export trained models to Hugging Face for reproducibility.

## Example Dataset

The 10x Genomics PBMC 10k dataset (10,000 peripheral blood mononuclear cells) is a standard benchmark:
- Contains multiple immune cell types
- Features well-characterized cell populations
- Available from the 10x Genomics official website

## Cell Type Annotation

After clustering, cell type annotation can be performed using the K-Nearest Neighbors (KNN) algorithm in conjunction with a reference dataset:

```python
from geniml.scembed import annotate_celltypes

# Annotate using a reference dataset
annotations = annotate_celltypes(
    query_adata=adata,
    reference_adata=reference,
    embedding_key='scembed_X',
    k=10
)

adata.obs['cell_type'] = annotations
```

## Outputs

scEmbed produces:
- Low-dimensional cell embeddings (stored in `adata.obsm`)
- Reusable trained model files
- Formats compatible with scanpy downstream analysis
- Optional: Export to Hugging Face for sharing