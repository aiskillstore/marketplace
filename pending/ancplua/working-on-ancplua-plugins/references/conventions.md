# Conventions

> Based on [official Claude Code plugin docs](https://code.claude.com/docs/en/plugins)

## Critical Architecture Rules

### 1. Path Variables

**ALWAYS** use `${CLAUDE_PLUGIN_ROOT}` for paths in configuration files (MCP, Hooks, etc.).
This ensures portability across different users and systems.

**Correct:**

```json
"args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"]
```

**Wrong:**

```json
"args": ["/Users/ancplua/projects/plugins/server/index.js"]
```

### 2. Manifest Locations

The `.claude-plugin/` directory is **ONLY** for manifests (`plugin.json`, `marketplace.json`).

- **DO NOT** put `skills/`, `commands/`, or `hooks/` inside `.claude-plugin/`.
- **DO** put them at the plugin root.

### 3. Relative Paths

In `plugin.json`, all relative paths must start with `./` and be relative to the plugin root.

---

## Directory Layout

Every plugin under `plugins/<plugin-name>/` must follow this structure
(per [official docs](https://code.claude.com/docs/en/plugins)):

```text
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json       # REQUIRED: name, description, version, author
├── skills/               # Agent Skills (1 folder per skill)
│   └── my-skill/
│       └── SKILL.md      # Requires: name, description frontmatter
├── commands/             # Custom Slash Commands
│   └── my-command.md
├── agents/               # Custom Agents
│   └── my-agent/
├── hooks/                # Event Handlers
│   └── hooks.json
├── scripts/              # Executable helper scripts
└── README.md             # REQUIRED
```

---

## plugin.json Fields

Per [official docs](https://code.claude.com/docs/en/plugins):

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Plugin identifier (kebab-case) |
| `description` | Yes | What the plugin does |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `author` | Yes | Object with at least `name` field |
| `license` | No | Optional license identifier |
| `repository` | No | Optional repo URL |
| `keywords` | No | Optional discovery tags |

---

## Naming Conventions

| Entity | Convention | Example |
|--------|------------|---------|
| Plugin Directory | `kebab-case` | `autonomous-ci` |
| Skill Directory | `kebab-case` | `code-review` |
| Skill File | `SKILL.md` | Always this name |
| Script File | `kebab-case.sh` | `verify-local.sh` |
| Manifest | strict name | `plugin.json` |

---

## Git Conventions

- **Branches**: `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat: add new skill`
  - `fix: resolve path issue`
  - `docs: update readme`
- **PRs**: Link related issues/specs.

---

## Documentation Standards

- **README.md**: Every plugin must have one.
- **CHANGELOG.md**: Required for non-trivial changes (repo root).
- **ADRs**: Architectural decisions go in `docs/decisions/`.
- **Specs**: Complex features need specs in `docs/specs/`.
