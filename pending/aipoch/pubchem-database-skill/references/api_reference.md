# PubChem API Reference

## PubChemPy
This skill relies heavily on `pubchempy`, a Python wrapper for the PubChem PUG-REST API.

- **Documentation**: [https://pubchempy.readthedocs.io/en/latest/](https://pubchempy.readthedocs.io/en/latest/)
- **Key Classes**:
    - `Compound`: Represents a single chemical record.
    - `get_compounds(identifier, namespace, searchtype)`: Main search function.

## PUG-REST API
For advanced queries not covered by PubChemPy (like specific assay summaries), we access PUG-REST directly.

- **Base URL**: `https://pubchem.ncbi.nlm.nih.gov/rest/pug`
- **Rate Limits**: No more than 5 requests per second.
- **Timeouts**: Complex structure searches may time out; use asynchronous PUG-REST approach (ListKey) for heavy tasks.

## Supported Identifiers
- Name (e.g., "Aspirin")
- CID (Compound ID, e.g., 2244)
- SMILES
- InChI
- Molecular Formula
