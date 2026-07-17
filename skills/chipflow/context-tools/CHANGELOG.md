# Changelog

All notable changes to the context-tools plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.16.0] - 2026-03-05

### Added
- **`save_session_context` MCP tool** - Claude can now save session insights (foci, learnings, dragons, narrative updates, open/resolved questions) directly to narrative.md and learnings.md before context compaction
- **Direct context preservation** - PreCompact hook now instructs Claude to call `save_session_context` instead of spawning a background `claude -p` process, eliminating orphan process issues and 30-90s latency
- **Concurrent write safety** - Lockfile with PID-based stale detection prevents corruption when multiple sessions write to the same narrative/learnings files
- **Git-based update trigger** - After saving, drops `.update-narrative-trigger` file; MCP server picks it up on next tool call and spawns `update-context.sh` in background (owned by MCP server, not hook process group)

### Changed
- PreCompact hook no longer spawns `update-context.sh` directly — context saving is immediate via MCP tool

## [0.15.6] - 2026-03-05

### Fixed
- **Auto-continue after plan completion** - Strengthened behavioral guidance so Claude calls `goal_update_step` immediately after finishing a plan's implementation, instead of stopping to report to the user

## [0.15.5] - 2026-03-05

### Fixed
- **Auto-continue after plan approval** - ExitPlanMode hook now injects via `additionalContext` (not `systemMessage`) and directs Claude to start executing immediately

## [0.15.4] - 2026-03-04

### Fixed
- **Stronger auto-continue after step completion** - When `goal_update_step` marks a step done, the hook now injects the full next-step context via `additionalContext` (not just a soft `systemMessage` nudge), with an explicit "ACTION REQUIRED: Continue immediately" directive

## [0.15.3] - 2026-03-04

### Added
- **Plan-to-goal intercept** - PreToolUse hook on EnterPlanMode nudges Claude to create a goal first when no active goal exists, keeping plans scoped to individual steps

## [0.15.1] - 2026-03-04

### Fixed
- **Process guardian** - New background watcher kills MCP servers and indexers when parent Claude session exits (prevents orphaned processes from accumulating across sessions)
- **Orphan cleanup on start** - Session start now detects and kills context-daddy processes reparented to init (ppid=1)
- **SessionEnd cleanup** - `on-exit.sh` now also kills `update-context.sh` background agents

## [0.15.0] - 2026-03-04

### Added
- **Context injection tracking** - All hooks wrapped by `hook-runner.sh` which logs output sizes to `~/.claude/logs/context-injection.tsv`
- **Collation script** - `uv run scripts/collate-injections.py` summarizes injection sizes by hook, session, and project
- Supports `--detail`, `--by-session`, `--since 24h`, and `--tail N` options

## [0.14.6] - 2026-03-02

### Added
- **Plan-to-goal capture** - PostToolUse hook on ExitPlanMode detects approved plan steps and nudges Claude to add them as goal steps, ensuring plan work persists across sessions

## [0.14.5] - 2026-03-02

### Added
- **Step reordering/removal instructions** - Goal skill and context helper now explain how to rearrange or delete plan steps by editing the goal file directly

## [0.14.4] - 2026-03-01

### Fixed
- **MCP permissions auto-installed** - No longer requires user consent prompt; wildcard allow rules added automatically on session start
- **Goal-driven workflow guidance** - Context injection tells Claude to use goals instead of plans for multi-step tasks, and to auto-continue after completing a step
- **PostToolUse nudge** - After completing a goal step, Claude is prompted to continue to the next one

## [0.14.3] - 2026-03-01

### Added
- **StatusLine with goal tracking** - Auto-installs a status bar showing model, context %, cost, and active goal (slug + focused step)
- Respects existing statusLine config - if one exists, injects guidance for Claude to help integrate goal tracking
- StatusLine script updated silently on plugin updates

## [0.14.2] - 2026-03-01

### Fixed
- **Goal context not showing on session resume** - f-string dict access broken inside single-quoted bash heredoc; switched to `.get()` with temp variables

## [0.14.1] - 2026-03-01

### Added
- **Goals MCP server** - 11 tools for goal management via MCP (no Bash noise)
  - `goal_create`, `goal_list`, `goal_show`, `goal_switch`, `goal_unset`
  - `goal_focus`, `goal_update_step`, `goal_add_learning`, `goal_add_step`
  - `goal_link_project`, `goal_archive`
