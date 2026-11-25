# Implementation notes

## 2026-11-25 — Partial multi-PR provider recovery

- The legacy recovery path binds one PR, but the atomic publisher can move up to 25 approved PRs in a push. Recovery now proves the entire contiguous publication range, original approval trees, successful publisher attempts, batch digest and unchanged published trees.
- Only a missing Skill with no source artifact receives an initial sync. Exact active Skill/current-artifact pairs are reused without repeating provider writes; every other projection blocks. The normal authenticated source distribution gate remains mandatory for new writes.
- Full-batch provider readback precedes per-submission callbacks, scoring and cache work. A separate reconciliation verifies all results and preserves the original failed run. No production limits or suppression decisions change.
- The existing source-authority JOIN was reviewed by database-performance, business-consistency and access-isolation roles. Production bindings were empty and skills had 7,261 rows; EXPLAIN used an empty bindings scan and skills primary-key lookup. No query or index changes were needed.

## 2026-11-25 — Backlog delivery: project installs and bounded publication (issues #4325–#4327)

- `add --no-global` scopes canonical files, Pack workflow, verification readback, and lock rollback to the current project. Explicit canonical-directory options preserve existing SDK and other-command defaults. Repeating add can repair a missing selected-agent link.
- Project parent-directory and lock symlinks fail before writes. Legacy conflicting Pack links are preserved and require moving the named project path aside before reinstalling; no home data is removed or automatically migrated.
- Oversized merged submissions remain whole and unpublished. Continuation may pass them only after effect reconciliation and proof that every outbox is safe; unknown receiver effects still block oldest-first. The 64-Skill receiver limit is unchanged.
- `update`, `install`, and `plugin install` retain their existing scope; use `add --no-global` again to refresh a project install. Fork PR policy is documented in CONTRIBUTING.md.

## 2026-10-17 — Reviewed Skill distribution

- Publishing checks the site's authenticated source authority (live immutable GitHub repository ID plus upstream path) and committed distribution markers, including after rebase. Withdrawal/erasure survives source repository rename or transfer; report-supplied IDs are not trusted.
- The existing cache secret authenticates a five-minute scheduled worker. It advances at most five stages, fails visibly on incomplete processing, and never publishes applicant identity or reviewer evidence. Merge after the site endpoint and database migration are deployed.
- Reimport is blocked by tombstones; restoration requires the site's reviewed lifecycle. Git history and external installed copies remain outside current-tree deletion. No historic Git rewrite.

## Historical Notes Summary

- 2026-10-11 — Publication dependency outcomes — Blocked dependency status remains distinct from execution failure; exact recovery proof wakes continuation without replay.

- 2026-10-11 — General Actions recovery — Preserve existing publication checks and recovery boundaries; full decisions remain in Git history.

- 2026-10-11 — Submission author identity — Preserve display authors while classifying targets by owner-scoped path, canonical repository/ref and slug; do not rewrite old reports or weaken provenance.
