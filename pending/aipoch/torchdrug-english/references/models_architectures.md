
# Models and Architectures

## Overview

TorchDrug provides a collection of ready-made model architectures for a variety of graph-based learning tasks. This reference documents all available models, their characteristics, typical use cases, and implementation details.

## Graph Neural Networks (GNN)

### GCN (Graph Convolutional Network)

**Type:** Spatial message passing  
**Paper:** Semi-Supervised Classification with Graph Convolutional Networks (Kipf & Welling, 2017)

**Highlights:**
- Simple and efficient aggregation
- Convolutions using a normalized adjacency matrix
- Performs well on homogeneous graphs
- Strong baseline for many tasks

**Suitable for:**
- Initial experiments and baselines
- When computational efficiency matters
- Graphs with clear local structure

**Parameters:**
- `input_dim`: node feature dimension
- `hidden_dims`: list of hidden dimensions
- `edge_input_dim`: edge feature dimension (optional)
- `batch_norm`: whether to apply batch normalization
- `activation`: activation function (relu, elu, etc.)
- `dropout`: dropout rate

**Use cases:**
- Molecular property prediction
- Citation network classification
- Social network analysis

### GAT (Graph Attention Network)

**Type:** Attention-based message passing  
**Paper:** Graph Attention Networks (Veličković et al., 2018)

**Highlights:**
- Learns attention weights for neighbors
- Assigns different importance to different neighbors
- Multi-head attention improves robustness
- Naturally handles varying node degrees

**Suitable for:**
- When neighbor importance varies
- Heterogeneous graphs
- Interpretable predictions

**Parameters:**
- `input_dim`, `hidden_dims`: standard dimensions
- `num_heads`: number of attention heads
- `negative_slope`: LeakyReLU slope
- `concat`: whether to concatenate or average multi-head outputs

**Use cases:**
- Protein-protein interaction prediction
- Molecular generation focused on reaction sites
- Knowledge graph reasoning with relation importance

### GIN (Graph Isomorphism Network)

**Type:** Highly expressive message passing  
**Paper:** How Powerful are Graph Neural Networks? (Xu et al., 2019)

**Highlights:**
- Theoretically one of the most expressive GNN architectures
- Injective aggregation functions
- Can distinguish graph structures that GCN cannot
- Often performs best on molecular tasks

**Suitable for:**
- Molecular property prediction (often SOTA)
- Tasks requiring structural discrimination
- Graph classification

**Parameters:**
- `input_dim`, `hidden_dims`: standard dimensions
- `edge_input_dim`: include edge features
- `batch_norm`: typically set to true
- `readout`: graph pooling (`sum`, `mean`, `max`)
- `eps`: learnable or fixed epsilon

**Use cases:**
- Drug property prediction (BBBP, HIV, etc.)
- Molecular generation
- Reaction prediction

### RGCN (Relational Graph Convolutional Network)

**Type:** Multi-relation message passing  
**Paper:** Modeling Relational Data with Graph Convolutional Networks (Schlichtkrull et al., 2018)

**Highlights:**
- Handles multiple edge/relation types
- Relation-specific weight matrices
- Basis decomposition for parameter efficiency
- Core model for knowledge graphs

**Suitable for:**
- Knowledge graph reasoning
- Heterogeneous molecular graphs
- Multi-relation data

**Parameters:**
- `num_relation`: number of relation types
- `hidden_dims`: hidden dimensions
- `num_bases`: basis decomposition (reduce params)

**Use cases:**
- Knowledge graph completion
- Retrosynthesis analysis (different bond types)
- Protein interaction networks

### MPNN (Message Passing Neural Network)

**Type:** General message passing framework  
**Paper:** Neural Message Passing for Quantum Chemistry (Gilmer et al., 2017)

**Highlights:**
- Flexible message and update functions
- Message computation can include edge features
- Uses GRU to update node hidden states
- Uses Set2Set for graph readout

**Suitable for:**
- Quantum chemistry prediction
- Tasks where edge information is important
- Scenarios requiring iterative node state evolution

**Parameters:**
- `input_dim`, `hidden_dim`: feature dimensions
- `edge_input_dim`: edge feature dimension
- `num_layer`: number of message passing iterations
- `num_mlp_layer`: number of MLP layers in the message function

**Use cases:**
- QM9 quantum property prediction
- Molecular dynamics
- 3D conformation-aware tasks

### SchNet (Continuous-filter Convolutional Network)

**Type:** 3D geometry-aware convolution  
**Paper:** SchNet: A continuous-filter convolutional neural network (Schütt et al., 2017)

**Highlights:**
- Operates on 3D atomic coordinates
- Continuous filter convolutions
- Rotational and translational invariance
- Excellent performance in quantum chemistry

