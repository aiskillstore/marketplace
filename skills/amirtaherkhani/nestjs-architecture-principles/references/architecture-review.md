# Architecture Review

Review the system that exists, not an imagined greenfield replacement.

## 1. Establish the baseline

Collect evidence for:

- deployables and bootstrap entry points;
- feature modules and import/export graph;
- transport handlers and request/message flow;
- application operations and domain rules;
- database, cache, queue, and vendor ownership;
- synchronous and asynchronous dependencies;
- transaction and consistency boundaries;
- security principals and tenant boundaries;
- tests, telemetry, and deployment constraints.

Write a compact baseline such as:

> Modular NestJS monolith organized by feature, with TypeORM repositories private to most modules; Billing directly reads Orders tables and creates the only cross-capability write leak.

## 2. Tie findings to change pressure

Do not report style preferences as architecture defects. A finding needs evidence and impact.

Use this format:

```text
ARCH-001 [high] Billing writes an Orders-owned table
Evidence: file paths, imports, and call path
Impact: invariant bypass and coordinated schema releases
Minimal remedy: export an Orders application operation and migrate the caller
Validation: integration test proves the invariant and no external repository import remains
```

Severity:

- **Critical:** current security, data-loss, tenant-isolation, or availability risk.
- **High:** boundary flaw likely to create incorrect behavior or block a known change.
- **Medium:** maintainability or operability cost with credible evidence.
- **Low:** localized improvement with limited risk.

## 3. Review questions

### Capabilities and modules

- Do module names express the business?
- Are providers private by default and exports intentional?
- Is there one clear owner for each invariant and write model?
- Are global and shared modules controlled?
- Is the import graph acyclic?

### Dependencies

- Do domain/application policies import framework or infrastructure details?
- Are ports owned by the consumer side?
- Are abstractions justified by volatility, substitution, or test value?
- Does runtime lookup hide dependencies?

### Data and consistency

- Are transactions aligned with use cases?
- Are cross-module reads and writes intentional?
- Are events published atomically when reliability requires it?
- Are idempotency and ordering defined at asynchronous boundaries?

### Operations

- Can the system start, become ready, drain, and stop predictably?
- Are timeouts and resource limits explicit?
- Can telemetry distinguish module/operation failures?
- Does a proposed service split include on-call and contract ownership?

## 4. Recommend one path

Compare viable options, then choose. State:

- what the recommendation optimizes;
- what it does not optimize;
- why a simpler option is insufficient or why a more complex option is unnecessary;
- the first reversible step.

## 5. Migrate incrementally

A common boundary repair sequence:

1. Characterize current behavior with tests and telemetry.
2. Define the target public operation or port.
3. Adapt the current implementation behind it.
4. Move one caller at a time.
5. Remove deep imports and obsolete exports.
6. Add a static or architecture test to prevent regression.
7. Remove temporary `forwardRef`, compatibility adapter, or dual-write path.

## Architecture tests

Depending on the repository, protect boundaries with:

- ESLint restricted imports or dependency-cruiser rules;
- module compilation tests;
- tests that scan forbidden `@nestjs/*` or ORM imports in domain folders;
- contract tests for provider adapters;
- integration tests for transaction and event behavior;
- CI checks for circular dependencies.

Do not add a new architecture-test dependency if a small existing lint rule can enforce the same boundary.
