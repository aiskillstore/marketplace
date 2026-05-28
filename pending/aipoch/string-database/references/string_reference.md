# STRING Database Documentation Reference

## 1. Introduction
The STRING Database skill provides a Python interface to the STRING API, allowing access to a vast network of protein-protein interactions (PPIs) covering over 59 million proteins and 20 billion interactions across 5000+ organisms.

## 2. Functions
*   **Network Retrieval**: Get physical or functional interaction networks.
*   **Functional Enrichment**: Analyze Gene Ontology, KEGG, Pfam enrichment for protein lists.
*   **Interaction Discovery**: Find partners for specific proteins (hub analysis).
*   **Visualization**: Generate network images (PNG) with evidence coloring.
*   **Homology**: Retrieve homology scores.

## 3. Source
*   **Skill Author**: K-Dense Inc.
*   **Data Source**: STRING Consortium (ELIXIR/EMBL).
*   **Website**: https://string-db.org

## 4. API / Logic Flow
1.  **ID Mapping**: Calls `string-db.org/api/json/get_string_ids` to resolve names.
2.  **Network Query**: Calls `string-db.org/api/tsv/network` with a list of IDs and score threshold.
3.  **Enrichment**: Calls `string-db.org/api/tsv/enrichment`.
4.  **Image**: Calls `string-db.org/api/image/network`.
5.  **Species**: All calls typically require the `species` parameter (NCBI Taxon ID, e.g., 9606 for human).

## 5. Technical Details
*   **Libraries**: `requests`, `pandas`
*   **Authentication**: None required for standard usage, but `caller_identity` parameter recommended.
