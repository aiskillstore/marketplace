---
name: uniprot-database
description: Direct REST API access to UniProt for protein search, entry retrieval, and identifier mapping; use when you need programmatic UniProtKB queries or cross-database ID conversion.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to search UniProtKB with Lucene-style queries (e.g., by gene name, organism, reviewed status).
- You want to fetch the full details of a specific protein entry by UniProt accession (e.g., `P12345`).
- You need to map identifiers between databases (e.g., gene names, Ensembl IDs, RefSeq IDs ↔ UniProt accessions).
- You are building pipelines that require automated protein annotation retrieval in JSON/TSV/FASTA formats.
- You need a lightweight client that talks directly to UniProt’s REST API without additional SDKs.

## Key Features

- **Protein search** via UniProtKB REST endpoint using Lucene query syntax.
- **Entry retrieval** by accession with selectable output formats.
- **Identifier mapping** between supported source/target databases using UniProt ID mapping service.
- **Format control** (default `json`) for consistent downstream parsing.
- **Reference docs** for query syntax and available API fields:
  - `references/query_syntax.md`
  - `references/api_fields.md`

## Dependencies

- Python `>=3.8`
- `requests >=2.31.0`

## Example Usage

```python
import time
import requests

BASE = "https://rest.uniprot.org"

def search_protein(query: str, fmt: str = "json", size: int = 5):
    """
    Search UniProtKB using Lucene-style query syntax.
    """
    url = f"{BASE}/uniprotkb/search"
    params = {"query": query, "format": fmt, "size": size}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json() if fmt == "json" else r.text

def retrieve_entry(accession: str, fmt: str = "json"):
    """
    Retrieve a UniProtKB entry by accession.
    """
    url = f"{BASE}/uniprotkb/{accession}"
    params = {"format": fmt}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json() if fmt == "json" else r.text

def id_mapping(from_db: str, to_db: str, ids, poll_interval_s: float = 1.0):
    """
    Map identifiers using UniProt ID Mapping.
    ids can be a list of strings or a comma-separated string.
    """
    if isinstance(ids, (list, tuple)):
        ids = ",".join(ids)

    # 1) Submit mapping job
    submit_url = f"{BASE}/idmapping/run"
    r = requests.post(
        submit_url,
        data={"from": from_db, "to": to_db, "ids": ids},
        timeout=30,
    )
    r.raise_for_status()
    job_id = r.json()["jobId"]

    # 2) Poll job status
    status_url = f"{BASE}/idmapping/status/{job_id}"
    while True:
        s = requests.get(status_url, timeout=30)
        s.raise_for_status()
        payload = s.json()
        if payload.get("jobStatus") in (None, "FINISHED"):
            break
        if payload.get("jobStatus") == "FAILED":
            raise RuntimeError(f"ID mapping failed: {payload}")
        time.sleep(poll_interval_s)

    # 3) Fetch results (JSON)
    results_url = f"{BASE}/idmapping/results/{job_id}"
    res = requests.get(results_url, params={"format": "json"}, timeout=30)
    res.raise_for_status()
    return res.json()

if __name__ == "__main__":
    # Search example: human BRCA1
    search = search_protein("gene:BRCA1 AND organism_id:9606", size=3)
    print("Search results (first accessions):",
          [item["primaryAccession"] for item in search.get("results", [])])

    # Retrieve entry example
    entry = retrieve_entry("P38398")  # UniProt accession for human BRCA1 (example)
    print("Entry primaryAccession:", entry.get("primaryAccession"))
    print("Protein name:", entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value"))

    # ID mapping example: gene name -> UniProtKB
    mapping = id_mapping(from_db="Gene_Name", to_db="UniProtKB", ids=["BRCA1"])
    print("Mapping results keys:", mapping.keys())
```

## Implementation Details

- **Search Protein**
  - Uses `GET /uniprotkb/search`
  - Key parameters:
    - `query`: Lucene-style query string (see `references/query_syntax.md`)
    - `format`: output format (default `json`)
    - Optional common parameters: `size`, `fields`, `sort`
  - Returns parsed JSON when `format=json`, otherwise raw text.

- **Retrieve Entry**
  - Uses `GET /uniprotkb/{accession}`
  - Key parameters:
    - `accession`: UniProt accession (e.g., `P12345`)
    - `format`: output format (default `json`)
  - Suitable for fetching full record details for a known accession.

- **ID Mapping**
  - Uses UniProt asynchronous mapping workflow:
    1. `POST /idmapping/run` with `from`, `to`, `ids`
    2. Poll `GET /idmapping/status/{jobId}` until finished
    3. Fetch `GET /idmapping/results/{jobId}?format=json`
  - `ids` accepts either a list or a comma-separated string.
  - Recommended parameters:
    - `poll_interval_s`: controls polling frequency to avoid excessive requests.
  - `from_db` / `to_db` must match UniProt-supported database identifiers (consult UniProt mapping documentation as needed).