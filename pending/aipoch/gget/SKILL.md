---
name: gget
description: Unified CLI/Python interface for querying genomic, proteomic, structure, and expression data across 20+ bioinformatics databases; use when you need fast, scriptable retrieval by gene/protein IDs or keywords.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to search genes/proteins by keyword and species across common databases (e.g., Ensembl/UniProt/NCBI).
- You want to fetch detailed metadata for one or many Ensembl/UniProt/NCBI identifiers.
- You need to retrieve nucleotide/protein sequences for downstream analysis or pipelines.
- You want to obtain or predict protein structures (PDB download or AlphaFold prediction) from a sequence.
- You need to query expression resources (e.g., ARCHS4, CELLxGENE, Bgee) or run enrichment analysis (Enrichr).

## Key Features

- Unified wrapper (`scripts/wrapper.py`) exposing multiple `gget` subcommands through a consistent interface.
- Gene/protein search and identifier resolution across multiple databases.
- Rich gene/protein information retrieval (annotations and metadata).
- Sequence retrieval for provided IDs.
- Structure workflows: PDB retrieval and AlphaFold-based prediction (optional plotting).
- Expression querying across popular expression atlases.
- Enrichment analysis via Enrichr.
- Backed by the upstream `gget` Python library.

## Dependencies

- Python 3.9+ (recommended)
- `gget` (latest compatible version)
- `pandas` (latest compatible version)

Install:
```bash
uv pip install gget pandas
```

## Example Usage

The skill is accessed via the unified wrapper script:

### 1) Search for genes by keyword
```bash
python scripts/wrapper.py search --keywords "insulin" --species "human"
```

### 2) Retrieve gene information by Ensembl ID
```bash
python scripts/wrapper.py info --ids "ENSG00000034713"
```

### 3) Fetch sequences by Ensembl ID
```bash
python scripts/wrapper.py seq --ids "ENSG00000034713"
```

### 4) Predict protein structure with AlphaFold (optional plotting)
```bash
python scripts/wrapper.py alphafold --sequence "MKWMFK..." --plot
```

## Implementation Details

- **Wrapper entrypoint**: `scripts/wrapper.py` acts as a dispatcher that maps subcommands (e.g., `search`, `info`, `seq`, `alphafold`) to the corresponding `gget` library functions, normalizing CLI arguments and output behavior.
- **Supported modules/functions**:
  - **ref**: Download reference genomes/annotations.
  - **search**: Keyword-based gene/protein lookup (Ensembl/UniProt/NCBI).
  - **info**: Detailed gene/protein metadata retrieval for one or multiple IDs.
  - **seq**: Nucleotide/protein sequence retrieval for provided IDs.
  - **structure**: Structure retrieval (PDB) and AlphaFold prediction.
  - **expression**: Expression queries (ARCHS4, CELLxGENE, Bgee).
  - **enrichment**: Enrichr-based enrichment analysis.
- **Notes on AlphaFold**: The `alphafold` subcommand requires additional setup depending on the environment (e.g., model/data availability). Use `--plot` to request visualization output when supported.
- **Further reference**: See `references/module_reference.md` for detailed module-level documentation and parameters.