Datasets Reference

Overview

TorchDrug provides 40+ curated datasets spanning chemistry, biology, and knowledge graphs. All datasets support lazy loading, automatic downloading, and customizable feature extraction.

Molecular Property Prediction Datasets

Drug Discovery Classification

| Dataset | Size | Task | Classes | Description |
|---------|------|------|---------|-------------|
| BACE | 1,513 | Binary | 2 | Beta-secretase inhibition related to Alzheimer's disease |
| BBBP | 2,039 | Binary | 2 | Blood-brain barrier permeability |
| HIV | 41,127 | Binary | 2 | Inhibiting HIV replication |
| ClinTox | 1,478 | Multi-label | 2 | Clinical trial toxicity |
| SIDER | 1,427 | Multi-label | 27 | Side effects by system/organ |
| Tox21 | 7,831 | Multi-label | 12 | Toxicity across 12 targets |
| ToxCast | 8,576 | Multi-label | 617 | High-throughput toxicology testing |
| MUV | 93,087 | Multi-label | 17 | Unbiased validation set for screening |

Key Features:
- Scaffold splits for realistic evaluation
- Binary metrics: AUROC, AUPRC
- Multi-label tasks support missing values

Applications:
- Drug safety prediction
- Virtual screening
- ADMET property prediction

Drug Discovery Regression

| Dataset | Size | Property | Units | Description |
|---------|------|----------|-------|-------------|
| ESOL | 1,128 | Solubility | logMol/L | Aqueous solubility |
| FreeSolv | 642 | Hydration energy | kcal/mol | Hydration free energy |
| Lipophilicity | 4,200 | LogD | - | Octanol/water partition |
| SAMPL | 643 | Solvation energy | kcal/mol | Solvation free energy |

Metrics: MAE, RMSE, R^2
Applications: ADME optimization, lead optimization

Quantum Chemistry

| Dataset | Size | Properties | Description |
|---------|------|------------|-------------|
| QM7 | 7,165 | 1 | Atomic energies |
| QM8 | 21,786 | 12 | Electronic spectra, excited states |
| QM9 | 133,885 | 12 | Geometry, energy, electronic, thermodynamic properties |
| PCQM4M | 3.8M | 1 | Large-scale HOMO-LUMO gap |

QM9 Properties include Dipole Moment, Isotropic Polarizability, HOMO/LUMO energies, internal energy, enthalpy, free energy, heat capacity, electronic spatial extent.
Applications: Quantum property prediction, method development, molecular pretraining

Large Molecule Databases

| Dataset | Size | Description | Use |
|---------|------|-------------|----|
| ZINC250k | 250k | Drug-like molecules | Generative model training |
| ZINC2M | 2M | Drug-like molecules | Large-scale pretraining |
| ChEMBL | ~1M | Bioactive molecules | Property prediction, molecular generation |

Protein Datasets

Function Prediction

| Dataset | Size | Task | Classes | Description |
|---------|------|------|---------|-------------|
| EnzymeCommission | 17,562 | Multiclass | 7 levels | EC enzyme classification |
| GeneOntology | 46,796 | Multilabel | 489 | GO term prediction (BP/MF/CC) |
| BetaLactamase | 5,864 | Regression | - | Enzyme activity levels |
| Fluorescence | 54,025 | Regression | - | GFP fluorescence |
| Stability | 53,614 | Regression | - | Thermostability (ΔΔG) |

Characteristics:
- Supports sequence and/or structure inputs
- Provides evolutionary information
- Includes multiple train/test splits

Applications:
- Protein engineering
- Functional annotation
- Enzyme design

Localization and Solubility

| Dataset | Size | Task | Classes | Description |
|---------|------|------|---------|-------------|
| Solubility | 62,478 | Binary | 2 | Protein solubility |
| BinaryLocalization | 22,168 | Binary | 2 | Membrane vs soluble |
| SubcellularLocalization | 8,943 | Multiclass | 10 | Subcellular localization |

Structure Prediction

| Dataset | Size | Task | Description |
|---------|------|------|-------------|
| Fold | 16,712 | Multiclass (1195) | Structure fold recognition |
| SecondaryStructure | 8,678 | Sequence labeling | 3 or 8 state secondary structure prediction |
| ProteinNet | variable | Contact prediction | Residue-residue contact map |

Protein Interactions

| Dataset | Size | Positives | Negatives | Description |
|---------|------|-----------|-----------|-------------|
| HumanPPI | 1,412 | 6,584 | - | Human protein interactions |
| YeastPPI | 2,018 | 6,451 | - | Yeast protein interactions |
| PPIAffinity | 2,156 pairs | - | - | Binding affinity values |

Biomolecule+Ligand Binding
| Dataset | Size | Type | Description |
|---------|------|------|-------------|
| BindingDB | ~1.5M | Affinity | Comprehensive binding data |
| PDBBind | 20,000+ | 3D complexes | Structure-based binding data |

Large Protein Databases
| Dataset | Size | Description |
|---------|------|-------------|
| AlphaFoldDB | 200M+ predicted structures |
| UniProt | Integrated sequence & annotations |

Knowledge Graph Datasets
General Knowledge
| Dataset | Entities | Relations | Triples | Domain |
|---------|---------|-----------|---------|------|
| FB15k | 14,951 | 1,345 | 592,213 | Freebase (general) |
| FB15k-237 | 14,541 | 237 | 310,116 | Filtered Freebase |
| WN18 | 40,943 | 18 | 151,442 | WordNet |
| WN18RR | 40,943 | 11 | 93,003 | Filtered WordNet |

Biomedical Knowledge
| Dataset | Entities | Relations | Triples | Description |
|---------|---------|-----------|---------|-------------|
| Hetionet | 45,158 | 24 | 2,250,197 | Integrated from 29 public biomedical databases |

Knowledge Graph Completion
- Link prediction with head/tail prediction tasks and multi-hop reasoning.

Datasets Usage Patterns

Loading Datasets
- Example snippets for BBBP, EnzymeCommission, FB15k237 are shown in the TorchDrug docs.

Data Splitting
- Random splits
- Scaffold splits (for chemistry)
- Predefined splits when datasets provide them

Feature Extraction
- Node features: atom type, charge, valence, aromaticity, chirality
- Edge features: bond type, distance, conjugation, ring status
- Protein features: amino acid type, physico-chemical properties, secondary structure
- Edge types: sequential, spatial, contact

Choosing Datasets
- By Task: molecular properties, protein, knowledge graphs, retrosynthesis
- By Size: small, medium, large
- By Domain: drug discovery, quantum chemistry, protein engineering, structural biology, biomedical

Best Practices
- Start small, use scaffold splits for chemistry tasks
- Use balanced metrics for imbalanced data (AUROC, AUPRC)
- Report multiple random seeds
- Be mindful of data leakage with pretraining
- Incorporate domain knowledge in preprocessing
