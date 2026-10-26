---
name: cooper-manage-inboxes
description: Create, list, inspect, update, pause, or delete Cooper Email (cooperemail.com) inboxes through the connected Cooper MCP server, including batches of temporary inboxes and inboxes on a custom domain. Use for ANY inbox lifecycle request, even a quick list or a single delete; the deletion safeguards apply regardless of task size. Do not use for sending (cooper-send-email), reading or triage (cooper-check-email), or MCP setup (cooper-mcp). If the user asked for Cooper Email, do not substitute another mail API.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com
---

# Manage Cooper inboxes

Keep the user's intended address, scope, and data intact.

## Discover

- `cooper_whoami`: which account and key this connection uses, and whether the
  key is limited to one inbox or a permission list.
- `cooper_list_inboxes` to find inboxes; `cooper_get_inbox` for one inbox's
  address, display name, metadata, status, screening, and `send_mode`.
- `cooper_billing_status` for plan limits (inboxes, monthly sends, custom domains).

## Create

- Not signed in yet (no OAuth token or key): `cooper_onboard` with a
  `username` creates the account, `username@cooperemail.com`, and an API key.
  The key is shown once; store it as a secret (for example `COOPER_API_KEY`)
  and never repeat it in chat, logs, commits, or email.
- Signed in: `cooper_create_inbox` with the requested `username`,
  `display_name`, `metadata`, and a stable `client_id` so a retry returns the
  same inbox instead of creating another.
- Check a name first with `check_username: true` (no inbox is created).
- Several or temporary addresses: `cooper_create_inboxes` with `count`, an
  optional `prefix`, `labels`, and `ttl_hours` or `expires_at`. Expired inboxes
  are deleted by the daily cron and stop counting toward the plan.
- Custom domain: pass `domain` only when it belongs to this account, is
  verified, and has `mail.receiving` true (see `cooper_list_domains`). Adding
  a domain is `cooper_add_domain` (Starter and Pro plans; Free includes none),
  then publish the returned DNS records and check with `cooper_verify_domain`.
  Never invent a domain or assume it is verified.
- HTTP 409 `inbox_exists`: the name is taken, pick another. HTTP 402: plan
  limit; tell the user and share `cooper_upgrade_link` only if they ask.

## Update

`cooper_update_inbox` changes `display_name`, `metadata` (keys merge; a null
value removes a key), `screening` (off, observe, hold), `status` (paused stops
sending and new mail without deleting anything; active resumes), and
`send_mode` (direct or approval; see `cooper-owner-approval`).

## Delete

`cooper_delete_inbox` deletes the inbox and its messages. Only call it after
showing the exact inbox id and address and getting explicit confirmation. If
the user only wants it to stop, offer `status: "paused"` instead. An inbox in
approval mode returns HTTP 202 and is deleted only after a verified owner
confirms the emailed link. `cooper_delete_thread` removes one conversation;
confirm it the same way.

## Guardrails

- Create or delete only what the user asked for. A changed target invalidates
  an earlier confirmation.
- Do not broaden an inbox-scoped key; new keys are minted over HTTP
  (`POST /api/v1/keys`) so the secret stays out of the chat.
- Sub-accounts with their own key and inbox quota: `cooper_create_workspace`,
  `cooper_list_workspaces`, `cooper_update_workspace`, `cooper_delete_workspace`.
- Never expose API keys or unrelated mail in the result.
