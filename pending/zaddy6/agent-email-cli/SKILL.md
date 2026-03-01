---
name: agent-email-cli
description: Operate the agent-email CLI to create disposable inboxes, poll for new mail, retrieve full message details, and manage local mailbox profiles. Use when the user needs terminal-based email inbox access for LLM or agent automation workflows.
---

# Agent Email CLI

## Overview

Use this skill to operate the `agent-email` command safely and predictably for agent workflows that need inbox access.

Prefer JSON-native command output and return key fields (`email`, `messageId`, `subject`, `createdAt`, `from.address`) in your summaries.

## Workflow

1. Verify CLI availability.

```bash
command -v agent-email
agent-email --help
```

If missing, install:

```bash
npm install -g @zaddy6/agentemail
# or
bun install -g @zaddy6/agentemail
```

2. Create a mailbox account.

```bash
agent-email create
```

Record these fields from JSON output:

- `data.email`
- `data.accountId`
- `data.activeEmail`

Do not record, repeat, or print secret values such as mailbox passwords or tokens.

3. Read latest messages.

```bash
agent-email read <email|default>
```

For inbox waiting/polling:

```bash
agent-email read <email|default> --wait 30 --interval 2
```

For full message payloads:

```bash
agent-email read <email|default> --full
```

4. Retrieve one message in detail.

```bash
agent-email show <email|default> <messageId>
```

Use `show` when you need body/source details for verification links, codes, or full content extraction.

5. Manage mailbox profiles.

```bash
agent-email accounts list
agent-email use <email|default>
agent-email accounts remove <email>
```

Avoid commands that require entering secrets on the command line in agent logs.

6. Delete processed/irrelevant message when requested.

```bash
agent-email delete <email|default> <messageId>
```

## Operational Guidance

- Keep command output machine-readable; avoid forcing human output unless requested.
- Prefer `default` alias when user does not specify an email.
- Never echo, store, or summarize secret values (`password`, `token`) from command output.
- If command fails, surface the JSON error `code` and `hint` fields directly.
- For auth failures (`AUTH_REQUIRED`/401), rerun command once and request user intervention if credentials must be re-established.
- For rate limits (`RATE_LIMITED`/429), retry after short delay.

## Troubleshooting

- `command not found`: ensure `~/.bun/bin` or npm global bin path is on `PATH`.
- `NO_ACTIVE_ACCOUNT`: run `agent-email create` or `agent-email use <email>`.
- `ACCOUNT_NOT_FOUND`: run `agent-email accounts list` and pick a valid address.
- `EOTP` during npm publish: use npm trusted publishing for CI or publish locally with OTP.

## References

- For command cheat sheet and JSON field map, read [references/commands.md](references/commands.md).