- **Step IDs** - Human-readable IDs auto-generated from step descriptions (e.g., `[fix-review]`)
- **Goal slugs** - Human-readable aliases auto-generated from titles (e.g., `goal-tracking-functionality`)
- **Step focus** - `/context-daddy:goal-focus` skill to set which step you're working on
- **Project-scoped context** - Session startup shows active goal, focused step, filtered activity, and recent learnings
- **PostToolUse hook** - Transient status update after goal changes
- **Storage format v2** - Goals have slugs, steps have IDs, `.current-goal` format is `UUID:step-id`
- **Migration** - `goals.py migrate` upgrades v1 goals to v2 in-place
- **24 goal tests** - Comprehensive test coverage including focus, context, slugs, migration, backwards compat

### Fixed
- Empty plan section rebuild (regex now matches 0+ steps)
- `goal_context` IndexError on malformed objectives
- Stale `.current-goal` when all steps completed
- Shell injection in goal-context-helper.sh (paths via env vars)
- Substring match for duplicate project detection

## [0.14.0] - 2026-03-01

### Added
- **Cross-session goal tracking** - Track multi-session objectives that persist across sessions and projects
  - Goals stored globally in `~/.claude/goals/`
  - Per-project index in `.claude/active-goals.json`
  - Active goal shown in session startup, post-compaction, and subagent context
  - Commits auto-tracked in goal's Recent Activity
- **Goal skill commands** - `/context-daddy:goal`, `/context-daddy:goal-new`, `/context-daddy:goal-done`

## [0.9.6] - 2026-01-16

### Added
- **Plugin configuration validation tests** - Comprehensive testing to prevent configuration bugs
  - `tests/test_plugin_config.py` - 7 static validation tests
    - Validates plugin.json has all required fields (including `hooks`)
    - Verifies hooks.json structure and referenced scripts exist
    - Checks version format and marketplace.json consistency
  - `.github/workflows/test-hooks.yml` - E2E hook execution test
    - Actually loads plugin into Claude Code
    - Tests SessionStart, PreCompact, and Stop hooks
    - Verifies hooks fire and create expected side effects
  - Added to CI pipeline - runs on every push
  - **Would have caught v0.9.4 bug** - missing `hooks` field now fails CI

### Changed
- CI now runs comprehensive plugin validation after JSON syntax checks

## [0.9.5] - 2026-01-16

### Fixed
- **CRITICAL: Stop hook not loading** - Added missing `hooks` field to plugin.json
  - Stop hook (post-compaction reorientation) wasn't being registered
  - All hooks were silently ignored since v0.9.0
  - Now properly references `hooks/hooks.json` in plugin manifest

## [0.9.4] - 2026-01-16

### Added
- **Database versioning** - Added `DB_VERSION = 1` constant for future schema migrations
  - Stored in metadata table as `db_version`
  - Enables safe schema changes and version checking in the future

### Changed
- **Removed plugin version cleanup** - No longer deletes old plugin versions at session start
  - Previous cleanup broke concurrent Claude sessions using different plugin versions
  - Prevents conflicts when multiple sessions run in the same project directory
  - Users can manually clean up old versions if needed

## [0.9.3] - 2026-01-16

### Changed
- **Learnings reminder in Stop hook** - Moved learnings update reminder to post-compaction block
  - Stop hook now prompts to update learnings.md BEFORE restoring context
  - More effective than precompact reminder (which gets lost during compaction)
  - Claude sees reminder right when being forced to restore context

## [0.9.2] - 2026-01-14

### Fixed
- **Progress percentage bug** - Fixed 5800% indexing progress display
  - generate-repo-map.py now includes `files_to_parse` in final "complete" status
  - session-start.sh falls back to `files_total` instead of defaulting to 1
  - Prevents divide-by-one error when `files_to_parse` is missing

## [0.9.1] - 2026-01-09

### Added
- **Markdown navigation tools** - Navigate large markdown documentation files efficiently
  - `md_outline(file_path)` - Get hierarchical heading structure (table of contents)
  - `md_get_section(file_path, heading)` - Extract content under specific heading
  - `md_list_tables(file_path)` - List all tables with headers and context
  - `md_get_table(file_path, index)` - Get full table content by index
  - `md_list_figures(file_path)` - List all images/figures with alt text and paths
  - All return clean markdown format for easy reading

