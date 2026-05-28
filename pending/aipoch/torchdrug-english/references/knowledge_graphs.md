Knowledge Graphs

Overview

A knowledge graph (KG) represents structured information as entities and relations. TorchDrug provides comprehensive support for embedding-based models and neural reasoning for knowledge graph completion (link prediction).

Available Datasets

General Knowledge Graphs

**FB15k (Freebase subset):**
- 14,951 entities
- 1,345 relation types
- 592,213 triples
- General world knowledge from Freebase

**FB15k-237:**
- 14,541 entities
- 237 relation types
- 310,116 triples
- Filtered version without inverse relations; more challenging benchmark

**WN18 (WordNet):**
- 40,943 entities (synsets)
- 18 relation types
- 151,442 triples

**WN18RR:**
- 40,943 entities
- 11 relation types
- 93,003 triples
- Filtered version removing inverse patterns

Biomedical Knowledge Graphs

**Hetionet:**
- 45,158 entities (genes, compounds, diseases, pathways, etc.)
- 24 relation types
- 2,250,197 edges
- Integrated from 29 public biomedical databases
- Designed for drug repurposing and disease understanding

Knowledge Graph Reasoning
Task: KnowledgeGraphCompletion
- Link prediction: given (head, relation, ?), predict tail; or (head, ?, tail)
- Multi-hop reasoning often required in biomedical contexts

Embeddings and Models
- General KG embeddings: TransE, RotatE, DistMult, ComplEx, SimplE
- Neural logic models: NeuralLP, KBGAT, etc.

Training and Evaluation
- Negative sampling strategies (Uniform, Self-Adversarial, Type-Constrained)
- Losses: BCE, margin, logistic losses; filtered vs raw evaluation
- Metrics: MR, MRR, Hits@K

Common Applications
- Link prediction, relation extraction, KG completion
- Biomedical knowledge base reasoning and multi-hop inference

Integration with TorchDrug
- Use KG embeddings as components in multi-task learning with molecular/biological prediction tasks
- Combine KG reasoning with molecular generation or retrosynthesis planning

Notes
- This document provides a concise reference for knowledge graph reasoning within TorchDrug. For deeper coverage, see the related KG literature and the TorchDrug docs.
