# Best Practices

Guide to using AnnData efficiently and effectively.

## Memory Management

### Use Sparse Matrices for Sparse Data
```python
import numpy as np
from scipy.sparse import csr_matrix
import anndata as ad

# Check data sparsity
data = np.random.rand(1000, 2000)
sparsity = 1 - np.count_nonzero(data) / data.size
print(f"Sparsity: {sparsity:.2%}")

# Convert if >50% zeros
if sparsity > 0.5:
    adata = ad.AnnData(X=csr_matrix(data))
else:
    adata = ad.AnnData(X=data)

# Benefit: 10-100x less memory for sparse genomics data
```

### Convert Strings to Categoricals
```python
# Inefficient: String column uses much memory
adata.obs['cell_type'] = ['Type_A', 'Type_B', 'Type_C'] * 333 + ['Type_A']

# Efficient: Convert to categorical
adata.obs['cell_type'] = adata.obs['cell_type'].astype('category')

# Convert all string columns
adata.strings_to_categoricals()

# Benefit: 10-50x less memory for repetitive strings
```

### Use Backed Mode for Large Datasets
```python
# Don't load everything into RAM
adata = ad.read_h5ad('large_dataset.h5ad', backed='r')

# Work with metadata
filtered = adata[adata.obs['quality'] > 0.8]

# Load only subset
adata_subset = filtered.to_memory()

# Benefit: Work with datasets larger than RAM
```

## Views vs Copies

### Understanding Views
```python
# Slicing creates a view by default
subset = adata[0:100, :]
print(subset.is_view)  # True

# Views don't duplicate data (memory efficient)
# But modifications can affect original

# Check if view
if adata.is_view:
    adata = adata.copy()  # Make independent copy
```

### When to Use Views
```python
# Recommended: Read-only operations on subsets
mean_expr = adata[adata.obs['cell_type'] == 'T cell'].X.mean()

# Recommended: Temporary analysis
temp_subset = adata[:100, :]
result = analyze(temp_subset.X)
```

### When to Use Copies
```python
# Create independent copy for modification
adata_filtered = adata[keep_cells, :].copy()

# Safe to modify without affecting original
adata_filtered.obs['new_column'] = values

# Always copy when:
# - Storing a subset for later use
# - Modifying data in a subset
# - Passing subset to functions that modify data
```

## Storage Best Practices

### Choosing Format

**H5AD (HDF5) - Default Choice**
```python
adata.write_h5ad('data.h5ad', compression='gzip')
```
- Fast random access
- Supports backed mode
- Good compression
- Use for: Most cases

**Zarr - Cloud & Parallel Access**
```python
adata.write_zarr('data.zarr', chunks=(100, 100))
```
- Great for cloud storage (S3, GCS)
- Parallel I/O supported
- Good compression
- Use for: Very large datasets, cloud workflows, parallel processing

**CSV - Interoperability**
```python
adata.write_csvs('output_dir/')
```
- Human readable
- Compatible with everything
- Large file size, slow
- Use for: Sharing with non-Python tools, small datasets

### Optimizing File Size
```python
# Before saving:

# 1. Convert to sparse if appropriate
from scipy.sparse import csr_matrix, issparse
if not issparse(adata.X):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:
        adata.X = csr_matrix(adata.X)

# 2. Convert strings to categoricals
adata.strings_to_categoricals()

# 3. Use compression
adata.write_h5ad('data.h5ad', compression='gzip', compression_opts=9)

# Typical result: 5-20x smaller files
```

## Backed Mode Strategies

### Read-Only Analysis
```python
# Open in read-only backed mode
adata = ad.read_h5ad('data.h5ad', backed='r')

# Filter without loading data
high_quality = adata[adata.obs['quality_score'] > 0.8]

# Load only filtered data
adata_filtered = high_quality.to_memory()
```

### Read-Write Modification
```python
# Open in read-write backed mode
adata = ad.read_h5ad('data.h5ad', backed='r+')

# Modify metadata (writes directly to disk)
adata.obs['new_annotation'] = values

# X remains on disk, modifications saved immediately
```

