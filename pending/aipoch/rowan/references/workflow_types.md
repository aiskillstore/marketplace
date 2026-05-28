# Rowan Workflow Types Reference

## Table of Contents

1. [Property Prediction Workflows](#property-prediction-workflows)
2. [Molecular Modeling Workflows](#molecular-modeling-workflows)
3. [Protein-Ligand Workflows](#protein-ligand-workflows)
4. [Spectroscopy Workflows](#spectroscopy-workflows)
5. [Advanced Workflows](#advanced-workflows)

---

## Property Prediction Workflows

### pKa Calculation

Predicts acid dissociation constants.

```python
workflow = rowan.submit_pka_workflow(
    initial_molecule=mol,
    name="pKa calculation"
)
```

**Output:**
- `strongest_acid`: pKa of the most acidic proton
- `strongest_base`: pKa of the most basic site
- `microscopic_pkas`: List of pKa values for specific sites
- `tautomer_populations`: Relative distribution at pH 7

---

### Redox Potential

Calculates oxidation/reduction potentials.

```python
workflow = rowan.submit_redox_potential_workflow(
    initial_molecule=mol,
    name="redox potential"
)
```

**Output:**
- `oxidation_potential`: Oxidation potential E° (V vs SHE)
- `reduction_potential`: Reduction potential E° (V vs SHE)

---

### Solubility Prediction

Predicts aqueous and non-aqueous solubility.

```python
workflow = rowan.submit_solubility_workflow(
    initial_molecule=mol,
    name="solubility"
)
```

**Output:**
- `aqueous_solubility`: Log S in water
- `solubility_class`: "High", "Medium", or "Low"

---

### Hydrogen Bond Basicity

Calculates hydrogen bond acceptor strength.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="hydrogen_bond_basicity",
    workflow_data={},
    name="H-bond basicity"
)
```

**Output:**
- `hb_basicity`: pKBHX value

---

### Bond Dissociation Energy (BDE)

Calculates homolytic bond dissociation energies.

```python
workflow = rowan.submit_bde_workflow(
    initial_molecule=mol,
    bond_indices=(0, 1),  # Atom indices of the bond
    name="BDE calculation"
)
```

**Output:**
- `bde`: Bond dissociation energy (kcal/mol)
- `radical_stability`: Stability of the generated radical

---

### Fukui Indices

Calculates nucleophilic/electrophilic attack reactivity indices.

```python
workflow = rowan.submit_fukui_workflow(
    initial_molecule=mol,
    name="Fukui indices"
)
```

**Output:**
- `fukui_plus`: Electrophilic attack susceptibility per atom
- `fukui_minus`: Nucleophilic attack susceptibility per atom
- `fukui_dual`: Dual descriptor per atom

---

### Spin States

Calculates relative energies of different spin multiplicities.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="spin_states",
    workflow_data={},
    name="spin states"
)
```

**Output:**
- `spin_state_energies`: Energy per multiplicity
- `ground_state`: Lowest energy multiplicity

---

### ADME-Tox Prediction

Predicts absorption, distribution, metabolism, excretion, and toxicity.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="admet",
    workflow_data={},
    name="ADMET"
)
```

**Output:**
- Various ADMET descriptors including:
  - `logP`, `logD`
  - `herg_inhibition` (hERG inhibition)
  - `cyp_inhibition` (CYP inhibition)
  - `bioavailability`
  - `bbb_permeability` (blood-brain barrier permeability)

---

## Molecular Modeling Workflows

### Single Point Energy

Calculates energy at a fixed geometry.

```python
workflow = rowan.submit_basic_calculation_workflow(
    initial_molecule=mol,
    workflow_type="single_point",
    name="single point"
)
```

**Output:**
- `energy`: Total energy (Hartree)
- `dipole`: Dipole moment vector
- `mulliken_charges`: Mulliken atomic partial charges

---

### Geometry Optimization

Optimizes molecular geometry to the energy minimum.

```python
workflow = rowan.submit_basic_calculation_workflow(
    initial_molecule=mol,
    workflow_type="optimization",
    name="optimization"
)
```

**Output:**
- `final_molecule`: Optimized structure
- `energy`: Final energy (Hartree)
- `convergence`: Optimization convergence details

---

### Vibrational Frequency

Calculates infrared (IR)/Raman frequencies and thermodynamic properties.

```python
workflow = rowan.submit_basic_calculation_workflow(
    initial_molecule=mol,
    workflow_type="frequency",
    name="frequency"
)
```

**Output:**
- `frequencies`: Vibrational frequencies (cm⁻¹)
- `ir_intensities`: Infrared intensities
- `zpe`: Zero-point energy
- `thermal_corrections`: Enthalpy, entropy, Gibbs free energy corrections
- `imaginary_frequencies`: Number of imaginary frequencies

---

### Conformational Search

Generates and optimizes conformational ensembles.

```python
workflow = rowan.submit_conformer_search_workflow(
    initial_molecule=mol,
    name="conformer search"
)
```

**Output:**
- `conformers`: List of conformer structures with energies
- `lowest_energy_conformer`: Global lowest energy structure
- `boltzmann_weights`: Boltzmann weight distribution at 298 K

---

### Tautomer Search

Enumerates and ranks tautomers.

```python
workflow = rowan.submit_tautomer_search_workflow(
    initial_molecule=mol,
    name="tautomer search"
)
```

**Output:**
- `tautomers`: List of tautomer structures
- `energies`: Relative energies
- `populations`: Boltzmann distribution weights

---

### Dihedral Scan

Scans torsional energy surface.

```python
workflow = rowan.submit_dihedral_scan_workflow(
    initial_molecule=mol,
    dihedral_indices=(0, 1, 2, 3),  # Atom indices
    name="dihedral scan"
)
```

**Output:**
- `angles`: Scanned dihedral angles (degrees)
- `energies`: Energy at each angle
- `barrier_height`: Rotation barrier (kcal/mol)

---

### Multi-Stage Optimization

Uses multiple methods for progressive refinement.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="multistage_optimization",
    workflow_data={
        "stages": ["gfn2_xtb", "aimnet2", "dft"]
    },
    name="multistage opt"
)
```

**Output:**
- `final_molecule`: Optimized structure
- `stage_energies`: Energy after each stage

---

### Transition State Search

Finds transition state geometries.

```python
workflow = rowan.submit_ts_search_workflow(
    initial_molecule=mol,  # Initial guess structure near TS
    name="TS search"
)
```

**Output:**
- `ts_structure`: Transition state geometry
- `imaginary_frequency`: Single imaginary frequency
- `barrier_height`: Activation energy

---

### Strain Energy Calculation

Calculates ligand strain energy.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="strain",
    workflow_data={},
    name="strain"
)
```

**Output:**
- `strain_energy`: Conformational strain energy (kcal/mol)
- `reference_energy`: Energy of the lowest energy conformation

---

### Orbital Calculation

Calculates molecular orbitals.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="orbitals",
    workflow_data={},
    name="orbitals"
)
```

**Output:**
- `homo_energy`: HOMO energy (eV)
- `lumo_energy`: LUMO energy (eV)
- `homo_lumo_gap`: Band gap (eV)
- `orbital_coefficients`: Molecular orbital coefficients

---

## Protein-Ligand Workflows

### Molecular Docking

Docks ligands into protein binding sites.

```python
workflow = rowan.submit_docking_workflow(
    protein=protein_uuid,
    pocket={
        "center": [10.0, 20.0, 30.0],
        "size": [20.0, 20.0, 20.0]
    },
    initial_molecule=mol,
    executable="vina",           # "vina" or "qvina2"
    scoring_function="vinardo",  # "vina" or "vinardo"
    exhaustiveness=8,
    do_csearch=True,             # Conformational search before docking
    do_optimization=True,        # Optimize conformations
    do_pose_refinement=True,     # Refine poses with quantum mechanics (QM)
    name="docking"
)
```

**Output:**
- `docking_score`: Best Vina score (kcal/mol)
- `poses`: List of docked poses with scores
- `ligand_strain`: Strain energy of binding conformation
- `pose_sdf`: SDF file of poses

---

### Batch Docking

Screens multiple ligands against one target.

```python
workflow = rowan.submit_batch_docking_workflow(
    protein=protein_uuid,
    pocket=pocket_dict,
    smiles_list=["CCO", "c1ccccc1", "CC(=O)O"],
    executable="qvina2",
    scoring_function="vina",
    name="batch docking"
)
```

**Output:**
- `results`: List of docking results for each ligand
- `rankings`: Results sorted by score

---

### Protein Cofolding

Predicts protein-ligand complex structures using AI.

```python
workflow = rowan.submit_protein_cofolding_workflow(
    initial_protein_sequences=["MSKGEELFT..."],
    initial_smiles_list=["CCO"],
    model="boltz_2",       # "boltz_1x", "boltz_2", "chai_1r"
    use_msa_server=False,  # Use MSA for improved accuracy
    use_potentials=True,   # Apply physical constraints
    compute_strain=False,  # Calculate ligand strain
    do_pose_refinement=False,
    name="cofolding"
)
```

**Models:**
- `chai_1r`: Chai-1 model (~2 minutes)
- `boltz_1x`: Boltz-1 model (~2 minutes)
- `boltz_2`: Boltz-2 model (latest, recommended)

**Output:**
- `structure_pdb`: Predicted complex structure
- `ptm_score`: Predicted TM score (0-1, higher indicates higher confidence)
- `interface_ptm`: Interface prediction confidence
- `aggregate_score`: Overall confidence metric
- `ligand_rmsd`: RMSD if reference structure is provided

---

### Pose Analysis MD

Molecular dynamics simulation of docked poses.

```python
workflow = rowan.submit_workflow(
    initial_molecule=mol,
    workflow_type="pose_analysis_md",
    workflow_data={
        "protein_uuid": protein_uuid,
        "pose_sdf": pose_sdf_content
    },
    name="pose MD"
)
```

**Output:**
- `trajectory`: MD trajectory file
- `rmsd_over_time`: Ligand RMSD over time
- `interactions`: Protein-ligand interactions

---

## Spectroscopy Workflows

### NMR Prediction

Predicts NMR chemical shifts.

```python
workflow = rowan.submit_nmr_workflow(
    initial_molecule=mol,
    name="NMR"
)
```

**Output:**
- `h_shifts`: ¹H chemical shifts (ppm)
- `c_shifts`: ¹³C chemical shifts (ppm)
- `coupling_constants`: J-coupling constant values

---

### Ion Mobility

Predicts collision cross-section (CCS) for mass spectrometry analysis.

```python
workflow = rowan.submit_ion_mobility_workflow(
    initial_molecule=mol,
    name="ion mobility"
)
```

**Output:**
- `ccs`: Collision cross-section (Å²)
- `conformer_ccs`: CCS for each conformer

---

## Advanced Workflows

### Molecular Descriptors

Calculates comprehensive descriptor sets.

```python
workflow = rowan.submit_descriptors_workflow(
    initial_molecule=mol,
    name="descriptors"
)
```

**Output:**
- 2D descriptors (RDKit-based)
- 3D descriptors (xTB-based)
- Electronic descriptors

---

### MSA (Multiple Sequence Alignment)

Generates multiple sequence alignment for protein sequences.

```python
workflow = rowan.submit_msa_workflow(
    sequences=["MSKGEELFT..."],
    name="MSA"
)
```

**Output:**
- `msa`: Multiple sequence alignment result
- `coverage`: Sequence coverage

---

### Protein Binder Design (BoltzGen)

Designs protein binders.

```python
workflow = rowan.submit_workflow(
    workflow_type="protein_binder_design",
    workflow_data={
        "target_sequence": "MSKGEELFT...",
        "target_hotspots": [10, 15, 20]
    },
    name="binder design"
)
```

**Output:**
- `designed_sequences`: Designed binder sequences
- `confidence_scores`: Confidence score for each design

---

## Workflow Parameter Reference

### Common Parameters

All workflow submission functions accept the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | str | Workflow name (optional) |
| `folder_uuid` | str | Organize into folder |
| `max_credits` | float | Credit limit |

### Method Selection

For basic calculations, specify the method:

```python
workflow = rowan.submit_basic_calculation_workflow(
    initial_molecule=mol,
    workflow_type="optimization",
    workflow_data={
        "method": "gfn2_xtb",  # or "aimnet2", "dft"
        "basis_set": "def2-SVP"  # DFT only
    }
)
```

**Available methods:**
- Neural networks: `aimnet2`, `egret`
- Semi-empirical: `gfn1_xtb`, `gfn2_xtb`
- DFT: `b3lyp`, `pbe`, `wb97x`
