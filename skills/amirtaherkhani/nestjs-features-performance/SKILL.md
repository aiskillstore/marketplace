---
name: nestjs-features-performance
description: 'Selects and implements NestJS runtime features, error and API contracts, security, testing, DevOps, performance, and safe scale. Use for middleware, guards, pipes, interceptors, exception filters, typed failures/results, Problem Details, validation errors, HTTP/GraphQL/RPC/gRPC/WebSocket error mapping, deadlines, cancellation, retry classification, fatal process errors, authentication, authorization, caching, queues, schedulers, CI/CD, containers, Kubernetes, configuration and secrets, migrations, supply-chain controls, health probes, logs/metrics/traces, SLOs and alerts, incident recovery, rollout and rollback, event-loop or database bottlenecks, load tests, horizontal scaling, idempotency, backpressure, and graceful shutdown. Do not use for frontend-only performance or non-NestJS services. When other skills also apply, reconcile ownership before mutation.'
license: MIT
metadata:
  author: amirtaherkhani
  version: '1.3.2'
---

# NestJS Features, Scaling, and Performance

Choose the NestJS primitive whose lifecycle matches the concern. Diagnose the limiting resource before optimizing or distributing the system.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Inspect repository instructions, installed versions, bootstrap/transport and deployment configuration, tests, operational contracts, and baseline measurements. Preserve user changes; establish lifecycle, evidence, environment, and authorization before choosing an optimization or delivery action. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns Nest lifecycle, API/error/security contracts, test layers, performance evidence, reliability, observability, and runtime delivery. When installed and relevant, coordinate with:

- `nestjs-architecture-principles`: module, dependency, data, and transaction boundaries.
- `nestjs-oop-design-patterns`: object responsibilities, invariants, and patterns.
- `nestjs-professional-software-engineering`: implementation and verification.
- `nestjs-code-audit`: read-only quality evidence and deduplicated reporting.
- `nestjs-feature-audit`: branch-specific roadmap gate and feature reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Check for incompatible edits/contracts, command order or side effects, competing owners, and unmet version, evidence, authorization, or repository prerequisites. Resolve using explicit user intent, repository contracts, verified runtime constraints, then the narrowest owner. Assign one lead per decision; do not create parallel designs to satisfy incompatible advice. If a material conflict remains, stop before mutation and ask for the smallest missing decision. Audits stay read-only; explicit fix authorization applies in a distinct implementation phase.

## Establish the runtime baseline

Before recommending or changing behavior:

1. Read the installed NestJS/Node versions, bootstrap code, adapter, modules, transports, persistence clients, cache/queue setup, and deployment manifests.
2. Trace one representative request, message, or job through guards, pipes, interceptors, handlers, providers, persistence, and external calls.
3. Identify the current symptom and evidence: latency percentiles, throughput, error rate, event-loop delay, CPU, heap/GC, database time, pool saturation, external latency, or queue lag.
4. Define a target and workload. "Make it faster" is not a measurable acceptance criterion.
5. Check framework and library APIs against official documentation and the repository version.

Never claim a performance improvement from code appearance. Measure before and after under a representative workload.

## Put behavior in the correct NestJS feature

Use [references/feature-selection.md](references/feature-selection.md).

General HTTP lifecycle:

```text
request
  -> middleware
  -> guards
  -> interceptors (before)
  -> pipes
  -> controller/resolver + providers
  -> interceptors (after, reverse order)
  -> exception filters for uncaught errors
  -> response
```

Defaults:

- **Middleware:** raw protocol preprocessing and correlation context.
- **Guard:** authentication/authorization decision for an execution context.
- **Pipe:** input validation and transformation.
- **Interceptor:** behavior around handler execution, response mapping, timing, tracing, or compatible caching.
- **Exception filter:** final protocol-specific error mapping.
- **Decorator:** declarative metadata or extraction of established context, not hidden I/O.
- **Provider/application operation:** business behavior and orchestration.
- **Queue/worker:** durable, deferred, bursty, or resource-heavy work.
- **Event:** a completed fact with independent reactions; choose in-process versus durable delivery explicitly.

For API and transport guidance, load [references/api-runtime.md](references/api-runtime.md). Use the focused rulebooks for [error handling](references/error-handling.md), [security](references/security.md), [testing](references/testing.md), [API design](references/api-design.md), and [deployment](references/devops-deployment.md) when those risks are in scope.

