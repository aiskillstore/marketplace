---
name: alphafold-db
description: Access over 200M protein structures from AlphaFold DB; use when you need to retrieve predicted 3D structures (PDB/mmCIF), confidence metrics (pLDDT/PAE), or protein metadata by UniProt accession.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# AlphaFold Database Skill

## When to Use
- You have a UniProt accession (e.g., `P00520`) and need to download its AlphaFold-predicted 3D structure in **mmCIF** or **PDB** format.
- You want to assess prediction reliability using **per-residue pLDDT** confidence scores.
- You need **PAE (Predicted Aligned Error)** data to support domain-level interpretation or inter-domain confidence checks.
- You want to programmatically retrieve AlphaFold DB **metadata** (e.g., model/structure URLs and related fields) for downstream pipelines.
- You are building an automated workflow that fetches structures + confidence metrics for many proteins by UniProt ID.

## Key Features
- Fetch AlphaFold DB predicted structures by **UniProt accession**.
- Download structure files in **mmCIF (default)** or **PDB**.
- Retrieve and save **metadata JSON**, including confidence-related fields (e.g., pLDDT) and URL information.
- Simple CLI workflow suitable for scripting and batch processing.

## Dependencies
- Python `>=3.8`
- `requests >=2.25`

## Example Usage
Fetch the structure and metadata for a UniProt ID and save them to a directory:

```bash
python scripts/fetch_structure.py --uniprot_id P00520 --output_dir ./out --format cif
```

Fetch as PDB instead:

```bash
python scripts/fetch_structure.py --uniprot_id P00520 --output_dir ./out --format pdb
```

Expected outputs in `./out`:
- `P00520.cif` (or `P00520.pdb`)
- `P00520_metadata.json` (includes confidence/URL fields such as pLDDT-related information)

## Implementation Details
- **Input identifier**: UniProt accession ID (e.g., `P00520`).
- **Formats**:
  - `--format cif` (default): downloads an mmCIF structure file.
  - `--format pdb`: downloads a PDB structure file.
- **Artifacts written**:
  - Structure file named `<UNIPROT_ID>.<cif|pdb>`.
  - Metadata JSON named `<UNIPROT_ID>_metadata.json`, used to store confidence metrics (e.g., pLDDT) and AlphaFold DB URL-related fields.
- **API reference**: Endpoint and response details are documented in `references/api_reference.md`.