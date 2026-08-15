---
name: valet
description: Use when the user wants to manage Valet agents, channels, connectors, organizations, or environment variables (secrets and plain config) via the valet CLI. Handles creation, deployment, linking, teardown, and all multi-step workflows. Also use when asked to "create an agent", "deploy an agent", "design an agent", "build me an agent that...", "create a connector", "set up a webhook", or anything involving the Valet platform or any request to create and deploy AI agents. Also use when asked to "learn from this session", "capture this workflow", "save this as an agent", "make this repeatable", or when writing SOUL.md files.
---

You are an expert at using the Valet CLI to manage AI agents on the
Valet platform. Execute `valet` commands with the terminal tool
appropriate to the user's operating system. Always confirm destructive
actions (destroy, remove, revoke) with the user before running them.

**Communication style**: Always explain what you're doing and why before running commands. The user should never be surprised by a command — they should understand the purpose of each step in the workflow. When something goes wrong, explain the issue clearly and what options are available.

## Installation

Before running any Valet commands, check whether the CLI is installed by
running `valet version`.

If `valet` is not installed, explain why it is needed and ask for permission
before installing it:

> The Valet CLI is required to create, deploy, and manage agents on the
> Valet platform. May I install the official release for your operating
> system?

Run the installer only after the user agrees.

On macOS or Linux, run the official installer:

```sh
curl -fsSL https://valet.dev/install.sh | sh
```

On Windows, run the official installer in PowerShell:

```powershell
irm https://valet.dev/install.ps1 | iex
```

After installation, run `valet version` again. If a Unix shell has not
reloaded its PATH yet, use `$HOME/.local/bin/valet` for the rest of the
current workflow. Do not reinstall the CLI.

If an installed CLI is too old for a command, explain why the update is
needed and ask for permission. After the user agrees, update it without
guessing how it was installed:

```
valet update
```

The updater preserves the installation method: official direct installs
self-update, while existing Homebrew installs continue through Homebrew.
If installation or updating fails, report the error and stop. Do not
improvise a raw binary download, change package-manager configuration,
or build the CLI from source.

## Prerequisites

After the CLI is installed, authenticate before any command that reads or
writes account state. Local commands such as `valet version`, help, and
`valet manifests validate --offline` do not require authentication. Explain
the login before starting it:

> Before we can create or manage agents, you need to be logged in to your Valet account. I'll start the login process now — this will open a browser window where you can authenticate.

Then run:

```
valet auth login
```

After login, verify the session with `valet auth whoami`. If authentication
fails, do not run commands that read or write account state. Local help and
offline validation remain available.

## Using the Built-in Help

The Valet CLI has extensive built-in help. **Use it proactively** when you need details about a command, flag, or feature not covered in this skill file:

```
valet help                          # Top-level help
valet help <command>                # Command-specific help (e.g. valet help channels)
valet <command> <subcommand> --help # Subcommand help (e.g. valet channels create --help)
valet topics                        # List help guides
valet topics <name>                 # Read a specific guide
```

Useful topic guides: `getting-started`, `agent-lifecycle`, `channels`, `connectors-overview` (covers both MCP server and command connectors), `resolution` (how the CLI picks `--agent` and `--org`).

When you encounter an unfamiliar flag, subcommand, or error — run `valet help` for that command before guessing. The CLI help is authoritative and up to date.


## Onboarding

### Scaffold a new agent project

Create a new agent project directory without running the full setup flow:

```
valet new <name> [--dir <path>]
```

Creates `<name>/` (or the path specified by `--dir`) containing `SOUL.md`,
`AGENTS.md`, `CLAUDE.md`, `valet.yaml`, `skills/`, and `channels/`. The
project is ready to edit. Update the generated files, then run
`valet agents create` to deploy it.

Flags:
- `--dir`: Directory to create the project in (default: `./<name>`)

## Core Concepts

- **Agent**: An AI agent defined by a `SOUL.md` file in a project directory. Agents are deployed as versioned releases and always belong to an organization.
- **Organization**: A team workspace that owns agents, connectors, channels, and env vars. All agents belong to an org — the default org is used when `--org` is omitted.
- **Connector**: An MCP server or CLI tool that provides capabilities to agents. Types: `mcp-server` (MCP tools via client) and `command` (CLI with secret injection). Transports: `stdio`, `sse`, `streamable-http`.
- **Channel**: A message entry point for agents. Types: `webhook`, `slack`, `telegram`, `heartbeat`, `cron`, `console`, `mcp`. Each channel has a session strategy and a prompt path.
- **Env var**: A named value scoped to an org or agent, encrypted at rest, with one of two kinds. **Secret** (the default) is a credential the agent can use through connectors and channels but never sees. **Plain** is agent-visible configuration delivered to the agent's environment, readable as `$NAME`. Either kind is referenced with `{{NAME}}` template syntax in connector and channel configurations. Agent-scoped env vars override org-scoped env vars of the same name.
- **Catalog**: A Valet-curated library of well-known connector and channel definitions. Browse with `valet connectors catalog` or `valet channels catalog`. Add from the catalog instead of configuring from scratch.
- **Shared resources**: Connectors, channels, and env vars can be scoped to an org and shared across agents. The pattern is: add from catalog (or create) at the org level, then attach to agents that need them. This maximizes reuse and simplifies credential rotation.
- **Channel file**: A markdown file at `channels/<channel-name>.md` that tells the agent how to handle incoming messages.

### Resolution

Most commands target an agent, an org, or both. The CLI resolves the target from three sources in strict precedence: **flags → project link → default org**. No mixing — if any flag is passed, project link and default org are ignored. In a linked directory (one with `.valet/config.json`), both agent and org come from the link. Otherwise the default org is used and the agent is unspecified.

Practical rules when writing valet commands:

- Pass `--org` explicitly whenever you know the target org and the user may belong to multiple orgs. Never assume the default org is set.
- When inside a linked project directory (e.g. after `valet agents create` or `valet agents link`), omit `--agent` / `--org` — the link provides both.
- If the user belongs to multiple orgs and a command needs disambiguation, `--agent X` alone may error (`agent exists in multiple orgs...`) — add `--org Y`.
- `valet agents link` requires `--org` for multi-org users and refuses to overwrite an existing link without `--force`.

Run `valet topics resolution` for the full rules. `valet auth whoami` surfaces the user's default org and any linked project so you can see what a bare command will target.

## Resource Creation Principles

These principles apply to all connectors, channels, and env vars. Follow this priority order every time:

1. **Catalog first**: Check `valet connectors catalog` or `valet channels catalog` before creating from scratch. Catalog entries handle transport, commands, and secret slots automatically.
2. **Reuse existing**: Check `valet connectors --org <org>` or `valet channels --org <org>` for resources that already provide what you need. Attach rather than duplicate.
3. **Org-scoped by default**: Always create connectors, channels, and env vars at the org level (`--org`). Org-scoped resources can be attached to any agent in the org, so a single `GITHUB_TOKEN` secret, `github` MCP connector, or `github-webhook` channel is reusable across every agent — no duplication, one place to rotate credentials. **Only drop to `--agent` when you have a concrete reason the resource cannot be shared** (e.g., per-agent rate limits, distinct credentials for the same service, a one-off test agent). When in doubt, use `--org` and attach. (Slack is a special case — see the Channels section.)
4. **Env vars at org level by default**: Setting an env var with `--org` makes it available to every org-scoped connector and channel, and org-scoped plain vars reach every agent in the org. Any agent that later attaches those connectors/channels automatically inherits access — no duplication. Agent-scoped env vars override org-scoped ones of the same name when a specific agent needs a different value.
5. **Verify before finalizing**: After the agent exists, test every
   secret-backed command with `valet exec` before treating the deployment as
   ready. See "Connector verification with valet exec."

## Agent Lifecycle

### Create an agent

The current directory must contain a `SOUL.md` file. This creates the agent, links the directory, deploys v1, and waits for readiness:

```
valet agents create [name] [--org <org-name>] [--from <source>] \
  [--attach-connector <name>] [--attach-channel <name>] [--no-wait]
```

Name is optional (auto-generated if omitted). When `--org` is omitted, the default org is used. The default org is set automatically when you create or join an org.

Sources for `--from`:
- **Current directory (default)** — uses the `SOUL.md` in the current directory
- **Local path** — `--from .` or `--from ./path/to/agent`
- **Git URL** — `--from github.com/user/repo` clones and deploys from a remote repo
- **Catalog** — `--from catalog:name` creates from a Valet-curated agent template

Use `--attach-connector` and `--attach-channel` to wire org-scoped resources to the agent at creation time (repeatable flags).

When using `--from <local-path>`, the CLI pushes your project source to code.storage without creating `.git` or `.gitignore` inside your directory. Agent directories nested in a monorepo can be staged and committed normally — no manual cleanup needed.

### Manifest inline channels (cron, heartbeat, and mcp)

When a `valet.yaml` manifest declares `cron`, `heartbeat`, or `mcp` channels using `type:` instead of `catalog:`, `valet agents create --from` automatically creates those channels during the deploy flow — no separate `valet channels create` step needed:

```yaml
channels:
  - type: cron
    schedule: "every day at 9am"
    timezone: America/New_York
  - type: heartbeat
    every: 5m
  - type: mcp
    description: exposes the agent as an MCP server
```

