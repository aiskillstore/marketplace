---
name: recursive-knowledge
description: "Process large document corpora (1000+ docs, millions of tokens) through knowledge graph construction and stateful multi-hop reasoning. Use when (1) User provides a large corpus exceeding context limits, (2) Questions require connections across multiple documents, (3) Multi-hop reasoning needed for complex queries, (4) User wants persistent queryable knowledge from documents. Replaces brute-force document stuffing with intelligent graph traversal."
---

# Recursive Knowledge Processing

Process arbitrarily large document sets through knowledge graph construction and stateful multi-hop queries. Based on RLM research but with proper state management and termination logic.

## Core Concept

Instead of stuffing documents into context (which causes degradation), this skill:
1. Indexes documents into a knowledge graph (entities, relationships)
2. Answers queries by traversing the graph
3. Tracks state to avoid redundant exploration
4. Uses confidence thresholds to know when to stop

## Workflow

### Phase 1: Indexing

For a new corpus, run the indexer:

```python
python3 scripts/index_corpus.py --input /path/to/documents --output /path/to/graph.json
```

This extracts:
- **Entities**: People, organizations, concepts, dates, locations
- **Relationships**: References, mentions, contradicts, supports, relates_to
- **Metadata**: Source document, position, extraction confidence

For details on entity/relationship schema, see [references/graph-schema.md](references/graph-schema.md).

### Phase 2: Querying

For user queries against an indexed corpus:

```python
python3 scripts/query.py --graph /path/to/graph.json --query "user question here"
```

The query engine:
1. Parses query into target entities/relationships
2. Finds entry points in graph
3. Traverses with state tracking
4. Stops when confidence threshold met
5. Returns answer with provenance

### Phase 3: Incremental Updates

Add new documents to existing graph:

```python
python3 scripts/index_corpus.py --input /path/to/new_docs --output /path/to/graph.json --append
```

## State Management (Critical)

The key improvement over naive recursive approaches is **stateful traversal**. See [references/state-management.md](references/state-management.md) for full details.

**During query execution, track:**

| State | Purpose |
|-------|---------|
| `visited_nodes` | Prevent re-exploring same entities |
| `visited_edges` | Prevent re-traversing same relationships |
| `findings` | Accumulated evidence with sources |
| `confidence` | Current certainty level (0-1) |
| `depth` | Current traversal depth |

**Termination conditions:**

```python
STOP if:
  - confidence >= 0.85 (high certainty)
  - len(corroborating_sources) >= 3 (multiple agreement)
  - depth > max_depth (prevent infinite exploration)
  - all relevant paths exhausted
```

## Multi-Hop Reasoning

For questions requiring connection across documents:

1. Identify query components (what entities/facts needed)
2. Find entry points for each component
3. Traverse from each entry point
4. Look for path intersections
5. Synthesize findings at intersection points

Example: "Who worked with X on project Y?"
- Entry point 1: Entity "X" → relationships → projects
- Entry point 2: Entity "Project Y" → relationships → people
- Intersection: People connected to both X and Project Y

See [references/traversal-patterns.md](references/traversal-patterns.md) for patterns.

## When NOT to Use This Skill

- Small document sets that fit in context (<50k tokens) - just use direct context
- Simple keyword search - use grep/search tools instead
- No multi-hop reasoning needed - simpler approaches work
- Real-time streaming data - this is for static corpora

## File Reference

- `scripts/index_corpus.py` - Build graph from documents
- `scripts/query.py` - Execute queries with state management
- `scripts/graph_ops.py` - Graph CRUD utilities
- `references/graph-schema.md` - Entity and relationship types
- `references/state-management.md` - Termination and confidence logic
- `references/traversal-patterns.md` - Multi-hop query patterns
