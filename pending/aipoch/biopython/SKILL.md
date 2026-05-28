---
name: biopython
description: A comprehensive toolbox for computational molecular biology; use it when you need programmatic sequence/structure parsing, batch bioinformatics pipelines, or automated NCBI/BLAST workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

- Batch-process DNA/RNA/protein sequences (translation, reverse complement, statistics) as part of a custom pipeline.
- Parse, validate, convert, or stream large bioinformatics files (FASTA/FASTQ/GenBank/PDB/mmCIF) without loading everything into memory.
- Programmatically query and download records from NCBI (GenBank, PubMed, Gene, Protein) via `Bio.Entrez`, respecting rate limits.
- Automate BLAST searches (web or local) and parse results to extract top hits and metadata.
- Build or manipulate phylogenetic trees from alignments or distance matrices (e.g., NJ trees) for downstream analysis.

> Note: For quick one-off queries, tools like **gget** may be more convenient; for multi-service API aggregation, **bioservices** may be a better fit.

## Key Features

- **Sequence objects and utilities**: `Bio.Seq`, `Bio.SeqRecord`, `Bio.SeqUtils` (GC fraction, molecular weight, translation, etc.).
- **File I/O and format conversion**: `Bio.SeqIO`, `Bio.AlignIO` for FASTA/FASTQ/GenBank and alignment formats.
- **NCBI access**: `Bio.Entrez` for `esearch`, `efetch`, `elink`, and structured parsing via `Entrez.read`.
- **BLAST**: `Bio.Blast.NCBIWWW` for remote BLAST and `Bio.Blast.NCBIXML` for XML parsing.
- **Structural bioinformatics**: `Bio.PDB` for PDB/mmCIF parsing, hierarchy traversal, and geometry calculations.
- **Phylogenetics**: `Bio.Phylo` and `Bio.Phylo.TreeConstruction` for tree I/O, distances, and construction.

Reference guides (if present in this repository) can be consulted for deeper module-specific patterns:
- `references/sequence_io.md`
- `references/alignment.md`
- `references/databases.md`
- `references/blast.md`
- `references/structure.md`
- `references/phylogenetics.md`
- `references/advanced.md`

## Dependencies

- Python **>= 3.8** (Biopython 1.85 supports Python 3)
- `biopython==1.85`
- `numpy>=1.20` (required by Biopython)

Install:

```bash
python -m pip install "biopython==1.85" "numpy>=1.20"
```

## Example Usage

A complete, runnable example that:

1) parses a FASTA file,  
2) computes GC fraction,  
3) runs a remote BLAST (optional),  
4) fetches the top hit from NCBI,  
5) prints basic results.

Create `example_biopython_pipeline.py`:

```python
from __future__ import annotations

import os
import time
from typing import Optional

from Bio import Entrez, SeqIO
from Bio.SeqUtils import gc_fraction

# Optional BLAST (remote). Comment out if you do not want network calls.
from Bio.Blast import NCBIWWW, NCBIXML


def configure_entrez() -> None:
    """
    NCBI requires an email. An API key increases rate limits.
    Set these via environment variables to avoid hardcoding secrets.
    """
    email = os.environ.get("NCBI_EMAIL")
    if not email:
        raise RuntimeError("Set NCBI_EMAIL env var (required by NCBI). Example: export NCBI_EMAIL='you@org.org'")
    Entrez.email = email

    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        Entrez.api_key = api_key


def read_first_fasta_record(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return next(SeqIO.parse(handle, "fasta"))


def blast_top_accession(sequence: str, program: str = "blastn", database: str = "nt") -> Optional[str]:
    """
    Remote BLAST can be slow and rate-limited. For large-scale BLAST, prefer local BLAST+.
    """
    result_handle = NCBIWWW.qblast(program, database, sequence)
    blast_record = NCBIXML.read(result_handle)

    if not blast_record.alignments:
        return None

    # Many BLAST titles include multiple identifiers; accession is usually available directly.
    return blast_record.alignments[0].accession


def fetch_fasta_by_accession(accession: str) -> str:
    with Entrez.efetch(db="nucleotide", id=accession, rettype="fasta", retmode="text") as handle:
        return handle.read()


def main() -> None:
    configure_entrez()

    record = read_first_fasta_record("input.fasta")
    seq = record.seq

    print(f"ID: {record.id}")
    print(f"Length: {len(seq)}")
    print(f"GC fraction: {gc_fraction(seq):.2%}")

    # Be polite to NCBI services in batch workflows.
    time.sleep(0.34)

    top_acc = blast_top_accession(str(seq))
    if not top_acc:
        print("No BLAST hits found.")
        return

    print(f"Top BLAST accession: {top_acc}")

    time.sleep(0.34)
    fasta_text = fetch_fasta_by_accession(top_acc)
    print("Top hit FASTA:")
    print(fasta_text)


if __name__ == "__main__":
    main()
```

Run:

```bash
export NCBI_EMAIL="your.email@example.com"
# export NCBI_API_KEY="your_ncbi_api_key"  # optional
python example_biopython_pipeline.py
```

Provide an `input.fasta` in the same directory, e.g.:

```text
>demo
ATCGATCGATCGATCGATCG
```

## Implementation Details

- **Streaming I/O for large datasets**: Prefer iterator-based parsing (`SeqIO.parse`) to avoid loading entire files into memory. Use `SeqIO.read` only when exactly one record is expected.
- **Entrez configuration and rate limits**:
  - Always set `Entrez.email` (NCBI requirement).
  - Optionally set `Entrez.api_key` to increase request limits.
  - In batch jobs, add delays (e.g., `time.sleep(0.34)` as a conservative baseline) and implement retries for transient HTTP failures.
- **BLAST considerations**:
  - `NCBIWWW.qblast(...)` is convenient but can be slow and is not ideal for high-throughput workloads.
  - Parse results with `NCBIXML.read(...)` (single record) or `NCBIXML.parse(...)` (multiple records).
  - Filter hits by HSP metrics (e-value, identity) by iterating `alignment.hsps`.
- **Sequence statistics and transformations**:
  - Use `Bio.SeqUtils.gc_fraction(seq)` for GC fraction (returns 0–1).
  - Use `seq.translate(table=...)` with the correct genetic code table for reproducibility.
- **Structure parsing (if used)**:
  - Use `Bio.PDB.PDBParser(QUIET=True)` to suppress warnings when appropriate.
  - Navigate the SMCRA hierarchy (Structure → Model → Chain → Residue → Atom) for robust traversal and geometry calculations.
- **Reproducibility**:
  - Record key parameters (file formats, translation table, BLAST program/database, e-value thresholds, NCBI query terms).
  - Cache downloaded records when iterating to avoid repeated network calls.