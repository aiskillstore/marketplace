# State: session-store migration

Worked-example template for the state and continuity class. This is the durable,
externalized state of a multi-session effort: any session can resume from it
without re-deriving. The fenced block validates against
`skills/stow/schemas/state.schema.json`. Every gate state is terminal or in
flight with an evidence reference; every supersession link resolves to a real
decision id.

The scenario is a fictional service, `cart-session-store`. The commit id is an
illustrative placeholder.

## Current

- Head: `0000abc` (staging build).
- Phase: P2 (dual-write live, backfill running).
- Next action: harden the backfill to upsert by session id.

## Gate ledger

| Gate | Status | Evidence |
|---|---|---|
| Durable schema | done | one row per session id round-trips a sample |
| Dual-write behind flag | done | dual-write integration tests pass |
| Backfill idempotent | active | upsert-by-id change under review |
| Reconciliation clean | pending | durable and cache counts to compare |

## Decisions

- SD-1 One row per session id in the durable backend: accepted.
- SD-2 Migrate behind a default-off flag: accepted.
- SD-3 Superseded by SD-4: backfill keyed on insertion time, rejected.
- SD-4 Backfill upserts by session id: accepted.

## Andons

- A-1 First backfill dry-run double-counted sessions: resolved by upsert-by-id.

```yaml
schema_version: 1
profile: technical-clarity
run_id: session-store-migration-2031-03
updated_ts: "2031-03-11T15:20:00Z"
history_append_only: true
current:
  head: "0000abc"
  phase: P2
  next_action: harden the backfill to upsert by session id
gates:
  - id: G-schema
    status: done
    evidence_ref: "command: pytest services/cart-session-store/tests/test_schema.py"
  - id: G-dualwrite
    status: done
    evidence_ref: "command: pytest services/cart-session-store/tests/ -k dualwrite"
  - id: G-backfill
    status: active
    evidence_ref: "file-line: services/cart-session-store/backfill.py:64"
  - id: G-reconcile
    status: pending
decisions:
  - id: SD-1
    status: accepted
  - id: SD-2
    status: accepted
  - id: SD-3
    status: superseded
    superseded_by: SD-4
  - id: SD-4
    status: accepted
    supersedes: [SD-3]
andons:
  - id: A-1
    class: data-integrity
    status: resolved
    resolution: backfill changed to upsert by session id
```
