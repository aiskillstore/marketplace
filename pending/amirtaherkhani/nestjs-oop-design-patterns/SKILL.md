---
name: nestjs-oop-design-patterns
description: 'Applies pragmatic OOP, SOLID, object-design rules, and design patterns to NestJS and TypeScript code. Use when writing or refactoring controllers, providers, use cases, entities, value objects, repositories, adapters, factories, strategies, handlers, or tests; when diagnosing god services, primitive obsession, inheritance misuse, duplicated conditionals, or leaky abstractions; and when selecting a pattern without over-engineering. Do not use for pure functional codebases or non-NestJS frontend work. When other skills also apply, reconcile ownership before mutation.'
license: MIT
metadata:
  author: amirtaherkhani
  version: '1.0.2'
---

# NestJS OOP and Design Patterns

Improve changeability and correctness through clear responsibilities, encapsulated invariants, and deliberate collaboration. Use patterns to solve observed forces, never as decoration.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Inspect repository instructions, installed versions, callers, tests, module wiring, and the observed design pressure. Preserve behavior and user changes; do not select a pattern before architecture/runtime constraints are known. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns object responsibilities, invariants, encapsulation, collaborator contracts, SOLID trade-offs, patterns, and behavior-preserving refactoring. When installed and relevant, coordinate with:

- `nestjs-architecture-principles`: module, dependency, data, and transaction boundaries.
- `nestjs-features-performance`: lifecycle, API/security, testing, runtime, and performance.
- `nestjs-professional-software-engineering`: implementation and verification.
- `nestjs-code-audit`: read-only quality evidence and deduplicated reporting.
- `nestjs-feature-audit`: branch-specific roadmap gate and feature reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Check for incompatible edits/contracts, command order or side effects, competing owners, and unmet version, evidence, authorization, or repository prerequisites. Resolve using explicit user intent, repository contracts, verified runtime constraints, then the narrowest owner. Assign one lead per decision; do not create parallel designs to satisfy incompatible advice. If a material conflict remains, stop before mutation and ask for the smallest missing decision. Audits stay read-only; explicit fix authorization applies in a distinct implementation phase.

## Inspect before prescribing

1. Read the relevant controller/provider/entity plus its callers, tests, module wiring, DTOs, and persistence mapping.
2. Identify the object's role: transport adapter, application coordinator, domain object/policy, infrastructure adapter, or composition root.
3. Name the actual pain: invariant leakage, divergent change, difficult substitution, hidden dependency, duplicated decision logic, or framework coupling.
4. Check repository conventions and existing abstractions before adding a new one.
5. Preserve behavior with a characterization test before a risky refactor.

Do not infer poor design from file length alone. Complexity, cohesion, public surface, dependency count, and change history are stronger evidence.

## OOP defaults

- Encapsulate invariants; do not merely move data behind getters and setters.
- Prefer composition and delegation over inheritance.
- Keep mutable state private and minimize its lifetime.
- Use polymorphism when a stable operation has real, varying implementations.
- Inject effects and volatility; keep deterministic calculations plain.
- Make invalid states difficult to construct when the domain value justifies the type.
- Use domain language consistently across types, methods, tests, and errors.
- Let Nest's container construct providers; do not instantiate dependency graphs inside business methods.

Load [references/oop-solid.md](references/oop-solid.md) for detailed OOP and SOLID guidance and [references/object-design.md](references/object-design.md) for entities, value objects, policies, services, and DTO boundaries.

## Apply SOLID as diagnostic questions

### Single Responsibility

Does this unit own one cohesive policy or change axis? A use case may coordinate several collaborators and still have one responsibility. Splitting every method into a provider creates navigation cost without cohesion.

### Open/Closed

Is a real variation forcing the same conditional to change repeatedly? Extract a strategy, policy, or adapter around that variation. Do not build extension points for hypothetical providers.

### Liskov Substitution

Can every implementation honor the same inputs, outputs, errors, side effects, timing assumptions, and invariants? If not, narrow the contract or use composition instead of inheritance.

### Interface Segregation

Does each consumer depend only on the capability it uses? Prefer small application-owned ports over one `CommonService` or generic repository interface.

### Dependency Inversion

Does high-level policy depend on an application contract while Nest modules select infrastructure implementations? Add a boundary for volatile effects, not an interface for every local class.

## Select patterns from forces

