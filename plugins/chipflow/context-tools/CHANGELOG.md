# Changelog

All notable changes to the context-tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.13] - 2026-01-09

### Changed
- **Improved learnings reminder wording** - Changed from "discoveries" to "what you built/learned"
  - "Discoveries" implied finding existing things, not recording implementations
  - Now explicitly prompts for: features/APIs implemented, integration points, design decisions
  - Added concrete examples: "Python bindings, new modules"
  - Added urgency: "Without this, context compaction will forget what you just built!"

### Fixed
- **Learnings not being used** - Better wording should prompt Claude to actually update learnings.md

## [0.8.12] - 2026-01-09

### Changed
- **Simplified precompact hook** - Removed all regeneration logic for significant performance improvement
  - MCP server maintains repo map automatically (no need to regenerate)
  - Session-start hook handles manifest generation (no need to regenerate during compaction)
  - Precompact now only shows learnings.md reminder (instant)

### Fixed
- **Slow precompact performance** - Hook no longer blocks on expensive repo map or manifest regeneration

## [0.8.11] - 2026-01-09

### Changed
- **Mandatory first action directive**: Session start now instructs Claude to run a test MCP query immediately
  - Forces Claude to verify tools work by running `list_files` or `search_symbols` at session start
  - Establishes tool usage habit from the very first action
  - Proves (not just tells) that MCP tools work in the current project
- **Explicit tool naming**: Changed "grep/find/ls" to "Search/Grep/Glob/find/ls" to explicitly mention Search tool
- **Real-world examples**: Updated list_files example to show `*ring*` pattern matching actual user scenarios
- **Stronger directive language**: Enhanced messaging to make MCP-first approach more mandatory

### Fixed
- **Tool adoption issue**: Despite "guaranteed to work" messaging, Claude was still defaulting to Search/ls commands
  - New approach: Make Claude actually USE the tools at session start, not just read about them

## [0.8.10] - 2026-01-09

### Added
- **Test coverage for exact paths**: Added test cases for list_files with exact paths (no wildcards)
  - `test_exact_path()` - verifies exact file name matches (e.g., "device.py")
  - `test_nonexistent_exact_path()` - verifies nonexistent files return empty list correctly
  - Total test coverage: 6/6 tests passing

## [0.8.9] - 2026-01-09

### Changed
- **Clarified messaging**: Changed "MCP tools guaranteed to work" to "context-tools MCP guaranteed to work" to avoid ambiguity with other MCP servers

## [0.8.8] - 2026-01-09

### Added
- **Progressive indexing feedback** - No more hanging or uncertainty!
  - MCP server starts indexing proactively on startup if DB doesn't exist
  - Tools return progress info (percentage, estimated time) instead of errors during indexing
  - Session start shows real-time status: "✅ Ready" or "⏳ Indexing: 45% (1200/2700 files, ~2m)"
  - New `get_indexing_progress()` function provides detailed progress information

### Changed
- **Reduced auto-wait timeout**: 60s → 15s for better responsiveness
  - Tools wait max 15 seconds, then return progress instead of hanging
  - No more hour-long waits - get feedback within 15 seconds
- **Confident messaging**: Session start now says "✅ Repo map ready: X symbols indexed - MCP tools guaranteed to work!"
  - Addresses Claude's uncertainty about whether tools will work
  - Shows proof that index exists and is ready

### Fixed
- **Claude's behavioral concerns addressed**:
  - Habit: More directive messaging with confident "guaranteed to work" language
  - Uncertainty: Real-time status proof at session start
  - Perceived simplicity: Clear that MCP tools work just like find/ls but faster

## [0.8.7] - 2026-01-08

### Added
- **New MCP tool: list_files** - List all indexed files, filtered by glob pattern
  - Much faster than find/ls for discovering file structure
  - Queries pre-built index instead of filesystem traversal
  - Examples: `list_files("*.va")`, `list_files("*psp103*")`, `list_files("**/devices/*")`
- **Real-world example**: Added user's PSP103/BSIM4 model discovery scenario to mcp-help
- **Session start guidance**: Added file listing to MCP tools quick reference
- **Comprehensive tests**: Test suite validates list_files functionality

### Changed
- Session start now mentions "BEFORE using grep/find/ls" instead of just grep

## [0.8.6] - 2026-01-08

### Changed
- **More directive session start**: Changed from "available" to "ALWAYS try MCP tools BEFORE grep" with specific triggers
- **Decision tree in SKILL.md**: Visual flowchart asking "Am I searching for code symbols?" before using grep
- **Concrete examples**: Added bullet points showing enum/struct/class lookups and function patterns
- **Rust enum example**: Added real user case of finding `InstructionData` enum variants (Phi vs PhiNode)

### Fixed
- Claude was still defaulting to grep despite v0.8.5 improvements - now more explicit about when to use MCP tools

## [0.8.5] - 2026-01-08