Use `type` (mutually exclusive with `catalog`) to declare inline channels. Supported fields: `schedule` (human-readable), `cron` (raw crontab expression), `every` (heartbeat interval), `timezone` (IANA timezone, default UTC). The `mcp` type takes none of these — it stands the agent up as an MCP server, materialized at deploy; mint a bearer token afterward with `valet channels token mint <channel> <name>` to connect a client. Run `valet agents create --help` for all options.

### Link a directory

```
valet agents link <name> [--org <org>] [--force]
```

Creates `.valet/config.json` pinning the current directory to the named agent in the given org. Subsequent commands auto-detect both agent and org from the link. Not needed if you created the agent from this directory.

- `--org` is **required** when you belong to multiple orgs. Single-org users can omit it; the CLI uses the one org.
- `--force` is required to replace an existing link in this directory. Without it, the command errors if `.valet/config.json` already exists.

### Deploy changes

After editing `SOUL.md`, channel files, or other project files:

```
valet deploy [-a <name>] [--org <org>] [--no-wait]
```

The target follows the standard resolver (flags → project link → default org). Inside a linked directory, both agent and org come from the link; passing `--agent` or `--org` overrides the link entirely.

The command reports progress through each step of the deploy pipeline. If the agent has pending connector installs or channel attachments that must be completed before deployment, the command exits with a clear error describing the required configuration.

### List agents

```
valet agents [--org <name> | -o <name>]
```

Lists agents in the default org, or the org specified with `--org` / `-o`. Errors with a helpful message if no default org is configured. Run `valet agents --help` for all options.

### Show agent details

```
valet agents info <name> [--org <org>]
```

Displays owner, current release, process state (including `idle`), channels, and connectors. Pass `--org` when the agent name is ambiguous across orgs you belong to; otherwise the server resolves the org from your memberships. Run `valet agents info --help` for all options.

### Agent drafts

Drafts are in-progress versions of an agent's code that haven't been promoted to the main branch yet. The `valet drafts` group provides full lifecycle management.

```
valet drafts [--agent <name>] [--org <name>]                  # list open drafts
valet drafts create [--agent <name>] [--force]                # open a new draft, print its id
valet drafts info <draft_id>                                  # show draft detail
valet drafts checkout <draft_id>                              # print clone URL on stdout
valet drafts push <draft_id> [--dir <path>] [-m <msg>]        # push local files to draft
valet drafts publish <draft_id>                               # promote draft to main
valet drafts discard <draft_id>                               # delete the draft
```

Use `drafts create` to open a standing draft you edit and review before
publishing. It prints the new draft id on stdout, which feeds `checkout`,
`push`, and `publish`. The agent comes from `--agent` or the linked
directory. An agent may have only one open draft, so `--force` discards an
existing one first. Confirm before using it. (`valet deploy` is the one-shot
alternative that creates, pushes, publishes, and deploys in one step.)

Use `drafts push` to ship local file edits to a draft branch without publishing. `--dir` defaults to the current working directory; `--message` (`-m`) sets the commit message (defaults to `"Update draft"`). If no files changed, the command exits 0 without creating a commit.

Run `valet drafts --help` for all options.

### Destroy an agent

```
valet agents destroy <name> [--org <org>]
```

Permanently removes the agent and all releases. Use `--org` to scope the lookup to a specific organization. Cannot be undone.

## Connectors

Connectors give agents access to MCP tools and CLI commands. **Default to `--org` when creating connectors** — an org-scoped connector can be attached to any agent in the org, so one `github` or `slack-mcp` connector serves every agent that needs it. Only use `--agent` when the connector is genuinely single-use. Follow the Resource Creation Principles above.

### Browse the catalog

```
valet connectors catalog
valet connectors catalog get <name>
```

The catalog contains Valet-curated connector definitions for well-known services (GitHub, Slack, Sentry, Linear, etc.). Each entry defines transport, command, and required secret slots. Optional slots are labeled `(optional)` in the output of `valet connectors catalog get <name>`.

### Create from the catalog (preferred)

```
valet connectors create <entry> [--org <org>] [--agent <agent>] [--as <name>]
```

Creates a connector from the catalog. Use `--as` to rename the instance (useful for multiple instances with different credentials). Required secrets must already be set.

Example:
```
valet env set GITHUB_TOKEN=ghp_abc123 --org acme
valet connectors create github --org acme
```

### Create a custom connector

Only use type-specific subcommands when the catalog doesn't have what you need:

```
# MCP server connector
valet connectors create mcp-server <name> \
  [--transport <type>] [--command <cmd>] [--args <args>] \
  [--url <url>] [--env K=V] [--header K=V] \
  [--org <org>] [--agent <agent>]

# Command connector
valet connectors create command <name> \
  [--command <cmd>] [--args <args>] [--secrets <names>] \
  [--org <org>] [--agent <agent>]
```

**Important**: `--args` takes comma-separated values. Use `{{NAME}}` to reference env vars (either kind) in `--env` and `--header` values.

```
# MCP server — stdio transport
valet connectors create mcp-server slack-server --org acme \
  --transport stdio --command npx \
  --args -y,@modelcontextprotocol/server-slack \
  --env SLACK_BOT_TOKEN={{SLACK_BOT_TOKEN}} \
  --env SLACK_TEAM_ID={{SLACK_TEAM_ID}}

# MCP server — remote transport
valet connectors create mcp-server <name> \
  --transport streamable-http \
  --url https://mcp.example.com/mcp \
  --header Authorization={{API_TOKEN}}
```

**Command connectors** wrap CLI tools. They require `--command` and accept `--secrets` (comma-separated secret names injected at runtime).

**Naming rule**: Name the connector after the CLI command the agent will type. The connector name becomes the executable on the agent's PATH, so it must match the command exactly. For tools installed via npx, the CLI command may differ from the npm package name — always use the CLI command.

```
# "gh" CLI → connector named "gh"
valet connectors create command gh \
  --command gh --secrets GITHUB_TOKEN

# "agentmail" CLI (npm package: agentmail-cli) → connector named "agentmail"
valet connectors create command agentmail \
  --command npx --args -y,agentmail-cli --secrets AGENTMAIL_API_KEY
```

**How command connectors surface to agents**: At runtime, the supervisor generates a wrapper script in `~/bin/` named after the **connector name**. The connector name becomes an executable on the agent's PATH that transparently injects secrets and runs the configured command. Only the connector name is on PATH — the agent runs `agentmail inboxes list`, not `npx agentmail-cli inboxes list` (which bypasses the wrapper and gets no secrets).

Run `valet connectors create --help` for all flags.

### Attach / Detach

Attach an org connector to an agent. Use `--as` for a custom alias:

```
valet connectors attach <name> [--agent <agent>] [--as <alias>]
valet connectors detach <name> [--agent <agent>]
```

### List and inspect

```
valet connectors [--org <org>] [--agent <agent>]
valet connectors info <name>
```

`valet connectors info` shows name, type, transport, command, args, URL, env, headers, secrets (for connectors with `--secrets` configured), and catalog origin.

### Destroy a connector

```
valet connectors destroy <name>
```

## Channels

Channels are message entry points for agents. **Default to `--org` when creating webhook channels** — one org-scoped webhook can be attached to multiple agents (each with its own `--events` filter), reusing the same webhook URL and signing secret. Use `--agent` when the channel truly belongs to one agent (cron and heartbeat schedules, Telegram bots).

**Slack is a two-step special case.** The org-level Slack channel (`valet channels create slack --org <org>`) authorizes Valet to create apps in your Slack workspace — one per org, a one-time prerequisite, not a reusable channel. Each agent that needs to appear in Slack then gets its **own** per-agent Slack channel (`valet channels create slack --agent <name>` or `valet channels attach slack --agent <name>`), which provisions a dedicated Slack app with its own bot identity. See "Create a Slack channel" below for the full flow.

Follow the Resource Creation Principles above — the catalog encodes signing schemes and service-specific behaviors for webhook channels.

**Always pass an explicit name when creating a channel that has a user-visible identity** (Slack `--bot-name`, Telegram bot name, etc.). Auto-defaults from the agent name are not reliable across orgs and surfaces — supply the flag yourself rather than letting it resolve server-side. For Slack specifically, this means passing `--bot-name <display-name>` on every `valet channels create slack --agent ...` and `valet channels attach slack --agent ...` call.

### Browse the catalog

```
valet channels catalog
valet channels catalog get <name>
```

The catalog contains Valet-curated channel definitions for well-known services (GitHub webhooks, Slack Events API, Stripe, etc.). Each entry defines signing scheme, event taxonomy, and required secret slots.

### Create from the catalog (preferred for webhooks)

```
valet channels create <entry> [--org <org>] [--agent <agent>] [--as <name>]
```

Creates a channel from the catalog. Use `--as` to rename the instance. If the catalog entry defines secret slots (e.g. `WEBHOOK_SECRET`), managed secrets are auto-generated and stored as secret-kind env vars. The `managed` field in the output is the secret name — use `valet env set` to rotate it.

Example:
```
valet env set GITHUB_WEBHOOK_SECRET=whsec_abc123 --org acme
valet channels create github-webhook --org acme
```

### Attach / Detach

Attach an org channel to an agent. Use `--events` to filter which event types are delivered:

