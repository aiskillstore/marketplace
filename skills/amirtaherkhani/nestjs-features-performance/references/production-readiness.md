# Production Readiness

Use this as a risk-based gate. Not every application needs every integration, but every omitted item should be an explicit decision.

## Configuration and startup

- [ ] Required environment/config values are validated at startup.
- [ ] Secrets are not committed, returned, or logged.
- [ ] Dependencies required for readiness are checked without making liveness fragile.
- [ ] Startup migrations have an explicit concurrency and rollback policy.
- [ ] Runtime/framework versions match deployment images and documentation.

## Contracts and data

- [ ] DTO/message/schema validation exists at every untrusted boundary.
- [ ] Unknown fields, coercion, nullability, pagination, and size limits are deliberate.
- [ ] Error codes and public response/message contracts are stable and documented.
- [ ] Database constraints protect uniqueness/referential invariants.
- [ ] Transactions align with use cases and do not hold locks across slow network calls.
- [ ] Breaking API/event/job changes have a compatibility migration.

## Security

- [ ] Authentication and authorization are separate and tested.
- [ ] Resource ownership/tenant filtering is enforced below route metadata alone.
- [ ] CORS, CSRF, cookies, headers, proxy trust, and rate limits match the client/deployment model.
- [ ] Uploads, webhooks, redirects, and outbound URLs have specific threat controls.
- [ ] Logs and traces redact credentials, tokens, cookies, and sensitive payloads.
- [ ] Dependency/package choices are verified rather than copied from an ecosystem list.

## Resource safety

- [ ] Request bodies, uploads, queries, pages, batches, and streams are bounded.
- [ ] Every external call has a timeout/deadline.
- [ ] Retries are classified, bounded, jittered, and within a total budget.
- [ ] DB/HTTP/broker pools are sized across the maximum replica count.
- [ ] CPU-heavy work cannot block user-facing event loops.
- [ ] Cache growth and in-memory maps/listeners are bounded.
- [ ] Backpressure/load shedding behavior is defined.

## Queues, events, and schedules

- [ ] Delivery semantics and duplicate behavior are documented.
- [ ] Consumers are idempotent and concurrency is bounded.
- [ ] Poison jobs/events have dead-letter/inspection/replay procedures.
- [ ] Scheduled work will not run once per replica unintentionally.
- [ ] Event publication is atomic with state change when the business requires it.
- [ ] Queue lag/age and failure counts are observable.

## Observability

- [ ] Structured logs carry request/job correlation identifiers.
- [ ] Metrics cover traffic, errors, duration, and saturation.
- [ ] Traces expose database and external dependency time for critical flows.
- [ ] Dashboards use percentiles and queue age, not averages alone.
- [ ] Alerts map to user impact and have an owner/runbook.
- [ ] High-cardinality labels and sensitive values are controlled.

## Health, deployment, and shutdown

- [ ] Liveness, readiness, and startup semantics are distinct.
- [ ] Readiness turns false before termination/drain.
- [ ] Shutdown hooks close resources in a tested order.
- [ ] In-flight requests, streams, sockets, and jobs have a drain deadline.
- [ ] Rolling deployment supports mixed versions where contracts require it.
- [ ] Rollback is compatible with schema, event, and cache changes.

## Testing and capacity

- [ ] Unit tests protect domain/application behavior.
- [ ] Integration tests exercise persistence/cache/broker adapters.
- [ ] E2E tests cover validation, auth, serialization, and real wiring.
- [ ] Duplicate, timeout, retry, and dependency-failure tests exist for critical paths.
- [ ] Load test reflects payloads, data volume, cache state, and concurrency.
- [ ] Soak/spike tests are used when leak or burst risk matters.
- [ ] Baseline and post-change p95/p99, throughput, error, and saturation metrics are retained.

## Rollout record

For a consequential performance or scaling change, record:

```text
Target SLO/workload
Baseline and limiting resource
Change and expected mechanism
Feature flag/canary plan
Correctness and failure tests
Success metrics
Rollback metrics and procedure
New capacity limit/next bottleneck
```

Use the official NestJS [health check](https://docs.nestjs.com/recipes/terminus), [testing](https://docs.nestjs.com/fundamentals/testing), and [lifecycle](https://docs.nestjs.com/fundamentals/lifecycle-events) guidance for framework behavior.
