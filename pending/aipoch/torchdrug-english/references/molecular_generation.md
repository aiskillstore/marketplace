#Molecular Generation
## Overview
Molecular generation involves the creation of novel molecular structures with desired properties. TorchDrug supports unconditional generation (exploring chemical space) and conditional generation (optimizing for specific properties).
##Task Types
### AutoregressiveGeneration
Build molecules step by step by sequentially adding atoms and chemical bonds. This approach enables fine control and optimization of properties during the generation process.
**Core Features:**- Sequential "atom-chemical bond" construction- Supports property optimization during generation- Can be combined with chemical validity constraints-Support multi-objective optimization
**Generation Strategy:**1. **Beam Search**: Keep the top k candidate solutions at each step2. **Sampling**: Selection based on probability to increase diversity3. **Greedy algorithm (Greedy)**: Always choose the action with the highest probability
**Property Optimization:**- Reward shaping based on desired properties- Real-time constraint satisfaction- Multi-objective balance (for example: drug effect + drug-like properties)
### GCPN Generation (GCPNGeneration - Graph Convolution Policy Network)
Use reinforcement learning to generate molecules optimized for specific properties.
**Components:**1. **Policy Network**: Decide which action to take (add atoms, add chemical bonds)2. **Reward Function**: Evaluate the quality of the generated molecules3. **Training**: Reinforcement learning using policy gradient
**Advantages:**- Directly optimize non-differentiable goals- Can combine complex domain knowledge- Balance exploration and exploitation
**application:**- Drug design for specific targets- Material discovery with property constraints- Multi-objective molecular optimization
## Generative Models
````markdown
# Molecular Generation

## Overview

Molecular generation involves creating novel molecular structures with desired properties. TorchDrug supports both unconditional generation (exploring chemical space) and conditional generation (optimizing for specific properties).

## Task Types

### Autoregressive Generation

Molecules are generated step-by-step by sequentially adding atoms and bonds. This approach allows fine-grained control and property optimization during generation.

**Key features:**
- Sequential "atom-then-bond" construction
- Supports property optimization during generation
- Can incorporate chemical validity constraints
- Supports multi-objective optimization

**Generation strategies:**
1. **Beam Search**: keep top-k candidates at each step
2. **Sampling**: sample actions stochastically to increase diversity
3. **Greedy**: always pick the most probable action

**Property optimization:**
- Reward shaping based on desired properties
- On-the-fly constraint satisfaction
- Multi-objective balancing (e.g., potency + drug-likeness)

### GCPN Generation (Graph Convolutional Policy Network)

Use reinforcement learning to generate molecules optimized for desired properties.

**Components:**
1. **Policy network**: decides actions (add atom, add bond, etc.)
2. **Reward function**: evaluates generated molecules
3. **Training**: policy-gradient-based reinforcement learning

**Advantages:**
- Direct optimization of non-differentiable objectives
- Can incorporate complex domain knowledge
- Balances exploration and exploitation

**Applications:**
- Drug design for specific targets
- Materials discovery with property constraints
- Multi-objective molecular optimization

## Generative Models

### GraphAutoregressiveFlow

A normalizing flow model for molecular generation with exact likelihoods.

**Architecture:**
- Coupling layers transform simple base distributions into complex molecular distributions
- Invertible transforms enable density estimation
- Supports conditional generation

