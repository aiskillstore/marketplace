# AlphaFold Database API Reference

## Base URL
`https://alphafold.ebi.ac.uk`

## Endpoints

### 1. Get Prediction Metadata
Retrieves metadata for a given UniProt accession, including download links for structure files and confidence metrics.

- **URL**: `/api/prediction/{uniprot_id}`
- **Method**: `GET`
- **Parameters**:
    - `uniprot_id`: The UniProt Accession ID (e.g., `P00520`).

**Example Response (JSON)**:
```json
[
  {
    "entryId": "AF-P00520-F1",
    "gene": "ABL1",
    "uniprotAccession": "P00520",
    "uniprotId": "ABL1_HUMAN",
    "uniprotDescription": "Tyrosine-protein kinase ABL1",
    "taxId": 9606,
    "organismScientificName": "Homo sapiens",
    "uniprotStart": 1,
    "uniprotEnd": 1130,
    "modelCreatedDate": "2022-06-01",
    "latestVersion": 4,
    "allVersions": [4],
    "cifUrl": "https://alphafold.ebi.ac.uk/files/AF-P00520-F1-model_v4.cif",
    "pdbUrl": "https://alphafold.ebi.ac.uk/files/AF-P00520-F1-model_v4.pdb",
    "paeImageUrl": "https://alphafold.ebi.ac.uk/files/AF-P00520-F1-predicted_aligned_error_v4.png",
    "paeDocUrl": "https://alphafold.ebi.ac.uk/files/AF-P00520-F1-predicted_aligned_error_v4.json"
  }
]
```

### 2. Direct File Access
If the AlphaFold ID is known (e.g., `AF-P00520-F1`), files can be accessed directly.

- **CIF**: `/files/{alphafold_id}-model_v4.cif`
- **PDB**: `/files/{alphafold_id}-model_v4.pdb`
- **PAE JSON**: `/files/{alphafold_id}-predicted_aligned_error_v4.json`
