---
name: cellxgene-census
description: Programmatically query the CZ CELLxGENE Census (61M+ cells) when you need cross-tissue, disease, or cell-type expression data for population-scale queries and reference atlas comparisons.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Cross-tissue or cross-disease expression comparisons** (e.g., macrophages across lung/liver/brain; COVID-19 vs control).
- **Reference atlas lookups** to contextualize findings from your own single-cell dataset (marker validation, expected expression patterns).
- **Population-scale metadata exploration** (what tissues/cell types/datasets exist; cell counts by cohort attributes).
- **Large-scale expression statistics** where results exceed RAM and require out-of-core iteration.
- **Model training on curated atlas data** (e.g., cell-type classifiers) using the experimental PyTorch integration.

## Key Features

- Programmatic access to **versioned** CZ CELLxGENE Census data (human and mouse).
- Query **cell (obs) metadata** and **gene (var) metadata** with expressive filter syntax.
- Retrieve expression as **AnnData** for small/medium queries via `get_anndata()`.
- Perform **out-of-core** expression access via SOMA `axis_query()` and chunked iteration.
- Optional **experimental ML utilities** (PyTorch dataloaders/datasets).
- Works well with **scanpy** workflows after loading AnnData.

## Dependencies

- `cellxgene-census` (latest)
- `tiledbsoma` (latest; required for `axis_query()` workflows)
- `pyarrow` (latest; used for chunked table batches)
- `anndata` (latest; for `get_anndata()` results)
- `scanpy` (latest; optional, for downstream analysis)
- `torch` (latest; optional, for experimental ML integration)

Install:
```bash
uv pip install cellxgene-census
```

Optional (experimental ML helpers):
```bash
uv pip install cellxgene-census[experimental]
```

## Example Usage

The following script is a complete, runnable example that:
1) opens a pinned Census version,  
2) explores metadata,  
3) loads a small AnnData slice, and  
4) runs an out-of-core query to compute a simple statistic.

```python
import numpy as np
import cellxgene_census
import tiledbsoma as soma

def main():
    # Pin a version for reproducibility (replace with a valid release if needed)
    census_version = "2023-07-25"

    with cellxgene_census.open_soma(census_version=census_version) as census:
        # 1) Explore summary info
        summary = census["census_info"]["summary"].read().concat().to_pandas()
        total_cells = int(summary["total_cell_count"].iloc[0])
        print(f"Census version: {census_version}")
        print(f"Total cells: {total_cells:,}")

        # 2) Explore obs metadata (always filter primary data unless you want duplicates)
        obs = cellxgene_census.get_obs(
            census,
            "homo_sapiens",
            value_filter="tissue_general == 'brain' and is_primary_data == True",
            column_names=["cell_type", "tissue_general", "disease", "donor_id"],
        )
        print(f"Brain (primary) cells returned (metadata only): {len(obs):,}")
        print("Top cell types:")
        print(obs["cell_type"].value_counts().head(10))

        # 3) Small/medium query -> AnnData in memory
        adata = cellxgene_census.get_anndata(
            census=census,
            organism="Homo sapiens",
            obs_value_filter=(
                "cell_type == 'T cell' and disease == 'COVID-19' and is_primary_data == True"
            ),
            var_value_filter="feature_name in ['CD4', 'CD8A', 'FOXP3']",
            obs_column_names=["cell_type", "tissue_general", "disease", "donor_id", "sex"],
        )
        print(adata)
        print("AnnData X shape:", adata.X.shape)

        # 4) Large-scale pattern -> out-of-core iteration with axis_query()
        # Example: compute mean of non-zero expression values for a few genes in brain.
        query = census["census_data"]["homo_sapiens"].axis_query(
            measurement_name="RNA",
            obs_query=soma.AxisQuery(
                value_filter="tissue_general == 'brain' and is_primary_data == True"
            ),
            var_query=soma.AxisQuery(
                value_filter="feature_name in ['FOXP2', 'TBR1', 'SATB2']"
            ),
        )

        n = 0
        s = 0.0
        for batch in query.X("raw").tables():
            # batch is a pyarrow.Table with at least: soma_data, soma_dim_0, soma_dim_1
            values = batch["soma_data"].to_numpy(zero_copy_only=False)
            n += values.size
            s += float(values.sum())

        mean_expr = s / n if n else np.nan
        print(f"Out-of-core mean expression (over returned entries): {mean_expr:.6g}")

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Opening the Census**
  - Use a context manager to ensure resources are released:
    - `with cellxgene_census.open_soma(...) as census: ...`
  - For reproducibility, set `census_version="YYYY-MM-DD"`; otherwise the latest stable release is used.

- **Data model (high level)**
  - Census data is stored in **SOMA** collections.
  - `census["census_info"]` provides summary tables (e.g., datasets, counts).
  - `census["census_data"][organism]` provides the experiment for an organism (e.g., `homo_sapiens`).

- **Filtering semantics**
  - `obs_value_filter` filters **cells** (obs); `var_value_filter` filters **genes** (var).
  - Combine predicates with `and` / `or`; use `in [...]` for multi-value membership.
  - Best practice: include `is_primary_data == True` to avoid double-counting cells that appear in multiple source datasets.

- **Choosing an access pattern**
  - Use `get_anndata()` when the result is expected to fit in memory (commonly < ~100k cells, depending on gene count and sparsity).
  - Use `axis_query()` + `query.X("raw").tables()` for **out-of-core** iteration and incremental statistics.

- **Expression layers / matrices**
  - Examples commonly use `X("raw")` to access raw expression.
  - Chunk iteration yields Arrow tables with:
    - `soma_data`: expression values
    - `soma_dim_0`: obs (cell) coordinates
    - `soma_dim_1`: var (gene) coordinates

- **Optional ML integration**
  - The `cellxgene_census.experimental.ml` utilities provide PyTorch-friendly datasets/dataloaders for training workflows, typically driven by the same obs/var filtering concepts used elsewhere.