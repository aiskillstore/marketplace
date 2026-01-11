# Context Tools for Claude Code

[![CI](https://github.com/ChipFlow/claude-context-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/ChipFlow/claude-context-tools/actions/workflows/ci.yml)

A Claude Code plugin that helps Claude maintain context awareness in large codebases through automatic project mapping, duplicate detection, and learning retention.

## Features

### Project Manifest
Automatically detects and tracks:
- Programming languages in your project
- Build system and commands (npm, uv, pdm, cargo, cmake, meson, go)
- Entry points and main scripts
- Git activity summary

### Repository Map with Duplicate Detection
Generates a comprehensive map of your codebase:
- **Multi-language support**: Python, C++, and Rust
- Extracts all classes, functions, and methods with their signatures
- Detects potentially similar classes that may have overlapping responsibilities
- Identifies similar functions that could be candidates for consolidation
- Analyzes documentation coverage to highlight gaps
- **Incremental caching**: Only re-parses changed files (mtime + content hash)
- **Parallel parsing**: Uses multiple CPU cores for large codebases
- **Background execution**: Repo map builds asynchronously on session start

### Learnings System
Helps Claude remember important discoveries:
- Project-specific learnings in `.claude/learnings.md`
- Global learnings in `~/.claude/learnings.md`
- Prompted to save learnings before context compaction

## What's New in v0.8.0

### 🏗️ Multiprocess Architecture
- MCP server spawns indexing subprocess (no longer thread-based)
- Watchdog can kill hung processes with resource limits (4GB memory, 20 min CPU)
- MCP server stays responsive even during indexing

### 📂 Dynamic Directory Support
- **Switch between projects without restarting!**
- MCP tools automatically adapt to current working directory
- Each project maintains its own index
- Tools "just work" wherever you are

### 🔒 Simplified Concurrency
- Rely on SQLite WAL mode + transactions (removed custom file locking)
- Multiple MCP servers can safely coexist
- Clean, robust concurrent access

### 📊 Comprehensive Logging
- Rotating logs in `.claude/logs/repo-map-server.log`
- Track tool usage, indexing events, resource limits
- Debug issues and understand usage patterns

[See full changelog](CHANGELOG.md)

## Installation

### Option 1: Install from GitHub (recommended)

First, add the repository as a plugin marketplace:

```bash
claude plugin marketplace add chipflow/claude-context-tools
```

Then install the plugin:

```bash
claude plugin install context-tools
```

### Option 2: Install from local directory (for development)

```bash
git clone https://github.com/chipflow/claude-context-tools.git
claude plugin marketplace add ./claude-context-tools
claude plugin install context-tools
```

### Option 3: Load directly without installing

For testing or one-off use:

```bash
claude --plugin-dir ./claude-context-tools
```

### Verify MCP Server is Loaded

After installing the plugin, **restart Claude Code**. The MCP server should auto-configure from the plugin manifest.

Verify the repo-map server is running:
```bash
claude mcp list
# Should show: repo-map: ... - ✓ Connected
```

Or in a Claude Code session, run `/mcp` to see available MCP servers.

**Troubleshooting**: If the server doesn't load, check that `uv` is installed and accessible in your PATH.

## Requirements

- [uv](https://docs.astral.sh/uv/) - Python package manager (for running scripts)
- Python 3.10+

## How It Works

### Hooks

The plugin registers two hooks:

1. **SessionStart**: When you start a Claude Code session, the plugin:
   - Generates/refreshes the project manifest
   - Displays a summary of project context
   - Shows count of available learnings

2. **PreCompact**: Before context compaction, the plugin:
   - Regenerates the project manifest
   - Updates the repository map
   - Reminds you to save important discoveries

### MCP Tools (Fast Symbol Lookup)

Once the MCP server is configured, Claude has access to these fast symbol search tools:

- `search_symbols` - Find functions/classes/methods by glob pattern (e.g., `get_*`, `*Handler`)
- `get_file_symbols` - List all symbols defined in a specific file
- `get_symbol_content` - Get full source code of a symbol by exact name
- `reindex_repo_map` - Trigger manual reindex if files changed
- `repo_map_status` - Check indexing status and staleness

These tools use a pre-built SQLite index, making them **much faster than Grep** for finding code symbols.

### Slash Commands

- `/context-tools:mcp-help` - **Guide for using MCP tools effectively** - Shows when to use MCP tools vs grep with real-world examples
- `/context-tools:repo-map` - Regenerate the repository map
- `/context-tools:manifest` - Regenerate the project manifest
- `/context-tools:learnings` - View and manage project learnings
- `/context-tools:status` - Check repo map indexing status

## Configuration

### Repo Map Options

The repo map generator supports command-line options:

```bash
# Use 75% of CPU cores for parsing (default: 50%)
uv run scripts/generate-repo-map.py /path/to/project --workers=75
```

### Supported Languages

| Language | Extensions | Parser |
|----------|------------|--------|
| Python | `.py` | Built-in AST |
| C++ | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.h`, `.hxx` | tree-sitter-cpp |
| Rust | `.rs` | tree-sitter-rust |

## Generated Files

The plugin creates files in your project's `.claude/` directory:

```
.claude/
├── project-manifest.json   # Build system, languages, entry points
├── repo-map.md             # Code structure with similarity analysis
├── repo-map.db             # SQLite database for fast symbol lookups (MCP server)
├── repo-map-cache.json     # Symbol cache for incremental updates
└── learnings.md            # Project-specific learnings
```

## Example Output

### Repository Map

```markdown
## Documentation Coverage

- **Classes**: 15/18 (83% documented)
- **Functions**: 42/50 (84% documented)

## ⚠️ Potentially Similar Classes

- **ConfigLoader** (src/config/loader.py)
  ↔ **SettingsLoader** (src/settings/loader.py)
  Reason: similar names (80%), similar docstrings (72%)

## Code Structure

### src/models/user.py

**class User**
  A user account in the system.
  - create(name: str, email: str) -> User
      Create a new user account.
  - update(self, **kwargs)
      Update user attributes.
```

### Project Manifest

```json
{
  "project_name": "my-project",
  "languages": ["python", "typescript"],
  "build_system": {
    "type": "uv",
    "commands": {
      "install": "uv sync",
      "build": "uv run build",
      "test": "uv run pytest"
    }
  },
  "entry_points": ["src/main.py", "src/cli.py"]
}
```

## Best Practices

### Recording Learnings

When you discover something important during a session, ask Claude to record it:

> "Add a learning about the database connection pooling optimization we just discovered"

Claude will add an entry to `.claude/learnings.md`:

```markdown
## Database: Connection pooling optimization

**Context**: High-traffic API endpoints with PostgreSQL
**Discovery**: Default pool size of 5 was causing connection exhaustion
**Solution/Pattern**: Increase pool size to 20, add 30s timeout, implement retry with exponential backoff
```

### Addressing Duplicate Detection

When the repo map shows similar classes or functions:
1. Review the flagged pairs to determine if they're truly duplicates
2. If they serve different purposes, improve their docstrings to clarify intent
3. If they're duplicates, consolidate them into a single implementation

## Development

### Running Tests Locally

```bash
# Validate JSON configs
python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"
python3 -c "import json; json.load(open('hooks/hooks.json'))"

# Check bash script syntax
bash -n scripts/session-start.sh
bash -n scripts/precompact.sh

# Test repo map generation
mkdir -p /tmp/test-project
echo 'def hello(): pass' > /tmp/test-project/main.py
uv run scripts/generate-repo-map.py /tmp/test-project
```

### Adding Language Support

To add support for a new language:

1. Add the tree-sitter grammar to dependencies in `generate-repo-map.py`
2. Create an `extract_symbols_from_<lang>()` function
3. Add file discovery in `find_<lang>_files()`
4. Update `parse_file_worker()` to handle the new language
5. Add tests in the CI workflow

## Uninstalling

To completely remove the plugin:

1. **Remove the MCP server:**
```bash
claude mcp remove repo-map
```

2. **Uninstall the plugin:**
```bash
claude plugin uninstall context-tools
```

3. **Clean up generated files** (optional - per project):
```bash
rm -rf .claude/repo-map.* .claude/project-manifest.json
```

Note: `.claude/learnings.md` contains your project insights - consider backing it up before deleting.

## License

MIT
