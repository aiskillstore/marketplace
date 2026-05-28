# Geniml Utilities and Additional Tools

## BBClient: BED File Caching

### Overview

BBClient provides indexing functionality for caching BED files from remote sources, enabling faster repeated access and integration with R workflows.

### Use Cases

Use BBClient when:
- You need repeated access to BED files from remote databases
- You are working with BEDbase repositories
- You are integrating genomic data into R pipelines
- Local caching is required for performance reasons

### Python Usage

```python
from geniml.bbclient import BBClient

# Initialize the client
client = BBClient(cache_folder='~/.bedcache')

# Fetch and cache a BED file
bed_file = client.load_bed(bed_id='GSM123456')

# Access the cached file
regions = client.get_regions('GSM123456')
```

### R Integration

```r
library(reticulate)
geniml <- import("geniml.bbclient")

# Initialize the client
client <- geniml$BBClient(cache_folder='~/.bedcache')

# Load a BED file
bed_file <- client$load_bed(bed_id='GSM123456')
```

### Best Practices

- Configure a cache directory with sufficient storage space
- Use consistent cache locations across different analyses
- Periodically clean the cache to remove unused files

---

## BEDshift: BED File Randomization

### Overview

BEDshift provides tools for randomizing BED files while preserving genomic context, which is essential for generating null distributions and performing statistical tests.

### Use Cases

Use BEDshift when:
- Creating null models for statistical testing
- Generating control datasets
- Assessing the significance of genomic overlaps
- Benchmarking analytical methods

### Usage

```python
from geniml.bedshift import bedshift

# Randomize a BED file while preserving chromosome distribution
randomized = bedshift(
    input_bed='peaks.bed',
    genome='hg38',
    preserve_chrom=True,
    n_iterations=100
)
```

### CLI Usage

```bash
geniml bedshift \
  --input peaks.bed \
  --genome hg38 \
  --preserve-chrom \
  --iterations 100 \
  --output randomized_peaks.bed
```

### Randomization Strategies

**Preserve Chromosome Distribution:**
```python
bedshift(input_bed, genome, preserve_chrom=True)
```
Keeps regions on the same chromosome as the original file.

**Preserve Distance Distribution:**
```python
bedshift(input_bed, genome, preserve_distance=True)
```
Maintains the distances between regions.

**Preserve Region Size:**
```python
bedshift(input_bed, genome, preserve_size=True)
```
Maintains the lengths of the original regions.

### Best Practices

- Choose a randomization strategy that matches your null hypothesis
- Generate multiple iterations for robust statistical results
- Verify that the randomized output maintains the desired properties
- Document randomization parameters to ensure reproducibility

---

## Evaluation: Model Evaluation Tools

### Overview

Geniml provides evaluation utilities for assessing embedding quality and model performance.

### Use Cases

Use evaluation tools when:
- Validating trained embeddings
- Comparing different models
- Assessing clustering quality
- Publishing model results

### Embedding Evaluation

```python
from geniml.evaluation import evaluate_embeddings

# Evaluate Region2Vec embeddings
metrics = evaluate_embeddings(
    embeddings_file='region2vec_model/embeddings.npy',
    labels_file='metadata.csv',
    metrics=['silhouette', 'davies_bouldin', 'calinski_harabasz']
)

print(f"Silhouette score: {metrics['silhouette']:.3f}")
print(f"Davies-Bouldin index: {metrics['davies_bouldin']:.3f}")
```

### Clustering Metrics

**Silhouette Score:** Measures cluster cohesion and separation (-1 to 1, higher is better).

**Davies-Bouldin Index:** Average similarity between clusters (≥0, lower is better).

**Calinski-Harabasz Score:** The ratio of between-group dispersion to within-group dispersion (higher is better).

### scEmbed Cell Type Annotation Evaluation

```python
from geniml.evaluation import evaluate_annotation

# Evaluate cell type predictions
results = evaluate_annotation(
    predicted=adata.obs['predicted_celltype'],
    true=adata.obs['true_celltype'],
    metrics=['accuracy', 'f1', 'confusion_matrix']
)

print(f"Accuracy: {results['accuracy']:.1%}")
print(f"F1 score: {results['f1']:.3f}")
```

### Best Practices

- Use multiple complementary metrics
- Compare against baseline models
- Report metrics on held-out test data
- Visualize embeddings (UMAP/t-SNE) alongside metrics

---

