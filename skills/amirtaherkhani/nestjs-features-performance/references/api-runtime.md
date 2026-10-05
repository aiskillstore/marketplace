# API and Runtime Features

## Bootstrap and configuration

Bootstrap order should be intentional:

1. create the application with the selected platform adapter;
2. load and validate configuration;
3. configure trust proxy/CORS/security headers as required by deployment;
4. register global validation, guards, interceptors, and filters through tested conventions;
5. generate/version public API documentation where applicable;
6. enable shutdown behavior;
7. listen only after required dependencies are ready.

Fail startup on missing required configuration. Do not scatter raw `process.env` reads through feature code.

## HTTP APIs

- Use DTOs for body, path, and query contracts.
- Bound pagination and filter/sort fields.
- Return status codes and errors with stable semantics.
- Make idempotency explicit for retry-prone create/payment operations.
- Version breaking public contract changes deliberately.
- Generate OpenAPI from the same DTO/operation definitions where the repository supports it.
- Avoid adapter-specific `@Req()`/`@Res()` unless lower-level behavior is genuinely required; direct response handling can bypass framework features.

## Serialization

Select only fields the consumer needs. Prevent credentials, internal flags, and private ORM relations from leaking through automatic serialization.

For large results:

- paginate collections;
- stream files/data where semantics permit;
- avoid materializing an entire export in memory;
- define cancellation and cleanup when the client disconnects.

## GraphQL

- Keep resolvers thin and delegate to application operations.
- Batch or prefetch relation access to prevent N+1 resolver queries.
- Apply authorization at the operation/field level appropriate to data sensitivity.
- Bound query depth/complexity and list sizes.
- Treat schema changes as public contract changes.

## WebSockets

- Gateways are singletons; do not inject request-scoped providers into them.
- Authenticate connection and sensitive messages; connection authentication alone may not authorize every room/resource.
- Externalize room/presence/pub-sub state when scaling across replicas.
- Plan adapter/broker behavior and sticky-session requirements.
- Bound message size, rate, and per-client buffers.

## Server-Sent Events and streaming

- Use typed event names and stable payload contracts.
- Propagate cancellation to upstream model/vendor/database work when the client disconnects.
- Add heartbeats only with a documented proxy/client need.
- Bound buffered data and apply backpressure.
- Define reconnect and resumability semantics; SSE reconnect does not make events durable automatically.
- For AI/LLM streams, isolate provider APIs behind a port and meter usage from authoritative provider results where available.

## Microservice transports

Transport choice does not remove distributed-systems responsibilities. Define:

- command/request versus event semantics;
- delivery guarantee and duplicate behavior;
- correlation, timeout, and cancellation;
- serialization/schema compatibility;
- retryable errors and dead-letter handling;
- ordering/partition keys;
- authentication and tenant context.

HTTP exceptions are not portable message errors. Map application failures into transport-specific contracts at the adapter.

## Caching

Use cache-aside or framework cache interceptors only when the data and invalidation semantics fit.

Define:

- namespaced, versioned key including tenant/auth dimensions;
- TTL and freshness tolerance;
- write invalidation or versioning;
- stampede protection for expensive misses;
- negative caching policy;
- safe behavior when cache is unavailable.

Never use a cache as the sole authority for authorization, quota, balance, billing, or uniqueness.

## Testing by boundary

| Boundary | Test |
| --- | --- |
| Domain policy/value | Plain unit test |
| Application operation | Unit test with owned fakes |
| Provider token/module wiring | Nest TestingModule compile/override test |
| Persistence/cache/broker adapter | Integration or contract test with realistic dependency |
| HTTP/GraphQL/WebSocket contract | E2E test through the transport |
| Message/job reliability | Duplicate, retry, timeout, and poison-message tests |
| Shutdown/readiness | Runtime integration test |

The official NestJS documentation index covers [validation](https://docs.nestjs.com/techniques/validation), [caching](https://docs.nestjs.com/techniques/caching), [queues](https://docs.nestjs.com/techniques/queues), [microservices](https://docs.nestjs.com/microservices/basics), [OpenAPI](https://docs.nestjs.com/openapi/introduction), and [testing](https://docs.nestjs.com/fundamentals/testing).
