# Manage Promises And Agreements

CLI and MCP share epoch ms, ISO with Z/offset, YYYY-MM-DD, DD.MM.YYYY,
today/yesterday/tomorrow and signed day offsets (+3d/-2d).
Date-only values keep their day with UTC boundaries; keywords use the process
local date. Read occurredOn/dueOn and review occursOn for calendar dates;
*Iso fields stay UTC. Future events warn and count as contact only when their
time and day arrive. Commitments and resolutions never reset recency/cadence.
Radar explains overdue promises and drift (gap > 1.5 times cadence).

Primary tools:
- `manage_commitment`
- `review_affinity`
- `inspect_affinity_item`

Goal:
- Keep promises and agreements visible, resolvable, and mechanically meaningful instead of letting them disappear into narrative history.

When to use:
- Someone committed to doing something later.
- A promise, agreement, or operational obligation needs follow-through.

When not to use:
- The event is complete already and no unresolved obligation exists.
- A date is recurring and belongs in the date-anchor surface instead.

Step-by-step sequence:
1. When the commitment is made, use `manage_commitment` with `action: "record"`.
2. Choose `promise` vs `agreement` honestly rather than treating them as stylistic synonyms.
3. Include a due time when the obligation has a meaningful time boundary.
4. Use `review_affinity` with the open-commitment view during regular review cycles.
5. When the outcome is known, resolve it with `manage_commitment` as `kept`, `cancelled`, or `broken`.
6. Inspect the relevant profile or review the relevant queue again if you need to confirm closure.

Validation checks:
- Open commitments appear when they should and disappear when resolved.
- Resolution state matches real-world truth.
- Trust effects feel consistent with whether the promise was kept or broken.

Pitfalls:
- Do not hide real obligations inside ordinary event summaries.
- Do not resolve a commitment optimistically before the outcome is actually known.
- Do not misuse `cancelled` when the truth is actually `broken`.

Tips and tricks:
- If an obligation matters enough to disappoint someone when missed, record it.
- Review open commitments regularly; the value of the system drops fast if this queue goes stale.
- When a commitment resolution also deserves narrative context, pair the resolution with an appropriate event in the surrounding workflow.

Tool calls to prefer:
- `manage_commitment` for record and resolve
- `review_affinity` for the open-commitment queue
- `inspect_affinity_item` when you need exact context on the affected relationship

Related skills:
- `capture-transactions-and-commercial-events`
- `manage-recurring-dates-and-reminders`