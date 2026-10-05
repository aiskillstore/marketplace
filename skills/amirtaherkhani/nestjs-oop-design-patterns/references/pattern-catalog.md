# Pattern Selection Catalog

Start from a force or failure mode. Use the smallest pattern that makes the variation, boundary, or reliability property explicit.

## Read catalogs correctly

Broad NestJS pattern lists often combine several different design levels:

- modular and hexagonal architecture shape system boundaries;
- controller-service-repository describes a possible layered request flow;
- dependency injection is a construction and inversion mechanism;
- middleware, guards, pipes, interceptors, and filters are framework lifecycle mechanisms;
- default provider scope is a container lifetime, not a reason to implement a static GoF Singleton;
- Strategy, Factory, Builder, Adapter, Bridge, Decorator, Proxy, Template Method, and Chain of Responsibility are object collaboration patterns;
- CQRS, repositories, events, outbox, and sagas address application, persistence, or distributed-system forces.

The categories can cooperate, but they are not interchangeable. Do not install patterns from a popularity chart, apply all patterns in a category, or infer runtime scalability from a class diagram. Select from repository evidence and verify the resulting behavior.

## Strategy

**Signal:** one stable operation has several real algorithms selected by tenant, product, region, or configuration.

```typescript
export interface FraudPolicy {
  evaluate(input: FraudInput): Promise<FraudDecision>;
}
```

Keep selection separate from execution. A strategy should not inspect its own type discriminator. Avoid when one algorithm exists and no accepted requirement introduces another.

## Factory

**Signal:** construction is complex or depends on a validated discriminator.

```typescript
@Injectable()
class ExporterFactory {
  constructor(
    private readonly csv: CsvExporter,
    private readonly pdf: PdfExporter,
  ) {}

  for(format: ExportFormat): Exporter {
    if (format === 'csv') return this.csv;
    if (format === 'pdf') return this.pdf;
    throw new UnsupportedExportFormat(format);
  }
}
```

Do not use a factory to hide a single `new` with no policy.

Nest custom `useFactory` providers are container construction factories. They are useful for validated configuration and dependency-aware setup, but they should not perform ordinary business workflows during bootstrap.

## Builder

**Signal:** construction has many optional or ordered parts and one final validation step should produce a complete value, request, configuration, or query specification.

Keep invalid intermediate state inside the builder and return a validated result from `build()`. For database queries, prefer the ORM's parameterized query builder or a typed criteria object when it already expresses the requirement. Do not introduce a fluent API for a clear constructor or object literal.

## Adapter

**Signal:** an external SDK, legacy model, or transport shape does not match the application contract.

The adapter translates types, errors, timeouts, and semantics. It should not leak vendor-specific status codes through an otherwise vendor-neutral port.

## Bridge

**Signal:** an abstraction and its implementation have two independent, real variation axes whose combinations would otherwise multiply subclasses.

Use composition so each axis can evolve independently, with Nest provider tokens selecting the implementations at the composition root. If only a vendor shape must be translated, use Adapter. If only an algorithm varies, use Strategy. Bridge is uncommon in ordinary NestJS features and should not be introduced merely to rename a port and adapter.

## Facade

**Signal:** consumers need one cohesive operation over a complex subsystem.

In NestJS, an exported application service often serves as the facade of a feature module. Keep the facade focused on that capability; do not create an application-wide service that forwards unrelated calls.

## Layered controller-service-repository flow

**Signal:** transport mapping, application coordination, and persistence have distinct responsibilities or change pressures.

A controller adapts the transport contract. A cohesive application service or use case coordinates the operation. A repository is optional and should express application persistence needs when isolating the ORM is valuable. Do not require three classes for every CRUD endpoint, put all business logic in a generic service, or wrap an ORM with an interface that simply reproduces its API.

## Decorator

**Signal:** behavior should wrap a stable operation without changing its contract—metrics, caching, tracing, or retry at a port boundary.

Distinguish the GoF object decorator from TypeScript/Nest metadata decorators. Nest interceptors can provide request-level wrapping, while an object decorator can wrap an application port outside HTTP.

Retries must be limited to operations safe to retry and must respect timeouts/idempotency.

## Proxy

