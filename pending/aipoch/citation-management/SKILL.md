---
name: citation-management
description: Comprehensive citation management for academic research; use when you need to discover papers (Google Scholar/PubMed), extract/verify metadata (DOI/PMID/arXiv/URL), and produce validated, clean BibTeX for manuscripts.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to **find relevant or highly cited papers** on a topic using Google Scholar or PubMed.
- You have identifiers (e.g., **DOI, PMID, arXiv ID, URL**) and must **convert them into correct BibTeX**.
- You want to **verify citation accuracy** (DOI resolution, required fields, consistency with CrossRef/PubMed).
- You need to **clean, deduplicate, sort, and standardize** an existing `.bib` file before submission.
- You are preparing a thesis/manuscript and need a **reproducible workflow** from search → extraction → formatting → validation.

## Key Features

- **Paper discovery**
  - Google Scholar search with year filtering, pagination, and citation-count sorting.
  - PubMed search with MeSH terms, field tags, publication-type filters, and date ranges.
- **Metadata extraction**
  - Resolve DOI/PMID/arXiv/URL to structured metadata via CrossRef, PubMed E-utilities, and arXiv APIs.
  - Batch processing from files containing mixed identifiers.
- **BibTeX generation & cleanup**
  - Generate BibTeX entries with appropriate entry types and required fields.
  - Format, sort (key/year/author), and deduplicate BibTeX libraries.
- **Citation validation**
  - DOI resolution checks and metadata cross-checking.
  - Required-field checks by entry type, syntax validation, duplicate detection, and optional auto-fix.
- **Workflow integration**
  - Produces submission-ready `.bib` files for LaTeX/Overleaf workflows and complements literature review pipelines.

## Dependencies

- Python: 3.10+ (recommended)
- Python packages:
  - `requests>=2.31.0`
  - `scholarly>=1.7.11` (optional; required only for Google Scholar automation)

## Example Usage

A complete, end-to-end workflow that searches, extracts metadata, formats, deduplicates, and validates a bibliography:

```bash
# 1) Search PubMed (biomedical focus)
python scripts/search_pubmed.py \
  --query '"CRISPR-Cas Systems"[MeSH] AND "Gene Editing"[MeSH]' \
  --date-start 2020-01-01 \
  --date-end 2024-12-31 \
  --limit 200 \
  --output crispr_pubmed.json

# 2) Search Google Scholar (broad coverage)
python scripts/search_google_scholar.py "CRISPR gene editing therapeutics" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --output crispr_scholar.json

# 3) Extract metadata from search outputs (or mixed identifiers)
cat crispr_pubmed.json crispr_scholar.json > combined_results.json
python scripts/extract_metadata.py \
  --input combined_results.json \
  --output combined.bib

# 4) Add known papers by DOI (append)
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2 >> combined.bib
python scripts/doi_to_bibtex.py 10.1126/science.aam9317 >> combined.bib

# 5) Format + deduplicate + sort (newest first)
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output formatted.bib

# 6) Validate + auto-fix common issues + emit report
python scripts/validate_citations.py formatted.bib \
  --auto-fix \
  --report validation.json \
  --output final_references.bib

# 7) Inspect validation results
cat validation.json
```

## Implementation Details

### 1) Search (Discovery)

- **Google Scholar** (`scripts/search_google_scholar.py`)
  - Supports query operators such as exact phrases (`"deep learning"`), author filters (`author:LeCun`), title-only (`intitle:"neural networks"`), exclusions (`-survey`), and year ranges.
  - Typical parameters:
    - `--year-start`, `--year-end`: constrain publication years
    - `--limit`: cap results
    - `--sort-by citations`: prioritize highly cited papers (when supported by the script)

- **PubMed** (`scripts/search_pubmed.py`)
  - Uses NCBI E-utilities (e.g., ESearch/EFetch/ESummary) to retrieve PMIDs and metadata.
  - Typical parameters:
    - `--query`: supports MeSH terms, field tags, and Boolean logic
    - `--date-start`, `--date-end`: publication date filtering
    - `--publication-types`: e.g., `Clinical Trial,Review`
    - `--format`: JSON or BibTeX output (if supported)

(See: `references/google_scholar_search.md`, `references/pubmed_search.md`)

### 2) Metadata Extraction (Normalization)

- **Identifier inputs**: DOI, PMID, arXiv ID, URL, or mixed lists/files.
- **Primary sources**:
  - CrossRef API for DOI-centric journal metadata
  - PubMed E-utilities for biomedical records (PMID/PMCID, MeSH, abstracts)
  - arXiv API for preprints and versioned records
  - DataCite API for datasets/software DOIs (if implemented/used)
- **Field mapping goals**:
  - Required: `author`, `title`, `year`
  - Articles: `journal`, `volume`, `number`, `pages`, `doi`
  - Conferences: `booktitle`, `pages`
  - Preprints: repository + identifier (e.g., `eprint`, `archivePrefix`)

(See: `references/metadata_extraction.md`)

### 3) BibTeX Formatting (Quality & Consistency)

- Entry types commonly produced: `@article`, `@inproceedings`, `@book`, `@misc`.
- Formatting rules enforced/encouraged:
  - Page ranges use `--` (e.g., `123--145`)
  - Protect capitalization in titles with braces (e.g., `{CRISPR}`)
  - Consistent author formatting (`Last, First and Last, First`)
  - Stable citation keys (project convention; often `FirstAuthorYearKeyword`)

(See: `references/bibtex_formatting.md`)

### 4) Validation (Correctness)

Validation typically checks:

- **DOI validity**: resolves via `doi.org` and matches CrossRef metadata.
- **Required fields**: present per entry type; no empty critical fields.
- **Consistency**: year format, numeric volume/issue, page-range syntax, URL accessibility.
- **Duplicates**: same DOI, near-identical titles, or same author/year/title combinations.
- **BibTeX syntax**: braces/quotes, commas, unique keys, special character handling.

Outputs may include a machine-readable report (e.g., JSON) with `errors` and `warnings`.
(See: `references/citation_validation.md`)