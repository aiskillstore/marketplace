# Shared DDD Compliance Checklists

Severity levels and layer-by-layer checklists referenced by both `ddd-check-incremental` and `ddd-check-full`.

## Severity Levels

| Level | Criteria |
|---|---|
| **CRITICAL** | Architecture violation — wrong layer dependency, missing required base class, domain depends on infrastructure |
| **HIGH** | Rule violation — wrong naming, public identity setter, domain service with no behavior, wrong exception mode |
| **MEDIUM** | Convention deviation — anemic entity, missing Field wrapper, no JavaDoc on public API |
| **LOW** | Style — inconsistent formatting, missing @Override |

## Domain Layer Checklist

- [ ] All aggregates extend `BaseAggregate<ID>`
- [ ] All entities extend `BaseEntity<ID>`
- [ ] All value objects extend `BaseValue`
- [ ] `setId()` is `protected`, not `public`
- [ ] No infrastructure imports (no Mapper, no JPA, no SQL)
- [ ] Repository interfaces extend `AggregateRepository<T, ID, Q>`
- [ ] External calls go through `GatewayI` interfaces
- [ ] Aggregate methods = business behaviors, not CRUD
- [ ] Design patterns FORBIDDEN in domain (Strategy, Factory, etc.)
- [ ] Blocking mode (阻断型) throws exception, branching mode (分支型) returns ResultDO

## Application Layer Checklist

- [ ] Cmd services extend `ApplicationCmdService`
- [ ] Qry services extend `ApplicationQueryService`
- [ ] APP catches Domain/Adaptor exceptions, converts to ResultDO
- [ ] APP never throws exceptions to Adaptor

## Infrastructure Layer Checklist

- [ ] Repository impls in correct package
- [ ] PO classes separate from domain objects
- [ ] Converter/Assembler between PO and domain
- [ ] `LevelLock` implementations are concrete (extend abstract class)
- [ ] All `GatewayI` implementations here, not in domain

## Client Layer Checklist

- [ ] All DTOs extend `BaseDTO`
- [ ] No domain classes exposed in DTOs
- [ ] Client module is deployable standalone (no domain imports)
