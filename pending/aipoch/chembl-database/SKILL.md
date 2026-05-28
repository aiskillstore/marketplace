---
name: chembl-database
description: Query the ChEMBL database for bioactive molecules, targets, bioactivities, and approved drugs; use this when you need to filter by physicochemical properties (e.g., MW, LogP), chemical structure (SMILES), or retrieve drug mechanism information.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Find candidate compounds by name or synonym (e.g., searching for “aspirin”) and retrieve their ChEMBL records.
- Filter molecules by physicochemical properties (e.g., molecular weight, LogP) to narrow down drug-like candidates.
- Look up targets (proteins/complexes) and connect them to ligands and known bioactivity measurements.
- Retrieve bioactivity data (e.g., IC50, Ki, EC50) for specific compound–target interactions to support SAR or benchmarking.
- Identify approved drugs and fetch mechanism-of-action information for target validation or competitive landscape analysis.

## Key Features

- Molecule search by preferred name and other metadata fields.
- Property-based filtering (e.g., MW, LogP) using ChEMBL API filter syntax.
- Structure-aware querying via SMILES (where supported by the API/client).
- Target lookup and navigation between targets, molecules, and activities.
- Bioactivity retrieval for common endpoints (IC50, Ki, EC50) and related assay context.
- Access to drug-related records, including mechanism information for approved drugs.

## Dependencies

- Python 3.9+ (recommended)
- `chembl_webresource_client` (latest available via pip/uv)

Install:

```bash
uv pip install chembl_webresource_client
```

Additional references (optional, if present in this repository):

- `references/api_reference.md` (filter syntax and resource list)
- `scripts/query_chembl.py` (CLI wrapper example)

## Example Usage

```python
from chembl_webresource_client.new_client import new_client

def main():
    molecule = new_client.molecule
    target = new_client.target
    activity = new_client.activity
    mechanism = new_client.mechanism

    # 1) Search for molecules by name (case-insensitive substring match)
    mols = list(molecule.filter(pref_name__icontains="aspirin")[:5])
    if not mols:
        raise SystemExit("No molecules found for query.")

    first = mols[0]
    chembl_id = first.get("molecule_chembl_id")
    print("Top molecule hit:", chembl_id, "-", first.get("pref_name"))

    # 2) Filter molecules by a simple property constraint (example: MW <= 500)
    # Note: exact field names and operators depend on ChEMBL API schema.
    druglike = list(molecule.filter(molecule_properties__mw_freebase__lte=500)[:5])
    print("Example drug-like hits (MW<=500):", [m.get("molecule_chembl_id") for m in druglike])

    # 3) Get target information (example: targets containing "COX")
    targets = list(target.filter(pref_name__icontains="cyclooxygenase")[:5])
    print("Example targets:", [(t.get("target_chembl_id"), t.get("pref_name")) for t in targets])

    # 4) Query bioactivity for a molecule (IC50/Ki/EC50 etc. depend on available records)
    # Here we fetch a few activity records linked to the molecule.
    acts = list(activity.filter(molecule_chembl_id=chembl_id)[:5])
    for a in acts:
        print(
            "Activity:",
            a.get("activity_id"),
            "type=", a.get("standard_type"),
            "value=", a.get("standard_value"),
            "units=", a.get("standard_units"),
            "target=", a.get("target_chembl_id"),
        )

    # 5) Retrieve mechanism-of-action records (often used for approved drugs)
    mechs = list(mechanism.filter(molecule_chembl_id=chembl_id)[:5])
    for m in mechs:
        print(
            "Mechanism:",
            "target=", m.get("target_chembl_id"),
            "action=", m.get("action_type"),
            "mechanism=", m.get("mechanism_of_action"),
        )

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Client/Resources**: Uses `chembl_webresource_client.new_client.new_client` to access resource endpoints such as `molecule`, `target`, `activity`, and `mechanism`.
- **Filtering Model**: Queries are built via `.filter(...)` with field lookups and operators (e.g., `__icontains`, `__lte`). The exact available fields and supported operators are defined by the ChEMBL API schema; consult `references/api_reference.md` for the authoritative list and examples.
- **Pagination/Slicing**: Results are iterable and can be sliced (e.g., `[:5]`) to limit network calls and output size.
- **Bioactivity Fields**: Common normalized fields include `standard_type`, `standard_value`, and `standard_units`. Not all records contain all fields; code should handle missing keys.
- **Mechanism Retrieval**: Mechanism-of-action data is accessed via the `mechanism` resource and is typically most complete for approved/annotated drugs.
- **Structure Queries (SMILES)**: Structure-based search support depends on the API endpoint and client capabilities; when enabled, it is typically performed by passing a SMILES string to the appropriate structure/compound endpoint or filter as documented in `references/api_reference.md`.