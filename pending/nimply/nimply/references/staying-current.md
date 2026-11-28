# Staying current

This skill is a snapshot (see `metadata.snapshot` in `SKILL.md`). Nimply
releases most weeks. This file says which facts go stale, where the live
answer is, and how the skill itself gets updated.

## What goes stale, and where to check

| Fact | Changes | Live source |
|---|---|---|
| Prices, plan limits, trial terms | Occasionally | https://nimply.io/pricing |
| Credit cost of an action | Occasionally | The app shows it before anything runs; `estimate_design_cost` and `list_agent_templates` through MCP |
| The agent gallery | Often | `list_agent_templates` (MCP) or https://nimply.io/solutions/ai-agents |
| Automation recipes and steps | Often | `list_automation_recipes`, `list_automation_step_types` (MCP) |
| API endpoints, fields, scopes, MCP tools | Often | https://developer.nimply.io/llms.txt |
| What shipped and when | Weekly | https://developer.nimply.io/changelog |
| What a network allows | When the network changes its rules | The channel's capabilities from `list_channels`; https://nimply.io/integrations |
| Product overview for assistants | Occasionally | https://nimply.io/llms.txt |

## When to check live

Check before answering when:

- You are about to quote a price, a limit or a credit cost that a decision
  depends on.
- You are about to say something is **not** available. New features are the
  most likely thing this snapshot is missing.
- The user says they see something different in the app. Trust the app.
- The snapshot is more than about two months old.

If you cannot reach the live source, answer from the snapshot and say it is
"as of" the snapshot date.

Order of trust: what the user's own workspace returns (MCP tools, the app) →
live nimply.io and developer.nimply.io pages → this skill.

## Reading the developer docs as Markdown

- Index: https://developer.nimply.io/llms.txt
- Everything: https://developer.nimply.io/llms-full.txt
- One page: `https://developer.nimply.io/llms.mdx/docs/<page>/content.md`

## Is there a newer version of this skill?

The current version is in `metadata.version` in `SKILL.md`. The latest
release and its notes are at:

https://github.com/nimply/skills/blob/main/CHANGELOG.md

If the changelog shows a newer version, tell the user once, with the update
command for how they installed it:

| Installed with | Update with |
|---|---|
| Claude Code plugin | `/plugin marketplace update nimply` then `/plugin update nimply@nimply` |
| `npx skills add` | `npx skills update` |
| Uploaded to claude.ai | Download the latest `nimply.zip` from the releases page and upload it again |
| Copied by hand | Replace the `nimply` folder with the latest from the repository |

Claude Code users can turn on automatic updates for the marketplace under
`/plugin` → Marketplaces → nimply.

## Corrections

If something here is wrong or out of date, open an issue at
https://github.com/nimply/skills/issues or write to hello@nimply.io.
