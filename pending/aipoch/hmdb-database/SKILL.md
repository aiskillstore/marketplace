---
name: hmdb-database
description: Access the Human Metabolome Database (HMDB) to search metabolites by name/structure/ID and extract chemical/biological/clinical fields when you need metabolomics research data or automated HMDB XML mining.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to look up a metabolite by **common name** (e.g., “Caffeine”) and retrieve its HMDB entry data.
- You have an **HMDB ID** (e.g., `HMDB0000001`) and want to extract standardized chemical/biological/clinical fields for downstream analysis.
- You want to build a **local, scriptable pipeline** to mine the HMDB XML dump instead of manually browsing the website.
- You need to **map HMDB identifiers** to external resources (e.g., KEGG, PubChem, ChEBI) for integration tasks.
- You are preparing metabolomics datasets and need **pathway/enzyme/transporter** annotations from HMDB entries.

## Key Features

- Search metabolites by:
  - Text name
  - HMDB identifier (e.g., `HMDB0000001`)
  - Structure-related query (as supported by the parser/search implementation)
- Parse the HMDB XML dataset and extract:
  - **Chemical data** (formula, molecular weight, InChI/SMILES where available)
  - **Biological data** (pathways, enzymes, transporters)
  - **Clinical data** (disease associations, biofluid concentrations)
- Optional structuring of extracted results for analysis workflows (e.g., tabular outputs).
- Supports integration workflows by exposing identifiers suitable for cross-database mapping.

## Dependencies

- Python `>=3.9`
- Standard library:
  - `xml.etree.ElementTree` (built-in)
- Optional:
  - `pandas >= 1.5`

## Example Usage

### 1) Download HMDB XML

Download the HMDB metabolite XML dataset from:
- https://hmdb.ca/downloads

Assume you saved it as:

```text
data/hmdb_metabolites.xml
```

### 2) Search and Extract Fields (Runnable Example)

```python
from scripts.hmdb_parser import HMDBParser

def main():
    # Path to the HMDB XML dump downloaded from hmdb.ca/downloads
    xml_path = "data/hmdb_metabolites.xml"

    parser = HMDBParser(xml_path)

    # Search by metabolite name (text query)
    results = parser.search("Caffeine")

    # Print basic information from the first match (structure depends on implementation)
    if not results:
        print("No results found.")
        return

    first = results[0]
    print("Top match:")
    print(first)

if __name__ == "__main__":
    main()
```

### 3) Field Reference

For a curated list of extractable fields and how they map to HMDB XML elements, see:

- `references/hmdb_data_fields.md`

## Implementation Details

- **Data acquisition**
  - Primary workflow uses the official HMDB downloadable XML dataset (recommended for bulk parsing).
  - Single-entry lookups can be done via the HMDB website, but this skill is designed around XML parsing.

- **Parsing approach**
  - The parser reads the HMDB XML and traverses metabolite entries using `xml.etree.ElementTree`.
  - Extracted fields should follow the definitions documented in `references/hmdb_data_fields.md`.

- **Search behavior**
  - Name/ID search typically matches against key textual identifiers (e.g., common name, synonyms, HMDB accession).
  - Structure-based search is dependent on what structural fields are indexed/exposed by `HMDBParser` (e.g., SMILES/InChI).

- **Integration / cross-references**
  - HMDB entries often include cross-references to external databases (e.g., KEGG, PubChem, ChEBI).
  - A common workflow is to extract these identifiers and build mapping tables for downstream joins.

- **Spectral analysis (conceptual)**
  - HMDB contains NMR/MS references for some metabolites; this skill can be extended to link parsed entries to spectral metadata.
  - Actual spectral matching/identification is not guaranteed unless implemented in the codebase.