# Connecting tools to a knowledge node

Run each of these only when the person asks for that connection.

## Coding agents: steering files

`agsc export --steer --target <names>` writes one file per target under `dist/export/steer/`, the same bytes at each path. Copy it where the tool reads it.

| Target | Path |
|---|---|
| `agents` | `AGENTS.md` (read by Codex, Cursor, GitHub Copilot, Claude Code) |
| `claude` | `CLAUDE.md` |
| `codex` | `AGENTS.override.md` (replaces `AGENTS.md` for Codex) |
| `cursor` | `.cursor/rules/agsc.mdc` |
| `copilot` | `.github/copilot-instructions.md` |
| `gemini` | `GEMINI.md` |
| `kiro` | `.kiro/steering/agsc.md` |
| `windsurf` | `.windsurf/rules/agsc.md` |
| `cline` | `.clinerules/agsc.md` |
| `aider` | `CONVENTIONS.md` (start Aider with `--read CONVENTIONS.md`) |
| `gabbe` | `GABBE/agents/AGENTS.md` |

A steering file is context, not enforcement. A `CLAUDE.md` can keep the node's file separate with one line, `@.agsc/CLAUDE.md`.

## Assistants: the tool server

Run in the Bundle. Claude Code: `claude mcp add --transport stdio my-knowledge -- npx -y agsc-cli mcp`. Codex CLI: `codex mcp add my-knowledge -- npx -y agsc-cli mcp`. Cursor (`.cursor/mcp.json`) and Claude Desktop use `{"mcpServers":{"my-knowledge":{"command":"npx","args":["-y","agsc-cli","mcp"]}}}`; VS Code (`.vscode/mcp.json`) uses the top-level key `servers` with `"type": "stdio"`. The server reads the Bundle once at start; restart it after edits.

## Skills

`agsc skills` then `agsc skills install .claude/skills` (or `.agents/skills`, `.github/skills`). From a cloned collection: `agsc import <clone> --from skills --list`, then `--dry-run`, then the import. To a collection: `agsc export --to skills --layout agentskills|claude-plugin|marketplace|cursor|windsurf`. Imported skills lose scripts, hooks and tool allow-lists; a skill without an open licence arrives as a draft.

## Memory systems and trackers

- Cognee (and what it migrated from Mem0, Letta, LangMem, Zep): `agsc export --to cogx`; back with `agsc import <dir> --from cogx`.
- One context file for a model: `agsc export --to llm-context`.
- Trackers: `agsc import <dir> --from board --format <f> --dry-run`, then without `--dry-run`; out with `agsc export --to board --format <f>`. Formats: `agsc-board`, `github`, `gitlab`, `jira`, `trello`, `linear`, `asana`, `notion`, `obsidian-kanban`, `markdown`, `todotxt`. Every imported row is a draft until a person publishes it.
- Diagrams: `agsc export --to mermaid`.

## Enforcement

- Before each commit: the `agsc-lint` hook from the engine's `.pre-commit-hooks.yaml` (pre-commit framework, `rev:` pinned).
- In CI: `uses: andreibesleaga/agentic-system-core@<tag-or-sha>` in a GitHub Actions job with `contents: read` and `fetch-depth: 0`; it runs `agsc ci`.
- Hosting: `agsc-host list` names the hosting profiles; `agsc-host emit <profile>` writes one host's configuration from the build.
