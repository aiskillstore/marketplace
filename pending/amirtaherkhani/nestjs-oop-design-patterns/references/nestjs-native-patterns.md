# NestJS-Native Patterns

NestJS already implements many architectural and behavioral patterns. Use its lifecycle and container instead of creating competing mechanisms.

## Classify by semantics, not by name

Nest metadata decorators such as `@UseGuards()` are not implementations of the GoF object Decorator pattern. A class extending Passport's `PassportStrategy` is a framework integration, but it demonstrates an application Strategy only when consumers select among real interchangeable authentication policies behind a stable contract. Likewise, a default-scoped provider has a shared container lifetime; it does not need a hand-written static Singleton implementation.

Name the actual mechanism and guarantee. A familiar pattern label must not imply durability, distribution, replay, independent scaling, or substitution that the implementation does not provide.

## Module as encapsulation and composition root

`@Module()` declares controllers, providers, imports, and exports. The exports are the module's public facade. Provider registrations choose concrete implementations behind tokens.

Do not create a second manual dependency container inside a module.

## Provider and dependency injection

Providers express constructor-injected collaboration. Custom providers support class, value, alias, and factory construction.

Use provider tokens for application ports and configuration. Avoid runtime service location unless implementing a plugin/discovery framework.

## Middleware

Use for raw request/response concerns that occur before Nest's route context is available, such as correlation identifiers or compatible low-level middleware.

Do not use middleware for route authorization; guards have execution context and metadata.

## Guard

Use for whether a principal/request may proceed. Guards can read route/controller metadata and work across supported execution contexts.

Keep authorization policy reusable. A guard adapts request context and calls the policy; it should not contain database-heavy business workflows by default.

## Pipe

Use for validation and transformation of handler arguments. Global DTO validation protects transport input; parameter pipes parse focused values.

Do not put side effects or business transactions in pipes.

## Interceptor

Use around handler execution for timing, tracing, response mapping, cache integration, or consistent cross-cutting behavior. Interceptors wrap the return path in reverse order.

Do not hide feature-specific business decisions in a global response interceptor.

## Exception filter

Use at the transport boundary to map uncaught exceptions into protocol-specific responses and logging. Domain/application errors should remain transport-neutral when the architecture requires multiple adapters.

Avoid catch-and-rethrow filters that add no mapping, context, or observability.

## Custom decorator

Use parameter decorators to extract already-established request context and metadata decorators to declare policies. A decorator should not perform hidden I/O or business mutations.

## Dynamic module

Use for configurable reusable infrastructure. Prefer normal feature modules for business capabilities.

## CQRS handlers

Commands, queries, events, and sagas are appropriate when explicit dispatch, separate models, or long-running workflows provide value. Do not use a command bus as a mandatory wrapper around every service call.

Dispatch alone does not queue, persist, replay, or audit a command. Add those guarantees explicitly when required. CQRS can separate read and write models, but it is not automatically more scalable than a cohesive CRUD/application-service design.

## Event emitter versus broker

- In-process emitter: best-effort reactions in the same process.
- Queue/broker: durable or independently scaled work across processes.
- Transactional outbox: database commit and external publication must stay consistent.

Do not assume an in-process event survives a crash or reaches another replica.

The same caution applies to an in-process CQRS `EventBus`: the event class and handler decorators do not by themselves create distributed pub/sub or reliable delivery.

## Adapter-neutral application code

Use `ExecutionContext` in framework-level guards/interceptors that support HTTP, GraphQL, WebSockets, or microservices. Keep application operations independent of all transport context when practical.

## Lifecycle order

The general HTTP path is middleware → guards → interceptors (before) → pipes → controller/provider → interceptors (after) → filters on uncaught exceptions.

Put a concern where the required information and semantics exist. Misplacing it creates duplication or surprising order dependencies.

See the official [request lifecycle](https://docs.nestjs.com/faq/request-lifecycle) and [provider](https://docs.nestjs.com/providers) documentation.
