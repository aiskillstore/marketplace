# UniProt Query Syntax

The UniProt search API uses Lucene-style query syntax.

## Basic Fields
- `gene`: Gene name (e.g., `gene:BRCA1`)
- `organism_id`: Organism Taxonomy ID (e.g., `organism_id:9606` for Human)
- `accession`: UniProt Accession (e.g., `accession:P12345`)
- `protein_name`: Protein name (e.g., `protein_name:insulin`)

## Operators
- `AND`: Combine terms (default)
- `OR`: Logical OR
- `NOT`: Exclude terms
- `*`: Wildcard

## Examples
- `gene:p53 AND organism_id:9606`
- `reviewed:true AND gene:cdc*`
