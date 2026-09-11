# Platform Installation

This skill is a plain Agent Skills package (top-level layout; the fully annotated tree is in README → Repository Layout):

```text
gpt-series-reasoning-style/
├── SKILL.md                 # entry point
├── VERSION
├── AGENTS.md                # cross-runtime entry alias (Codex/Gemini/Copilot CLI) — routes here
├── README.md / LICENSE / CHANGELOG.md
├── agents/openai.yaml       # optional platform metadata
├── identities/              # built-in role identities
├── custom-identities/       # user-defined identities
├── references/              # on-demand detailed rules
├── docs/minimal-discipline.md  # minimal three-rule quick card (also valid standalone)
├── hooks/                   # optional session-start reminder (opt-in)
├── scripts/                 # install.ps1 / install.sh / selfcheck.py / selftest-runner.py / artifact-check.py / claim-check.py
├── probes/ · site/          # maintainer instruments (probe runner; static docs page)
├── generate-banner.py       # maintainer tool: renders social-preview.png
└── social-preview.png / .svg
```

The installers strip repo-only surfaces (`.git*`, `.github/`, `site/`, `__pycache__/`) so an
installed copy contains only what the host needs; the fully annotated tree is in README → Repository Layout.

Copy or symlink the whole folder into the skill directory used by your tool. Keep the folder name `gpt-series-reasoning-style`.

This skill is a behavior overlay, not an identity replacement. Follow the host agent's identity and platform rules first.

In this table, product names such as Trae refer to the IDE platform itself, not to an AI, model, or project role.

Optional platform metadata:

```text
agents/openai.yaml
```

`agents/openai.yaml` is optional UI metadata used by OpenAI/Codex-compatible skill surfaces. It provides `display_name`, `short_description`, and `default_prompt`. The `default_prompt` is part of the execution layer for platforms that use it: it carries the mandatory pre-implementation gate and clarification-mode selection into the first invocation. Other platforms do not need this file, but if a platform uses `default_prompt`, do not replace it with a generic "use the skill" prompt.

## Common Install Paths

| Platform | Skill directory |
| --- | --- |
| Codex CLI / Codex desktop | `~/.codex/skills/` or `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| VS Code Copilot | `~/.claude/skills/` or `.github/skills/` |
| Cursor | `.cursor/rules/` |
| Windsurf | `.windsurf/rules/` |
| Cline | `.clinerules/` |
| Gemini CLI | `~/.gemini/skills/` |
| Kiro | `~/.kiro/skills/` |
| Trae | `.trae/rules/` |
| Goose | `~/.config/goose/skills/` |
| OpenCode | `~/.config/opencode/skills/` |
| Roo Code | `.roo/rules/` |
| Antigravity | `~/.agents/skills/` |
| Generic Agent Skills | `~/.agents/skills/` |

## Windows Example

```powershell
& powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Platform agents
```

## macOS / Linux Example

```bash
chmod +x scripts/install.sh
./scripts/install.sh agents
```

## Verification

After installation, invoke the skill by name:

```text
使用 $gpt-series-reasoning-style 按本推理风格执行本次任务。
```

The skill should load `SKILL.md`; reference files are read on demand only when the current phase needs them.
