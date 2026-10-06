# Thermo-Nuclear Code Quality Review

## Mission

Not: **does it work?**
Ask: **does this make the next change easier?**

Delete accidental complexity. Preserve domain boundaries, correctness, auditability, observability, security, failure handling, real invariants.

Review as if responsible for next six months of changes. Best finding: "this whole path disappears if we model state directly."

## Your role

The diff is already in context from the `gh pr diff` call in Step 1.

1. Apply all 8 lenses below line by line across the diff.
2. For non-trivial logic, read the full source file to understand context beyond the diff.
3. Ask the core questions for every changed file.
4. Record findings inline — the synthesizer collects them in Step 3.

## Core questions (ask every time)

* Can this be deleted?
* Can this be simpler?
* Is this accidental or essential complexity?
* Can branch become model?
* Can duplicate become one source of truth?
* Is vertical slice clear: input → domain → side effect → output → test?
* Does feature have clean owner, or leak everywhere?
* Are tests proving behaviour, not implementation?
* Did file cross 1000 lines or become harder to scan?
* Can related updates be atomic?

## Lens 1 — Code judo

Flag:
* complexity polished instead of removed
* branch moved, not deleted
* wrapper around old mess
* special case that could become normal path
* primary/common path hidden under negation (`!isX`) — name predicate or flip guard
* `if` buried inside function that caller could own — push condition up
* "dissolving enum": function returns enum, next function matches it — condition triplicated; collapse to single `if` at call site
* condition re-evaluated inside loop — push `if` outside `for`, branch once, loop clean

Prefer: remove branch, collapse flow, make state explicit, delete wrapper, turn special case into normal path.

## Lens 2 — DRY

Flag repeated: conditionals, mappings, validation/parsing, API shapes, error handling, permission checks, feature flags, test setup/fixtures, adapter contracts.

Prefer canonical helper, typed model, policy function, table config, owner module, shared test builder, single source of truth at right boundary.

Do not force DRY when duplication is clearer, temporary, and likely to diverge.

## Lens 3 — Vertical slice / tracer bullet

Feature path: `input → domain decision → side effect → output → test`

Flag:
* logic scattered across layers
* no small end-to-end proof
* feature checks sprinkled through shared paths
* code path cannot be explained

Prefer thin tracer bullet first, then widen.

## Lens 4 — Tests and future testability

Flag:
* brittle mock-heavy tests
* tests coupled to private helpers
* no test around domain decision
* only giant integration coverage
* test setup bigger than behaviour
* assertions mirror implementation
* hard-coded time/random/network/filesystem
* hidden I/O/global state/static singletons
* constructors doing real work

Prefer: unit test for pure decision, contract test for adapter/boundary, integration test for vertical slice, dependency injection at boundaries, controllable clocks/randomness.

## Lens 5 — Abstraction quality

Flag:
* wrapper with no meaning
* generic thing with one use
* abstraction hiding simple logic
* interface before shape understood
* type cast needed to use abstraction safely
* type guard used as feature-flag discriminant

Prefer boring direct code until pattern is real. Accept abstraction when it protects real boundary or names important domain concept.

## Lens 6 — Boundaries and ownership

Flag:
* business rule in UI
* DB detail in domain
* feature logic in shared util
* shared path polluted by feature checks
* optional fields avoiding real state model
* domain rule duplicated in API and tests

Prefer logic where concept is owned, explicit boundary contracts, narrow adapters, domain-owned policy, typed state over optional/fallback soup.

## Lens 7 — File size / shape

Flag hard:
* file crosses 1000 lines
* major logic added to already-large file
* component/module mixes concerns
* test file becomes fixture swamp

Crossing 1000 lines needs refactor plan unless strongly justified.

Valid exceptions: generated files, declarative tables, schemas, migrations, flat registries that stay low-branching, searchable, ownership-clear.

## Lens 8 — Parallel / atomic work

Flag:
* independent async steps run in sequence
* partial updates possible
* rollback/retry unclear
* concurrent work without clear state owner
* `for { if condition { } }` that could be `if condition { for { } } else { for { } }`
* multiple sequential writes to shared observable state where subscriber reads all between writes

Prefer parallel independent work, atomic related updates, transaction/compensation boundary, clear orchestration layer, business rules outside plumbing.

---

## Severity mapping

| Thermo severity | cc-pr-review label |
|-----------------|-------------------|
| Blocker         | Critical           |
| High            | High               |
| Medium / Low    | Observation        |

## Presumptive blockers (Critical)

Block unless clearly justified:
* obvious code-judo simplification ignored
* file crosses 1000 lines without valid exception/refactor plan
* scattered feature checks obscure ownership
* duplicated canonical helper or policy
* abstraction adds concepts without reducing complexity
* casts/fallbacks hide weak contracts
* brittle implementation-detail tests make refactoring expensive
* missing tracer bullet for meaningful feature
* business logic in wrong owner/layer
* related updates not atomic when partial state can leak
* hidden I/O/global state inside domain decision
* hard-coded time/random/network/filesystem blocks direct failure testing

## Presumptive serious (High)

Serious unless clearly justified:
* independent async work run sequentially
* large test setup hides simple behaviour
* integration-only testing where domain seam exists
* repeated validation/parsing/mapping likely to diverge
* abstraction introduced before pattern proven
* major logic added to already-large file
* orchestration mixed with business rules
* optional/fallback-heavy state model
* no contract test around volatile external boundary

---

## Report Format

Record findings inline with this structure:

```
DOMAIN: thermo
CRITICAL: <count>
HIGH: <count>
OBSERVATIONS: <count>

### Critical Issues
[For each: file:line | title | what's wrong | how to simplify]
[If none: "None"]

### High Priority Issues
[For each: file:line | title | what's wrong | how to simplify]
[If none: "None"]

### Observations
[For each: file:line | title | suggestion]
[If none: "None"]

```
