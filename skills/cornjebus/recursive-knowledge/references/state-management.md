# State Management and Termination Logic

This document explains the core innovation that prevents the infinite verification loop problem seen in naive recursive approaches.

## The Problem with RLM

In the RLM paper's approach:
1. Model finds an answer
2. Model has no signal that answer is "good enough"
3. Model keeps verifying, re-checking, re-exploring
4. Earlier correct answer gets buried in context
5. Model eventually picks wrong answer or runs forever

**Root cause**: No state management for the reasoning process itself.

## Our Solution: Stateful Traversal

### State Tracking

Every query execution maintains:

```python
@dataclass
class TraversalState:
    # What we've explored (prevents re-exploration)
    visited_nodes: set[str]    # Entity IDs
    visited_edges: set[str]    # Relationship IDs
    
    # What we've found (accumulates evidence)
    findings: list[Finding]
    
    # Confidence tracking (knows when to stop)
    confidence: float          # 0.0 to 1.0
    corroborating_sources: set[str]  # Document IDs
    
    # Depth tracking (prevents infinite depth)
    current_depth: int
    max_depth: int
```

### Termination Conditions

The `should_stop()` method checks multiple conditions:

```python
def should_stop(self) -> tuple[bool, str]:
    # Condition 1: High confidence
    if self.confidence >= 0.85:
        return True, "Confidence threshold met"
    
    # Condition 2: Sufficient corroboration
    if len(self.corroborating_sources) >= 3:
        return True, "Multiple sources agree"
    
    # Condition 3: Depth limit
    if self.current_depth >= self.max_depth:
        return True, "Maximum depth reached"
    
    return False, ""
```

### Confidence Calculation

Confidence updates as findings accumulate:

```python
def _update_confidence(self):
    # Factor 1: Average confidence of individual findings
    avg_finding_confidence = mean(f.confidence for f in self.findings)
    
    # Factor 2: Number of corroborating sources
    source_factor = min(1.0, len(sources) / required_sources)
    
    # Factor 3: Number of findings (diminishing returns)
    count_factor = min(1.0, len(self.findings) / 5)
    
    # Weighted combination
    self.confidence = (
        avg_finding_confidence * 0.4 +
        source_factor * 0.4 +
        count_factor * 0.2
    )
```

## Traversal Control Flow

```
START QUERY
    │
    ▼
Parse query → Find entry points
    │
    ▼
For each entry point:
    │
    ├──► Check should_stop() ──► YES ──► EXIT
    │           │
    │          NO
    │           │
    │           ▼
    ├──► Check already_visited(node) ──► YES ──► SKIP
    │           │
    │          NO
    │           │
    │           ▼
    ├──► Record visit
    │           │
    │           ▼
    ├──► Evaluate entity → Add finding
    │           │
    │           ▼
    ├──► Check should_stop() ──► YES ──► EXIT
    │           │
    │          NO
    │           │
    │           ▼
    └──► For each neighbor edge:
              │
              ├──► Check already_visited(edge) ──► YES ──► SKIP
              │           │
              │          NO
              │           │
              │           ▼
              ├──► Record visit, add finding
              │           │
              │           ▼
              ├──► Check should_stop() ──► YES ──► EXIT
              │           │
              │          NO
              │           │
              │           ▼
              └──► RECURSE to neighbor (depth + 1)
```

## Key Guarantees

1. **No node visited twice**: `visited_nodes` set prevents re-exploration
2. **No edge traversed twice**: `visited_edges` set prevents redundant paths
3. **Findings persist**: Each finding recorded with provenance
4. **Confidence monotonic**: Can only increase (no "unlearning")
5. **Bounded depth**: Hard limit prevents infinite recursion
6. **Early termination**: Stops as soon as criteria met

## Tunable Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `max_depth` | 5 | Higher = more exploration, higher cost |
| `confidence_threshold` | 0.85 | Higher = more certain but more exploration |
| `min_corroborating_sources` | 3 | Higher = more evidence required |

## Comparison to RLM

| Aspect | RLM | This Approach |
|--------|-----|---------------|
| Node revisit | Possible | Prevented |
| Edge revisit | Possible | Prevented |
| Termination | Hope model outputs FINAL() | Deterministic conditions |
| Confidence | None | Tracked and updated |
| Provenance | Lost in context | Preserved in findings |
| Cost control | Variable (can explode) | Bounded by state |
