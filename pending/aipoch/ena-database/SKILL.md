---
name: ena-database
description: Access the European Nucleotide Archive (ENA) via REST APIs and FTP/Aspera to search and retrieve sequences, raw reads (FASTQ), assemblies, and metadata when you have accession IDs or need metadata-driven discovery for genomics pipelines.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. Download raw sequencing reads (FASTQ) for a run/experiment/study using ENA accessions (e.g., `ERR...`, `SRR...`, `PRJ...`).
2. Find samples, runs, experiments, or assemblies by metadata filters (organism, platform, collection date, geography, etc.).
3. Retrieve record metadata (XML/JSON/TSV) for reproducible reporting and pipeline inputs.
4. Query taxonomic lineage/rank for organisms to drive filtering or grouping in analyses.
5. Perform bulk discovery + bulk download workflows (search first, then fetch many files via FTP/Aspera/tools).

## Key Features

- **Multi-object ENA coverage**: studies/projects, samples, experiments, runs, assemblies, sequences, analyses, taxonomy records.
- **Two primary API styles**:
  - **Portal API** for advanced search and metadata export (JSON/TSV/CSV).
  - **Browser API** for direct record retrieval by accession (XML).
- **Multiple data formats**: FASTQ, FASTA, BAM/CRAM, EMBL flat file, plus metadata in XML/JSON/TSV.
- **Bulk transfer options**: FTP/Aspera and command-line tooling patterns for large datasets.
- **Cross-references and reference retrieval**: ENA xref service and CRAM reference registry endpoints.
- **Operational guidance**: rate limiting awareness (HTTP 429) and best practices for robust pipelines.

> For detailed endpoint and parameter documentation, see `references/api_reference.md`.

## Dependencies

- Python `>=3.9`
- `requests >=2.31.0`

Optional (recommended for XML parsing when using the Browser API):
- `lxml >=4.9.0`

## Example Usage

The following script is a complete, runnable example that:
1) searches ENA for runs in a study via the **Portal API** (JSON), then  
2) fetches one run’s record via the **Browser API** (XML), and  
3) retrieves taxonomy lineage via the **Taxonomy REST API**.

```python
#!/usr/bin/env python3
import sys
import time
import requests

PORTAL_SEARCH = "https://www.ebi.ac.uk/ena/portal/api/search"
BROWSER_XML = "https://www.ebi.ac.uk/ena/browser/api/xml"
TAXONOMY = "https://www.ebi.ac.uk/ena/taxonomy/rest"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ena-database-skill/1.0"})

def get_with_backoff(url, params=None, max_retries=6, timeout=30):
    delay = 1.0
    for attempt in range(max_retries):
        r = SESSION.get(url, params=params, timeout=timeout)
        if r.status_code != 429:
            r.raise_for_status()
            return r
        time.sleep(delay)
        delay *= 2
    r.raise_for_status()

def search_runs_by_study(study_accession, limit=5):
    params = {
        "result": "read_run",
        "query": f"study_accession={study_accession}",
        "format": "json",
        "limit": limit,
        # Ask for a few useful fields; adjust as needed for your pipeline.
        "fields": "run_accession,study_accession,sample_accession,experiment_accession,tax_id,scientific_name,fastq_ftp"
    }
    r = get_with_backoff(PORTAL_SEARCH, params=params)
    return r.json()

def fetch_run_xml(run_accession):
    url = f"{BROWSER_XML}/{run_accession}"
    r = get_with_backoff(url)
    return r.text  # XML string

def fetch_taxonomy_lineage(tax_id):
    url = f"{TAXONOMY}/tax-id/{tax_id}"
    r = get_with_backoff(url)
    return r.json()

def main():
    if len(sys.argv) < 2:
        print("Usage: python ena_example.py <STUDY_ACCESSION>  (e.g., PRJEB1234)", file=sys.stderr)
        sys.exit(2)

    study = sys.argv[1]
    runs = search_runs_by_study(study_accession=study, limit=5)

    if not runs:
        print(f"No runs found for study {study}")
        return

    print(f"Found {len(runs)} runs for study {study}")
    first = runs[0]
    run_acc = first.get("run_accession")
    tax_id = first.get("tax_id")

    print("\nFirst run summary (Portal API JSON):")
    for k in ["run_accession", "sample_accession", "experiment_accession", "scientific_name", "tax_id", "fastq_ftp"]:
        print(f"  {k}: {first.get(k)}")

    if run_acc:
        xml = fetch_run_xml(run_acc)
        print("\nBrowser API XML (first 600 chars):")
        print(xml[:600])

    if tax_id:
        tax = fetch_taxonomy_lineage(tax_id)
        print("\nTaxonomy lineage (ENA Taxonomy REST API):")
        # Response is typically a list with one record
        rec = tax[0] if isinstance(tax, list) and tax else tax
        print(f"  scientificName: {rec.get('scientificName')}")
        print(f"  rank: {rec.get('rank')}")
        print(f"  lineage: {rec.get('lineage')}")

if __name__ == "__main__":
    main()
```

