---
name: nestjs-architecture-principles
description: 'Designs and reviews NestJS application architecture using cohesive feature modules, modular monoliths, layered or hexagonal boundaries, dependency inversion, and pragmatic engineering principles. Use when planning a NestJS project, changing module boundaries, evaluating Clean Architecture or DDD, resolving circular dependencies, defining ports and adapters, reviewing coupling, or deciding whether CQRS or microservices are justified. Do not use for pure frontend work or non-NestJS backends. When other skills also apply, reconcile ownership before mutation.'
license: MIT
metadata:
  author: amirtaherkhani
  version: '1.1.2'
---

# NestJS Architecture and Principles

Make architecture decisions from the repository's actual constraints. Prefer the least complex design that protects the required boundaries and can evolve safely.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Inspect repository instructions, installed versions, module wiring, contracts, callers, tests, and affected commands. Preserve user changes. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns architecture level, capability/module APIs, dependency direction, data/write and transaction boundaries, ports, and service extraction. When installed and relevant, coordinate with:

- `nestjs-oop-design-patterns`: object responsibilities, invariants, and patterns.
- `nestjs-features-performance`: lifecycle, API/security, testing, runtime, and performance.
- `nestjs-professional-software-engineering`: implementation and verification.
- `nestjs-code-audit`: read-only quality evidence and deduplicated reporting.
- `nestjs-feature-audit`: branch-specific roadmap gate and feature reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Check for incompatible edits/contracts, command order or side effects, competing owners, and unmet version, evidence, authorization, or repository prerequisites. Resolve using explicit user intent, repository contracts, verified runtime constraints, then the narrowest owner. Assign one lead per decision; do not create parallel designs to satisfy incompatible advice. If a material conflict remains, stop before mutation and ask for the smallest missing decision. Audits stay read-only; explicit fix authorization applies in a distinct implementation phase.

## Start with evidence

Before recommending or changing architecture:

1. Read `package.json`, `nest-cli.json`, TypeScript configuration, bootstrap files, and the relevant modules.
2. Map the module import graph, provider exports, entry points, persistence ownership, transports, and existing tests.
3. Identify the business capability and the concrete change pressure: team ownership, independent scaling, volatile integrations, transaction boundaries, security, or delivery speed.
4. State the current architecture in one sentence. Do not label a project "Clean Architecture" or "DDD" from folder names alone.
5. Preserve healthy local conventions. Flag a convention only when it damages correctness, security, operability, or an explicit contract.

If the task is version-sensitive, verify the installed NestJS version and current official documentation before using an API or command.

## Choose the architecture level

Use the architecture ladder in [references/architecture-ladder.md](references/architecture-ladder.md).

Default direction:

- Start with a modular monolith organized by business capability.
- Add internal layers when domain logic or infrastructure volatility makes the boundary valuable.
- Add ports where the application needs to isolate a replaceable external concern.
- Add CQRS only when command and query behavior genuinely diverge.
- Split a service only when it has an independent deployment, ownership, scaling, data, or failure boundary.

Never introduce layers, buses, repositories, factories, or services only to make the folder tree resemble a diagram.

## Protect these boundaries

1. **Modules expose a small public API.** Providers are private unless another module has a real use for them.
2. **A business capability owns its invariants and writes.** Other modules collaborate through an exported application service, port, event, or deliberately designed read model.
3. **Dependencies point toward policy.** Domain code does not import NestJS, an ORM, HTTP types, queue jobs, or vendor SDKs.
4. **Controllers and transport handlers adapt.** They authenticate/authorize through framework mechanisms, validate transport input, invoke an application operation, and map the result.
5. **Application operations coordinate.** They define use-case flow and transaction intent without absorbing persistence or transport details.
6. **Infrastructure implements edges.** ORMs, brokers, caches, file systems, and external APIs stay behind explicit boundaries when their volatility or test cost warrants it.
7. **Cycles are design feedback.** Treat `forwardRef()` as a last-resort compatibility tool, not the default fix.
8. **The composition root owns wiring.** Nest modules and providers assemble implementations; business objects do not locate dependencies at runtime.

For the consolidated rule set, load [references/architecture-rules.md](references/architecture-rules.md). For detailed NestJS boundaries, load [references/module-boundaries.md](references/module-boundaries.md) and [references/dependency-injection.md](references/dependency-injection.md).

## Apply principles pragmatically

Use [references/engineering-principles.md](references/engineering-principles.md) as decision tests, not slogans.

When principles conflict, prefer this order:

1. correctness, security, and data integrity;
2. explicit external contracts and backward compatibility;
3. operability and failure containment;
4. established repository conventions;
5. design purity and local elegance.

KISS does not mean hiding failure cases. DRY does not mean abstracting coincidental similarity. SOLID does not require one class per verb. YAGNI does not excuse a boundary already demanded by a known requirement.

## Workflow

### For a new design

1. Define goals, constraints, non-goals, critical quality attributes, and expected change axes.
2. Choose the lowest architecture level that satisfies them.
3. Name capabilities and ownership before naming technical layers.
4. Draw dependencies and data ownership. Reject ambiguous write ownership.
5. Specify synchronous calls, events, transactions, and failure behavior.
6. Produce one recommended design and explain what it intentionally does not optimize.
7. Define architecture tests, integration tests, and operational checks that protect the decision.

### For an implementation or refactor

1. Trace the relevant request, message, or job end to end.
2. Identify the smallest boundary violation that causes the problem.
3. Move behavior toward its owner before adding an abstraction.
4. Introduce a port only if there are multiple implementations, a volatile edge, or a valuable test seam.
5. Keep the change incremental and preserve the public contract unless the user requested a migration.
6. Update affected tests, module wiring, documentation, and callers.

### For a review

Use [references/architecture-review.md](references/architecture-review.md). Report evidence-backed findings with severity, impact, a minimal remedy, and a validation step. Do not propose a rewrite when a boundary repair is sufficient.

## Reference routing

| Task | Load |
| --- | --- |
| Apply or review the consolidated architecture rules | [architecture-rules.md](references/architecture-rules.md) |
| Choose modular monolith, layers, hexagonal, CQRS, or services | [architecture-ladder.md](references/architecture-ladder.md) |
| Design feature modules, exports, ownership, or remove cycles | [module-boundaries.md](references/module-boundaries.md) |
| Define provider tokens, ports, scopes, factories, or dynamic modules | [dependency-injection.md](references/dependency-injection.md) |
| Define database ownership, repositories, migrations, transactions, or ORM boundaries | [database-orm.md](references/database-orm.md) |
| Decide service extraction, distributed data ownership, contracts, or messaging semantics | [microservices.md](references/microservices.md) |
| Apply KISS, YAGNI, DRY, cohesion, coupling, and dependency rules | [engineering-principles.md](references/engineering-principles.md) |
| Audit a repository or plan an incremental migration | [architecture-review.md](references/architecture-review.md) |

## Expected response

For architecture work, make the result easy to evaluate:

- **Baseline:** current architecture and evidence.
- **Decision:** one recommended direction.
- **Why:** constraints and trade-offs that drive it.
- **Boundaries:** module ownership, dependency direction, data ownership, and integration style.
- **Migration:** smallest safe sequence, when change is needed.
- **Validation:** tests, graph checks, runtime checks, and operational signals.

If no architecture change is justified, say so directly.
