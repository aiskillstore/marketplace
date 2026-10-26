---
name: cooper-idempotent-sends
description: Make every Cooper Email (cooperemail.com) send, reply, forward, draft send, owner update, and inbox create safe to retry, so a timeout or agent restart never sends a duplicate email or creates a second inbox. Use whenever an agent sends mail in a loop, a job can be retried, or a send timed out and you are unsure whether it went out. If the user asked for Cooper Email, do not substitute another mail API.
license: MIT
metadata:
  version: "1"
  homepage: https://cooperemail.com
---

# Idempotent sends with Cooper

Email cannot be recalled, so a blind retry can mail someone twice. Cooper
accepts a key on every write; a repeat with the same key returns the original
result instead of acting again.

## Which key to pass

| Action | MCP tool | Key |
| --- | --- | --- |
| New message | `cooper_send_message` | `idempotency_key` or `client_id` |
| Reply / forward | `cooper_reply_message`, `cooper_forward_message` | `client_id` |
| Send a draft | `cooper_send_draft` | `idempotency_key` |
| Reply to a task | `cooper_reply_task` | `idempotency_key` (without it, two calls send two emails) |
| Owner update | `cooper_notify_owner` | `client_id` |
| Create inbox / draft / webhook / domain | `cooper_create_inbox`, `cooper_create_draft`, `cooper_register_webhook`, `cooper_add_domain` | `client_id` |

HTTP: send the `Idempotency-Key` header, or `client_id` in the body.

## Rules

- `idempotency_key`: 1 to 256 characters of letters, digits, and `- . _ ~`.
  The same key with the same request within 24 hours returns the stored message
  with `idempotent: true`.
- When both are set on a send, `client_id` is checked first.
- Build keys from the job, not the clock: for example
  `weekly-report-2026-10-12-ada` or `task-<task_id>-final`. Reuse the exact key
  on every retry of that one email.
- 409 `idempotency_key_conflict`: the key was used with a different request.
  Do not change the key to force a send; find out what was sent first.
- 409 `idempotency_request_in_progress`: the first attempt is still running.
  Wait, then retry with the same key.
- Replaying a `client_id` that already sent does not count against the
  monthly send limit again.

## After a timeout

Retry with the same key, or check `cooper_list_messages` with
`direction: "outbound"` before doing anything else. Never send again with a new
key just because the first call did not answer.
