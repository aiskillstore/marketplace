# Datamol Conformers module reference

`datamol.conformers` provides utilities to generate and analyze molecular 3D conformations.

## Conformer Generation

### `dm.conformers.generate(mol, n_confs=None, rms_cutoff=None, minimize_energy=True, method='ETKDGv3', add_hs=True, ...)`
Generate 3D conformers for a molecule.
- **Parameters**:
  - `mol`: Input molecule.
  - `n_confs`: Number of conformers to generate (if None, determined automatically from rotatable bonds).
  - `rms_cutoff`: RMS threshold (in Å) used to filter similar conformers and remove duplicates.
  - `minimize_energy`: Whether to apply UFF energy minimization (default: True).
  - `method`: Embedding method — options include:
    - `'ETDG'` — Experimental Torsion Distance Geometry.
    - `'ETKDG'` — ETDG with additional priors.
    - `'ETKDGv2'` — Enhanced version 2.
    - `'ETKDGv3'` — Enhanced version 3 (default, recommended).
  - `add_hs`: Add hydrogens before embedding (default: True; important for conformer quality).
  - `random_seed`: Set random seed for reproducibility.
- **Returns**: Molecule with embedded conformers.
- **Example**:
  ```python
  mol = dm.to_mol("CCO")
  mol_3d = dm.conformers.generate(mol, n_confs=10, rms_cutoff=0.5)
  conformers = mol_3d.GetConformers()  # get all conformers
  ```

## Conformer Clustering

### `dm.conformers.cluster(mol, rms_cutoff=1.0, already_aligned=False, centroids=False)`
Group conformers by RMS distance.
- **Parameters**:
  - `rms_cutoff`: Clustering threshold (in Å, default: 1.0).
  - `already_aligned`: Whether conformers are pre-aligned.
  - `centroids`: Return centroid conformers (True) or cluster assignments (False).
- **Returns**: Clustering information or centroid conformers.
- **Use case**: Identify distinct conformer families.

### `dm.conformers.return_centroids(mol, conf_clusters, centroids=True)`
Extract representative conformers from clusters.
- **Parameters**:
  - `conf_clusters`: Cluster index sequence returned by `cluster()`.
  - `centroids`: Return a single molecule per centroid (True) or a list of molecules (False).
- **Returns**: Centroid conformers.

## Conformer Analysis

### `dm.conformers.rmsd(mol)`
Compute the pairwise RMSD matrix between all conformers.
- **Requirements**: At least 2 conformers are required.
- **Returns**: An NxN matrix of RMSD values.
- **Use case**: Quantify conformer diversity.

### `dm.conformers.sasa(mol, n_jobs=1, ...)`
Compute solvent-accessible surface area (SASA) using FreeSASA.
- **Parameters**:
  - `n_jobs`: Number of parallel jobs for multiple conformers.
- **Returns**: Array of SASA values (one per conformer).
- **Storage**: Values are stored as the conformer property `'rdkit_free_sasa'`.
- **Example**:
  ```python
  sasa_values = dm.conformers.sasa(mol_3d)
  # or access from conformer properties
  conf = mol_3d.GetConformer(0)
  sasa = conf.GetDoubleProp('rdkit_free_sasa')
  ```

## Low-Level Conformer Manipulation

### `dm.conformers.center_of_mass(mol, conf_id=-1, use_atoms=True, round_coord=None)`
Compute the molecular center.
- **Parameters**:
  - `conf_id`: Conformer index (-1 indicates the first conformer).
  - `use_atoms`: Use atomic masses (True) or geometric center (False).
  - `round_coord`: Decimal precision for rounding coordinates.
- **Returns**: 3D coordinates of the center.
- **Use case**: Center molecules for visualization or alignment.

### `dm.conformers.get_coords(mol, conf_id=-1)`
Get atomic coordinates from a conformer.
- **Returns**: Nx3 numpy array of atomic positions.
- **Example**:
  ```python
  positions = dm.conformers.get_coords(mol_3d, conf_id=0)
  # positions.shape: (num_atoms, 3)
  ```

### `dm.conformers.translate(mol, conf_id=-1, transform_matrix=None)`
Reposition a conformer using a transformation matrix.
- **Mutation**: Operates in-place.
- **Use case**: Align or reposition molecules.

## Workflow example

```python
import datamol as dm

# 1. Create a molecule and generate conformers
mol = dm.to_mol("CC(C)CCO")  # isopentanol
mol_3d = dm.conformers.generate(
    mol,
    n_confs=50,           # generate 50 initial conformers
    rms_cutoff=0.5,       # filter similar conformers
    minimize_energy=True  # energy minimization
)

# 2. Analyze conformers
n_conformers = mol_3d.GetNumConformers()
print(f"Generated {n_conformers} unique conformers")

# 3. Compute SASA
sasa_values = dm.conformers.sasa(mol_3d)

# 4. Conformer clustering
clusters = dm.conformers.cluster(mol_3d, rms_cutoff=1.0, centroids=False)

# 5. Get representative conformers
centroids = dm.conformers.return_centroids(mol_3d, clusters)

# 6. Access 3D coordinates
coords = dm.conformers.get_coords(mol_3d, conf_id=0)
```

## Key concepts

- **Distance Geometry**: A method to generate 3D structures from connectivity information.
- **ETKDG**: A method that uses experimental torsion preferences and additional chemical priors.
- **RMS Cutoff**: Lower values = more unique conformers; higher values = fewer but more distinct conformers.
- **Energy Minimization**: Relax a structure to the nearest local energy minimum.
- **Hydrogens**: Hydrogens are important for accurate 3D geometry — include them during embedding.