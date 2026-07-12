# Creator Projection View Template

This is a presentation template for `memory/creators/<aggregate-id>.md`. The canonical history is `memory/events/creators.ndjson`; current state is `memory/projections/creators.json`. Generate this view only from accepted events and expose its source revision/offset.

Use a pseudonymous aggregate ID. Do not put raw email, phone, postal address, credentials, or unnecessary personal history in the event or view.

```yaml
---
type: creator-projection-view
aggregate_id: creator-7f42
projection_revision: 4
projection_offset: 18
last_event_id: 2bf09d16-9ab8-5a93-a579-3bc4f85a027e
last_updated: 2026-07-10
status: active
---
```

## Identity Links

| Platform | Public handle ref | Link status | Evidence ref/date |
|---|---|---|---|
| Instagram | profile-ref-82 | confirmed | verified-crosslink-2026-06-01 |
| TikTok | profile-ref-91 | unconfirmed | none |

Similarity alone never confirms identity.

## Commercial Facts

| Field | Value | As-of | Evidence type/ref |
|---|---|---|---|
| Agreed rate | USD 1,900 / defined bundle | 2026-05-18 | user-provided / signed-terms-41 |
| Usage rights | organic, 6 months | 2026-05-20 | measured / contract-41 |
| Exclusivity | skincare to 2026-08-30 | 2026-05-20 | measured / contract-41 |

## Outcome Baselines

Keep campaign/window/denominator/source explicit. Platform reports and deduplicated own outcomes remain separate.

## Compliance Events

List dated C3 ART artifact IDs and observed events. Never summarize them into a “safe”, “risky”, or reputation label.

## Proposal Decisions

| Proposal event ID | Decision event ID | Decision | Rationale |
|---|---|---|---|

Resolved proposals remain in the append-only stream. Never add a “processed/cleared” instruction.

## Conflict Rule

Compare only the same field/unit/window. Newer evidence does not automatically dominate a different construct. For comparable same-date conflicts, prefer stronger direct evidence when defensible and preserve both source events plus the adjudication rationale. Identity merges require verified cross-links or user confirmation.
