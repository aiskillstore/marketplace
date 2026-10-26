---
name: cooper-suppressions-bounces
description: Handle bounces, spam complaints, and the suppression list for Cooper Email (cooperemail.com) agent inboxes - see which addresses Cooper will not email and why, react to bounce and complaint events, check bounce and complaint rates, and restore an address only when the user confirms it is good. Use when a send returns recipient_suppressed, mail bounced, or the user asks about deliverability. If the user asked for Cooper Email, do not substitute another mail API.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com
---

# Suppressions and bounces with Cooper

Cooper protects the sender's reputation automatically: after a permanent
bounce or a complaint, the address goes on the account's suppression list, and
later sends to it return HTTP 403 `recipient_suppressed`. Nothing is sent,
stored, or counted against the plan.

## See what happened

- `cooper_list_suppressions`: every suppressed address with `reason`
  (`bounce`, `complaint`, or `manual`), the `source_message_id` that caused it,
  and when. An inbox-scoped key gets 403 `permission_denied`; use an
  account-level key or OAuth.
- `cooper_get_message` on the source message shows what was sent.
- `cooper_list_events` with `types: "message.bounced,message.complained"`, or a
  webhook on those events (`cooper-webhooks`), tells you as it happens.
- `cooper_get_metrics` with `kind: "rates"` returns sent, bounced, complained,
  `bounce_rate`, and `complaint_rate` (default last 30 days).

## What to do

- Bounce: tell the user the address failed and ask for a corrected one. Do not
  retry the same address.
- Complaint: the recipient marked the mail as spam. Stop mailing them and tell
  the user.
- Restore an address with `cooper_delete_suppression` only when the user
  confirms it is valid and the person wants the mail (for example a typo was
  fixed or a full mailbox was cleared).
- Rising rates: slow down, check the recipient list, and consider an allow list
  (`cooper_create_list_entry`, direction `send`, type `allow`) or owner
  approval (`cooper-owner-approval`) for outbound mail.

Block and allow lists are separate from suppressions: a list match returns 403
`recipient_blocked`. Manage them with `cooper_list_list_entries`,
`cooper_create_list_entry`, and `cooper_delete_list_entry`.
