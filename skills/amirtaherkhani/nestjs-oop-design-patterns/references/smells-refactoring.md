# Code Smells and Refactoring

A smell is a prompt to investigate, not proof of a defect.

## God service

**Evidence:** unrelated dependency clusters, many actors requesting changes, mixed transport/domain/persistence logic, broad test setup.

**Refactor:** identify application operations and domain policies; move vendor/persistence behavior to adapters; keep a cohesive feature facade if consumers benefit.

Do not split one readable service into dozens of one-line providers without reducing coupling.

## Generic `BaseService<T>`

**Evidence:** feature services inherit CRUD methods but override authorization, filtering, events, or transaction behavior inconsistently.

**Refactor:** compose focused persistence helpers or keep explicit feature operations. Share stable mechanics, not business semantics.

## Primitive obsession

**Evidence:** repeated parsing/validation, mixed identifiers, currency/unit bugs, conditionals around the same primitive.

**Refactor:** introduce a value object or branded type where it protects a real invariant. Do not wrap primitives that carry no behavior or confusion risk.

## Feature envy and train wrecks

**Evidence:** one class repeatedly traverses another object's internals to decide behavior.

**Refactor:** move the decision to the owner or expose a purpose-built query. Do not hide an anemic model by merely shortening a chain.

## Repeated conditional dispatch

**Evidence:** the same `switch` on provider/type/region appears across operations and changes together.

**Refactor:** select a strategy, handler, or adapter in one place. Keep a single stable switch if it is clearer than a hierarchy.

## Shotgun surgery

**Evidence:** one business rule change edits controllers, services, entities, and multiple modules.

**Refactor:** find the missing owner and centralize knowledge. Preserve distinct external DTOs even if mapping remains duplicated.

## Divergent change

**Evidence:** one class changes for unrelated business, vendor, transport, and persistence reasons.

**Refactor:** split by change axis and lifecycle, then inject collaboration explicitly.

## Leaky adapter

**Evidence:** application code imports SDK response types, ORM exceptions, broker messages, or HTTP status codes.

**Refactor:** translate at the edge into application-owned values and errors. Add contract tests for the adapter.

## Circular dependency and `forwardRef`

**Evidence:** two providers need each other's behavior and constructor order becomes relevant.

**Refactor:** repair ownership, extract a coordinator/policy, introduce a narrow read port, or replace a reverse call with an event when consistency allows.

## Hidden service locator

**Evidence:** business methods call `ModuleRef.get`, a global container, or static singleton to find dependencies.

**Refactor:** declare constructor dependencies. Retain runtime discovery only for true plugin/lifecycle requirements.

## Boolean flag arguments

**Evidence:** a method changes responsibility or behavior substantially based on flags.

**Refactor:** use named operations, an options object, or strategies when variations are real. A simple optional formatting flag may not justify new classes.

## Data-only domain model

**Evidence:** entities expose all state while services own every invariant.

**Refactor:** move business decisions and state transitions to the entity/policy. Keep cross-aggregate orchestration in the application layer.

## Speculative generality

**Evidence:** unused interfaces, factories, hooks, feature flags, or provider registries with one hypothetical future consumer.

**Refactor:** remove the abstraction and keep the direct design. Git preserves the option to restore it when a real requirement arrives.

## Safe refactoring loop

1. Reproduce behavior with a test or trace.
2. Make one structural change.
3. Keep external contracts stable.
4. Run the narrow test, then boundary/integration tests.
5. Measure complexity by improved locality and dependency reduction.
6. Remove transitional code.

Prefer a sequence of reversible refactors over a pattern rewrite.
