# Agent Compatibility

`prettify-pdf` follows the common Agent Skills layout:

```text
prettify-pdf/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

Only `SKILL.md` is required. The helper script and reference files are optional.

## Works Best When The Agent Can

- Read local files.
- Render PDFs to images or use a local PDF renderer.
- Create or modify PDFs with local tools.
- Run optional local scripts.
- Inspect rendered images visually or ask a vision-capable model/reviewer to compare source and final renders.

## No Provider Lock-In

The skill does not require:

- OpenAI API keys.
- Anthropic API keys.
- A hosted app.
- A web server.
- MCP servers.
- External OCR or PDF APIs.

Agents may use any local PDF tooling available in their environment: PyMuPDF, Poppler, ReportLab, WeasyPrint, LibreOffice, browser print-to-PDF, or equivalent tools.

## Installation Patterns

Codex-style local skill:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/sethupavan12/prettify-pdf "${CODEX_HOME:-$HOME/.codex}/skills/prettify-pdf"
```

Claude Code-style personal skill:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.claude/skills/prettify-pdf"
```

Project-scoped skill:

```bash
mkdir -p .claude/skills
cp -R prettify-pdf .claude/skills/prettify-pdf
```

Generic agent:

Point the agent at `SKILL.md` and tell it to follow the instructions when transforming or QAing PDFs.

OpenClaw shared skill:

```bash
mkdir -p "$HOME/.openclaw/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.openclaw/skills/prettify-pdf"
openclaw skills list
```

OpenClaw workspace skill:

```bash
mkdir -p skills
git clone https://github.com/sethupavan12/prettify-pdf skills/prettify-pdf
openclaw skills list
```

OpenCode-style project skill:

```bash
mkdir -p .opencode/skill
git clone https://github.com/sethupavan12/prettify-pdf .opencode/skill/prettify-pdf
```