## Diagnose performance by resource

Use [references/performance-diagnosis.md](references/performance-diagnosis.md).

Classify the primary constraint before selecting a remedy:

| Constraint | Evidence | Typical first moves |
| --- | --- | --- |
| Event-loop blocking | High event-loop delay/utilization, CPU callback hotspots | Remove synchronous work; bound input; offload CPU work |
| Database | Slow queries, N+1, pool waits, locks, high rows scanned | Fix query shape/indexes; bound results; shorten transactions |
| External I/O | Dependency spans dominate latency | Deadlines, connection reuse, bounded retry, concurrency control |
| Memory/GC | Heap growth, GC pauses, OOM/restarts | Remove retention; stream/bound data; profile allocations |
| Serialization/logging | CPU or payload size grows with response | Select fields; paginate/stream; reduce hot-path logging |
| Capacity | Stable per-instance performance but saturated replicas | Horizontal scale with stateless processes and safe dependencies |

Do not switch to Fastify, add Redis, introduce worker threads, or split services before evidence identifies the bottleneck and compatibility cost is understood.

## Scaling rules

Use [references/scaling-reliability.md](references/scaling-reliability.md).

1. Keep web replicas stateless; move shared sessions, locks, job state, and coordination to appropriate external systems.
2. Prefer default singleton providers. Request scope propagates through the injection chain and adds per-request allocation; use only for a real lifetime requirement.
3. Bound every collection, page, batch, queue concurrency, retry count, payload, upload, and timeout.
4. Make jobs and message consumers idempotent. Assume duplicate delivery and partial failure.
5. Use exponential backoff with jitter for transient failures; never blindly retry validation, authorization, or invariant errors.
6. Add backpressure. Reject, shed, pause, or queue load instead of allowing unbounded memory and latency growth.
7. Separate user-facing processes from CPU-heavy or slow background work when their capacity profiles differ.
8. Treat caches as derived state. Define key namespace, TTL, invalidation, stampede behavior, and safe fallback.
9. Drain before shutdown: stop accepting work, mark unready, finish or safely requeue in-flight work, then close resources.
10. Scale from service-level objectives and saturation signals, not average CPU alone.

## Implementation workflow

### Add or change a feature

1. Locate the correct lifecycle stage and existing repository convention.
2. Define the contract, scope, and failure behavior.
3. Implement the smallest provider/component and bind it at the narrowest useful level.
4. Test its behavior in isolation and its ordering/wiring at a boundary.
5. Update OpenAPI/schema, configuration validation, telemetry, and docs when the public or operational contract changes.

### Design or repair error handling

1. Inventory every entry point, current public error contract, filter binding, adapter/vendor error, client dependency, and partial side effect.
2. Classify expected business, validation, identity/access, conflict, transient, permanent, cancellation/timeout, and unknown failures without parsing messages.
3. Define the application-owned type/result and translate vendor failures at infrastructure adapters while preserving a safe cause.
4. Map each HTTP, GraphQL, RPC/gRPC, WebSocket, or worker boundary independently; keep one non-sensitive unknown fallback.
5. Define deadlines, cancellation, retry/idempotency, acknowledgement, transaction, and unknown-outcome behavior before adding recovery logic.
6. Bind the narrowest correct NestJS filter/handler and verify hybrid, gateway, adapter, stream, and process-fatal paths as applicable.
7. Test the stable contract, side effects, observability ownership, sensitive-data absence, and restart/recovery behavior.

### Optimize a slow path

1. Reproduce with a controlled benchmark or trace.
2. Record baseline percentiles, throughput, errors, and resource saturation.
3. Profile the dominant path.
4. Change one limiting factor.
5. Repeat the same workload and compare.
6. Run correctness and failure tests; faster incorrect behavior is a regression.
7. Document the capacity limit and rollback signal.

### Plan scale

1. Define workload shape, SLO, consistency, durability, and cost constraints.
2. Estimate per-instance capacity and identify shared dependency limits.
3. Choose vertical tuning, replicas, workers, queues, partitions, or service extraction based on the actual resource boundary.
4. Design overload and partial-failure behavior before adding capacity.
5. Prove the plan with load, soak, spike, and failure tests appropriate to the risk.

### Build, deploy, or diagnose production

