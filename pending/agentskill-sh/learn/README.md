# /learn

**Teach your AI agent anything — mid-conversation.**

Remember [the scene in The Matrix](https://www.youtube.com/watch?v=w_8NsPQBdV0) where Neo gets Kung Fu uploaded directly into his brain? *"I know Kung Fu."* Agent Skills work the same way — except for AI agents. You upload a skill file, and suddenly your agent knows about [SEO](https://agentskill.sh/for/seo-specialist), [how to write cold emails](https://agentskill.sh/humanizerai/cold-email), or even [accounting in France](https://agentskill.sh/romainsimon/french-accountant).

`/learn` lets you do this mid-conversation. One command, 40,000+ skills from [agentskill.sh](https://agentskill.sh).

```
/learn seo
```

Your agent searches the directory, shows the best matches, and installs your pick. No restart. No context switch.

---

## Why /learn?

### Security First

Every skill on agentskill.sh has a security score (0-100). Before installing anything, `/learn` performs a local security scan to catch malicious instructions.

After incidents like OpenClaw showed how rogue SKILL.md files can compromise agents, vetting matters. Skills below 30 require explicit confirmation.

### Feedback Loop

Agents auto-rate skills after use (1-5 scale with comments). The best skills surface. Broken ones get flagged. Your agent contributes to — and benefits from — collective quality signals.

### Search Broadly

Instead of hunting for skills manually, search 40,000+ skills mid-conversation. Find what you need, install it, keep working.

---

## Install

**Claude Code (recommended)**

```bash
/plugin marketplace add https://agentskill.sh/marketplace.json
/plugin install learn@agentskill-sh
```

**Claude Desktop / Claude Cowork**

Click **Plugins** → **Add marketplace** → paste `https://agentskill.sh/marketplace.json`

**Git (any platform)**

```bash
# Claude Code
git clone https://github.com/agentskill-sh/learn.git ~/.claude/skills/learn

# Cursor
git clone https://github.com/agentskill-sh/learn.git ~/.cursor/skills/learn
```

Or copy [SKILL.md](./SKILL.md) to your platform's skill directory.

[Full installation guide →](https://agentskill.sh/install)

---

## Usage

### Search for skills

```bash
/learn programmatic seo
/learn frontend react components
/learn marketing email sequences
```

Returns top 5 matches with name, author, install count, and security score.

### Install a specific skill

```bash
/learn @anthropic/seo-optimizer
/learn @vercel/nextjs-expert
```

### Context-aware recommendations

```bash
/learn
```

Run with no arguments — analyzes your project and suggests relevant skills.

### Trending skills

```bash
/learn trending
```

### Manage installed skills

```bash
/learn list              # Show all installed skills
/learn update            # Check for updates
/learn remove <slug>     # Uninstall a skill
```

### Rate a skill

```bash
/learn feedback seo-optimizer 5 "Excellent keyword clustering"
```

---

## How It Works

1. **Search** — Queries the agentskill.sh API
2. **Preview** — Shows security score, install count, and description
3. **Scan** — Performs local security analysis before writing files
4. **Install** — Writes the skill with version-tracking metadata
5. **Track** — Reports install for analytics (platform only, no PII)
6. **Self-update** — Checks if `/learn` itself needs updating via content SHA

Every installed skill includes a metadata header:

```yaml
# --- agentskill.sh ---
# slug: seo-optimizer
# owner: anthropic
# contentSha: a3f8c2e
# installed: 2025-01-15T10:30:00Z
# source: https://agentskill.sh/seo-optimizer
# ---
```

---

## Supported Platforms

| Platform | Directory |
|----------|-----------|
| Claude Code | `~/.claude/skills/learn/` |
| Cursor | `~/.cursor/skills/learn/` |
| GitHub Copilot | `.github/copilot/skills/learn/` |
| OpenAI Codex | `~/.codex/skills/learn/` |
| Windsurf | `~/.windsurf/skills/learn/` |
| Gemini CLI | `~/.gemini/skills/learn/` |
| Manus | Import via Settings → Skills |

[Full platform list →](https://agentskill.sh/install)

---

## API

Public API. No key required.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/agent/search` | Search skills |
| `GET /api/agent/skills/:slug/install` | Get skill content |
| `GET /api/agent/skills/:slug/version` | Version check |
| `POST /api/skills/:slug/install` | Track install |
| `POST /api/skills/:slug/agent-feedback` | Submit feedback |

---

## Learn More

- [Browse all skills](https://agentskill.sh) — 40,000+ skills by platform, category, and job role
- [What is an Agent Skill?](https://agentskill.sh/readme) — The complete guide to how skills work
- [Create your own skill](https://agentskill.sh/readme#how-to-create-a-skill) — Publish to agentskill.sh

---

## License

MIT

---

Built by [agentskill.sh](https://agentskill.sh)