## Tokenization: Region Tokenization Utilities

### Overview

Tokenization converts genomic regions into discrete tokens using a reference universe, enabling word2vec-style training.

### Use Cases

Tokenization is a required preprocessing step for:
- Region2Vec training
- scEmbed model training
- Any embedding method requiring discrete tokens

### Hard Tokenization

Tokenization based strictly on overlap:

```python
from geniml.tokenization import hard_tokenization

hard_tokenization(
    src_folder='bed_files/',
    dst_folder='tokenized/',
    universe_file='universe.bed',
    p_value_threshold=1e-9
)
```

**Parameters:**
- `p_value_threshold`: Significance level for overlap (typically 1e-9 or 1e-6)

### Soft Tokenization

Probabilistic tokenization allowing partial matches:

```python
from geniml.tokenization import soft_tokenization

soft_tokenization(
    src_folder='bed_files/',
    dst_folder='tokenized/',
    universe_file='universe.bed',
    overlap_threshold=0.5
)
```

**Parameters:**
- `overlap_threshold`: Minimum overlap proportion (0-1)

### Universe-Based Tokenization

Maps regions to universe tokens using custom parameters:

```python
from geniml.tokenization import universe_tokenization

universe_tokenization(
    bed_file='peaks.bed',
    universe_file='universe.bed',
    output_file='tokens.txt',
    method='hard',
    threshold=1e-9
)
```

### Best Practices

- **Universe Quality**: Use comprehensive and well-constructed universes.
- **Threshold Selection**: Choose stricter (lower p-value) thresholds for higher confidence.
- **Validation**: Check tokenization coverage (percentage of regions successfully tokenized).
- **Consistency**: Use the same universe and parameters across related analyses.

### Tokenization Coverage

Check how well regions are tokenized:

```python
from geniml.tokenization import check_coverage

coverage = check_coverage(
    bed_file='peaks.bed',
    universe_file='universe.bed',
    threshold=1e-9
)

print(f"Tokenization coverage: {coverage:.1%}")
```

Aim for coverage >80% for reliable training.

---

## Text2BedNN: Search Backend

### Overview

Text2BedNN creates neural network-based search backends for querying genomic regions using natural language or metadata.

### Use Cases

Use Text2BedNN when:
- Building search interfaces for genomic databases
- Enabling natural language queries for BED files
- Creating metadata-aware search systems
- Deploying interactive genomic search applications

### Workflow

**Step 1: Prepare Embeddings**

Train a BEDspace or Region2Vec model using metadata.

**Step 2: Build Search Index**

```python
from geniml.search import build_search_index

build_search_index(
    embeddings_file='bedspace_model/embeddings.npy',
    metadata_file='metadata.csv',
    output_dir='search_backend/'
)
```

**Step 3: Query the Index**

```python
from geniml.search import SearchBackend

backend = SearchBackend.load('search_backend/')

# Natural language query
results = backend.query(
    text="T cell regulatory regions",
    top_k=10
)

# Metadata query
results = backend.query(
    metadata={'cell_type': 'T_cell', 'tissue': 'blood'},
    top_k=10
)
```

### Best Practices

- Train embeddings with rich metadata for better search performance
- Index large collections for comprehensive coverage
- Validate search relevance on known queries
- Deploy with an API to support interactive applications

---

## Additional Tools

### I/O Utilities

```python
from geniml.io import read_bed, write_bed, load_universe

# Read a BED file
regions = read_bed('peaks.bed')

# Write a BED file
write_bed(regions, 'output.bed')

# Load a universe
universe = load_universe('universe.bed')
```

### Model Utilities

```python
from geniml.models import save_model, load_model

# Save a trained model
save_model(model, 'my_model/')

# Load a model
model = load_model('my_model/')
```

### Common Patterns

**Pipeline Workflow:**
```python
# 1. Build universe
universe = build_universe(coverage_folder='coverage/', method='cc', cutoff=5)

# 2. Tokenization
hard_tokenization(src_folder='beds/', dst_folder='tokens/',
                   universe_file='universe.bed', p_value_threshold=1e-9)

# 3. Train embeddings
region2vec(token_folder='tokens/', save_dir='model/', num_shufflings=1000)

# 4. Evaluation
metrics = evaluate_embeddings(embeddings_file='model/embeddings.npy',
                               labels_file='metadata.csv')
```

This modular design allows for flexible combination of geniml tools for various genomic machine learning workflows.