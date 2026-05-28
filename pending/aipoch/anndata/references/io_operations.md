# I/O Operations

AnnData provides comprehensive I/O capabilities for reading and writing data in various formats.

## Native Formats

### H5AD (HDF5-based)
Recommended native format for AnnData objects, offering efficient storage and fast access.

#### Writing H5AD
```python
import anndata as ad

# Write to file
adata.write_h5ad('data.h5ad')

# Write with compression
adata.write_h5ad('data.h5ad', compression='gzip')

# Write with specific compression level (0-9, higher means more compression)
adata.write_h5ad('data.h5ad', compression='gzip', compression_opts=9)
```

#### Reading H5AD
```python
# Read entire file into memory
adata = ad.read_h5ad('data.h5ad')

# Read in backed mode (lazy loading for large files)
adata = ad.read_h5ad('data.h5ad', backed='r')  # Read-only
adata = ad.read_h5ad('data.h5ad', backed='r+')  # Read-write

# Backed mode supports datasets larger than RAM
# Only accessed data is loaded into memory
```

#### Backed Mode Operations
```python
# Open in backed mode
adata = ad.read_h5ad('large_dataset.h5ad', backed='r')

# Access metadata without loading X
print(adata.obs.head())
print(adata.var.head())

# Subsetting creates a view (not loaded)
subset = adata[:100, :500]  # View, data not loaded

# Load specific data into memory
X_subset = subset.X[:]  # Loads this subset now

# Convert entire backed object to memory
adata_memory = adata.to_memory()
```

### Zarr
Hierarchical array storage format optimized for cloud storage and parallel I/O.

#### Writing Zarr
```python
# Write to Zarr store
adata.write_zarr('data.zarr')

# Write with specific chunks (important for performance)
adata.write_zarr('data.zarr', chunks=(100, 100))
```

#### Reading Zarr
```python
# Read Zarr store
adata = ad.read_zarr('data.zarr')
```

#### Remote Zarr Access
```python
import fsspec

# Access Zarr from S3
store = fsspec.get_mapper('s3://bucket-name/data.zarr')
adata = ad.read_zarr(store)

# Access Zarr from URL
store = fsspec.get_mapper('https://example.com/data.zarr')
adata = ad.read_zarr(store)
```

## Alternative Input Formats

### CSV/TSV
```python
# Read CSV (genes as columns, cells as rows)
adata = ad.read_csv('data.csv')

# Read with custom delimiter
adata = ad.read_csv('data.tsv', delimiter='\t')

# Specify first column as row names
adata = ad.read_csv('data.csv', first_column_names=True)
```

### Excel
```python
# Read Excel file
adata = ad.read_excel('data.xlsx')

# Read specific sheet
adata = ad.read_excel('data.xlsx', sheet='Sheet1')
```

### Matrix Market (MTX)
Common sparse matrix format in genomics.

```python
# Read MTX and associated files
# Expects: matrix.mtx, genes.tsv, barcodes.tsv
adata = ad.read_mtx('matrix.mtx')

# Read with custom gene and barcode files
adata = ad.read_mtx(
    'matrix.mtx',
    var_names='genes.tsv',
    obs_names='barcodes.tsv'
)

# Transpose if needed (MTX often has genes as rows)
adata = adata.T
```

### 10X Genomics Format
```python
# Read 10X h5 format
adata = ad.read_10x_h5('filtered_feature_bc_matrix.h5')

# Read 10X MTX directory
adata = ad.read_10x_mtx('filtered_feature_bc_matrix/')

# Specify genome if multiple present
adata = ad.read_10x_h5('data.h5', genome='GRCh38')
```

### Loom
```python
# Read Loom file
adata = ad.read_loom('data.loom')

# Read with specific obs/var annotations
adata = ad.read_loom(
    'data.loom',
    obs_names='CellID',
    var_names='Gene'
)
```

### Text Files
```python
# Read generic text file
adata = ad.read_text('data.txt', delimiter='\t')

# Read with custom parameters
adata = ad.read_text(
    'data.txt',
    delimiter=',',
    first_column_names=True,
    dtype='float32'
)
```

### UMI tools
```python
# Read UMI tools format
adata = ad.read_umi_tools('counts.tsv')
```

### HDF5 (Generic)
```python
# Read from HDF5 file (not h5ad format)
adata = ad.read_hdf('data.h5', key='dataset')
```

## Alternative Output Formats

### CSV
```python
# Write to CSV files (creates multiple files)
adata.write_csvs('output_dir/')

# This creates:
# - output_dir/X.csv (expression matrix)
# - output_dir/obs.csv (observation annotations)
# - output_dir/var.csv (variable annotations)
# - output_dir/uns.csv (unstructured annotations if feasible)

# Skip certain components
adata.write_csvs('output_dir/', skip_data=True)  # Skip X matrix
```

### Loom
```python
# Write to Loom format
adata.write_loom('output.loom')
```

## Reading Specific Elements

For fine-grained control, read specific elements from storage:

