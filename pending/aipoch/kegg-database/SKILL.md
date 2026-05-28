---
name: kegg-database
description: Direct access to KEGG via the REST API for academic-only pathway/gene/compound/drug queries; use when you need precise HTTP-level control or targeted KEGG ID mapping.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to fetch **KEGG pathway, gene, compound, enzyme, disease, or drug** records directly from the **KEGG REST API**.
- You want to perform **gene ↔ pathway** mapping (e.g., building inputs for pathway enrichment or reporting).
- You need **cross-references** between KEGG databases (e.g., pathway → genes, gene → KO, pathway → compounds).
- You must **convert identifiers** between KEGG and external databases (e.g., KEGG gene → NCBI Gene ID / UniProt; KEGG compound → PubChem).
- You need **drug–drug interaction (DDI)** lookups for KEGG drug IDs.

> Note: KEGG REST access is intended for academic use. Non-academic/commercial use may require a separate KEGG license.

## Key Features

- Full coverage of core KEGG REST operations via Python helpers:
  - `kegg_info` (database metadata)
  - `kegg_list` (catalog listing)
  - `kegg_find` (keyword/property search)
  - `kegg_get` (entry retrieval; sequences/structures/images)
  - `kegg_conv` (ID conversion)
  - `kegg_link` (cross-database linking)
  - `kegg_ddi` (drug–drug interactions)
- Supports common KEGG identifiers and formats:
  - Pathways: `map00010`, `hsa00010`
  - Genes: `hsa:10458`
  - Compounds: `cpd:C00002`
  - Drugs: `dr:D00001`
  - Enzymes: `ec:1.1.1.1`
  - KO: `ko:K00001`
- Output format options for `kegg_get`: `aaseq`, `ntseq`, `mol`, `kcf`, `image`, `kgml`, `json` (some formats are single-entry only).

## Dependencies

- Python `>=3.9`
- `requests >=2.31.0`

## Example Usage

```python
"""
End-to-end example:
1) Find a human gene by keyword
2) Link the gene to pathways
3) Retrieve one pathway entry
4) Convert the gene ID to UniProt
"""

from scripts.kegg_api import kegg_find, kegg_link, kegg_get, kegg_conv

# 1) Search for a gene keyword in KEGG GENES
hits = kegg_find("genes", "p53")
print("FIND results (first lines):")
print("\n".join(hits.splitlines()[:5]), "\n")

# Choose a known KEGG gene ID for TP53 (human)
gene_id = "hsa:7157"

# 2) Link gene -> pathways
pathway_links = kegg_link("pathway", gene_id)
print("LINK gene -> pathways (first lines):")
print("\n".join(pathway_links.splitlines()[:5]), "\n")

# Parse the first pathway ID from the link output
# Typical line format: path:hsaXXXXX<TAB>hsa:7157
first_line = next((ln for ln in pathway_links.splitlines() if ln.strip()), None)
if not first_line:
    raise RuntimeError("No pathways returned for the gene ID.")

path_id = first_line.split("\t")[0].replace("path:", "")
print("Selected pathway:", path_id, "\n")

# 3) Retrieve the pathway entry (flat text)
pathway_entry = kegg_get(path_id)
print("GET pathway entry (first 30 lines):")
print("\n".join(pathway_entry.splitlines()[:30]), "\n")

# 4) Convert KEGG gene ID -> UniProt
uniprot_map = kegg_conv("uniprot", gene_id)
print("CONV KEGG -> UniProt:")
print(uniprot_map)
```

## Implementation Details

### API-to-function mapping

This skill wraps KEGG REST endpoints into Python functions (see `scripts/kegg_api.py`):

- `kegg_info(database_or_org)`  
  Retrieves database or organism metadata (release info, counts, etc.).

- `kegg_list(database, organism=None)`  
  Lists entries in a database; optionally scoped to an organism (e.g., `("pathway", "hsa")`).  
  Also supports listing explicit IDs (batch-style) when passed as a single string.

- `kegg_find(database, query, option=None)`  
  Searches by keyword or by chemical properties. Common `option` values:
  - `formula` (exact match)
  - `exact_mass` (range like `300-310`)
  - `mol_weight` (range)

- `kegg_get(entry_ids, option=None)`  
  Retrieves full entries or specific formats:
  - Sequences: `aaseq`, `ntseq`
  - Structures: `mol`, `kcf`
  - Pathway assets: `image` (PNG), `kgml` (XML), `json` (Pathway JSON)

  **Batching rules**:
  - Most operations allow up to **10 entries** per request.
  - `image`, `kgml`, and `json` typically allow **only 1 entry** per request.

- `kegg_conv(target_db, source)`  
  Converts IDs between KEGG and external databases (e.g., `uniprot`, `ncbi-geneid`, `pubchem`, `chebi`).  
  Output is tab-delimited pairs: `source_id<TAB>target_id`.

- `kegg_link(target_db, source)`  
  Cross-references entries across KEGG databases (e.g., gene → pathway, pathway → compound, gene → KO).

- `kegg_ddi(drug_ids)`  
  Returns known drug–drug interactions for one or more KEGG drug IDs (up to typical batch limits).

### Practical constraints and error handling

- **Entry limits**: Prefer chunking lists into batches of ≤10 IDs; enforce single-entry calls for `image/kgml/json`.
- **HTTP status codes**: Treat non-200 responses as failures; common issues include:
  - `400` (bad request / malformed parameters)
  - `404` (unknown database or entry ID)
- **Rate behavior**: KEGG does not publish strict rate limits; avoid high-frequency polling and add backoff/retry for robustness.

### Reference documentation

For detailed endpoint syntax, database lists, and species codes, consult:
- `references/kegg_reference.md`