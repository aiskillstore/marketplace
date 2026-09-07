# Delivery Patterns

“薄发” is about limiting the surface area of new ownership without lowering quality.

> **薄，是变更面薄，不是质量薄。**

## Minimum Coherent Value Slice (MCVS)

MCVS describes **what size of value should enter ownership**.

A coherent slice should complete one real user or system goal and include only the necessary:

- interface or interaction path;
- business logic;
- data/state changes;
- permissions;
- error handling;
- observability;
- rollback, disablement, or migration safety appropriate to the risk.

The goal is not “minimum code”. The goal is the smallest change that is still complete enough to be useful, testable, and responsibly owned.

## Vertical Slice

Vertical Slice describes **how to cut the implementation**.

Prefer an end-to-end slice through UI/API/business logic/data rather than completing every database concern first, then every backend concern, then every UI concern.

Example:

```text
User goal
  ↓
Necessary UI / API
  ↓
Necessary business logic
  ↓
Necessary data
  ↓
Necessary tests and observability
```

## Walking Skeleton

A Walking Skeleton is a minimal end-to-end implementation of the system architecture that can execute a real path.

Use it to prove that the essential delivery path works before filling in broad functionality.

A Walking Skeleton is especially useful when integration risk is more important than feature depth.

## Tracer Bullet

A Tracer Bullet is an early end-to-end probe through uncertain technical terrain.

Use it when the most important question is whether a proposed path can reach the target at all—for example, a new protocol, toolchain, model integration, or cross-service workflow.

A Tracer Bullet may be disposable. Do not confuse a successful probe with production readiness.

## Relationship between the patterns

- **MCVS** — what coherent value is worth owning?
- **Vertical Slice** — how should implementation be sliced across layers?
- **Walking Skeleton** — what minimal end-to-end system path must exist?
- **Tracer Bullet** — what uncertain path should be tested early?

These patterns can be combined. For example, a new product may first use a Tracer Bullet to test a risky model integration, then a Walking Skeleton to establish the end-to-end system, and finally Vertical Slices to deliver successive MCVS units.
