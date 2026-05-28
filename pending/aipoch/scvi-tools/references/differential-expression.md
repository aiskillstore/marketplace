# Differential Expression Analysis in scvi-tools

This document provides detailed information on performing differential expression (DE) analysis using the scvi-tools probabilistic framework.

## Overview

scvi-tools implements Bayesian differential expression testing, utilizing learned generative models to estimate expression differences between groups. Compared to traditional methods, this approach offers the following advantages:

- **Batch Correction**: DE testing on batch-corrected representations
- **Uncertainty Quantification**: Probabilistic estimation of effect sizes
- **Zero-inflation Handling**: Proper modeling of dropouts and zero values
- **Flexible Comparisons**: Comparisons between any groups or cell types
- **Multimodal Support**: Applicable to RNA, protein (totalVI), and accessibility (PeakVI)

## Core Statistical Framework

### Problem Definition

The goal is to estimate the log fold-change of expression between two conditions:

```
log fold-change = log(μ_B) - log(μ_A)
```

where μ_A and μ_B are the mean expression levels in conditions A and B, respectively.

### Three-stage Pipeline

**Stage 1: Estimate Expression Levels**
- Sample from the posterior distribution of cell states
- Generate expression values from the learned generative model
- Aggregate across cells to obtain population-level estimates

**Stage 2: Detect Relevant Features (Hypothesis Testing)**
- Test for differential expression using a Bayesian framework
- Provides two testing modes:
  - **"vanilla" mode**: Point null hypothesis (β = 0)
  - **"change" mode**: Composite hypothesis (|β| ≤ δ)

**Stage 3: Control False Discoveries**
- Posterior expected False Discovery Proportion (FDP) control
- Select the maximum number of discoveries such that E[FDP] ≤ α

## Basic Usage

### Simple Two-group Comparison

```python
import scvi

# After training the model
model = scvi.model.SCVI(adata)
model.train()

# Compare two cell types
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# View top DE genes
top_genes = de_results.sort_values("lfc_mean", ascending=False).head(20)
print(top_genes[["lfc_mean", "lfc_std", "bayes_factor", "is_de_fdr_0.05"]])
```

### One-vs-Rest Comparison

```python
# Compare one group against all others
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells"  # Not setting group2 = compare against all remaining groups
)
```

### All Pairwise Comparisons

```python
# Perform pairwise comparisons for all cell types
all_comparisons = {}

cell_types = adata.obs["cell_type"].unique()

for ct1 in cell_types:
    for ct2 in cell_types:
        if ct1 != ct2:
            key = f"{ct1}_vs_{ct2}"
            all_comparisons[key] = model.differential_expression(
                groupby="cell_type",
                group1=ct1,
                group2=ct2
            )
```

## Key Parameters

### `groupby` (Required)
Column name in `adata.obs` defining the groups to compare.

```python
# Must be a categorical variable
de_results = model.differential_expression(groupby="cell_type")
```

### `group1` and `group2`
Groups to compare. If `group2` is None, `group1` is compared against all other groups.

```python
# Specific comparison
de = model.differential_expression(groupby="condition", group1="treated", group2="control")

# One-vs-rest comparison
de = model.differential_expression(groupby="cell_type", group1="T cells")
```

### `mode` (Hypothesis Testing Mode)

**"vanilla" mode** (default): Point null hypothesis
- Tests whether β is exactly equal to 0
- More sensitive, but may find tiny, biologically insignificant effects

**"change" mode**: Composite null hypothesis
- Tests whether |β| ≤ δ
- Requires biologically meaningful changes
- Reduces false discoveries from small effects

```python
# Use Change mode with a minimum effect size constraint
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    mode="change",
    delta=0.25  # Minimum log fold-change
)
```

### `delta`
Minimum effect size threshold in "change" mode.
- Typical values: 0.25, 0.5, 0.7 (log scale)
- log2(1.5) ≈ 0.58 (1.5-fold change)
- log2(2) = 1.0 (2-fold change)

```python
# Require at least 1.5-fold change
de = model.differential_expression(
    groupby="condition",
    group1="disease",
    group2="healthy",
    mode="change",
    delta=0.58  # log2(1.5)
)
```

### `fdr_target`
False Discovery Rate threshold (default: 0.05)

```python
# Stricter FDR control
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    fdr_target=0.01
)
```

### `batch_correction`
Whether to perform batch correction during DE testing (default: True)

```python
# Perform testing within specific batches
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    batch_correction=False
)
```

### `n_samples`
Number of posterior samples used for estimation (default: 5000)
- More samples = more accurate but slower
- Decrease for speed, increase for precision

```python
# High-precision analysis
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    n_samples=10000
)
```

## Interpreting Results

### Output Column Descriptions

The resulting DataFrame contains several important columns:

