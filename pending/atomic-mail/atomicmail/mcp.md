---
description: Install and configure the @atomicmail/mcp-gh-pages stdio server, tools (register, jmap_request, help), and host-specific notes for chat-based agents.
---

# @atomicmail/mcp-gh-pages

Atomic Mail MCP server — a local stdio Model Context Protocol server that gives
an AI agent a programmable email inbox over JMAP, with automatic Proof-of-Work
auth and capability-token rotation.

## For AI agents — call `help` early and often

**Use the `help` tool as your primary documentation source.** MCP hosts choose
tools from short descriptions; when placeholders, JMAP `using` URNs, attachment
uploads, or cron setup are unclear, **call `help` instead of guessing** from
general JMAP knowledge or a stale README copy. The topics ship inside the
installed package and always match the version your host is running.

**Suggested calls:** `help` with no topic (overview) at the start of a mail
task; `help` with topic `presets` before your first non-trivial `jmap_request`;
`help` with topic `cron` immediately after a successful `register`; `help`
with topic `jmap_cheatsheet` when sending mail or using blobs; `help` with
topic `troubleshooting` when errors mention missing placeholders, auth, or
preset shadowing. If anything disagrees with docs you read elsewhere, **trust
`help` from this package**.

## Install

```json
// mcp.json

{
  "mcpServers": {
    "atomicmail": {
      "command": "npx",
      "args": ["-y", "@atomicmail/mcp-gh-pages"]
    }
  }
}
```

Your MCP host spawns this process; see configuration below.

For ClawHub, use the MCP-only channel package:

```json
{
  "mcpServers": {
    "atomicmail": {
      "command": "npx",
      "args": ["-y", "@atomicmail/mcp-clawhub"]
    }
  }
}
```

## Tools exposed

| Tool           | Description                                                                                                                                                                                                       |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `register`     | PoW signup; persists credentials. Usernames are 5–21 characters (local-part of your `@atomicmail.ai` address). Idempotent when username matches inbox. A different username is rejected unless you pass a separate `credentials_dir` or `forced: true`. Optional `credentials_dir` per call (parity with AgentSkill `--credentials-dir`). |
| `jmap_request` | JMAP batch via `ops` or `ops_file`. Optional `credentials_dir` per call. Uppercase `$VAR_NAME` tokens are substituted (`$ACCOUNT_ID` / `$INBOX` / `$INBOX_MAILBOX_ID` / `$UPLOAD_URL` / `$DOWNLOAD_URL` from session; others via optional `vars` map). |
| `help`         | Built-in docs (`topic` optional); use `topic: "readme"` for the published package `README.md`. Use `topic: "multi_account"` for multiple inboxes on one MCP server.                                                                                                                    |

## Typical MCP workflow

1. Call `register` with a username (or rely on existing `credentials.json`).
   If credentials already exist for a different username, pass a **separate**
   `credentials_dir` to add another account, or pass `forced: true` only when
   you intend to replace credentials in the **same** directory (after backing
   it up).
2. **After register:** arrange hourly inbox polling per your runtime. Native cron
   hosts (OpenClaw, Hermes, atomic-agent) schedule an hourly **agent** job whose
   prompt fetches inbox mail via `{ "ops_file": "list_inbox.json" }`. Hosts
   without native cron should ask the operator to set up polling on a capable
   host or remind manual fetch — do **not** work around with OS schedulers or
   cross-platform scheduling. Do **not** cron `atomicmail jmap_request` alone.
   Call `help` with topic `cron` for examples.
3. `jmap_request` with `ops` or `ops_file` (optional `vars` for `$TO`,
   `$SUBJECT`, etc.).
4. `help` when stuck.

### Hourly inbox polling (after register)

Invoke a **full agent turn** so you can reply, forward, or follow up — not a
raw CLI log or headless one-shot.

| Setup | Workflow |
| --- | --- |
| OpenClaw | `openclaw cron add` + `--announce` |
| Hermes | `hermes cron create` + `--deliver` |
| Atomic Bot | OpenClaw or Hermes |
| atomic-agent | `atomic-agent task create --cron` |
| No native cron (Claude, Pi, Cursor, …) | Ask operator to schedule on a capable host, or remind manual fetch |

