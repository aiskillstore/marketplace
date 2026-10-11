# Performance

Read when reducing graph round trips, bounding pagination, or deciding whether work belongs in an
Action, Mutation, Query, or Workflow.

## Measure the semantic operation

Optimize from observed Client calls and payload sizes, not from database-specific shortcuts. Preserve
visibility, Policy, pagination, preconditions, and outcome evidence. A reduction is valuable only when
the same product invariant remains proven.

## Read through reusable Queries

Author reusable reads with `defineQuery` or `defineCompositeQuery` from `@astrale-os/sdk/query` and
execute them with the Action or Workflow's bound Client. Use resolved Schema Classes and Properties;
do not copy Definition keys, parse paths, issue raw database queries, or recreate the canonical Query
AST.

- Use one Query when one graph observation answers the question.
- Use a composite Query for a closed set of dependent reads with one final projection.
- Declare complete pagination when completeness is required; let the SDK bound and validate cursors.
- Project from the returned graph instead of re-reading each returned node.
- Treat an absent visible node as unavailable; do not infer that it does not exist.

Query execution owns remote response admission and pagination. A local projection should remain pure.

Do not replace several observations with a composite expecting one network round trip: ordinary
leaves still execute separately. A supported collection union can combine compatible Class collections;
measure the actual calls rather than inferring batching from one `query(...)` in the handler.

## Write one invariant as one Mutation

One bounded Mutation avoids per-item round trips only when all writes belong to one atomic invariant.
Its operations are not sequential commands: combine updates to one target and keep independently
raceable facts as preconditions. `runtime.md` covers the effect-set and pre-state constraints.

## Choose Action versus Workflow by semantics

An Action performs one semantic asynchronous operation and has no Step API. Do not split it merely to
make tests easier. Use a Workflow when the operation has several explicit observations or effects,
especially an Integration call between graph reads and writes. Stable steps improve diagnosability,
but the current inline runner is not a durability system.

## Avoid hidden N-plus-one work

Common regressions are:

- loading each node again after a Query already returned it;
- invoking one Mutation per item when one bounded atomic document owns the invariant;
- constructing an Integration client per invocation instead of once in Runtime initialization;
- performing external calls during module import;
- placing build, declaration-packaging, linter, or scaffolding code in the Worker closure.

Assert call counts at the injected Query, Mutation, and Integration boundaries. Inspect the built
Worker closure and packed package, because a source-only test cannot prove deploy-time isolation.

## Let the Registry lower Policy Node selectors

Do not duplicate a long list of concrete Classes to optimize an existential Policy. Kernel resolves
`node(Class)` through the pinned Registry to the active concrete descendants, including installed
foreign descendants. It resolves `node()` from the active concrete Registry and narrows that set from
the variable's Edge endpoints when the normalized Policy makes a safe constraint available. The
backend then evaluates exact label alternatives rather than discovering inheritance per candidate.

Selector choice still follows authorization semantics. `node.exact(Class)` is the smallest extent;
`node(Class)` can grow as concrete descendants are installed; and `node()` can remain broad when its
Edge topology does not narrow it. Review the resolved selector extent and Policy plan when a broad
existential is on a measured hot path, but do not make an exact selector merely to improve a benchmark.

## Stop before cleverness

Do not add a generic repository, cache, batching framework, persistent catalog, or adapter-specific
query abstraction without multiple real consumers and measured benefit. Prefer a small named Query or
Mutation owner and delete it again if the product operation disappears.
