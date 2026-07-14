---
description: Use Atomic Mail in Dify from marketplace install to Agent/Workflow usage, including a practical workflow pattern and polling guidance.
---

# Dify Plugin

Atomic Mail is available in the Dify marketplace as a tool plugin for Dify
Agent and Workflow apps.

## How to install in Dify

1. Open **Plugins** in your Dify workspace.
2. Search for **Atomic Mail** in Marketplace and install it in the workspace.
3. Open the plugin settings and configure credentials.

Dify plugin behavior to keep in mind (official docs):

- Plugins are workspace-scoped (install once, usable in all apps in that
  workspace): [Dify Plugins docs](https://docs.dify.ai/en/use-dify/workspace/plugins)
- Most plugins need configuration after install (API keys, endpoints, or other
  provider settings): [Dify Plugins docs](https://docs.dify.ai/en/use-dify/workspace/plugins)

## First-run setup (recommended order)

After installing Atomic Mail, use the same operational order as MCP/AgentSkill:

1. `register` once (create/recover inbox credentials)
2. `help` (especially topic `cron` and `presets`)
3. `jmap_request` for inbox/send flows

Use `help` early and often inside the plugin tools to avoid guessing JMAP
details.

## Using Atomic Mail in Dify apps

### Agent app

- Add Atomic Mail tools in the app's tool section.
- Start with `register`, then call `jmap_request` for read/send actions.
- Keep `help` available so the agent can fetch topic guidance while running.

### Workflow app

1. Add a **Tool** node and choose an Atomic Mail action.
2. If prompted, select/create plugin credentials in node settings.
3. Map workflow variables to the tool inputs (`ops`, `ops_file`, `vars`).

Relevant Dify docs for tool-node behavior:

- [Tool Node](https://docs.dify.ai/en/use-dify/nodes/tools)
- [Tools in workspace](https://docs.dify.ai/en/use-dify/workspace/tools)

## Example workflow pattern

Use this minimal pattern for mailbox triage in Dify Workflow:

1. **Start/User Input** node (optional controls such as mailbox scope)
2. **Tool node** -> Atomic Mail `jmap_request` with `ops_file:
   "list_inbox.json"`
3. **LLM node** -> summarize messages and extract required follow-ups
4. **If/Else** -> route urgent vs non-urgent items
5. **Tool node** (optional) -> send response via Atomic Mail preset
6. **End** node

For Dify's general plugin-in-workflow style (install tool, authorize, wire
nodes), see:
[Workflow lesson: Enhance Workflows (Plugins)](https://docs.dify.ai/en/use-dify/tutorials/workflow-101/lesson-07)

## Hourly inbox polling after `register`

After `register`, arrange hourly inbox polling for the inbox. The important
rule is to run a full **agent turn** that uses `list_inbox.json`, not a raw
`jmap_request` one-shot cron job without agent reasoning.

If your runtime has no native agent cron/scheduler, ask the operator to set up
polling on a capable host, or use manual fetch reminders.

For exact prompt patterns and runtime-specific guidance, use Atomic Mail `help`
topic `cron`.
