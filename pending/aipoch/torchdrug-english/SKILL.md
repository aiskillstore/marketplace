---
name: torchdrug-english
description: PyTorch-native Graph Neural Network framework for molecules and proteins. Suitable for building custom GNN architectures for drug discovery, protein modeling, or knowledge graph reasoning. Best for custom model development, protein property prediction, and retrosynthesis. If you need pretrained models and diverse feature extractors, use deepchem; if you need benchmark datasets, use pytdc.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# TorchDrug

## When to Use

- Use this skill when you need pytorch-native graph neural network framework for molecules and proteins. suitable for building custom gnn architectures for drug discovery, protein modeling, or knowledge graph reasoning. best for custom model development, protein property prediction, and retrosynthesis. if you need pretrained models and diverse feature extractors, use deepchem; if you need benchmark datasets, use pytdc in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `the documented workflow in this package` is the most direct path to complete the request.
- Use this skill when you need the `TorchDrug (English)` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: PyTorch-native Graph Neural Network framework for molecules and proteins. Suitable for building custom GNN architectures for drug discovery, protein modeling, or knowledge graph reasoning. Best for custom model development, protein property prediction, and retrosynthesis. If you need pretrained models and diverse feature extractors, use deepchem; if you need benchmark datasets, use pytdc.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Data Analytics/TorchDrug-English
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

See `## Overview` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Overview

TorchDrug is a PyTorch-based comprehensive machine learning toolbox designed for drug discovery and molecular science. It applies graph neural networks, pretrained models, and task definitions to molecules, proteins, and biological knowledge graphs, covering molecular property prediction, protein modeling, knowledge graph reasoning, molecular generation, retrosynthesis planning, and more, including 40+ curated datasets and 20+ model architectures.

## When to Use This Skill

Use this skill when dealing with the following:

**Data Types:**
- SMILES strings or molecular structures
- Protein sequences or 3D structures (PDB files)
- Reactions and retrosynthesis
- Biomedical knowledge graphs
- Drug discovery datasets

**Tasks:**
- Predict molecular properties (solubility, toxicity, activity)
- Protein function or structure prediction
- Drug-target binding prediction
- Generate new molecular structures
- Plan chemical synthesis routes
- Link prediction in biomedical knowledge bases
- Train graph neural networks on scientific data

**Libraries and Integration:**
- TorchDrug as core library
- Often with RDKit for cheminformatics
- PyTorch and PyTorch Lightning compatibility
- Integrated AlphaFold and ESM for proteins

## Getting Started

### Installation

```bash
pip install torchdrug
```

- Or install full version with optional dependencies

```bash
pip install torchdrug[full]
```

### Quick Example

