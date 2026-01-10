# TODO: Future Enhancements

## ✅ COMPLETED: Multiprocess Architecture (v0.8.0)

**Status**: ✅ COMPLETED in v0.8.0

**Motivation**: The v0.7.x thread-based architecture had a critical limitation - hung tree-sitter parsing would freeze the entire MCP server process. Multiprocess architecture solves this by spawning a separate subprocess for indexing.

**Benefits**:
- **MCP server always responsive**: Even if indexing hangs, the MCP server remains operational
- **Watchdog can kill hung processes**: Using SIGKILL on the subprocess doesn't affect MCP server
- **Clean process isolation**: Each indexing run is independent
- **SQLite WAL handles concurrent access**: Database can be read while indexing subprocess writes

**Implementation**:
- Changed `_is_indexing` boolean to `_indexing_process: subprocess.Popen | None`
- Modified `do_index()` to spawn subprocess: `uv run scripts/generate-repo-map.py`
- Updated `check_indexing_watchdog()` to kill hung subprocess with SIGKILL
- All status checks now use `_indexing_process.poll()` to detect running process

**Testing**:
- Verified subprocess spawning works correctly
- Database metadata correctly tracks status
- Watchdog can kill hung subprocess without affecting MCP server

**Resource Limits** (v0.8.0):
- Added `setrlimit` on Unix/macOS to catch runaway resource usage
- Memory limit: 4GB virtual address space (catches pathological allocation issues)
- CPU time limit: 20 minutes (catches infinite loops in parsing)
- Automatic detection and logging:
  - SIGXCPU: CPU time limit exceeded
  - SIGSEGV: Possible memory limit exceeded
  - SIGKILL: Process was killed by watchdog
- Checked on startup and every 60 seconds
- Normal indexing unaffected by generous limits

---

## ✅ COMPLETED: Indexing Status and Wait Support (v0.7.0 - v0.7.1)

**Status**: ✅ COMPLETED in v0.7.0 and v0.7.1

**Problem**: (SOLVED)
- ~~MCP tools may be called before indexing completes~~
- ~~Returns incomplete/empty results on first use~~
- ~~No way to check if indexing is done or wait for completion~~

**Solution**: ✅ Implemented metadata table to track indexing status

### Schema Addition

```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Status values: 'idle' | 'indexing' | 'completed' | 'failed'
-- Other keys: last_indexed, symbol_count, file_count, index_start_time, error_message
```

### Implementation Tasks ✅ ALL COMPLETED

1. ✅ **generate-repo-map.py**: Updated status in metadata table (v0.7.0)
   - ✅ Set `status='indexing'` at start
   - ✅ Set `status='completed'` on success
   - ✅ Set `status='failed'` on error with error_message
   - ✅ Single transaction for all writes (v0.7.1 - prevents data corruption)

2. ✅ **MCP Server - Enhanced status tool** (v0.7.0):
   - ✅ Return metadata from database
   - ✅ Show indexing progress
   - ✅ Calculate indexing duration
   - ✅ Detect stale/hung indexing

3. ✅ **MCP Server - Auto-wait behavior** (v0.7.0):
   - ✅ Check status before processing tool calls
   - ✅ If `status='indexing'`, poll until complete (60s timeout)
   - ✅ Return helpful error if timeout
   - ✅ Trigger indexing if DB doesn't exist

4. ✅ **New MCP tool**: `wait_for_index(timeout_seconds=60)` (v0.7.0)
   - ✅ Explicitly wait for indexing to complete
   - ✅ Return progress updates
   - ✅ Configurable timeout

### Benefits Achieved ✅
- ✅ Tools "just work" even on first use
- ✅ Users don't get confusing empty results
- ✅ Can show progress during long indexing
- ✅ Can detect and recover from hung indexing
- ✅ Database protected from corruption (v0.7.1)

### Watchdog for Recovery ✅ IMPLEMENTED (v0.7.0)

**Problem**: (SOLVED) ~~Indexing can crash/hang leaving status stuck at 'indexing'~~

**Solution**: Add watchdog logic in MCP server

```python
def check_indexing_watchdog():
    """Check if indexing is stuck and reset if needed."""
    if not DB_PATH.exists():
        return

    try:
        conn = get_db()
        cursor = conn.execute("SELECT value FROM metadata WHERE key = ?", ["status"])
        row = cursor.fetchone()

        if row and row[0] == "indexing":
            # Check how long it's been indexing
            cursor = conn.execute("SELECT value FROM metadata WHERE key = ?", ["index_start_time"])
            start_row = cursor.fetchone()

            if start_row:
                start_time = datetime.fromisoformat(start_row[0])
                elapsed = (datetime.now() - start_time).total_seconds()

                # If indexing for > 10 minutes, assume it crashed
                if elapsed > 600:
                    logger.warning(f"Indexing stuck for {elapsed}s, resetting status")
                    conn.execute("UPDATE metadata SET value = ? WHERE key = ?", ["failed", "status"])
                    conn.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                                ["error_message", f"Indexing hung/crashed after {elapsed}s"])
                    conn.commit()

        conn.close()
    except Exception as e:
        logger.error(f"Watchdog check failed: {e}")

# Run watchdog on server startup
async def main():
    check_indexing_watchdog()  # Check for stuck indexing

    # Start periodic staleness checker
    asyncio.create_task(periodic_staleness_check())
    asyncio.create_task(periodic_watchdog_check())  # New: periodic watchdog

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

async def periodic_watchdog_check():
    """Run watchdog every 60 seconds to detect hung indexing."""
    while True:
        await asyncio.sleep(60)
        try:
            check_indexing_watchdog()
        except Exception as e:
            logger.warning(f"Watchdog check failed: {e}")
```