**Suitable for:**
- 3D molecular structure tasks
- Quantum property prediction
- Protein structure analysis
- Energy and force prediction

**Parameters:**
- `input_dim`: atom features
- `hidden_dims`: hidden dimensions
- `num_gaussian`: number of RBF basis functions for distance
- `cutoff`: interaction cutoff distance

**Use cases:**
- QM9 property prediction
- Molecular dynamics simulations
- Structure-based protein–ligand binding
- Crystal property prediction

### ChebNet (Chebyshev Spectral Convolution)

**Type:** Spectral convolution  
**Paper:** Convolutional Neural Networks on Graphs (Defferrard et al., 2016)

**Highlights:**
- Spectral graph convolutions
- Chebyshev polynomial approximation
- Captures global graph structure
- Computationally efficient

**Suitable for:**
- Tasks requiring global information
- When the graph Laplacian contains useful signals
- Theoretical analyses

**Parameters:**
- `input_dim`, `hidden_dims`: dimensions
- `num_cheb`: order of Chebyshev polynomials

**Use cases:**
- Citation network classification
- Brain network analysis
- Graph signal processing

### NFP (Neural Fingerprint)

**Type:** Learned molecular fingerprints  
**Paper:** Convolutional Networks on Graphs for Learning Molecular Fingerprints (Duvenaud et al., 2015)

**Highlights:**
- Learns differentiable molecular fingerprints
- Alternative to handcrafted fingerprints (ECFP)
- Iterative convolution similar to ECFP
- Learnable and interpretable features

**Suitable for:**
- Molecular similarity learning
- Property prediction with limited data
- When interpretability matters

**Parameters:**
- `input_dim`, `output_dim`: feature dims
- `hidden_dims`: hidden dimensions
- `num_layer`: depth of iterative convolutions

**Use cases:**
- Virtual screening
- Molecular similarity search
- QSAR modeling

## Protein-specific Models

### GearNet (Geometric-aware Relational Graph Network)

**Type:** Protein structure encoder  
**Paper:** Protein Representation Learning by Geometric Structure Pretraining (Zhang et al., 2023)

**Highlights:**
- Integrates 3D geometric information
- Multiple edge types (sequence, spatial, KNN)
- Designed specifically for proteins
- SOTA for many protein tasks

**Suitable for:**
- Protein structure prediction
- Protein function prediction
- Protein–protein interaction prediction
- Any task involving protein 3D structure

**Parameters:**
- `input_dim`: residue feature dimension
- `hidden_dims`: hidden dimensions
- `num_relation`: edge types (sequence, radius, KNN)
- `edge_input_dim`: geometric features (distances, angles)
- `batch_norm`: typically true

**Use cases:**
- Enzyme function prediction (EnzymeCommission)
- Fold recognition
- Contact prediction
- Binding site identification

### ESM (Evolutionary Scale Modeling)

**Type:** Protein language model (Transformer)  
**Paper:** Biological structure and function emerge from scaling unsupervised learning (Rives et al., 2021)

**Highlights:**
- Pretrained on over 250 million protein sequences
- Captures evolutionary and structural signals
- Transformer architecture
- Effective for transfer learning on downstream tasks

**Suitable for:**
- Any sequence-based protein task
- When no structural information is available
- Transfer learning with limited labeled data

**Variants:**
- ESM-1b: 650M parameters
- ESM-2: multiple sizes (8M to 15B parameters)

**Use cases:**
- Protein function prediction
- Variant effect prediction
- Protein design
- Structure prediction (ESMFold)

### ProteinBERT

**Type:** Masked protein language model

**Highlights:**
- BERT-style pretraining
- Masked amino acid prediction
- Bidirectional context
- Suitable for sequence-based tasks

**Use cases:**
- Functional annotation
- Subcellular localization
- Stability prediction

### ProteinCNN / ProteinResNet

**Type:** Sequence convolutional networks

**Highlights:**
- 1D convolutions over sequences
- Local pattern recognition
- Faster than Transformers
- Good for motif detection

**Use cases:**
- Binding site prediction
- Secondary structure prediction
- Domain recognition

### ProteinLSTM

**Type:** Sequence recurrent network

**Highlights:**
- Bidirectional LSTM
- Captures long-range dependencies
- Sequential processing
- Solid baseline for sequence tasks

**Use cases:**
- Order prediction
- Sequence annotation
- Protein time-series data

## Knowledge Graph Models

### TransE (Translational Embedding)

**Type:** Translation-based embeddings  
**Paper:** Translating Embeddings for Modeling Multi-relational Data (Bordes et al., 2013)

**Highlights:**
- h + r ≈ t (head + relation ≈ tail)
- Simple and interpretable
- Suited for one-to-one relations
- Memory efficient

