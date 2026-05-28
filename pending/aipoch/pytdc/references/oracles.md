# TDC Molecular Generation Oracles (Prediction Functions)

Oracles are functions that evaluate the quality of generated molecules across specific dimensions. TDC provides over 17 Oracle functions for molecular optimization tasks in de novo drug design.

## Overview

Oracles are used to measure molecular properties, primarily for two purposes:

1. **Goal-directed generation**: Optimizing molecules to maximize/minimize specific properties.
2. **Distribution learning**: Evaluating whether generated molecules match the expected property distribution.

## Using Oracles

### Basic Usage

```python
from tdc import Oracle

# Initialize oracle
oracle = Oracle(name='GSK3B')

# Evaluate a single molecule (SMILES string)
score = oracle('CC(C)Cc1ccc(cc1)C(C)C(O)=O')

# Evaluate multiple molecules
scores = oracle(['SMILES1', 'SMILES2', 'SMILES3'])
```

### Oracle Categories

TDC Oracles are categorized into the following groups based on the molecular properties being evaluated.

## Biochemical Oracles

Predicting the binding affinity or activity of molecules against biological targets.

### Target-Specific Oracles

**DRD2 - Dopamine Receptor D2**
```python
oracle = Oracle(name='DRD2')
score = oracle(smiles)
```
- Measures binding affinity to the DRD2 receptor
- Significant for neurological and psychiatric drug development
- Higher scores indicate stronger binding affinity

**GSK3B - Glycogen Synthase Kinase-3 Beta**
```python
oracle = Oracle(name='GSK3B')
score = oracle(smiles)
```
- Predicts GSK3β inhibitory activity
- Relevant to Alzheimer's, diabetes, and cancer research
- Higher scores indicate better inhibitory effect

**JNK3 - c-Jun N-terminal Kinase 3**
```python
oracle = Oracle(name='JNK3')
score = oracle(smiles)
```
- Measures JNK3 kinase inhibitory activity
- Target for neurodegenerative diseases
- Higher scores indicate stronger inhibition

**5HT2A - 5-Hydroxytryptamine Receptor 2A**
```python
oracle = Oracle(name='5HT2A')
score = oracle(smiles)
```
- Predicts serotonin receptor binding
- Crucial for psychiatric drugs
- Higher scores indicate stronger binding affinity

**ACE - Angiotensin-Converting Enzyme**
```python
oracle = Oracle(name='ACE')
score = oracle(smiles)
```
- Measures ACE inhibitory activity
- Target for hypertension treatment
- Higher scores indicate better inhibitory effect

**MAPK - Mitogen-Activated Protein Kinase**
```python
oracle = Oracle(name='MAPK')
score = oracle(smiles)
```
- Predicts MAPK inhibitory activity
- Target for cancer and inflammatory diseases

**CDK - Cyclin-Dependent Kinase**
```python
oracle = Oracle(name='CDK')
score = oracle(smiles)
```
- Measures CDK inhibitory activity
- Significant for anticancer drug development

**P38 - p38 MAP Kinase**
```python
oracle = Oracle(name='P38')
score = oracle(smiles)
```
- Predicts p38 MAPK inhibitory activity
- Target for inflammatory diseases

**PARP1 - Poly [ADP-ribose] polymerase 1**
```python
oracle = Oracle(name='PARP1')
score = oracle(smiles)
```
- Measures PARP1 inhibitory activity
- Cancer treatment target (DNA repair mechanism)

**PIK3CA - Phosphatidylinositol-4,5-bisphosphate 3-kinase**
```python
oracle = Oracle(name='PIK3CA')
score = oracle(smiles)
```
- Predicts PIK3CA inhibitory activity
- Important target in oncology

## Physicochemical Property Oracles

Evaluating drug-likeness properties and ADME characteristics.

### Drug-likeness Oracles

**QED - Quantitative Estimate of Drug-likeness**
```python
oracle = Oracle(name='QED')
score = oracle(smiles)
```
- Integrates multiple physicochemical properties
- Score range from 0 (non-drug-like) to 1 (drug-like)
- Based on criteria by Bickerton et al.

**Lipinski - Rule of Five**
```python
oracle = Oracle(name='Lipinski')
score = oracle(smiles)
```
- Number of Lipinski rule violations
- Rules: MW ≤ 500, logP ≤ 5, HBD ≤ 5, HBA ≤ 10
- A score of 0 indicates full compliance with the rules

### Molecular Properties

**SA - Synthetic Accessibility**
```python
oracle = Oracle(name='SA')
score = oracle(smiles)
```
- Estimates the ease of synthesis
- Score range from 1 (easy) to 10 (difficult)
- Lower scores indicate easier synthesis

**LogP - Octanol-Water Partition Coefficient**
```python
oracle = Oracle(name='LogP')
score = oracle(smiles)
```
- Measures lipophilicity
- Crucial for cell membrane permeability
- Typical drug-like range: 0-5

**MW - Molecular Weight**
```python
oracle = Oracle(name='MW')
score = oracle(smiles)
```
- Returns molecular weight in Daltons
- Drug-like range is typically 150-500 Da

## Composite Oracles

Combining multiple properties for multi-objective optimization.

**Isomer Meta**
```python
oracle = Oracle(name='Isomer_Meta')
score = oracle(smiles)
```
- Evaluates specific isomer properties
- Used for stereochemical optimization

**Median Molecules**
```python
oracle = Oracle(name='Median1', 'Median2')
score = oracle(smiles)
```
- Tests the ability to generate molecules with median property scores
- Suitable for distribution learning benchmarks

**Rediscovery**
```python
oracle = Oracle(name='Rediscovery')
score = oracle(smiles)
```
- Measures similarity to known reference molecules
- Tests the ability to rediscover existing drugs