### Chunked Processing
```python
# Process huge datasets in chunks
adata = ad.read_h5ad('huge_dataset.h5ad', backed='r')

results = []
chunk_size = 1000

for i in range(0, adata.n_obs, chunk_size):
    chunk = adata[i:i+chunk_size, :].to_memory()
    result = process(chunk)
    results.append(result)

final_result = combine(results)
```

## Performance Optimization

### Slicing Performance
```python
# Fast: Boolean indexing with array
mask = np.array(adata.obs['quality'] > 0.5)
subset = adata[mask, :]

# Slow: Boolean indexing with Series (creates view chain)
subset = adata[adata.obs['quality'] > 0.5, :]

# Fastest: Integer indexing
indices = np.where(adata.obs['quality'] > 0.5)[0]
subset = adata[indices, :]
```

### Avoid Repeated Slicing
```python
# Inefficient: Multiple slices
for cell_type in ['A', 'B', 'C']:
    subset = adata[adata.obs['cell_type'] == cell_type]
    process(subset)

# Efficient: Groupby then process
groups = adata.obs.groupby('cell_type').groups
for cell_type, indices in groups.items():
    subset = adata[indices, :]
    process(subset)
```

### Chunked Operations on Large Matrices
```python
# Process X in chunks
for chunk in adata.chunked_X(chunk_size=1000):
    result = compute(chunk)

# Memory efficient compared to loading full X
```

## Handling Raw Data

### Storing Raw Data Before Filtering
```python
# Full dataset
adata = ad.AnnData(X=counts)

# Store as raw before filtering
adata.raw = adata.copy()

# Filter to highly variable genes
adata = adata[:, adata.var['highly_variable']]

# Later: Access original data
original_expression = adata.raw.X
all_genes = adata.raw.var_names
```

### When to Use Raw
```python
# Use raw for:
# - Differential expression on filtered genes
# - Visualization of specific genes not in filtered set
# - Accessing original counts after normalization

# Accessing raw data
if adata.raw is not None:
    gene_expr = adata.raw[:, 'GENE_NAME'].X
else:
    gene_expr = adata[:, 'GENE_NAME'].X
```

## Metadata Management

### Naming Conventions
```python
# Consistent naming improves usability

# Observations (obs):
# - cell_id, sample_id
# - cell_type, tissue, condition
# - n_genes, n_counts, percent_mito
# - cluster, leiden, louvain

# Variables (var):
# - gene_id, gene_name
# - highly_variable, n_cells
# - mean_expression, dispersion

# Embeddings (obsm):
# - X_pca, X_umap, X_tsne
# - X_diffmap, X_draw_graph_fr

# Follows scanpy/scverse ecosystem conventions
```

### Documenting Metadata
```python
# Store descriptions in uns
adata.uns['metadata_descriptions'] = {
    'cell_type': 'Cell type annotation from automated clustering',
    'quality_score': 'QC score from scrublet (0-1, higher is better)',
    'batch': 'Experimental batch identifier'
}

# Store processing history
adata.uns['processing_steps'] = [
    'Raw counts loaded from 10X',
    'Filtered: n_genes > 200, n_counts < 50000',
    'Normalized to 10000 counts per cell',
    'Log transformed'
]
```

## Reproducibility

### Setting Seeds
```python
import numpy as np

# Set random seed for reproducible results
np.random.seed(42)

# Record in uns
adata.uns['random_seed'] = 42
```

### Storing Parameters
```python
# Store analysis parameters in uns
adata.uns['pca'] = {
    'n_comps': 50,
    'svd_solver': 'arpack',
    'random_state': 42
}

adata.uns['neighbors'] = {
    'n_neighbors': 15,
    'n_pcs': 50,
    'metric': 'euclidean',
    'method': 'umap'
}
```

### Version Tracking
```python
import anndata
import scanpy
import numpy

# Store library versions
adata.uns['versions'] = {
    'anndata': anndata.__version__,
    'scanpy': scanpy.__version__,
    'numpy': numpy.__version__,
    'python': sys.version
}
```

## Error Handling

