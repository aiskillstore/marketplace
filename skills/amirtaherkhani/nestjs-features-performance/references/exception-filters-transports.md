# Exception Filters and Transports

Use NestJS exception filters as final transport adapters for uncaught failures. Do not make them business-policy engines, retry coordinators, or substitutes for transaction design.

## Understand filter execution

In Nest's request lifecycle, an uncaught exception skips to filters. Filter order begins at the narrowest bound scope and moves outward, but an exception handled by one filter is not passed to another.

Consequences:

- a `try/catch` that consumes an error prevents the filter from seeing it;
- do not expect route, controller, and global filters to form a logging/mapping pipeline;
- keep narrow filters only for genuinely different contracts;
- centralize the unknown fallback so behavior is deterministic;
- test the actual binding and execution context, not only the mapper function.

## Separate classification from response writing

A maintainable boundary normally has two responsibilities:

1. a pure translator maps a known application failure into a transport representation;
2. a thin filter selects the execution context, records an unexpected failure once, and writes/emits the representation.

The translator should not query databases, call remote services, start transactions, or retry. Mapping must remain bounded even while dependencies are failing.

## Bind filters deliberately

- Prefer passing a filter class to `@UseFilters()` so Nest can reuse and inject it.
- Register a DI-dependent global filter with `APP_FILTER` from the module that owns it.
- A filter passed to `app.useGlobalFilters()` is created outside module DI.
- `useGlobalFilters()` does not automatically cover gateways or every hybrid application context.
- When extending a Nest base filter, delegate only the cases the base filter actually owns.
- Verify the installed NestJS version before relying on exception hierarchy or adapter behavior.

## Stay adapter-aware without leaking adapters

For HTTP, prefer `HttpAdapterHost` when a filter must work with Express and Fastify. Avoid casting every response to an Express type in shared boundary code.

Before writing:

- determine whether headers/body have already been committed;
- preserve required headers such as authentication challenges or safe retry hints;
- set the correct content type for the selected error representation;
- avoid serializing unknown objects directly;
- end or abort a partially written stream safely when a replacement body is impossible.

An exception filter cannot roll back bytes already sent, a database commit, broker acknowledgement, email, or external charge.

## Map each execution context

| Context | Boundary behavior |
| --- | --- |
| HTTP | Map application meaning to HTTP status, headers, and the documented response or Problem Details shape |
| GraphQL | Preserve GraphQL request/field error semantics and partial-data behavior; expose stable codes through documented extensions |
| Nest microservice RPC | Use the transport's `RpcException`/filter contract; a microservice filter's `catch()` returns an `Observable` |
| gRPC | Map to gRPC status codes and metadata supported by the installed transport; do not reuse HTTP codes |
| WebSocket | Use the gateway's `WsException`/event contract and define whether the socket stays connected |
| Queue/event worker | Let the worker/transport policy own acknowledgement, retry, dead-letter, and replay; an HTTP filter has no authority here |

Hybrid applications require an explicit coverage inventory. List every HTTP server, gateway, connected microservice, standalone worker, and scheduled entry point, then verify which filter or handler owns its unknown fallback.

## Handle RxJS error channels correctly

Nest interceptors and microservice clients may use Observables. When transforming an error:

- use `catchError` only to add context, map a known category, recover deliberately, or rethrow;
- return `throwError(() => mappedError)` when the operator contract requires an error Observable;
- do not turn a terminal error into a successful `undefined` value accidentally;
- preserve unsubscribe/cancellation and finalize resource cleanup;
- avoid retry operators without idempotency, classification, and a total deadline.

Verify APIs against the installed RxJS version.

## Keep logging ownership singular

Expected public failures usually need counters and selected audit events, not a full stack at every layer. Unknown failures should produce one primary diagnostic record with:

- application error code/category and operation;
- request/message/job and trace correlation;
- safe transport metadata;
- redacted cause chain and stack according to environment;
- running revision when operationally useful.

Adapters may add breadcrumbs but should not duplicate the same stack as an independent error at every hop.

## Test the boundary

- Unit-test the pure translator with known and unknown `unknown` values.
- E2E-test status/code/body/headers through each real transport.
- Test filter scope and hybrid/gateway registration.
- Test adapter parity if both Express and Fastify are supported.
- Test response-committed and streaming failure behavior.
- Assert secrets, SQL, tokens, internal class names, and raw vendor bodies are absent.
- Verify expected failures do not generate duplicate high-severity logs.

See the official NestJS [exception filters](https://docs.nestjs.com/exception-filters), [request lifecycle](https://docs.nestjs.com/faq/request-lifecycle), [execution context](https://docs.nestjs.com/fundamentals/execution-context), [microservice filters](https://docs.nestjs.com/microservices/exception-filters), and [WebSocket filters](https://docs.nestjs.com/websockets/exception-filters).