Run:

```bash
python ena_example.py PRJEB1234
```

## Implementation Details

### ENA data model (what you query and retrieve)
ENA organizes records into common object types used in pipelines:

- **Study/Project**: umbrella entity for a dataset; primary unit for citation.
- **Sample**: biological material metadata.
- **Experiment**: library prep + instrument metadata.
- **Run**: the actual sequencing output files (often FASTQ) for one run.
- **Assembly**: genome/transcriptome/metagenome assemblies.
- **Sequence/Record**: annotated sequences (e.g., EMBL records).
- **Analysis**: computational results derived from sequence data.
- **Taxonomy**: lineage and rank information.

### API selection guidance
- **Portal API** (`/ena/portal/api/search`): use for *searching and exporting metadata* at scale.
  - Typical outputs: `json`, `tsv`, `csv`.
  - Supports complex query expressions (see `references/api_reference.md`).
- **Browser API** (`/ena/browser/api/xml/{accession}`): use for *direct retrieval by accession*.
  - Output: XML (parse with an XML parser, not regex).
- **Taxonomy REST API** (`/ena/taxonomy/rest/...`): use for lineage/rank lookups.
- **Cross-reference service**: `https://www.ebi.ac.uk/ena/xref/rest/` for related records in external databases.
- **CRAM reference registry**: `https://www.ebi.ac.uk/ena/cram/` for reference sequence retrieval by checksum.

### Query parameters and outputs (practical notes)
- **Portal API core parameters** (commonly used):
  - `result`: record type (e.g., `sample`, `read_run`, `assembly`)
  - `query`: filter expression (e.g., `study_accession=PRJEB1234`, `tax_tree(Escherichia coli)`)
  - `fields`: comma-separated fields to return (improves performance vs returning everything)
  - `format`: `json`/`tsv`/`csv`
  - `limit` (and pagination where applicable)
- **File retrieval**:
  - For raw reads, prefer extracting file locations (e.g., `fastq_ftp`) from Portal results, then download via FTP/Aspera for scale.

### Rate limiting and robustness
- ENA APIs are rate-limited (commonly documented as **50 requests/second**). Exceeding limits returns **HTTP 429**.
- Implement:
  - exponential backoff on 429,
  - request consolidation (fetch multiple fields in one query),
  - bulk download mechanisms for large datasets instead of per-accession loops.

### Recommended pipeline pattern (search → resolve → download)
1. **Search** with Portal API to obtain accessions and file URLs.
2. **Resolve** any needed details (optional) via Browser API XML for specific accessions.
3. **Download** large files via FTP/Aspera or tooling (rather than API streaming).
4. **Cache** taxonomy lookups when processing many records to reduce repeated calls.