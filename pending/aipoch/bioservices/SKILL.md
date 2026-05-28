---
name: bioservices
description: Unified Python access to 40+ bioinformatics web services; use when you need to query multiple databases (e.g., UniProt/KEGG/ChEMBL/Reactome) with one consistent API in a single workflow, especially for cross-database analysis and identifier mapping.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to **retrieve and combine biological data from multiple databases** (e.g., UniProt + KEGG + GO) in one Python workflow.
- You need **cross-database identifier mapping** (e.g., UniProt ↔ KEGG, KEGG compound ↔ ChEMBL) as part of downstream analysis.
- You want to **programmatically explore pathways and networks** (e.g., KEGG pathway parsing, exporting interactions to SIF).
- You need **service-agnostic access** across many providers (REST and SOAP/WSDL) without writing custom clients per service.
- You are building **integrated bioinformatics pipelines** (protein → sequence → BLAST → pathways → interactions) that span multiple resources.

## Key Features

- **Unified API** for ~40+ bioinformatics services (single Python package, consistent patterns).
- **Transparent protocol handling** (REST and SOAP/WSDL).
- **Protein-centric workflows** via UniProt (search, retrieve, ID mapping).
- **Pathway discovery and parsing** via KEGG (KGML parsing, relations extraction, SIF export).
- **Compound lookup and cross-referencing** (e.g., KEGG compounds + UniChem mapping to ChEMBL).
- **Sequence analysis integrations** (e.g., NCBI BLAST asynchronous jobs).
- **Ontology and annotation queries** (e.g., QuickGO).
- **Protein–protein interaction queries** via PSICQUIC-compatible services.

## Dependencies

- `python >= 3.9`
- `bioservices` (install via pip/uv; version depends on your environment)

Optional (commonly used alongside returned formats):
- `pandas >= 1.5` (TSV/tabular outputs)
- `beautifulsoup4 >= 4.11` (XML parsing)
- `lxml >= 4.9` (faster XML parsing)
- `networkx >= 2.8` (network analysis of interactions)
- `biopython >= 1.81` (sequence handling for FASTA outputs)

## Example Usage

A single runnable script that demonstrates a cross-service workflow:
1) UniProt search + FASTA retrieval  
2) UniProt → KEGG ID mapping  
3) KEGG pathway lookup and KGML relation extraction  
4) QuickGO annotation query  
5) PSICQUIC interaction query  
6) KEGG compound lookup + UniChem mapping to ChEMBL

```python
"""
Run:
  uv pip install bioservices pandas
  python bioservices_example.py

Notes:
- Some services may rate-limit or be temporarily unavailable.
- NCBI BLAST requires an email; this example does not run BLAST to stay lightweight.
"""

from bioservices import UniProt, KEGG, QuickGO, PSICQUIC, UniChem


def main():
    # --- UniProt: search + retrieve ---
    u = UniProt(verbose=False)

    # Search by entry name (example: ZAP70 human)
    tab = u.search("ZAP70_HUMAN", frmt="tab", columns="id,entry name,genes,organism")
    print("UniProt search (tab):")
    print(tab.splitlines()[0:3], "\n")  # show header + first rows

    uniprot_ac = "P43403"  # ZAP70_HUMAN accession
    fasta = u.retrieve(uniprot_ac, "fasta")
    print("UniProt FASTA header:")
    print(fasta.splitlines()[0], "\n")

    # --- UniProt: identifier mapping (UniProt -> KEGG) ---
    mapping = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_ac)
    print("UniProt -> KEGG mapping:")
    print(mapping, "\n")

    # --- KEGG: pathway discovery + parsing ---
    k = KEGG(verbose=False)
    k.organism = "hsa"

    # Example gene: ZAP70 is KEGG gene hsa:7535
    pathways = k.get_pathway_by_gene("7535", "hsa")
    print("KEGG pathways containing hsa:7535:")
    print(pathways, "\n")

    pathway_id = "hsa04660"  # T cell receptor signaling pathway (example)
    kgml_relations = k.parse_kgml_pathway(pathway_id).get("relations", [])
    print(f"KEGG KGML relations count for {pathway_id}: {len(kgml_relations)}\n")

    # Export to SIF (useful for network tools)
    sif = k.pathway2sif(pathway_id)
    print(f"KEGG SIF preview for {pathway_id}:")
    print("\n".join(sif.splitlines()[:5]), "\n")

    # --- QuickGO: GO annotations for a UniProt protein ---
    g = QuickGO(verbose=False)
    ann = g.Annotation(protein=uniprot_ac, format="tsv")
    print("QuickGO annotation TSV header:")
    print(ann.splitlines()[0], "\n")

    # --- PSICQUIC: interaction query (database name may vary by availability) ---
    p = PSICQUIC(verbose=False)
    # Example query: ZAP70 interactions in human
    # Choose a database that is active in your environment; "intact" is commonly available.
    interactions = p.query("intact", "ZAP70 AND species:9606")
    print("PSICQUIC query result preview:")
    print("\n".join(interactions.splitlines()[:3]), "\n")

    # --- Compound workflow: KEGG compound -> UniChem -> ChEMBL ---
    # Example: Geldanamycin
    cpd_hits = k.find("compound", "Geldanamycin")
    print("KEGG compound find('Geldanamycin'):")
    print(cpd_hits, "\n")

    # If you already know the KEGG compound ID:
    kegg_compound_id = "C11222"
    uc = UniChem(verbose=False)
    chembl_id = uc.get_compound_id_from_kegg(kegg_compound_id)
    print(f"UniChem KEGG {kegg_compound_id} -> ChEMBL:")
    print(chembl_id, "\n")


if __name__ == "__main__":
    main()
```

## Implementation Details

- **Service objects**: Each remote resource is exposed as a Python class (e.g., `UniProt`, `KEGG`, `QuickGO`, `PSICQUIC`, `NCBIblast`). You instantiate a client and call methods that wrap the underlying endpoints.
- **Protocols**: BioServices abstracts **REST** and **SOAP/WSDL** services behind similar method calls; returned payloads may be text (TSV), XML, JSON-like dicts, or FASTA.
- **Common parameters**
  - `verbose`: toggles HTTP/request logging (`verbose=False` is recommended for scripts).
  - `TIMEOUT`: per-service timeout control (useful for slow networks or large responses).
  - Service-specific parameters (examples):
    - UniProt: `search(query, frmt=..., columns=...)`, `retrieve(accession, format)`, `mapping(fr=..., to=..., query=...)`
    - KEGG: `find(db, query)`, `get(entry_id)`, `parse(raw)`, `parse_kgml_pathway(pathway_id)`, `pathway2sif(pathway_id)`
    - NCBI BLAST: asynchronous job model (`run(...)` → `getStatus(jobid)` → `getResult(jobid, ...)`)
- **Data handling guidance**
  - TSV/tabular outputs: load into `pandas.read_csv(io.StringIO(text), sep="\t")`
  - XML outputs: parse with `BeautifulSoup` or `lxml`
  - Network exports (SIF): import into NetworkX/Cytoscape-compatible tooling
- **Operational considerations**
  - Many endpoints are **rate-limited**; implement retries/backoff for production pipelines.
  - Some services require **contact information** (e.g., NCBI BLAST email) and may enforce usage policies.
  - Availability varies by provider; design workflows to degrade gracefully (try/except, fallbacks).