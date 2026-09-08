# Runbook: cut over the session store to the durable backend

Worked-example template for the runbook class. An operator executes this under
time pressure, so every step is a single imperative. Every step that can fail
carries a `verify` and a `rollback`. Every safety step states a risk level and
its consequence. Commands are protected literals: copy them exactly. The fenced
block is the machine-readable step list.

The scenario is a fictional service, `cart-session-store`. Every command is
illustrative.

## Preconditions

- The backfill has completed and reconciliation reported zero drift.
- The migrate_sessions flag is present and default-off.

## Steps

1. Run the session-store test suite.
   - Verify: the suite exits zero.
   - Rollback: none (read-only).
2. Run reconciliation between the cache and the durable backend.
   - Verify: the drift count is zero.
   - Rollback: none (read-only).
3. Enable durable reads by turning on the migrate_sessions flag.
   - Verify: read latency stays within budget and the error rate is flat.
   - Rollback: turn the migrate_sessions flag off.
4. CAUTION (medium): disabling the cache write makes the durable backend the only
   store. Consequence: a durable outage now drops session writes. Disable the
   cache write only after step 3 has held for one full traffic peak.
   - Verify: new sessions appear only in the durable backend.
   - Rollback: re-enable the cache write and keep dual-write.

## Success check

Reads resolve from the durable backend, new sessions land only there, and the
reconciliation job reports zero drift.

## Safety

- CAUTION (high): never truncate the durable session table. Consequence: every
  active session is lost and users are signed out.
- To undo the cutover, turn the migrate_sessions flag off and restore dual-write.
  Do not delete any row.

```yaml
schema_version: 1
profile: controlled-technical-guided
runbook_id: RB-session-store-cutover
preconditions:
  - backfill complete and reconciliation reports zero drift
  - the migrate_sessions flag is present and default-off
steps:
  - n: 1
    action: run the session-store test suite
    verify: the suite exits zero
    rollback: none
    risk: none
  - n: 2
    action: run reconciliation between the cache and the durable backend
    verify: the drift count is zero
    rollback: none
    risk: none
  - n: 3
    action: enable durable reads by turning on the migrate_sessions flag
    verify: read latency stays within budget and the error rate is flat
    rollback: turn the migrate_sessions flag off
    risk: low
  - n: 4
    action: disable the cache write so the durable backend is the only store
    verify: new sessions appear only in the durable backend
    rollback: re-enable the cache write and keep dual-write
    risk: medium
    consequence: a durable outage now drops session writes
success_check: reads resolve from the durable backend and reconciliation reports zero drift
```
