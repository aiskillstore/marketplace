# Process Architecture

## Tree-Sitter Process Structure

**Key Finding:** Tree-sitter is **NOT** a subprocess - it's a native C extension that runs **in-process**.

```
┌─────────────────────────────────────────────────────────────┐
│  Python Process (PID: 12345)                                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Python Interpreter                                     │ │
│  │                                                        │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │ generate-repo-map.py                             │ │ │
│  │  │                                                  │ │ │
│  │  │  • find_python_files()                          │ │ │
│  │  │  • for file in files:                           │ │ │
│  │  │      extract_symbols_from_python(file) ────┐    │ │ │
│  │  │                                            │    │ │ │
│  │  └────────────────────────────────────────────┼────┘ │ │
│  │                                               │      │ │
│  │  ┌────────────────────────────────────────────▼────┐ │ │
│  │  │ tree_sitter._binding.cpython-313-darwin.so    │ │ │
│  │  │ (Native C Extension - SAME PROCESS)           │ │ │
│  │  │                                               │ │ │
│  │  │  • parser.parse(source_bytes)                │ │ │
│  │  │  • Native C code executing                   │ │ │
│  │  │  • Returns Tree object to Python             │ │ │
│  │  └───────────────────────────────────────────────┘ │ │
│  │                                                      │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  Memory Space: All shared                                   │
│  Threads: 1 (MainThread only)                               │
│  Child Processes: 0                                          │
└─────────────────────────────────────────────────────────────┘
```

## What This Means for Hung Processes

### Scenario: Tree-sitter Parser Hangs

If `parser.parse()` hangs (e.g., infinite loop in C code):

```
1. Python calls parser.parse(source)
2. Control transfers to native C code
3. C code enters infinite loop
4. Python thread BLOCKED waiting for C to return
5. ENTIRE PROCESS frozen (not just a subprocess)
```

**Effect of SIGSTOP:**
- Freezes the ENTIRE Python process
- Freezes tree-sitter C code execution
- Freezes Python interpreter
- No child processes to kill separately

**Effect of SIGKILL:**
- Kills the ENTIRE Python process
- Kills tree-sitter C code execution
- Process terminates immediately
- SQLite transaction rolled back (WAL ensures safety)

### Why Our Watchdog Works

**Without Watchdog:**
```
Time 0:   Process starts indexing (status='indexing')
Time 5m:  tree_sitter hangs in C code
Time ∞:   Process frozen forever, status stuck at 'indexing'
          Database locked, no way to recover
```

**With Watchdog (v0.7.0+):**
```
Time 0:    Process starts indexing (status='indexing')
Time 5m:   tree_sitter hangs in C code
Time 15m:  Watchdog (separate process) checks timestamp
           Detects hung process (>10 min)
           Sets status='failed' with error message
Time 15m+: Hung process CANNOT overwrite (safety check)
           Database accessible to other processes
           Can trigger new indexing
```

## Process Tree During Indexing

### Single-Threaded Execution
```bash
$ ps -ef | grep generate-repo-map
501 12345     1  0 13:00 ??  0:05.23 python3 generate-repo-map.py

$ ps -M -p 12345  # Show threads
USER   PID  TT  %CPU STAT PRI     STIME     UTIME COMMAND
501  12345 ??   1.2 S    31T   0:00.01   0:05.23 python3
```

**Only 1 thread** (MainThread) - No worker threads, no child processes.

### Memory Map (Loaded Libraries)
```
/usr/bin/python3                                    (interpreter)
.venv/.../tree_sitter/_binding.cpython-313.so       (tree-sitter core)
.venv/.../tree_sitter_cpp/_binding.abi3.so          (C++ grammar)
.venv/.../tree_sitter_rust/_binding.abi3.so         (Rust grammar)
/usr/lib/libsqlite3.dylib                           (SQLite)
```

All loaded into **same address space** - no IPC, no subprocess spawning.

## Implications for Testing

### What We Tested:

