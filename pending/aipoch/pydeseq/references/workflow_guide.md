# PyDESeq2 Workflow Guide

This document provides a detailed step-by-step workflow for common analysis patterns in PyDESeq2.

## Table of Contents
1. [Complete Differential Expression Analysis](#complete-differential-expression-analysis)
2. [Data Loading and Preparation](#data-loading-and-preparation)
3. [Single-factor Analysis](#single-factor-analysis)
4. [Multi-factor Analysis](#multi-factor-analysis)
5. [Result Export and Visualization](#result-export-and-visualization)
6. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Complete Differential Expression Analysis

### Overview
A standard PyDESeq2 analysis consists of 12 main steps across two phases:

**Phase 1: Read Count Modeling (Steps 1-7)**
- Normalization and dispersion estimation
- Log fold-change (LFC) fitting
- Outlier detection

**Phase 2: Statistical Analysis (Steps 8-12)**
- Wald test
- Multiple hypothesis testing correction
- Optional LFC shrinkage

### Complete Workflow Code

```python
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Load data
counts_df = pd.read_csv("counts.csv", index_col=0).T  # Transpose if necessary
metadata = pd.read_csv("metadata.csv", index_col=0)

# Filter low-count genes
genes_to_keep = counts_df.columns[counts_df.sum(axis=0) >= 10]
counts_df = counts_df[genes_to_keep]

# Remove samples with missing metadata
samples_to_keep = ~metadata.condition.isna()
counts_df = counts_df.loc[samples_to_keep]
metadata = metadata.loc[samples_to_keep]

# Initialize DeseqDataSet
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~condition",
    refit_cooks=True
)

# Run normalization and fitting
dds.deseq2()

# Perform statistical tests
ds = DeseqStats(
    dds,
    contrast=["condition", "treated", "control"],
    alpha=0.05,
    cooks_filter=True,
    independent_filter=True
)
ds.summary()

# Optional: Apply LFC shrinkage for visualization
ds.lfc_shrink()

# Get results
results = ds.results_df
print(results.head())
```

---

## Data Loading and Preparation

### Loading CSV Files

Count data is often provided in "genes × samples" format but needs to be transposed:

```python
import pandas as pd

# Load count matrix (genes × samples)
counts_df = pd.read_csv("counts.csv", index_col=0)

# Transpose to samples × genes
counts_df = counts_df.T

# Load metadata (already in samples × variables format)
metadata = pd.read_csv("metadata.csv", index_col=0)
```

### Loading from Other Formats

**From TSV:**
```python
counts_df = pd.read_csv("counts.tsv", sep="\t", index_col=0).T
metadata = pd.read_csv("metadata.tsv", sep="\t", index_col=0)
```

**From saved pickle:**
```python
import pickle

with open("counts.pkl", "rb") as f:
    counts_df = pickle.load(f)

with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)
```

**From AnnData:**
```python
import anndata as ad

adata = ad.read_h5ad("data.h5ad")
counts_df = pd.DataFrame(
    adata.X,
    index=adata.obs_names,
    columns=adata.var_names
)
metadata = adata.obs
```

### Data Filtering

**Filtering low-count genes:**
```python
# Remove genes with total counts less than 10
genes_to_keep = counts_df.columns[counts_df.sum(axis=0) >= 10]
counts_df = counts_df[genes_to_keep]
```

**Filtering samples with missing metadata:**
```python
# Remove samples where 'condition' column is NA
samples_to_keep = ~metadata.condition.isna()
counts_df = counts_df.loc[samples_to_keep]
metadata = metadata.loc[samples_to_keep]
```

**Filtering based on multiple criteria:**
```python
# Keep only samples meeting all criteria
mask = (
    ~metadata.condition.isna() &
    (metadata.batch.isin(["batch1", "batch2"])) &
    (metadata.age >= 18)
)
counts_df = counts_df.loc[mask]
metadata = metadata.loc[mask]
```

### Data Validation

**Checking data structure:**
```python
print(f"Counts shape: {counts_df.shape}")  # Should be (samples, genes)
print(f"Metadata shape: {metadata.shape}")  # Should be (samples, variables)
print(f"Indices match: {all(counts_df.index == metadata.index)}")

# Check for negative values
assert (counts_df >= 0).all().all(), "Counts must be non-negative"

# Check for non-integer values
assert counts_df.applymap(lambda x: x == int(x)).all().all(), "Counts must be integers"
```

---

## Single-factor Analysis

### Simple Two-group Comparison

Comparing treated vs. control samples:

```python
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Design: Model expression as a function of condition
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~condition"
)

dds.deseq2()

# Test treated vs control
ds = DeseqStats(
    dds,
    contrast=["condition", "treated", "control"]
)
ds.summary()

# Results
results = ds.results_df
significant = results[results.padj < 0.05]
print(f"Found {len(significant)} significant genes")
```

### Multiple Pairwise Comparisons

When comparing multiple groups:

```python
# Test each treatment vs control
treatments = ["treated_A", "treated_B", "treated_C"]
all_results = {}

for treatment in treatments:
    ds = DeseqStats(
        dds,
        contrast=["condition", treatment, "control"]
    )
    ds.summary()
    all_results[treatment] = ds.results_df

# Compare results of different treatments
for name, results in all_results.items():
    sig = results[results.padj < 0.05]
    print(f"{name}: {len(sig)} significant genes")
```

---

## Multi-factor Analysis

### Two-factor Design

Accounting for batch effects while testing for condition:

```python
# Design includes batch and condition
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~batch + condition"
)

dds.deseq2()

# Test condition effect while controlling for batch
ds = DeseqStats(
    dds,
    contrast=["condition", "treated", "control"]
)
ds.summary()
```

### Interaction Effects

Testing if the treatment effect differs across groups:

```python
# Design includes interaction term
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~group + condition + group:condition"
)

dds.deseq2()

# Test interaction term
ds = DeseqStats(dds, contrast=["group:condition", ...])
ds.summary()
```

### Continuous Covariates

Including continuous variables like age:

```python
# Ensure age in metadata is numeric
metadata["age"] = pd.to_numeric(metadata["age"])

dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~age + condition"
)

dds.deseq2()
```

---

## Result Export and Visualization

### Saving Results

**Exporting to CSV:**
```python
# Save statistical results
ds.results_df.to_csv("deseq2_results.csv")

# Save only significant genes
significant = ds.results_df[ds.results_df.padj < 0.05]
significant.to_csv("significant_genes.csv")

# Save sorted results
sorted_results = ds.results_df.sort_values("padj")
sorted_results.to_csv("sorted_results.csv")
```

**Saving DeseqDataSet:**
```python
import pickle

# Save as AnnData for later use
with open("dds_result.pkl", "wb") as f:
    pickle.dump(dds.to_picklable_anndata(), f)
```

**Loading Saved Results:**
```python
# Load results
results = pd.read_csv("deseq2_results.csv", index_col=0)

# Load AnnData
with open("dds_result.pkl", "rb") as f:
    adata = pickle.load(f)
```

### Basic Visualization

**Volcano Plot:**
```python
import matplotlib.pyplot as plt
import numpy as np

results = ds.results_df.copy()
results["-log10(padj)"] = -np.log10(results.padj)

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(
    results.log2FoldChange,
    results["-log10(padj)"],
    alpha=0.5,
    s=10
)
plt.axhline(-np.log10(0.05), color='red', linestyle='--', label='padj=0.05')
plt.axvline(1, color='gray', linestyle='--')
plt.axvline(-1, color='gray', linestyle='--')
plt.xlabel("Log2 Fold Change")
plt.ylabel("-Log10(Adjusted P-value)")
plt.title("Volcano Plot")
plt.legend()
plt.savefig("volcano_plot.png", dpi=300)
```

**MA Plot:**
```python
plt.figure(figsize=(10, 6))
plt.scatter(
    np.log10(results.baseMean + 1),
    results.log2FoldChange,
    alpha=0.5,
    s=10,
    c=(results.padj < 0.05),
    cmap='bwr'
)
plt.xlabel("Log10(Base Mean + 1)")
plt.ylabel("Log2 Fold Change")
plt.title("MA Plot")
plt.savefig("ma_plot.png", dpi=300)
```

---

## Common Patterns and Best Practices

### 1. Data Preprocessing Checklist

Before running PyDESeq2:
- ✓ Ensure counts are non-negative integers
- ✓ Verify data orientation is "samples × genes"
- ✓ Check that sample names match between count data and metadata
- ✓ Remove or handle missing metadata values
- ✓ Filter low-count genes (typically total counts < 10)
- ✓ Verify experimental factors are correctly encoded

### 2. Design Formula Best Practices

**Order matters:** Place adjustment variables before the variable of interest
```python
# Correct: Control for batch, test for condition
design = "~batch + condition"

# Suboptimal: Condition column first
design = "~condition + batch"
```

**Use categorical types for discrete variables:**
```python
# Ensure data types are correct
metadata["condition"] = metadata["condition"].astype("category")
metadata["batch"] = metadata["batch"].astype("category")
```

### 3. Statistical Testing Guidelines

**Setting an appropriate alpha value:**
```python
# Standard significance threshold
ds = DeseqStats(dds, alpha=0.05)

# Stricter threshold for exploratory analysis
ds = DeseqStats(dds, alpha=0.01)
```

**Use Independent Filtering:**
```python
# Recommended: Filter tests with low statistical power
ds = DeseqStats(dds, independent_filter=True)

# Disable only if there is a specific reason
ds = DeseqStats(dds, independent_filter=False)
```

### 4. LFC Shrinkage

**When to use:**
- For visualization (volcano plots, heatmaps)
- For ranking genes by effect size
- When prioritizing genes for follow-up validation

**When not to use:**
- For reporting statistical significance (use unshrunken p-values)
- For Gene Set Enrichment Analysis (GSEA, usually uses unshrunken values)

```python
# Save both versions
ds.results_df.to_csv("results_unshrunken.csv")
ds.lfc_shrink()
ds.results_df.to_csv("results_shrunken.csv")
```

### 5. Memory Management

For large datasets:
```python
# Use parallel processing
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~condition",
    n_cpus=4  # Adjust based on available cores
)

# Process in batches if necessary
# (Split genes into chunks, analyze separately, then merge results)
```

---

## Troubleshooting

### Error: Index Mismatch Between Counts and Metadata

**Problem:** Sample names do not match
```
KeyError: Sample names in counts and metadata don't match
```

**Solution:**
```python
# Check indices
print("Counts samples:", counts_df.index.tolist())
print("Metadata samples:", metadata.index.tolist())

# Align if necessary
common_samples = counts_df.index.intersection(metadata.index)
counts_df = counts_df.loc[common_samples]
metadata = metadata.loc[common_samples]
```

### Error: All Genes Have Zero Counts

**Problem:** Data might need to be transposed
```
ValueError: All genes have zero total counts
```

**Solution:**
```python
# Check data orientation
print(f"Counts shape: {counts_df.shape}")

# If genes > samples, transposition might be needed
if counts_df.shape[1] < counts_df.shape[0]:
    counts_df = counts_df.T
```

### Warning: Many Genes Filtered Out

**Problem:** Too many low-count genes removed

**Check:**
```python
# View gene count distribution
print(counts_df.sum(axis=0).describe())

# Visualization
import matplotlib.pyplot as plt
plt.hist(counts_df.sum(axis=0), bins=50, log=True)
plt.xlabel("Total counts per gene")
plt.ylabel("Frequency")
plt.show()
```

**Adjust filtering threshold if necessary:**
```python
# Try a lower threshold
genes_to_keep = counts_df.columns[counts_df.sum(axis=0) >= 5]
```

### Error: Design Matrix is Not Full Rank

**Problem:** Confounded design (e.g., all treated samples in the same batch)

**Solution:**
```python
# Check for design confounding
print(pd.crosstab(metadata.condition, metadata.batch))

# Remove confounding variable or add interaction term
design = "~condition"  # Drop batch
# OR
design = "~condition + batch + condition:batch"  # Add interaction term
```

### Problem: No Significant Genes Found

**Possible causes:**
1. Small effect size
2. High biological variability
3. Insufficient sample size
4. Technical issues (batch effects, outliers)

**Diagnosis:**
```python
# Check dispersion estimates
import matplotlib.pyplot as plt
dispersions = dds.varm["dispersions"]
plt.hist(dispersions, bins=50)
plt.xlabel("Dispersion")
plt.ylabel("Frequency")
plt.show()

# Check size factors (should be close to 1)
print("Size factors:", dds.obsm["size_factors"])

# View top genes, even if not significant
top_genes = ds.results_df.nsmallest(20, "pvalue")
print(top_genes)
```

### Memory Errors on Large Datasets

**Solution:**
```python
# 1. Use fewer CPUs (paradoxically, this sometimes helps)
dds = DeseqDataSet(..., n_cpus=1)

# 2. Filter more stringently
genes_to_keep = counts_df.columns[counts_df.sum(axis=0) >= 20]

# 3. Process in batches
# Split analysis by gene subsets and merge results
```