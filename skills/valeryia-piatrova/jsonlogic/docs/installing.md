# Installing in other Agent Skills clients

This skill uses the open [Agent Skills](https://agentskills.io) format, so any
client that supports it can load it. In every case: clone this repository,
name the local folder `jsonlogic` (matching the `name` in `SKILL.md`'s
frontmatter), and put it at the path below for your tool. Paths checked
against each tool's own docs on 2026-09-16 — re-check if a tool has since
changed its convention.

### Cursor

Project-local:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git .cursor/skills/jsonlogic
```
All projects:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git ~/.cursor/skills/jsonlogic
```
Cursor also reads `.claude/skills/`, so the Claude Code install in the main
README works there too.

### GitHub Copilot

This repo only:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git .github/skills/jsonlogic
```
All repos:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git ~/.copilot/skills/jsonlogic
```

### VS Code

Copilot Chat / agent mode, workspace:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git .github/skills/jsonlogic
```
User profile:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git ~/.claude/skills/jsonlogic
```

### Codex

For ChatGPT / Codex, current repo:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git .agents/skills/jsonlogic
```
Every repo:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git ~/.agents/skills/jsonlogic
```

### Gemini CLI

Workspace:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git .gemini/skills/jsonlogic
```
User-level:
```bash
git clone https://github.com/valeryia-piatrova/jsonlogic-skill.git ~/.gemini/skills/jsonlogic
```

**Any other Agent Skills client:** most newer tools converge on the
interoperable `.agents/skills/` (project) and `~/.agents/skills/` (user) paths
shown for Codex — try those first, then check that tool's docs, linked from
its entry at [agentskills.io/clients](https://agentskills.io/clients), if it
doesn't pick the skill up.

After cloning, restart or reload the tool (or its skills panel, if it has
one) — most don't pick up new folders until then.
