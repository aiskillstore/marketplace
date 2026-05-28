---
name: biopython-alignment
description: Sequence alignment and alignment file processing with Biopython (Bio.Align/Bio.AlignIO), triggered when you need global/local pairwise alignment, MSA read/write/format conversion, or alignment statistics/filtering.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# biopython-alignment

## When to Use

- You need **global alignment** between two protein (or nucleotide) sequences and want a reproducible score and aligned strings.
- You need **local alignment** to find the best matching fragment/subsequence between two DNA/RNA/protein sequences.
- You need to **read, write, or convert** multiple sequence alignment (MSA) files (e.g., FASTA/Clustal/Stockholm) using Biopython I/O.
- You want to compute **alignment statistics** (e.g., identity, coverage, conservation per column) and filter alignments by thresholds.
- You need to apply **substitution matrices** (e.g., BLOSUM62) and tune gap penalties for biologically meaningful scoring.

## Key Features

- Pairwise alignment via `Bio.Align.PairwiseAligner` (global and local modes).
- Alignment scoring with configurable match/mismatch and gap penalties.
- Protein substitution matrices via `Bio.Align.substitution_matrices` (e.g., BLOSUM/PAM).
- MSA parsing and serialization via `Bio.AlignIO` (read/write/format conversion).
- Basic alignment statistics: identity, aligned length, coverage, and MSA column conservation.

## Dependencies

- `biopython>=1.81`
- `numpy>=1.21`

## Example Usage

```python
# -*- coding: utf-8 -*-
"""
Runnable examples for:
1) Global protein alignment
2) Local DNA alignment (best fragment)
3) MSA parsing + column conservation

Requires: biopython, numpy
"""

from __future__ import annotations

from io import StringIO
import numpy as np

from Bio.Align import PairwiseAligner
from Bio.Align import substitution_matrices
from Bio import AlignIO


def global_protein_alignment(seq_a: str, seq_b: str) -> None:
    matrix = substitution_matrices.load("BLOSUM62")

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.substitution_matrix = matrix
    aligner.open_gap_score = -10.0
    aligner.extend_gap_score = -0.5

    alignments = aligner.align(seq_a, seq_b)
    best = alignments[0]

    print("=== Global protein alignment (best) ===")
    print("Score:", best.score)
    print(best)


def local_dna_alignment_best_fragment(seq_a: str, seq_b: str) -> None:
    aligner = PairwiseAligner()
    aligner.mode = "local"
    aligner.match_score = 2.0
    aligner.mismatch_score = -1.0
    aligner.open_gap_score = -2.0
    aligner.extend_gap_score = -0.5

    best = aligner.align(seq_a, seq_b)[0]

    # Extract the aligned fragment coordinates from the first aligned block.
    # aligned is a tuple: (aligned_coords_in_seq_a, aligned_coords_in_seq_b)
    a_blocks, b_blocks = best.aligned
    a_start, a_end = a_blocks[0]
    b_start, b_end = b_blocks[0]

    print("=== Local DNA alignment (best) ===")
    print("Score:", best.score)
    print(best)
    print("Best fragment in seq_a:", seq_a[a_start:a_end], f"(coords {a_start}:{a_end})")
    print("Best fragment in seq_b:", seq_b[b_start:b_end], f"(coords {b_start}:{b_end})")


def msa_column_conservation(fasta_text: str) -> None:
    handle = StringIO(fasta_text)
    msa = AlignIO.read(handle, "fasta")  # MultipleSeqAlignment

    # Convert to a 2D array of characters: shape (n_seqs, aln_len)
    arr = np.array([list(str(rec.seq)) for rec in msa], dtype="U1")
    n_seqs, aln_len = arr.shape

    # Conservation per column: fraction of the most common non-gap character.
    # Treat '-' as gap; ignore gaps when computing the most common residue.
    conservation = []
    for j in range(aln_len):
        col = arr[:, j]
        col = col[col != "-"]
        if col.size == 0:
            conservation.append(0.0)
            continue
        values, counts = np.unique(col, return_counts=True)
        conservation.append(float(counts.max() / counts.sum()))

    print("=== MSA column conservation ===")
    print("n_seqs:", n_seqs, "aln_len:", aln_len)
    print("conservation:", [round(x, 3) for x in conservation])


def main() -> None:
    # 1) Global alignment (protein)
    seq_a = "MKTAYIAKQRQISFVKSHFSRQDILD"
    seq_b = "MKLAYIAKQRQISFVKSHFTRQDILN"
    global_protein_alignment(seq_a, seq_b)

    # 2) Local alignment (DNA)
    seq_a = "ATGCGTACGTTAGC"
    seq_b = "GGGATGCGTACGAAAC"
    local_dna_alignment_best_fragment(seq_a, seq_b)

    # 3) MSA conservation (FASTA)
    fasta_text = ">s1\nACGTACGT\n>s2\nACGTTCGT\n>s3\nACGTACGA\n"
    msa_column_conservation(fasta_text)


if __name__ == "__main__":
    main()
```

## Implementation Details

- **Pairwise alignment engine**: uses `Bio.Align.PairwiseAligner`, which performs dynamic programming alignment under the selected mode:
  - `mode="global"`: aligns full-length sequences end-to-end.
  - `mode="local"`: finds the highest-scoring matching region (best subsequence pair).
- **Scoring configuration**:
  - For proteins, prefer `substitution_matrix` (e.g., `BLOSUM62`) plus gap penalties (`open_gap_score`, `extend_gap_score`).
  - For nucleotides, a simple scheme is common: `match_score`, `mismatch_score`, and gap penalties.
- **Selecting the best alignment**: `aligner.align(a, b)` returns an iterable of alignments sorted by score; use `[0]` for the top-scoring result.
- **Local “best fragment” extraction**:
  - `alignment.aligned` returns aligned coordinate blocks for each sequence.
  - The first block `(start, end)` typically corresponds to the highest-scoring contiguous aligned region; slice the original sequences with these coordinates to obtain the fragment.
- **MSA I/O and statistics**:
  - `Bio.AlignIO.read(handle, fmt)` parses an alignment into a `MultipleSeqAlignment`.
  - Column conservation can be computed as:  
    `max_count(non-gap residues in column) / total_non_gap_count(column)`.
- **Operational conventions (recommended)**:
  - Store runtime configuration in `config/task_config.json` and invoke scripts as `python scripts/<task_name>.py`.
  - Avoid stacking many CLI `--` parameters; keep parameters in the config file.
  - Always specify `encoding="utf-8"` for file I/O; for JSON output use `ensure_ascii=False`.