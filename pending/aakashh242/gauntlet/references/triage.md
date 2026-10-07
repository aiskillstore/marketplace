# Triage: choose work that can change the verdict

## Establish a review contract

Record the artifact and snapshot, user's objective, authoritative requirements, in-scope components and direct consumers, excluded areas, permitted operations, baseline failures, and available verification tools. Include uncommitted changes in the snapshot; a commit hash alone is insufficient for a dirty tree. Do not sweep unrelated secrets into a digest or artifact bundle. Prefer a scoped file manifest with content hashes and record what was excluded.

Resolve ambiguous intended behavior from requirements and project conventions. Ask only when the ambiguity changes correctness, authority, or a costly/irreversible decision. Otherwise state a bounded assumption and continue. Do not silently convert a design review into an implementation project.

## Risk routing

Use the highest applicable risk, not an average that dilutes a severe failure. **Focused**: small, local, reversible behavior with no security/data-integrity boundary. **Standard**: normal feature, multi-component flow, public contract change, or incomplete test baseline. **Critical**: credentials/authz, cross-tenant access, money, destructive operations, irreversible migration, meaningful distributed-state hazards, or safety-relevant automation. Weak evidence or unfamiliar dependencies justify increasing depth, not a claim of greater certainty.

Set the max rounds and clean re-attacks from SKILL.md. Also record a wall-clock or tool-call budget suited to the user's request. Sub-agent calls consume the same global budget. The first reached limit stops expansion. A user-requested smaller budget must be honored and may yield a partial result.

## Mandatory core lens

Every run checks specification consistency, changed behavior, assumptions, evidence quality, relevant boundary cases, and the impact of a proposed fix. The local tracker's `core` task represents these obligations; do not mark it not applicable. For a tiny documentation change this can be the only lens, with inspection rather than execution as the verification method.

## Select additional lenses from observed surfaces

| Surface or change | Select | Concrete obligations |
| --- | --- | --- |
| Branches, parsing, library code, API behavior | correctness-api | Invariants, input partitions, caller compatibility, error semantics |
| User input, identities, permissions, file/network access | security-privacy | Trust-boundary violations, tenant isolation, canonicalization, sensitive data |
| DB writes, migrations, async jobs, retries, shared state | reliability-data | Partial failure, atomicity, idempotency, ordering, recovery |
| Browser/app views or interactive flows | frontend-accessibility | Racey state, error/retry UX, keyboard access, semantic controls |
| Hot paths, queues, caches, deploys, infra | performance-operations | Resource bounds, backpressure, rollback, diagnosability |
| Prompts, skills, RAG, tools, model-based decisions | ai-agents | Injection, permission boundaries, evidence quality, eval leakage, termination |
| Architecture, plans, prose claims, experiments | specifications-research | Missing requirements, counterexamples, sources, uncertainty, falsifiability |

Lenses are not mutually exclusive. A payment webhook plausibly needs correctness, security, reliability, and operations. A spelling-only edit does not need a database race audit. Record a reason for each relevant-looking lens that you omit. Add a domain-specific task when the matrix misses a real risk; these categories are routing aids, not a claim of universal coverage.

## Select verification before repair

Choose required named checks and expected outcomes before editing. Include a baseline suite, a defect-specific regression when repairing, and checks at the layer where the defect manifests. Examples: a transaction failure needs storage-boundary testing; a UI state-loss race needs controlled deferred responses; an authz issue needs two distinct principals/tenants, not just a logged-out test.

Use `execution` when runnable software behavior is in scope. Use `inspection` for genuinely non-executable artifacts or explicitly inspection-only work; do not switch to inspection simply to hide unavailable execution. If execution is required but unavailable, preserve the blocker and provide source-backed partial review.

## Depth adjustments

Broaden from a changed function to direct callers/callees, shared primitives, storage constraints, and deployment contracts when a causal path requires it. Stop broadening once the defect mechanism and impact boundary are explained. Reassess risk when a small change touches a hidden trust boundary, duplicated safety check, shared cache, or global invariant. A large diff caused by needless rewrites is not evidence of deep review.
