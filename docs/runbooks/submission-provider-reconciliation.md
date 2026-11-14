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

### Reading historical receiver logs

GitHub job logs can contain terminal formatting. The shared log reader explicitly allows those bytes through `gh api`, then removes VT control sequences with Node's native utility before reconciliation. Logs are parsed as data and never executed or printed raw. The installed older gh 2.83.0 does not recognize this flag: only its exact unsupported-flag error permits retrying the same GET without the flag, still stripping VT sequences. Other fetch failures remain failures; missing or unverified evidence never releases a reservation.

The audited receiver revision, exact workflow/job/step inventory, PR and batch correlation, terminal pre-push error, trusted status owner and outbox binding remain mandatory. Repairing transport does not prove publication or provider completion. After merging a reader repair, inspect the automatically triggered continuation first; do not blindly dispatch or rerun a receiver.

### Audited pre-push execution — 2026-11-11

[Publication run 43064391205](https://github.com/aiskillstore/marketplace/actions/runs/43064391205), attempt 1, job `130675307647`, executed revision `9898ee93fc8e1da796c7b3ea7e9c582bae316f25` (receiver blob `99e203b5bf8a47478db755e2845f2653bdbf6805`). Its sole PR input is 4163, batch `9b5e4725314fb274ecd7771bf0c3e866d6a2b60347f9a87116a7dea7ece95ff6`. The unique terminal `Main advanced; re-preflight required` precedes the sole publication push and submission callback. The failed outbox remains bound to merge `5106f5815b7cd4467967858b3c4beba60cfbaa51`; both latest reservation contexts are failures owned by this exact run.

Compared with the previously audited `70175e06306db8eab43d3f63538b9553d73b8caa`, the workflow and its Action pins, source validator, provider-recovery verifier and scope module are unchanged. The execution closure changes only add read-only pre-push reconciliation to planner/receiver and its shared log reader. Imports do not run their guarded CLI entrypoints. The scope JSON is data and keeps the November 4 cutoff. Real job steps/checkout/cleanup and exact terminal log were independently inspected; no publication push or submission callback occurred.

This does **not** mean zero external writes: outbox/status reservations were written, and source admission calls an existing POST before the push. The [source route](https://github.com/aiskillstore/skillstore/blob/700900fd0061bf1c274b2064da466665ab4ddfa7/src/routes/api/automation/skill-distribution/source/%2Bserver.ts) resolves repository identity and invokes `check_distribution_source`. Its [SQL definition](https://github.com/aiskillstore/skillstore/blob/700900fd0061bf1c274b2064da466665ab4ddfa7/supabase/migrations/20261018_add_skill_distribution_lifecycle.sql) upserts the repository-ID lookup and refreshes `checked_at`, then checks suppression. Repeating admission can refresh this metadata; it does not publish/update skills or artifacts, alter suppression decisions, invoke the submission callback, or dispatch provider sync. This is source-contract evidence, not a claim of live database inspection.

Only this separately inspected execution revision/blob pair is added. Unknown revisions, even with the same receiver blob, remain rejected. All existing creator, attempt, job inventory, PR/batch, terminal-log, outbox and concurrent-reservation checks remain mandatory. Keep original history and inspect the automatically resumed continuation before any further action; publication/provider completion still requires separate readback.

### Audited pre-push execution — 2026-11-12

[Publication run 43267925980](https://github.com/aiskillstore/marketplace/actions/runs/43267925980), attempt 1, job `131356427843`, executed revision `51965b79d69e82e99d7adf2602fca28be16788d5`, receiver blob `99e203b5bf8a47478db755e2845f2653bdbf6805`. Its sole input is PR 4192; batch `f8ffa3b564236270d38c88199af75ed3885a40de8c84821dc2efd4c8d87612ae`; outbox attempt `1794503894103-1` binds merge `5ac16e9cc82fe8d1dbb180514427dd357f70b5e6`. The sole publish job passed setup/checkout, then ended with the unique `Main advanced; re-preflight required` immediately followed by exit code 1. Main advanced to PR 4194's merge while this receiver prepared its local commit. This error is before its sole push and submission callback; original outbox/status failures remain audit history.

The complete non-truncated root trees of this execution and the already audited `9898ee93fc8e1da796c7b3ea7e9c582bae316f25` have identical `.github` (`1e984566d4e0a098bf93eb4216824afa9c7af54d`), `packages`, `schemas`, `governance`, `ops`, package manifest and lockfile objects. Complete scripts-tree comparison changes only `publication-prepush-recovery.mjs` and its test: that delta adds the preceding `9898ee` revision registration and regression cases. Receiver, source validator, provider-recovery verifier, scope data, workflow/Action pins and all executable imports are unchanged. Changed docs and submitted/published package data are not executed by the receiver. No package contents or advisory risk fields were inspected for this audit.

This is not a claim of zero external effects: the outbox/status reservations already exist and source admission can refresh repository-identity/check metadata under the source contract documented above. That contract is source evidence, not a live database audit. The terminal failure excludes this run's publication push, post-push submission callback and push-triggered provider sync; it does not hide another run's evidence. Only this exact independently reviewed revision/blob pair is registered. Other revisions (including the same receiver blob), reruns, additional job steps, wrong owners/batches/PRs and unknown push outcomes remain rejected.

After the reviewed repair reaches main, inspect the automatically triggered continuation before any dispatch. Require a fresh exact-bound native attempt that preserves the failed attempt, then separately verify the correlated publication commit, provider sync and canonical package integrity. Keep subsequent PR merges paused until this failed publication has recovered; normal merge/publication overlap caused the initial race and is optional, not a completion requirement.

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

## Provider and callback completed, separate ancillary recovery

When the original sync job fails **after** provider upload and the published callback succeeded, do not replay either effect. If original scoring and all other downstream jobs were skipped, the reconciliation workflow accepts an optional `score_recovery_run_id` alongside `recovery_run_id` pointing to the later `warm-cache.yml` run.

Both successful manual runs must belong to this repository's main branch at the exact original publication SHA. The score run must finish both `recalculate` and `score cache closure (hosted)`. Its digest-verified four-file `score-closure-<id>` artifact must bind the run/SHA, contain exactly the original changed slug set, zero failed slugs/errors and real, in-run score snapshots. The warm run must consume the original provider artifact and invalidate/verify the exact scope after both score jobs completed. Completion times come from jobs for the exact run attempt; workflow-run REST objects do not supply `completed_at`.

All original trusted submission, immutable tree/blob, original provider/callback success, current provider projection/artifact and published receiver GET checks still apply. Missing evidence rejects closure. This option cannot be mixed with audit or bounded callback-finalization modes; neither scoring nor warming is dispatched by reconciliation.

For the November 13 interruption, the evidence IDs are original sync `43448267048`, scoring `43543076341` and warm recovery `43543619658`. After independent review and normal merge of this repair, inspect current reconciliation state before dispatching once with those IDs:

```sh
gh workflow run reconcile-submission-sync.yml --repo aiskillstore/marketplace --ref main \
  -f failed_run_id=43448267048 -f recovery_run_id=43543619658 \
  -f score_recovery_run_id=43543076341
```

The historical failure remains failed. Only a successful new verifier followed by its separate reconciliation status releases continuation. Local tests and GitHub evidence verification do not claim the production provider GET or reconciliation has run.

## Post-push merged-callback failure (provider never started)

`publish-approved-batch.mjs` can push the canonical publication successfully and
then lose the merged callback connection. Do not repeat the batch or overwrite
its failed statuses. The push sync will correctly fail its publication gate.

Use the existing reconciliation workflow's **opt-in** `publication_run_id`, with
`failed_run_id` identifying that exact push sync. Do not combine this mode with
provider, score, bounded or audit recovery inputs. This mode:

1. Accepts only a first-attempt failed, latest main push and its exact failed
   single-submission batch publisher/reservation. The original provider and
   published callback must both be skipped.
2. Verifies the exact trusted merged PR/trailer, complete pending-to-skills move,
   unchanged approved/current full package trees and preceding successful push.
3. GETs the exact receiver. Only `in_review` with no approval/publication may send
   the **missing merged callback**. `approved` already owned by the original
   publisher is verified without sending it again; ambiguous states fail closed.
   A network failure stops: inspect receiver state before any further attempt.
4. GETs the committed callback and records a **new**
   `agentcrew/publication-reconciliation/<failed-push-id>` on the publication SHA.
   No push, provider, scoring or cache operation runs in this mode. Original
   publisher/push failures and publication/attempt statuses remain unchanged.

This is not full provider completion and does not release the queue. Afterwards,
use `sync-to-supabase.yml`'s existing `resume_failed_run` input for the same push.
Its normal exact-root/tree admission now accepts the separate trusted publication
proof only when the original provider was skipped. The verified plan emits an
explicit provider mode: `initial-sync` runs the first provider sync **without**
`--resume-current`; ordinary failed-provider recovery retains `resume-current`;
`ancillary-only` never invokes provider sync. Missing or contradictory modes fail
before CLI execution.

Initial sync is deliberately limited to a new, never-installed package: fresh
receiver GET must still be approved by the original publisher, with no published
state; fresh provider GETs must show **no skill row and no artifact for the exact
canonical path**. Existing/partial artifacts, even from an earlier dispatch, stop
this mode for investigation rather than overwrite or repeat them. This is not an
initial-sync route for an existing installed skill update.

A failed recovery dispatch is not the original push and cannot replace its ID.
Before a new dispatch, inspect all prior recovery steps and provider state; a
sync error alone proves no such thing. In particular the security-event drain
may run after sync failure. Preserve its effects and all failed run history;
never rerun a run that may already have written the provider. Verify the full
recovery, then run normal provider reconciliation with its exact recovery run. The separate full
provider proof remains mandatory for continuation and future sync baselines.
