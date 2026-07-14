---
description: Install and run the @atomicmail/agent-skill-gh-pages CLI (register, jmap_request, help) for shell-capable agents and automation.
---

# @atomicmail/agent-skill-gh-pages

Atomic Mail AgentSkill CLI for shell-capable AI agents. It exposes three
commands: `register`, `jmap_request`, and `help`. **`jmap_request`** uses the
same shared library as **`@atomicmail/mcp-gh-pages`**.

## For AI agents — run `atomicmail help`

**Invoke `atomicmail help` before improvising JMAP or preset details.** The CLI
embeds the topic docs — written for agents,
version-matched to your install, and cheaper to fetch on demand than reconstructing
placeholder grammar or attachment flows from memory.

**When to call help:** at the start of a mail task (`atomicmail help` or
`help --topic overview`); before custom batches (`help --topic presets` and
`help --topic jmap_cheatsheet`); right after `register` (`help --topic cron`
for hourly inbox polling after `register`); when errors mention missing
placeholders, auth, or an old preset file on disk (`help --topic
troubleshooting`). Prefer the installed binary over static README copies in
other repos — **trust `help` from the package you are running**.

## Install / run

```bash
npx --package=@atomicmail/agent-skill-gh-pages atomicmail --help
```

## Quick start

```bash
npx --package=@atomicmail/agent-skill-gh-pages atomicmail register \
  --username "myagent"

npx --package=@atomicmail/agent-skill-gh-pages atomicmail jmap_request \
  --ops '[["Mailbox/get", {"accountId": "$ACCOUNT_ID"}, "m0"]]'
```

Usernames must be 5–21 characters (local-part of your `@atomicmail.ai`
address).

If credentials already exist for a different username, `register` fails by
default. Pass `--forced` only after backing up the credential directory.

## After register: hourly inbox polling

After `register`, arrange hourly inbox polling per your runtime. **Native cron
hosts** (OpenClaw, Hermes, atomic-agent) schedule an **hourly AI agent** to
fetch and triage mail with preset `list_inbox.json`. **Hosts without native
cron** should ask the operator to set up polling on a capable host, or remind
manual fetch — do **not** work around with OS schedulers or cross-platform
scheduling. Do **not** cron `atomicmail jmap_request` alone.

**Hermes users:** follow [Hermes Agent](#hermes-agent) — accept the skill
blueprint via `/suggestions` after `register`.

Options and agent prompt:
[`SKILL.md`](./SKILL.md#hourly-inbox-polling-after-register) · `atomicmail help --topic cron`
· MCP `help` topic `cron`

## Hermes Agent

Hermes ships a bundled Atomic Mail skill with a launcher CLI and an hourly inbox
blueprint. Requires [Hermes](https://hermes-agent.nousresearch.com) with the
skills toolset and Node.js 20+ (for the bundled launcher).

### Install

Unified in-repo tap (updated on each GitHub release):

```bash
hermes skills install Atomic-Mail/atomic-mail-agentic/integrations/skill/atomicmail
```

### Credentials

On Hermes the default credential directory is **`~/.hermes/atomicmail`**, not
`~/.atomicmail` (used by npm/npx AgentSkill and MCP defaults).

The skill launcher sets `ATOMIC_MAIL_CREDENTIALS_DIR` to `$HOME/.hermes/atomicmail`
when that variable is **not** already set. Override explicitly with
`ATOMIC_MAIL_CREDENTIALS_DIR` or `atomicmail.credentials_dir` in Hermes config.

| Runtime | Default credentials dir |
| ------- | ----------------------- |
| Hermes skill | `~/.hermes/atomicmail` |
| npm/npx AgentSkill, MCP | `~/.atomicmail` |

Files in each directory (mode `0600`): `credentials.json`, `session.jwt`,
`capability.jwt`.

### Register

Use the skill's bundled CLI — no `npx`:

```bash
atomicmail register --username "myagent"
```

The launcher handles the credentials directory; omit `--credentials-dir` in the
default single-inbox flow. For **multiple inboxes**, pass `--credentials-dir`
with a separate directory per account on `register` and `jmap_request`.

### After register (required)

1. Run `/suggestions` in Hermes and **accept** the Atomic Mail hourly inbox
   blueprint.
2. The blueprint schedules a full **agent** turn (`no_agent: false`) with
   `list_inbox.json` and `deliver: origin`. Do **not** skip this step.
3. Do **not** cron raw `jmap_request` alone or use `--no-agent` (no LLM triage).

**Manual fallback** if you skip the blueprint:

```bash
hermes cron create "0 * * * *" \
  "Use atomicmail jmap_request --ops-file list_inbox.json to fetch my inbox. Summarize new messages, highlight what needs a reply, and stay available — I may ask you to reply, forward, search, or dig into something important." \
  --name "atomicmail-inbox" \
  --deliver origin
```

See `atomicmail help --topic cron` for the full prompt and delivery options.

### Links

- Hermes creating skills (blueprints):
  https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills
- Hermes cron (manual fallback):
  https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
- Maintainer publish workflow:
  [CONTRIBUTING.md](https://github.com/Atomic-Mail/atomic-mail-agentic/blob/develop/CONTRIBUTING.md)
  (unified skill section)

## `jmap_request`, presets, and placeholders

`jmap_request` accepts inline `--ops` JSON or `--ops-file` (same shapes as MCP:
methodCalls array or full `{ "using", "methodCalls" }`). Pass custom
`$PLACEHOLDERS` via `--vars '{"PLACEHOLDER":"value"}'` (keys without `$`).

```bash
npx --package=@atomicmail/agent-skill-gh-pages atomicmail jmap_request \
  --ops-file send_mail.json \
  --vars '{"TO":"alice@example.com","SUBJECT":"Hello","BODY":"Hi there"}'
```

**Resolution:** relative `--ops-file` resolves to `--credentials-dir` (default
`~/.atomicmail`), then bundled presets.

**Details** (placeholder grammar, built-ins, shadowing, bundled preset list,
attachments): see [@atomicmail/mcp-gh-pages](./mcp.md) and the embedded **`help`** topic
**`presets`** (`atomicmail help --topic presets`).

## Shared state

Each credential **directory** is an isolated account (default `~/.atomicmail`,
mode `0600` files):

- `credentials.json`
- `session.jwt`
- `capability.jwt`

The CLI and MCP read and write the directory you select per command
(`--credentials-dir` / `credentials_dir`) or the default from
`ATOMIC_MAIL_CREDENTIALS_DIR`. Multiple accounts = multiple directories; see
MCP `help` topic `multi_account` or [mcp.md](./mcp.md#multiple-accounts--agents).

## Defaults

- auth endpoint: `https://auth.atomicmail.ai`
- api endpoint: `https://api.atomicmail.ai`
- credentials directory: `~/.atomicmail`

## Overriding defaults

- Endpoints: `--auth-url`, `--api-url` or `ATOMIC_MAIL_AUTH_URL`,
  `ATOMIC_MAIL_API_URL`
- Credentials path: `--credentials-dir` or `ATOMIC_MAIL_CREDENTIALS_DIR`
- PoW salt: `--scrypt-salt` or `ATOMIC_MAIL_SCRYPT_SALT`
