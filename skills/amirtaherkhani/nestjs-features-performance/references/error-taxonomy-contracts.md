# Error Taxonomy and Contracts

Give failures application-owned meaning before mapping them to a protocol. A stable taxonomy prevents vendor errors, HTTP concerns, and human messages from becoming the contract.

## Start from the existing contract

Inspect current error classes/results, DTO validation output, filters, transport adapters, OpenAPI/GraphQL/protobuf schemas, client expectations, persistence/vendor codes, logs, and tests. Identify which public codes are already consumed before changing names or shapes.

## Separate internal meaning from public disclosure

An internal failure model may carry:

- a stable application code and category;
- safe structured context needed by the owning use case;
- whether the operation is known to be retryable under stated conditions;
- the original cause for diagnostics;
- ownership/severity metadata used internally.

The public representation is an allow-listed projection. Do not serialize an error object or cause chain directly. Treat `catch` values as `unknown`; normalize only documented shapes.

## Choose exceptions or results deliberately

Use a typed result when an expected negative outcome is a frequent branch that callers must exhaustively handle. Throw a typed error when the operation cannot continue and unwinding is clearer. Either can be valid.

Avoid these extremes:

- returning `null` or `false` for unrelated failure meanings;
- throwing generic `Error` with messages callers must parse;
- wrapping every failure until the useful type/code is lost;
- returning a result for programmer defects and then continuing with invalid state;
- forcing `Result` wrappers through all NestJS code when the repository has no such convention.

## Translate infrastructure failures in the adapter

Map only documented vendor signals that matter to the application. For example, a database unique constraint may become an application conflict when the constraint is known; an unknown driver error remains an unexpected dependency failure.

- Prefer stable driver codes/types over text matching.
- Preserve `cause` and safe operation context internally.
- Do not leak SQL, provider request bodies, credentials, hostnames, or SDK response objects.
- Do not convert every dependency error into “not found” or “unavailable.”
- Keep application codes independent of a replaceable vendor.

## Design the HTTP representation

Use the established envelope when compatible. If adopting RFC 9457 Problem Details, use `application/problem+json` and keep its standard members semantically correct:

```json
{
  "type": "https://api.example.com/problems/order-not-payable",
  "title": "Order cannot be paid",
  "status": 409,
  "detail": "The order is not in a payable state.",
  "instance": "https://api.example.com/problem-occurrences/01J...",
  "code": "ORDER_NOT_PAYABLE"
}
```

- The HTTP status and optional `status` member must agree.
- `type` identifies stable problem semantics; host it under a URI the API controls when practical.
- `detail` helps the client correct this occurrence; it is not a debug dump or machine parser input.
- `instance` is an opaque occurrence URI/identifier and must not reveal sensitive internals.
- Extension members such as `code` or validation errors need documented types and compatibility.

Do not migrate to Problem Details merely for aesthetics when clients already depend on a safe, stable envelope.

## Map HTTP semantics precisely

| Meaning | Common status | Guardrail |
| --- | --- | --- |
| Malformed or invalid input | `400` or `422` by documented API policy | Choose consistently; do not expose validator internals |
| Missing/invalid authentication | `401` | Include protocol-required challenge behavior where applicable |
| Authenticated but not allowed | `403` | A disclosure policy may intentionally use `404` for hidden resources |
| Resource absent | `404` | Do not collapse dependency outages into absence |
| State/uniqueness conflict | `409` | Explain the application conflict with a stable code |
| Failed conditional request | `412` | Use for HTTP preconditions such as `If-Match`, not every domain precondition |
| Rate/capacity limit | `429` | Supply a safe `Retry-After` signal when the retry time is known |
| Temporary service inability | `503` | Do not mark permanent configuration/contract defects transient |
| Gateway deadline/failure | `502`/`504` when the service is acting as a gateway | Do not use `504` as a generic label for every internal timeout |
| Unknown implementation failure | `500` | Return a non-sensitive fallback and correlate internally |

Use RFC 9110 semantics and the repository's documented API policy. Status codes are not substitutes for stable application codes.

## Map other transports without pretending they are HTTP

- **GraphQL:** preserve the GraphQL response/error model, including possible partial data. Put stable application codes in documented extensions without exposing internals.
- **gRPC:** map deliberately to gRPC status semantics such as `INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `ABORTED`, `UNAVAILABLE`, and `DEADLINE_EXCEEDED`; these are not HTTP aliases.
- **WebSockets:** define event/acknowledgement error envelopes and whether the connection remains usable.
- **Messages/jobs:** define retryable versus terminal failure, acknowledgement, dead-letter, replay, and duplicate behavior; there may be no immediate public response.

## Protect compatibility

Treat public error codes, validation field paths, status mapping, and retry signals as contracts. Add new optional detail compatibly; version breaking removals or meaning changes. Human wording may evolve when clients do not parse it.

See [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html), [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html), the [GraphQL error specification](https://spec.graphql.org/September2025/#sec-Errors), [gRPC status codes](https://grpc.io/docs/guides/status-codes/), and the OWASP [Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html).
