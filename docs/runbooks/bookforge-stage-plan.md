# Bookforge ancillary stage proposal (offline only)

## Scope and status

This is the development slice for recovery Task #6309. It does **not** implement or authorize production recovery. The accepted artifact/current/observation diagnostic remains separate and unchanged.

Fixed incident: `gongnyang-bookforge`, root `skills/gongnyang/bookforge`, publication `549325ce6f288514ab5da9bf11af95814f848048`, submission `df71079f-cd85-4980-8be5-6a3921396e83`.

```sh
node scripts/bookforge-stage-plan.mjs --plan
CI=true node --test scripts/tests/bookforge-stage-plan.test.mjs
```

The only CLI command is `--plan`. Extra arguments, effects and receipt input are rejected with a generic message; no input or parser detail is echoed. No connector, environment credential access, subprocess, network, write, stage executor or receipt verifier is added. The module reuses the existing diagnostic's `assessSnapshot` validation; importing that library does not invoke its snapshot-file CLI.

All stages remain `UNKNOWN`, and `authorizesExecution`, `readScopeApproved`, `executorImplemented`, `replayAllowed` and `continuationAllowed` are false. This proposal is **not an expansion of the previously approved three-table GET**. All proposed ancillary reads require separate scoped authority and an approved connector; no queries are executed here.

## Entry points and identity

- `stageReadPlan()` returns a fresh proposal; it accepts no arguments.
- `bindExpectedCurrent(snapshot)` accepts only the existing diagnostic's complete exact incident snapshot: one skill, one publication artifact, one current artifact and one observation with exact root/SHA/content/tree/source identity, matching pointers and positive revision. It rejects extra fields, missing/duplicate rows and divergent identity with `Invalid stage plan input`.
- `compareExpectedCurrent(expectedCurrent, snapshot)` validates both inputs, compares the full fixed identity plus skill/artifact UUID and revision, and reports **offline equality only**. A newer internally consistent pointer/revision/skill fails comparison. It never performs atomic CAS, authenticates database evidence, accepts a claimed receipt, or grants write/replay authority.

The JS identity API captures all own keys and data descriptors once, rejecting accessors and extra fields (including hidden/non-enumerable and Symbol keys). It creates an owned snapshot using the diagnostic read plan's exact row fields, including bounded dense arrays; assessment and binding use that same copy. Expected-current comparison likewise uses its own validated identity copy, never rereading caller properties after validation. This does not authenticate arbitrary proxy behavior or its provenance: only the captured data is assessed, and caller `get` accessors are never invoked.

Inputs are untrusted. JSON cannot authenticate its own source. Callers must retain independently verifiable read receipts, query scope, observation time and completeness outside the JSON. Even matching snapshots leave production state UNKNOWN.

## Proposed reads and cardinality

Each query uses GET, schema `skillstore`, explicit metadata columns, object-bound filters and `limit=2`. `$expectedCurrent`, `$verifiedAudit` and `$verifiedProjectionJob` are unresolved dependencies, **not executable parameters**. No placeholder may be used until its provenance, exact linkage and freshness have been verified.

|Query|Object and linkage|Cardinality / limitation|
|---|---|---|
|catalog|`skills`: fixed slug and expected skill id|Zero-or-one; identities/timestamps do not prove projected payload|
|aiContent|`skill_ai_content`: expected skill id|Zero-or-one; content hash/version are not independent payload digest proof|
|audit|`skill_security_audit`: expected skill id; version/created_at/id descending|Latest candidate, not whole history; do not select an older matching audit to bypass a newer divergent one|
|projectionJob|`security_change_projection_jobs`: expected skill id, source_type=audit, verified audit id|Zero-or-one; source/version and projected event/time must agree|
|projectionEvent|`security_change_events`: expected skill id, verified job event id, audit source id/type|Zero-or-one; `idempotency_key` must agree with independently verified immutable source|
|eligibility|`skills`: expected id and fixed slug|Zero-or-one; audit pointer linkage does not itself prove safety|
|attestation|`security_audit_attestations`: verified audit id; issued_at/id descending|Bounded candidates only; multiple key attestations are possible, no complete-history or signature-validation claim|
|submission|`submissions`: fixed submission id|Zero-or-one; status alone does not prove all callback effects|
|notification|`submission_github_notifications`: fixed submission id and event=published|Zero-or-one; ledger claim/comment URL is not delivery proof|
|score|`skills`: expected id and fixed slug|Zero-or-one; score/timestamp alone does not prove correct input snapshot|

For singleton lookups, zero leaves the stage unresolved and two indicates ambiguity. For audit history, two historical audits are not duplicate identities: select the highest version/created_at/id and verify it, without claiming full history. Attestation results are only bounded candidates. No read automatically triggers a write, and no metadata-only result is consumed to mark a stage complete. Cache evidence needs separately approved service/build readbacks for both this slug and containing pack derivatives; no fabricated database cache query is supplied.

Schema names were cross-checked against the local skillstore source at HEAD `6bd2bee6957fe1f4e09e0801538e437fca056f4d`, not a deployed schema claim:

- `001_create_skillstore_schema.sql` / `036_add_ai_content_hash.sql`: AI content metadata.
- `014_add_marketplace_sync_fields.sql`: catalog publication timestamp.
- `20260726_add_security_audit_attestations.sql`: `subject_*`, audit payload hash, attestation metadata (no payload/signature selection).
- `20260729_harden_security_change_projection_outbox.sql`: job/source/event/time linkage.
- `20260727_add_security_risk_watch.sql`: event `idempotency_key`, not an invented `event_key` column.
- `20260711_add_skill_public_eligibility.sql` and `20260713_add_quality_evidence_snapshots.sql`: eligibility/score pointers.
- `20260707_submission_submitter_publish_notifications.sql` and `20260708_submission_github_notification_threads.sql`: submission/notification metadata, no submitter/user id.

