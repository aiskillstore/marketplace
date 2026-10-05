# Error Handling Rules

Design failures as stable contracts. Preserve business meaning across layers, map it once at each transport boundary, and make retry, partial-effect, privacy, and process-failure behavior explicit.

## Load the focused guide

| Task | Load |
| --- | --- |
| Define failure categories, typed errors/results, public codes, validation shape, or HTTP semantics | [Error taxonomy and contracts](error-taxonomy-contracts.md) |
| Implement NestJS filters or map HTTP, GraphQL, RPC, gRPC, WebSocket, and worker failures | [Exception filters and transports](exception-filters-transports.md) |
| Design deadlines, cancellation, retries, fatal-process behavior, telemetry, or failure-path tests | [Failure resilience and testing](failure-resilience-testing.md) |

Use these guides conditionally. Preserve an established compatible contract instead of replacing it only to adopt a fashionable error format.

## Classify before mapping

| Category | Meaning | Default handling |
| --- | --- | --- |
| Expected business rejection | Current business state disallows the operation | Stable application failure; normally not retried |
| Invalid request or message | Input cannot satisfy the boundary contract | Reject before business side effects |
| Authentication or authorization | Identity is absent/invalid, or the principal is not allowed | Apply security disclosure policy; never retry blindly |
| Conflict or precondition | State/version/uniqueness changed | Return a stable conflict; retry only the correct unit when safe |
| Transient dependency or capacity | A dependency may recover | Bound by deadline, idempotency, and retry budget |
| Permanent dependency failure | Contract, configuration, credentials, or unsupported operation is wrong | Translate and escalate; repeated retry is harmful |
| Cancellation or timeout | The caller no longer waits or the deadline expired | Stop cancellable work; treat side-effect outcome as potentially unknown |
| Invariant defect or unknown | The implementation violated an assumption or the cause is unclassified | Safe server failure, one diagnostic record, no automatic recovery in-place |

Do not infer category from an error message. Use an application-owned type/discriminant or translate a documented driver/vendor code in its adapter. Preserve the original `cause` for internal diagnostics without exposing it publicly.

Expected outcomes may use a typed result when callers routinely branch on them. Exceptions are appropriate when a failure must unwind the current operation. Do not impose either style universally; keep the public meaning the same.

## Keep mapping at boundaries

- Domain/application code expresses business meaning without `HttpException`, `RpcException`, GraphQL, or WebSocket types.
- Infrastructure adapters translate vendor errors into application-owned categories and retain a safe cause chain.
- Each transport maps known categories to its own protocol semantics.
- One fallback handles unknown values without trusting that a caught value is an `Error`.

Using Nest `HttpException` in a small HTTP-only controller or boundary service is pragmatic. It becomes harmful when reusable policy, shared application code, or multi-transport operations depend on HTTP status codes.

## Define a public contract

A public error needs a stable machine-readable identifier independent of human wording. It may use the repository's existing envelope or RFC 9457 Problem Details for HTTP APIs; do not mix incompatible shapes accidentally.

```json
{
  "code": "ORDER_NOT_PAYABLE",
  "message": "The order cannot be paid in its current state",
  "requestId": "01J...",
  "details": []
}
```

- Keep `code` stable across wording/localization changes and document its compatibility policy.
- Make the transport status consistent with the body; status alone is not the application failure code.
- Include field-level validation paths/reasons only when safe and useful.
- Never expose stack traces, SQL, filesystem paths, secrets, tokens, raw vendor bodies, or internal class names.
- Use an opaque occurrence/request identifier for support correlation, not a database key or sensitive trace payload.

## Use filters as the final NestJS mapping layer

Filters run for uncaught exceptions. A caught error does not reach them, and once a narrower filter handles an exception it is not passed to another filter. Therefore, keep filter ownership deliberate rather than expecting a middleware-like chain.

- Register DI-dependent global filters with `APP_FILTER`; manually created global filters are outside module injection.
- Use `HttpAdapterHost` when mapping must support both Express and Fastify.
- Select the correct `ArgumentsHost` context and contract for HTTP, GraphQL, RPC, or WebSockets.
- Audit gateways and hybrid applications separately; an HTTP global filter does not prove every transport is covered.
- Do not try to rewrite a response after headers or stream data have been committed.
- Log an unexpected failure once with correlation context; avoid duplicate stack traces at every layer.

## Bound asynchronous and resilience behavior

- `await` or return every promise whose failure matters. Move durable background work to an owned queue/worker instead of floating it from a request.
- Give outbound operations explicit deadlines and propagate cancellation when the client and dependency support it.
- Retry only classified transient failures, only when the operation is safe or idempotent, with jitter, attempt/deadline limits, and overload awareness.
- A timeout does not prove a write failed. Reconcile or use an idempotency key before repeating a side effect.
- Preserve transaction, outbox, compensation, and acknowledgement ownership in the use case or adapter; filters cannot undo partial effects.
- Treat `uncaughtException` and unhandled rejection reporting as last-resort diagnostics. Do not continue normal service after an uncaught exception; let the process supervisor restart a clean instance.

## Observe and test failures safely

Record a stable error category/code, operation, correlation identifiers, and a redacted cause chain. Do not use raw messages, paths, user IDs, or stack traces as metric labels. Keep known client failures from flooding error logs while retaining security-relevant audit events.

Test application categories, adapter translation, public transport contracts, unknown fallbacks, sensitive-data absence, timeout/cancellation, duplicate/retry behavior, partial effects, committed streams, and process restart behavior according to risk.

Primary ownership remains explicit: OOP shapes cohesive failure types; Architecture owns transactions and cross-boundary consistency; API Design owns compatibility; Security owns disclosure; Scaling owns overload/retry capacity; Observability & SRE owns telemetry operations. This rulebook owns classification and runtime mapping.

See the official NestJS [exception filters](https://docs.nestjs.com/exception-filters), [request lifecycle](https://docs.nestjs.com/faq/request-lifecycle), and [microservice filters](https://docs.nestjs.com/microservices/exception-filters), plus [Node.js errors](https://nodejs.org/api/errors.html) and [process](https://nodejs.org/api/process.html) guidance.
