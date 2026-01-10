---
name: data-substrate-analysis
description: Analyze fundamental data primitives, type systems, and state management patterns in a codebase. Use when (1) evaluating typing strategies (Pydantic vs TypedDict vs loose dicts), (2) assessing immutability and mutation patterns, (3) understanding serialization approaches, (4) documenting state shape and lifecycle, or (5) comparing data modeling approaches across frameworks.
---

# Data Substrate Analysis

Analyzes the fundamental units of data and state management patterns.

## Process

1. **Locate type files** — Find types.py, schema.py, models.py, state.py
2. **Classify typing** — Strict (Pydantic), structural (TypedDict), loose (dict)
3. **Analyze mutation** — In-place modification vs. copy-on-write
4. **Document serialization** — json(), dict(), pickle, custom methods

## Typing Strategy Classification

### Detection Patterns

| Strategy | Indicators | Files to Check |
|----------|-----------|----------------|
| **Pydantic** | `BaseModel`, `Field()`, `validator` | models.py, schema.py |
| **Dataclass** | `@dataclass`, `field()` | types.py, models.py |
| **TypedDict** | `TypedDict`, `Required[]`, `NotRequired[]` | types.py |
| **NamedTuple** | `NamedTuple`, `typing.NamedTuple` | types.py |
| **Loose** | `Dict[str, Any]`, plain `dict` | Throughout |

### Analysis Questions

- Are boundaries validated (API ingress/egress)?
- Is nesting depth reasonable (<3 levels)?
- Are optional fields explicit or implicit None?
- Version migration path (Pydantic V1 → V2)?

## Immutability Analysis

### Mutable Patterns (Risk Indicators)

```python
# In-place list modification
state.messages.append(msg)
state.history.extend(new_items)

# Direct dict mutation
state['key'] = value
state.update(new_data)

# Object attribute mutation
state.status = 'complete'
```

### Immutable Patterns (Safer)

```python
# Pydantic copy
new_state = state.model_copy(update={'key': value})

# Dataclass replace
new_state = replace(state, messages=[*state.messages, msg])

# Spread operator style
new_state = {**state, 'key': value}

# Frozen dataclass
@dataclass(frozen=True)
class State: ...
```

## Serialization Strategy

### Common Patterns

| Method | Code Pattern | Trade-offs |
|--------|-------------|------------|
| Pydantic JSON | `.model_dump_json()` | Type-safe, automatic |
| Pydantic Dict | `.model_dump()` | For internal use |
| Dataclass | `asdict(obj)` | Manual, no validation |
| Custom | `to_dict()`, `from_dict()` | Full control |
| Pickle | `pickle.dumps()` | Fast, fragile, security risk |
| JSON | `json.dumps(obj, default=...)` | Requires encoder |

### Questions to Answer

- Is serialization implicit (automatic) or explicit (manual)?
- How are nested objects handled?
- Is deserialization validated?
- What happens with unknown fields?

## Output Template

```markdown
## Data Substrate Analysis: [Framework Name]

### Typing Strategy
- **Primary Approach**: [Pydantic/Dataclass/TypedDict/Loose]
- **Key Files**: [List of files]
- **Nesting Depth**: [Shallow/Medium/Deep]
- **Validation**: [At boundaries/Everywhere/None]

### Core Primitives

| Type | Location | Purpose | Mutability |
|------|----------|---------|------------|
| Message | schema.py:L15 | Chat message | Immutable |
| State | state.py:L42 | Agent state | Mutable ⚠️ |
| Result | types.py:L78 | Tool output | Immutable |

### Mutation Analysis
- **Pattern**: [In-place/Copy-on-write/Mixed]
- **Risk Areas**: [List of mutable state locations]
- **Concurrency Safe**: [Yes/No/Partial]

### Serialization
- **Method**: [Pydantic/Custom/JSON]
- **Implicit/Explicit**: [Description]
- **Round-trip Tested**: [Yes/No/Unknown]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify type files
- **Feeds into**: `comparative-matrix` for typing decisions
- **Related**: `resilience-analysis` for error handling in serialization
