# Transcript Analytics with DuckDB - Implementation Plan

## Overview

Extend the existing transcript extraction tools with a DuckDB-based index for querying past Claude Code and Codex CLI sessions at scale.

## Schema Design (v2)

```sql
-- sessions table: file_path is the unique key (not session_id)
CREATE TABLE sessions (
    file_path TEXT PRIMARY KEY,      -- unique identifier (filename handles subagent collision)
    session_id TEXT,                 -- original session_id (for reference, not unique)
    source TEXT NOT NULL,            -- 'claude_code' | 'codex'
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    model TEXT,
    cwd TEXT,
    git_branch TEXT,
    git_repo TEXT,                   -- derived from cwd
    message_count INTEGER,
    tool_count INTEGER,
    file_mtime REAL,                 -- for incremental indexing
    file_size INTEGER,               -- for change detection
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL REFERENCES sessions(file_path),
    message_idx INTEGER NOT NULL,
    role TEXT NOT NULL,              -- 'user' | 'assistant'
    content TEXT,
    timestamp TIMESTAMP,
    has_thinking BOOLEAN DEFAULT FALSE,
    UNIQUE(file_path, message_idx)
);

-- tool_calls table (simplified - no success tracking)
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL REFERENCES sessions(file_path),
    message_idx INTEGER,            -- nullable: Codex function_call events lack message context
    tool_name TEXT NOT NULL
    -- NOTE: succeeded/input_summary removed - not derivable from current parsing
);

-- Full-text search index (DuckDB native)
-- DuckDB doesn't have fts5; use LIKE/ILIKE for simple search or:
-- Option 1: Use DuckDB's full-text search extension (duckdb_fts)
-- Option 2: Use PRAGMA create_fts_index (experimental)
-- For Phase 1, use simple ILIKE queries; add FTS extension in later phase
CREATE INDEX idx_messages_content ON messages(content);
```

### Design Decisions

1. **`file_path` as primary key**: The existing `extract_transcript.py` explicitly uses filename (not session_id) as the unique identifier because session_id can be shared across subagents (see line 130-131). This schema follows that pattern.

2. **No `tool_calls.succeeded`**: Current extractors only capture `tool_use` blocks. `tool_result` blocks are skipped in Codex parsing (line 86-87 of `extract_codex_transcript.py`) and not correlated in Claude parsing. Adding success tracking would require new extraction logic.

3. **No `messages.token_count`**: Current extractors don't capture usage/token data. Would require parsing additional fields from session JSONL.

4. **Session linking deferred**: No parent/subagent metadata exists in current session format. Tree construction would require heuristics or new metadata.

5. **`tool_calls.message_idx` nullable**: Claude Code tool_use blocks are nested in assistant messages (so message_idx is available), but Codex function_call events are standalone entries without message context (see `extract_codex_transcript.py:67-69`). Making this nullable allows both sources to populate the schema.

6. **FTS via ILIKE for Phase 1**: DuckDB doesn't support SQLite's fts5 syntax. Phase 1 uses simple `ILIKE` queries on an indexed column. The `duckdb_fts` extension can be added later for better performance.

---

## Incremental Indexing Strategy

Per-file tracking stored in DuckDB (no separate JSON file):

```python
def should_reindex(file_path: Path, db: DuckDB) -> bool:
    """Check if file needs reindexing."""
    current_mtime = file_path.stat().st_mtime
    current_size = file_path.stat().st_size
    
    result = db.execute("""
        SELECT file_mtime, file_size FROM sessions 
        WHERE file_path = ?
    """, [str(file_path)]).fetchone()
    
    if result is None:
        return True  # New file
    
    stored_mtime, stored_size = result
    return current_mtime != stored_mtime or current_size != stored_size

def reindex_file(file_path: Path, db: DuckDB):
    """Delete old data and reindex file."""
    db.execute("DELETE FROM tool_calls WHERE file_path = ?", [str(file_path)])
    db.execute("DELETE FROM messages WHERE file_path = ?", [str(file_path)])
    db.execute("DELETE FROM sessions WHERE file_path = ?", [str(file_path)])
    # ... parse and insert fresh data

def delete_session(file_path: str, db: DuckDB):
    """Remove all data for a session file."""
    db.execute("DELETE FROM tool_calls WHERE file_path = ?", [file_path])
    db.execute("DELETE FROM messages WHERE file_path = ?", [file_path])
    db.execute("DELETE FROM sessions WHERE file_path = ?", [file_path])

def cleanup_deleted_files(db: DuckDB):
    """Remove entries for files that no longer exist."""
    indexed_files = db.execute("SELECT file_path FROM sessions").fetchall()
    for (file_path,) in indexed_files:
        if not Path(file_path).exists():
            delete_session(file_path, db)  # Just delete, don't reindex
```

### Handles

| Scenario | Detection | Action |
|----------|-----------|--------|
| New file | Not in DB | Full index |
| Modified file | mtime or size changed | Delete + reindex |
| Deleted file | Path no longer exists | Delete from DB |
| Append-only growth | Size increased | Delete + reindex |

---

## CLI Commands

```bash
# Index/reindex sessions
transcript index                     # Incremental index of all sessions
transcript index --full              # Force full reindex
transcript index --path <dir>        # Index specific directory

# Search
transcript search "error handling"   # FTS across message content
transcript search "error" --cwd ~/myproject  # Filter by project

# List sessions  
transcript recent                    # Last 10 sessions
transcript recent --project myapp    # Filter by cwd containing "myapp"
transcript recent --since 7d         # Last 7 days

# Analytics
transcript tools                     # Top 10 tools by usage
transcript tools --top 20            # Top 20
transcript stats                     # Session counts, durations, model breakdown

# View session
transcript show <file_path>          # Full transcript
transcript show <file_path> --summary  # Summary only
```

---

## Directory Structure

```
~/.claude/transcript-index/
└── sessions.duckdb      # Single database file with all tables + FTS
```

---

## Implementation Phases

### Phase 1: Core indexing
- DuckDB schema creation
- Parse Claude Code JSONL → sessions/messages/tool_calls tables
- Incremental indexing with mtime/size tracking
- Basic CLI: `index`, `recent`, `search`

### Phase 2: Codex support
- Add Codex session parsing
- Unified schema handles both sources via `source` column

### Phase 3: Analytics
- `tools` command with aggregations
- `stats` command for usage patterns
- Time-series queries

### Phase 4: Future considerations
- Session linking heuristics (if metadata becomes available)
- Token counting (if extraction adds usage parsing)
- Semantic search via embeddings

---

## Out of Scope (with rationale)

| Feature | Reason | Reference |
|---------|--------|-----------|
| `tool_calls.succeeded` | Requires `tool_result` parsing not in current extractors | `extract_codex_transcript.py:86-87` |
| `messages.token_count` | Not captured by current extraction | `extract_transcript.py:108-125` |
| Parent/subagent linking | No metadata available in session format | `extract_transcript.py:93-100` |
| Real-time updates | Batch indexing only; run `transcript index` as needed | Design choice |
