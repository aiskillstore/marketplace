# Open Gaps

## Ledger Rules

- Allowed statuses: `Open`, `Resolved`, `Closed`, `Reclassified non-critical`, `None`.
- A gap cannot remain `Open` after the phase named in its owner or next-action field has passed.
- Phase 7 fails if any critical gap is still `Open`, stale, or contradicted by another phase artifact.
- When a later phase fixes or defends a gap, update this file in that same phase.
- `Pending` is a template placeholder, not a valid ledger status after Phase 0.
- If there are no gaps, use `None currently recorded` rows.

## Critical Gaps

| Gap | Phase found | Status | Owner/next action | Evidence |
| --- | --- | --- | --- | --- |
| None currently recorded | Phase 0 | None | Recheck every phase | Fresh ledger; replace this row immediately when a critical gap is found |

## Non-Critical Gaps

| Gap | Phase found | Status | Defense/next action | Evidence |
| --- | --- | --- | --- | --- |
| None currently recorded | Phase 0 | None | Recheck every phase | Fresh ledger; replace this row immediately when a non-critical gap is found |

## Resolved Gaps

| Gap | Resolved in phase | Fix | Evidence |
| --- | --- | --- | --- |
| None currently recorded | Phase 0 | None | No resolved gaps yet |