**Key features:**
- Exact likelihoods (vs. VAE's approximate likelihood)
- Stable training (vs. GAN adversarial training)
- Efficient sampling via invertible transforms
- Can generate molecules conditioned on properties

**Training:**
- Maximum likelihood training on molecular datasets
- Optional property prediction heads for conditional generation
- Commonly trained on ZINC or QM9 datasets

**Use cases:**
- Generating diverse drug-like molecules
- Interpolation between known molecules
- Density estimation in molecular space

## Generation Workflows

### Unconditional Generation

Generate diverse molecules without specific property targets.

**Workflow:**
1. Train a generative model on a molecular dataset (e.g., ZINC250k)
2. Sample from the learned distribution
3. Post-process for validity and uniqueness
4. Evaluate diversity metrics

**Evaluation metrics:**
- **Validity**: fraction of chemically valid molecules
- **Uniqueness**: fraction of non-duplicate molecules among valid ones
- **Novelty**: fraction of molecules not in the training set
- **Diversity**: internal diversity measured by fingerprint similarity

### Conditional Generation

Generate molecules optimized for specific properties.

**Property targets:**
- **Drug-likeness**: LogP, QED, Lipinski rules
- **Synthesizability**: SA score, retrosynthetic feasibility
- **Bioactivity**: predicted IC50, binding affinity
- **ADMET**: absorption, distribution, metabolism, excretion, toxicity
- **Multi-objective**: balancing multiple properties simultaneously

**Workflow:**
1. Define a reward function combining multiple property objectives
2. Train GCPN or conditional flow models for the properties
3. Generate molecules within the desired property ranges
4. Validate generated molecules (in silico → wet lab)

### Scaffold-Based Generation

Generate molecules around a fixed scaffold or core structure.

**Applications:**
- Lead optimization while preserving core pharmacophores
- R-group enumeration for SAR studies
- Fragment linking and growing

**Methods:**
- Mask the scaffold during training
- Condition generation on a scaffold
- Post-generation grafting and decoration

### Fragment-Based Generation

Build molecules from validated fragments.

**Benefits:**
- Ensures drug-like substructures
- Reduces search space
- Incorporates medicinal chemistry knowledge

**Methods:**
- Use a fragment library as building blocks
- Vocabulary-based generation over fragments
- Learnable linkers for fragment connection

## Property Optimization Strategies

### Single-Objective Optimization

Maximize or minimize a single property (e.g., binding affinity).

**Methods:**
- Define a scalar reward function
- Train with GCPN using reinforcement learning
- Generate and rank candidate molecules

**Challenges:**
- May sacrifice other important properties
- Risk of adversarial examples (valid but non-drug-like)
- Need to enforce drug-likeness constraints

### Multi-Objective Optimization

Balance multiple competing objectives (e.g., potency, selectivity, synthesizability).

**Weighting methods:**
- **Linear combination**: w1×prop1 + w2×prop2 + ...
- **Pareto optimization**: search for non-dominated solutions
- **Constraint satisfaction**: set thresholds for secondary objectives

**Example targets:**
- High target affinity
- Low off-target affinity
- High synthesizability (SA score)
- Drug-likeness (QED)
- Low molecular weight

**Workflow example:**
```python
from torchdrug import tasks

# Define multi-objective reward
def reward_function(mol):
    affinity_score = predict_binding(mol)
    druglikeness = calculate_qed(mol)
    synthesizability = sa_score(mol)

    # weighted combination
    reward = 0.5 * affinity_score + 0.3 * druglikeness + 0.2 * (1 - synthesizability)
    return reward

# GCPN task with custom reward
task = tasks.GCPNGeneration(
    model,
    reward_function=reward_function,
    criterion="ppo"  # proximal policy optimization
)
```

### Constraint-Based Generation

Generate molecules that satisfy hard constraints.

**Common constraints:**
- Molecular weight range
- LogP range
- Number of rotatable bonds
- Ring count limits
- Substructure inclusion/exclusion
- Synthesizability thresholds

**Implementation:**
- Validity checks during generation
- Early termination for invalid molecules
- Penalty terms in the reward function

## Training Considerations

### Dataset Selection

**ZINC (drug-like compounds):**
- ZINC250k: 250,000 compounds
- ZINC2M: 2 million compounds
- Pre-filtered for drug-likeness
- Suitable for drug discovery applications

**QM9 (small organic molecules):**
- 133,885 molecules
- Includes quantum properties
- Suitable for property-prediction models

**ChEMBL (bioactive molecules):**
- Millions of bioactive compounds
- Provides activity data
- Useful for target-specific generation

**Custom datasets:**
- Focused on specific chemical spaces
- Incorporate expert knowledge
- Domain-specific constraints

### Data Augmentation

**SMILES augmentation:**
- Generate multiple SMILES for the same molecule
- Helps the model learn canonical representations
- Improves robustness

**Graph augmentations:**
- Random node/edge masking
- Subgraph sampling
- Motif replacement

### Model Architecture Choices

**For small molecules (<30 atoms):**
- Simple architectures suffice
- Faster training and generation
- Use GCN or GIN backbones

**For drug-like molecules:**
- Deeper architectures (4–6 layers)
- Attention mechanisms can help
- Consider molecular fingerprints

**For macrocycles/polymers:**
- Handle larger graphs
- Ring-closure mechanisms are critical
- Consider long-range dependencies

## Validation and Filtering

### In Silico Validation

**Chemical validity:**
- Valence rules
- Aromaticity rules
- Neutrality of charge
- Stable substructures

**Drug-likeness filters:**
- Lipinski rules
- Veber rules
- PAINS filters (pan-assay interference compounds)
- BRENK filters (toxic/reactive substructures)

**Synthesizability:**
- SA score (synthetic accessibility)
- Retrosynthetic feasibility
- Commercial availability of precursors

**Property prediction:**
- ADMET properties
- Toxicity prediction
- Off-target binding
- Metabolic stability

### Ranking and Selection

**Criteria:**
1. Predicted target affinity
2. Drug-likeness score
3. Synthesizability
4. Novelty (difference from known actives)
5. Diversity (within the generated set)
6. Predicted ADMET properties

**Selection strategies:**
- Pareto frontier selection
- Weighted scoring
- Clustering and representative selection
- Active learning for wet-lab prioritization

## Best Practices

1. **Start simple**: begin with unconditional generation, then add constraints.
2. **Validate chemical properties**: always check validity and drug-likeness.
3. **Diverse training data**: use large, diverse datasets for better generalization.
4. **Multi-objective from the start**: consider multiple properties early.
5. **Iterative improvement**: generate → validate → retrain with feedback.
6. **Expert review**: consult medicinal chemists before synthesis.
7. **Benchmarking**: compare against known actives and random baselines.
8. **Prioritize synthesizability**: favor molecules that can be practically made.
9. **Interpretability**: understand why models generate specific structures.
10. **Wet-lab validation**: ultimately validate promising candidates experimentally.

## Common Applications

### Drug Discovery
- Lead generation for novel targets
- Lead optimization around active scaffolds
- Bioisosteric replacements
- Fragment elaboration

### Materials Science
- Designing polymers with target properties
- Catalyst discovery
- Energy storage materials
- Photovoltaic materials

### Chemical Biology
- Probe molecule design
- PROTAC design
- Molecular glue discovery

## Integration with Other Tools

**Docking:**
- Generate molecules → dock to target → retrain using docking scores

**Retrosynthesis:**
- Filter generated molecules by synthetic accessibility
- Plan synthetic routes for top candidates

**Property prediction:**
- Use pretrained property predictors as reward functions
- Joint generation and prediction via multi-task learning

**Active learning:**
- Generate candidate molecules → predict properties → synthesize optimal molecules → retrain

````
