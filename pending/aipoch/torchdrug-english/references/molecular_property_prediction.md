# Molecular Property Prediction

## Overview

Molecular property prediction involves predicting chemical, physical, or biological properties of molecules from their structures. TorchDrug provides comprehensive support for classification and regression tasks on molecular graphs.

## Available Datasets

### Drug Discovery Datasets

**Classification tasks:**
- **BACE** (1,513 molecules): binary classification for β-secretase inhibitors
- **BBBP** (2,039 molecules): blood–brain barrier permeability prediction
- **HIV** (41,127 molecules): inhibition of HIV replication
- **Tox21** (7,831 molecules): toxicity prediction across 12 targets
- **ToxCast** (8,576 molecules): toxicology screening
- **ClinTox** (1,478 molecules): clinical trial toxicity
- **SIDER** (1,427 molecules): drug side effects (27 system organ classes)
- **MUV** (93,087 molecules): Maximum Unbiased Validation set for virtual screening

**Regression tasks:**
- **ESOL** (1,128 molecules): aqueous solubility
- **FreeSolv** (642 molecules): hydration free energy
- **Lipophilicity** (4,200 molecules): octanol/water partition coefficient
- **SAMPL** (643 molecules): solvation free energy

### Large-Scale Datasets

- **QM7** (7,165 molecules): quantum mechanical properties
- **QM8** (21,786 molecules): electronic spectra and excited-state properties
- **QM9** (133,885 molecules): geometry, energy, electronic, and thermodynamic properties
- **PCQM4M** (3,803,453 molecules): large-scale quantum chemistry dataset
- **ZINC250k/2M** (250k/2M molecules): drug-like compounds for generative modeling

## Task Types

### PropertyPrediction

Standard graph-level property prediction task supporting classification and regression.

**Key parameters:**
- `model`: graph representation model (GNN)
- `task`: prediction level (`node`, `edge`, or `graph`)
- `criterion`: loss (`mse`, `bce`, `ce`)
- `metric`: evaluation metrics (`mae`, `rmse`, `auroc`, `auprc`)
- `num_mlp_layer`: number of MLP layers used in readout

**Example workflow:**
```python
import torch
from torchdrug import core, models, tasks, datasets

# Load dataset
dataset = datasets.BBBP("~/molecule-datasets/")

# Define model
model = models.GIN(input_dim=dataset.node_feature_dim,
                   hidden_dims=[256, 256, 256, 256],
                   edge_input_dim=dataset.edge_feature_dim,
                   batch_norm=True, readout="mean")

# Define task
task = tasks.PropertyPrediction(model, task=dataset.tasks,
                                 criterion="bce",
                                 metric=("auprc", "auroc"))
```

### MultipleBinaryClassification

Task for multi-label settings where each molecule can have multiple binary labels (e.g., Tox21, SIDER).

**Key features:**
- Graceful handling of missing labels
- Per-label metrics and averaged metrics
- Support for class-weighted losses for imbalanced datasets

## Model Selection

### Recommended models by dataset size

**Small molecule datasets (< 1k molecules):**
- GIN (Graph Isomorphism Network)
- SchNet (when 3D structures are available)

**Medium datasets (1k–100k molecules):**
- GCN, GAT, or GIN
- NFP (Neural Fingerprint)
- MPNN (Message Passing Neural Network)

**Large datasets (> 100k molecules):**
- Fine-tunable pretrained models
- Self-supervised pretraining with InfoGraph or MultiviewContrast
- Deeper GIN architectures

**When 3D structures are available:**
- SchNet (continuous-filter convolutions)
- GearNet (geometry-aware relational graph)

## Feature Engineering

### Node Features

TorchDrug automatically extracts atom features:
- Atom type
- Formal charge
- Explicit/implicit hydrogens
- Hybridization
- Aromaticity
- Chirality

### Edge Features

Bond features include:
- Bond type (single, double, triple, aromatic)
- Stereochemistry
- Conjugation
- Whether the bond belongs to a ring

### Custom Features

Add custom node/edge features using transforms:
```python
from torchdrug import data, transforms

# Add custom transform
transform = transforms.VirtualNode()  # add virtual node
dataset = datasets.BBBP("~/molecule-datasets/",
                        transform=transform)
```

## Training Workflow

### Basic pipeline

1. **Load dataset**: choose a suitable dataset
2. **Split data**: use scaffold split for realistic drug discovery evaluation
3. **Define model**: choose a GNN architecture
4. **Create task**: configure loss and metrics
5. **Set optimizer**: Adam often works well
6. **Train**: use PyTorch Lightning or a custom loop

### Data splitting strategies

**Random Split**: standard train/validation/test split
**Scaffold Split**: group molecules by Bemis–Murcko scaffolds (recommended for drug discovery)
**Stratified Split**: preserve label distributions across splits

### Best practices

- Use scaffold split for realistic drug discovery evaluation
- Apply data augmentation (virtual nodes, virtual edges) for small datasets
- Monitor multiple metrics (AUROC/AUPRC for classification; MAE/RMSE for regression)
- Use early stopping based on validation performance
- Consider ensemble methods for critical applications
- Pretrain on large datasets before fine-tuning on small datasets

## FAQs and Troubleshooting

**Issue: poor performance on imbalanced datasets**
- Solution: use weighted loss, Focal Loss, or oversampling/undersampling.

**Issue: overfitting on small datasets**
- Solution: increase regularization, use simpler models, apply augmentation, or pretrain on larger datasets.

**Issue: high memory usage**
- Solution: reduce batch size, use gradient accumulation, or implement graph sampling.

**Issue: slow training**
- Solution: use GPU acceleration, optimize data loading with multiple workers, or use mixed precision training.