```python
from anndata import read_elem

# Read only observation annotations
obs = read_elem('data.h5ad/obs')

# Read specific layer
layer = read_elem('data.h5ad/layers/normalized')

# Read unstructured data element
params = read_elem('data.h5ad/uns/pca_params')
```

## Writing Specific Elements

```python
from anndata import write_elem
import h5py

# Write element to existing file
with h5py.File('data.h5ad', 'a') as f:
    write_elem(f, 'new_layer', adata.X.copy())
```

## Lazy Operations

For very large datasets, use lazy reading to avoid loading full datasets:

```python
from anndata.experimental import read_elem_lazy

# Lazy read (returns dask array or similar)
X_lazy = read_elem_lazy('large_data.h5ad/X')

# Compute only when needed
subset = X_lazy[:100, :100].compute()
```

## Common I/O Patterns

### Format Conversion
```python
# Convert MTX to H5AD
adata = ad.read_mtx('matrix.mtx').T
adata.write_h5ad('data.h5ad')

# Convert CSV to H5AD
adata = ad.read_csv('data.csv')
adata.write_h5ad('data.h5ad')

# Convert H5AD to Zarr
adata = ad.read_h5ad('data.h5ad')
adata.write_zarr('data.zarr')
```

### Loading Metadata Without Data
```python
# Backed mode allows checking metadata without loading X
adata = ad.read_h5ad('large_file.h5ad', backed='r')
print(f"Dataset has {adata.n_obs} observations and {adata.n_vars} variables")
print(adata.obs.columns)
print(adata.var.columns)
# X is not loaded into memory
```

### Appending to Existing File
```python
# Open in read-write mode
adata = ad.read_h5ad('data.h5ad', backed='r+')

# Modify metadata
adata.obs['new_column'] = values

# Changes are written to disk
```

### Downloading from URL
```python
import anndata as ad

# Read directly from URL (for h5ad files)
url = 'https://example.com/data.h5ad'
adata = ad.read_h5ad(url, backed='r')  # Stream access

# For other formats, download first
import urllib.request
urllib.request.urlretrieve(url, 'local_file.h5ad')
adata = ad.read_h5ad('local_file.h5ad')
```

## Performance Tips

### Reading
- Use `backed='r'` for large files where you only need to query.
- Use `backed='r+'` if you need to modify metadata without loading all data.
- H5AD format is generally fastest for random access.
- Zarr is better for cloud storage and parallel access.
- Consider compression on storage, but note it may slow down reading.

### Writing
- Use compression for long-term storage: `compression='gzip'` or `compression='lzf'`.
- LZF is faster but compresses less than GZIP.
- For Zarr, tune chunk sizes based on access patterns:
  - Larger chunks for sequential reads.
  - Smaller chunks for random access.
- Convert string columns to categoricals before writing (smaller files).

### Memory Management
```python
# Convert strings to categoricals (smaller file size and memory footprint)
adata.strings_to_categoricals()
adata.write_h5ad('data.h5ad')

# Use sparse matrices for sparse data
from scipy.sparse import csr_matrix
if isinstance(adata.X, np.ndarray):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:  # If more than 50% zeros
        adata.X = csr_matrix(adata.X)
```

## Handling Large Datasets

### Strategy 1: Backed Mode
```python
# Work with datasets larger than RAM
adata = ad.read_h5ad('100GB_file.h5ad', backed='r')

# Filter based on metadata (fast, no data loading)
filtered = adata[adata.obs['quality_score'] > 0.8]

# Load filtered subset into memory
adata_memory = filtered.to_memory()
```

### Strategy 2: Chunked Processing
```python
# Process data in chunks
adata = ad.read_h5ad('large_file.h5ad', backed='r')

chunk_size = 1000
results = []

for i in range(0, adata.n_obs, chunk_size):
    chunk = adata[i:i+chunk_size, :].to_memory()
    # Process chunk
    result = process(chunk)
    results.append(result)
```

### Strategy 3: Using AnnCollection
```python
from anndata.experimental import AnnCollection

# Create collection without loading data
adatas = [f'dataset_{i}.h5ad' for i in range(10)]
collection = AnnCollection(
    adatas,
    join_obs='inner',
    join_vars='inner'
)

# Process collection lazily
# Data loaded only when accessed
```

## Common Issues & Solutions

### Issue: Out of Memory when Reading
**Solution**: Use backed mode or chunked reading
```python
adata = ad.read_h5ad('file.h5ad', backed='r')
```

### Issue: Slow Reads from Cloud Storage
**Solution**: Use Zarr format with appropriate chunking
```python
adata.write_zarr('data.zarr', chunks=(1000, 1000))
```

### Issue: File Size Too Large
**Solution**: Use compression and convert to sparse/categorical
```python
adata.strings_to_categoricals()
from scipy.sparse import csr_matrix
adata.X = csr_matrix(adata.X)
adata.write_h5ad('compressed.h5ad', compression='gzip')
```

### Issue: Cannot Modify Backed Object
**Solution**: Load to memory or open in 'r+' mode
```python
# Option 1: Load to memory
adata = adata.to_memory()

# Option 2: Open in read-write mode
adata = ad.read_h5ad('file.h5ad', backed='r+')
```
