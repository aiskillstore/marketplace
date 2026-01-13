# Efficient Page Loading Guide

Load documentation efficiently without wasting tokens.

## Token Costs by File Type

| File Type | Typical Size | When to Load |
|-----------|--------------|--------------|
| `_index.toon` (category) | 100-150 tokens | Freely - navigation aid |
| `_index.toon` (library) | 150-250 tokens | Freely - navigation aid |
| `_index.toon` (section) | 100-200 tokens | Freely - navigation aid |
| `pages/*.toon` | 250-450 tokens | When you need the content |
| `full-context.md` | 5,000-15,000 tokens | **Sparingly** - last resort |

## Loading Strategies

### Single Feature (~600 tokens)

```
# Load just what you need
@ai-docs/libraries/baml/_index.toon        # 200 tokens
@ai-docs/libraries/baml/guide/pages/error-handling.toon  # 400 tokens
```

### Multi-Page Feature (~1,200 tokens)

```
# Load related pages
@ai-docs/libraries/baml/guide/pages/error-handling.toon
@ai-docs/libraries/baml/guide/pages/timeouts.toon
@ai-docs/libraries/baml/reference/pages/retry-policy.toon
```

### Multi-Library (~2,000-4,000 tokens)

```
# Load from multiple libraries
@ai-docs/libraries/baml/_index.toon
@ai-docs/libraries/baml/guide/pages/types.toon
@ai-docs/libraries/mcp/_index.toon
@ai-docs/libraries/mcp/guide/pages/tool-servers.toon
```

## When to Use full-context.md

**Appropriate:**
- Major library migrations
- Writing comprehensive tutorials
- Initial deep learning of new library
- Architecture reviews

**Inappropriate (use targeted loading):**
- Simple syntax questions
- Single feature implementation
- Bug fixes
- Quick lookups

## Cost Comparison

```
Answering "What's the retry syntax in BAML?"

Option A: full-context.md
- Tokens: ~15,000
- Time: Slow (large read)
- Waste: ~14,500 tokens

Option B: Targeted loading
- error-handling.toon: ~400 tokens
- Time: Fast
- Waste: ~0 tokens

Winner: Option B (37x more efficient)
```

## Anti-Patterns

| Bad | Good | Savings |
|-----|------|---------|
| Load full-context.md for simple question | Load specific page | ~14,000 tokens |
| Load all library indexes | Load only relevant library | ~500 tokens |
| Re-navigate in sub-agents | Pre-load and pass context | Avoids duplication |
| Guess at paths | Navigate through indexes | Avoids failed reads |
