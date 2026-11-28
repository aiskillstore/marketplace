# Reliability and recovery

- [Circuit breakers for dependency failure](../knowledge/reliability/circuit-breaker.md) · Constrain repeated attempts to a dependency whose health is below the service's tolerance.
- [Poison messages and dead-letter handling](../knowledge/reliability/dead-letter-queues.md) · Isolate work that cannot complete while preserving diagnostics and controlled replay.
- [Recovery objectives and restore verification](../knowledge/reliability/disaster-recovery.md) · Align backups and failover with stated recovery-point and recovery-time objectives.
- [Distributed tracing and sampling](../knowledge/reliability/distributed-tracing.md) · Connect a slow or failed user interaction to its upstream and downstream work with affordable trace coverage.
- [Graceful shutdown and work draining](../knowledge/reliability/graceful-shutdown.md) · Stop accepting new work, finish safe in-flight operations and leave unfinished work recoverable.
- [End-to-end deadlines and timeouts](../knowledge/reliability/outbound-timeouts.md) · Bound a dependency's latency and make cancellation meaningful through the whole request path.
- [Stateful failover and split-brain prevention](../knowledge/reliability/primary-failover.md) · Restore a stateful service after failure while preventing concurrent leaders from applying conflicting updates.
- [Readiness, liveness and startup checks](../knowledge/reliability/readiness-liveness.md) · Route traffic only to ready instances without restarting healthy processes during dependency incidents.
- [Retry budgets, backoff and jitter](../knowledge/reliability/retry-backoff.md) · Recover transient failures within a deadline without multiplying downstream load.
- [Mixed-version deployment compatibility](../knowledge/reliability/rolling-deploy-compatibility.md) · Plan deploys and rollbacks for a period when old and new code read and write the same data.
- [Service-level objectives and burn alerts](../knowledge/reliability/slo-error-budget.md) · Define an observable reliability target from user outcomes and alert on meaningful consumption.
- [Structured logs and request correlation](../knowledge/reliability/structured-logging.md) · Capture events that let operators trace a failure without logging sensitive inputs or drowning in noise.
