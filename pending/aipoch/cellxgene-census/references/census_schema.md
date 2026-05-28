# CZ CELLxGENE Census Data Schema Reference

## Overview

The CZ CELLxGENE Census is a versioned collection of single-cell data built on the TileDB-SOMA framework. This reference document details its data structure, available metadata fields, and query syntax.

## High-Level Structure

The Census is organized as a `SOMACollection` containing two main components:

### 1. census_info
Summary information, including:
- **summary**: Build date, cell counts, and dataset statistics
- **datasets**: All datasets from CELLxGENE Discover and their metadata
- **summary_cell_counts**: Cell counts stratified by metadata categories

### 2. census_data
Species-specific `SOMAExperiment` objects:
- **"homo_sapiens"**: Human single-cell data
- **"mus_musculus"**: Mouse single-cell data

## Data Structure Per Organism

Each organism's experiment object contains:

### obs (Cell Metadata)
Cell-level annotations stored as a `SOMADataFrame`. Access via:
```python
census["census_data"]["homo_sapiens"].obs
```

### ms["RNA"] (Measurement Data)
RNA measurement data, including:
- **X**: Data matrices containing the following layers:
  - `raw`: Raw count data
  - `normalized`: Normalized counts (if available)
- **var**: Gene metadata
- **feature_dataset_presence_matrix**: A sparse boolean array showing which genes were measured in each dataset

## Cell Metadata Fields (obs)

### Required/Core Fields

**Identity & Dataset:**
- `soma_joinid`: Unique integer identifier for joining
- `dataset_id`: Source dataset identifier
- `is_primary_data`: Boolean flag (True = unique cell, False = duplicate cell across datasets)

**Cell Type:**
- `cell_type`: Human-readable cell type name
- `cell_type_ontology_term_id`: Standardized ontology term (e.g., "CL:0000236")

**Tissue:**
- `tissue`: Specific tissue name
- `tissue_general`: Broader tissue category (useful for grouping)
- `tissue_ontology_term_id`: Standardized ontology term

**Assay:**
- `assay`: Sequencing technology used
- `assay_ontology_term_id`: Standardized ontology term

**Disease:**
- `disease`: Disease state or condition
- `disease_ontology_term_id`: Standardized ontology term

**Donor:**
- `donor_id`: Unique donor identifier
- `sex`: Biological sex (male, female, unknown)
- `self_reported_ethnicity`: Self-reported ethnicity information
- `development_stage`: Life stage (adult, child, embryonic, etc.)
- `development_stage_ontology_term_id`: Standardized ontology term

**Organism:**
- `organism`: Scientific name (Homo sapiens, Mus musculus)
- `organism_ontology_term_id`: Standardized ontology term

**Technical:**
- `suspension_type`: Sample preparation type (cell, nucleus, na)

## Gene Metadata Fields (var)

Access via:
```python
census["census_data"]["homo_sapiens"].ms["RNA"].var
```

**Available Fields:**
- `soma_joinid`: Unique integer identifier for joining
- `feature_id`: Ensembl gene ID (e.g., "ENSG00000161798")
- `feature_name`: Gene symbol (e.g., "FOXP2")
- `feature_length`: Gene length in base pairs

## Value Filter Syntax

Queries use Python-like expressions for filtering. The syntax is handled by TileDB-SOMA.

### Comparison Operators
- `==`: Equal to
- `!=`: Not equal to
- `<`, `>`, `<=`, `>=`: Numerical comparisons
- `in`: Membership test (e.g., `feature_id in ['ENSG00000161798', 'ENSG00000188229']`)

### Logical Operators
- `and`, `&`: Logical AND
- `or`, `|`: Logical OR

### Examples

**Single condition:**
```python
value_filter="cell_type == 'B cell'"
```

**Multiple conditions with AND:**
```python
value_filter="cell_type == 'B cell' and tissue_general == 'lung' and is_primary_data == True"
```

**Using IN for multiple values:**
```python
value_filter="tissue in ['lung', 'liver', 'kidney']"
```

**Complex conditions:**
```python
value_filter="(cell_type == 'neuron' or cell_type == 'astrocyte') and disease != 'normal'"
```

**Filtering genes:**
```python
var_value_filter="feature_name in ['CD4', 'CD8A', 'CD19']"
```

## Data Inclusion Criteria

The Census includes all CZ CELLxGENE Discover data that meet the following criteria:

1. **Organism**: Human (*Homo sapiens*) or Mouse (*Mus musculus*)
2. **Technology**: Approved RNA sequencing technologies
3. **Count Type**: Raw counts only (datasets with only processed/normalized data are excluded)
4. **Metadata**: Standardized according to the CELLxGENE schema
5. **Spatial and Non-spatial Data**: Includes both traditional transcriptomics and spatial transcriptomics

## Important Data Characteristics

### Duplicate Cells
Cells may appear in multiple datasets. For most analyses, use `is_primary_data == True` to filter for unique cells.

### Count Types
The Census includes:
- **Molecule counts**: From UMI-based methods
- **Full-gene sequencing read counts**: From non-UMI methods
These may require different normalization approaches.

### Versioning
Census releases are versioned (e.g., "2023-07-25", "stable"). For reproducibility in analysis, always specify the version:
```python
census = cellxgene_census.open_soma(census_version="2023-07-25")
```

## Dataset Presence Matrix

Access which genes were measured in each dataset:
```python
presence_matrix = census["census_data"]["homo_sapiens"].ms["RNA"]["feature_dataset_presence_matrix"]
```

This sparse boolean matrix helps to understand:
- Gene coverage across datasets
- Which datasets should be included for specific gene analyses
- Technical batch effects related to gene coverage

## SOMA Object Types

Core TileDB-SOMA objects used:
- **DataFrame**: Tabular data (obs, var)
- **SparseNDArray**: Sparse matrices (X layers, presence matrix)
- **DenseNDArray**: Dense arrays (less common)
- **Collection**: Container for related objects
- **Experiment**: Top-level container for measurement data
- **SOMAScene**: Spatial transcriptomics scene
- **obs_spatial_presence**: Spatial data availability