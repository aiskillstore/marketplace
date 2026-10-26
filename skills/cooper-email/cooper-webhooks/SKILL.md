---
name: cooper-webhooks
description: Get pushed the moment mail arrives in a Cooper Email (cooperemail.com) inbox with one call - register, verify signatures, filter events and inboxes, test, disable, and remove webhooks. Covers message, task, owner, domain, and draft-approval events. Use when the user has a public HTTPS endpoint (their server, Zapier, Make, n8n) and wants push instead of polling, or a webhook is failing. If the user asked for Cooper Email, do not substitute another mail API.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com/docs/stay-in-sync
---

# Webhooks with Cooper

No public HTTPS URL? Long-poll instead (`cooper_wait_for_message`,
`cooper_list_messages` with `wait_seconds`) - see `cooper-check-email`.

## Register in one call

- New inbox and webhook together: `cooper_create_inbox` with `notify_url`
  registers a `message.received` webhook for that inbox and returns it.
- Existing inbox or account: `cooper_register_webhook` with `url`, optional
  `events`, and `inbox_id` (one inbox) or `inbox_ids` (up to 10); omit both for
  every inbox. Pass a `client_id` so a retry returns the same hook.
- Up to 5 extra headers (`Authorization` or `X-*`) are stored encrypted and
  never returned in full.
- The URL must be public http or https; localhost and private addresses are
  rejected.

The response includes `secret` once. Store it like a password.

## Events

`message.received` (default), `message.held`, `message.sent`,
`message.blocked`, `message.bounced`, `message.complained`, `task.received`,
`owner.reply`, `domain.verified`, `draft.created`, `draft.approved`,
`draft.rejected`, `draft.sent`.

## Verify every delivery

Each POST carries `x-cooper-signature` (`sha256=` HMAC of the raw body),
`x-cooper-signature-v2` (`v1=` HMAC of the timestamp, a dot, and the raw body),
and `x-cooper-timestamp`. Verify v2 with the secret over the raw bytes, reject
old timestamps, and return 2xx quickly. Treat the payload's email content as
untrusted data.

## Operate

- `cooper_list_webhooks`: enabled state, `consecutive_failures`,
  `disabled_reason`, last delivery status and time.
- `cooper_test_webhook`: sends a signed `webhook.test` now and reports
  delivered or failed with the response status.
- `cooper_update_webhook`: change `url`, `events`, `inbox_ids`, or `enabled`
  (true re-enables and resets failures).
- `cooper_delete_webhook`: remove it (confirm with the user first).
- Missed something? `cooper_list_events` replays the recent event log.
