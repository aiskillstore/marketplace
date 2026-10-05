# Scaling and Reliability

Scaling changes failure modes. Add capacity and control overload together.

## Horizontal web scaling

Web replicas should be replaceable and stateless between requests.

Externalize or deliberately coordinate:

- sessions and revocation state;
- cache and rate-limit counters when global semantics matter;
- WebSocket pub/sub and presence;
- scheduled jobs and distributed locks;
- uploaded files and generated artifacts;
- queue state and idempotency records.

Use readiness to remove a replica from traffic before termination. Make liveness indicate process deadlock/failure, not temporary dependency degradation that would restart every replica.

## Capacity model

Estimate:

```text
required instances ~= peak requests per second / safe requests per second per instance
```

Then adjust for headroom, zone failure, burstiness, deployment overlap, and downstream limits. A safe per-instance rate comes from a representative load test at the SLO, not the maximum rate before crash.

Watch concurrency and queueing, not only requests per second. Little increases in arrival rate near saturation can cause large latency growth.

## Queues and workers

Use queues to smooth bursts, isolate slow/CPU-heavy work, and recover persisted jobs. Separate producer and consumer deployment when their capacity differs.

Every handler defines:

- idempotency key and duplicate result;
- retryable versus terminal errors;
- maximum attempts and exponential backoff with jitter;
- per-job timeout/cancellation behavior;
- concurrency and downstream rate limit;
- dead-letter/failed-job inspection and replay;
- progress/status contract;
- retention and payload sensitivity.

Persist only identifiers and required immutable input when large/sensitive objects can be reloaded safely. Version job payloads when deployments may process older jobs.

## Idempotency

Do not rely on "exactly once" marketing. Build an idempotent effect:

1. derive a stable operation/event key;
2. record claim/result atomically with the protected write where possible;
3. return or no-op on a completed duplicate;
4. distinguish in-progress, completed, and failed/retryable states;
5. retain keys for the real redelivery window.

External APIs may need their own idempotency key. A local dedupe record does not make a non-idempotent remote call atomic.

## Retry and timeout budget

Retries multiply load during incidents. Use:

- a total deadline across attempts;
- exponential backoff and jitter;
- bounded attempts;
- retry only for classified transient failures;
- circuit/open-state or load shedding when a dependency cannot recover under retry traffic.

Never retry authentication, validation, insufficient funds, uniqueness conflict, or other deterministic failures without a state change.

This reference owns retry amplification, capacity, and overload controls. [Error handling](error-handling.md) owns failure classification and public mapping; database/application policy owns whether a complete concurrency unit is safe to repeat.

## Backpressure and overload

Bound:

- HTTP body/upload size;
- per-client streams and WebSocket buffers;
- database and external-call concurrency;
- queue consumer concurrency;
- in-memory work queues and caches;
- list/page/batch size.

When saturated, choose explicit behavior: reject quickly, return retry guidance, degrade a non-critical feature, pause consumption, or enqueue within a known capacity. Unbounded queues convert overload into memory failure and extreme latency.

## Scheduled and singleton work

Every replica runs Nest schedules unless deployment prevents it. Use a platform scheduler, dedicated replica, lease-based distributed lock, or unique queued job.

A lock needs owner identity, expiration, renewal, fencing/uniqueness where stale owners are dangerous, and telemetry. "SET if absent" without failure design is not sufficient for critical work.

## Data and cache scale

- Size DB pools across all replicas; per-instance defaults can exhaust the database after autoscaling.
- Prefer keyset/cursor pagination for deep mutable collections when product UX permits.
- Partition only after access patterns and operational ownership are understood.
- Cache derived reads, not invariants; plan invalidation and warm-up.
- Protect hot keys and synchronized expirations.

## Service extraction

Extract a service when independent deployment, ownership, data, security, failure, or scaling justifies network and operational cost. A separate worker deployment can scale CPU-heavy code without creating a new business service boundary.

Define schema evolution, retries, timeouts, idempotency, observability, and on-call ownership before moving a method across the network.

## Graceful shutdown

Recommended sequence:

1. receive termination signal;
2. mark the instance unready and stop accepting new work;
3. stop/pause queue and scheduler intake;
4. drain in-flight requests/jobs within a deadline;
5. requeue or release leases safely when the deadline expires;
6. flush telemetry;
7. close broker/cache/database connections;
8. exit with an observable result.

Test shutdown during active HTTP, stream, WebSocket, and job workloads. Nest lifecycle hooks help coordinate resources but do not design the drain policy for you.

See the official NestJS [queues](https://docs.nestjs.com/techniques/queues), [microservices](https://docs.nestjs.com/microservices/basics), and [lifecycle](https://docs.nestjs.com/fundamentals/lifecycle-events) documentation.
