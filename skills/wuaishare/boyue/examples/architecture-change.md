# Example: Architecture Change

## Scenario

A plugin platform wants to replace an internal extension mechanism with a public extension API used by third-party developers.

This is not a normal refactor. Once external developers depend on the API, compatibility and migration obligations become long-lived.

## Commitment Boundary

Question:

> Is a public API required to solve the current ecosystem problem, or would a private extension point be sufficient?

Evidence supports external integration, so the team chooses **COMMIT**.

Non-goal:

> Do not expose every internal object merely because it already exists.

## Risk Review

### Reversibility

Low. Third-party adoption makes breaking changes expensive.

### Failure consequence

High. A poor contract can create years of compatibility and maintenance cost.

### Shaping evidence

- document the minimum external use cases;
- prototype the API with two representative integrations;
- write an ADR for contract boundaries;
- review versioning and lifecycle expectations;
- rehearse deprecation behavior;
- define a limited beta period.

## Ownership Boundary

New ownership surface:

- public endpoint contract;
- versioning policy;
- documentation;
- support and compatibility expectations;
- deprecation and migration obligations.

Decision: **REDUCE** before **OWN**.

The first production version exposes only the smallest stable surface needed by validated integrations. Internal objects remain private.

## Deliver

Ship a narrow beta Vertical Slice:

```text
Third-party client calls one supported capability
  ↓
Receives a documented response
  ↓
Errors are observable
  ↓
Version lifecycle is defined
```

The expensive decision receives more shaping because the cost of being wrong is high and reversibility is low.