Use [references/pattern-catalog.md](references/pattern-catalog.md) and [references/nestjs-native-patterns.md](references/nestjs-native-patterns.md).

Treat pattern catalogs as discovery aids, not implementation checklists. Architecture styles, framework lifecycle mechanisms, provider lifetimes, and GoF object patterns solve different kinds of problems even when an article groups them together. Popularity, familiarity, or a claim that a pattern is "scalable" is not evidence that the current repository needs it.

| Signal | Consider | Avoid when |
| --- | --- | --- |
| Same operation, real interchangeable algorithms | Strategy | One stable algorithm |
| Construction varies by configuration/type | Factory | Constructor is already simple |
| Complex construction has ordered or optional validated steps | Builder | An object literal or constructor stays clear |
| Vendor model leaks into application code | Adapter | Library API is already isolated at the edge |
| Abstraction and implementation have two independent variation axes | Bridge | Adapter or Strategy handles the only variation |
| Complex subsystem needs a narrow entry point | Facade/application service | It becomes an unrelated god service |
| A stable workflow has a few deliberate extension steps | Template Method or composed pipeline | Inheritance would be the only reason to use it |
| Cross-cutting request behavior | Interceptor, guard, pipe, filter | Core business policy belongs in a domain/application object |
| Independent reactions to a completed fact | Domain/integration event | Caller requires an immediate transactional result |
| Explicit use-case messages add value | Command/query handler | Basic CRUD gains only indirection |
| Reliable event publication with a DB write | Transactional outbox | Best-effort in-process notification is sufficient |

Before applying a pattern, state the problem, why a direct solution is insufficient, and the added operational or cognitive cost.

## Refactoring workflow

1. Lock current behavior with focused tests.
2. Mark responsibilities and effects in the current code.
3. Move misplaced behavior to its owner before extracting abstractions.
4. Extract one seam around the observed variation or boundary.
5. Rewire through Nest providers without changing the public contract unnecessarily.
6. Remove obsolete branches, wrappers, and abstractions.
7. Run unit, module, integration, and e2e checks in proportion to the changed boundary.

Use [references/smells-refactoring.md](references/smells-refactoring.md) for symptom-to-refactoring guidance.

## Testing rules

- Test public behavior and invariants, not private method calls.
- Use plain unit tests for domain objects and policies.
- Instantiate a use case directly when constructor dependencies are simple; use `TestingModule` when Nest wiring or provider overrides are what the test must prove.
- Mock or fake boundaries you own, not the class under test.
- Add contract tests when several adapters implement the same port.
- Keep e2e tests for transport, validation, authorization, serialization, and real module wiring.

TDD is useful when behavior can be expressed incrementally, but do not falsely claim a red test was written first when changing an existing implementation. Match the repository's requested workflow.

## Reject rigid pseudo-rules

Do not enforce arbitrary limits such as ten-line methods, fifty-line classes, two fields per object, mandatory value objects for every primitive, or no `else` statements. Use them only as prompts to inspect cohesion and readability.

Do not force:

- inheritance where composition is clearer;
- a repository wrapper over an already suitable persistence boundary;
- factories for one straightforward constructor;
- domain events for synchronous return values;
- DTO reuse across unrelated external contracts;
- a generic `BaseService<T>` that erases feature-specific invariants.

## Reference routing

| Task | Load |
| --- | --- |
| Apply encapsulation, composition, polymorphism, or SOLID | [oop-solid.md](references/oop-solid.md) |
| Design entities, value objects, policies, services, and DTO mapping | [object-design.md](references/object-design.md) |
| Select creational, structural, behavioral, persistence, event, or reliability patterns | [pattern-catalog.md](references/pattern-catalog.md) |
| Map patterns to Nest modules, providers, guards, pipes, interceptors, filters, and CQRS | [nestjs-native-patterns.md](references/nestjs-native-patterns.md) |
| Diagnose smells and choose a safe refactor | [smells-refactoring.md](references/smells-refactoring.md) |

## Expected response

For a design or review, report:

- **Role and responsibility:** what the object should own.
- **Evidence:** the concrete coupling, invariant leak, or change pressure.
- **Pattern or direct design:** one recommendation and why it fits.
- **Trade-off:** indirection, lifecycle, consistency, or testing cost introduced.
- **Change:** smallest safe refactor.
- **Verification:** behavior and contract checks.

If a pattern is not justified, recommend the direct implementation.
