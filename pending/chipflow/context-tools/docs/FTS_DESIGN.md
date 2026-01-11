# Full-Text Search (FTS) Design

## Goal
Enable fast, relevance-ranked searches across comments, docstrings, and string literals in the codebase.

## Use Cases
1. **Finding concepts in documentation**: Search "connection pooling" finds all related docstrings
2. **Finding error messages**: Search for specific error text across the codebase
3. **Finding TODOs/FIXMEs**: Aggregate all technical debt markers
4. **Documentation exploration**: Discover what functionality exists by reading comments

## Database Schema Extension

### New FTS5 Virtual Table

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS code_text_fts USING fts5(
    file_path UNINDEXED,     -- File location (not searchable, for display)
    line_number UNINDEXED,   -- Line number (not searchable, for display)
    element_type UNINDEXED,  -- 'comment', 'docstring', 'string_literal'
    symbol_name UNINDEXED,   -- Symbol name if docstring, NULL otherwise
    content,                 -- The searchable text content
    tokenize='unicode61 remove_diacritics 2'
);
```

**Why this schema:**
- `UNINDEXED` columns are stored but not searchable (metadata only)
- Only `content` is full-text searchable
- `tokenize='unicode61 remove_diacritics 2'` handles Unicode, removes accents, splits on punctuation

### Size Estimate

For a medium codebase (10K LOC):
- Symbols only: ~1-2MB
- Comments/docstrings: ~500KB-1MB (compressed in FTS5)
- String literals: ~200-500KB
- **Total with FTS: ~2-4MB** (2-3x increase)

## What Gets Indexed

### Python
- **Docstrings**: Triple-quoted strings after class/function definitions
- **Comments**: Lines starting with `#`
- **String literals**: `"..."` and `'...'` (excluding docstrings)

### Rust
- **Doc comments**: `///` and `//!`
- **Regular comments**: `//` and `/* ... */`
- **String literals**: `"..."` and raw strings `r"..."`

### C++
- **Doc comments**: `/**` and `///` (Doxygen-style)
- **Regular comments**: `//` and `/* ... */`
- **String literals**: `"..."` and raw strings `R"(...)"`

## New MCP Tool

### `search_text`

Search for text across comments, docstrings, and string literals.

**Parameters:**
```python
{
    "query": str,              # Search query (phrase, boolean, wildcards)
    "element_type": Optional[str],  # 'comment', 'docstring', 'string_literal', 'all'
    "limit": int = 20          # Maximum results
}
```

**Returns:**
```python
[
    {
        "file_path": "src/db/pool.py",
        "line_number": 42,
        "element_type": "docstring",
        "symbol_name": "ConnectionPool.__init__",
        "content": "Initialize connection pool with size and timeout...",
        "rank": 0.85  # Relevance score (0-1)
    },
    ...
]
```

**Query syntax:**
- Simple: `"connection pool"`
- Phrase: `"connection pooling optimization"`
- Boolean: `"database AND (timeout OR deadline)"`
- Wildcard: `"connect*"`

## Implementation Phases

### Phase 1: Schema & Infrastructure (v0.9.0-alpha)
- [ ] Add FTS5 table to database schema
- [ ] Migrate version bump (v4 → v5)
- [ ] Add text extraction utilities

### Phase 2: Python Support (v0.9.0-beta)
- [ ] Extract comments from Python AST
- [ ] Extract string literals from Python AST
- [ ] Index during repo-map generation
- [ ] Test on real codebases

### Phase 3: Rust/C++ Support (v0.9.0)
- [ ] Extract comments from Rust tree-sitter
- [ ] Extract comments from C++ tree-sitter
- [ ] Extract string literals from both
- [ ] Full testing and documentation

### Phase 4: MCP Tool (v0.9.0)
- [ ] Implement `search_text` MCP tool
- [ ] Add relevance ranking
- [ ] Add query syntax support
- [ ] Update SKILL.md and mcp-help

## Updated Workflow

**New decision tree:**
```
Am I searching for something in code?
├─ Searching for symbols (function/class/enum)?
│  └─ Use: search_symbols / get_symbol_content
│
├─ Searching for concepts/documentation?
│  └─ Use: search_text(element_type="comment") or search_text(element_type="docstring")
│
├─ Searching for error messages?
│  └─ Use: search_text(element_type="string_literal")
│
└─ Searching for arbitrary text patterns?
   └─ Use: Grep (for non-indexed files like markdown/JSON)
```

## Performance Expectations

**Search speed:**
- FTS5 queries: <50ms for most codebases
- Grep: 100-500ms depending on size
- **10-20x faster than grep for text searches**

**Indexing time:**
- Text extraction adds ~20-30% to indexing time
- Still completes in background, no user impact

## Open Questions

1. **String literal filtering**: Should we filter out very short strings (< 5 chars) to reduce noise?
2. **Comment filtering**: Should we filter out copyright headers, license blocks?
3. **Snippet length**: How much context to return with each match?
4. **Deduplication**: Should we dedupe identical strings that appear multiple times?

## Alternatives Considered

### Alternative 1: Use ripgrep for everything
- **Pros**: Already fast, no database bloat
- **Cons**: No relevance ranking, no cross-file aggregation, spawns processes

### Alternative 2: Index full file content
- **Pros**: Can search any text
- **Cons**: Database would be 100+ MB, duplicates all code

### Alternative 3: Don't implement FTS
- **Pros**: Keep it simple
- **Cons**: Miss opportunity for concept searches with relevance ranking

**Decision: Implement Option 3 (minimal FTS)** - Best balance of features vs complexity.