### Use Cases
- Navigate large CLAUDE.md, learnings.md, or API documentation
- Extract specific sections without reading entire files
- Find and compare benchmark tables
- Locate images and diagrams
- Pairs perfectly with post-compaction reorientation (fetch specific sections)

### Examples
```markdown
## md_outline(".claude/learnings.md")
- Project Learnings (line 1)
  - OSDI Python Bindings (line 3)
  - JAX Circuit Evaluation (line 15)
    - Performance Optimization (line 20)

## md_list_tables("docs/benchmarks.md")
1. Line 23: | Test Case | Time (ms) | Memory (MB) |
2. Line 45: | Framework | Score |

## md_list_figures("README.md")
1. Line 46: Architecture Diagram -> ./images/arch.png
```

## [0.9.0] - 2026-01-09

### Changed
- **BREAKING: Switched to Stop hook pattern for post-compaction reorientation** - Much more effective!
  - Inspired by [context-forge](https://github.com/webdevtodayjason/claude-hooks) approach
  - Stop hook **BLOCKS Claude** until context is restored (vs passive injection in v0.8.14)
  - Returns `{"decision": "block", "reason": "Instructions..."}` to force action
  - Makes Claude **actively read files** instead of passively receiving injected content
  - 5-minute window for detecting recent compaction

### How It Works Now
1. **PreCompact**: Creates `.claude/needs-reorientation` marker file
2. **Compaction happens** (Claude Code does this)
3. **Claude finishes response** → Stop hook fires
4. **Stop hook detects marker** (if <5 min old) → **BLOCKS Claude**
5. **Claude must read** CLAUDE.md, learnings.md, and query MCP tools to restore context
6. Marker removed (one-time per compaction)

### Why This Is Better
- ✅ **Blocks Claude** - Can't continue without reading files (vs passive prompt injection)
- ✅ **Active restoration** - Claude reads and processes files (more effective than passive text)
- ✅ **Uses existing files** - CLAUDE.md, learnings.md (no generated content needed)
- ✅ **Proven pattern** - Based on context-forge's successful implementation
- ✅ **5-minute window** - Prevents stale marker triggering

### Removed
- UserPromptSubmit hook approach (replaced with Stop hook)
- `post-compact-reorient.sh` (replaced with `stop-reorient.sh`)

## [0.8.15] - 2026-01-09

### Changed
- **All MCP tools now return markdown instead of JSON** - Major improvement for Claude readability
  - `search_symbols()` - Returns formatted list with `**Name** (kind) - path:line` and docstrings
  - `get_file_symbols()` - Returns organized symbol list with signatures and docs
  - `get_symbol_content()` - Returns formatted markdown with syntax-highlighted code blocks
  - `list_files()` - Returns grouped file list organized by directory
  - Clean, scannable format with headers, bullet points, and inline code
  - Error messages now use emoji (❌) for quick visual scanning

### Benefits
- ✅ Much easier for Claude to read and understand
- ✅ Natural markdown format instead of raw JSON structures
- ✅ Syntax highlighting in code blocks
- ✅ Hierarchical organization (headings, grouped content)
- ✅ Inline documentation and docstrings included where available

## [0.8.14] - 2026-01-09

### Added
- **Post-compaction reorientation system** - Automatically restores context after `/compact`
  - PreCompact hook creates `.claude/needs-reorientation` flag
  - UserPromptSubmit hook detects flag and prepends reorientation context to first prompt after compaction
  - Context includes: MCP tools reminder, project structure, key components, recent learnings
  - All formatted in clean, scannable markdown
  - Flag automatically removed after first use
- **Enhanced learnings reminder** - Added "Solution approaches discussed and agreed with user" to precompact message

### Changed
- **Improved reorientation format** - Switched from raw SQL/JSON output to clean markdown
  - Section headings: `## MCP Tools Available`, `## Project Structure`, etc.
  - Inline code formatting with backticks
  - File locations shown as `path:line`
  - Natural, hierarchical structure for quick scanning

### Fixed
- **Context loss after compaction** - Claude no longer forgets major implementations (like OSDI Python bindings) after `/compact`
- **MCP tools reminder after compaction** - Claude receives fresh reminder to use MCP tools instead of Search/Grep

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