### Checking Validity
```python
# Verify dimensions
assert adata.n_obs == len(adata.obs)
assert adata.n_vars == len(adata.var)
assert adata.X.shape == (adata.n_obs, adata.n_vars)

# Check for NaNs
has_nan = np.isnan(adata.X.data).any() if issparse(adata.X) else np.isnan(adata.X).any()
if has_nan:
    print("Warning: Data contains NaN values")

# Check for negative values (if counts expected)
has_negative = (adata.X.data < 0).any() if issparse(adata.X) else (adata.X < 0).any()
if has_negative:
    print("Warning: Data contains negative values")
```

### Validating Metadata
```python
# Check for missing values
missing_obs = adata.obs.isnull().sum()
if missing_obs.any():
    print("Missing values in obs:")
    print(missing_obs[missing_obs > 0])

# Verify unique indices
assert adata.obs_names.is_unique, "Observation names not unique"
assert adata.var_names.is_unique, "Variable names not unique"

# Check alignment
assert len(adata.obs) == adata.n_obs
assert len(adata.var) == adata.n_vars
```

## Integration with Other Tools

### Scanpy Integration
```python
import scanpy as sc

# AnnData is native format for scanpy
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
```

### Pandas Integration
```python
import pandas as pd

# Convert to DataFrame
df = adata.to_df()

# Create from DataFrame
adata = ad.AnnData(df)

# Work with metadata as DataFrame
adata.obs = adata.obs.merge(external_metadata, left_index=True, right_index=True)
```

### PyTorch Integration
```python
from anndata.experimental import AnnLoader

# Create PyTorch DataLoader
dataloader = AnnLoader(adata, batch_size=128, shuffle=True)

# Iterate in training loop
for batch in dataloader:
    X = batch.X
    # Train model on batch
```

## Common Pitfalls

### Pitfall 1: Modifying Views
```python
# Bad: Modifying a view can affect original data
subset = adata[:100, :]
subset.X = new_data  # Might modify adata.X!

# Good: Copy before modifying
subset = adata[:100, :].copy()
subset.X = new_data  # Independent copy
```

### Pitfall 2: Index Misalignment
```python
# Bad: Assuming order matches
external_data = pd.read_csv('data.csv')
adata.obs['new_col'] = external_data['values']  # Risk of misalignment!

# Good: Align by index
adata.obs['new_col'] = external_data.set_index('cell_id').loc[adata.obs_names, 'values']
```

### Pitfall 3: Mixing Sparse and Dense
```python
# Bad: Converting sparse to dense explodes memory
result = adata.X + 1  # Converts sparse to dense!

# Good: Sparse operations
from scipy.sparse import issparse
if issparse(adata.X):
    result = adata.X.copy()
    result.data += 1
```

### Pitfall 4: View Lifecycle
```python
# Bad: Assuming subset is independent
subset = adata[mask, :]
del adata  # Subset might become invalid!

# Good: Copy if needed
subset = adata[mask, :].copy()
del adata  # Subset remains valid
```

### Pitfall 5: Ignoring Memory Limits
```python
# Bad: Loading huge dataset into RAM
adata = ad.read_h5ad('100GB_file.h5ad')  # OOM Error!

# Good: Use backed mode
adata = ad.read_h5ad('100GB_file.h5ad', backed='r')
subset = adata[adata.obs['keep']].to_memory()
```

## Example Workflow

Complete best-practices workflow:

```python
import anndata as ad
import numpy as np
from scipy.sparse import csr_matrix

# 1. Load with backed mode if large
adata = ad.read_h5ad('data.h5ad', backed='r')

# 2. Quick check without loading
print(f"Dataset: {adata.n_obs} cells × {adata.n_vars} genes")

# 3. Filter based on metadata
high_quality = adata[adata.obs['quality_score'] > 0.8]

# 4. Load filtered subset to memory
adata = high_quality.to_memory()

# 5. Convert to optimized types
adata.strings_to_categoricals()
if not issparse(adata.X):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:
        adata.X = csr_matrix(adata.X)

# 6. Store raw before filtering genes
adata.raw = adata.copy()

# 7. Filter to highly variable genes
adata = adata[:, adata.var['highly_variable']].copy()

# 8. Document processing
adata.uns['processing'] = {
    'filtered': 'quality_score > 0.8',
    'n_hvg': adata.n_vars,
    'date': '2025-11-03'
}

# 9. Save optimized file
adata.write_h5ad('processed.h5ad', compression='gzip')
```
