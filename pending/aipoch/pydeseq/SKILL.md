---
name: pydeseq
description: "Differential gene expression analysis for bulk RNA-seq count matrices using a DESeq2-like workflow in Python; use when you need Wald tests, FDR correction, and optional LFC shrinkage for condition/batch/covariate designs."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to run DESeq2-style differential expression in Python, especially in these scenarios:

1. **Case vs control bulk RNA-seq** from a raw integer count matrix (e.g., treated vs control).
2. **Multi-factor designs** to adjust for batch effects or covariates (e.g., `~ batch + condition`, `~ age + condition`).
3. **DESeq2 migration** when converting an R DESeq2 workflow into a Python pipeline.
4. **Pipeline integration** where results must stay in Python objects (pandas/AnnData) for downstream QC, plots, or reporting.
5. **Requests mentioning** “DESeq2”, “differential expression”, “Wald test”, “FDR/padj”, “volcano plot”, “MA plot”, or “PyDESeq2”.

## Key Features

- End-to-end DESeq2-like workflow: normalization (size factors), dispersion estimation/shrinkage, LFC fitting, outlier handling.
- **Wald tests** for differential expression with **Benjamini–Hochberg FDR** (`padj`).
- **Design formulas** in Wilkinson/R-style notation (single-factor and multi-factor).
- **Contrast-based comparisons**: `[variable, test_group, reference_group]`.
- Optional **Cook’s distance** outlier filtering and refitting.
- Optional **LFC shrinkage** (apeGLM-style) for visualization/ranking.
- Works naturally with **pandas** and can interoperate with **AnnData**.

## Dependencies

Minimum environment (as documented in the source material):

- Python **3.10–3.11**
- `pydeseq2` (install via pip/uv)
- `pandas` **>= 1.4.3**
- `numpy` **>= 1.23.0**
- `scipy` **>= 1.11.0**
- `scikit-learn` **>= 1.1.1**
- `anndata` **>= 0.8.0** (optional, for AnnData I/O)

Optional plotting:

- `matplotlib` (recommended)
- `seaborn` (optional)

Installation:

```bash
uv pip install pydeseq2
```

## Example Usage

The following script is a complete, runnable example for a standard treated-vs-control analysis.

```python
import pandas as pd
import numpy as np

from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# -----------------------------
# 1) Load inputs
# -----------------------------
# counts.csv is commonly stored as genes x samples; transpose to samples x genes.
counts_df = pd.read_csv("counts.csv", index_col=0).T
metadata = pd.read_csv("metadata.csv", index_col=0)

# Ensure sample alignment
common = counts_df.index.intersection(metadata.index)
counts_df = counts_df.loc[common]
metadata = metadata.loc[common]

# -----------------------------
# 2) Basic filtering
# -----------------------------
# Remove genes with very low total counts
min_total_counts = 10
genes_to_keep = counts_df.columns[counts_df.sum(axis=0) >= min_total_counts]
counts_df = counts_df[genes_to_keep]

# Drop samples with missing condition
metadata = metadata.dropna(subset=["condition"])
counts_df = counts_df.loc[metadata.index]

# -----------------------------
# 3) Fit DESeq2 model
# -----------------------------
dds = DeseqDataSet(
    counts=counts_df,
    metadata=metadata,
    design="~ condition",
    refit_cooks=True,
    n_cpus=1,
)
dds.deseq2()

# -----------------------------
# 4) Wald test with contrast
# -----------------------------
ds = DeseqStats(
    dds,
    contrast=["condition", "treated", "control"],
    alpha=0.05,
    cooks_filter=True,
    independent_filter=True,
)
ds.summary()

# -----------------------------
# 5) Results + optional shrinkage
# -----------------------------
res = ds.results_df.copy()
sig = res[res["padj"] < 0.05].sort_values("padj")
print(f"Significant genes (padj < 0.05): {len(sig)}")

# Optional: shrink LFC for visualization/ranking (p-values do not change)
ds.lfc_shrink()
res_shrunk = ds.results_df.copy()

# Export
res.to_csv("deseq2_results.csv")
res_shrunk.to_csv("deseq2_results_shrunk_lfc.csv")
sig.to_csv("significant_genes.csv")

# -----------------------------
# 6) Minimal volcano plot (optional)
# -----------------------------
try:
    import matplotlib.pyplot as plt

    plot_df = res.copy()
    plot_df["neglog10_padj"] = -np.log10(plot_df["padj"].clip(lower=1e-300))
    is_sig = plot_df["padj"] < 0.05

    plt.figure(figsize=(9, 5))
    plt.scatter(
        plot_df.loc[~is_sig, "log2FoldChange"],
        plot_df.loc[~is_sig, "neglog10_padj"],
        s=10,
        alpha=0.3,
        c="gray",
        label="Not significant",
    )
    plt.scatter(
        plot_df.loc[is_sig, "log2FoldChange"],
        plot_df.loc[is_sig, "neglog10_padj"],
        s=10,
        alpha=0.6,
        c="red",
        label="padj < 0.05",
    )
    plt.axhline(-np.log10(0.05), linestyle="--", color="blue", alpha=0.5)
    plt.xlabel("Log2 Fold Change")
    plt.ylabel("-Log10(adjusted p-value)")
    plt.title("Volcano Plot")
    plt.legend()
    plt.tight_layout()
    plt.savefig("volcano_plot.png", dpi=300)
except ImportError:
    pass
```

## Implementation Details

### Inputs and orientation

- **Counts matrix** must be **samples × genes** with **non-negative integer** counts.
- Many files are stored as **genes × samples**; transpose with `.T` after loading.

### Design formula (Wilkinson/R-style)

- Use strings like:
  - `~ condition` (single factor)
  - `~ batch + condition` (batch-adjusted)
  - `~ age + condition` (continuous covariate)
  - `~ group + condition + group:condition` (interaction)
- Put **adjustment variables first** (e.g., `~ batch + condition`) so the primary effect is interpreted cleanly.

### What `dds.deseq2()` does (high level)

The fitting pipeline typically includes:

1. **Size factor** estimation (library-size normalization)
2. **Gene-wise dispersion** estimation
3. Dispersion **trend** fitting and **prior** estimation
4. **MAP dispersion** shrinkage
5. **Log2 fold change** fitting under the specified design
6. **Cook’s distance** outlier detection
7. Optional **refitting** after outlier handling (`refit_cooks=True`)

### Statistical testing and multiple testing correction

- `DeseqStats(...).summary()` runs **Wald tests** for the requested coefficient/contrast.
- Output columns commonly include:
  - `baseMean`: mean normalized expression
  - `log2FoldChange`, `lfcSE`, `stat`
  - `pvalue`: raw p-value
  - `padj`: **Benjamini–Hochberg FDR** adjusted p-value
- Use `padj < alpha` (commonly 0.05) for significance.

### Contrast specification

- Format: `contrast=["variable", "test_group", "reference_group"]`
- Example: `["condition", "treated", "control"]` tests treated relative to control.

### LFC shrinkage (optional)

- `ds.lfc_shrink()` applies shrinkage to **log2FoldChange** for more stable ranking/plots.
- Shrinkage is intended for **visualization and prioritization**; statistical significance is still based on the (unshrunken) Wald test p-values.

### Notes on bundled references/scripts

If your repository includes them, use:
- `references/api_reference.md` for parameter/object details.
- `references/workflow_guide.md` for extended workflows and troubleshooting.
- `scripts/run_deseq2_analysis.py` for a CLI-style batch workflow (counts/metadata/design/contrast/output, optional plots).