```
valet channels attach <name> [--agent <agent>] [--as <alias>] [--events <types>] [--bot-name <name>]
valet channels detach <name> [--agent <agent>] [--force]
```

For Slack channels, `--bot-name` sets the bot display name (defaults to agent name). After attaching, the CLI opens a browser for the Slack OAuth install flow and shows the bot name and workspace.

For Slack channels, detaching destroys the per-agent Slack bot. The CLI
prompts for confirmation before proceeding. Use `--force` only after the user
explicitly confirms the destruction.

Example:
```
valet channels attach github-webhook --agent my-reviewer --events pull_request,issue_comment
valet channels attach slack --agent my-agent --bot-name my-bot
valet channels detach slack --agent my-agent
```

### Create a webhook channel

```
valet channels create webhook [name] \
  [--agent <agent-name>] [--org <org>] \
  [--verify <scheme>]
```

Verification schemes: `hmac-sha256` (default), `slack`, `stripe`, `svix`, `static-token`, `none`. Key flags: `--secret-name` (name of an existing secret from `valet env` to use instead of auto-generating; required for `slack`, `stripe`, and `svix`), `--signature-header` (not used with `slack` or `svix`), `--delivery-key-header`, `--delivery-key-path`, `--prompt`. For `hmac-sha256` and `static-token`, a managed secret is auto-generated if `--secret-name` is omitted. The `slack` scheme implements Slack's Events API signing protocol and handles `url_verification` challenges automatically. Run `valet channels create webhook --help` for full details.

The command prints the **webhook URL**, **signing secret**, and, when
applicable, **managed secret name**. Report the URL and managed secret name.
Do not repeat the raw signing secret in the response. Tell the user to copy
it from their terminal output and store it securely. If command output is
captured in the conversation, prefer `--secret-name` with a secret the user
set in their own terminal so the command does not generate a new value.

### Create a Slack channel

Slack is a two-step setup. Do both in order:

**Step 1 — Once per org (prerequisite):** create the org-level Slack channel. This authorizes Valet to create Slack apps in your workspace.

```
valet channels create slack --org <org>
```