**Similarity**
```python
oracle = Oracle(name='Similarity')
score = oracle(smiles)
```
- Calculates structural similarity to a target molecule
- Based on molecular fingerprints (usually Tanimoto similarity)

**Uniqueness**
```python
oracle = Oracle(name='Uniqueness')
scores = oracle(smiles_list)
```
- Measures the diversity of the generated molecular set
- Returns the proportion of unique molecules

**Novelty**
```python
oracle = Oracle(name='Novelty')
scores = oracle(smiles_list, training_set)
```
- Measures the degree of difference between generated molecules and the training set
- Higher scores indicate more novel structures

## Specialized Oracles

**ASKCOS - Retrosynthesis Score**
```python
oracle = Oracle(name='ASKCOS')
score = oracle(smiles)
```
- Evaluates synthetic feasibility using retrosynthesis
- Requires ASKCOS backend (IBM RXN)
- Scores based on the availability of retrosynthetic routes

**Docking Score**
```python
oracle = Oracle(name='Docking')
score = oracle(smiles)
```
- Molecular docking score against a target protein
- Requires protein structure and docking software
- Lower scores usually indicate better binding

**Vina - AutoDock Vina Score**
```python
oracle = Oracle(name='Vina')
score = oracle(smiles)
```
- Protein-ligand docking using AutoDock Vina
- Predicts binding affinity (unit: kcal/mol)
- Larger negative values indicate stronger binding affinity

## Multi-objective Optimization

Combining multiple Oracles for multi-attribute optimization:

```python
from tdc import Oracle

# Initialize multiple oracles
qed_oracle = Oracle(name='QED')
sa_oracle = Oracle(name='SA')
drd2_oracle = Oracle(name='DRD2')

# Define custom scoring function
def multi_objective_score(smiles):
    qed = qed_oracle(smiles)
    sa = 1 / (1 + sa_oracle(smiles))  # Invert SA (lower is better)
    drd2 = drd2_oracle(smiles)

    # Weighted combination
    return 0.3 * qed + 0.3 * sa + 0.4 * drd2

# Evaluate molecule
score = multi_objective_score('CC(C)Cc1ccc(cc1)C(C)C(O)=O')
```

## Oracle Performance Considerations

### Speed
- **Fast**: QED, SA, LogP, MW, Lipinski (rule-based calculations)
- **Medium**: Target-specific machine learning models (DRD2, GSK3B, etc.)
- **Slow**: Docking-based Oracles (Vina, ASKCOS)

### Reliability
- Oracles are machine learning models trained on specific datasets
- May not generalize to all chemical spaces
- Recommended to use multiple Oracles to validate results

### Batch Processing
```python
# Efficient batch evaluation
oracle = Oracle(name='GSK3B')
smiles_list = ['SMILES1', 'SMILES2', ..., 'SMILES1000']
scores = oracle(smiles_list)  # Faster than calling individually
```

## Common Workflows

### Goal-directed Generation
```python
from tdc import Oracle
from tdc.generation import MolGen

# Load training data
data = MolGen(name='ChEMBL_V29')
train_smiles = data.get_data()['Drug'].tolist()

# Initialize oracle
oracle = Oracle(name='GSK3B')

# Generate molecules (user-implemented generative model)
# generated_smiles = generator.generate(n=1000)

# Evaluate generated molecules
scores = oracle(generated_smiles)
best_molecules = [(s, score) for s, score in zip(generated_smiles, scores)]
best_molecules.sort(key=lambda x: x[1], reverse=True)

print(f"Top 10 molecules:")
for smiles, score in best_molecules[:10]:
    print(f"{smiles}: {score:.3f}")
```

### Distribution Learning
```python
from tdc import Oracle
import numpy as np

# Initialize oracle
oracle = Oracle(name='QED')

# Evaluate training set
train_scores = oracle(train_smiles)
train_mean = np.mean(train_scores)
train_std = np.std(train_scores)

# Evaluate generated set
gen_scores = oracle(generated_smiles)
gen_mean = np.mean(gen_scores)
gen_std = np.std(gen_scores)

# Compare distributions
print(f"Training: μ={train_mean:.3f}, σ={train_std:.3f}")
print(f"Generated: μ={gen_mean:.3f}, σ={gen_std:.3f}")
```

## Integration with TDC Benchmarks

```python
from tdc.generation import MolGen

# Use GuacaMol benchmark
data = MolGen(name='GuacaMol')

# Oracles are automatically integrated
# Each GuacaMol task has an associated oracle
benchmark_results = data.evaluate_guacamol(
    generated_molecules=your_molecules,
    oracle_name='GSK3B'
)
```

## Notes

- Oracle scores are predicted values, not experimental measurements
- Always validate top candidates through experiments
- Different Oracles may have different score ranges and interpretations
- Some Oracles require additional dependencies or API access
- Check Oracle documentation for detailed information: https://tdcommons.ai/functions/oracles/

## Adding Custom Oracles

Create custom Oracle functions:

```python
class CustomOracle:
    def __init__(self):
        # Initialize your model/method
        pass

    def __call__(self, smiles):
        # Implement your scoring logic
        # Return score or list of scores
        pass

# Use it just like a built-in Oracle
custom_oracle = CustomOracle()
score = custom_oracle('CC(C)Cc1ccc(cc1)C(C)C(O)=O')
```

## References

- TDC Oracles Documentation: https://tdcommons.ai/functions/oracles/
- GuacaMol Paper: "GuacaMol: Benchmarking Models for de Novo Molecular Design"
- MOSES Paper: "Molecular Sets (MOSES): A Benchmarking Platform for Molecular Generation Models"