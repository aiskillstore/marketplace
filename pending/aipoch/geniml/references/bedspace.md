# BEDspace: Joint Region and Metadata Embeddings

## Overview

BEDspace applies the StarSpace model to genomic data, enabling the simultaneous training of numerical embeddings for Region Sets and their Metadata Labels in a shared low-dimensional space. This allows for rich query functionality across regions and metadata.

## When to Use

Use BEDspace when dealing with:
- Region sets with associated metadata (cell types, tissues, experimental conditions)
- Search tasks requiring metadata-aware similarity
- Cross-modal queries (e.g., "Find regions similar to label X")
- Joint analysis of genomic content and experimental conditions

## Workflow

BEDspace consists of four sequential operations:

### 1. Preprocess

Format genomic intervals and metadata for StarSpace training:

```bash
geniml bedspace preprocess \
  --input /path/to/regions/ \
  --metadata labels.csv \
  --universe universe.bed \
  --labels "cell_type,tissue" \
  --output preprocessed.txt
```

**Required Files:**
- **Input folder**: Directory containing BED files
- **Metadata CSV**: Must contain a `file_name` column matching the BED filenames, along with metadata columns
- **Universe file**: Reference BED file used for tokenization
- **Labels**: Comma-separated list of metadata columns to use

The preprocessing step adds a `__label__` prefix to metadata and converts regions into a StarSpace-compatible format.

### 2. Train

Perform StarSpace model training on the preprocessed data:

```bash
geniml bedspace train \
  --path-to-starspace /path/to/starspace \
  --input preprocessed.txt \
  --output model/ \
  --dim 100 \
  --epochs 50 \
  --lr 0.05
```

**Key training parameters:**
- `--dim`: Embedding dimension (typically 50-200)
- `--epochs`: Number of training epochs (typically 20-100)
- `--lr`: Learning rate (typically 0.01-0.1)

### 3. Distances

Calculate distance metrics between region sets and metadata labels:

```bash
geniml bedspace distances \
  --input model/ \
  --metadata labels.csv \
  --universe universe.bed \
  --output distances.pkl
```

This step creates the distance matrix required for similarity search.

### 4. Search

Retrieve similar items in three scenarios:

**Region-to-Label (r2l)**: Query region set → Retrieve similar metadata labels
```bash
geniml bedspace search -t r2l -d distances.pkl -q query_regions.bed -n 10
```

**Label-to-Region (l2r)**: Query metadata label → Retrieve similar region sets
```bash
geniml bedspace search -t l2r -d distances.pkl -q "T_cell" -n 10
```

**Region-to-Region (r2r)**: Query region set → Retrieve similar region sets
```bash
geniml bedspace search -t r2r -d distances.pkl -q query_regions.bed -n 10
```

The `-n` parameter controls the number of results returned.

## Python API

```python
from geniml.bedspace import BEDSpaceModel

# Load the trained model
model = BEDSpaceModel.load('model/')

# Query for similar items
results = model.search(
    query="T_cell",
    search_type="l2r",
    top_k=10
)
```

## Best Practices

- **Metadata Structure**: Ensure the metadata CSV contains a `file_name` column that exactly matches the BED filenames (without paths).
- **Label Selection**: Choose metadata columns that are informative and capture the biological variation of interest.
- **Universe Consistency**: Use the same universe file for preprocessing, distance calculation, and any subsequent analysis.
- **Validation**: Preprocess and check the output format before investing significant time in training.
- **StarSpace Installation**: StarSpace must be installed separately as it is an external dependency.

## Output Interpretation

Search results are ranked by similarity in the joint embedding space:
- **r2l**: Identifies metadata labels that characterize your query regions.
- **l2r**: Finds region sets that match your metadata criteria.
- **r2r**: Discovers region sets with similar genomic content.

## Requirements

BEDspace requires a separate installation of StarSpace. Please download it from here: https://github.com/facebookresearch/StarSpace