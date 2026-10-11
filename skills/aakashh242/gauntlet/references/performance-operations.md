# Performance, resources, and operations lens

Trigger: hot paths, large inputs, caches, queues, resource ownership, CI/CD, infrastructure, or production-readiness claims.

## Resource and complexity attack

Identify input-controlled loops, fan-out, recursion, expansion, regex backtracking, joins, scans, sorting, and serialization. Ask what bounds memory, CPU, file descriptors, connections, queue length, retries, and retained state. A limit that applies only after allocation is too late to protect the allocation. Look for N+1 work, unbounded caches, leaked listeners/tasks, and work continuing after cancellation.

Use representative and adversarial-but-bounded fixtures. State hardware/runtime, input scale, concurrency, warmup, and measured result. Do not invent benchmark numbers or extrapolate a tiny test into production capacity. Prefer measured bottlenecks to speculative micro-optimization.

## Operational attack

Check configuration validation, safe defaults, deployment ordering, rolling-version compatibility, readiness/liveness meaning, graceful shutdown, draining, rollback, backups, restore drills, resource requests/limits, secret delivery, and least-privilege identities as applicable. Infrastructure plans are review evidence, not authorization to apply them.

Inspect timeouts and retries as a coupled budget. Ensure backpressure and cancellation propagate to upstream work. Consider dependency outage, DNS failure, disk full, quota exhaustion, partial rollout, expired certificates/credentials, and lost telemetry. Review build/install hooks and CI permissions before running repository-supplied commands.

## Diagnosability and recovery

Could an operator distinguish rejection, retryable failure, partial commit, and permanent corruption? Are error codes and correlation identifiers sufficient without exposing secrets? Do metrics and logs show saturation, retry storms, dropped work, and recovery failure? Are runbooks executable under the privileges operators actually have?

A recovery plan must address the durable state after failure, not only process restart. Do not mark a backup as useful without considering restoration compatibility and access.

## Evidence and re-attack

Record the bounded workload/failure condition, metric or trace, bottleneck mechanism, and effect on user-visible behavior. Test whether the repair moves pressure to another resource, changes semantics, or makes failure less observable. Do not stress a live service, modify deployment policy, install telemetry, or increase cloud spend without authorization.
