---
name: cargo-mcp
description: "Drive Cargo from its hosted MCP server at https://mcp.getcargo.io/mcp — connect a client, discover and price an action, run it over one record or a batch, poll it, and read workspace models, with no CLI install. Also when to call an MCP tool instead of shelling out to `cargo-ai`. Triggers: \"connect Cargo to Claude Desktop\", \"add Cargo to ChatGPT\", \"Cargo MCP server\", \"mcp.getcargo.io\", \"use Cargo without installing anything\", \"which Cargo tool do I call\", \"search_actions\", \"execute_action_batch\", \"MCP server is showing the wrong workspace\". Tools: whoami, search_actions, get_action_schema, execute_action, execute_action_batch, get_run, query_models. Skip when: you have a shell and the job is a workflow, a CDK deploy, warehouse SQL, or a mailbox — use the CLI skills; when publishing an MCP server out of your own workspace or attaching one to a Cargo agent — use cargo-ai."
version: "1.0.3"
compatibility: Requires the hosted Cargo MCP server at https://mcp.getcargo.io/mcp — OAuth (discovered from the 401 challenge) or a workspace-scoped API token as a bearer. The CLI is needed only for the jobs this skill routes away
homepage: https://github.com/getcargohq/cargo-skills
metadata:
  author: getcargo
  openclaw:
    requires:
      bins:
        - cargo-ai
    install:
      - kind: node
        package: "@cargo-ai/cli@latest"
        bins:
          - cargo-ai
    homepage: https://github.com/getcargohq/cargo-skills
---

# Cargo — the hosted MCP server

Cargo has two surfaces. The rest of this bundle documents the CLI. This one
documents `https://mcp.getcargo.io/mcp`, and, more usefully, **when to reach for
which.**

> **Three different things here are called MCP.** This skill is the **hosted
> server Cargo runs**, which you point a client at. Publishing a curated server
> *out of* your own workspace (`ai mcp-server create`, then `cargo-ai mcp` over
> stdio) and attaching somebody else's server *to* a Cargo agent
> (`release update-draft --mcp-clients`) are both
> [`cargo-ai`](../cargo-ai/SKILL.md). Check which one the user means before
> answering: the words are identical and the answers share nothing.

## Which surface

| The job | Surface |
| --- | --- |
| Run one action, or one action over many records | either; MCP if it is already connected |
| Find what Cargo can do, and what it costs | either (`search_actions` is the MCP half) |
| Read records off a model | either |
| Warehouse SQL, aggregates, joins | **CLI** ([`cargo-storage`](../cargo-storage/SKILL.md)) |
| Build or edit a multi-step workflow, tool, or play | **CLI** ([`cargo-orchestration`](../cargo-orchestration/SKILL.md)) |
| Workspace as code, plan and deploy | **CLI** ([`cargo-project`](../cargo-project/SKILL.md)) |
| Provision mailboxes, warm up, send | **CLI** ([`cargo-mailbox-management`](../cargo-mailbox-management/SKILL.md)) |
| Segments, connectors, content libraries, alerts, hosting, billing admin | **CLI** |
| No shell at all (ChatGPT, Claude Desktop, claude.ai, n8n) | **MCP**, and say plainly what is out of reach |

The rule underneath the table: **MCP is the runtime, the CLI is the platform.**
Thirteen tools cover discovering an action, running it, watching it finish, and
reading data back. Everything that *builds* something reusable is CLI only. An
agent holding both should prefer the CLI for anything the user will want to
re-run or version, and MCP for one-shot execution inside a conversation.

When the job routes to the CLI, this is the whole bootstrap:

```bash
npm install -g @cargo-ai/cli
cargo-ai login --email you@company.com   # emailed code, no browser; creates the account on first use
cargo-ai whoami                          # confirm the workspace before anything that spends
```

## Connect

The endpoint is `https://mcp.getcargo.io/mcp`, Streamable HTTP. An
unauthenticated request returns `401` with a `WWW-Authenticate` challenge
carrying `resource_metadata`, so an OAuth-capable client discovers the
authorization server, registers, and prompts the user with no configuration
beyond the URL. A `401` on first connect is the handshake, not a fault.

```bash
claude mcp add --transport http cargo https://mcp.getcargo.io/mcp
```

Any client taking a JSON block (Claude Desktop, Cursor, a project `.mcp.json`):