```python
from torchdrug import datasets, models, tasks
from torch.utils.data import DataLoader
import torch

# Load molecular dataset
dataset = datasets.BBBP("~/molecule-datasets/")
train_set, valid_set, test_set = dataset.split()

# Define GNN model
model = models.GIN(
    input_dim=dataset.node_feature_dim,
    hidden_dims=[256, 256, 256],
    edge_input_dim=dataset.edge_feature_dim,
    batch_norm=True,
    readout="mean"
)

# Create property prediction task
task = tasks.PropertyPrediction(
    model,
    task=dataset.tasks,
    criterion="bce",
    metric=["auroc", "auprc"]
)

# Train with PyTorch
optimizer = torch.optim.Adam(task.parameters(), lr=1e-3)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)

for epoch in range(100):
    for batch in train_loader:
        loss = task(batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

## Core Capabilities

### 1. Molecular Property Prediction

Predict chemical, physical, and biological properties from molecular structures.

**Use Cases:**
- Drug-likeness and ADMET properties
- Toxicity screening
- Quantum chemical properties
- Binding affinity prediction

**Core Components:**
- 20+ molecular datasets (BBBP, HIV, Tox21, QM9, etc.)
- GNN models (GIN, GAT, SchNet)
- `PropertyPrediction` and `MultipleBinaryClassification` tasks

**Reference:** See molecular_property_prediction.md

### 2. Protein Modeling

Process protein sequences, structures, and properties.

**Use Cases:**
- Enzyme function prediction
- Protein stability and solubility
- Subcellular localization
- Protein-protein interactions
- Structure prediction

**Core Components:**
- 15+ protein datasets (EnzymeCommission, GeneOntology, PDBBind, etc.)
- Sequence models (ESM, ProteinBERT, ProteinLSTM)
- Structure models (GearNet, SchNet)
- Multiple task types for different prediction levels

**Reference:** See protein_modeling.md

### 3. Knowledge Graph Reasoning

Predict missing links and relations in biomedical knowledge graphs.

**Use Cases:**
- Drug repurposing
- Disease mechanism discovery
- Gene-disease associations
- Multi-hop biomedical reasoning

**Core Components:**
- General KGs (FB15k, WN18) and biomedical KGs (Hetionet)
- Embedding models (TransE, RotatE, ComplEx)
- `KnowledgeGraphCompletion` task

**Reference:** See knowledge_graphs.md

### 4. Molecular Generation

Generate novel molecular structures with desired properties.

**Use Cases:**
- De novo drug design
- Lead compound optimization
- Chemical space exploration
- Property-directed generation

**Core Components:**
- Autoregressive generation
- GCPN (policy-based generation)
- `GraphAutoregressiveFlow`
- Property optimization workflows

**Reference:** See molecular_generation.md

### 5. Retrosynthesis

Predict synthesis routes from target molecules to starting materials.

**Use Cases:**
- Synthesis planning
- Route optimization
- Synthesizability assessment
- Multi-step planning

**Core Components:**
- USPTO-50k reaction dataset
- `CenterIdentification` (reaction center prediction)
- `SynthonCompletion` (reactant prediction)
- End-to-end retrosynthesis pipeline

**Reference:** See retrosynthesis.md

### 6. Graph Neural Network Models

Comprehensive catalog of GNN architectures for different data types and tasks.

**Available Models:**
- General GNN: GCN, GAT, GIN, RGCN, MPNN
- 3D-aware: SchNet, GearNet
- Protein-specific: ESM, ProteinBERT, GearNet
- Knowledge graphs: TransE, RotatE, ComplEx, SimplE
- Generative: GraphAutoregressiveFlow

**Reference:** See models_architectures.md

### 7. Datasets

40+ curated datasets covering chemistry, biology, and knowledge graphs.

**Categories:**
- Molecular properties (drug discovery, quantum chemistry)
- Protein properties (function, structure, interactions)
- Knowledge graphs (general and biomedical)
- Retrosynthesis reactions

**Reference:** See datasets.md

## Common Workflows

### Workflow 1: Molecular Property Prediction

Scenario: Predict blood-brain barrier permeability for drug candidates.
Steps:
- Load dataset: datasets.BBBP()
- Choose model: GNN for molecular graphs (e.g., GIN)
- Define task: PropertyPrediction with binary classification
- Train using scaffold split for realistic evaluation
- Evaluate with AUROC and AUPRC

Navigation: references/molecular_property_prediction.md → Dataset Selection → Model Selection → Training

### Workflow 2: Protein Function Prediction

Scenario: Predict enzyme function from sequence.
Steps:
- Load dataset: datasets.EnzymeCommission()
- Choose model: pretrained ESM or GearNet with structure
- Define task: PropertyPrediction with multi-class classification
- Finetune pretrained model or train from scratch
- Evaluate with accuracy and per-class metrics

Navigation: references/protein_modeling.md → Model Selection (Sequence vs Structure) → Pretraining Strategies

### Workflow 3: Drug Repurposing via Knowledge Graph

Scenario: Find new disease treatments in Hetionet.
Steps:
- Load dataset: datasets.Hetionet()
- Choose model: RotatE or ComplEx
- Define task: KnowledgeGraphCompletion
- Train with negative sampling
- Query predictions for compound-treats-disease
- Filter by plausibility and mechanism

Navigation: references/knowledge_graphs.md → Hetionet Dataset → Model Selection → Biomedical Applications