1. Identify the source revision, immutable artifact/image digest, target environment, and owner.
2. Compare repository intent, built artifact, desired deployment, and running state; do not infer live state from configuration files alone.
3. Define migration/configuration compatibility, rollout strategy, success signals, abort threshold, and rollback or forward-repair path.
4. Apply the smallest authorized change through the repository's delivery mechanism.
5. Verify live revision, readiness, representative traffic/work, errors, latency, saturation, queues/dependencies, and drain behavior.
6. Record the release or incident evidence and reconcile any emergency drift back into declared state.

## Production gate

Use [references/production-readiness.md](references/production-readiness.md) before calling a feature production-ready. At minimum verify configuration, security, contracts, resource bounds, observability, health/readiness, shutdown, and recovery.

## Reference routing

| Task | Load |
| --- | --- |
| Pick middleware, guard, pipe, interceptor, filter, decorator, event, queue, or scheduler | [feature-selection.md](references/feature-selection.md) |
| Build HTTP/GraphQL/WebSocket/SSE/microservice contracts and tests | [api-runtime.md](references/api-runtime.md) |
| Classify failures, map stable errors, or design filters and retries | [error-handling.md](references/error-handling.md) |
| Define typed errors/results, public codes, validation shape, Problem Details, or HTTP semantics | [error-taxonomy-contracts.md](references/error-taxonomy-contracts.md) |
| Implement filters across HTTP, GraphQL, RPC/gRPC, WebSocket, workers, or hybrid apps | [exception-filters-transports.md](references/exception-filters-transports.md) |
| Design deadlines, cancellation, safe retries, fatal-process handling, telemetry, or failure tests | [failure-resilience-testing.md](references/failure-resilience-testing.md) |
| Review authentication, authorization, validation, secrets, output, or abuse controls | [security.md](references/security.md) |
| Choose unit, module, integration, contract, E2E, or reliability tests | [testing.md](references/testing.md) |
| Design DTOs, responses, errors, pagination, idempotency, or versioning | [api-design.md](references/api-design.md) |
| Diagnose latency, CPU, event loop, database, memory, cache, or Fastify choices | [performance-diagnosis.md](references/performance-diagnosis.md) |
| Add replicas, workers, queues, retries, idempotency, backpressure, or distributed coordination | [scaling-reliability.md](references/scaling-reliability.md) |
| Design build, configuration, migration, health, observability, rollout, or shutdown controls | [devops-deployment.md](references/devops-deployment.md) |
| Build CI/CD, container images, provenance, promotion, or artifact rollback | [ci-cd-containers.md](references/ci-cd-containers.md) |
| Configure or diagnose Kubernetes workloads, probes, resources, HPA, rollout, or termination | [kubernetes-operations.md](references/kubernetes-operations.md) |
| Define SLOs, logs/metrics/traces, alerts, dashboards, incidents, backups, or recovery | [observability-sre.md](references/observability-sre.md) |
| Review operational readiness and rollout safety | [production-readiness.md](references/production-readiness.md) |

## Expected response

For performance/scaling work, report:

- **Symptom and target**
- **Baseline evidence**
- **Primary constraint**
- **Recommended change and trade-off**
- **Correctness/failure risks**
- **Before/after verification plan**

If evidence is missing, propose the smallest measurement needed before an architectural change.

For Error Handling work, report:

- **Failure model:** categories, stable codes/types, and expected versus unknown behavior.
- **Boundary mapping:** application-to-transport mapping for every affected entry point.
- **Effects and resilience:** committed/possible side effects, deadline, cancellation, retry/idempotency, and recovery ownership.
- **Disclosure:** public fields, redaction, logging ownership, and sensitive-data controls.
- **Framework wiring:** filter/handler scope, execution context, adapter/hybrid coverage, and fatal-process behavior.
- **Verification:** contract, adapter, timeout, duplicate, partial-effect, privacy, and restart tests.

For DevOps work, report:

- **Release identity:** source revision, artifact/digest, environment, and owner.
- **State comparison:** repository intent, desired deployment, and observed runtime.
- **Safety:** migrations/configuration compatibility, security gates, and failure risks.
- **Rollout:** strategy, success/abort signals, observation window, and capacity impact.
- **Verification:** live revision, health, representative work, telemetry, and drain.
- **Recovery:** rollback or forward-repair procedure and trigger.
