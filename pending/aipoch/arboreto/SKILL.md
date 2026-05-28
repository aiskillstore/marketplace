---
name: arboreto
description: Infer gene regulatory networks (GRNs) from gene expression matrices using GRNBoost2 or GENIE3; use when analyzing bulk or single-cell RNA-seq to identify TF→target regulatory relationships.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a bulk RNA-seq expression matrix and want to infer transcription factor (TF) → target gene regulatory edges.
- You have single-cell RNA-seq data (after normalization/aggregation as needed) and want to recover putative regulatory interactions.
- You need GRN inference that can scale to large datasets using parallel/distributed execution.
- You want to compare gradient-boosting–based GRN inference (GRNBoost2) versus random-forest–based inference (GENIE3).
- You need a reproducible, scriptable pipeline to generate a ranked network edge list from expression data.

## Key Features

- GRN inference from gene expression data using **GRNBoost2** (gradient boosting) or **GENIE3** (random forest).
- Scalable execution via **Dask**, from a single machine to multi-node clusters.
- Command-line workflow for generating a GRN edge list from a tabular expression matrix.
- Algorithm guidance and comparison: see `references/algorithms.md`.
- Distributed setup notes: see `references/distributed_computing.md`.

## Dependencies

- arboreto
- dask
- distributed
- pandas
- scipy
- scikit-learn

## Example Usage

Run GRN inference from an expression matrix (TSV) and write the inferred network to an output file:

```bash
python scripts/infer_network.py \
  --input expression_data.tsv \
  --output network.tsv \
  --algo grnboost2
```

To use the alternative algorithm:

```bash
python scripts/infer_network.py \
  --input expression_data.tsv \
  --output network.tsv \
  --algo genie3
```

## Implementation Details

- **Input/Output**
  - **Input**: a gene expression matrix (e.g., TSV) where rows typically represent samples/cells and columns represent genes (exact expectations depend on `scripts/infer_network.py`).
  - **Output**: a ranked edge list representing inferred regulatory relationships (TF → target) with an importance/weight score.

- **Algorithms**
  - **GRNBoost2**: uses gradient boosting to estimate feature importance of candidate regulators for each target gene; generally preferred for larger datasets due to speed and scalability.
  - **GENIE3**: uses random forests to compute regulator importance per target gene; a classic baseline for GRN inference.
  - For a detailed comparison and practical guidance, refer to `references/algorithms.md`.

- **Parallel/Distributed Execution**
  - Computation is parallelized with **Dask**, enabling scaling from local multi-core execution to distributed clusters.
  - Cluster configuration and deployment considerations are documented in `references/distributed_computing.md`.

- **Key Parameters**
  - `--algo`: selects the inference method (`grnboost2` or `genie3`), affecting runtime and model behavior.
  - Additional runtime/cluster parameters (if exposed by the script) typically control Dask scheduling, worker counts, and resource usage.