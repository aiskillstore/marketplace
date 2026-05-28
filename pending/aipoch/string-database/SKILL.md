---
name: string-database
description: Access the STRING database to map identifiers, retrieve protein–protein interaction networks, and run functional/PPI enrichment when you need interaction context for a gene/protein set.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have gene symbols (e.g., `TP53`) and need to resolve them to STRING protein identifiers for downstream analysis.
- You want to retrieve a protein–protein interaction (PPI) network (functional/physical) with confidence scores for one or more proteins.
- You need to find interaction partners for a target protein to expand a candidate list (e.g., add top N neighbors).
- You want to perform functional enrichment (GO/KEGG/Reactome, etc.) for a protein set to interpret biological themes.
- You need a quick static visualization (PNG/SVG) of a STRING network for reports or notebooks.

## Key Features

- **ID Mapping**: Convert gene/protein names to STRING identifiers for a given organism.
- **Network Retrieval**: Fetch interaction edges with confidence scores from STRING.
- **Interaction Partners**: Expand a protein list by retrieving interaction partners.
- **Enrichment Analysis**:
  - Functional enrichment (e.g., GO, KEGG, Reactome)
  - PPI enrichment statistics
  - Functional annotations (e.g., PFAM/SMART where supported by STRING endpoints)
- **Visualization**: Download static network images (PNG/SVG).

## Dependencies

- Python `>=3.8`
- `requests` (tested with `>=2.28`)
- `pandas` (tested with `>=1.5`)

Install:

```bash
pip install requests pandas
```

## Example Usage

```python
from scripts.string_api import StringClient

def main():
    # STRING does not require a secret API key, but providing a caller identity is recommended.
    client = StringClient(caller_identity="my_analysis_tool")

    # 1) Map an identifier (e.g., TP53 in Homo sapiens; NCBI taxonomy ID 9606)
    protein_id = client.map_id(identifier="TP53", species=9606)
    print("Mapped ID:", protein_id)

    # 2) Download a network image and expand by adding interaction partners
    client.get_network_image(
        identifiers=[protein_id],
        output_file="tp53_network.png",
        add_color_nodes=10,  # add 10 partners
    )
    print("Saved network image to tp53_network.png")

    # 3) Run PPI enrichment for the set
    ppi_stats = client.get_ppi_enrichment(identifiers=[protein_id])
    print("PPI enrichment:", ppi_stats)

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Client entry point**: `scripts/string_api.py` provides the main wrapper (e.g., `StringClient`) around the STRING REST API.
- **Caller identity**:
  - STRING endpoints do **not** require an API key.
  - A `caller_identity` string is strongly recommended (project name/email/URL) to support rate/load management.
  - Pass it at initialization (e.g., `StringClient(caller_identity="my_email@example.com")`) or inject via environment variables in your own wrapper.
- **Organism selection**:
  - Most operations require a species identifier (commonly NCBI taxonomy ID, e.g., `9606` for human).
- **Network retrieval and scoring**:
  - Network endpoints return interactions with confidence scores; downstream filtering is typically done by applying a score threshold in your analysis code (if exposed by the wrapper).
- **Visualization**:
  - Static images are retrieved directly from STRING image endpoints and written to disk (PNG/SVG depending on the method/parameters).
- **Reference documentation**:
  - See `references/string_reference.md` for original API notes and endpoint details included with this skill.