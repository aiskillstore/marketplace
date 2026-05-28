---
name: scikit-bio
description: A Python bioinformatics toolkit for sequence, phylogeny, and microbiome/community-ecology analysis; use it when you need to compute diversity/ordination/statistics from biological data and standard formats (FASTA/FASTQ/Newick/BIOM).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to parse, validate, and manipulate biological sequences (DNA/RNA/protein) and their metadata.
- You are running microbiome/community-ecology workflows (alpha/beta diversity, UniFrac, ordination, PERMANOVA).
- You need to build, transform, or compare phylogenetic trees (Newick I/O, pruning/rerooting, patristic distances).
- You want to compute and work with distance matrices and downstream multivariate analyses (PCoA, Mantel, ANOSIM).
- You need to read/write common bioinformatics formats (FASTA/FASTQ, Newick, BIOM) and convert between them.

## Key Features

- **Sequence objects**: `DNA`, `RNA`, `Protein`, and generic `Sequence` with validation, slicing, motif search, reverse complement, transcription/translation, and metadata handling.
- **Alignment utilities**: pairwise local alignment (SSW-based) and multiple sequence alignment containers (`TabularMSA`) with consensus support.
- **Phylogenetics**: `TreeNode` manipulation, tree construction from distance matrices (e.g., Neighbor Joining), and tree distance/metrics.
- **Diversity**: alpha diversity (e.g., Shannon, Faith’s PD) and beta diversity (e.g., Bray-Curtis, UniFrac) returning `Series`/`DistanceMatrix`.
- **Ordination & stats**: PCoA and ecological hypothesis tests (PERMANOVA, ANOSIM, Mantel) operating on distance matrices.
- **I/O ecosystem**: FASTA/FASTQ and Newick reading/writing; BIOM table support via `Table`.

## Dependencies

- `scikit-bio>=0.6.0`
- `numpy>=1.23`
- `pandas>=1.5`

## Example Usage

```python
# pip install scikit-bio numpy pandas

import numpy as np
import pandas as pd

import skbio
from skbio import DNA, TreeNode
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats.ordination import pcoa
from skbio.stats.distance import permanova

# ----------------------------
# 1) Sequence manipulation
# ----------------------------
seq = DNA("ACGTACGTNN--ACGT", metadata={"id": "seq1"})
seq_clean = seq.degap()
rc = seq_clean.reverse_complement()
motif_hits = seq_clean.find_with_regex("ACG[TA]")

print("Original:", str(seq))
print("Degapped:", str(seq_clean))
print("Reverse complement:", str(rc))
print("Motif hits:", list(motif_hits))

# ----------------------------
# 2) Microbiome-style counts
# ----------------------------
# rows = samples, cols = features/OTUs/ASVs
counts = np.array([
    [10,  0,  3,  1],
    [ 0,  8,  2,  0],
    [ 5,  1,  0,  4],
], dtype=int)

sample_ids = ["S1", "S2", "S3"]
feature_ids = ["F1", "F2", "F3", "F4"]

# Alpha diversity (Shannon)
shannon = alpha_diversity("shannon", counts, ids=sample_ids)
print("\nAlpha diversity (Shannon):")
print(shannon)

# Beta diversity (Bray-Curtis) -> DistanceMatrix
dm = beta_diversity("braycurtis", counts, ids=sample_ids)
print("\nBeta diversity (Bray-Curtis) distance matrix:")
print(dm)

# ----------------------------
# 3) Ordination (PCoA)
# ----------------------------
ord_res = pcoa(dm)
print("\nPCoA sample coordinates (first 2 axes):")
print(ord_res.samples[["PC1", "PC2"]])

# ----------------------------
# 4) PERMANOVA on the distance matrix
# ----------------------------
grouping = pd.Series(["A", "A", "B"], index=sample_ids)
perma = permanova(dm, grouping=grouping, permutations=99)
print("\nPERMANOVA result:")
print(perma)

# ----------------------------
# 5) Tree I/O (Newick) + basic manipulation
# ----------------------------
newick = "((F1:0.1,F2:0.2):0.3,(F3:0.2,F4:0.4):0.1);"
tree = TreeNode.read([newick])
subtree = tree.shear(["F1", "F2", "F3"])
print("\nSheared tree (tips F1,F2,F3):")
print(subtree.ascii_art())
```

## Implementation Details

- **Sequence model**
  - Use `DNA`/`RNA`/`Protein` for alphabet-aware validation and biological operations (e.g., `reverse_complement`, `transcribe`, `translate`).
  - Use `Sequence` when you need a generic container without strict alphabet constraints.
  - FASTQ quality scores (when read via scikit-bio I/O) are stored as positional metadata.

- **Diversity computations**
  - `alpha_diversity(metric, counts, ids=...)` returns a per-sample vector (typically a pandas `Series`).
  - `beta_diversity(metric, counts, ids=...)` returns a `DistanceMatrix` suitable for ordination and hypothesis tests.
  - Count inputs should be **non-negative integers** representing abundances (not relative frequencies). Phylogenetic metrics (e.g., Faith’s PD, UniFrac) additionally require a tree and feature/OTU IDs.

- **Distance matrices**
  - `DistanceMatrix` enforces symmetry and a zero diagonal; IDs are used for consistent alignment with metadata and group labels.
  - Many downstream methods (PCoA, PERMANOVA, ANOSIM, Mantel) operate directly on `DistanceMatrix`.

- **Ordination**
  - `pcoa(dm)` performs eigen-decomposition on a transformed distance matrix and returns `OrdinationResults` containing eigenvalues and sample coordinates.

- **Permutation-based statistics**
  - `permanova(dm, grouping, permutations=N)` estimates significance by permuting group labels; increase `permutations` (e.g., 999+) for more stable p-values in real analyses.