**Effect Size Estimation**:
- `lfc_mean`: Mean of log fold-change
- `lfc_median`: Median of log fold-change
- `lfc_std`: Standard deviation of log fold-change
- `lfc_min`: Lower bound of effect size
- `lfc_max`: Upper bound of effect size

**Statistical Significance**:
- `bayes_factor`: Bayes factor for differential expression
  - Higher values = stronger evidence
  - Values >3 are generally considered meaningful
- `is_de_fdr_0.05`: Boolean, indicates if the gene is DE at FDR 0.05
- `is_de_fdr_0.1`: Boolean, indicates if the gene is DE at FDR 0.1

**Expression Levels**:
- `mean1`: Mean expression in group 1
- `mean2`: Mean expression in group 2
- `non_zeros_proportion1`: Proportion of non-zero cells in group 1
- `non_zeros_proportion2`: Proportion of non-zero cells in group 2

### Interpretation Example

```python
de_results = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# Find genes significantly upregulated in T cells
upreg_tcells = de_results[
    (de_results["is_de_fdr_0.05"]) &
    (de_results["lfc_mean"] > 0)
].sort_values("lfc_mean", ascending=False)

print(f"Number of upregulated genes in T cells: {len(upreg_tcells)}")
print(upreg_tcells.head(10))

# Find genes with large effect sizes
large_effect = de_results[
    (de_results["is_de_fdr_0.05"]) &
    (abs(de_results["lfc_mean"]) > 1)  # 2-fold change
]
```

## Advanced Usage

### DE in Specific Cell Subsets

```python
# Perform DE testing only within a subset of cells
subset_indices = adata.obs["tissue"] == "lung"

de = model.differential_expression(
    idx1=adata.obs["cell_type"] == "T cells" & subset_indices,
    idx2=adata.obs["cell_type"] == "B cells" & subset_indices
)
```

### Batch-specific DE

```python
# Perform DE testing separately within each batch
batches = adata.obs["batch"].unique()

batch_de_results = {}
for batch in batches:
    batch_idx = adata.obs["batch"] == batch
    batch_de_results[batch] = model.differential_expression(
        idx1=(adata.obs["condition"] == "treated") & batch_idx,
        idx2=(adata.obs["condition"] == "control") & batch_idx
    )
```

### Pseudo-bulk DE

```python
# Aggregate cells before DE testing
# Suitable for cases with low cell numbers per group

de = model.differential_expression(
    groupby="cell_type",
    group1="rare_cell_type",
    group2="common_cell_type",
    n_samples=10000,  # Increase sample size for stability
    batch_correction=True
)
```

## Visualization

### Volcano Plot

```python
import matplotlib.pyplot as plt
import numpy as np

de = model.differential_expression(
    groupby="condition",
    group1="treated",
    group2="control"
)

# Plot volcano plot
plt.figure(figsize=(10, 6))
plt.scatter(
    de["lfc_mean"],
    -np.log10(1 / (de["bayes_factor"] + 1)),
    c=de["is_de_fdr_0.05"],
    cmap="coolwarm",
    alpha=0.5
)
plt.xlabel("Log Fold Change")
plt.ylabel("-log10(1/Bayes Factor)")
plt.title("Volcano Plot: Treated vs Control")
plt.axvline(x=0, color='k', linestyle='--', linewidth=0.5)
plt.show()
```

### Heatmap of Significant DE Genes

```python
import seaborn as sns

# Get top DE genes
top_genes = de.sort_values("lfc_mean", ascending=False).head(50).index

# Get normalized expression
norm_expr = model.get_normalized_expression(
    adata,
    indices=adata.obs["condition"].isin(["treated", "control"]),
    gene_list=top_genes
)

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(
    norm_expr.T,
    cmap="viridis",
    xticklabels=False,
    yticklabels=top_genes
)
plt.title("Top 50 DE Genes")
plt.show()
```

### Gene Ranking Plot

```python
# Plot genes ranked by effect size
de_sorted = de.sort_values("lfc_mean", ascending=False)

plt.figure(figsize=(12, 6))
plt.plot(range(len(de_sorted)), de_sorted["lfc_mean"].values)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel("Gene Rank")
plt.ylabel("Log Fold Change")
plt.title("Genes Ranked by Effect Size")
plt.show()
```

## Comparison with Traditional Methods

### scvi-tools vs. Wilcoxon Test

```python
import scanpy as sc

# Traditional Wilcoxon test
sc.tl.rank_genes_groups(
    adata,
    groupby="cell_type",
    method="wilcoxon",
    key_added="wilcoxon"
)

# scvi-tools DE
de_scvi = model.differential_expression(
    groupby="cell_type",
    group1="T cells"
)

# Compare results
wilcox_results = sc.get.rank_genes_groups_df(adata, group="T cells", key="wilcoxon")
```

**Advantages of scvi-tools**:
- Automatically accounts for batch effects
- Properly handles zero-inflation
- Provides uncertainty quantification
- No need for manual pseudocounts
- Better statistical properties