```json
{
  "mcpServers": {
    "cargo": {
      "type": "http",
      "url": "https://mcp.getcargo.io/mcp"
    }
  }
}
```

For CI, a headless agent, or a client with no OAuth, pass a workspace-scoped API
token from **Settings > API** instead. Read it from the environment; never inline
the value:

```json
{
  "mcpServers": {
    "cargo": {
      "type": "http",
      "url": "https://mcp.getcargo.io/mcp",
      "headers": { "Authorization": "Bearer ${CARGO_API_TOKEN}" }
    }
  }
}
```

**The tool list is not fixed.** The endpoint serves the platform tools below
plus whatever that workspace published with `defineMcpServer`, so two tokens can
see two different lists. Read the list you actually got rather than the one
documented here.

## The spine

```
whoami                 → which workspace am I in, how many credits
search_actions         → find the action, and read its cost
get_action_schema      → what inputs it takes
autocomplete_action    → resolve a field needing a picked id (HubSpot object type, Slack channel)
execute_action         │ one record
execute_action_batch   │ many records
get_run / get_batch    → poll while outcome is "executing"
```

For data: `list_models` → `describe_model` → `query_models`. Alongside,
`list_runs` lists recent ad-hoc runs, and `get_usage` breaks the last 7 days of
credit spend down by integration.

**Open every session with `whoami`.** The token binds the session to exactly one
workspace and there is no flag to override it. A session pointed at the wrong
workspace returns plausible, confidently wrong reads: the models are real and
the records are real, they just belong to somebody else. Name the workspace back
to the user before acting on anything.

**`search_actions` prices the work before you do it.** Each result carries
`credits[].cost` beside the `action` object you pass verbatim to everything
downstream:

```json
{
  "name": "Enrich person & find email",
  "credits": [{ "cost": 0.1, "type": "fixed" }],
  "action": {
    "kind": "connector",
    "integrationSlug": "aiArk",
    "actionSlug": "enrichPerson",
    "connectorUuid": "7bb944ec-0254-44bc-b0e4-8a56378e80cf"
  }
}
```

**Pass that `action` object exactly as it comes, with no `config` key.** Inputs
belong in `data` (single) or `records` (batch) — never in a `config`, which is a
*node's* configuration and has no meaning on a top-level action. Inputs
misplaced there are silently dropped and the action runs with none, so an
unexplained empty result is worth checking against this first.

`get_action_schema` takes the same pair: the action, plus an optional `data` for
the actions whose output depends on their inputs — a HubSpot object type or a
target sheet decides which fields come back. The CLI's
`orchestration action get-output-schema` behaves identically.

Four `kind` values come back: `connector` (a third-party integration), `native`
(a built-in platform operation), `tool` (a saved workflow in this workspace),
and `agent` (an AI agent in this workspace). Narrow a noisy catalog with the
`kind` and `integrationSlug` filters.

## Three ways this goes wrong

**Fanning out `execute_action`.** One call per record is slower, bills more, and
leaves nothing to inspect afterwards. `execute_action_batch` takes the same
`action` plus a `records` array, produces one batch object, and a finished batch
carries a download for its output CSV. The tool description says never to loop
it: take that literally.

**Spending before quoting.** Run **10–20 records** first, report the observed
cost and hit rate, then quote the full **record count** and **credit estimate**
and let the user approve. Hit rates on people data run 40 to 70 percent, so cost
per *usable* row is not the sticker price and is not knowable without the
sample. Full discipline:
[`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md).

**`query_models` mistaken for SQL.** It lists records off one model with a limit
and an offset. It does not aggregate, join, or filter by expression. Any
question shaped like "how many", "grouped by", or "joined to" is a CLI question
([`cargo-storage`](../cargo-storage/SKILL.md)). Say so, rather than pulling rows
and counting them yourself, which silently truncates at the limit.

## Anything that touches a person

The consent rules do not relax because the surface changed. A lawful basis, a
suppression check, and relevance to that person's job gate every step that
sources, enriches, or contacts someone. Bulk unsolicited messaging, purchased or
scraped lists, and consumer targeting are refused. The full text is
[`../cargo-gtm/references/acceptable-use.md`](../cargo-gtm/references/acceptable-use.md);
where no sibling skill is installed, the paragraph above binds on its own.

## Reporting back

Narrate and summarize; never paste raw JSON at a user. After a batch, give the
record count, the hit rate, the credits actually spent, and the download, in
that order.
