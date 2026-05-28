Core Concepts and Technical Details

Overview

This reference covers TorchDrug's core architecture, design principles, and technical implementations.

Architectural Philosophy

Modular Design

TorchDrug separates concerns into distinct modules:

- Representation Models (models.py): encode graphs into embeddings
- Task Definitions (tasks.py): define learning objectives and evaluation metrics
- Data Handling (data.py, datasets.py): graph structures and datasets
- Core Components (core.py): base classes and utilities

Benefits:
- Reuse representations across tasks
- Flexible component composition
- Facilitates experimentation and prototyping
- Clear separation of concerns

Configurable System

All components derive from core.Configurable:
- Serialize to configuration dicts
- Rebuild from configuration
- Save and load entire pipelines for reproducibility
- Enable repeatable experiments

Core Components

core.Configurable

Base class for TorchDrug components.

Key Methods:
- config_dict(): serialize to dict
- load_config_dict(config): load from dict
- save(file): save to file
- load(file): load from file

Example:
```python
from torchdrug import core, models

model = models.GIN(input_dim=10, hidden_dims=[256, 256])

# Save configuration
config = model.config_dict()
# {'class': 'GIN', 'input_dim': 10, 'hidden_dims': [256, 256], ...}

# Rebuild model from config
model2 = core.Configurable.load_config_dict(config)
```

core.Registry

Decorators for registering models, tasks, and datasets.

Usage:
```python
from torchdrug import core as core_td

@core_td.register("models.CustomModel")
class CustomModel(nn.Module, core_td.Configurable):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, hidden_dim)

    def forward(self, graph, input, all_loss, metric):
        # model implementation
        pass
```

Benefits:
- Models can be automatically serialized
- Text-based model specification
- Easier model discovery and instantiation

Data Structures

Graph (core data structure)

Represents the core object for molecules or proteins.

Attributes:
- num_node: number of nodes
- num_edge: number of edges
- node_feature: tensor [num_node, feature_dim]
- edge_feature: tensor [num_edge, feature_dim]
- edge_list: edge connectivity [num_edge, 2 or 3]
- num_relation: number of relation types (for heterogeneous graphs)

Methods:
- node_mask(mask): subset of nodes
- edge_mask(mask): subset of edges
- undirected(): convert to undirected graph
- directed(): convert to directed graph

Batching:
- Pack multiple graphs into a single batched graph
- DataLoader handles batching, while preserving per-graph node/edge indices

Molecule (Graph subclass)

Specialized graph for molecules.

Additional Properties:
- atom_type, bond_type, formal_charge, explicit_hs

Methods:
- from_smiles(smiles)
- from_molecule(mol)
- to_smiles()
- to_molecule()
- ion_to_molecule(): neutralize charges

Example:
```python
from torchdrug import data

# Create from SMILES
mol = data.Molecule.from_smiles("CCO")

# Atom features
print(mol.atom_type)  # [6, 6, 8] (C, C, O)
print(mol.bond_type)  # [1, 1] (single bonds)
```

### Protein (Protein Graph)

Specialized graph for proteins.

Additional Properties:
- residue_type, atom_name, atom_type, residue_number, chain_id

Methods:
- from_pdb(pdb_file)
- from_sequence(sequence)
- to_pdb(pdb_file)

Graph Construction:
- Nodes typically represent residues
- Edges can be sequence-based, spatial (KNN), or contact-based
- Configurable edge construction strategies

Example:
```python
from torchdrug import data

# Load protein
protein = data.Protein.from_pdb("1a3x.pdb")

# Build a graph with multiple edge types
graph = protein.residue_graph(
    node_position="ca",  # use Cα positions
    edge_types=["sequential", "radius"]
)
```

PackedGraph

Efficient batching structure for heterogeneous graphs.

Purpose:
- Batch graphs of different sizes
- Allocate memory on a single GPU
- Efficient parallel processing

Attributes:
- num_nodes: list of node counts per graph
- num_edges: list of edge counts per graph
- graph_ind: graph index per node

Usage:
- Used by DataLoader for automatic batching
- Custom batching strategies
- Multi-graph operations

Model Interfaces

Forward Function Signature

All TorchDrug models follow a standard interface:
```python
def forward(self, graph, input, all_loss=None, metric=None):
    """
    Arguments:
        graph (Graph): batch of graphs
        input (Tensor): node input features
        all_loss (Tensor, optional): loss accumulator
        metric (dict, optional): metric dictionary

    Returns:
        dict: output with representation keys
    ```

Key Points:
- graph: batched graph structure
- input: node features [num_node, input_dim]
- all_loss: accumulated loss (for multi-task)
- metric: shared metrics dictionary
- Returns: dictionary with representation types

Necessary Attributes

All models must define:
- input_dim: expected input feature dimension
- output_dim: output representation dimension

Example:
```python
class CustomModel(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = hidden_dim
        # network layers...
```

Task Interface

Core Task Methods

All tasks should implement:
```python
class CustomTask(tasks.Task):
    def preprocess(self, train_set, valid_set, test_set):
        pass

    def predict(self, batch):
        graph, label = batch
        output = self.model(graph, graph.node_feature)
        pred = self.mlp(output["graph_feature"])
        return pred

    def target(self, batch):
        graph, label = batch
        return label

    def forward(self, batch):
        pred = self.predict(batch)
        target = self.target(batch)
        loss = self.criterion(pred, target)
        return loss

    def evaluate(self, pred, target):
        metrics = {}
        metrics["auroc"] = compute_auroc(pred, target)
        metrics["auprc"] = compute_auprc(pred, target)
        return metrics
```

Training Workflows and Best Practices
Standard training loop example and evaluation practices using PyTorch Lightning or pure PyTorch.
