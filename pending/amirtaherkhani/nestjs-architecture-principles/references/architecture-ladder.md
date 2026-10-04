# Architecture Ladder

Choose the lowest level that satisfies known requirements. The levels are evolutionary options, not maturity badges.

## Level 1: cohesive feature modules

Use for most CRUD-heavy applications and early products.

```text
src/
  orders/
    dto/
    orders.controller.ts
    orders.service.ts
    orders.repository.ts
    orders.module.ts
  catalog/
  app.module.ts
```

Rules:

- Organize by business capability, not global technical buckets such as `controllers/` and `services/`.
- Keep controllers thin and services cohesive.
- Keep persistence access inside the owning feature.
- Export only the operations other features actually need.
- A module may own several related tables; a table does not automatically deserve its own module.

Upgrade signal: business rules are difficult to test without Nest or the ORM, infrastructure choices leak into use cases, or a feature contains multiple workflows with different change pressure.

## Level 2: layered feature modules

Use when a capability has meaningful domain rules, several entry points, or volatile infrastructure.

```text
src/orders/
  domain/
    order.ts
    order-policy.ts
  application/
    place-order.ts
    ports/
      order-repository.ts
      payment-gateway.ts
  infrastructure/
    persistence/
      typeorm-order.repository.ts
    payments/
      stripe-payment.gateway.ts
  presentation/
    http/
      orders.controller.ts
      dto/
  orders.module.ts
```

Dependency direction:

```text
presentation ──> application ──> domain
infrastructure ────────────────> application/domain
orders.module ── wires every implementation at the edge
```

Rules:

- Domain objects contain invariants and import no framework or persistence package.
- Application operations depend on ports owned by the application side.
- Infrastructure implements ports and performs mapping.
- Transport DTOs do not become domain entities by convenience.
- The Nest module is the composition root for the capability.

Do not create a port for every class. A stable, local helper with no external effect usually needs no interface.

## Level 3: hexagonal boundaries or CQRS

Hexagonal design is useful when the same application behavior is reached through multiple adapters or depends on several replaceable edges. CQRS is useful when command and query models have materially different authorization, performance, consistency, or representation needs.

Signals that justify CQRS:

- complex workflows benefit from explicit command handlers;
- read models need denormalized projections or different stores;
- auditability and domain events are central requirements;
- command and query scaling differ;
- teams can support eventual-consistency and handler-discovery complexity.

Signals that do not justify CQRS:

- a desire to place every service method in a separate class;
- simple CRUD with identical read/write models;
- using a bus only to call a handler in the same process;
- no operational plan for projections, replay, ordering, or failures.

Keep commands imperative (`PlaceOrder`) and queries descriptive (`GetOrderDetails`). A command succeeds or fails; it should not become a generic data-fetching channel.

## Level 4: independently deployed services

Split a modular monolith only when at least one strong boundary exists:

- independent release cadence or team ownership;
- independent scaling profile;
- distinct security or compliance zone;
- failure isolation that cannot be achieved in-process;
- different runtime or availability requirement;
- data ownership that can be made explicit.

Before splitting, document:

- API/event contract and compatibility policy;
- database ownership and migration plan;
- latency, timeout, retry, and idempotency behavior;
- observability and on-call ownership;
- local development and test strategy;
- cost of partial failure and distributed transactions.

If two services share tables, require synchronized releases, or call each other for every request, the split has probably created a distributed monolith.

## Decision table

| Requirement | Default response |
| --- | --- |
| Small team, one deployable, mostly CRUD | Feature-module modular monolith |
| Rich invariants and multiple adapters | Layer the affected feature |
| Vendor API changes often | Add an application-owned port and infrastructure adapter |
| Read model differs radically from writes | Consider CQRS for that bounded capability |
| CPU-heavy job needs independent capacity | Separate worker deployment before a business microservice split |
| One feature needs independent ownership and data | Consider service extraction after contract design |
| Circular module graph | Repair ownership; do not jump to microservices |
| Need faster delivery | Reduce boundaries and coordination, not necessarily add infrastructure |

## Architecture decision record

Record consequential choices with:

```text
Title
Status and date
Context and constraints
Decision
Alternatives considered
Consequences and what is not optimized
Migration/rollback
Validation signals
```

Architecture is successful when likely changes remain local, contracts are explicit, and operators can understand failure—not when the directory tree is maximally elaborate.
