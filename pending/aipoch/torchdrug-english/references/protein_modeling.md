Protein Modeling

Overview

TorchDrug provides broad support for protein-related tasks, including sequence analysis, structure prediction, property prediction, and protein-protein interactions. Proteins are represented as graphs, where nodes are amino acid residues and edges encode spatial or sequence relationships.

Available Datasets

Protein Function Prediction

Enzyme Function:
- Enzyme Commission (EC) numbers for 17,562 proteins: EC number classification (7 levels)
- BetaLactamase (5,864 sequences): enzyme activity prediction

Protein Characteristics:
- Fluorescence (54,025 sequences): GFP fluorescence intensity
- Stability (53,614 sequences): thermal stability prediction
- Solubility (62,478 sequences): protein solubility classification
- BinaryLocalization (22,168 proteins): membrane vs soluble proteins
- SubcellularLocalization (8,943 proteins): 10-class localization prediction

Gene Ontology:
- GeneOntology (46,796 proteins): GO term prediction across biological processes, molecular functions, and cellular components

Protein Structure Prediction

- Fold (16,712 proteins): structural fold classification (1,195 classes)
- SecondaryStructure (8,678 proteins): 3-state or 8-state secondary structure prediction
- ContactPrediction via ProteinNet: residue-residue contact graph

Protein Interactions

Protein-Protein Interactions:
- HumanPPI (1,412 proteins): human protein interaction network
- YeastPPI (2,018 proteins): yeast protein interaction network
- PPIAffinity (2,156 pairs): binding affinity measurements

Protein-Ligand Binding:
- BindingDB (~1.5M entries): comprehensive binding affinity data
- PDBBind (20,000+ complexes): structure-based binding data
  - Refined set: high-quality crystal structures
  - Core set: diverse benchmark

Large Protein Databases:
- AlphaFoldDB: predictions for over 200 million proteins
- ProteinNet: standard dataset for structure prediction

Task Types

NodePropertyPrediction

Predict residue-level properties such as secondary structure or contact maps.

Use Cases:
- Secondary structure prediction
- Residue-level disorder prediction
- Post-translational modification sites
- Binding site prediction

PropertyPrediction

Predict protein-level properties such as function, stability, or localization.

Use Cases:
- Enzyme function classification
- Subcellular localization
- Protein stability prediction
- GO term prediction

InteractionPrediction

Predict interactions between proteins or protein-ligand pairs.

Key Features:
- Supports sequence and structure inputs
- Symmetric (PPI) and non-symmetric interactions
- Various negative sampling strategies

ContactPrediction

Dedicated task to predict residue-residue contact distances in folded structures.

Applications:
- Predicting structures from sequence
- Protein folding pathway analysis
- Structure validation

Protein Representation Models

Sequence-Based Models

ESM (Evolutionary Scale Modeling):
- Transformer model pretrained on 250M+ sequences
- State-of-the-art for pure sequence tasks
- Available in multiple scales (ESM-1b, ESM-2)
- Encodes evolutionary and structural information

ProteinBERT
- BERT-style masked language model
- Pretrained on UniProt sequences
- Suitable for transfer learning

ProteinLSTM
- Bi-directional LSTM for sequence encoding
- Lightweight and fast
- Strong baseline for sequence tasks

ProteinCNN / ProteinResNet
- Convolutional architectures
- Captures local sequence patterns
- Faster than transformers in some settings

Structure-Based Models

GearNet (Geometry-Aware Relational Graph Network)
- Geometry-aware protein graph encoder
- Edge types: sequence, radius, KN-based
- Backbone/full-atom representations

GCN / GAT / GIN for protein graphs
- Standard GNNs adapted for proteins
- Flexible edge definitions

SchNet
- Continuous-filter convolution
- Works with 3D coordinates
- Suitable for structure-aware predictions

Feature-Based Models

Statistical features:
- Amino acid composition
- Sequence length statistics
- Motif counts

Physicochemical Features:
- Hydrophobicity scales
- Charge properties
- Secondary structure propensity
- Molecular weight and pI

Protein Graph Construction

Edge Types
- Sequential edges: connect adjacent residues
- Spatial edges: 3D space neighbors
- Contact edges: based on heavy-atom distances

Node Features
- Residue Identity: one-hot encoding of 20 amino acids
- Learned embeddings
- Position information: 3D coordinates (CA, N, C, O); backbone angles
...
