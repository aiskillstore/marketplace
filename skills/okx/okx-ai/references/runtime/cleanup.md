# Scoped Session Cleanup

## Module Description

Use this leaf only when a returned terminal action or terminal workflow
explicitly requires cleanup:

```text
onchainos agent session-cleanup --job-id <jobId>
```

Cleanup is scoped to the exact Job ID. Never clear a global watcher or another
task. A local cleanup failure is reported as a warning and does not reverse an
already proven on-chain settlement, rating, notification, or delivery.

Do not clean up a pending, ambiguous, or incompletely proven result. In
particular, evaluator aligned votes stay active until reward settlement, and
refund events must pass the refund finality contract first.