**Signal:** access, laziness, remote invocation, or caching must be controlled behind the same interface.

Be explicit about remote failure semantics; a network proxy is not behaviorally identical to an in-memory object unless the contract includes latency, timeout, and partial failure.

A caching proxy also needs key ownership, TTL, invalidation, serialization, stampede behavior, observability, and a safe fallback. The wrapper shape alone does not make caching correct or improve performance.

## Observer and domain events

**Signal:** a fact has occurred and independent consumers may react without changing the source operation.

Use an in-process event for best-effort decoupling inside one process. Use a durable integration event plus outbox when other processes must reliably observe a committed change.

Avoid events when the producer requires an immediate result to complete its invariant.

## Command

**Signal:** a use-case request benefits from a named message, handler, middleware pipeline, audit trail, or dispatch abstraction.

Nest's CQRS package can implement commands, queries, and events. A plain injectable use-case class is simpler when dispatch adds no capability.

A command object or command bus does not automatically make work durable, queued, replayable, or auditable. Those properties require explicit persistence, broker, idempotency, ordering, and recovery design.

## Template Method

**Signal:** a workflow sequence is stable while a small number of explicitly supported steps vary, and the inheritance contract is intentionally part of the design.

Prefer composition with injected policies or steps when variations can combine independently. An abstract base workflow can be appropriate for a genuinely fixed skeleton, but inheritance couples subclasses to protected hooks and initialization behavior; do not use it only to remove a few repeated lines.

## Chain of Responsibility

**Signal:** ordered processors may handle, transform, authorize, or reject a request.

Nest middleware, guards, pipes, and interceptors form framework-managed chains. Put behavior in the correct lifecycle stage rather than building a parallel chain.

## Repository

**Signal:** the domain/application needs collection-like persistence operations independent of ORM details.

Design methods from use cases (`findPendingForSettlement`) rather than exposing a generic query builder. Do not wrap an ORM only to reproduce its complete API.

Repository is not essential for every NestJS application. An ORM repository used directly inside a cohesive infrastructure/application boundary can be sufficient when persistence substitution, domain isolation, and focused test seams do not justify another abstraction.

## Nest provider lifetime versus Singleton

Nest uses singleton provider scope by default. Let the container manage that lifetime instead of adding static `getInstance()` methods or global mutable registries.

Register a shared provider once in its owning module and export it deliberately. Registering the same class separately in multiple modules can create separate instances. Never store per-request mutable state in a default-scoped provider, and use request or transient scope only for a real lifetime requirement.

## Unit of Work

**Signal:** one use case changes several aggregates/repositories atomically and needs an explicit transaction boundary.

Keep transaction control at the application/infrastructure boundary. Avoid starting transactions in controllers or hiding long external network calls inside a database transaction.

## Specification

**Signal:** a business rule or query predicate is composed and reused across contexts.

Do not mix an in-memory domain predicate with an ORM expression unless the abstraction clearly supports both semantics and tests them.

## Transactional outbox

**Signal:** a database change and integration event must not diverge.

Write the aggregate change and outbox record in one local transaction. A relay publishes with retries; consumers remain idempotent. Plan retention, ordering keys, poison events, and observability.

## Saga/process manager

**Signal:** a long-running workflow spans services/transactions and needs explicit state, compensations, timeouts, and correlation.

Do not call a chain of ordinary service methods a saga. The pattern earns its cost only when partial progress and recovery are real domain concerns.

## Selection questions

Before adding any pattern:

1. What concrete change or failure is difficult now?
2. What remains stable, and what varies?
3. Who owns the abstraction?
4. What new indirection or runtime state appears?
5. How will tests prove all implementations preserve the contract?
6. What simpler design was rejected, and why?

If those questions have no concrete answers, keep the direct implementation.

For Nest-specific semantics, verify the current official documentation for [modules](https://docs.nestjs.com/modules), [custom providers](https://docs.nestjs.com/fundamentals/custom-providers), [guards](https://docs.nestjs.com/guards), [interceptors](https://docs.nestjs.com/interceptors), [injection scopes](https://docs.nestjs.com/fundamentals/injection-scopes), and [CQRS](https://docs.nestjs.com/recipes/cqrs).
