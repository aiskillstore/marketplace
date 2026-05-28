---
name: biopython-entrez
description: Use Bio.Entrez to access NCBI databases (e.g., PubMed/GenBank) for searching, fetching summaries, and downloading records when your workflow needs to call the NCBI E-utilities API over the network.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to search PubMed for articles by keyword, author, journal, or date range and then retrieve metadata or abstracts.
- You want to download GenBank records (e.g., nucleotide/protein sequences) in batch given accession IDs or search queries.
- You need to convert identifiers or discover related records across NCBI databases (e.g., PubMed ↔ PMC, Gene ↔ Protein) via cross-links.
- You must retrieve lightweight summaries (titles, IDs, basic metadata) before deciding which full records to fetch.
- You are integrating NCBI E-utilities into an automated pipeline and need API key usage and rate-limit-aware requests.

## Key Features

- Supports core NCBI E-utilities via `Bio.Entrez`: `esearch`, `efetch`, `esummary`, `elink`.
- Query-based searching and ID list retrieval for downstream batch operations.
- Batch downloading of records in common formats (e.g., GenBank, FASTA, XML).
- API key configuration and rate-limit-friendly request patterns.
- XML response parsing using Biopython’s Entrez parsers for structured results.
- Standardized configuration and invocation conventions:
  - Write runtime configuration to `config/task_config.json`.
  - Invoke tasks via `python scripts/<task_name>.py`.
  - Avoid stacking many CLI `--` parameters; prefer config files.
  - Use explicit UTF-8 encoding for file I/O and `ensure_ascii=False` for JSON output.

## Dependencies

- `biopython>=1.80`

## Example Usage

The following example is a complete, runnable script that:
1) searches PubMed, 2) retrieves summaries for the top results, and 3) writes output to JSON.

**1) Create `config/task_config.json`:**
```json
{
  "email": "your-email@example.com",
  "api_key": "",
  "db": "pubmed",
  "term": "CRISPR Cas9 2020[PDAT]",
  "retmax": 5,
  "out_json": "outputs/pubmed_summaries.json"
}
```

**2) Create `scripts/pubmed_summaries.py`:**
```python
import json
import os
import time
from typing import Any, Dict, List

from Bio import Entrez


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def main() -> None:
    cfg = load_config("config/task_config.json")

    Entrez.email = cfg["email"]
    api_key = cfg.get("api_key") or ""
    if api_key:
        Entrez.api_key = api_key

    db = cfg.get("db", "pubmed")
    term = cfg["term"]
    retmax = int(cfg.get("retmax", 20))
    out_json = cfg.get("out_json", "outputs/pubmed_summaries.json")

    # 1) ESearch: get IDs
    with Entrez.esearch(db=db, term=term, retmax=retmax, usehistory="n") as handle:
        search_result = Entrez.read(handle)

    id_list: List[str] = search_result.get("IdList", [])
    if not id_list:
        ensure_parent_dir(out_json)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump({"query": term, "count": 0, "items": []}, f, ensure_ascii=False, indent=2)
        return

    # Be polite with NCBI: small delay (especially without API key)
    time.sleep(0.34 if api_key else 0.5)

    # 2) ESummary: get summaries for IDs
    with Entrez.esummary(db=db, id=",".join(id_list), retmode="xml") as handle:
        summary_result = Entrez.read(handle)

    items = []
    for docsum in summary_result:
        items.append({
            "id": str(docsum.get("Id", "")),
            "title": str(docsum.get("Title", "")),
            "pubdate": str(docsum.get("PubDate", "")),
            "source": str(docsum.get("Source", "")),
            "authors": [str(a.get("Name", "")) for a in docsum.get("AuthorList", [])],
        })

    payload = {
        "query": term,
        "count": len(items),
        "items": items,
    }

    ensure_parent_dir(out_json)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
```

**3) Run:**
```bash
python scripts/pubmed_summaries.py
```

## Implementation Details

- **Core E-utilities mapping**
  - `ESearch`: builds a query against an NCBI database and returns matching IDs (and optionally WebEnv/QueryKey for history-based batching).
  - `ESummary`: returns lightweight document summaries for a list of IDs.
  - `EFetch`: downloads full records (e.g., GenBank/FASTA/XML) for IDs; choose `rettype`/`retmode` based on the target database.
  - `ELink`: discovers cross-database relationships (e.g., PubMed → PMC, Gene → Protein).

- **Batching strategy**
  - Prefer `ESearch` to obtain IDs, then call `ESummary`/`EFetch` in chunks (e.g., 100–500 IDs per request depending on payload size).
  - For large jobs, consider `usehistory="y"` in `ESearch` and then fetch via `WebEnv`/`QueryKey` to avoid very long ID lists.

- **Rate limiting and API key**
  - NCBI enforces request limits; using an API key increases allowed throughput.
  - Implement a small delay between requests and retry on transient network errors (HTTP 429/5xx) with backoff.

- **Parsing**
  - Use `Entrez.read(handle)` for structured parsing of XML responses into Python objects.
  - For raw text formats (e.g., FASTA), use `handle.read()` and write to disk with `encoding="utf-8"` where applicable.

- **Configuration and I/O conventions**
  - Store runtime parameters in `config/task_config.json` as an intermediate artifact.
  - Avoid complex CLI flags; keep scripts callable as `python scripts/<task_name>.py`.
  - Always specify `encoding="utf-8"` for file I/O and use `ensure_ascii=False` for JSON outputs.

- **Reference**
  - See `references/databases.md` for database notes and selection guidance.