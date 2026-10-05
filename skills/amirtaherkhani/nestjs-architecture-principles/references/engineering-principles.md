# Engineering Principles as Decision Tests

Principles help expose trade-offs. They are not automatic verdicts.

## Cohesion and coupling

Ask:

- Do these files change for the same business reason?
- Can a consumer use the capability without knowing its internals?
- Does changing a vendor, table, or transport force unrelated features to change?
- Is a shared abstraction coupling concepts that only look similar?

Move behavior toward the data and invariants it owns. Prefer a narrow explicit dependency over ambient globals or deep import paths.

## KISS

Choose the simplest design that handles known correctness and failure requirements. Simplicity includes operational behavior; a one-line fire-and-forget call is not simple if failures disappear.

Test: can a maintainer trace the main success and failure paths without simulating hidden framework magic?

## YAGNI

Do not build hypothetical extension points, transports, tenants, providers, or services. Do preserve a boundary when a current requirement already has volatility, security, or ownership pressure.

Test: which accepted requirement or observed change makes this abstraction pay rent now?

## DRY and the Rule of Three

Remove duplicated knowledge, not every repeated line. Two DTOs may look identical today but represent different contracts and should evolve independently. Three repeated mapping implementations for the same concept may reveal a missing owner.

Test: if one business rule changes, how many places must change together?

## Separation of concerns

- Transport validates and maps protocol concerns.
- Application coordinates use cases.
- Domain enforces business invariants.
- Infrastructure handles persistence and external systems.
- Nest modules assemble dependencies.

The separation may be conceptual within a small feature rather than a directory for every layer.

## Dependency inversion

High-level policy should not import volatile low-level details. Introduce an application-owned port when the direction matters. Do not confuse dependency inversion with wrapping every library in a class.

Test: can the business operation be understood and tested without importing the ORM, broker, or vendor SDK?

## Information hiding

A module should expose what consumers need and hide schema, caching, retry, and mapping decisions. Avoid getters that leak an entire ORM model or vendor response.

Test: could the implementation change without editing consumers?

## Law of Demeter

Avoid navigation chains that make one feature understand another feature's object graph:

```typescript
// Fragile knowledge of several internals
order.customer.account.plan.canUse(feature);

// Owner answers the business question
order.canUseFeature(feature);
```

Do not apply this as a ban on ordinary property access in data-transfer structures.

## Tell, do not ask

Place decisions with the object or policy that owns the invariant. Application services may still query state to coordinate multiple owners. Avoid moving orchestration into entities merely to eliminate conditionals.

## Explicit contracts

Validate at trust boundaries. Make nullability, idempotency, ordering, timeout, and error behavior visible. Treat API DTOs, events, database constraints, and provider tokens as contracts with consumers.

## Fail fast and degrade deliberately

Reject invalid configuration at startup. At runtime, distinguish retryable, non-retryable, partial, and unavailable states. A fallback must preserve safety; never silently bypass authorization, billing, or data-integrity checks.

## Evolutionary architecture

Prefer changes that are reversible and independently deployable:

- add before remove;
- support old and new contracts during migration;
- separate schema expansion from cleanup;
- measure before and after;
- record a removal condition for temporary compatibility.

## Principle conflict examples

| Tension | Decision test |
| --- | --- |
| DRY vs coupling | Share stable knowledge, not coincidental shape |
| KISS vs reliability | Include known failure behavior; omit speculative machinery |
| Encapsulation vs reporting | Expose a purpose-built query/read model, not internal persistence |
| Strict layering vs delivery | Layer only the complex capability; keep simple features compact |
| Consistency vs autonomy | Choose explicit transactions or eventual consistency from product needs |
| Reuse vs ownership | Prefer duplicated adapters over shared business write ownership |

The goal is local reasoning, safe change, and observable behavior—not maximum compliance with terminology.
