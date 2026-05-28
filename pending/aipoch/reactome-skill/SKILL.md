---
name: reactome-skill
description: Query the Reactome REST API for pathway content and enrichment analyses; use when you need curated pathway data, reaction details, or overrepresentation results for a gene list.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a list of genes/proteins and want to run pathway overrepresentation (enrichment) analysis against Reactome.
- You need to retrieve curated pathway content (hierarchy, reactions, participants) by Reactome stable IDs (e.g., `R-HSA-69278`).
- You want to map expression values onto pathways to support pathway-level interpretation.
- You need to project pathways across species/organisms using Reactome’s species projection capabilities.
- You are building a systems biology workflow that requires programmatic access to Reactome via its REST API.

## Key Features

- **Pathway enrichment (overrepresentation)** for identifier lists.
- **Expression analysis** by mapping expression data to Reactome pathways.
- **Content retrieval** for pathways, reactions, and participating molecules.
- **Pathway hierarchy access** to navigate curated pathway structures.
- **Species projection** to map pathways across organisms.
- **API documentation reference**: see `references/api_reference.md`.

## Dependencies

- `python` (3.x)
- `requests` (latest compatible)
- `reactome2py` (latest compatible)

Install:

```bash
uv pip install reactome2py requests
```

## Example Usage

The following commands are runnable examples using the provided CLI script.

### 1) Query pathway content by Reactome ID

```bash
python scripts/reactome_tool.py query_content --id "R-HSA-69278"
```

### 2) Run overrepresentation analysis for a gene list

```bash
python scripts/reactome_tool.py analyze_identifiers --identifiers "TP53,BRCA1"
```

## Implementation Details

- **API access pattern**: The skill uses the Reactome REST API (via `reactome2py` and/or direct HTTP calls with `requests`) to fetch pathway content and submit analyses.
- **Identifier input**: Gene/protein identifiers are provided as a comma-separated string (e.g., `TP53,BRCA1`) and are submitted for overrepresentation analysis.
- **Stable IDs**: Content retrieval expects Reactome stable identifiers (commonly formatted like `R-HSA-xxxxx` for human pathways).
- **Outputs**: Results typically include pathway/reaction metadata and analysis outputs (e.g., enriched pathways with associated statistics), depending on the invoked action.
- **Reference**: Reactome developer documentation is available at https://reactome.org/dev and the local API notes at `references/api_reference.md`.