The CLI prompts for a config token and refresh token (generate them at https://api.slack.com/apps under "Your App Configuration Tokens"), stores them encrypted, and records the workspace. There is exactly one org-level Slack channel per org — skip this step if the org is already connected (`valet channels --org <org>` will show a `slack` entry with the workspace name).

**Step 2 — Once per agent that needs to be in Slack:** create a per-agent Slack channel.

```
valet channels create slack [name] --agent <agent-name> [--bot-name <display-name>]
```

This provisions a dedicated Slack app for the agent, giving it a unique `@bot-name` in the workspace. If the org-level prerequisite is missing, the command errors and directs you to run Step 1 first. `--bot-name` sets the display name (defaults to agent name, resolved server-side). After creation the CLI opens a browser for the OAuth install flow, polls until install completes, and shows the bot name and workspace. Attaching an existing org's Slack to an agent (`valet channels attach slack --agent <name>`) is equivalent.

Run `valet channels create slack --help` for all flags.

### Create a Telegram channel

```
valet channels create telegram [name] \
  [--agent <agent-name>]
```

Creates a Telegram channel and outputs a deep link (`t.me/...`) for connecting the bot. Run `valet channels create telegram --help` for all flags.

### Create a heartbeat channel

```
valet channels create heartbeat [name] --agent <agent-name> --every 5m
```

Fires a prompt on a fixed interval. Run `valet channels create heartbeat --help` for all flags.

### Create a cron channel

```
valet channels create cron [name] --agent <agent-name> --schedule "every day at 9am"
# Or with a raw crontab expression:
valet channels create cron [name] --agent <agent-name> --cron "0 9 * * *"
```

Run `valet channels create cron --help` for all flags (`--timezone`, `--prompt`, etc.).

### List, inspect, destroy

```
valet channels [--org <org>] [--agent <agent>]
valet channels info <name>
valet channels destroy <name>
```

For Slack channels, `valet channels` shows the workspace name in the listing. Destroying an org-level Slack channel cascades — all per-agent Slack bots are destroyed first, then the org Slack connection is removed.

## Environment Variables

Env vars are named values scoped to an org or agent, managed with the `valet env` command family. Every env var has one of two kinds:

- **Secret** (the default): credentials (API tokens, service keys, signing secrets) used by connectors and channels at runtime. The agent can invoke tools that depend on secrets but never sees the values — they flow through connectors and channels, not through the agent's environment, and list output masks them.
- **Plain** (`--plain`): configuration the agent should read directly — a region, a base URL, a customer identifier. Plain values are delivered to the agent's unix environment, readable as `$NAME` from bash and from code the agent writes, listed by name in the agent's system prompt, and displayed in list output.

Reference an env var of either kind in connector or channel configuration with `{{NAME}}` syntax. Names are unique per scope across both kinds, and a var's kind cannot be changed in place — unset it and set it again with the new kind.

**Default to `--org` when setting env vars.** Org-scoped env vars are available to every org-scoped connector and channel — and org-scoped plain vars reach every agent in the org — so one `GITHUB_TOKEN` or `REGION` serves every agent that needs it, and rotation is a single `valet env set` away. Use `--agent` only when an agent needs a different value for the same name (e.g., a distinct API key per agent); the agent-scoped var overrides the org-scoped one.

**When an existing connector works but one agent needs different credentials, override the secret at the agent level — do NOT create a new connector.** This is the canonical fix for any "the org-scoped token is wrong for this agent" situation: read-only org token vs. a read-write token for one agent, different tenant/account, narrower or broader scopes, separate rate-limit budget. Run `valet env set <SAME_NAME>=<value> --agent <agent>` and the existing org connector will pick up the agent-scoped value automatically. Spinning up a parallel connector is almost always the wrong answer — it duplicates configuration and forfeits the org-level catalog wiring.

**NEVER ask the user for secret values within the LLM session.** Direct them to run `valet env set NAME=VALUE --org <org>` in their terminal and wait for confirmation before proceeding. Plain values are not credentials — you may set those directly yourself.

### Set env vars

```
valet env set <NAME=VALUE>... [--plain] [--org <org>] [--agent <agent>] [--no-wait]
```

Kind defaults to secret; pass `--plain` for values the agent should read from its environment. All vars in one invocation share a kind, and the command echoes the kind it applied (`Set REGION (plain)`). Scope follows the resolver: `--agent` / `--org` flags, then project link, then default org (org-scoped). Setting an env var triggers a redeploy so the change takes effect — agent-scoped changes redeploy that agent (the CLI waits for readiness; use `--no-wait` to skip), org-scoped changes redeploy the affected agents in the org. Reserved names (`VALET_*`, `LD_*`, `PATH`, `HOME`, and other runtime-owned names) are rejected for plain vars.

Give an agent configuration with a plain var:

```
valet env set REGION=us-east-1 --plain --agent my-agent
```

After the redeploy the agent reads `$REGION` in bash and in any code it writes, and the name appears in its system prompt.

### {{NAME}} template syntax

Use `{{NAME}}` in connector `--env`, `--header`, or `--url` values to reference an env var of either kind. Templates are resolved at deploy time and can appear anywhere in a value:

```
--url https://{{DB_HOST}}/api
--header "Authorization=Bearer {{API_TOKEN}}"
--env SLACK_BOT_TOKEN={{SLACK_BOT_TOKEN}}
```

When directing the user to set secrets, **always tell them what format the value should be in**, including any prefix the service expects.

### List and unset

```
valet env [--agent <name> | --org <name>]
valet env unset <NAME> [--agent <name> | --org <name>] [--force]
```

`valet env` lists the effective environment: each var's kind and scope,
plain values inline, secret values masked, and an `overrides org` annotation
when an agent-scoped var shadows an org-scoped one. Unsetting a referenced
var fails with an error naming the dependent connector or channel. Use
`--force` only after the user confirms those dependents may break.

## Organizations

Organizations own agents, connectors, channels, and env vars. All agents belong to an org.

```
valet orgs create <name>           # Create a new org
valet orgs                         # List your orgs
valet orgs info <name>             # Show org details
valet orgs destroy <name>          # Delete an org
valet orgs members <name>          # List members
valet orgs invite <name> <email>   # Invite a member
valet orgs join <code>             # Accept an invitation
valet orgs leave <name>            # Leave an org
valet orgs remove <name> <email>   # Remove a member
valet orgs revoke <name> <email>   # Cancel an invitation
valet orgs set-default <name>      # Switch the default org
```

**Org tips**: The default org is set automatically when you create or join an org — you don't need `--org` on every command when targeting the default. Inside a linked project directory, the link's org takes precedence over the default (see `valet topics resolution`). Use `valet orgs set-default <name>` to switch the default after joining multiple orgs. Run `valet orgs set-default --help` for details.

## Other Commands

| Command | Purpose | Help |
|---------|---------|------|
| `valet run <prompt>` | Send a single prompt to an agent; supports `--org` | `valet help run` |
| `valet console` | Start an interactive REPL with an agent; supports `--org` and `--resume <session-id>`. Surfaces actionable stream errors (`timed out; try again?`, `rate limited; try again in a moment`, `could not reach server; check your network`) with the raw detail appended after the prefix | `valet help console` |
| `valet exec` | Run a command with secrets injected into its environment | `valet help exec` |
| `valet logs [-n <num>]` | Stream live logs; shows 100 historical lines by default (`-n 0` for live only); supports `--org` | `valet help logs` |
| `valet ps` | List agent processes (can show `idle` state); supports `--org` | `valet help ps` |
| `valet ps scale` | Change an agent's model or process count (see [Scaling](#scaling)) | `valet help ps scale` |
| `valet drains` | Configure log drains (OTLP HTTP) | `valet help drains` |

## Scaling

`valet ps scale` is how an agent's **model** is changed. There is no
separate model command, and the manifest does not carry one — if the
user asks to switch an agent to a different model, this is the answer.

```
valet ps scale agent=glm-5.2                 # Change model, keep the count
valet ps scale agent=0                       # Stop the agent, keep the model
valet ps scale agent=1                       # Start it again
valet ps scale agent=claude-sonnet-5:1       # Set both at once
```

Pass a single `agent=<value>` pair. The right side is a model ID, a
process count, or `model:count`. Changing one preserves the other, so
`agent=glm-5.2` does not stop a running agent and `agent=0` does not
reset its model.

**An agent's count is 0 or 1 today.** There is no horizontal scaling of
agents, so `agent=2` is not a way to add capacity.

Run `valet help ps scale` for the current model list rather than
quoting one from memory — the set changes, and a stale model ID fails
the command.

Scaling bounces the affected containers so the new setting takes effect
on restart. It is not a redeploy: the release is untouched.

**Sites have no processes and cannot be scaled at all.**

## Sessions

Sessions persist conversation state so the user can disconnect and come back. Each `valet console` invocation writes to a session, and the same session can be resumed later or deleted.

### Resume a session

```
valet console [-a <agent>] --resume <session-id>
```

Reopens the console on an existing session. The transcript is replayed locally and the agent continues where it left off. Use the session ID printed when the console started, or look it up via the dashboard. Without `--resume`, `valet console` starts a new session.

### Delete a session

```
valet sessions delete <session-id> [-a <agent>]
```

Removes a session and its transcript. Destructive — confirm before running. Run `valet sessions --help` for the full session subcommand list.

## Using valet exec

`valet exec` is the **only way** to run local commands with Valet-managed env
vars injected. It fetches both kinds. Values live in the control plane, not
in your local shell. After the agent exists, test secret-backed commands
before treating its deployment as ready.

There are two modes:

### Connector mode (no `--`)

The first argument is looked up as a connector name. If a `command` connector is found, its secrets are fetched and injected, and the connector's configured command is executed. Extra arguments are appended after the connector's configured args:

```
# Run the "gh" command connector (looks up connector named "gh")
valet exec -a my-agent gh pr list

# Use linked agent from current directory
valet exec gh pr list
```

### Explicit secrets mode (with `--`)

Secret names are passed as a comma-separated positional argument before `--`. The command and its arguments follow after `--`:

```
valet exec [-a <agent>] SECRET[,SECRET...] -- command [args...]
```

Fetches the requested secret values and executes the given command with those secrets injected into the environment. The current process is replaced by the command.

```
# Run gh with GITHUB_TOKEN injected as an env var
valet exec -a my-agent GITHUB_TOKEN -- gh pr list

# Pass a secret as a CLI argument using {{}} syntax
valet exec -a my-agent API_KEY -- curl -H "Authorization: Bearer {{API_KEY}}" https://api.example.com

# Multiple secrets in one command
valet exec -a my-agent GITHUB_TOKEN,SLACK_TOKEN -- \
  sh -c 'test -n "$GITHUB_TOKEN" && test -n "$SLACK_TOKEN"'
```

Flag: `--agent` or `-a`: Agent that owns the secrets (uses linked agent if omitted). Run `valet exec --help` for full details.

### Template syntax for CLI arguments

Use `{{SECRET_NAME}}` in command arguments to substitute secret values directly. This is useful for tools that accept credentials as flags or in URLs rather than reading from the environment. Works in both modes.

### Running MCP servers locally

To test an MCP server that requires secret-backed environment variables:

```
valet exec -a my-agent SLACK_BOT_TOKEN,SLACK_TEAM_ID -- \
  npx -y @modelcontextprotocol/server-slack
```

Without `valet exec`, the MCP server would start without the required tokens and fail to authenticate.

### Why valet exec is required

Regular shell commands (`curl`, `npx`, `node`, etc.) cannot access Valet secrets. This will **not** work:

```
# WRONG — $API_KEY is not set in your shell
curl https://api.example.com/data?key=$API_KEY

# CORRECT — valet exec injects the secret (explicit secrets mode)
valet exec -a my-agent API_KEY -- curl https://api.example.com/data?key={{API_KEY}}

# OR use connector mode if you have a command connector configured
valet exec -a my-agent my-connector-name
```

The same applies to any connector command. If its `--command` or `--args`
reference secret-backed environment variables, test the exact command
through `valet exec` before treating the deployment as ready.

## Connector verification with valet exec

After the initial `valet agents create` deploy, test every command that
requires secrets with `valet exec`. This catches authentication failures,
wrong secret names, malformed URLs, and missing dependencies before you
treat the deployment as ready. Deploy any resulting source fix before the
end-to-end test.

### What to test

Any connector command that references secrets in its `--env` flags should be verified locally. Reproduce the exact command the connector will run, wrapping it in `valet exec`:

```
# If the connector is defined as:
valet connectors create github-server \
  --transport stdio \
  --command npx \
  --args -y,@modelcontextprotocol/server-github \
  --env GITHUB_PERSONAL_ACCESS_TOKEN={{GITHUB_TOKEN}}

# Test the underlying command locally:
valet exec -a my-agent GITHUB_TOKEN -- \
  npx -y @modelcontextprotocol/server-github
```

For remote connectors (SSE/streamable-http) with secret-backed headers or URLs, test with curl:

```
# If the connector uses --header Authorization={{API_TOKEN}} --url https://mcp.example.com/mcp
# Test the endpoint is reachable and the token works:
valet exec -a my-agent API_TOKEN -- \
  curl -s -o /dev/null -w "%{http_code}" -H "Authorization: {{API_TOKEN}}" https://mcp.example.com/mcp
```

Do not test a webhook by sending an arbitrary request to a production
endpoint. Use the provider's documented test-event flow or a dedicated test
endpoint. If either action can trigger real work, get the user's approval
first.

### Verification checklist

Before running `valet deploy`, confirm:

1. All env vars are set: `valet env --agent <name>` and `valet env --org <org>` list every name referenced by connectors
2. Each connector's command succeeds locally via `valet exec`
3. Any secret-backed URLs resolve and authenticate correctly

Do not treat the setup as complete until all `valet exec` tests pass.

## Common Workflows

### Full agent setup (org-first, preferred)

Follow Resource Creation Principles — set up org-scoped resources first, then attach to the agent.

1. Direct the user to set org-scoped secrets in their terminal:
   ```
   valet env set GITHUB_TOKEN=<their-token> --org acme
   ```

2. Add connectors from the catalog at the org level:
   ```
   valet connectors catalog
   valet connectors create github --org acme
   ```

3. If no catalog entry exists, create a custom connector at the org level:
   ```
   valet connectors create mcp-server my-tool --org acme \
     --transport stdio \
     --command npx \
     --args -y,@example/mcp-server \
     --env API_KEY={{API_KEY}}
   ```

4. Add channels from the catalog at the org level (for webhooks):
   ```
   valet channels create github-webhook --org acme
   ```

5. Write the channel file at `channels/<channel-name>.md` when the agent
   needs one. See "Writing Channel Files."

6. Create the agent and attach org resources. This command performs the
   initial deploy:
   ```
   cd my-agent-project
   valet agents create my-agent --org acme \
     --attach-connector github \
     --attach-channel github-webhook
   ```
   Or attach after creation:
   ```
   valet connectors attach github --agent my-agent
   valet channels attach github-webhook --agent my-agent --events pull_request
   ```

7. Verify each connector command with `valet exec` after the agent exists:
   ```
   valet exec -a my-agent GITHUB_TOKEN -- \
     npx -y @modelcontextprotocol/server-github
   ```
   The create command already performed the initial deploy. Fix any
   authentication, dependency, or command failure before the final deploy.

8. Deploy any fixes made after verification:
   ```
   valet deploy
   ```

9. Validate end-to-end with the interactive test loop below.

### One-off agent setup (agent-scoped)

Use this flow **only** when you have a concrete reason an agent cannot share resources — e.g., distinct credentials for the same service, a throwaway test agent, or per-agent rate limits. For everything else, prefer the org-first flow above. Standalone setup:

1. Create the agent (pass `--org` if the user belongs to multiple orgs; omit for single-org users):
   ```
   cd my-agent-project
   valet agents create my-agent --org acme
   ```

2. Set agent-scoped secrets and create agent-scoped connectors:
   ```
   valet env set API_KEY=<value> --agent my-agent
   valet connectors create mcp-server my-tool --agent my-agent \
     --transport stdio --command npx \
     --args -y,@example/server \
     --env API_KEY={{API_KEY}}
   ```

3. Create channels, channel files, deploy, and test as above.

### Interactive test loop (mandatory for first-time channel setup)

1. Start streaming logs in the background:
   ```
   valet logs > /tmp/valet-test-<agent-name>.log 2>&1
   ```
   (Run via Bash with `run_in_background: true`.)

2. Ask the user to trigger the channel (send the email, push to GitHub, etc.). Be specific about what they need to do.

3. Wait for the user to confirm the trigger completed.

4. Stop the background log stream and read the log file.

5. Review the logs:
   - **Healthy**: Few turns, `mcp_call_tool_start`/`mcp_call_tool_done` pairs, `dispatch_complete`.
   - **Unhealthy**: Many turns with only built-in tools (agent looping), no `mcp_call_tool_start` (can't find tools), no `dispatch_complete` (timeout/stuck).

6. If problems, fix SOUL.md or channel prompt, redeploy, and repeat. Each change triggers a full VM reboot — wait for it to complete and stream fresh logs before evaluating.

### Teardown (order matters)

Detach org resources first, then destroy agent-scoped resources, then the agent:
```
# Detach org resources (they remain available for other agents)
valet connectors detach github --agent my-agent
valet channels detach github-webhook --agent my-agent

# Destroy agent-scoped resources
valet channels destroy <agent-channel>
valet connectors destroy <agent-connector>

# Destroy the agent
valet agents destroy <agent-name>
```

### Debugging

```
valet agents info my-agent                   # Check state, channels, connectors
valet agents info my-agent --org my-org      # Specify org when looking up by name
valet logs --agent my-agent                  # Stream live logs (last 100 lines, then live)
valet logs --agent my-agent -n 0             # Live logs only, skip history
valet ps restart -a my-agent                 # Restart without redeploying
valet ps restart -a my-agent --org my-org    # Restart with explicit org
valet ps scale agent=0                       # Stop the agent (model preserved)
valet ps scale agent=1                       # Start it again
```

## Designing a New Agent

**When to use**: The user asks to "build an agent", "create an agent from scratch", "design an automation", or provides skill/MCP URLs to assemble into an agent.

Be curious, confirmatory, and opinionated. Suggest improvements, anticipate edge cases, and help refine the idea. **7 questions max, fewer if sufficient.**

### Step 1: Parse the user's input

The user's prompt may contain a description of what they want and/or URLs pointing to skills, tools, or MCP servers. Extract both.

| URL type | Pattern | How to fetch |
|----------|---------|--------------| 
| GitHub SKILL.md | `github.com/.../SKILL.md` | Convert to `raw.githubusercontent.com/...`. Explore parent dir for siblings. |
| GitHub directory | `github.com/.../tree/...` | Fetch listing. Look for SKILL.md, README.md. |
| skills.sh listing | `skills.sh/<name>` | Fetch page for description + source repo URL. Follow source link. |
| MCP server README | npmjs.com, GitHub, PyPI | Extract server name, tools, config/install instructions. |

For each URL: fetch with `WebFetch`, identify type, discover the full package, extract name/description/tools/dependencies/config. Check if equivalent tools already exist via `ToolSearch` — **always prefer existing tools**.

If no URLs, proceed directly to the interview.

### Step 2: Interview

Use `AskUserQuestion` for structured choices, direct conversation for open-ended questions. Track question count — stop and build once you have enough.

**Important: When using `AskUserQuestion`, the `question` field must be a complete, clear question sentence that ends with a question mark.** The user sees this question text prominently — it's the primary thing they read to understand what you're asking. Bad: "Trigger" or "Trigger type". Good: "How should this agent be triggered?" Option labels should be short (1-5 words) with the description providing detail.

**Question 1 — Confirm understanding + trigger type:**

Present a concise summary of the agent you will build based on what you understood from the initial prompt:
- If URLs provided: present what you fetched — names, descriptions, capabilities and combine with any instructions to suggest the agent you will build.

Ask about the trigger if not already clear:
- Webhook — event-driven (email, push, form submission)
- Prompt — user sends a message via `valet run` or console

**Questions 2–6 — Adaptive deep-dive**

Be opinionated: suggest better approaches, flag automatable manual steps, raise obvious edge cases. **Stop early** if 1–3 questions gives a clear picture of the user intent.

Some example topics you might need to understand better are:

* Tool/skill discovery (see below) — skip if URLs already provided the tools
* Workflow clarification — decision points, branching logic
* Output format — where/how results are delivered (Slack channel, email, file, etc.)
* Edge cases and guardrails — suggest failure modes, ask about constraints

#### Tool discovery

When the user mentions a capability not covered by imported URLs, search in this order (per Resource Creation Principles): catalog (`valet connectors catalog`) → existing org connectors → `ToolSearch` for local MCP tools → `WebFetch` on `skills.sh` → `WebSearch` on PulseMCP/Smithery. If no match, the agent can use built-in tools or it remains a manual step.

### Step 3: Present the plan and confirm

After the interview and any tool/skill discovery, **stop and present a clear plan to the user before building anything**. The plan sets expectations about what will happen on their machine, what the agent will do automatically, and what the user will need to do manually. This gives the user a chance to change direction before any work begins — especially important when external setup (API credentials, third-party configuration, cloud consoles) is involved.

Present the plan in this format:

```
Here's the plan for your <agent-name> agent:

**What I'll create on your machine:**
- A project directory with SOUL.md defining the agent's identity and behavior
- [Channel files for <channel-type> triggers, if applicable]
- [Skill files for <connector> usage, if applicable]

**What I'll set up on the Valet platform:**
- The agent itself (registered and deployed in org <org-name>)
- [Org connectors: <list each, noting if from catalog or custom>]
- [Org channels: <list each, noting if from catalog or custom>]
- [Agent-scoped resources, if any: <list with reason they're not org-scoped>]

**What you'll need to do:**
- [Set secrets in your terminal (org-scoped by default): <list each secret and what it's for>]
- [External setup: <specific steps, e.g., "Create a Google Cloud project,
  enable the Gmail API, and generate OAuth credentials — I'll walk you
  through this when we get there">]
- [Any other manual steps the user must perform]

[If external setup is complex, call it out explicitly: "The <service>
integration requires some setup on your end — <brief description of
what's involved>. If that feels like too much, we could <alternative
approach> instead."]

Want to proceed with this plan, or would you like to adjust anything?
```

**Guidelines for the plan:**

- **Be specific about user obligations.** Don't say "set up API credentials" — say "create a Slack app at api.slack.com, add the `chat:write` scope, install it to your workspace, and copy the Bot User OAuth Token." The user needs to know what they're signing up for.
- **Flag complexity honestly.** If an integration requires navigating a cloud console, setting up OAuth, configuring webhooks on a third-party service, or any multi-step external process — say so clearly. This is often where users decide to change approach.
- **Offer alternatives when they exist.** If the user's goal can be achieved a simpler way (different service, fewer integrations, manual step instead of automation), mention it.
- **Wait for explicit confirmation.** Do not proceed to Step 4 until the user says yes. If they want changes, revise the plan and present it again.

### Step 4: Generate the agent

1. Scaffold the project with `valet new <agent-name>`.
2. Write `SOUL.md` using the "Writing SOUL.md" guidance below.
3. Write channel files when the agent uses webhooks. See "Writing Channel
   Files."
4. Write custom skills under `skills/<name>/SKILL.md` when the agent needs
   local procedural knowledge.
5. Fill in the generated `valet.yaml` metadata. Add catalog setup fields only
   when the user asked for the dashboard or catalog workflow.
6. Update the generated `AGENTS.md` last, after every setup requirement is
   known. This keeps the deployed release and future setup instructions in
   sync.
7. Run the validation checklist:
   - [ ] SOUL.md exists with non-empty Purpose and Workflow
   - [ ] Guardrails has both Always and Never subsections
   - [ ] No hardcoded IDs that should be `<placeholder>`s
   - [ ] Channel files have Scope section if webhook-driven
   - [ ] Channel files include webhook payload location instruction
   - [ ] No secrets or API keys in any file
   - [ ] AGENTS.md documents all setup without containing secret values
   - [ ] `valet manifests validate` passes
8. Direct the user to set secrets at the org level (preferred) or agent level:
   ```
   valet env set SECRET_NAME=<value> --org <org-name>
   ```
   For non-sensitive configuration the agent should read directly (a region, a base URL, a team name), set a plain var — the agent reads it as `$NAME` after deploy:
   ```
   valet env set NAME=<value> --plain --org <org-name>
   ```
9. Set up connectors — **check the catalog first**:
   ```
   valet connectors catalog
   valet connectors create <entry> --org <org-name>
   ```
   Only create custom connectors if no catalog entry exists:
   ```
   valet connectors create mcp-server <name> --org <org-name> \
     --transport stdio \
     --command <cmd> --args <args> \
     --env KEY={{SECRET_NAME}}
   ```
10. Set up channels — **check the catalog first** for webhook channels:
   ```
   valet channels catalog
   valet channels create <entry> --org <org-name>
   ```
   Or create directly:
   ```
   valet channels create webhook <channel-name> --agent <agent-name>
   ```
11. Create and deploy the agent, attaching org resources:
   ```
   cd <agent-name>
   valet agents create [name] --org <org-name> \
     --attach-connector <connector> \
     --attach-channel <channel>
   ```
12. Verify each connector command locally with `valet exec` after the agent
    exists:
    ```
    valet exec -a <agent-name> SECRET_NAME -- <cmd> <args>
    ```
    The create command performed the initial deploy. Fix any failures before
    deploying the corrected configuration.
13. Run `valet deploy` when verification required source changes.
14. If the agent has channels, run the interactive test loop. See
    "Interactive test loop" under Common Workflows.

### Design edge cases

| Case | Handling |
|------|----------|
| No URLs, pure description | Standard confirmatory interview. |
| URLs only, no description | Present imported capabilities, ask what the agent should do with them. |
| Mix of URLs and description | Fetch URLs first, then interview with imported context. |
| URL unreachable | Report error. Ask for alternative URL or direct paste. |
| Name collision | Run `valet agents` to check. Ask to choose a different name. |
| MCP server needs API keys | Document in SOUL.md Environment Requirements. Direct user to `valet env set`. Never ask for actual values. |

## Learning from the Current Session

**When to use**: The user says "save this as an agent", "capture this workflow", "learn from this session", or "make this repeatable".

### Step 1: Locate the session log

1. Convert the current working directory to the Claude projects path:
   `~/.claude/projects/-<cwd-with-slashes-replaced-by-dashes>/`
   Example: `/Users/me/Developer/my-project` → `~/.claude/projects/-Users-me-Developer-my-project/`
2. Find the active session log:
   ```bash
   ls -t ~/.claude/projects/-<path>/*.jsonl | head -1
   ```

### Step 2: Parse the session

Read the JSONL file with the Read tool. Each line is a JSON object. Extract:

- **User prompts**: Entries where `type` is `"user"` and `message.content` is a string. Capture the text (truncate to 500 chars each).
- **MCP tool usage**: Entries where `type` is `"assistant"` and `message.content` contains objects with `type: "tool_use"`. If the tool `name` starts with `mcp__`, split on `__` to get server and tool name (e.g., `mcp__slack__post_message` → server: `slack`, tool: `post_message`).
- **Skill invocations**: Tool calls where `name` is `"Skill"` — extract `input.skill` for the skill name.
- **Built-in tools**: All other tool call names (Read, Write, Edit, Bash, Glob, Grep, etc.).
- **Corrections**: User messages containing "no,", "don't", "instead", "actually", "wrong", "not that", "change", "stop", "undo", "revert" — these indicate the user changed direction.
- **Stop point**: Stop parsing when you encounter a Skill tool call with `input.skill` matching the learn/capture trigger. Exclude everything after.

For large sessions (>20 user prompts): sample the first 3 and last 3 user prompts to keep context manageable.

Also check `~/.claude/projects/<project-path>/sessions-index.json` for `summary` and `firstPrompt` fields matching the session ID (derived from the JSONL filename).

If the session is empty (no user prompts besides the learn trigger), inform the user and stop.

### Step 3: Present analysis and interview

Show the analysis:

```
Session Analysis:
- Objective: [summary from first prompt or sessions-index]
- User prompts: N messages
- MCP tools used: [server names + tool counts]
- Skills invoked: [names]
- Built-in tools: [names]
- Corrections detected: N
```

Ask clarifying questions (skip any with obvious answers from the session):

1. **Trigger**: What should invoke this agent? Propose a draft based on the first user prompt — webhook or prompt?
2. **Scope**: Does the extracted objective + tool list capture the full scope, or should it be narrowed/expanded?
3. **Corrections**: Surface each detected correction and ask whether the agent should always follow the corrected approach.
4. **Name**: Propose a kebab-case name (<64 chars). Let the user confirm.

### Step 4: Present plan and confirm

Follow the same confirmation flow as "Designing a New Agent" Step 3. Present what will be created, what platform resources will be set up, and what the user needs to do. Wait for confirmation.

### Step 5: Generate the agent

Follow the same generation flow as "Designing a New Agent" (Step 4 above), but source content from the session:

- **Purpose**: From user prompts + corrections + interview refinements
- **Workflow phases**: From the chronological sequence of tool calls, grouped by logical purpose (e.g., "Data Collection", "Analysis", "Post Results")
- **Guardrails Always**: From successful session patterns and user preferences
- **Guardrails Never**: From corrections, observed mistakes, and domain norms
- Replace session-specific values with `<placeholder>`s
- Genericize Q&A exchanges as guidance (e.g., "if ambiguous, prefer X")
- **Last step**: Write `AGENTS.md` in the project root (see "Writing AGENTS.md")

### Edge cases

| Case | Handling |
|------|----------|
| Empty session | Inform user: "This session is empty — nothing to capture." Stop. |
| No MCP tools used | Skip connector creation. Agent uses only built-in tools. |
| Long session (>500 entries) | Sample first 3 + last 3 user prompts. Summarize tool usage by frequency. |
| Many corrections | Present each one. Let the user decide which to encode as guardrails. |

## Writing SOUL.md

SOUL.md defines the agent's identity and behavior. It's the only required file.

### Template

```markdown
# <Agent Title>

## Purpose

<2-3 sentences: what this agent does and why. Name the specific tools, inputs, and outputs.>

## Personality

<3-4 traits matching the agent's domain. Skip for simple utility agents.>

- **<Trait>**: <Description>

## Workflow

### Phase 1: <Phase Name>

1. <Concrete step referencing specific tool names>
2. <Next step>

### Phase 2: <Phase Name>

1. <Steps>

## Guardrails

### Always
- <Positive constraint>

### Never
- <Negative constraint>
```

### Optional sections

Add as needed: **Target Channel**, **Environment Requirements**, **Webhook Scope Rule**, **Skills Used**, **MEMORY.md Format**.

### Synthesis rules

- **Purpose**: Specific what + why. Name inputs, outputs, and tools. Good: "Monitors YouTube channel X for new episodes, downloads transcripts, and posts digests to #channel on Slack." Bad: "Processes data."
- **Workflow**: Concrete numbered steps with actual tool names. Group into phases by logical purpose.
- **Guardrails Always**: From positive patterns the agent must consistently follow.
- **Guardrails Never**: From corrections and constraints the agent must avoid.
- **Placeholders**: Replace user-specific values (IDs, URLs, keys) with `<placeholder-name>`.

### Command connector references in SOUL.md

When the agent uses a command connector, the SOUL.md workflow must reference the **connector name** as the command — not the npm package name, underlying transport, or `npx` invocation. The connector name is the CLI command the agent types, and it is the only name on the agent's PATH.

Good: `Run agentmail inboxes list to verify the CLI is connected.`
Bad: `Run npx agentmail-cli inboxes list` or `Run agentmail-cli inboxes list`

Using the wrong name either bypasses secret injection (calling npx directly) or fails entirely (command not found). When creating connectors, always name them after the CLI command (see naming rule in the Connectors section).

### Common mistakes

- Empty or vague Purpose — always name specific inputs, tools, and outputs
- Missing Workflow — Purpose without steps leaves the agent guessing
- Hardcoded values that should be `<placeholder>`s
- No scope boundary for webhook agents (see Writing Channel Files)
- Using the wrong command name for command connectors — the connector must be named after the CLI command (e.g., `agentmail` not `agentmail-cli`), and SOUL.md must reference that same name

## Writing Channel Files

Channel files tell the agent what to do when a message arrives. They are instructions TO the agent, written as direct imperatives.

### Webhook payload location (critical)

The JSON webhook payload is appended inline after the channel file in the user message. Every channel file **must** start with:

```
The JSON webhook payload is appended directly after these instructions
in the user message. Parse it inline — do not fetch, list, or search
for the payload elsewhere. Do NOT use tools to read the payload.
```

Without this, agents waste turns searching for the payload with tool calls.

### Structure

1. **Payload location** — the instruction above
2. **What happened** — describe the event
3. **What to extract** — which payload fields identify the transaction (IDs, refs)
4. **Scope boundary** — all actions must be scoped to those identifiers
5. **What to do** — step-by-step processing instructions

### Example

```markdown
# New Email Received

The JSON webhook payload is appended directly after these instructions
in the user message. Parse it inline — do not fetch, list, or search
for the payload elsewhere. Do NOT use tools to read the payload.

You received a webhook for a single new email.

## Scope

Extract the `thread_id` from the payload. All actions are scoped to
this thread. Do not list, read, or act on any other threads.

## Steps

1. Extract `thread_id`, `from_`, `subject`, and `text` from the payload.
2. [... task-specific steps ...]
```

### Reinforcing scope in SOUL.md

For webhook-driven agents, add to SOUL.md:

```markdown
## Webhook Scope Rule

When you receive a webhook, your scope of work is defined by the
identifiers in the payload. Use any tools to fully understand and act
on that specific content, but do not act on unrelated content.
```

## Writing valet.yaml

`valet.yaml` is optional project metadata for standalone agents, sites, and
apps. `valet new` creates a placeholder for new agent projects. Agents
published to the Valet catalog require a complete manifest.

When a project has a manifest, keep its metadata header current:

```yaml
name: <resource-name>
display_name: <Human-Readable Name>
description: <One sentence on what this is and who it is for>
```

These fields identify the resource wherever a name alone is not enough. A
DNS name like `webinar-slides-20260810` tells a reader nothing, so write
`display_name` for a person and `description` for someone deciding whether
to open it. Deploy reads the file and promotes both onto the resource.

Agents also need `category` — one lowercase word (`finance`, `research`, `developer-tools`) that the dashboard's preview card renders. Sites and apps have no preview card, so leave it off.

For a standalone resource, everything below the header stays opt-in.
`connectors`, `channels`, `story`, and `example` drive the dashboard setup
flow. Add them when the user asks for a deploy button, dashboard setup,
one-click setup, or catalog publication. A catalog-published agent requires
the complete story and dependency fields described below.

Sites and apps take the header and nothing else. A `connectors` or `channels` block on either is rejected at deploy: a site has no runtime and an app runs a Procfile process, so neither can act on one.

**Keep the manifest current.** When a resource's purpose changes, update `display_name` and `description` in the same change. A stale description outlives the content it describes, and the next deploy publishes it.

### Catalog items only

The manifest only supports connectors and channels that exist in the Valet catalog. Custom connectors and channels cannot be represented in `valet.yaml` — the dashboard setup flow looks up each `catalog` value and fails if the entry doesn't exist.

**Before writing valet.yaml**, run `valet connectors catalog` and `valet channels catalog` to check which of the agent's connectors and channels are in the catalog.

- **Mix of catalog and custom resources**: Include only the catalog items in `valet.yaml`. Document the custom resources in `AGENTS.md` with CLI setup instructions. Users will configure catalog resources through the dashboard flow and create custom resources manually with the CLI afterward.
- **Only custom resources**: Still write `valet.yaml` with the four required top-level fields and omit the `connectors` and `channels` arrays. The dashboard uses this metadata to display the agent's name, description, and category.
- **Missing catalog entries**: If a connector or channel should be in the catalog but isn't, direct the user to email support@valet.dev to request it be added.

### Template

```yaml
name: <agent-name>
display_name: <Human-Readable Name>
description: >-
  <What the agent does — shown in the dashboard
  during setup>
category: <category>
connectors:
  - catalog: <catalog-entry-name>
    description: >-
      <Agent-specific context for this connector>
    slot_descriptions:
      <SLOT_NAME>: <Label shown in the setup flow>
channels:
  - catalog: <catalog-entry-name>
    description: >-
      <Agent-specific context for this channel>
    events:
      - <event_type>
    slot_descriptions:
      <SLOT_NAME>: <Label shown in the setup flow>
```

### Rules

- **`name`** must match the agent name used in `valet agents create`.
- **`catalog` values must come from the catalog.** Run `valet connectors catalog` and `valet channels catalog` to verify. Only include connectors/channels that exist in the catalog — omit custom ones from the yaml and document them in `AGENTS.md` instead.
- **`slot_descriptions` keys must match slot names from the catalog entry.** Run `valet connectors catalog get <name>` or `valet channels catalog get <name>` to discover slot names.
- **`description`** should be a complete sentence suitable for display in the dashboard.
- **`category`** should be a descriptive term (e.g. `development`, `ops`, `utilities`, `developer-tools`, `testing`).
- Omit `connectors` and `channels` arrays entirely if the agent has none.
- Omit optional fields (`description`, `events`, `slot_descriptions`) when the catalog defaults are sufficient.

### Validation checklist

After writing the file, verify:
1. All four top-level fields are present and non-empty
2. Every `catalog` value was confirmed to exist by running `valet connectors catalog` / `valet channels catalog`
3. Every `slot_descriptions` key matches a slot defined in the catalog entry
4. Custom (non-catalog) connectors/channels are omitted from the yaml and documented in `AGENTS.md`

## Writing AGENTS.md

`AGENTS.md` is the **last project file written** before deployment. It lives
in the agent project root and serves as a human- and LLM-readable setup guide
for anyone who needs to deploy the agent later.

**NEVER include secret values, API keys, or tokens in AGENTS.md.** Only describe what is needed and why.

### Template

```markdown
This folder contains the source for a Skilled Agent originally built for the Valet runtime. Changes should follow the Skilled Agent open standard.

## Setup

### Connectors

- **<connector-name>**: <plain-English description of what it provides and why the agent needs it>
  [Repeat for each connector]

### Channels

- **<channel-name>** (<channel-type>): <what triggers this channel and what the agent does when it fires>
  [Repeat for each channel]

### Secrets

- **<SECRET_NAME>**: <what this secret is for, where to obtain it, and any scopes or permissions required>
  [Repeat for each secret]

### External Setup

[If the agent requires any configuration outside of Valet — third-party service setup, OAuth apps, cloud console steps, DNS records, etc. — describe each step here in plain English. Be specific enough that a person unfamiliar with the project can follow along.]
```

### Rules

- Write in plain English — describe requirements as nouns with reasons, not CLI commands
- Be specific about secrets — include required scopes/permissions and where to obtain them
- Include external setup steps (OAuth apps, cloud consoles, webhook registrations, etc.)
- Omit sections that don't apply. Write this file last.

## Authoring the agent story (valet.yaml)

Agents published to the Valet catalog ship with a `valet.yaml`
manifest. The Valet dashboard reads it to render the friendly
`agents/new` configuration wizard. Standalone agents (deployed only
via `valet agents create` without catalog publication) do not need
one.

When authoring `valet.yaml`, fill in four things:

1. **Top-level metadata** — `name`, `display_name`, `description`, `category`.
2. **`story` block** — slot-driven narrative copy.
3. **`connectors[]` and `channels[]`** — dependencies with per-agent UI
   overrides.
4. **Catalog references (`catalog:`) must match existing Valet catalog
   entries** — otherwise the wizard can't resolve icons or brand copy.

### The `story` block

The story is a 3-step narrative that answers: *what's the trigger*,
*what does the agent do*, *what is the outcome*. Every field has a
hard length cap enforced by `valet manifests validate`. Do not exceed
it.

```yaml
story:
  hero: "Let's get AskADev answering questions for your team."
  subheadline: "Watches one Slack channel. Searches GitHub. Replies in-thread."
  steps:
    - role: trigger
      title: "Your team asks a question in Slack."
      body: "Someone posts 'where do we handle the Stripe webhook retry logic?'"
      catalog: slack-webhook
    - role: action
      title: "AskADev reads your code."
      body: "Searches the repo. Finds the handler and surrounding comments."
      catalog: github
    - role: outcome
      title: "And answers — with sources."
      body: "Replies in-thread, linking to the exact file, line, and commit."
      catalog: slack-mcp
```

**Role contract:** exactly three steps in order: `trigger`, `action`,
`outcome`. Nothing else.

**`catalog:` on a step:** optional. When set, it must match a
`catalog:` declared on one of this manifest's `connectors` or
`channels`. The wizard renders that service's icon as the step glyph.
Leave empty to render the agent monogram (useful for the middle
"the agent thinks" step that has no external service).

### Drafting copy from SOUL.md

Do not invent copy from scratch — derive it from the agent's
SOUL.md. The Purpose and Workflow sections already describe the
agent's trigger, action, and outcome in prose; your job is to
distill that prose into the slot-driven format.

Work in this order (top-down matches what the user reads in the
wizard):

1. **Extract the three beats.** Open SOUL.md. The `Purpose` sentence
   names the trigger, the action, and the outcome — usually in that
   order. If Purpose is vague, fall back to the Workflow phases:
   Phase 1 → trigger, Phase 2 → action, Phase 3 → outcome.
2. **Find the hook.** What makes this agent specific? A concrete
   time (*"8am hits"*), a concrete place (*"posts to #ai-news"*), or
   a concrete constraint (*"only after you approve"*). Write the hook
   down — it anchors the hero and subheadline and often becomes the
   outcome body.
3. **Draft the trigger, action, and outcome steps first.** Concrete
   details are easier to write than the hero. Use the tone rules
   below. Aim for the sweet-spot lengths in the next table.
4. **Write the outcome `done_note`s next.** These are short — one
   line each. They fall out of step 3.
5. **Write the subheadline.** One concrete sentence that names the
   services and the reward. The subheadline is the "elevator pitch"
   beneath the hero.
6. **Write the hero last.** The hero is the most compressed, most
   brand-defining line. Writing it after the steps gives you
   material to compress from.
7. **Run `valet manifests validate`.** Non-negotiable. The dashboard
   rejects invalid manifests at render time.
8. **Read it aloud.** Every line should sound like something a human
   could read out loud without flinching. If it sounds like a
   marketing page, rewrite.

### Length targets (what looks good, not just what validates)

The caps are hard limits enforced by `valet manifests validate`. The
sweet-spot ranges are what actually renders well in the wizard — use
them as targets, not the caps.

| Field | Sweet spot | Hard cap | Too short | Too long |
|-------|-----------|----------|-----------|----------|
| `hero` | 45–75 chars | 80 | Hollow, generic | Wraps awkwardly on narrow viewports |
| `subheadline` | 110–170 chars | 200 | Reads like a slogan, not an explainer | Crammed, unreadable at a glance |
| step `title` | 25–50 chars | 60 | Lacks grip | Runs onto two lines, breaks the rhythm |
| step `body` | 80–130 chars | 140 | Feels like filler | Looks dense under the title |
| ui `headline` | 30–55 chars | — | Generic ("Connect GitHub") | Repeats the step title |
| ui `blurb` | 80–140 chars | — | No agent-specific angle | Reads like the catalog description |
| ui `done_note` | 20–45 chars | — | No concrete "it works" signal | Belongs in a status page |

Length cap > sweet spot: use the sweet spot. Only push toward the
cap when the extra characters carry real information (a
channel name, a specific time, a named artifact). Never pad.

### Voice and style

**Always:**

- Write in present tense, active voice. *"Posts the briefing"*, not
  *"Will post the briefing"* or *"The briefing is posted"*.
- Name the agent at least once in the hero. The user is meeting it
  for the first time.
- Name concrete things: services (*Slack*, *GitHub*), artifacts
  (*#ai-news*, *pull request*), times (*8am*, *every Friday*). Never
  *"messaging platforms"* or *"on a schedule"*.
- Use em dashes (*—*) for rhythm when a thought has two beats. The
  wizard font renders them well.
- Address the reader as *you*. *"Your team asks"*, *"You paste a
  message"*. Never *"the user"*.

**Never:**

- Use buzzwords: *seamless*, *leverages*, *empowers*, *intelligent*,
  *cutting-edge*, *streamlines*, *unlocks*, *powerful*, *robust*.
- Use passive voice for the action step. *"AskADev reads your
  code"* — not *"Your code is read by AskADev"*.
- Describe mechanism when a result would do. *"Authenticates via
  OAuth"* is mechanism; *"Uses OAuth — no API token needed"* is a
  result. *"Parses the payload"* is mechanism; *"Reads the PR"* is
  a result.
- Write copy that could belong to a different agent. If you can
  swap *AskADev* for *Code Reviewer* without the sentence breaking,
  the copy is generic — add the hook.
- Use emoji unless the agent's personality demands it and you've
  stress-tested it across viewports.

### Tone rules (per field)

These override any other guidance. They're optimized for the way
the wizard renders each field.

- **Hero** is imperative or present-indicative, names the agent.
  Write *"Let's get AskADev answering questions for your team."* —
  not *"AskADev is an AI agent that answers questions"*.
- **Subheadline** is one concrete sentence naming the services and
  the reward. No lists, no semicolons.
- **Trigger title** starts with the user or the channel event:
  *"Your team asks…"*, *"A PR is opened."*, *"8am hits."*
- **Action title** uses active voice, names the agent:
  *"AskADev reads your code."*
- **Outcome title** names the concrete artifact the user sees:
  *"Replies in-thread, linking to the file."*

### Good vs. bad examples

| Field | ❌ Bad | ✅ Good | Why |
|-------|-------|--------|-----|
| hero | *"AskADev is an AI-powered Slack assistant that answers code questions."* | *"A Slack bot that reads your code before it answers."* | Bad leads with category + buzzword. Good leads with behavior and names the hook ("before it answers"). |
| subheadline | *"Uses GitHub MCP and Slack MCP to provide intelligent responses to developer questions."* | *"Ask a question about a GitHub repo in Slack. AskADev researches the actual code and commit history, then replies in-thread."* | Bad names the plumbing. Good names the action and the reward. |
| trigger title | *"Webhook event received"* | *"A PR is opened."* | Bad names the mechanism. Good names what happened in the user's world. |
| action title | *"Diff analysis"* | *"Code Reviewer reads the diff."* | Bad is a noun phrase. Good is a sentence with a subject and verb. |
| outcome title | *"Review submitted"* | *"Inline comments — or an approve."* | Bad is passive mechanism. Good names the two concrete outputs. |
| step body | *"The agent processes the incoming webhook payload and performs configured actions."* | *"Checks correctness, security, maintainability, and test coverage. Reads full files when context matters."* | Bad is generic. Good enumerates specifics. |
| ui blurb | *"Connect your GitHub account to give the agent access to your repositories."* | *"AskADev reads your code when it answers — like a new hire would."* | Bad could belong to any GitHub connector. Good is about *this* agent's use of GitHub. |
| ui done_note | *"Successfully connected"* | *"Listening in #engineering"* | Bad is a status. Good is the concrete outcome the user wanted. |

### Per-service `ui:` block

Each `connectors[]` and `channels[]` entry can carry a `ui:` block
that overrides generic catalog copy with agent-specific copy:

```yaml
connectors:
  - catalog: github
    description: "GitHub MCP server for browsing repos and reading files"
    ui:
      headline: "Point AskADev at your repo."
      blurb: "AskADev reads your code when it answers — like a new hire would."
      done_note: "Connected to your repo"

channels:
  - catalog: slack-webhook
    description: "Receives Slack messages and app mentions"
    ui:
      headline: "Let AskADev hear your team in Slack."
      blurb: "We'll add AskADev as a normal Slack app. You pick the channel."
      done_note: "Listening in the channel you invite it to"
```

- `headline` replaces the step's default headline. Write it as a
  verb + service imperative: *"Let AskADev hear your team in Slack."*
- `blurb` is a one-paragraph summary of *this specific agent's* use
  of the service. Not a generic Slack/GitHub explainer — that's what
  the catalog `description` is for.
- `done_note` is the one-line summary shown on the deploy screen
  once the service is connected. Write what the user will see after
  deploy: *"Listening in #engineering"*, *"Connected to valetdotdev/ark"*.

**What NOT to put in `ui:`:** permissions, restrictions, safety
chips, "why", verb, minutes. Those are catalog-owned fields filled
in by the Valet team — do not duplicate them per-agent.

### Keep `valet.yaml` and `README.md` in sync

The agent's `README.md` tagline (the one-liner under the project
title) and the `valet.yaml` `subheadline` are the same piece of
marketing copy, surfaced on two different surfaces — GitHub and the
dashboard wizard. Keep them **word-for-word identical**. When you
update one, update the other in the same commit.

Do the same for the `README.md` project title and the
`display_name`: they should match exactly. Users who click through
from GitHub to the wizard should see the same name and the same
pitch in both places — drift is the surest way to make an agent
look unmaintained.

```markdown
<!-- README.md -->
# Deep Researcher

Every morning, Deep Researcher scans the AI news landscape,
summarizes the 5 most important stories, and posts the briefing
to #ai-news.
```

```yaml
# valet.yaml
display_name: Deep Researcher
story:
  subheadline: "Every morning, Deep Researcher scans the AI news landscape, summarizes the 5 most important stories, and posts the briefing to #ai-news."
```

### Validating

After writing or editing a `valet.yaml`, always validate:

```bash
valet manifests validate
```

Or with an explicit path:

```bash
valet manifests validate path/to/valet.yaml
```

`valet manifests validate` enforces length caps, the 3-step contract,
and the step-catalog reference rule. If it fails, fix the reported
errors before deploying — the dashboard wizard will reject invalid
manifests.

## Agent Project Structure

```
my-agent/
  AGENTS.md            # Setup guide for future developers (required)
  CLAUDE.md            # Points Claude Code at AGENTS.md
  SOUL.md              # Agent identity and behavior (required)
  valet.yaml           # From valet new; required for catalog publication
  channels/            # Channel files (for webhook/trigger-driven agents)
    <channel-name>.md
  skills/              # Agent-scoped skill documentation (optional)
    <connector-name>/
      SKILL.md
  .valet/
    config.json        # Auto-managed by CLI
```

All deployed files are **read-only** at runtime. The agent can write new files (e.g., MEMORY.md), but written files **do not survive deploys**.

## Execution Guidelines

- Run commands with the terminal tool appropriate to the operating system.
- **Be explanatory**: Before running any valet command, briefly tell the user *what* you're about to do and *why*. Don't silently execute commands — the user should always understand the purpose of each step.
- **Installation guardrails**: Follow the Installation section strictly.
  Use the official direct installer for new installations and `valet
  update` for existing ones. If either fails, stop rather than downloading
  a raw binary or building from source.
- **Authenticate before account access**: Run `valet auth whoami` before a
  command reads or writes account state. If the user is logged out, explain
  why login is required and start `valet auth login`. Local version, help,
  and offline manifest-validation commands remain available while logged
  out.
- **Use `valet help` proactively**: When you encounter a command, flag, or feature you're unsure about, run `valet help <command>` before guessing. The CLI help is the authoritative source.
- **Never ask for secret values inside the LLM session.** Direct the user to run `valet env set NAME=VALUE` in their own terminal and wait for confirmation. Plain env vars (`valet env set NAME=VALUE --plain`) are not credentials and may be set directly.
- **Verify privileged commands with `valet exec`.** After the agent exists,
  test each underlying command with `valet exec <names> -- <command>`. This
  is the only way to run commands with Valet-managed secrets locally. Fix
  failures before the final deploy and end-to-end test. Use
  `{{SECRET_NAME}}` only when a tool requires a secret in an argument.
- When the user asks to create an agent from scratch, follow "Designing a New Agent".
- When the user asks to capture the current session as an agent, follow "Learning from the Current Session".
- When writing SOUL.md, follow the template and synthesis rules. Never leave Purpose or Workflow empty.
- When authoring a `valet.yaml` for a catalog-published agent, follow "Authoring the agent story". Run `valet manifests validate` after every edit — length caps and the 3-step role order are non-negotiable.
- For destructive commands (`destroy`, `remove`, `revoke`), always confirm with the user first.
- When creating webhook channels, report the webhook URL and managed secret
  name. Do not repeat the raw signing secret. When writing channel files,
  include the payload location instruction.
- After deploying an agent with channels for the first time, run the interactive test loop.
- If a command fails, read the error and troubleshoot. Common issues: not
  logged in, no `SOUL.md`, not linked, or an agent crash. For installer or
  updater errors, stop and let the user resolve them manually.

## Setup

[If the agent requires any configuration outside of Valet — third-party service setup, OAuth apps, cloud console steps, DNS records, etc. — describe each step here in plain English. Be specific enough that a person unfamiliar with the project can follow along.]
