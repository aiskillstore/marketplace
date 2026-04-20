# Method Family Library

Map the classified need to method families.

## Family A: Regularized statistical / tree baselines
Typical role: robust baseline for tabular omics or smaller cohorts.
Examples: elastic net, Cox/penalized Cox, random forest, gradient boosting.

## Family B: Pathway-guided interpretable neural models
Typical role: pathway-aware prediction, biologically structured hidden layers, interpretable omics modeling.
Examples: pathDNN-type architectures, PathHDNN-type hierarchical pathway models, pathway-prior sparse networks.

## Family C: Graph and knowledge-network models
Typical role: disease-gene ranking, drug-target prioritization, graph-aware response modeling.
Examples: GNNs, heterogeneous network learning, knowledge graph methods.

## Family D: Multi-omics latent representation models
Typical role: integration across omics layers and subtype or response modeling.
Examples: matrix factorization, variational autoencoder families, cross-modal integration methods.

## Family E: Cell-state / trajectory / spatial models
Typical role: single-cell, spatial transcriptomics, cell-state transition, deconvolution.

## Family F: Causal-inference-supporting analytical families
Typical role: strengthen causal interpretation when prediction-only approaches are insufficient.
Examples: MR, QTL integration, mediation, longitudinal causal models.

## Rule
Always include a family because it solves the project’s actual problem, not merely because it is recent.
