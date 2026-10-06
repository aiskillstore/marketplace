# oil-ui missing update snapshot recovery (2026-10-06)

## Incident and scope

[PR #3671](https://github.com/aiskillstore/marketplace/pull/3671) merged at `6f4b33012f276898d109099ccd1d735c06f6a39a`, head `4b85b545be916371fb7eeaa9d2d999fddc074653`. Its initial-submission report has no `previous_tree_hash` / `previous_source_ref`. An earlier [PR #3669](https://github.com/aiskillstore/marketplace/pull/3669) published the same target first. The [preflight failure](https://github.com/aiskillstore/marketplace/actions/runs/37313430404) correctly refused to overwrite it. Only one preflight failure status exists, with no publication reservation/outbox attempt. This is not a provider failure or a reason to rerun an old receiver.

Frozen inspected identities:

- Pending root: `pending/oil-oil/oil-ui`; Git tree `c4fd7bfc921031a433b55b2bf480e1ed0e20a13b`; report blob `07a9e0976ffff42eb107a9badfb7bc2894819e18`.
- Published root: `skills/oil-oil/oil-ui`; Git tree `dd69021639954aed29dad075b5113fb843fc3c02`; canonical tree SHA256 `74dfcc43cd92eb80de5c25761160452842152842998f71db5053d996e5d148f7`.
- Published upstream source: `b7004ab84654f04d9a0820dbaacd9f555bbb269a`; reviewed pending source: `48518fd02946ccbda54cd3544f8bd102413128cf`. GitHub compare confirms exactly one commit ahead, no divergence.
- Corrected report blob: `52cd9d2dabdc062fb7167e244551e440fdb1fe01`. Only the two missing meta values are added; every other JSON value and every Skill file remains unchanged.

## Recovery design

The manual, main-only `recover-oil-ui-snapshot.yml` calls an **incident-specific** script, not a generic publisher. Its App token creates one report-only correction PR on `submission/recover-oil-ui-3671-snapshot`. It does not write main, provider data, old PRs, statuses, or dispatch publication. It does not weaken any publication guard. The normal trusted submission route then independently reviews/merges/publishes the correction. Existing report-only validation verifies exact prior/merged history, unchanged content/tree hashes and both prior published snapshot fields.

Every incident SHA/tree/status/source ancestry and the original submission ID is revalidated. Any tree drift, additional original status, outbox record, existing correction branch **or all-state correction PR** stops before a business write. Git objects, branch, PR head/App author and label are read back. No mutation retry; a partial/unknown result requires inspection. Do not delete its deterministic branch to retry.

This handles the race through a new reviewed snapshot, not by inventing a missing old approval. The current submission producer already refuses a changed/colliding target at PR construction. The final publication snapshot check stays strict because a target can change between PR construction and publication.

## Callback contract

The new PR retains the original submission ID only after asserting its exact occurrence in the original PR body. The current website callback implementation at revision `26e5261465ca3ffbee3000ff117460a3a39d76c3`, `src/routes/api/submit/callback/+server.ts` (blob `eba9c16c9e3a82d6933bd8815641bf9a238189b4`) accepts the authenticated `merged` event by submission ID and sets the replacement PR number/URL, then `published` closes it. Thus a new publication correlation is deliberate; no old publication effect exists to replay. Source inspection is not proof of production callback completion: confirm the actual provider workflow's callback steps and durable publication result after execution.

## Evidence

- Red: new unit test failed with `ERR_MODULE_NOT_FOUND`; added three negative guards first and observed failure before implementation.
- Green: `CI=true node --test scripts/tests/oil-ui-snapshot-recovery.test.mjs scripts/tests/resolve-approved-submission.test.mjs scripts/tests/publication-continuation.test.mjs scripts/tests/publish-approved-batch.test.mjs scripts/tests/workflow-action-pin-policy.test.mjs scripts/tests/workflow-pr-runner-safety.test.mjs`: 98 pass, 0 fail, 0 skipped.
- Live read-only `node scripts/recover-oil-ui-snapshot.mjs`: accepted exact incident against main `82f88e7c6b002ea14bc4768f1073a56477fe570f`; no writes.
- Actual-tree integration: archived only the two incident roots from that immutable main into a disposable Git fixture; uncorrected report fails with the original snapshot mismatch. Applied `correctedReport`, committed its single report change, then used unchanged `resolveApprovedSubmission` with exact fixture base/merge commits. Result: one `report-only` update, `duplicate=false`, exact previous source ref; canonical hashes match; every other report value remains equal. Local evidence retained in `shared/workspace/reviews/marketplace/2026-10-06-oil-ui-recovery/` (not a public artifact link).

## Execution and acceptance

1. Independently review and normally merge the repair PR. No dispatch from an unmerged branch.
2. Read current main/head/CI and original incident proof. Dispatch once: `gh workflow run recover-oil-ui-snapshot.yml --repo aiskillstore/marketplace --ref main`.
3. Read exact run result and generated App PR/head. No direct main/status/provider recovery writes.
4. Process remaining eligible bot PRs oldest-first under existing rules, including the correction PR; update main branch, use only new-head CI, normal merge. The old zero-mutation preflight is superseded only after the corrected report is merged, not by rewriting its failure status.
5. Read correction publication SHA and provider/scores/cache/callback completion independently. Original PR3671 is historical/superseded, not falsely marked successful.
6. Rollback before execution: revert this isolated repair. After a correction PR exists, close it through review if necessary; do not delete evidence or replay automatically.

Current implementation status: locally verified; independent review, CI, merge, dispatch, correction PR and downstream effects still pending. Update this section with actual run/PR/commit links as they complete.