**Suitable for:**
- Large-scale knowledge graphs
- Initial experiments
- Interpretable embeddings

**Parameters:**
- `num_entity`, `num_relation`: graph size
- `embedding_dim`: embedding dimension (typically 50–500)

### RotatE (Rotational Embedding)

**Type:** Rotation in complex space  
**Paper:** RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space (Sun et al., 2019)

**Highlights:**
- Models relations as rotations in complex space
- Handles symmetric, antisymmetric, inverse, and composite relations
- Achieves SOTA on several benchmarks

**Suitable for:**
- Most knowledge graph tasks
- Complex relation patterns
- When accuracy is critical

**Parameters:**
- `num_entity`, `num_relation`: graph size
- `embedding_dim`: must be even (complex embeddings)
- `max_score`: score clipping value

### DistMult

**Type:** Bilinear model

**Highlights:**
- Models symmetric relations
- Fast and efficient
- Cannot model antisymmetric relations

**Suitable for:**
- Symmetric relations (e.g., "similar to")
- When speed is critical
- Large graphs

### ComplEx

**Type:** Complex-valued embeddings

**Highlights:**
- Handles asymmetric and symmetric relations
- Often outperforms DistMult
- Good trade-off between expressiveness and efficiency

**Suitable for:**
- General knowledge graph completion
- Mixed relation types
- When RotatE is too complex

### SimplE

**Type:** Enhanced embedding model

**Highlights:**
- Each entity has two embeddings (forward + inverse)
- Fully expressive
- Slightly more parameters than ComplEx

**Suitable for:**
- When full expressiveness is required
- When inverse relations are important

## Generative Models

### GraphAutoregressiveFlow

**Type:** Molecular normalizing flow

**Highlights:**
- Exact likelihood computation
- Invertible transformations
- Stable training (non-adversarial)
- Supports conditional generation

**Suitable for:**
- Molecular generation
- Density estimation
- Molecular interpolation

**Parameters:**
- `input_dim`: atom features
- `hidden_dims`: coupling layers
- `num_flow`: number of flow transforms

**Use cases:**
- De novo drug design
- Chemical space exploration
- Property-guided generation

## Pretraining Models

### InfoGraph

**Type:** Contrastive learning

**Highlights:**
- Maximizes mutual information
- Node-level and graph-level contrast
- Unsupervised pretraining
- Works well for small datasets

**Use cases:**
- Pretraining molecular encoders
- Few-shot learning
- Transfer learning

### MultiviewContrast

**Type:** Multiview contrastive learning for proteins

**Highlights:**
- Contrasts different views of proteins
- Geometric pretraining
- Uses 3D structural information
- Strong performance on protein tasks

**Use cases:**
- Pretraining GearNet on protein structures
- Transfer to property prediction
- Scenarios with scarce labeled data

## Model Selection Guide

### By Task Type

**Molecular property prediction:**
1. GIN (preferred)
2. GAT (for interpretability)
3. SchNet (when 3D data is available)

**Protein tasks:**
1. ESM (sequence only)
2. GearNet (when structure is available)
3. ProteinBERT (sequence-based, lighter than ESM)

**Knowledge graphs:**
1. RotatE (best performance)
2. ComplEx (good balance)
3. TransE (large graphs, efficient)

**Molecular generation:**
1. GraphAutoregressiveFlow (exact likelihood)
2. GCPN variants built on GIN (property optimization)

**Retrosynthesis / retrosynthetic analysis:**
1. GIN (fragment completion)
2. RGCN (identify centers by bond types)

### By Dataset Size

**Small (< 1k):**
- Use pretrained models (ESM for proteins)
- Simple architectures (GCN, ProteinCNN)
- Strong regularization

**Medium (1k–100k):**
- GIN for molecules
- GAT for interpretability
- Standard training

**Large (> 100k):**
- Any model is feasible
- Deeper architectures
- Train from scratch if desired

### By Compute Budget

**Low:**
- GCN (simplest)
- DistMult (knowledge graphs)
- ProteinLSTM

**Medium:**
- GIN
- GAT
- ComplEx

**High:**
- ESM (large)
- SchNet (3D)
- High-dimensional RotatE

## Implementation Tips

1. **Start simple**: benchmark with GCN or GIN first.
2. **Use pretraining**: ESM for proteins, InfoGraph for molecules.
3. **Tune depth**: 3–5 layers is often sufficient.
4. **Batch Normalization**: usually helpful (except for some KG embeddings).
5. **Residual connections**: important for deep networks.
6. **Readout function**: `mean` often works well.
7. **Edge features**: include them when available (bond types, distances).
8. **Regularization**: use dropout, weight decay, and early stopping.

