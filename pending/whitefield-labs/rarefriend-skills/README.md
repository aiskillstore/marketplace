# Rarefriend Skills

Cross-agent skills for [Rarefriend](https://rarefriend.com) — your personal CRM.

Works with **Claude Code**, **Cursor**, **Codex**, **OpenClaw**, **Gemini CLI**, and any client that supports the [Agent Skills](https://agentskills.io/specification) format (`SKILL.md` + MCP).

Each skill is a focused `SKILL.md` that teaches your AI assistant a specific Rarefriend capability. Install only what you need, or install all six.

## Available skills

| Skill                              | What it does                                       |
| ---------------------------------- | -------------------------------------------------- |
| `network-and-relationship-manager` | Full CRM — contacts, notes, tags, all integrations |
| `manage-linkedin-network`          | Search and manage LinkedIn-synced connections      |
| `schedule-with-google-calendar`    | Google Calendar scheduling and availability        |
| `organize-google-contacts`         | Google Contacts sync and management                |
| `schedule-with-outlook`            | Microsoft Outlook contacts and calendar            |
| `find-outlook-emails`              | Microsoft email search and management              |

## Install skills

Use the [skills CLI](https://skills.sh) (works across supported agents):

**All skills:**

```bash
npx skills add Whitefield-Labs/rarefriend-skills --skill network-and-relationship-manager -y
npx skills add Whitefield-Labs/rarefriend-skills --skill manage-linkedin-network -y
npx skills add Whitefield-Labs/rarefriend-skills --skill schedule-with-google-calendar -y
npx skills add Whitefield-Labs/rarefriend-skills --skill organize-google-contacts -y
npx skills add Whitefield-Labs/rarefriend-skills --skill schedule-with-outlook -y
npx skills add Whitefield-Labs/rarefriend-skills --skill find-outlook-emails -y
```

**Just the main skill (recommended starting point):**

```bash
npx skills add Whitefield-Labs/rarefriend-skills --skill network-and-relationship-manager -y
```

> **Note:** The `--all` flag installs only the first skill due to a known CLI bug ([#1015](https://github.com/anthropics/claude-code/issues/1015)). Use `--skill <name>` for each one until the bug is fixed.

**Cursor:** skills install into `.cursor/skills/` or `~/.cursor/skills/` depending on scope.

**Claude Code / Codex:** global install via `npx skills add …` (same command).

**OpenClaw:** skills include `metadata.openclaw` blocks for ClawHub; install via ClawHub or copy from this repo.

## Requirements — Rarefriend MCP

Skills call Rarefriend via MCP. Connect once per client:

| Client                             | Setup                                                                                                                            |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Claude Code / Codex**            | `claude mcp add rarefriend -e RAREFRIEND_CLIENT_ID=your-id -e RAREFRIEND_CLIENT_SECRET=your-secret -- npx -y @rarefriend-ai/mcp` |
| **Cursor**                         | Add to `~/.cursor/mcp.json` — see [MCP repo](https://github.com/Whitefield-Labs/rarefriend-mcp)                                  |
| **Claude Desktop**                 | Add to `claude_desktop_config.json` — see [MCP repo](https://github.com/Whitefield-Labs/rarefriend-mcp)                          |
| **OpenClaw / Gemini CLI / others** | Run `npx -y @rarefriend-ai/mcp` with `RAREFRIEND_CLIENT_ID` and `RAREFRIEND_CLIENT_SECRET` in env                                |

Get credentials at [rarefriend.com](https://rarefriend.com) → Settings → Integrations → MCP.

Per-skill setup details: `skills/<name>/references/SETUP.md`.

## License

MIT
