---
name: schedules
description: Keep a SpecStream list current on a schedule, hourly to yearly, within a limit per run and per month, and send new and changed records to a signed webhook, Slack or a connected tool.
---

# Keep a list current on a schedule

SpecStream is the live web data engine for teams and agents. Use the configured MCP server at `https://api.specstream.ai/mcp`.

A schedule (a monitor) reruns a request on the live web at a set cadence and labels each record: still matches, no longer matches, unresolved or unavailable. A refresh costs half the row rate for a row that changed and 1 cent for a row that did not.

## Set it up

1. Read the request with `compile` and show the person how it was read. Price it with `quote_capacity_work`.
2. Agree on the cadence and the limits with the person before any write: how often it runs (`cadence_seconds`, at least 3600, or a `calendar_schedule`), the first run (`first_due_at`), the end date (`valid_until`), the most one run can spend (`per_run_cents`) and the most it can spend in one UTC calendar month (`period_cents`).
3. `create_capacity_schedule` is a write. Call it only after the person says yes to those limits, with the priced scope and a stable `idempotency_key`. The response shows `monthly_maximum_cents` and `scheduled_monthly_cents`; show both to the person.

Creating a schedule does not fund it. A balance or a schedule is never permission to spend more than the agreed limits. A blocked or missed run is not an unchanged result and is not bought later.

## Deliver to a webhook

`set_schedule_delivery` chooses where new and changed records go: `notify` (SpecStream notifications), `slack` (a channel of the one connected Slack workspace), `sendTo` (a connected tool) or `webhook` (an HTTPS URL). It needs the schedule's current `expected_version` from `list_capacity_schedules`. Nothing runs when delivery is set. Slack and webhook delivery need a plan that includes deliveries: check `get_capacity_entitlements` first.

The response shows the webhook signing secret once. Ask the person to store it; never print it again or put it in code. Each delivery is a JSON POST with the headers `Specstream-Event-Id` and `Specstream-Signature: t=<unix time>,v1=<hex>`, where `v1` is the HMAC-SHA256 of `<t>.<raw body>` with the signing secret. The receiver checks the signature and the time before it trusts the body, and uses the event id to drop repeats.

For a webhook on other events of the account (a run finished, a monitor found something, records added), use `create_webhook` with `events`.

## Watch and change it

- `list_capacity_schedules` shows each schedule, whether it is running or paused, and its limits.
- `list_capacity_occurrences` shows each completed, blocked and missed run with its reason.
- `get_collection_changes` shows each changed fact, before and after, with the page where the new value was seen.
- `update_capacity_schedule` pauses, resumes or deletes a schedule with its `expected_version`. Do this when the owner says so.
