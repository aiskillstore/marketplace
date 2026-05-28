# Datamol Fragments and Scaffolds Reference

## Scaffold Module (datamol.scaffold)

- Scaffolds represent the core structure of a molecule and are commonly used to identify structural families and analyze structure–activity relationships (SAR).

### Murcko Scaffold

#### dm.to_scaffold_murcko(mol)
- Extracts the Bemis–Murcko scaffold (molecular framework).

- Method: Removes side chains while retaining ring systems and linker chains.

- Returns: A molecule object representing the scaffold.

- Use case: Identifying core structures within compound series.

- Example:

    - mol = dm.to_mol("c1ccc(cc1)CCN")  # Phenethylamine
    - scaffold = dm.to_scaffold_murcko(mol)
    - scaffold_smiles = dm.to_smiles(scaffold)
# Returns: 'c1ccccc1CC' (benzene ring + ethyl linker)

- Scaffold analysis workflow:

# Extract scaffolds from a compound library
- scaffolds = [dm.to_scaffold_murcko(mol) for mol in mols]
- scaffold_smiles = [dm.to_smiles(s) for s in scaffolds]

# Count scaffold frequency
- from collections import Counter
- scaffold_counts = Counter(scaffold_smiles)
- most_common = scaffold_counts.most_common(10)

### Fuzzy Scaffolds

#### dm.scaffold.fuzzy_scaffolding(mol, ...)
- Generates fuzzy scaffolds and optionally enforces specific groups to be present in the core.

- Purpose: Provides a more flexible scaffold definition than Murcko rules, allowing specification of required functional groups.

- Use case: Custom scaffold definitions beyond standard Murcko extraction.

### Applications

- Scaffold-based dataset splitting (for machine learning model validation):

# Group compounds by scaffold

```python 
scaffold_to_mols = {}
for mol, scaffold in zip(mols, scaffolds):
    smi = dm.to_smiles(scaffold)
    if smi not in scaffold_to_mols:
        scaffold_to_mols[smi] = []
    scaffold_to_mols[smi].append(mol)
```

# Ensure training and test sets contain different scaffolds

- SAR analysis:

# Group by scaffold and analyze activity
for scaffold_smi, molecules in scaffold_to_mols.items():
    activities = [get_activity(mol) for mol in molecules]
    print(f"Scaffold: {scaffold_smi}, Mean activity: {np.mean(activities)}")

## Fragment Module (datamol.fragment)

- Molecular fragmentation breaks molecules into smaller units based on chemical rules, supporting fragment-based drug design and substructure analysis.

### BRICS Fragmentation

#### dm.fragment.brics(mol, ...)
- Performs molecular fragmentation using the BRICS (Breaking Retrosynthetically Interesting Chemical Substructures) method.

- Method: Cleaves bonds based on 16 chemically meaningful bond types.

- Consideration: Takes into account chemical environment and neighboring substructures.

- Returns: A set of fragment SMILES strings.

- Use case: Retrosynthetic analysis and fragment-based design.

- Example:

    - mol = dm.to_mol("c1ccccc1CCN")
    - fragments = dm.fragment.brics(mol)
# Returns fragments such as: '[1*]CCN', '[1*]c1ccccc1', etc.
# [1*] indicates an attachment point

### RECAP Fragmentation

#### dm.fragment.recap(mol, ...)
- Performs molecular fragmentation using the RECAP (Retrosynthetic Combinatorial Analysis Procedure) method.

- Method: Cleaves bonds based on 11 predefined bond types.

- Rules:

    - Retains alkyl chains shorter than 5 carbons.

    - Preserves ring bonds.

- Returns: A set of fragment SMILES strings.

- Use case: Combinatorial library design.

- Example:

    - mol = dm.to_mol("CCCCCc1ccccc1")
    - fragments = dm.fragment.recap(mol)

### MMPA Fragmentation

#### dm.fragment.mmpa_frag(mol, ...)
- ragmentation for Matched Molecular Pair Analysis (MMPA).

- Purpose: Generates fragments suitable for identifying matched molecular pairs.

- Use case: Analyzing how small structural changes affect properties.

- Example:

    - fragments = dm.fragment.mmpa_frag(mol)
# Used to find molecular pairs differing by a single transformation

### Method Comparison

Method	Number of Bond Types	Preserves Rings	Best Use Case
BRICS	16	Yes	Retrosynthetic analysis, fragment recombination
RECAP	11	Yes	Combinatorial library design
MMPA	Variable	Depends	Structure–activity relationship (SAR) analysis

### Fragmentation Workflow

import datamol as dm

# 1. Fragment a molecule
mol = dm.to_mol("CC(=O)Oc1ccccc1C(=O)O")  # Aspirin
brics_frags = dm.fragment.brics(mol)
recap_frags = dm.fragment.recap(mol)

# 2. Analyze fragment frequency across a library
all_fragments = []
for mol in molecule_library:
    frags = dm.fragment.brics(mol)
    all_fragments.extend(frags)

# 3. Identify common fragments
from collections import Counter
fragment_counts = Counter(all_fragments)
common_fragments = fragment_counts.most_common(20)

# 4. Convert fragments back to molecules (remove attachment points)
def clean_fragment(frag_smiles):
    # Remove attachment point markers such as [1*], [2*]
    clean = frag_smiles.replace('[1*]', '[H]')
    return dm.to_mol(clean)

### Advanced Application: Fragment-Based Virtual Screening

# Build a fragment library from known active compounds
active_fragments = set()
for active_mol in active_compounds:
    frags = dm.fragment.brics(active_mol)
    active_fragments.update(frags)

# Score compounds based on presence of active fragments
def score_by_fragments(mol, fragment_set):
    mol_frags = dm.fragment.brics(mol)
    overlap = mol_frags.intersection(fragment_set)
    return len(overlap) / len(mol_frags)

# Score screening library
scores = [score_by_fragments(mol, active_fragments) for mol in screening_lib]

### Core Concepts

Attachment Points: Marked as [1*], [2*], etc., in fragment SMILES.

Retrosynthetic: Fragmentation mimics bond disconnections used in synthesis.

Chemically Meaningful: Cleavages occur at typical synthetic bond positions.

Recombination: Fragments can theoretically be recombined into valid molecules.