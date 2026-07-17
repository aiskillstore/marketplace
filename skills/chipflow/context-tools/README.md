<p align="center">
  <img src="docs/social.png" alt="context daddy" width="640">
</p>

<p align="center">
  <a href="https://github.com/ChipFlow/context-daddy/actions/workflows/ci.yml"><img src="https://github.com/ChipFlow/context-daddy/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://chipflow.github.io/context-daddy/"><img src="https://github.com/ChipFlow/context-daddy/actions/workflows/pages.yml/badge.svg" alt="Docs"></a>
</p>

**[Documentation](https://chipflow.github.io/context-daddy/)** · **[Changelog](CHANGELOG.md)**

## What

Context Daddy is a sophisticated code understanding plugin for Claude Code that fundamentally changes how AI assistants explore and comprehend large codebases. By combining tree-sitter parsing, intelligent caching, and a custom MCP (Model Context Protocol) server, we're creating a system that can quickly generate semantic maps of entire repositories and provide fast, targeted code retrieval without overwhelming context windows. The project now includes narrative documentation tools that capture the evolving "tribal knowledge" of codebases - the stories, gotchas, and hard-won insights that traditional documentation misses.

Built in tools include:
- **Fast symbol search** - 10-100x faster than grep via MCP tools
- **Living narratives** - Capture the "why", not just the "what"
- **Tribal knowledge** - Dragons, gotchas, and hard-won insights that survive context compaction

## Why

Understanding code isn't just about parsing syntax. It's about the *stories* - "here be dragons", "we did X because Y", "this is WTF but it works". That knowledge lives in people's heads and gets lost.

**context daddy** captures both: fast code exploration AND the narrative that makes codebases actually understandable.

## Quick Start

```bash
# Install
claude plugin marketplace add chipflow/context-daddy
claude plugin install context-daddy

# Verify MCP tools work
claude mcp list  # Should show: repo-map: ✓ Connected

# Generate a narrative for your project
cd /path/to/your-project
/context-daddy:story
```

Or load directly without installing:
```bash
claude --plugin-dir /path/to/context-daddy
```

## Features

### 🔍 Fast Symbol Search

```
search_symbols("*Handler")         → Find all handler classes
get_symbol_content("AuthService")  → Full source with docstrings
get_file_symbols("src/api.py")     → Everything in a file
list_files("*.py")                 → Find files by pattern
```

Pre-built SQLite index with FTS5. Claude explores your codebase without drowning in context.

### 📖 Living Narratives

Not changelogs. **Stories**:

- **Summary** - What and why
- **Current Foci** - What we're working on now
- **How It Works** - Architecture in plain language
- **The Story So Far** - How we got here
- **Dragons & Gotchas** - Warnings for future-us
- **Open Questions** - Things we're still figuring out

```bash
/context-daddy:story    # Bootstrap from git history
/context-daddy:refresh  # Revise after sessions
```

Written in "we" voice. Opinionated. Updated after context compaction.

### 🎯 Cross-Session Goals

Track multi-session objectives that persist across sessions and projects:

```
/context-daddy:goal-new    → Guided goal creation with plan steps
/context-daddy:goal-done   → Complete current step, advance to next
/context-daddy:goal-focus  → Set which step you're working on
/context-daddy:goal        → List, switch, or archive goals
```

Goals have human-readable slugs and step IDs. The active goal and focused step appear automatically in every session's context.

### 🧠 Learnings

Hard-won insights that persist:
- `.claude/learnings.md` - Project-specific
- `~/.claude/learnings.md` - Global
- Prompted to save before compaction

## Commands

| Command | Purpose |
|---------|---------|
| `/context-daddy:story` | Bootstrap narrative from git |
| `/context-daddy:refresh` | Update narrative after a session |
| `/context-daddy:readme` | Generate README from narrative |
| `/context-daddy:map` | Regenerate repo map |
| `/context-daddy:scan` | Regenerate project manifest |
| `/context-daddy:status` | Indexing status |
| `/context-daddy:learn` | Manage learnings |
| `/context-daddy:goal-new` | Create a new goal |
| `/context-daddy:goal` | Manage goals |
| `/context-daddy:goal-done` | Complete current step |
| `/context-daddy:goal-focus` | Set focused step |
| `/context-daddy:help` | MCP tools guide |

## How It Works

**Three components:**
1. **Tree-sitter indexing** → Semantic symbols from Python, C++, Rust
2. **SQLite + FTS5** → Fast retrieval and search
3. **MCP server** → Tools Claude can query

**Multiprocess design:** Indexing runs in isolated subprocesses (4GB memory, 20 min CPU limit, watchdog). MCP server stays responsive.

**Hooks:** SessionStart loads context, Stop hook guides reorientation after compaction.

**Generated files:**
```
.claude/
├── narrative.md           # Project story
├── project-manifest.json  # Build system, languages
├── repo-map.db            # Symbol index
├── learnings.md           # Your insights
├── active-goals.json      # Goal index for this project
├── .current-goal          # Active goal reference
└── logs/
    ├── repo-map-server.log
    └── goals-server.log
~/.claude/goals/           # Goal files (global)
```

## Requirements

- [uv](https://docs.astral.sh/uv/) for Python
- Python 3.10+
- `ANTHROPIC_API_KEY` for narrative generation

---

## The Journey

We started simple: parse code with tree-sitter, generate repo maps. Then reality hit.

**Memory explosion.** Large codebases broke everything. We moved to incremental caching and parallel parsing with resource limits.

**Static maps weren't enough.** Claude needed fast, targeted access. We built an MCP server - a live query interface, not just generated docs.

**Process management nightmares.** Zombie processes, resource leaks, conflicts. Multiple iterations before landing on isolated subprocesses with watchdog monitoring.

**User experience matters.** Database versioning for seamless upgrades. Simpler hook patterns. Progressive feedback during indexing.

**The philosophical shift.** We realized understanding codebases isn't just parsing - it's capturing stories, decisions, and hard-won insights. Traditional docs capture what code does; narratives capture why it exists.

Throughout: balancing comprehensive understanding against context overload. That tension shapes everything.

## Known Dragons 🐉

**Hooks are fragile.** Autodiscovery doesn't always match expectations. We've been bitten in CI.

**SQLite WAL helps but isn't magic.** We moved away from heavy locking after deadlocks.

**Tree-sitter memory spikes.** Subprocess isolation is our safety net.

**MCP lifecycle is underdocumented.** We've reverse-engineered start/stop behavior.

## Open Questions

- FTS5 search is underutilized - what's the right UX?
- Are 'learnings' needed with new claude memory capability?
- Can we make better use of new claude memory?
- 
## License

MIT
