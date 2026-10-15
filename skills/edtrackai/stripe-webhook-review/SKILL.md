---
name: stripe-webhook-review
description: Review Next.js Stripe webhook route handlers for missing signature verification, JSON parsed before verification, missing or non-status-aware idempotency on event.id (pending/completed), unsafe reprocessing of pending events, and billing periods read from items.data[0]. Use when the user asks to review a Stripe webhook, idempotency, duplicate events, or payments before launch.
allowed-tools: Read Grep Glob
---

# stripe-webhook-review

Read-only review. Don't edit files unless the user asks for the fixes afterwards.

## Scope
Find the handlers: `grep -rl "constructEvent\|stripe-signature\|webhooks" app/ src/ pages/` (route handlers under `app/api/**/route.ts` or `pages/api/**`). Read each one and the helpers it calls (claim/complete functions, sync functions).

## Checks
For each finding, give file:line, the check id, severity, and the fix.

| Id | Severity | Look for | Fix |
|---|---|---|---|
| S1 | critical | No `stripe.webhooks.constructEvent(...)` (or `constructEventAsync`) before the event is trusted | Verify `constructEvent(rawBody, signature, secret)` first; return 400 on failure. |
| S2 | critical | `await request.json()` (or a parsed body) used before or instead of the raw body | `const body = await request.text()` and pass that string to `constructEvent`. |
| S3 | medium | `event.id` never recorded (no `stripe_events`/processed-events table) | Record `event.id` (unique) before processing; see the idempotency rule below. |
| S6 | medium | Dedupe without status: any already-seen `event.id` returns 200 (e.g. on `23505`), or claim-then-delete | A first attempt that failed or crashed is lost forever. Use the pending/completed rule below. |
| S7 | low | Billing period read from `subscription.items.data[0]` | Since API `2025-03-31.basil`, periods live on subscription items; `items.data[0]` is only right for single-item subscriptions. Use the item whose price grants the entitlement. |

### Idempotency rule (for S3 and S6)
Record `event.id` in `stripe_events` with `status = 'pending'`. On a unique violation (`23505`), read the row: if `completed`, return 200 and stop; if still `pending`, process it again. That is only safe when overlapping deliveries can't double-apply work: handlers must be idempotent upserts keyed on Stripe ids, or the row must be claimed atomically with a lease, for example:

```sql
update stripe_events set locked_until = now() + interval '5 minutes'
where id = $1 and status = 'pending' and (locked_until is null or locked_until < now());
-- skip if no row was claimed
```

so a crashed attempt can be reclaimed later. Give side effects such as emails or credit grants their own dedupe key. Set `status = 'completed'` only after processing (or enqueueing) succeeds. If processing fails, return 5xx so Stripe retries.

When you see pending events being reprocessed, check the handlers: flag it only if they do non-idempotent work (inserts without a unique key, emails, credit grants) with no lease and no dedupe key.

### Also note (not scored)
- `export const runtime = "edge"` on the webhook route: prefer the Node.js runtime for the Stripe SDK.
- A user id taken from event metadata or `client_reference_id` is fine when your server set it at checkout; a client-supplied user id is only a finding when the server doesn't verify it.

## Report
1. One line: handlers reviewed and findings by severity.
2. A table: severity, id, file:line, what you saw, fix.
3. Anything you couldn't verify (helpers in other packages, queue workers).

These are heuristics: each finding is a prompt to review, not proof of a vulnerability.
