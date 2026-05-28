---
name: pdb-database
description: Access the RCSB Protein Data Bank (PDB) to search, download, and programmatically retrieve 3D macromolecular structures and metadata; use when you need structure discovery (text/sequence/3D similarity) or automated structural data ingestion for structural biology and drug discovery workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

- Find protein/nucleic acid 3D structures by **keywords**, **organism**, **experimental method**, or **resolution**.
- Identify related structures via **sequence similarity** (e.g., homolog search for modeling).
- Identify related structures via **3D structure similarity** (e.g., fold-level comparisons).
- **Download coordinates** (PDB/mmCIF) for downstream analysis, visualization, docking, or modeling.
- Run **batch retrieval** of metadata/coordinates to feed pipelines in drug discovery, protein engineering, or structural bioinformatics.

## Key Features

- Text and attribute-based search over RCSB PDB entries.
- Sequence similarity search with configurable thresholds (e-value, identity).
- Structure similarity search using an existing entry as a query.
- Programmatic metadata retrieval via the RCSB Data API (schema-based or GraphQL).
- Direct coordinate downloads in **PDB** and **mmCIF** formats.
- Batch processing patterns for multiple PDB IDs.

## Dependencies

- `rcsb-api` (latest recommended; provides `rcsbapi.search` and `rcsbapi.data`)
- `requests>=2.0` (HTTP downloads)
- `biopython>=1.80` (optional; parsing/analyzing PDB coordinates)

Install (example):

```bash
uv pip install rcsb-api requests biopython
```

## Example Usage

The following script is end-to-end runnable: it searches for a target, fetches metadata, downloads coordinates, and parses the structure.

```python
#!/usr/bin/env python3
import pathlib
import requests

from rcsbapi.search import TextQuery, AttributeQuery
from rcsbapi.search.attrs import rcsb_entry_info
from rcsbapi.data import fetch, Schema

from Bio.PDB import PDBParser


def download_text(url: str, out_path: pathlib.Path) -> None:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.write_text(r.text, encoding="utf-8")


def main():
    out_dir = pathlib.Path("pdb_out")
    out_dir.mkdir(exist_ok=True)

    # 1) Search: hemoglobin entries with resolution < 2.0 Å
    q_text = TextQuery("hemoglobin")
    q_res = AttributeQuery(
        attribute=rcsb_entry_info.resolution_combined,
        operator="less",
        value=2.0,
    )
    query = q_text & q_res

    pdb_ids = list(query())[:5]
    if not pdb_ids:
        raise SystemExit("No results found.")
    pdb_id = pdb_ids[0]
    print(f"Selected PDB ID: {pdb_id}")

    # 2) Fetch entry metadata
    entry = fetch(pdb_id, schema=Schema.ENTRY)
    title = entry.get("struct", {}).get("title")
    method = (entry.get("exptl") or [{}])[0].get("method")
    resolution = (entry.get("rcsb_entry_info") or {}).get("resolution_combined")
    deposit_date = (entry.get("rcsb_accession_info") or {}).get("deposit_date")

    print("Metadata:")
    print(f"  Title: {title}")
    print(f"  Method: {method}")
    print(f"  Resolution: {resolution}")
    print(f"  Deposit date: {deposit_date}")

    # 3) Download coordinates (PDB and mmCIF)
    pdb_path = out_dir / f"{pdb_id}.pdb"
    cif_path = out_dir / f"{pdb_id}.cif"

    download_text(f"https://files.rcsb.org/download/{pdb_id}.pdb", pdb_path)
    download_text(f"https://files.rcsb.org/download/{pdb_id}.cif", cif_path)
    print(f"Downloaded: {pdb_path} and {cif_path}")

    # 4) Parse PDB coordinates (example: count atoms)
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_id, str(pdb_path))

    atom_count = sum(1 for _ in structure.get_atoms())
    chain_ids = sorted({chain.id for chain in structure.get_chains()})
    print("Parsed structure:")
    print(f"  Chains: {chain_ids}")
    print(f"  Atom count: {atom_count}")


if __name__ == "__main__":
    main()
```

## Implementation Details

### Search Modes and Query Composition

- **Text search** uses free-text matching over entry annotations (titles, keywords, descriptions).
- **Attribute search** filters by structured fields (e.g., organism, method, resolution).
- **Sequence similarity search** typically supports:
  - `evalue_cutoff`: lower is more stringent (fewer, more confident hits).
  - `identity_cutoff`: fraction identity threshold (e.g., `0.9` for near-identical).
- **Structure similarity search** uses an existing structure (e.g., an `entry_id`) as the geometric reference.
- Queries can be combined with boolean logic:
  - `query1 & query2` (AND)
  - `query1 | query2` (OR)
  - `~query` (NOT), where supported by the client

### Data Retrieval (Schema vs GraphQL)

- **Schema-based fetch** (e.g., `Schema.ENTRY`, `Schema.POLYMER_ENTITY`) is convenient for common objects and stable access patterns.
- **GraphQL fetch** is best when you need a custom selection of fields in one request (reduce round-trips and payload).

Example GraphQL pattern:

```python
from rcsbapi.data import fetch

query = """
{
  entry(entry_id: "4HHB") {
    struct { title }
    exptl { method }
    rcsb_entry_info { resolution_combined deposited_atom_count }
  }
}
"""
data = fetch(query_type="graphql", query=query)
```

### Coordinate Downloads and Formats

- **PDB**: legacy text format; widely supported but less expressive for large/complex structures.
- **mmCIF (PDBx)**: modern standard; preferred for completeness and large structures.

Direct download endpoints:

- `https://files.rcsb.org/download/{PDB_ID}.pdb`
- `https://files.rcsb.org/download/{PDB_ID}.cif`

### Batch Processing Pattern

For batch metadata retrieval, iterate over IDs and call `fetch(pdb_id, schema=Schema.ENTRY)`; handle exceptions per-ID to keep pipelines robust. For large batches, consider rate limiting and caching to avoid repeated downloads.

### Reference Documentation

If present in this repository, consult:

- `references/api_reference.md` for advanced endpoint usage, query patterns, schema notes, rate limits, and troubleshooting.