The tests assert proposal contracts; they are not a live DB integration test.

## Future execution and receipt requirements (not implemented)

A future separately authorized executor must perform exact expected-current comparison **in the same transaction** as each database mutation. Lock and compare skill id, slug/root, artifact id/revision, publication SHA, content/tree hashes and source ref; preserve immutable snapshots and existing timestamp semantics. Already-complete projections are no-op; changed identity fails closed. A DB CAS does not make external callback effects idempotent.

Stages: catalog → AI content → audit → durable event → eligibility/attestation → callback → score → cache. The plan contains per-stage proof requirements. In particular:

- Catalog/AI content require canonical input and projected content digests, not row-existence claims.
- Missing audit cannot be repaired by draining jobs; 24-hour audit dedup is not indefinite replay protection.
- Global job drain success is not this slug's event proof.
- Callback requires independent reconciliation of status, comment delivery, favorites and skill events; its header/notification claim is not end-to-end idempotency.
- Score requires exact input and snapshot evidence; cache requires build/key/version and second HIT/SKIPPED evidence, including packs. Partial sync may already have invalidated caches.

A future receipt verifier must independently resolve durable `beforeReadRef`, `effectRef`, `afterReadRef` with stage, scope, expected-current identity, input digest, observation time and outcome. This module cannot ingest or authenticate receipts. UNKNOWN effects prohibit replay until exact authoritative reconciliation.

Existing publication reconciliation still requires same-publication-SHA successful full manual sync. No staged receipt acceptance, successful manual artifact, provider status backfill or continuation unlock is produced. Implementing a verifier/executor, production stage/RPC/callback/sync/catalog/status writes, workflow dispatch, merge/deploy/release/continuation, S2/S3 expansion and external notifications are out of scope.

## Development verification log

2026-10-10: old import failure reconciled separately; it remains a failed test. Fresh TDD reproduced missing module under enforced `read_only_offline`. Implemented proposal/identity functions and ordinary Validate Marketplace source path/test wiring; stage test 13/13 passed under `CI=true` and `read_only_offline`.

Independent read-only advisory review identified generic accessor error leakage and ambiguous blanket history-cardinality wording. Added failing regressions, corrected both, and reran 13/13 green. Advisory review is not Ada acceptance.

Earlier broader diagnostic/workflow attempts failed in enforced no-write mode: existing suites use `mkdtemp`; workflow suites also lacked installed `yaml`/`gray-matter`. Those historical failures remain failures, not hidden or skipped.

2026-10-10 03:50 Asia/Shanghai: the ordinary governed executor is available again. Installed the existing lockfile with `npm ci --ignore-scripts` (no dependency changes). With `CI=true`, normal temp-enabled tests passed:

- `node --test scripts/tests/bookforge-stage-plan.test.mjs scripts/tests/bookforge-readonly-diagnostic.test.mjs scripts/tests/submission-scope-workflows.test.mjs scripts/tests/validate-marketplace-autofix.test.mjs`: 72/72, zero skips.
- `node --test scripts/tests/workflow-action-pin-policy.test.mjs scripts/tests/workflow-runner-safety.test.mjs`: 30/30, zero skips.
- `node scripts/check-workflow-action-pins.mjs` and `node scripts/check-workflow-runner-safety.mjs`: PASS (43 workflows).

The lockfile installation reports four dependency advisories (two moderate, two high); dependencies were not changed or auto-fixed in this scoped slice. This is not a dependency-security clearance. Normal PR CI and Ada independent review remain required. Production state remains UNKNOWN. No merge, deployment, sync replay or production change was performed.

2026-10-10: Ada independent review rejected head `6b4b40d66a24bbf83d5d7e36f1f3f6b2d1ee482c` for two P2 offline identity findings ([review](https://github.com/aiskillstore/marketplace/pull/3717#issuecomment-6088952490)): post-assessment pointer substitution and incomplete own-field rejection. Added seven failing regression cases first: enforced offline stage suite 13 PASS / 7 FAIL, zero skips. Fixed both using descriptor-only owned snapshots and identities; added two further stable-copy/proxy regressions. No diagnostic/S1 implementation changes.

- Stage + diagnostic run in no-write mode: 28 PASS / 1 FAIL solely because diagnostic CLI fixture requires `mkdtemp`; retained as a failed invocation. Repeated in ordinary governed temp-enabled mode: 29/29 PASS. No test was skipped or weakened.
- Final six affected suites with `CI=true`: `node --test scripts/tests/bookforge-stage-plan.test.mjs scripts/tests/bookforge-readonly-diagnostic.test.mjs scripts/tests/submission-scope-workflows.test.mjs scripts/tests/validate-marketplace-autofix.test.mjs scripts/tests/workflow-action-pin-policy.test.mjs scripts/tests/workflow-runner-safety.test.mjs`: 111/111 PASS, zero skips (stage 22 cases).
- Both policy CLIs and `git diff --check`: PASS (43 workflows).
- New exact head and normal PR CI must be read back after push. Ada independent re-review remains required; no production queries/writes, merge/deploy/release, continuation, notification or S2/S3 work is included.
