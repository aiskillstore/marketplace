# Reliability, concurrency, and data lens

Trigger: persistence, migrations, queues, retries, timeouts, shared state, external side effects, or multi-process systems.

## Map durable state and commit boundaries

Write the operation as a sequence of reads, writes, external calls, acknowledgments, and commits. Ask what survives if the process stops between each pair. Identify the authoritative state and the invariant joining records. Determine which steps can be retried and what identifies the same logical operation.

Inject failure before and after durable writes, acknowledgment, message publication, and external side effects. Check crash recovery, repeated delivery, lost responses after successful commit, reordered callbacks, delayed old writes, lease expiry, and cancellation after partial success. An error response must not imply rollback when the operation already committed.

## Concurrency questions

Which interleavings violate a uniqueness, balance, quota, ordering, or ownership invariant? Is a precheck separated from the write it protects? Which database isolation/constraint behavior is actually configured? Do locks cover all writers, including background jobs and separate instances? Are lock scopes, expiry, fencing, and deadlock behavior adequate for the actual coordination mechanism?

Distinguish a local mutex from a distributed invariant. Distinguish at-least-once delivery from exactly-once effects. Do not claim exactly-once behavior from the presence of a retry loop or message ID alone. Use controlled barriers or deterministic schedules rather than unexplained sleeps in tests.

## Data and migration questions

Inspect schema constraints, nullability, precision, encoding, foreign keys, deletion semantics, rollback, backfill idempotency, partially migrated state, old/new client coexistence, version skew, and backup restoration. Test both empty and populated databases, malformed legacy records, duplicate history, and interrupted migrations when relevant. Do not execute destructive migrations without explicit authorization and a recoverable test environment.

For exports/imports, verify count and balance reconciliation, duplicate handling, deterministic ordering, escaping, formula injection where relevant, and failure atomicity. For financial-like calculations, define units and rounding from requirements rather than guessing.

## Temporal and distributed edge cases

Clock skew; monotonic versus wall-clock deadlines; daylight-saving transitions; stale caches; tombstone resurrection; retries after timeout; unbounded exponential backoff without deadlines; queue visibility timeout shorter than processing; connection loss during commit; rolling deployments with incompatible payloads.

## Evidence and repair re-attack

Collect before/after state, the exact interruption/interleaving, the observed client result, and repeated-operation behavior. A test should check persistent state as well as returned values. The repair must protect the invariant at the correct durability/concurrency boundary. Re-attack another interruption point and verify recovery, not merely successful retry in an ideal environment.