**Watchdog Features:**
- Runs on MCP server startup
- Runs periodically (every 60 seconds)
- Detects indexing stuck > 10 minutes
- Resets status to 'failed' with error message
- Allows recovery by triggering new index

**Edge Cases Handled:**
1. **Crash during indexing**: Watchdog detects and resets
2. **Multiple concurrent indexing**: Lock in do_index() prevents this
3. **Partial index left behind**: Status='failed' triggers fresh reindex
4. **Zombie processes**: Session start hook already kills them

### Migration
- Bump CACHE_VERSION to 4
- Create metadata table if not exists
- Set initial status based on symbol count
- Run watchdog on first load to detect any stuck state

---

## String Literals and Comments Indexing

**Status**: Planned for future release

**Goal**: Extend repo-map indexing to capture string literals and comments, making it a comprehensive search tool that eliminates most Grep usage.

### Use Cases

**String Literals:**
- Find error messages: `search_strings("connection failed")`
- Find API endpoints: `search_strings("/api/users")`
- Find log messages: `search_strings("Starting server")`
- Find config keys: `search_strings("DATABASE_URL")`

**Comments:**
- Find TODOs: `search_comments(tags="TODO")`
- Find FIXMEs: `search_comments(tags="FIXME")`
- Find architecture notes: `search_comments("design pattern")`
- Find explanatory comments: `search_comments("this function")`

### Schema Extensions

```sql
-- New: String literals table
CREATE TABLE string_literals (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- The literal value
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    context TEXT,               -- Function/class containing this literal
    kind TEXT                   -- single, double, triple, f-string, raw, etc.
);

-- New: Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    content TEXT NOT NULL,      -- Comment text (without # or // or /* */)
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    kind TEXT,                  -- line, block, docstring
    tags TEXT                   -- TODO, FIXME, NOTE, BUG, HACK, XXX, etc.
);

-- Indexes for fast searching
CREATE INDEX idx_string_content ON string_literals(content);
CREATE INDEX idx_string_file ON string_literals(file_path);
CREATE INDEX idx_comment_content ON comments(content);
CREATE INDEX idx_comment_file ON comments(file_path);
CREATE INDEX idx_comment_tags ON comments(tags);
```

### New MCP Tools

- `search_strings(pattern, file?)` - Find string literals matching pattern
- `search_comments(pattern?, tags?, file?)` - Find comments, optionally filtered by tags
- `get_todos()` - Shorthand for `search_comments(tags="TODO")`
- `get_fixmes()` - Shorthand for `search_comments(tags="FIXME")`

### Implementation Tasks

1. **Python Support** (Easiest - use AST):
   - Extract `ast.Constant` nodes with string values
   - Extract comment nodes (use `tokenize` module)
   - Detect comment tags (TODO, FIXME, etc.) with regex

2. **C++ Support** (tree-sitter):
   - Extend tree-sitter query for `string_literal` nodes
   - Extract `comment` nodes from parse tree
   - Handle different comment styles: `//`, `/**/`, docstrings

3. **Rust Support** (tree-sitter):
   - Extract `string_literal` and `raw_string_literal` nodes
   - Extract `line_comment` and `block_comment` nodes
   - Handle doc comments `///` and `//!`

4. **MCP Server Updates**:
   - Add `search_strings` tool
   - Add `search_comments` tool
   - Add convenience tools (`get_todos`, `get_fixmes`)

5. **Database Migration**:
   - Bump `CACHE_VERSION` to trigger reindex
   - Create new tables with proper indexes
   - Update `write_symbols_to_sqlite` to handle new tables

### Considerations

**Performance:**
- Database size will increase (many more entries)
- Consider limiting string literal length (exclude very long strings)
- Consider excluding common/boring strings ("", " ", etc.)

**Memory:**
- Current single-threaded indexing should handle this fine
- Might need to batch writes to SQLite for large projects

**Configuration:**
- Add option to disable string/comment indexing (for very large repos)
- Add option to configure which comment tags to index

### Breaking Changes

- Requires database schema change (CACHE_VERSION bump)
- Users will need to wait for full reindex on first use
- Old repo-map.db files won't be compatible

### Benefits

- **Eliminates ~80% of Grep usage** for code searches
- Find error messages without reading whole codebase
- Track TODOs/FIXMEs systematically
- Fast API endpoint discovery
- Understand logging patterns across project

### Estimated Effort

- Python implementation: 4-6 hours
- C++/Rust implementation: 6-8 hours
- MCP tools: 2-3 hours
- Testing: 3-4 hours
- **Total: ~20 hours**

---

## Other Future Ideas

### Multi-Repository Support
Track symbols across multiple related repositories (monorepo support).

### Symbol References
Track where symbols are used, not just where they're defined (call graph).

### Import/Include Tracking
Index all imports/includes to understand dependencies.

### Type Information
Enhanced type tracking beyond just signatures (full type hierarchies).

### AI-Powered Similar Code Detection
Use embeddings to find semantically similar code beyond just name matching.
