---
name: clinvar-database
description: Utilities for querying the NCBI ClinVar database to retrieve variant records, clinical significance, and phenotype relationships; use when searching variants by gene/condition/significance, interpreting Pathogenic/Benign/VUS classifications, or annotating VCF files with ClinVar annotations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to find ClinVar variant records by **gene**, **condition/phenotype**, or **clinical significance** (e.g., *BRCA1* + *pathogenic*).
- You want to interpret a variant’s **clinical significance** (Pathogenic/Benign/VUS) and **review status** for reporting or triage.
- You need to **annotate a VCF** with ClinVar identifiers and interpretation fields as part of a variant annotation pipeline.
- You want to perform **bulk retrieval** of ClinVar datasets for offline analysis or periodic database refresh.
- You are building a workflow that relies on **NCBI E-utilities** to programmatically query ClinVar.

## Key Features

- **ClinVar search** via NCBI E-utilities using flexible query terms (gene/condition/significance).
- **Clinical interpretation retrieval**, including clinical significance categories and review status.
- **VCF annotation** workflow integration (leveraging `bcftools`) to enrich variants with ClinVar data.
- **Bulk data access** through ClinVar FTP downloads for large-scale processing.
- Reference documentation:
  - API details: `references/api_reference.md`
  - Clinical significance definitions: `references/clinical_significance.md`

## Dependencies

- Python `>=3.8`
- `requests` (Python package)
- `bcftools` (system dependency; required for VCF annotation)
- `pandas` (Python package; optional for downstream data processing)

## Example Usage

### 1) Search ClinVar for pathogenic variants in a gene

```bash
python scripts/search.py --term "BRCA1[gene] AND pathogenic[CLNSIG]"
```

### 2) Annotate a VCF with ClinVar data

```bash
python scripts/annotate.py --input input.vcf --output annotated.vcf
```

## Implementation Details

- **Search (`scripts/search.py`)**
  - Uses **NCBI E-utilities** to query ClinVar with a user-provided `--term`.
  - The query term supports ClinVar/Entrez syntax (e.g., `BRCA1[gene]`, `pathogenic[CLNSIG]`) to filter by gene and clinical significance.
  - Output is expected to include matching ClinVar records/identifiers suitable for follow-up interpretation or annotation.

- **Interpretation fields**
  - Clinical significance values (e.g., Pathogenic/Benign/VUS) and related interpretation guidance follow ClinVar conventions; see `references/clinical_significance.md`.
  - Review status (e.g., level of evidence/review) is retrieved alongside significance where available.

- **VCF annotation (`scripts/annotate.py`)**
  - Takes an input VCF (`--input`) and produces an annotated VCF (`--output`).
  - Integrates with `bcftools` to add ClinVar-derived annotations to variant records (requires `bcftools` installed and available on `PATH`).
  - Designed for pipeline use: deterministic input/output files and command-line parameters.

- **Bulk downloads**
  - Supports obtaining ClinVar datasets via FTP for offline indexing/annotation workflows.
  - Recommended when you need reproducible, high-throughput annotation without repeated API calls.