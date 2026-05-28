# gget Module Reference

## Overview
gget is a free, open-source Python package and command-line tool that enables efficient querying of genomic, proteomic, and expression data from various databases.

## Key Modules

### 1. gget ref
Fetch FTP links to reference genomes and annotations from Ensembl.
- **Source**: Ensembl
- **Output**: List of URLs (FASTA, GTF, JSON)

### 2. gget search
Query Ensembl for genes and transcripts using free-text search.
- **Source**: Ensembl
- **Parameters**: `keywords`, `species`
- **Output**: DataFrame with Ensembl IDs, gene names, descriptions.

### 3. gget info
Look up detailed information for genes/transcripts by ID.
- **Source**: Ensembl, UniProt, NCBI
- **Parameters**: `ens_ids`
- **Output**: Comprehensive metadata.

### 4. gget seq
Retrieve nucleotide or amino acid sequences.
- **Source**: Ensembl, UniProt
- **Parameters**: `ens_ids`, `translate` (bool)
- **Output**: FASTA formatted sequences.

### 5. gget alphafold
Predict protein 3D structures using AlphaFold 2.
- **Source**: AlphaFold EBI API
- **Parameters**: `sequence`
- **Output**: PDB file, PAE plot.

### 6. gget expression
Query gene expression data.
- **Sources**: 
    - **bgee**: Gene expression patterns across tissues/species.
    - **archs4**: RNA-seq data from human/mouse.
    - **cellxgene**: Single-cell RNA-seq data.

### 7. gget enrichment
Perform enrichment analysis on a list of genes.
- **Source**: Enrichr
- **Parameters**: `genes`, `database`

## Links
- **Official Documentation**: https://pachterlab.github.io/gget/
- **Repository**: https://github.com/pachterlab/gget
