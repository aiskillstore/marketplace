# Bookforge publication: offline readback preparation

## Exact incident and limits

- Failure: [sync run 37490264751](https://github.com/aiskillstore/marketplace/actions/runs/37490264751), attempt 1, `skills catalog projection` socket connection closed.
- Owner: [PR #3694](https://github.com/aiskillstore/marketplace/pull/3694).
- Publication SHA: `549325ce6f288514ab5da9bf11af95814f848048`.
- Publication trailer: `submission-pr-3694-4d887ff8a92c5371dcbf23025618dffb7b713e86-be66e58ebb569f8d1b258eeb109756926a20b2e9`.
- Only slug/root: `gongnyang-bookforge` / `skills/gongnyang/bookforge`.
- Expected content/tree/source hashes are pinned in `scripts/bookforge-readonly-diagnostic.mjs` from this publication's report meta, not from mutable main or report risk fields.

This PR delivers **offline code and a read plan only**. It does not configure a connector, bind a credential, query production, authenticate arbitrary JSON, install a migration, or perform recovery. There is no network client, environment credential lookup, subprocess, workflow dispatch, provider mutation, callback, score/cache action, status backfill or production-triggered job. Existing workflow changes only run the offline tests and add their source-path trigger.

The actual artifact/current projection/provider outcome remains **UNKNOWN** until an operator/runtime-approved read capability supplies authoritative evidence. `0 synced` and a failed run are not zero-write proof. Current CLI source has an artifact RPC before the ancillary catalog update; that source ordering is a reason to inspect possible partial effects, not proof of the old run's committed state.

## Commands (no production access)

```sh
node scripts/bookforge-readonly-diagnostic.mjs --plan
node scripts/bookforge-readonly-diagnostic.mjs --snapshot /path/to/scoped-export.json
CI=true node --test scripts/tests/bookforge-readonly-diagnostic.test.mjs
```

The snapshot file must be regular, non-symlink, valid UTF-8 JSON and <=64 KiB. Other CLI flags, malformed input, unknown fields and out-of-scope identities fail with a constant error that never echoes the payload, path, parser error or credentials. Outputs contain only fixed incident identifiers, classifications and bounded counts. No input data is changed.

## Proposed production read boundary — not yet authorized or bound

Use a **runtime-governed read-only connector/export**, not a raw credential in a command or the old sync runner. No such connector is selected by this code. The operator must first name an available connector and enforce its exact scope; do not infer capability from the plan.

Allow only SELECT/GET in schema `skillstore`, no RPC or write grants, no arbitrary SQL/table/URL supplied by the model:

1. `skills`, `slug = gongnyang-bookforge`, limit 2, explicit fields `id,slug,plugin_path,marketplace_commit_sha,content_hash,tree_hash,current_artifact_version_id,artifact_revision`.
2. Require one valid skill row. Bind its ID, never an independent caller-supplied ID.
3. `skill_artifact_versions` for that skill ID, the fixed publication SHA and fixed root, limit 2, fields `id,skill_id,source_path,marketplace_commit_sha,content_hash,tree_hash,artifact_revision,snapshot_status`.
4. Same table for that skill ID + its current artifact pointer + fixed root, limit 2, same fields. A null pointer means no current-artifact query, not an unfiltered query.
5. `skill_artifact_observations` for that skill ID, fixed publication SHA/root, limit 2, fields `skill_id,artifact_version_id,marketplace_commit_sha,source_path,upstream_commit_sha`. These are the related immutable processing records in this slice. Do not pull audit bodies, risk findings or generic security-event records for the slug.

The connector must stop on ambiguous first-stage identity, truncation, redirection, schema mismatch or missing permissions. Retain query identity, retrieval time, completeness and authentic runtime/operator receipt **outside** the snapshot JSON. Query scope and field allowlists above must be enforced by the access boundary, not merely trusted because this Markdown lists them. Never substitute a broad service-role key or expand to other slugs as fallback.

## Snapshot contract and interpretation

Envelope keys are exactly `schemaVersion` (1), `slug`, `publicationSha`, `skills`, `publicationArtifacts`, `currentArtifacts`, `observations`. Arrays contain at most two rows and each row contains only its planned fields. UUID/revision/hash types and cross-table skill linkage are checked.

The assessor distinguishes missing/ambiguous, incomplete, partial/historical/divergent, and internally exact-current snapshots. An exact result requires matching publication/content/tree identity, current artifact pointer and revision, exact snapshot status, and a matching immutable observation/source commit.

**Every result remains `productionState: UNKNOWN`, `inputTrust: unverified-offline-snapshot`, `replayAllowed: false`.** A supplied JSON document cannot authenticate itself; even a genuine exact artifact snapshot does not prove ancillary catalog metadata, audit projection, callbacks, scores or caches completed. No classification calls recovery or marks a failed workflow successful. A later operator/runtime review must combine these results with independently verified read receipts and the failed run's stage evidence. Missing artifact rows can also reflect a reused historical artifact recorded by an observation; do not infer zero writes from absence.

## Already-observed GitHub processing evidence

Read on 2026-10-09: the original provider step failed; `Reconcile durable security change events` and `Record durable publication provider result` completed, while scoring/cache stages were skipped. A successful *record-result step* is not successful provider sync. Subsequent publication continuation failed at the previous-push gate, including [run 37891261258](https://github.com/aiskillstore/marketplace/actions/runs/37891261258).

Existing `reconcile-submission-sync.yml` is not this diagnostic: it requires a successful exact-SHA recovery and writes a separate GitHub status after verification. Existing rerun guard rejects rerunning a previously executed provider step. This PR does not loosen either gate, create a replacement status or add an automatic retry.

## Tests and next owner

Offline cases cover: fixed GET/three-table plan; no implied authority; consistent data; empty/duplicate arrays; wrong incident/linkage/source/path/hash/pointer/revision; null current pointer; malformed/extra/oversized/secret-bearing input; symlink input; constant error/no raw data echo; structural absence of network/process/write dependencies; and CI source-path coverage. Expected-red import/test-path checks were run before implementation/integration; targeted suite is 9/9 PASS with zero skips.

Cody retains follow-up #6285. Ada independently reviews this precise code/plan; operator/runtime separately authorizes and binds production read access. After authoritative readback, design only the missing, idempotent recovery stage with separate review/authorization. Do not resume a publication batch that would also publish agy-worker's superseded pending v0.24.0; its replacement work is tracked separately in [Issue #3703](https://github.com/aiskillstore/marketplace/issues/3703).

Source schema evidence: `aiskillstore/skillstore` revision `d4ac9fc88c34bc4364fc3a88f571d846acad3274`, artifact version/observation migrations and current sync implementation; existing Marketplace `reconcile-submission-sync.mjs` safe projection fields. These are code evidence, not proof that production currently has that schema or state.