### Added
- **New command**: `/context-tools:mcp-help` - Comprehensive guide showing when to use MCP tools vs grep with real-world examples
- **Enhanced session start**: More prominent message with emoji and reference to help command
- **SKILL.md examples**: Added real-world usage scenarios comparing inefficient grep patterns vs efficient MCP tool usage

### Changed
- Session start now says "🚀 Fast Symbol Search Available" and points to `/context-tools:mcp-help`
- Better discoverability of MCP tools when Claude explores codebases

## [0.8.4] - 2026-01-08

### Changed
- **Reduced context flooding**: Trimmed session start context from 17 lines to 1 concise line
- Now just reminds Claude that MCP tools are faster than Grep for symbol lookups
- Removed verbose tool listings and restart instructions that were overwhelming context

## [0.8.3] - 2026-01-08

### Changed
- **Session start context**: Embedded SKILL.md guidance directly in session-start.sh additionalContext
- Claude now receives dynamic directory support and restart requirement instructions at session start
- Alternative approach since plugin manifest doesn't support automatic context loading via skills field

## [0.8.2] - 2026-01-08

### Fixed
- **Plugin validation error**: Removed `skills` field from plugin.json - not supported in current plugin manifest format
- Plugin now loads correctly without validation errors

## [0.8.1] - 2026-01-08 [YANKED]

### Fixed
- **Attempted skill registration**: Added `skills` field to plugin.json (YANKED - caused validation errors)

## [0.8.0] - 2026-01-08

### Added
- **Multiprocess architecture**: MCP server spawns indexing subprocess instead of using threads
- **Resource limits**: 4GB memory (RLIMIT_AS) and 20 min CPU time (RLIMIT_CPU) for indexing subprocess
- **Dynamic directory support**: MCP tools automatically query current working directory, not session start directory
- **Rotating logs**: Comprehensive logging to `.claude/logs/repo-map-server.log` (1MB per file, 3 backups)
- **Exit status detection**: Logs specific resource limit violations (SIGXCPU, SIGSEGV, SIGKILL)
- **SKILL.md**: Usage instructions for Claude with session restart guidance
- **PROCESS-ARCHITECTURE.md**: Documents architecture evolution and design decisions
- **TESTING.md**: Comprehensive test documentation with 18 test cases

### Changed
- **Simplified database writes**: Removed tmp file + rename pattern, rely on SQLite WAL mode + transactions
- **Removed file locking**: SQLite's built-in locking is sufficient for concurrent access
- **Watchdog can kill subprocess**: Using SIGKILL on subprocess doesn't affect MCP server
- **MCP server stays responsive**: Even during indexing or hung processes
- **Better logging**: Tool calls, results, indexing events, and errors all logged

### Fixed
- **Multi-project support**: Can now switch between projects in one session without restart
- **Concurrent indexing**: Multiple MCP servers can safely coexist, SQLite handles coordination
- **Resource leak detection**: Logs when subprocess exceeds memory or CPU limits

## [0.7.1] - 2026-01-07

### Fixed
- **Critical data corruption fix**: Wrap all database writes in single BEGIN IMMEDIATE / COMMIT transaction
- **Race condition protection**: Safety check prevents hung processes from overwriting after watchdog intervention
- **Transaction safety**: Rollback on exception, all-or-nothing writes

### Changed
- `set_metadata()` no longer commits internally - caller must commit
- Database writes are atomic (single transaction for all changes)

## [0.7.0] - 2026-01-07

### Added
- **Indexing status tracking**: Metadata table tracks status (idle/indexing/completed/failed)
- **Auto-wait behavior**: Tools automatically wait up to 60s if indexing in progress
- **Watchdog**: Detects hung indexing (>10 min) and resets status to 'failed'
- **Periodic watchdog**: Runs every 60 seconds to detect stuck processes
- **New MCP tool**: `wait_for_index` to explicitly wait for indexing completion
- **Status reporting**: `repo_map_status` shows indexing progress and duration

### Changed
- Bumped CACHE_VERSION from 3 to 4 (metadata table added)
- Tools "just work" on first use - auto-wait for indexing to complete

## [0.6.1] - 2026-01-06

### Changed
- Simplified MCP server configuration in plugin.json

## [0.6.0] - 2026-01-06

### Added
- **MCP server architecture**: Moved from PreToolUse hook to persistent MCP server
- Single long-running process per Claude Code session
- Background thread for indexing (replaced nohup subprocess)

### Fixed
- **Memory leak**: Eliminated "hundreds of gigs" memory usage from multiple background processes
- No more subprocess accumulation from hook calls

### Removed
- PreToolUse hook (replaced by MCP server)
- nohup subprocess spawning

## [0.5.x and earlier]

Initial releases with PreToolUse hook architecture.

[0.8.0]: https://github.com/ChipFlow/claude-context-tools/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/ChipFlow/claude-context-tools/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/ChipFlow/claude-context-tools/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/ChipFlow/claude-context-tools/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/ChipFlow/claude-context-tools/releases/tag/v0.6.0
