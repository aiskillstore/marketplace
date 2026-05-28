---
name: pubchem-database-skill
description: Programmatic access to the PubChem database (via PUG-REST API and PubChemPy) for searching chemical compounds, retrieving physicochemical properties, performing structure similarity/substructure searches, and obtaining bioactivity data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

* You need to **search for chemical compounds** by name, CID, SMILES, InChI, or molecular formula.
* You want to **retrieve physicochemical properties** (e.g., molecular weight, LogP, TPSA, H-bond donors/acceptors).
* You need to **perform structure-based searches**, such as similarity or substructure queries.
* You want to **obtain bioactivity data** (e.g., assay summaries, target information) for a given compound.
* You are building an automated cheminformatics or drug discovery workflow that requires **programmatic access to PubChem**.

## Key Features

* **Flexible compound search** by name, CID, SMILES, InChI, or formula.
* **Property retrieval** via PubChem PUG-REST and PubChemPy (e.g., MW, LogP, Canonical SMILES).
* **Structure search**:

  * Similarity search
  * Substructure search
* **Bioactivity retrieval** linked to PubChem BioAssay records.
* **Rate-limit aware implementation** (respects PubChem’s limit of max 5 requests/sec).
* **Python function interface** for seamless integration into scientific pipelines.

## Dependencies

Install the required Python packages:

```bash
uv pip install pubchempy requests
```

* `pubchempy` (version: not pinned)
* `requests` (version: not pinned)

## Example Usage

Primary module:

* `scripts/pubchem_ops.py`

### 1) Get compound properties

```bash
python -c "from scripts.pubchem_ops import get_properties; print(get_properties(query_value='Aspirin', query_type='name'))"
```

Or in Python:

```python
from scripts.pubchem_ops import get_properties

result = get_properties(query_value="Aspirin", query_type="name")
print(result)
```

### 2) Structure search (similarity)

```bash
python -c "from scripts.pubchem_ops import structure_search; print(structure_search(query_value='CC(=O)OC1=CC=CC=C1C(=O)O', search_type='similarity'))"
```

Or in Python:

```python
from scripts.pubchem_ops import structure_search

smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
result = structure_search(query_value=smiles, search_type="similarity")
print(result)
```

### 3) Get bioactivity data

```bash
python -c "from scripts.pubchem_ops import get_bioactivity; print(get_bioactivity(cid=2244))"
```

Or in Python:

```python
from scripts.pubchem_ops import get_bioactivity

result = get_bioactivity(cid=2244)
print(result)
```

## Implementation Details

* **Primary script**: `scripts/pubchem_ops.py`
* **Data sources / endpoints**:

  * Compound & properties: `pubchem.ncbi.nlm.nih.gov/rest/pug`
  * Bioactivity: PubChem BioAssay endpoints
  * Python wrapper: `PubChemPy`
* **Supported operations**:

  * `get_properties`: retrieve physicochemical properties by name/CID/SMILES/InChI/formula.
  * `structure_search`: perform similarity or substructure search.
  * `get_bioactivity`: retrieve assay and bioactivity-related data by CID.
* **Input constraints**:

  * `query_type` must match supported types (e.g., `name`, `cid`, `smiles`, `inchi`, `formula`).
  * `search_type` must be `similarity` or `substructure`.
* **Error handling**:

  * Returns structured error or `None` if compound is not found.
  * Handles PubChem rate limits (≤ 5 requests/sec).
* **Troubleshooting considerations**:

  * Ensure network access to `pubchem.ncbi.nlm.nih.gov`.
  * Verify query format (e.g., valid SMILES or InChI) if results are empty.
* **Additional reference**:

  * API documentation pointers: `references/api_reference.md`

