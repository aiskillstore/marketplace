# Standalone Semantic Review

Use these lanes when reviewing a NestJS repository. Optional architecture, OOP, and runtime skills can deepen a relevant lane; their absence does not block this audit. Confirm framework behavior against the target's installed version and official documentation.

## Architecture: trace a consumer, not just exports

Follow controller/message entry → application operation → storage/external adapter and Nest imports/providers/exports. Ask who owns each write and transaction. An exported storage provider is not automatically a defect: show a consumer bypassing a public operation and the concrete invariant, authorization, consistency, or change boundary it evades. A broad export with no harmful call path is a review candidate, not a confirmed bug.

Healthy control: a consumer calls the owning module's public operation, which enforces the invariant and performs the write. Do not demand a port, CQRS, separate service, or Clean Architecture layer when the existing direct design protects the contract. Confirm cycles from imports/wiring, not folder names or `forwardRef` alone.

## Object design: locate the policy

Read callers and public operations. Find invariants enforced inconsistently, hidden dependencies, unrelated reasons to change, or real interchangeable behavior. Trace at least one failing/unsafe path before proposing a pattern. File length, a `switch`, plain objects, and constructor injection are not defects by themselves. One boundary leak must not become separate architecture and OOP findings.

## Runtime and security: check boundary behavior

Trace input through actual pipes/DTO transformation, guards, handlers, filters, and response mapping. Query strings arrive as strings: Boolean coercion treats the string `"false"` as truthy. Verify omitted, true, false, and invalid values over HTTP using the repository's contract; do not assume a type annotation parses input. Inspect authentication separately from resource/tenant authorization.

Check retry/idempotency and transaction effects together. Validate timeouts, resource bounds, shutdown, and failure contracts from code and safe evidence. Never run live load, migration, external-service, or shared-database checks merely to complete a report.

## Performance: measurement before conclusions

Trace dependency calls and request counts, then measure a controlled workload when authorized. Repeated sequential I/O can suggest a hypothesis, not a measured latency claim. Compare the same inputs and environment before/after, preserve response ordering/equality and failure handling, and bound concurrency. Request-local deduplication differs from cross-request caching: stale data and authorization keys require separate justification.

## Evidence and negative controls

Report file/line and call-path evidence, impact, smallest remedy, and validation. Separate a known tool failure from a semantic finding. Mark unrun checks and uncertain performance/security claims as needing verification. Record healthy controls actually observed, and do not flag them simply because they resemble the seeded problem.

Sources: [Nest modules](https://docs.nestjs.com/modules), [pipes](https://docs.nestjs.com/pipes), and [testing](https://docs.nestjs.com/fundamentals/testing).