**When to use Wilcoxon**:
- Very fast exploratory analysis
- When comparison with published results using Wilcoxon is needed

## Multimodal DE

### Protein DE (totalVI)

```python
# Train totalVI on CITE-seq data
totalvi_model = scvi.model.TOTALVI(adata)
totalvi_model.train()

# RNA differential expression
rna_de = totalvi_model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    protein_expression=False  # Default value
)

# Protein differential expression
protein_de = totalvi_model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    group2="B cells",
    protein_expression=True
)

print(f"Number of DE genes: {rna_de['is_de_fdr_0.05'].sum()}")
print(f"Number of DE proteins: {protein_de['is_de_fdr_0.05'].sum()}")
```

### Differential Accessibility (PeakVI)

```python
# Train PeakVI on ATAC-seq data
peakvi_model = scvi.model.PEAKVI(atac_adata)
peakvi_model.train()

# Differential accessibility analysis
da = peakvi_model.differential_accessibility(
    groupby="cell_type",
    group1="T cells",
    group2="B cells"
)

# Interpretation is the same as DE
```

## Handling Special Cases

### Groups with Low Cell Numbers

```python
# Increase posterior sample size for stability
de = model.differential_expression(
    groupby="cell_type",
    group1="rare_type",  # e.g., 50 cells
    group2="common_type",  # e.g., 5000 cells
    n_samples=10000
)
```

### Unbalanced Comparisons

```python
# When group sizes differ significantly
# Use change mode to avoid finding tiny effects

de = model.differential_expression(
    groupby="condition",
    group1="rare_condition",
    group2="common_condition",
    mode="change",
    delta=0.5
)
```

### Multiple Hypothesis Testing Correction

```python
# Results already include correction via FDP control
# But additional corrections can be applied

from statsmodels.stats.multitest import multipletests

# Bonferroni correction (very conservative)
_, pvals_corrected, _, _ = multipletests(
    1 / (de["bayes_factor"] + 1),
    method="bonferroni"
)
```

## Performance Considerations

### Speed Optimization

```python
# Fast DE testing for large datasets
de = model.differential_expression(
    groupby="cell_type",
    group1="T cells",
    n_samples=1000,  # Reduce sample size
    batch_size=512    # Increase batch size
)
```

### Memory Management

```python
# For ultra-large datasets
# Test one comparison at a time instead of all pairwise comparisons

cell_types = adata.obs["cell_type"].unique()
for ct in cell_types:
    de = model.differential_expression(
        groupby="cell_type",
        group1=ct
    )
    # Save results
    de.to_csv(f"de_results_{ct}.csv")
```

## Best Practices

1. **Use "change" mode**: To obtain biologically interpretable results.
2. **Set an appropriate delta**: Based on biological significance.
3. **Check expression levels**: Filter out low-expression genes.
4. **Validate findings**: Check if marker genes align with common knowledge.
5. **Visualize results**: Always plot the top DE genes.
6. **Report parameters**: Document the mode, delta, and FDR used.
7. **Consider batch effects**: Use `batch_correction=True`.
8. **Multiple comparisons**: Be mindful of the impact when testing multiple groups.
9. **Sample size**: Ensure each group has enough cells (suggested >50).
10. **Biological validation**: Follow up with functional experiments.

## Example: Complete DE Analysis Workflow

```python
import scvi
import scanpy as sc
import matplotlib.pyplot as plt

# 1. Train model
scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata)
model.train()

# 2. Perform DE analysis
de_results = model.differential_expression(
    groupby="cell_type",
    group1="Disease_T_cells",
    group2="Healthy_T_cells",
    mode="change",
    delta=0.5,
    fdr_target=0.05
)

# 3. Filter and analyze
sig_genes = de_results[de_results["is_de_fdr_0.05"]]
upreg = sig_genes[sig_genes["lfc_mean"] > 0].sort_values("lfc_mean", ascending=False)
downreg = sig_genes[sig_genes["lfc_mean"] < 0].sort_values("lfc_mean")

print(f"Number of significant genes: {len(sig_genes)}")
print(f"Number of upregulated genes: {len(upreg)}")
print(f"Number of downregulated genes: {len(downreg)}")

# 4. Visualize top genes
top_genes = upreg.head(10).index.tolist() + downreg.head(10).index.tolist()

sc.pl.violin(
    adata[adata.obs["cell_type"].isin(["Disease_T_cells", "Healthy_T_cells"])],
    keys=top_genes,
    groupby="cell_type",
    rotation=90
)

# 5. Functional enrichment analysis (using external tools)
# e.g., g:Profiler, DAVID, or gprofiler-official Python package
upreg_genes = upreg.head(100).index.tolist()
# Perform pathway analysis...

# 6. Save results
de_results.to_csv("de_results_disease_vs_healthy.csv")
upreg.to_csv("upregulated_genes.csv")
downreg.to_csv("downregulated_genes.csv")
```