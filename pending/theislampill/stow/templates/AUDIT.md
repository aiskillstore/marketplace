# Audit: session-store migration readiness

Worked-example template for the audit and evidence class. A read-only reviewer
produces findings a decision-maker acts on. FACTS are separated from
RECOMMENDATIONS; every record carries a verifiable locator and reaches a terminal
disposition: no orphan findings. The fenced block validates against
`skills/stow/schemas/evidence-record.schema.json`. A `fact` needs at least one
resolvable locator; a `finding` with `verified: true` needs a `failure_scenario`;
`disposition` is one of the terminal set
`{fixed, already-covered, rejected-with-evidence, owner-decision, blocked, deferred}`.

The subject is a fictional service, `cart-session-store`, migrating its session
store from an in-process cache to a durable backend. The commit ids and paths are
illustrative placeholders.

## Verdict

The dual-write path is sound, but the backfill keys on insertion time, so a
retried run re-copies sessions and the durable backend over-counts them. One
fixed finding, one recommendation, one confirmed fact.

## Facts

- New sessions write to both the cache and the durable backend behind one flag.

## Findings

- The backfill re-inserts a session it already copied, because it keys on
  insertion time rather than the session id.

## Recommendations

- Make the backfill upsert by session id so a retried run stays idempotent.

```yaml
records:
  - record_id: F-1
    kind: fact
    statement: >-
      New sessions are written to both the in-process cache and the durable
      backend behind the migrate_sessions feature flag.
    locators:
      - {type: file-line, value: "services/cart-session-store/writer.py:120"}
      - {type: command, value: "grep -n migrate_sessions services/cart-session-store/writer.py"}
    severity: info
    disposition: already-covered
    verified: true
  - record_id: N-1
    kind: finding
    statement: >-
      The backfill keys on insertion time, so a retried run re-copies a session
      it already migrated and the durable backend counts it twice.
    locators:
      - {type: command, value: "python -m cart_session_store.backfill --dry-run"}
    severity: high
    disposition: fixed
    verified: true
    failure_scenario: >-
      A worker restarts mid-backfill, the run resumes from the last checkpoint,
      and every session after that checkpoint is inserted a second time, so the
      active-session count reads high until the next reconciliation.
  - record_id: R-1
    kind: recommendation
    statement: >-
      Change the backfill to upsert by session id so a retried run converges to
      one row per session no matter how many times it runs.
    locators:
      - {type: file-line, value: "services/cart-session-store/backfill.py:64"}
    severity: medium
    disposition: owner-decision
    verified: false
```
