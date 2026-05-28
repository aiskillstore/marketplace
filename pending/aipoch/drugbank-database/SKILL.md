---
name: drugbank-database
description: Programmatic access to DrugBank drug and target data; use when you need to download, parse, and analyze DrugBank XML for properties, interactions, pathways, and pharmacology.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to extract structured drug properties (e.g., identifiers, synonyms, ATC codes) from DrugBank XML for downstream analysis.
- You want to build and analyze drug–drug interaction (DDI) networks from DrugBank interaction records.
- You are mapping drugs to targets (proteins/genes) to support target discovery, mechanism-of-action analysis, or enrichment workflows.
- You need to connect drugs to pathways and pharmacology annotations for systems pharmacology or knowledge graph construction.
- You want to generate tabular datasets (CSV/Parquet) from DrugBank for use in notebooks, dashboards, or ML pipelines.

## Key Features

- Programmatic download of DrugBank releases via `drugbank-downloader` (requires DrugBank access).
- XML parsing and traversal using `lxml` for reliable extraction of nested DrugBank entities.
- Data wrangling into `pandas` DataFrames for filtering, joining, and export.
- Network construction and analysis with `networkx` (e.g., DDI graphs, drug–target bipartite graphs).
- Optional cheminformatics support with `rdkit` for structure-based processing (e.g., SMILES/InChI handling when present).

## Dependencies

- `drugbank-downloader` (version varies by your environment)
- `lxml>=4.9`
- `pandas>=2.0`
- `networkx>=3.0`
- `rdkit>=2022.09` (optional; required only for structure/chemistry workflows)

## Example Usage

```python
"""
End-to-end example:
1) Parse a local DrugBank XML file
2) Extract a minimal drug table
3) Extract drug-drug interactions
4) Build a DDI graph

Prerequisites:
- You must obtain DrugBank XML via your DrugBank account/license.
- Place the XML file at ./drugbank.xml (or update the path).
"""

from lxml import etree
import pandas as pd
import networkx as nx

DRUGBANK_XML_PATH = "./drugbank.xml"
NS = {"db": "http://www.drugbank.ca"}  # DrugBank XML namespace

# --- Parse XML ---
tree = etree.parse(DRUGBANK_XML_PATH)
root = tree.getroot()

# --- Extract drug records (minimal fields) ---
drugs = []
for drug in root.xpath("//db:drug", namespaces=NS):
    drugbank_id = drug.xpath("string(db:drugbank-id[@primary='true'])", namespaces=NS).strip()
    name = drug.xpath("string(db:name)", namespaces=NS).strip()
    drug_type = drug.get("type", "").strip()

    # Optional: first SMILES if present
    smiles = drug.xpath(
        "string(db:calculated-properties/db:property[db:kind='SMILES']/db:value)",
        namespaces=NS,
    ).strip()

    drugs.append(
        {
            "drugbank_id": drugbank_id,
            "name": name,
            "type": drug_type,
            "smiles": smiles or None,
        }
    )

drugs_df = pd.DataFrame(drugs).dropna(subset=["drugbank_id"])
print("Drugs:", len(drugs_df))
print(drugs_df.head())

# --- Extract drug-drug interactions ---
interactions = []
for drug in root.xpath("//db:drug", namespaces=NS):
    src_id = drug.xpath("string(db:drugbank-id[@primary='true'])", namespaces=NS).strip()
    src_name = drug.xpath("string(db:name)", namespaces=NS).strip()

    for ddi in drug.xpath("db:drug-interactions/db:drug-interaction", namespaces=NS):
        tgt_id = ddi.xpath("string(db:drugbank-id)", namespaces=NS).strip()
        tgt_name = ddi.xpath("string(db:name)", namespaces=NS).strip()
        description = ddi.xpath("string(db:description)", namespaces=NS).strip()

        if src_id and tgt_id:
            interactions.append(
                {
                    "source_id": src_id,
                    "source_name": src_name,
                    "target_id": tgt_id,
                    "target_name": tgt_name,
                    "description": description or None,
                }
            )

ddi_df = pd.DataFrame(interactions)
print("Interactions:", len(ddi_df))
print(ddi_df.head())

# --- Build a DDI graph ---
G = nx.from_pandas_edgelist(
    ddi_df,
    source="source_id",
    target="target_id",
    edge_attr=["description"],
    create_using=nx.Graph(),
)

print("DDI graph nodes:", G.number_of_nodes())
print("DDI graph edges:", G.number_of_edges())

# Example analysis: top 10 drugs by interaction degree
top_degree = sorted(G.degree, key=lambda x: x[1], reverse=True)[:10]
top_degree_df = pd.DataFrame(top_degree, columns=["drugbank_id", "degree"]).merge(
    drugs_df[["drugbank_id", "name"]],
    on="drugbank_id",
    how="left",
)
print(top_degree_df)
```

## Implementation Details

- **Access & authentication**
  - DrugBank data access requires a free academic account or a paid license depending on your use case.
  - The `drugbank-downloader` step is responsible for fetching the release artifacts; ensure you comply with DrugBank terms.

- **XML parsing approach**
  - DrugBank is distributed as a large XML document; `lxml.etree` is used for robust XPath-based extraction.
  - The XML uses a namespace (commonly `http://www.drugbank.ca`); XPath queries must include the namespace mapping (e.g., `NS = {"db": "http://www.drugbank.ca"}`).

- **Core extraction patterns**
  - **Primary DrugBank ID**: `db:drugbank-id[@primary='true']`
  - **Drug name**: `db:name`
  - **Calculated properties (e.g., SMILES)**: `db:calculated-properties/db:property[db:kind='SMILES']/db:value`
  - **Drug interactions**: `db:drug-interactions/db:drug-interaction` with fields `db:drugbank-id`, `db:name`, `db:description`

- **Data modeling**
  - Use `pandas` DataFrames for normalized tables (drugs, targets, interactions, pathways).
  - Use `networkx` for graph representations:
    - DDI graph: nodes are drugs, edges are interactions (store `description` as edge attribute).
    - Drug–target graph: bipartite graph with drug nodes and target nodes.

- **Performance considerations**
  - DrugBank XML can be large; for memory-sensitive environments, consider iterative parsing (`etree.iterparse`) and writing intermediate results to disk.
  - Normalize identifiers early (e.g., always keep primary DrugBank IDs) to simplify joins across tables.

- **Further references**
  - See: `references/data-access.md`
  - See: `references/drug-queries.md`
  - See: `references/interactions.md`