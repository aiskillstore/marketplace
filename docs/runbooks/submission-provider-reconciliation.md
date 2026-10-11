# Submission provider reconciliation (no replay)

## Purpose and boundaries

Close one inspected failed submission publication push **without executing another provider write**. The existing source-monitor recovery route is unchanged. Original failed Actions runs and `agentcrew/publication/*` history remain intact; the new workflow records `agentcrew/provider-reconciliation/<failed-run-id>` on the publication SHA. All consumers use `recoveredPushSync`, including publication continuation, batch receiver admission, source-monitor admission, and the sync baseline CLI.

This is not a generic green-run bypass. It requires:

- Same-repository main sync workflow, failed completed push and a later successful manual recovery at the **same publication SHA**, exact attempts and complete job evidence.
- Original authoritative publication-completion step succeeded and provider step failed; successful recovery includes provider, artifact upload, event reconciliation, published-submission callback, scores and cache aggregation.
- Exactly one submission publication trailer and linear commit parent equal to the trusted bot PR merge commit; <=25 canonical roots, a complete <300-file baseline comparison containing only added/modified canonical files, and exact published/pending tree entries at their immutable SHAs.
- Exact SHA-256-verified `synced-slugs` artifact (<=64 KiB ZIP, single regular `synced-slugs.txt`, <=8 KiB unpacked), whose unique slug set equals the entire changed root set.
- Read-only provider GETs in schema `skillstore`, exactly one skill and its **current** artifact, matching path, marketplace SHA, content/tree hashes, artifact revision and `snapshot_status=exact`.
- A successful dedicated reconciliation run on main with both required verification/record steps. A bare status, unrelated manual success, fork run, skipped verifier or stale/missing provider projection never releases the guard.

Intentionally unsupported: cancelled original push, multiple publication trailers/batch publication, incomplete/truncated evidence, failed push outside newest-100 bounded inventory, later provider versions or archived/no-op projections. These stop for inspection rather than guess coverage. Publication-wait failures remain rejected (this verifier requires that step succeeded). No new package dependencies; ZIP verification uses Python stdlib on `ubuntu-latest`.

## Governed operation

### Reading continuation outcomes

`Continue merged Skill publications` is a queue planner. Its `outcome` job output and run summary distinguish:

- `idle`: no pending skills.
- `waiting`: a provider sync, publication receiver or fresh dispatch is still active; no new batch was dispatched.
- `blocked`: a completed dependency needs verified reconciliation, a receiver has unresolved durable evidence, or no pending approval can safely proceed. The summary links the original failed provider run or identifies the affected PRs. A successful planner run does not mean publication succeeded.
- `ready`: a read-only invocation found a batch; it did not dispatch it.
- `dispatched`: the batch receiver was invoked; its publication, provider sync, callbacks, scores and cache still need separate acceptance.

Repeated checks of the same failed dependency do not throw another execution error or replay a write. Recovery remains explicit and scoped; only the existing verified reconciliation proof releases the guard. Completion of the reconciliation workflow wakes the planner immediately, with the schedule retained as a fallback. A failed verification does not release it.

API errors, invalid/truncated evidence, publication holds and provider runs stalled beyond the existing time limit still fail visibly. Do not use `continue-on-error`, rerun the failed provider blindly, or clear its history to release the queue.

### Reconciliation procedure

1. Get implementation independently reviewed; merge only the approved exact repair head through the normal repository/human gate. The workflow runs only from main and pins runtime checkout to `github.sha`.
2. Inspect both exact run IDs and confirm provider recovery already completed. Do not rerun either sync workflow, and do not change the old publication status.
3. Obtain the runtime's exact dispatch approval, then dispatch:

   `gh workflow run reconcile-submission-sync.yml --repo aiskillstore/marketplace --ref main -f failed_run_id=36738667705 -f recovery_run_id=36801132971`

4. Read the new run, current attempt's two steps, and separate status on `421067cfa94823ceb4f1ab2c95ce369dddc36528`. Require completed/success plus the exact target run link. Do not equate dispatch acceptance with completion. Failed verification writes no closure status; no automatic retry.
5. Read continuation/receiver runs for PR 3620, publication commit and provider result separately. Scheduled continuation may proceed once proof is accepted. Resume PR 3621 only under existing serial bot-PR eligibility/head-CI/ruleset/merge rules and runtime gates. Final provider acceptance remains independent.

