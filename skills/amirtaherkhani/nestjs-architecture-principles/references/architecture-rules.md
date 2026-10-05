# Architecture Rules

Use these rules to shape a NestJS system without turning one preferred diagram into a universal answer. Inspect the repository and its change pressures before choosing a structure.

## Rules

### 1. Organize around business capabilities

Prefer cohesive feature modules such as `OrdersModule` or `BillingModule` over global technical buckets such as `ControllersModule` and `ServicesModule`. A feature should make its owned behavior, data, and public entry points easy to find.

Technical modules remain appropriate for reusable infrastructure such as configuration, telemetry, or a database client. They must not become a miscellaneous `SharedModule` that exports the entire container.

### 2. Keep module APIs small

Providers are private by default. Export only the application service, token, or read capability another module actually needs. Import the module that owns a provider instead of re-declaring the provider elsewhere.

Global modules are suitable for a few process-wide facilities. They are not a substitute for explicit capability dependencies.

### 3. Assign one owner to every invariant and write

Responsibility is defined by a reason to change, not class size or a one-method rule. Keep each business invariant and write path under one capability owner. If several modules coordinate a workflow, name the coordinator and its transaction boundary explicitly.

### 4. Point dependencies toward policy

Controllers, message handlers, persistence adapters, and vendor integrations depend on application policy. Domain code must not depend on Nest decorators, HTTP responses, ORM records, queue jobs, or vendor SDK types.

Use a direct local dependency when it is stable and remains inside one boundary. Add a port when an external or volatile edge, meaningful alternate implementation, or valuable test seam justifies it.

### 5. Treat cycles as design feedback

Map the import and provider graph before fixing a circular dependency. A cycle often exposes ambiguous ownership, a workflow that needs a coordinator, or an overly broad module API.

Repair ownership first. A narrow query port or an event can help only when its consistency and failure semantics fit. `forwardRef()` is a compatibility escape hatch, not the default architecture.

### 6. Choose calls, events, and queues by semantics

- Use a synchronous call when the caller needs an immediate result or shares one transaction.
- Use an in-process event for optional reactions whose failure and durability requirements are understood.
- Use a durable message or queue when work must survive process failure, absorb bursts, or run independently.

An event is not automatically more decoupled if publishers and consumers still share data ownership or deployment. Durable messages also require schema compatibility, idempotency, retry, ordering, and observability decisions.

### 7. Do not require repositories everywhere

Use an application-owned repository or store port when domain behavior needs persistence independence, several use cases need a stable capability-oriented interface, or an adapter is likely to change. Direct ORM access in a simple application service can be clearer for straightforward CRUD inside one owned boundary.

Never expose an ORM repository or entity as another feature's write API. Query methods should express a use-case need rather than merely mirror every ORM operation.

### 8. Keep wiring at the composition root

Construct and select implementations through Nest modules and providers. Business objects receive dependencies explicitly; they do not reach into `ModuleRef`, a global container, or static service locator during ordinary execution.

## Decision sequence

1. Name the capability, invariant owner, and required external contract.
2. Draw module imports, provider exports, data writes, and asynchronous paths.
3. Choose the lowest architecture level that protects the known boundary.
4. Define consistency, failure, and compatibility behavior before selecting a transport.
5. Add only the abstractions that isolate real volatility or clarify ownership.
6. Protect the result with module, architecture, integration, and contract tests.

## Conflict guardrails

- Object-level responsibility and pattern selection belong to the OOP and Design Patterns skill.
- Database ownership and transaction boundaries are detailed in [database-orm.md](database-orm.md).
- Service extraction and distributed ownership are detailed in [microservices.md](microservices.md).
- Runtime middleware, guards, pipes, interceptors, filters, queues, and performance controls belong to the Features, Scaling, and Performance skill.

See [module-boundaries.md](module-boundaries.md), [dependency-injection.md](dependency-injection.md), and the official NestJS guidance on [modules](https://docs.nestjs.com/modules), [providers](https://docs.nestjs.com/providers), [circular dependencies](https://docs.nestjs.com/fundamentals/circular-dependency), and [events](https://docs.nestjs.com/techniques/events).
