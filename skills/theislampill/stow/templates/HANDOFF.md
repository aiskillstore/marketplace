# Handoff: dual-write landed, backfill phase next

Worked-example template for the agent-handoff class. An orchestrator finishing a
bounded phase transfers control to a fresh subagent that has no access to this
transcript. The receiver must reconstruct goal, what is done, what is not, the
constraints, the single next action, the artifacts, and the open risks from this
file alone. The fenced block below is the machine-readable instance; it validates
against `skills/stow/schemas/handoff.schema.json`.

The scenario is a fictional service, `cart-session-store`, moving its session
store to a durable backend. The commit ids and paths are illustrative
placeholders.

## Next action

Run the backfill in dry-run mode against a staging copy and record the count of
sessions it would insert, before enabling any write.

## Done

- Sessions write to both the cache and the durable backend behind the
  migrate_sessions flag.
- The read path prefers the durable backend and falls back to the cache on a miss.
- The dual-write path has integration coverage for create, update, and expire.

## Not done

- Historical sessions are not backfilled into the durable backend.
- The cache still serves as the source of truth.

## Constraints

- Keep the migrate_sessions flag default-off until the backfill is verified.
- Do not delete any cache entry during the migration.
- The durable backend keeps one row per session id.

## Open risks

- A backfill without an idempotency guard can double-count sessions on retry.
- Clock skew between writers can reorder create and expire under dual-write.

```yaml
schema_version: 1
profile: technical-clarity
handoff_id: HO-dualwrite-to-backfill
from_actor: orchestrator
to_actor: subagent-backfill
created_ts: "2031-03-04T15:10:00Z"
goal: >-
  Migrate cart-session-store to a durable backend so sessions survive a restart,
  without losing or duplicating any active session.
plan_ref: skills/stow/templates/PLAN.md
done:
  - claim: sessions dual-write to the cache and the durable backend
    evidence_ref: "command: pytest services/cart-session-store/tests/test_dualwrite.py"
  - claim: the read path prefers the durable backend with a cache fallback
    evidence_ref: "file-line: services/cart-session-store/reader.py:48"
  - claim: dual-write integration coverage exists for create, update, and expire
    evidence_ref: "command: pytest services/cart-session-store/tests/ -k dualwrite"
not_done:
  - historical sessions are not backfilled into the durable backend
  - the cache still serves as the source of truth
constraints:
  - keep the migrate_sessions flag default-off until backfill is verified
  - do not delete any cache entry during the migration
  - the durable backend keeps one row per session id
next_action: >-
  Run the backfill in dry-run mode against a staging copy and record the count of
  sessions it would insert, before enabling any write.
artifacts:
  - path: services/cart-session-store/writer.py
    role: dual-write entry point behind the migrate_sessions flag
  - path: services/cart-session-store/backfill.py
    role: backfill job the next phase runs and hardens
  - path: services/cart-session-store/reader.py
    role: read path with durable-first, cache-fallback lookup
open_risks:
  - a backfill without an idempotency guard can double-count sessions on retry
  - clock skew between writers can reorder create and expire under dual-write
acceptance_for_next: >-
  The backfill runs idempotently against staging, the durable session count
  matches the cache count within the reconciliation window, and no cache entry
  was deleted.
```
