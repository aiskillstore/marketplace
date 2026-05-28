# Open Targets API Reference

## Endpoint
- **URL**: `https://api.platform.opentargets.org/api/v4/graphql`
- **Method**: POST
- **Content-Type**: application/json

## Core Entities

### Target
- **Identifier**: Ensembl ID (e.g., `ENSG00000157764`)
- **Fields**: `approvedSymbol`, `biotype`, `geneticConstraints`, `associatedDiseases`

### Disease
- **Identifier**: EFO ID (Experimental Factor Ontology)
- **Fields**: `name`, `description`, `synonyms`, `associatedTargets`

### Evidence
Data sources include:
- GWAS Catalog
- ClinVar
- ChEMBL
- CRISPR screens

## Scoring
Association scores range from 0 to 1, representing the harmonic sum of evidence from various data types.
