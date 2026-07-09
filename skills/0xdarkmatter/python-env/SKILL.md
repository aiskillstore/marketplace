---
name: python-env
description: "Fast Python environment management with uv (10-100x faster than pip). Triggers on: uv, venv, pip, pyproject, python environment, install package, dependencies."
license: MIT
compatibility: "Requires uv CLI tool. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
allowed-tools: "Bash"
metadata:
  author: claude-mods
---

# Python Environment

Fast Python environment management with uv. Prefer the uv **project** workflow
(`uv add` / `uv sync` / `uv run`) over the `uv pip` compatibility layer — it
manages `pyproject.toml` + a lockfile for you and is reproducible.

## Quick Commands

| Task | Command |
|------|---------|
| Start a project | `uv init <name>` (app) · `uv init --package <name>` (installable, `src/` layout) |
| Add dependency | `uv add httpx` |
| Add dev dependency | `uv add --dev pytest ruff` |
| Remove dependency | `uv remove httpx` |
| Sync env from lockfile | `uv sync` |
| Run in project env | `uv run pytest` |
| Update lockfile | `uv lock` |
| Install a CLI tool | `uv tool install ruff` · one-shot: `uvx ruff` |
| Install a Python | `uv python install 3.12` |

## Start a Project

```bash
# Application (flat layout, no package build)
uv init myapp

# Installable package (src/ layout — separate tests/ that import by name)
uv init --package wordtools
# → src/wordtools/__init__.py, pyproject.toml with build-system
```

`uv init` creates `pyproject.toml`, pins a Python version, and prepares the
project for `uv add` / `uv sync`. The `--package` (src) layout is preferred for
anything with a test suite or that you intend to ship.

## Manage Dependencies

```bash
# Add runtime deps (writes to [project.dependencies] + updates the lockfile)
uv add "httpx>=0.25" pydantic

# Add dev-only deps (writes to the dev dependency-group)
uv add --dev pytest ruff mypy

# Add with extras
uv add "fastapi[standard]"

# Remove
uv remove httpx

# Install everything from pyproject + uv.lock into .venv (reproducible)
uv sync

# Refresh the lockfile (e.g. after manual pyproject edits)
uv lock
```

`uv` creates and manages `.venv` automatically — you rarely activate it; just
prefix commands with `uv run`.

## Run Code

```bash
uv run python script.py     # run a script in the project env
uv run pytest               # run a tool from the dev group
uv run -- ruff check .      # `--` ends uv flag parsing
```

Never call bare `python` / `pytest` / `ruff` in a uv project — they may resolve
to a different interpreter. Always `uv run`.

## CLI Tools (global, not project deps)

```bash
uv tool install ruff        # persistent, isolated, on PATH
uv tool upgrade ruff
uvx ruff check .            # ephemeral one-shot run, nothing installed
```

Use `uv tool` / `uvx` for developer CLIs (ruff, pre-commit, httpie). Use
`uv add` only for things your code imports.

## Python Versions

```bash
uv python install 3.12      # download a managed interpreter
uv python list              # show available + installed
uv init --python 3.12 app   # pin a project to a version
```

Check python.org for the current stable (3.14 as of 2026-07; recent releases add
opt-in free-threading and a JIT). 3.11+ is a sensible floor for new projects
(TaskGroup, `Self`, faster interpreter).

## Minimal pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.25",
    "pydantic>=2.0",
]

# Dev deps live here; `uv add --dev <pkg>` manages this group.
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

## Compatibility Layer (`uv pip`) — last resort

`uv pip` mirrors pip's interface for environments uv doesn't manage (a hand-made
venv, a legacy `requirements.txt`, CI that isn't uv-native). It does **not**
update `pyproject.toml` or the lockfile — prefer `uv add` / `uv sync` whenever
you control the project.

```bash
uv venv                              # bare venv (no project)
uv pip install -r requirements.txt   # legacy requirements file
uv pip install -e .                  # editable install into an unmanaged venv
uv pip compile requirements.in -o requirements.txt   # pin a requirements.txt
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No Python found" | `uv python install 3.12` |
| Pin project Python | `uv init --python 3.12` or edit `requires-python` |
| Lock/resolve conflict | `uv lock --resolution=lowest-direct` to probe, then loosen bounds |
| Stale env after pull | `uv sync` |
| Cache issues | `uv cache clean` |

## When to Use

- **Always** use uv over pip — 10-100x faster
- `uv add` / `uv remove` / `uv sync` for project dependencies (not `uv pip install`)
- `uv run` to execute anything inside the project env
- `uv tool install` / `uvx` for standalone developer CLIs
- `uv pip` only for environments uv doesn't manage

## Additional Resources

For detailed patterns, load:
- `./references/pyproject-patterns.md` - Full pyproject.toml examples, tool configs
- `./references/dependency-management.md` - Lock files, workspaces, private packages
- `./references/publishing.md` - PyPI publishing, versioning, CI/CD

---

## See Also

This is a **foundation skill** with no prerequisites.

**Build on this skill:**
- `python-typing-ops` - Type hints for projects
- `python-pytest-ops` - Testing infrastructure
- `python-fastapi-ops` - Web API development
