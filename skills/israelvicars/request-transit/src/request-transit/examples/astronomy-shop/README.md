# examples/astronomy-shop (SYNTHETIC)

A tiny, made-up code base whose routes line up with the synthetic OpenTelemetry demo checkout trace in
`../../samples/otel-demo-checkout.otlp.json`. It exists only so the optional contract layer can be shown
end to end (story 1). It is not runnable, and it is not the real OpenTelemetry demo source: only the
service names and route names are borrowed so the trace and the code meet.

| service | how its contract is declared | extractor |
| --- | --- | --- |
| frontend | Express route + Zod schema imported from the shared package `@shop/schemas`, response via `Response<T>` | express + zod (cross-package) |
| checkout | NestJS `@GrpcMethod` + class-validator DTOs; publishes `orders` with `satisfies OrderPlacedEvent` | nest + class-validator |
| cart | NestJS gRPC; DTO classes imported from `@shop/schemas` | nest + class-validator (cross-package) |
| currency | NestJS gRPC with plain TypeScript interfaces | ts-types (medium confidence) |
| payment | NestJS gRPC, request checked with `ChargeRequest.parse(...)` (Zod) | nest + zod |
| shipping | Express routes + Joi schemas, response interfaces | express + joi |
| quote | OpenAPI document (served under `/api/v1`) | openapi |
| email | Express + Zod, no response type: shown as a gap | express + zod |
| accounting | NestJS `@EventPattern('orders')` | nest event (ts-types) |
| fraud-detection | no code configured: falls back to the producer's shape | topic fallback (medium) |
| product-catalog | `catalog.proto` (nested messages, enum, repeated, optional, map, oneof) importing `proto/shop/money.proto` | protobuf |

Build the index (explicit, never automatic) and a contract-aware page:

```
node src/request-transit/scripts/transit.mjs index --config src/request-transit/examples/astronomy-shop/transit.config.json
node core/build.mjs src/request-transit/samples/otel-demo-checkout.otlp.json --contracts --out out/otel-contracts/transit.html
```
