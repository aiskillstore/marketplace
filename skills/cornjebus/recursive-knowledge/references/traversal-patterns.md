# Traversal Patterns for Multi-Hop Reasoning

## Pattern 1: Single Entry Point Expansion

**Use when**: Query mentions one entity, needs related information.

**Example**: "What projects did John Smith work on?"

```
Entry: John Smith
    │
    ├──► works_on ──► Project A
    ├──► works_on ──► Project B
    └──► created ──► Project C

Findings: [Project A, Project B, Project C]
```

## Pattern 2: Multi-Entry Point Intersection

**Use when**: Query requires connecting multiple entities.

**Example**: "Who worked with John Smith on Project Alpha?"

```
Entry 1: John Smith          Entry 2: Project Alpha
    │                              │
    ├──► works_with ──► Alice      ├──► has_member ──► Alice ◄── INTERSECTION
    ├──► works_with ──► Bob        ├──► has_member ──► Carol
    └──► works_with ──► Carol      └──► has_member ──► John Smith

Finding: Alice (appears in both paths)
```

## Pattern 3: Chain Traversal

**Use when**: Query implies sequential relationships.

**Example**: "Who is the CEO of the company that made CrimeMiner?"

```
Entry: CrimeMiner
    │
    └──► created_by ──► Chuqlab
                           │
                           └──► has_ceo ──► Cornelius

Path: CrimeMiner → Chuqlab → Cornelius
```

## Pattern 4: Attribute Filter

**Use when**: Query specifies constraints.

**Example**: "What events in 2024 involved Anthropic?"

```
Entry: Anthropic
    │
    ├──► participated_in ──► Event A (date: 2023) ──► FILTER OUT
    ├──► participated_in ──► Event B (date: 2024) ──► INCLUDE
    └──► hosted ──► Event C (date: 2024) ──► INCLUDE

Findings: [Event B, Event C]
```

## Pattern 5: Contradiction Detection

**Use when**: Need to identify conflicting information.

**Example**: "Are there conflicting claims about X?"

```
Entry: Claim X
    │
    ├──► supported_by ──► Source A
    ├──► supported_by ──► Source B
    └──► contradicted_by ──► Source C ◄── FLAG

Finding: Sources A, B support; Source C contradicts
```

## Pattern 6: Hub Discovery

**Use when**: Finding central/important entities.

```
Count incoming edges for each entity type:
    │
    ├──► Person with most connections = key player
    ├──► Concept with most references = central topic
    └──► Document with most citations = authoritative source
```

## Implementation Notes

### Entry Point Selection

```python
def select_entry_points(query, graph):
    # 1. Extract entities mentioned in query
    mentioned = extract_entities_from_query(query)
    
    # 2. Find matches in graph
    matches = [find_entity(name, graph) for name in mentioned]
    
    # 3. If no direct matches, find semantically similar
    if not matches:
        matches = semantic_search(query, graph.entities)
    
    return matches
```

### Path Scoring

When multiple paths exist, score by:

1. **Confidence**: Product of edge confidences along path
2. **Length**: Shorter paths often more relevant
3. **Source count**: More corroborating sources = higher score

```python
def score_path(path, findings):
    confidence = product(f.confidence for f in findings)
    length_penalty = 1.0 / len(path)
    source_bonus = len(unique_sources(findings)) * 0.1
    
    return confidence * length_penalty + source_bonus
```

### Handling Cycles

The state management prevents infinite cycles:

```python
# Before traversing to neighbor:
if state.already_visited_node(neighbor.id):
    continue  # Skip - already explored

# This guarantees termination even in cyclic graphs
```

## Query Type → Pattern Mapping

| Query Type | Pattern | Example |
|------------|---------|---------|
| "What does X do?" | Single expansion | Expand from X |
| "Who connects X and Y?" | Intersection | Find common neighbors |
| "How does X relate to Y?" | Chain | Find path between |
| "What X in time period?" | Attribute filter | Filter by date |
| "Is X consistent?" | Contradiction | Check support/contradict edges |
| "What's most important?" | Hub discovery | Count connections |