Workflow options and agent prompt: MCP `help` topic `cron`, [`SKILL.md`](./SKILL.md#hourly-inbox-polling-after-register), or `atomicmail help --topic cron`.

## `jmap_request` input patterns

`jmap_request` accepts either:

- inline `ops` — a JSON **string** whose value is either a **methodCalls array**
  (for example `[["Mailbox/get", {...}, "m0"]]`) or a full envelope object
  `{ "using": [...], "methodCalls": [...] }`, or
- `ops_file` — path to a JSON file containing the same shapes as `ops`.

When using `ops_file`, relative paths first resolve against the credential
directory. If a file is not present there, the runtime falls back to bundled
presets shipped in the npm package.

### Default `using` for a bare methodCalls array

If `ops` is **only** a methodCalls array (no `using` in the JSON), the server
merges the tool’s default capability list — today
**`urn:ietf:params:jmap:core`** and **`urn:ietf:params:jmap:mail`** only. For
**`EmailSubmission/set`**, **`Blob/upload`**, or **`Blob/get`**, either pass a
full envelope that includes the right URNs in `using`, or rely on your MCP host
passing an extended `using` array on the tool call (when supported). See
[`JMAP using and inline ops`](/jmap-using) for the full picture.

Successful responses may include a top-level **`_next`** field (suggested
follow-ups); that is not part of RFC 8620 — see [`Raw JMAP requests`](/jmap)
(“Successful responses and `_next`”).

## Presets and placeholders

Pass **`vars`** on the **`jmap_request`** tool next to **`ops`** or
**`ops_file`** (not inside the ops JSON string).

Examples:

`{ "ops_file": "list_inbox.json" }`

`{ "ops_file": "send_mail.json", "vars": { "TO": "a@b.com", "SUBJECT": "Hi", "BODY": "..." } }`

**Resolution:** relative `ops_file` paths resolve to the credential directory
first, then bundled presets in the package.

**Preset shadowing:** a file such as `list_inbox.json` in the credential
directory replaces the bundled preset with the same name. After upgrading
`@atomicmail/mcp-gh-pages`, errors about missing placeholders often mean an **older**
preset copy on disk — delete or update it, or pass an absolute `ops_file` path.

**Full** placeholder grammar, built-ins (`$INBOX` vs `$INBOX_MAILBOX_ID`,
attachment tokens, bundled preset names): use the **`help`** tool with topic
**`presets`**.

## Credential files and token lifecycle

Mode `0600`: `credentials.json` (includes `apiKey`, `inboxId`, endpoints, blob
URL templates), `session.jwt` (session bearer, rotated), `capability.jwt` (JMAP
bearer, short TTL). MCP and the AgentSkill CLI create and rotate these
automatically.

For raw HTTP auth steps, see [`REST authentication flow`](/rest-auth).

## Attachments and blobs

- **In-band (RFC 9404):** `Blob/upload` / `Blob/get` in the same JMAP batch as
  mail methods. Shapes, limits, and copy-paste JSON:
  [Raw JMAP requests](./jmap.md#attachments-rfc-9404-inline-blob-flow).
- **Out-of-band (RFC 8620):** session **`uploadUrl`** / **`downloadUrl`**. MCP
  **`attachments`** uploads each local file first, then substitutes
  `$ATTACHMENT_N_BLOB_ID` (and related placeholders) into your ops. Use preset
  **`send_mail_blob_attachment.json`** with **`attachments`**.

When the session advertises blob limits, **`jmap_request`** may **reject before
POST** computable oversize `Blob/upload` payloads and attachment file sizes (see
[RFC 9404 §3.1](https://www.rfc-editor.org/rfc/rfc9404#section-3.1)). If
`maxSizeBlobSet` is `null`, no client octet cap is applied (the server may still
reject the request).

## Multiple accounts / agents

One MCP server can manage several isolated inboxes. Pass optional
`credentials_dir` on **`register`** and **`jmap_request`** (same idea as
AgentSkill `--credentials-dir`). When omitted, the default directory applies
(`ATOMIC_MAIL_CREDENTIALS_DIR` or `~/.atomicmail`).

```json
{ "username": "alice", "credentials_dir": "~/.atomicmail/alice" }
{ "ops_file": "list_inbox.json", "credentials_dir": "~/.atomicmail/bob" }
```

- **Add a second account** without touching the first: use a new path on
  `register`, not `forced: true`.
- **Replace** credentials in one directory: back it up, then `forced: true`.
- **Concurrency:** do not run parallel tool calls against the same
  `credentials_dir` (JWT files have no locking).

Full details: MCP `help` topic **`multi_account`**.

## Defaults

- auth endpoint: `https://auth.atomicmail.ai`
- api endpoint: `https://api.atomicmail.ai`
- credentials directory: `~/.atomicmail`

## Overriding defaults

```json
{
  "mcpServers": {
    "atomicmail": {
      "command": "npx",
      "args": ["-y", "@atomicmail/mcp-gh-pages"],
      "env": {
        "ATOMIC_MAIL_AUTH_URL": "https://custom-auth.example",
        "ATOMIC_MAIL_API_URL": "https://custom-api.example",
        "ATOMIC_MAIL_CREDENTIALS_DIR": "/Users/me/.atomicmail",
        "ATOMIC_MAIL_INBOX_DOMAIN": "mail.example.com",
        "ATOMIC_MAIL_SCRYPT_SALT": "hex-salt-override",
        "ATOMIC_MAIL_API_KEY": "existing-api-key"
      }
    }
  }
}
```
