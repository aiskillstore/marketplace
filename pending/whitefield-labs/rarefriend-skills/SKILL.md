---
name: rarefriend-skills
description: >
  Cross-agent skills for Rarefriend personal CRM — search contacts, LinkedIn network,
  Google Calendar, Google Contacts, Microsoft Outlook email and calendar. Requires
  Rarefriend MCP. Use with Claude Code, Cursor, Codex, OpenClaw, Gemini CLI, or any
  Agent Skills-compatible client. Install per skill via npx skills add Whitefield-Labs/rarefriend-skills --skill <name>.
license: MIT-0
compatibility: Requires @rarefriend-ai/mcp and OAuth credentials from rarefriend.com. Agent Skills-compatible clients.
tags:
  - productivity
  - crm
  - networking
  - contacts
  - calendar
metadata:
  author: Rarefriend
  homepage: https://rarefriend.com
  repository: https://github.com/Whitefield-Labs/rarefriend-skills
  category: productivity
---

# Rarefriend Skills

Cross-agent skills for [Rarefriend](https://rarefriend.com) personal CRM. Each skill lives under `skills/<name>/SKILL.md`.

## Skills

| Skill                              | Purpose                                            |
| ---------------------------------- | -------------------------------------------------- |
| `network-and-relationship-manager` | Full CRM — contacts, notes, tags, all integrations |
| `manage-linkedin-network`          | LinkedIn connections search and management         |
| `schedule-with-google-calendar`    | Google Calendar scheduling and availability        |
| `organize-google-contacts`         | Google Contacts sync and management                |
| `schedule-with-outlook`            | Microsoft Outlook contacts and calendar            |
| `find-outlook-emails`              | Microsoft Outlook email search                     |

## Install

```bash
npx skills add Whitefield-Labs/rarefriend-skills --skill network-and-relationship-manager -y
```

See [README.md](./README.md) for all install commands and MCP setup.
