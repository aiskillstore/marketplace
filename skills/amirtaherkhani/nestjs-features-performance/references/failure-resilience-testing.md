# Failure Resilience and Testing

Bound failure propagation, cancellation, retry, and recovery. Error mapping explains a failure; it does not make an unsafe operation safe to repeat or a corrupted process safe to continue.

## Observe every asynchronous failure channel

- `await` or return promises whose outcome matters.
- Attach the required `'error'` handling for streams and `EventEmitter` APIs; `try/catch` around the initiating call cannot catch errors emitted later.
- Use stream/pipeline APIs that propagate completion, error, cancellation, and cleanup.
- Give scheduled callbacks and long-lived consumers an explicit owner and failure policy.
- Move durable background work to a queue/worker with acknowledgement and replay semantics instead of starting floating work from a request.
- Make intentional best-effort work explicit, bounded, observable, and safe to lose.

## Use end-to-end deadlines and cancellation

A timeout bounds how long the caller waits; cancellation attempts to stop work. Neither proves a remote side effect did not happen.

- Establish a total operation deadline, then allocate smaller dependency budgets within it.
- Propagate `AbortSignal` or the installed client's equivalent when supported.
- Stop starting new work after cancellation and release listeners, sockets, cursors, and timers.
- Distinguish caller cancellation, local timeout, dependency timeout, and shutdown drain in diagnostics.
- Do not return a timeout while continuing unbounded hidden work.
- When outcome is unknown, reconcile by operation/idempotency key before retrying a write.

## Decide retries from semantics

| Failure | Default retry decision |
| --- | --- |
| Validation, authentication, authorization, invariant rejection | Do not retry unchanged input |
| Permanent contract/configuration/credential defect | Do not loop; alert the owner or fail deployment/startup |
| Rate/capacity limit | Retry only when allowed, respecting safe server hints and total budget |
| Transient connection reset/unavailability | Retry only a safe/idempotent operation with backoff and jitter |
| Optimistic concurrency/serialization conflict | Retry the complete read-decide-write unit only when its policy remains valid |
| Timeout after a possible write | Treat outcome as unknown; reconcile or use idempotency before repetition |
| Unknown implementation failure | Do not classify as transient by default |

Every retry needs a maximum attempt count, total deadline, exponential backoff with jitter, cancellation, telemetry, and capacity analysis. Retry amplification across HTTP clients, service code, SDKs, brokers, and queues can turn one failure into an outage.

Circuit breakers, bulkheads, queues, and fallbacks are conditional reliability controls—not default decorators. A fallback must preserve authorization, billing, consistency, freshness, and user expectations.

## Own partial effects

Before handling a failure, ask what may already have changed:

- Was the database transaction committed or rolled back?
- Was an external request accepted even though its response timed out?
- Was a message published or acknowledged?
- Were bytes already sent to the client?
- Can the operation be safely repeated, reconciled, compensated, or only escalated?

Architecture owns transaction and consistency boundaries. Use idempotency, uniqueness constraints, outbox/inbox, acknowledgement discipline, sagas/compensation, or reconciliation only where the business requirement justifies them. An exception filter cannot supply these guarantees after the fact.

## Treat fatal process errors as fatal

Use unhandled-rejection and uncaught-exception hooks for last-resort reporting, not request recovery. After an uncaught exception, application state may be inconsistent.

- stop claiming readiness/accepting new work when possible;
- perform only minimal, bounded best-effort diagnostics/cleanup appropriate to the failure path;
- exit instead of resuming normal service;
- rely on a process supervisor/orchestrator to restart a clean instance;
- investigate repeated crash loops rather than hiding them with infinite restart.

Normal deployment signals use the graceful shutdown path; they are not equivalent to an uncaught programmer/runtime failure.

## Keep failure telemetry useful and safe

- Use stable application categories/codes for aggregation and low-cardinality metrics.
- Correlate logs and traces with request/message/job identifiers without exposing them publicly unless safe.
- Record the exception at the span/log boundary where it escapes; avoid duplicate exception events for handled expected outcomes.
- Redact credentials, authorization headers, cookies, personal data, raw bodies, SQL, and sensitive exception messages.
- Fingerprint unknown failures by controlled type/stack data internally, never by unbounded raw message labels.
- Track retry attempts, exhaustion, timeout source, dead-letter age/count, and compensation/reconciliation outcomes.

## Build a failure test matrix

| Boundary | Minimum useful evidence |
| --- | --- |
| Domain/application | Expected failure categories, invariants, and side effects |
| Vendor adapter | Realistic driver/SDK codes translated correctly; unknowns preserved |
| Public transport | Status/code/body/headers or protocol-specific error contract |
| Dependency call | timeout, cancellation, connection loss, malformed response, and exhausted retry |
| Write workflow | duplicate request, unknown outcome, concurrency conflict, partial commit, and reconciliation |
| Worker/message | redelivery, poison message, dead-letter, replay, and shutdown during work |
| Streaming/WebSocket | disconnect, mid-stream failure, cleanup, and connection policy |
| Process | unhandled rejection/exception reporting, readiness removal, exit, and supervisor restart |
| Privacy | no secrets or internal diagnostics in public responses, logs, metrics, or traces |

Use deterministic fakes for policy, realistic integration tests for adapter semantics, and E2E/runtime tests for framework wiring. Fault injection should target a named failure and expected invariant, not randomly break production.

See the official Node.js [errors](https://nodejs.org/api/errors.html), [process events](https://nodejs.org/api/process.html), and [`AbortSignal`](https://nodejs.org/api/globals.html#class-abortsignal) documentation, RxJS [`timeout`](https://rxjs.dev/api/operators/timeout), OpenTelemetry [exception conventions](https://opentelemetry.io/docs/specs/semconv/exceptions/), and OWASP [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