Only a GitHub status is written by this workflow. Provider requests are GET only, redirects rejected, 15-second deadline, two-row limit and 16 KiB response bound. Credentials stay in workflow secret handles; none enter inputs, output, report or source control.

## Incident evidence: 2026-10-01

- Original submission [PR 3619](https://github.com/aiskillstore/marketplace/pull/3619): head `5b78483cc8d80faf17e70dabb83bde9d4ef7a419`, merge `1b57c16bda833bb3adf34589120053709c21e437`, publication `421067cfa94823ceb4f1ab2c95ce369dddc36528`.
- Failed [push sync 36738667705](https://github.com/aiskillstore/marketplace/actions/runs/36738667705); initial bounded manual recovery also failed before provider writes. Source connectivity then restored by CEO.
- Successful [manual recovery 36801132971](https://github.com/aiskillstore/marketplace/actions/runs/36801132971), exact publication SHA, exact slug `apidojo-io-tiktok-scraper`; provider, event reconciliation, callback, scores and cache success. No additional provider sync needed.
- Live read-only SQL confirmed projection and current artifact both match pinned content/tree hashes and SHA, revision 1, snapshot `exact`. Provider REST verification by new workflow is still **UNKNOWN until approved dispatch**; SQL is not a claim that the new receiver ran.
- [PR 3620](https://github.com/aiskillstore/marketplace/pull/3620) independently read as MERGED at `978dc44dd951396dfc66814c66aa5eb70b2c97a8`; this Cody repair did not perform that merge. Publication continuation remains blocked on old push proof until repair approval and reconciliation.
- [PR 3621](https://github.com/aiskillstore/marketplace/pull/3621) OPEN at `e793afb2c165165417ec0cd2252a4dffdd0c9eb7`; new-head CI/update/merge/publication not performed by this repair.

## Implementation evidence and rollback

- Red: `CI=true node --test scripts/tests/submission-sync-reconciliation.test.mjs` failed before the new module existed.
- Green: affected unit, archive-boundary, shared-guard, monitor, continuation, batch receiver, baseline-shell and action-pin tests. Re-run command in PR description.
- Live GitHub smoke: verifier accepted original runs, baseline comparison, pinned published/pending entries and SHA-256 archive with a captured SQL projection fixture. This smoke does **not** claim live REST receiver execution.
- No production configuration, provider or history mutations made by implementation. Rollback the repair source through normal reviewed revert if needed; do not rewrite an emitted reconciliation status without independent inspection. The original failed status remains available for audit.

## Execution and API contract correction — 2026-10-01

- Repair merged at `1784402905118ff83e695c3f976844682663ce83`.
- [Reconciliation 36810614321](https://github.com/aiskillstore/marketplace/actions/runs/36810614321) succeeded with real provider REST verification; separate status on `421067cfa94823ceb4f1ab2c95ce369dddc36528` is success. Do **not** rerun it or the original provider sync.
- [Continuation 36810677911](https://github.com/aiskillstore/marketplace/actions/runs/36810677911) failed before publication dispatch: combined-status API omits `creator`, unlike the status-list API. The original mocks incorrectly supplied this field.
- Follow-up changes only the submission proof consumer to the status-list endpoint. GitHub returns newest first; the first exact context wins even when failed/pending/untrusted. Bounded pagination stops after 10 pages and rejects malformed/incomplete evidence. Existing actor, workflow, exact run and step checks remain intact. Source-monitor logic is unchanged.
- Red regression uses creator-free combined response; it fails with the original consumer. Green affected suite: 52 pass, 0 fail, 0 skipped, including a newer failure/pending/error or wrong creator ahead of old success, paging and bounds, and baseline shell integration.
- Live read-only `node scripts/recovered-push-sync.mjs 36738667705` with the corrected consumer returns `Push sync 36738667705 reconciled by verified recovery 36810614321`. This reads existing GitHub proof only, no provider or GitHub writes.
- After independent exact-head review and approved merge, resume **continuation only**. Main push itself may trigger continuation and publication. Read current runs before any dispatch to avoid duplicate effects. PR3620/3621 publication/provider acceptance remains pending until source-of-truth readback.
