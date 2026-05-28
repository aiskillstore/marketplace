# Datamol Core API Reference

This document covers the main functions available in the datamol namespace.

## Molecule Creation & Conversion

### `to_mol(mol, ...)`
Converts a SMILES string or other molecular representation into an RDKit molecule object.
- **Parameters**: Accepts SMILES strings, InChI, or other molecular formats
- **Returns**: `rdkit.Chem.Mol` object
- **Common usage**: `mol = dm.to_mol("CCO")`

### `from_inchi(inchi)`
Converts an InChI string to a molecule object.

### `from_smarts(smarts)`
Converts a SMARTS pattern to a molecule object.

### `from_selfies(selfies)`
Converts a SELFIES string to a molecule object.

### `copy_mol(mol)`
Creates a copy of a molecule object to avoid modifying the original.

## Molecule Export

### `to_smiles(mol, ...)`
Converts a molecule object to a SMILES string.
- **Common parameters**: `canonical=True`, `isomeric=True`

### `to_inchi(mol, ...)`
Converts a molecule to an InChI string representation.

### `to_inchikey(mol)`
Converts a molecule to an InChI key (fixed-length hash).

### `to_smarts(mol)`
Converts a molecule to a SMARTS pattern.

### `to_selfies(mol)`
Converts a molecule to SELFIES (Self-Referencing Embedded Strings) format.

## Cleaning & Standardization

### `sanitize_mol(mol, ...)`
Enhanced version of RDKit sanitize operation using mol→SMILES→mol conversion and aromatic nitrogen fix.
- **Purpose**: Fixes common molecular structure issues
- **Returns**: Sanitized molecule, or None if sanitization fails

### `standardize_mol(mol, disconnect_metals=False, normalize=True, reionize=True, ...)`
Applies comprehensive standardization procedures, including:
- Metal disconnection
- Normalization (charge correction)
- Reionization
- Fragment handling (selects largest fragment)

### `standardize_smiles(smiles, ...)`
Applies SMILES standardization procedures directly to a SMILES string.

### `fix_mol(mol)`
Attempts to automatically fix molecular structure issues.

### `fix_valence(mol)`
Corrects valence errors in molecular structures.

## Molecular Properties

### `reorder_atoms(mol, ...)`
Ensures consistent atom ordering for the same molecule regardless of the original SMILES representation.
- **Purpose**: Maintains reproducibility for feature generation

### `remove_hs(mol, ...)`
Removes hydrogen atoms from the molecular structure.

### `add_hs(mol, ...)`
Adds explicit hydrogen atoms to the molecular structure.

## Fingerprints & Similarity

### `to_fp(mol, fp_type='ecfp', ...)`
Generates molecular fingerprints for similarity calculations.
- **Fingerprint types**:
  - `'ecfp'` - Extended Connectivity Fingerprints (Morgan)
  - `'fcfp'` - Functional Connectivity Fingerprints
  - `'maccs'` - MACCS keys
  - `'topological'` - Topological fingerprints
  - `'atompair'` - Atom pair fingerprints
- **Common parameters**: `n_bits`, `radius`
- **Returns**: Numpy array or RDKit fingerprint object

### `pdist(mols, ...)`
Computes pairwise Tanimoto distances between all molecules in a list.
- **Supports**: Parallel processing via `n_jobs` parameter
- **Returns**: Distance matrix

### `cdist(mols1, mols2, ...)`
Computes Tanimoto distances between two sets of molecules.

## Clustering & Diversity

### `cluster_mols(mols, cutoff=0.2, feature_fn=None, n_jobs=1)`
Clusters molecules using the Butina clustering algorithm.
- **Parameters**:
  - `cutoff`: Distance threshold (default 0.2)
  - `feature_fn`: Custom function for extracting molecular features
  - `n_jobs`: Parallelization (-1 to use all cores)
- **Important note**: This function builds a full distance matrix - suitable for ~1000 structures, not for 10,000+
- **Returns**: List of clusters (each cluster is a list of molecule indices)

### `pick_diverse(mols, npick, ...)`
Selects a diverse subset of molecules based on fingerprint diversity.

### `pick_centroids(mols, npick, ...)`
Selects centroid molecules representing clusters.

## Graph Operations

### `to_graph(mol)`
Converts a molecule to a graph representation for graph-based analysis.

### `get_all_path_between(mol, start, end)`
Finds all paths between two atoms in a molecular structure.

## DataFrame Integration

### `to_df(mols, smiles_column='smiles', mol_column='mol')`
Converts a list of molecules to a pandas DataFrame.

### `from_df(df, smiles_column='smiles', mol_column='mol')`
Converts a pandas DataFrame to a list of molecules.