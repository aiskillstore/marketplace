---
name: comparative-matrix
description: Generate structured comparisons and decision matrices across analyzed frameworks. Use when (1) comparing multiple frameworks or approaches side-by-side, (2) making architectural decisions between alternatives, (3) creating best-of-breed selection documentation, (4) synthesizing findings from multiple analysis skills into actionable decisions, or (5) producing recommendation reports for technical stakeholders.
---

# Comparative Matrix

Synthesizes analysis outputs into structured decision frameworks.

## Process

1. **Collect** analysis outputs from multiple frameworks
2. **Normalize** findings to comparable dimensions
3. **Generate** comparison matrix
4. **Apply** decision heuristics
5. **Document** recommendations with rationale

## Comparison Dimensions

### Core Dimensions (Always Include)

| Dimension | What to Compare | Decision Criteria |
|-----------|-----------------|-------------------|
| **Typing** | Strict (Pydantic) vs Loose (dicts) | Team preference, runtime safety needs |
| **Async** | Native async vs sync-with-wrappers | Scalability requirements |
| **State** | Immutable vs mutable | Concurrency safety, debugging |
| **Config** | Code-first vs config-first | Flexibility vs discoverability |
| **Extensibility** | Composition vs inheritance | Maintainability, learning curve |

### Domain-Specific Dimensions

| Dimension | When to Include |
|-----------|-----------------|
| **Reasoning Pattern** | Comparing agent frameworks |
| **Memory Strategy** | Long-running agents |
| **Multi-Agent** | Orchestration systems |
| **Observability** | Production deployments |
| **Tool Interface** | Custom tool development |

## Matrix Template

```markdown
## Best-of-Breed Matrix: [Analysis Title]

| Dimension | Framework A | Framework B | Framework C | **Recommendation** |
|:----------|:------------|:------------|:------------|:-------------------|
| **Typing** | Pydantic V1, deep nesting | TypedDict, flat | Loose dicts | *Pydantic V2, flat structures* |
| **Async** | Sync core, async wrapper | Native async | Mixed | *Native async required* |
| **State** | Mutable, in-place | Immutable copy | Hybrid | *Immutable preferred* |
| **Config** | YAML + Python | Pure Python | JSON | *Python for type safety* |
| **Extensibility** | Deep inheritance (6 layers) | Composition | Protocols | *Composition + Protocols* |

### Dimension Details

#### Typing
- **Framework A**: Uses Pydantic V1 with deeply nested models (Message → Content → Block → ...)
  - Pro: Full validation at boundaries
  - Con: Difficult to extend, version migration pain
- **Framework B**: TypedDict with flat structure
  - Pro: Simple, fast, IDE support
  - Con: No runtime validation
- **Recommendation**: Adopt Pydantic V2 with intentionally flat structures. Use TypedDict for internal types.

[Continue for each dimension...]
```

## Decision Heuristics

Apply these heuristics when recommendations aren't obvious:

### Scalability-First
```
IF high_concurrency_expected:
    PREFER native_async
    PREFER immutable_state
    PREFER stateless_tools
```

### DX-First (Developer Experience)
```
IF team_is_small OR rapid_iteration:
    PREFER simple_inheritance_over_protocols
    PREFER code_first_config
    PREFER explicit_over_magic
```

### Production-First
```
IF mission_critical:
    PREFER strict_typing
    PREFER comprehensive_observability
    PREFER explicit_error_boundaries
```

## Output Artifacts

1. **Summary Matrix** - Single-page comparison table
2. **Detailed Analysis** - Per-dimension breakdown with evidence
3. **Recommendation Document** - Actionable decisions with rationale
4. **Trade-off Log** - Documented compromises and their justification

## Example Output Structure

```
comparative-analysis/
├── matrix.md              # Summary comparison table
├── dimensions/
│   ├── typing.md          # Detailed typing analysis
│   ├── async.md           # Concurrency model analysis
│   └── ...
├── recommendations.md     # Final decisions
└── tradeoffs.md          # Documented compromises
```

## Integration

- **Inputs from**: All Phase 1 & 2 analysis skills
- **Outputs to**: `antipattern-catalog`, `architecture-synthesis`