✅ **SIGSTOP to freeze entire process**
- Simulates tree-sitter hanging in C code
- Process becomes unresponsive
- Watchdog can detect and mark as failed

✅ **SIGCONT to resume frozen process**
- Process continues after watchdog intervention
- Safety check prevents overwriting database
- Hung process cannot corrupt data

✅ **Process completing after watchdog**
- Most critical test
- Proves safety check works
- Database protected from race condition

### What We Did NOT Need to Test:

❌ Killing child processes (none exist)
❌ IPC between processes (everything in-process)
❌ Thread synchronization (single-threaded)
❌ Subprocess cleanup (no subprocesses)

## Architecture Evolution

### v0.5.x: PreToolUse Hook (Deprecated)
```
┌─────────────────────────────────────────────┐
│ Claude Code Process                          │
│  └─ PreToolUse hook                         │
│      └─ nohup generate-repo-map.py &        │  ← SUBPROCESS!
│          └─ python3 (PID: 12346)            │
│              └─ tree_sitter (in-process)    │
└─────────────────────────────────────────────┘

Problem: Multiple background processes accumulate
Memory leak: Each subprocess loads tree-sitter (~500MB)
```

### v0.6.0 - v0.7.x: Thread-Based Indexing (Deprecated)
```
┌─────────────────────────────────────────────┐
│ MCP Server Process (repo-map-server.py)     │
│  └─ Background thread calls do_index()     │
│      └─ tree_sitter (in-process)           │
└─────────────────────────────────────────────┘

Solution: Single persistent process
Memory: One tree-sitter instance
Problem: Hung tree-sitter freezes entire MCP server
Watchdog: Can detect but can't kill without killing MCP
```

### v0.8.0+: Multiprocess Architecture (Current)
```
┌─────────────────────────────────────────────┐
│ MCP Server Process (repo-map-server.py)     │
│  └─ Spawns subprocess via do_index()       │
│      └─ tracks _indexing_process: Popen    │
│      └─ watchdog can SIGKILL subprocess    │
│                                              │
│  Subprocess (PID: 12347)                    │
│  ┌──────────────────────────────────────┐  │
│  │ generate-repo-map.py                 │  │
│  │  └─ tree_sitter (in-process)        │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘

Solution: Clean process isolation
MCP server: Always responsive
Watchdog: Can kill subprocess without affecting MCP
SQLite WAL: Handles concurrent read/write safely
```

## Key Architectural Decisions

1. **Tree-sitter is in-process** (native C extension)
   - Consequence: Hung parser = hung entire indexing subprocess
   - Mitigation: MCP server spawns subprocess, watchdog can SIGKILL it (v0.8.0+)

2. **Single-threaded parsing** (no ThreadPoolExecutor for tree-sitter)
   - Consequence: Sequential parsing, slower
   - Benefit: Simpler, no GIL contention, deterministic

3. **WAL mode + single transaction** (v0.7.1)
   - Consequence: Crash during parse = old data intact
   - Benefit: No partial state, safe to kill process

4. **Safety check before atomic rename** (v0.7.1)
   - Consequence: Hung process can complete but can't overwrite
   - Benefit: Watchdog decision is final

5. **Multiprocess architecture** (v0.8.0+)
   - Consequence: MCP server always responsive, even if indexing hangs
   - Benefit: Watchdog can kill hung subprocess without affecting MCP server
   - SQLite WAL: Handles concurrent read (MCP) and write (subprocess) safely

## Testing Recommendations

When testing hung processes:
- Use **SIGSTOP** to freeze (simulates C code hang)
- Use **SIGCONT** to resume (test safety check)
- Use **SIGKILL** to terminate (test WAL recovery)
- **Don't** look for child processes (none exist)
- **Don't** try to kill tree-sitter separately (in-process)

## Summary

Tree-sitter process "tree":
```
generate-repo-map.py
 └─ (no child processes)
 └─ (no threads)
 └─ (just native C library loaded in-process)
```

It's a **flat single-process architecture**, not a process tree.
