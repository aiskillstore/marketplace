# Manage Recurring Dates And Reminders

CLI and MCP share epoch ms, ISO with Z/offset, YYYY-MM-DD, DD.MM.YYYY,
today/yesterday/tomorrow and signed day offsets (+3d/-2d).
Date-only values keep their day with UTC boundaries; keywords use the process
local date. Read occurredOn/dueOn and review occursOn for calendar dates;
*Iso fields stay UTC. Future events warn and count as contact only when their
time and day arrive. Commitments and resolutions never reset recency/cadence.
Radar explains overdue promises and drift (gap > 1.5 times cadence).

Primary tools:
- `manage_date_anchor`
- `review_affinity`
- `inspect_affinity_item`

Goal:
- Materialize recurring important dates into a durable reminder surface that later review and relationship maintenance can trust.

When to use:
- A date recurs yearly and matters to a contact or link.
- You want reminders for birthdays, anniversaries, renewals, memorials, or other yearly anchors.

When not to use:
- The date is a one-off event.
- The fact is a preference or metadata note rather than a recurring anchor.

Step-by-step sequence:
1. Confirm the target contact or link first.
2. Use `manage_date_anchor` with `action: "add"` and the right recurrence kind.
3. Keep the summary operator-friendly so future reminders are immediately understandable.
4. Use `review_affinity` with the upcoming-dates view and an explicit horizon during regular review work.
5. Revise anchors when recurrence details change.
6. Remove anchors when the reminder surface should no longer treat the date as active.

Validation checks:
- The anchor appears in upcoming-date review when it falls within the chosen horizon.
- Duplicate anchors are not silently piling up.
- The summary and significance are still meaningful for later action.

Pitfalls:
- Do not store important recurring dates only as loose attributes.
- Do not create duplicate yearly anchors for the same target and meaning.
- Do not use recurring anchors for commitments; those belong in the commitment flow.

Tips and tricks:
- Tune horizons by workflow: short for weekly review, longer for quarterly planning.
- Use significance to help order upcoming-date review meaningfully.
- Link-level anchors are valuable when the date belongs to a relationship rather than one person.

Tool calls to prefer:
- `manage_date_anchor` for add, revise, and remove
- `review_affinity` with the upcoming-dates view
- `inspect_affinity_item` when you need exact context on the target

Related skills:
- `manage-promises-and-agreements`
- `review-radar-progression-and-graph`