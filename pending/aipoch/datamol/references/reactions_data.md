# Datamol Reaction and Data Module Reference

## Reaction Module (datamol.reactions)

The reaction module allows chemical transformations to be applied programmatically using SMARTS reaction patterns.

### Applying Chemical Reactions

#### dm.reactions.apply_reaction(rxn, reactants, as_smiles=False, sanitize=True, single_product_group=True, rm_attach=True, product_index=0)
Applies a chemical reaction to reactant molecules.

Parameters:

rxn: Reaction object (created from a SMARTS pattern)

reactants: Tuple of reactant molecules

as_smiles: Return SMILES strings (True) or molecule objects (False)

sanitize: Sanitize the product molecules

single_product_group: Return a single product (True) or all product groups (False)

rm_attach: Remove attachment point markers

product_index: Specify which product to return from the reaction

Returns: Product molecule(s) or SMILES

Example:

from rdkit import Chem

# Define reaction: alcohol + carboxylic acid → ester
rxn = Chem.rdChemReactions.ReactionFromSmarts(
    '[C:1][OH:2].[C:3](=[O:4])[OH:5]>>[C:1][O:2][C:3](=[O:4])'
)

# Apply to reactants
alcohol = dm.to_mol("CCO")
acid = dm.to_mol("CC(=O)O")
product = dm.reactions.apply_reaction(rxn, (alcohol, acid))

### Creating Reactions

Reactions are typically created from SMARTS patterns using RDKit:

from rdkit.Chem import rdChemReactions

# Reaction pattern: [reactant1].[reactant2]>>[product]
rxn = rdChemReactions.ReactionFromSmarts(
    '[1*][*:1].[1*][*:2]>>[*:1][*:2]'
)

### Validation Functions

The module includes functions for:

Checking if a molecule is a valid reactant: Verifies whether a molecule matches the reactant pattern

Validating reactions: Checks whether a reaction is synthetically reasonable

Handling reaction files: Loading reactions from files or databases

### Common Reaction Patterns

Amide synthesis:

# Amine + carboxylic acid → amide
amide_rxn = rdChemReactions.ReactionFromSmarts(
    '[N:1].[C:2](=[O:3])[OH]>>[N:1][C:2](=[O:3])'
)

Suzuki coupling:

# Aryl halide + boronic acid → biaryl
suzuki_rxn = rdChemReactions.ReactionFromSmarts(
    '[c:1][Br].[c:2][B]([OH])[OH]>>[c:1][c:2]'
)

Functional group transformation:

# Alcohol → ester
esterification = rdChemReactions.ReactionFromSmarts(
    '[C:1][OH:2].[C:3](=[O:4])[Cl]>>[C:1][O:2][C:3](=[O:4])'
)

### Workflow Example

import datamol as dm
from rdkit.Chem import rdChemReactions

# 1. Define reaction
rxn_smarts = '[C:1](=[O:2])[OH:3]>>[C:1](=[O:2])[Cl:3]'  # Acid → acyl chloride
rxn = rdChemReactions.ReactionFromSmarts(rxn_smarts)

# 2. Apply to molecule library
acids = [dm.to_mol(smi) for smi in acid_smiles_list]
acid_chlorides = []

for acid in acids:
    try:
        product = dm.reactions.apply_reaction(
            rxn,
            (acid,),  # Single reactant must be passed as a tuple
            sanitize=True
        )
        acid_chlorides.append(product)
    except Exception as e:
        print(f"Reaction failed: {e}")

# 3. Validate products
valid_products = [p for p in acid_chlorides if p is not None]

### Core Concepts

SMARTS: SMiles ARbitrary Target Specification — the pattern language for reactions

Atom Mapping: Numbers such as [C:1] preserve atomic identity during the reaction

Attachment Points: [1*] indicates generic attachment points

Reaction Validation: Not all SMARTS reactions are chemically reasonable

## Data Module (datamol.data)

The data module provides convenient access to curated molecular datasets for testing and learning purposes.

### Available Datasets

#### dm.data.cdk2(as_df=True, mol_column='mol')
RDKit CDK2 dataset — kinase inhibitor data.

Parameters:

as_df: Return DataFrame (True) or list of molecules (False)

mol_column: Name of the molecule column

Returns: Dataset containing molecular structures and activity data

Use case: Small dataset for algorithm testing

Example:

cdk2_df = dm.data.cdk2(as_df=True)
print(cdk2_df.shape)
print(cdk2_df.columns)

#### dm.data.freesolv()
FreeSolv dataset — experimentally measured and calculated hydration free energies.

Content: 642 molecules including:

IUPAC name

SMILES string

Experimental hydration free energy

Calculated value

Warning: “Intended only as a toy dataset for teaching and testing purposes”

Not suitable for: Benchmarking or production model training

Example:

freesolv_df = dm.data.freesolv()
# Columns: iupac, smiles, expt (kcal/mol), calc (kcal/mol)

#### dm.data.solubility(as_df=True, mol_column='mol')
RDKit solubility dataset with predefined train/test splits.

Content: Aqueous solubility data with predefined splits

Columns: Includes a 'split' column with values 'train' or 'test'

Use case: Testing machine learning workflows with proper train/test separation

Example:

sol_df = dm.data.solubility(as_df=True)

# Split into training/testing sets
train_df = sol_df[sol_df['split'] == 'train']
test_df = sol_df[sol_df['split'] == 'test']

# For model development
X_train = dm.to_fp(train_df[mol_column])
y_train = train_df['solubility']

### Usage Guide

For testing and tutorials:

# Quickly get a dataset for testing code
df = dm.data.cdk2()
mols = df['mol'].tolist()

# Test descriptor calculation
descriptors_df = dm.descriptors.batch_compute_many_descriptors(mols)

# Test clustering
clusters = dm.cluster_mols(mols, cutoff=0.3)

For learning workflows:

# Example of a complete machine learning pipeline
sol_df = dm.data.solubility()

# Preprocessing
train = sol_df[sol_df['split'] == 'train']
test = sol_df[sol_df['split'] == 'test']

# Feature engineering
X_train = dm.to_fp(train['mol'])
X_test = dm.to_fp(test['mol'])

# Model training (example)
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor()
model.fit(X_train, train['solubility'])
predictions = model.predict(X_test)

### Important Notes

Toy datasets: Designed specifically for teaching purposes, not for production use

Small scale: Limited number of compounds, suitable for quick testing

Preprocessed: Data have already been cleaned and formatted

Attribution: Check dataset documentation for proper citation if publishing results

### Best Practices

Use for development only: Do not draw scientific conclusions from toy datasets

Validate on real data: Always test production code on real project datasets

Proper attribution: Cite the original data source if used in publications

Understand limitations: Be aware of each dataset’s scope and quality