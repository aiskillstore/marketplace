# PyDESeq2 API Reference Guide

This document provides a comprehensive API reference for PyDESeq2's classes, methods, and utility functions.

## Core Classes

### DeseqDataSet

The core class for differential expression analysis, responsible for the data pipeline from normalization to log fold change (LFC) fitting.

**Purpose:** Implements the estimation of dispersion and log fold change (LFC) for RNA-seq count data.

**Initialization Parameters:**
- `counts`: A pandas DataFrame of shape (samples × genes) containing non-negative integer read counts.
- `metadata`: A pandas DataFrame of shape (samples × variables) containing sample annotations.
- `design`: str, specifies the Wilkinson formula for the statistical model (e.g., "~condition", "~group + condition").
- `refit_cooks`: bool, whether to refit parameters after removing Cook's distance outliers (default: True).
- `n_cpus`: int, number of CPUs used for parallel processing (optional).
- `quiet`: bool, whether to suppress progress messages (default: False).

**Key Methods:**

#### `deseq2()`
Runs the full DESeq2 pipeline, including normalization and dispersion/LFC fitting.

**Execution Steps:**
1. Calculate normalization factors (size factors)
2. Fit gene-wise dispersions
3. Fit dispersion trend curve
4. Calculate dispersion priors
5. Fit MAP (Maximum A Posteriori) dispersions
6. Fit log fold changes (LFC)
7. Calculate Cook's distances for outlier detection
8. If `refit_cooks=True`, perform optional refitting

**Returns:** None (modifies the object in place)

#### `to_picklable_anndata()`
Converts the DeseqDataSet into a picklable AnnData object.

**Returns:** An AnnData object containing:
- `X`: Count data matrix
- `obs`: Sample-level metadata (1D)
- `var`: Gene-level metadata (1D)
- `varm`: Gene-level multidimensional data (e.g., LFC estimates)

**Usage:**
```python
import pickle
# Save in binary write mode
with open("result_adata.pkl", "wb") as f:
    pickle.dump(dds.to_picklable_anndata(), f)
```

**Attributes (after running deseq2()):**
- `layers`: Dictionary containing various matrices (normalized counts, etc.)
- `varm`: Dictionary containing gene-level results (log fold changes, dispersions, etc.)
- `obsm`: Dictionary containing sample-level information
- `uns`: Dictionary containing global parameters

---

### DeseqStats

A class for performing statistical tests and calculating differential expression p-values.

**Purpose:** Facilitates statistical testing for PyDESeq2 using Wald tests and optional LFC shrinkage.

**Initialization Parameters:**
- `dds`: A DeseqDataSet object that has been processed with `deseq2()`.
- `contrast`: list or None, specifies the contrast for testing.
  - Format: `[variable, test_level, reference_level]`
  - Example: `["condition", "treated", "control"]` to test treated vs control.
  - If None, the last coefficient in the design formula is used.
- `alpha`: float, significance threshold for independent filtering (default: 0.05).
- `cooks_filter`: bool, whether to filter outliers based on Cook's distance (default: True).
- `independent_filter`: bool, whether to perform independent filtering (default: True).
- `n_cpus`: int, number of CPUs used for parallel processing (optional).
- `quiet`: bool, whether to suppress progress messages (default: False).

**Key Methods:**

#### `summary()`
Runs the Wald test and calculates p-values and adjusted p-values.

**Execution Steps:**
1. Run Wald statistical test on the specified contrast
2. Optional Cook's distance filtering
3. Optional independent filtering to remove tests with low statistical power
4. Multiple hypothesis testing correction (Benjamini-Hochberg method)

**Returns:** None (results are stored in the `results_df` attribute)

**Result DataFrame Column Descriptions:**
- `baseMean`: Mean of normalized counts for all samples
- `log2FoldChange`: log2 fold change between conditions
- `lfcSE`: Standard error of the log2 fold change
- `stat`: Wald test statistic
- `pvalue`: Raw p-value
- `padj`: Adjusted p-value (FDR corrected)

#### `lfc_shrink(coeff=None)`
Shrinks log fold changes using the apeGLM method.

**Purpose:** Reduces noise in LFC estimates for better visualization and ranking, especially for genes with low counts or high variability.

**Parameters:**
- `coeff`: str or None, the name of the coefficient to shrink (if None, the coefficient from the contrast is used).

**Important Note:** Shrinkage is for visualization/ranking purposes only. Statistical test results (p-values, adjusted p-values) remain unchanged.

**Returns:** None (updates `results_df` with shrunken LFCs)

**Attributes:**
- `results_df`: A pandas DataFrame containing test results (available after calling `summary()`).

---

## Utility Functions

### `pydeseq2.utils.load_example_data(modality="single-factor")`

Loads synthetic example datasets for testing and tutorials.

**Parameters:**
- `modality`: str, "single-factor" or "multi-factor".

**Returns:** (counts_df, metadata_df) tuple
- `counts_df`: A pandas DataFrame containing synthetic count data.
- `metadata_df`: A pandas DataFrame containing sample annotations.

---

## Preprocessing Module

The `pydeseq2.preprocessing` module provides tools for data preparation.

**Common Operations:**
- Gene filtering based on minimum read counts
- Sample filtering based on metadata criteria
- Data transformation and normalization

---

## Inference Classes

### Inference
Abstract base class defining the interface for DESeq2-related inference methods.

### DefaultInference
Default implementation of inference methods using scipy, sklearn, and numpy.

**Purpose:** Provides mathematical implementations for:
- GLM (Generalized Linear Model) fitting
- Dispersion estimation
- Trend curve fitting
- Statistical testing

---

## Data Structure Requirements

### Count Matrix
- **Shape:** (samples × genes)
- **Type:** pandas DataFrame
- **Values:** Non-negative integers (raw read counts)
- **Index:** Sample identifiers (must match metadata index)
- **Columns:** Gene identifiers

### Metadata
- **Shape:** (samples × variables)
- **Type:** pandas DataFrame
- **Index:** Sample identifiers (must match count matrix index)
- **Columns:** Experimental factors (e.g., "condition", "batch", "group")
- **Values:** Categorical or continuous variables used in the design formula

### Important Notes
- Sample order must be consistent between the count matrix and metadata.
- Missing values in metadata should be handled before analysis.
- Gene names should be unique.
- Count files often need to be transposed: `counts_df = counts_df.T`

---

## Common Workflow Patterns

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# 1. Initialize the dataset
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~condition",
    refit_cooks=True
)

# 2. Fit dispersions and LFCs
dds.deseq2()

# 3. Perform statistical tests
ds = DeseqStats(
    dds,
    contrast=["condition", "treated", "control"],
    alpha=0.05
)
ds.summary()

# 4. Optional: Shrink LFCs for visualization
ds.lfc_shrink()

# 5. Get results
results = ds.results_df
```

---

## Version Compatibility

PyDESeq2 aims to match the default settings of DESeq2 v1.34.0. Since it is re-implemented in Python, some differences may exist.

**Test Environment:**
- Python 3.10-3.11
- anndata 0.8.0+
- numpy 1.23.0+
- pandas 1.4.3+
- scikit-learn 1.1.1+
- scipy 1.11.0+