# Phase 3 - Second Execution, Integrity, And Check/Lint Validation

## Second-Pass Review

| Review area | Finding | Action taken | Evidence |
| --- | --- | --- | --- |
| Task alignment | Pending | Pending | Pending |
| Missing routes/actions | Pending | Pending | Pending |
| Data/state wiring | Pending | Pending | Pending |
| Error/runtime behavior | Pending | Pending | Pending |
| Associated UI consistency | Pending | Pending | Pending |
| Associated API/service/schema coverage | Pending | Pending | Pending |
| Docs and phase-boundary gaps | Pending | Pending | Pending |

## Implementation Integrity Review

| Area | Status | Evidence |
| --- | --- | --- |
| Imports and symbols | Pending | Pending |
| Route/action wiring | Pending | Pending |
| Schema/data shapes | Pending | Pending |
| State transitions | Pending | Pending |
| Extracted `AGENTS.md` development rules followed | Pending | Pending |
| Unrelated edits avoided | Pending | Pending |
| Type safety and narrow assertions | Pending | Pending |
| Tooling warnings from changed code resolved or defended | Pending | Pending |

## Console And Logging Review

Changed app/server source must not keep `console.*`. Temporary `console.*` may be used only during Phase 5 interactive testing when it directly helps debug browser/runtime behavior by reading console output. Remove those logs after the issue is understood and before Phase 5 reruns, Phase 3 re-passes, or Phase 7 signs off. If lasting logging is needed, use the repo-approved logging or telemetry path recorded from `AGENTS.md` and relevant docs.

| Area inspected | Console usage found? | Temporary Phase 5 debug only? | Removed or replaced evidence |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

## Gap Closure

| Gap | Status | Fix/defense | Evidence |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

## Production Database Safety

Production/live workspace databases, especially `.dbs/database.db`, are not scratch files. Deleting, resetting, reseeding, truncating, manipulating, or corrupting them can destroy user work and can cause the user to lose his job. The only allowed production/live DB action is the repo's required app migration command for a real schema change. If Phase 2 or Phase 3 created or changed a migration, the repo's app migration command must run against the production/live default DB before this phase passes. No other production/live DB action is allowed.

| Check | Status | Evidence |
| --- | --- | --- |
| Connected data/migration work reviewed for production/live DB safety | Pending | Pending |
| Production/live DB paths, including `.dbs/database.db` or equivalent default user-data DB, were not deleted/reset/seeded/truncated/used as fixtures | Pending | Pending |
| Production/live DB action, if any, was only the repo's required app migration command for a real schema change | Pending | Pending |
| Migration files/scripts created or changed in Phase 2 or Phase 3? If yes, app migration command ran against production/live default DB before Phase 3 pass | Pending | Pending |
| Migration command, if any, records target DB/source, reason, output, and no seed/reset/test cleanup mixed into it | Pending | Pending |
| No manual query, data manipulation, direct SQLite, seed, reset, fixture, data repair, cleanup, delete, or truncate touched production/live DB | Pending | Pending |
| Check/build validation did not depend on modifying production/live user data outside legitimate migrations | Pending | Pending |

## Ordered Static And Build Checkpoint

Run this checkpoint after the second-pass connected-place review and any Phase 3 repairs. Use the repo's native commands. If the repo has no separate command for an item, record the repo-specific reason. If a command fails, inspect enough output to identify visible issue groups, fix every locally-fixable group as a batch, then rerun that same command before moving to the next row. If a temporary full-output log is needed for large output, delete it after extracting issue groups.

| Step | Command | First result and visible issue groups | Batch fix evidence | Temp full-output log deleted? | Rerun/final result |
| --- | --- | --- | --- | --- | --- |
| Check (`pnpm run check` or repo equivalent) | Pending | Pending | Pending | Pending | Pending |
| Focused lint (`pnpm run lint` or repo equivalent, only when useful) | Pending | Pending | Pending | Pending | Pending |
| Build, when separate from check | Pending | Pending | Pending | Pending | Pending |

## Reusable Build Evidence

Record the passing build output so later phases can reuse it instead of rebuilding. Rebuild only if code, config, package/dependency files, migrations/build inputs, generated assets, stale output, or incompatible verification tooling invalidates this evidence.

| Item | Evidence |
| --- | --- |
| Passing build command and output/log path | Pending |
| Last source/config/build-input change before build | Pending |
| Later phases may reuse this build? | Pending |
| Conditions that would require rebuild | Pending |

## Downstream Coverage Handoff

Phase 3 is an inspection, integrity, and check/lint validation pass. Record coverage questions for the owning later phase instead of deciding them here.

| Item | Evidence |
| --- | --- |
| Unit-test questions or needs, if any, were recorded for Phase 4 | Pending |
| E2E questions or needs, if any, were recorded for Phase 6 | Pending |
| Any early coverage artifacts or command output were handed to the owning phase decision | Pending |

## Gate

| Metric | Required | Actual |
| --- | --- | --- |
| Score | >= 26/32 | 0/32 |
| Critical second-pass items | all pass | Pending |
| Associated UI/API/data surfaces reviewed for consistency | yes | Pending |
| Related surfaces fixed or explicitly defended | yes | Pending |
| Implementation integrity review completed and clean | yes | Pending |
| Production/live database safety evidence is recorded and clean | yes | Pending |
| Logging review completed with repo-approved logging/telemetry evidence | yes | Pending |
| Ordered check, focused lint if used, and build checkpoint passed or missing commands have repo-specific evidence | yes | Pending |
| Command failures grouped, locally-fixable groups fixed as a batch, and temporary full-output logs deleted before rerunning | yes | Pending |
| Reusable build evidence recorded | yes | Pending |
| Downstream unit/E2E coverage handoff recorded where relevant | yes | Pending |
| Critical gaps resolved, closed, or reclassified with evidence | yes | Pending |
| Remaining non-critical gaps defended | yes | Pending |
| `open-gaps.md` finalized with real rows or explicit none rows | yes | Pending |
| `progress.md` current and points to Phase 4 next action | yes | Pending |
| `progress.md` points to this Phase 3 artifact for second-pass repair details | yes | Pending |
| `progress.md` Phase Artifact Index and Artifact Pointers current | yes | Pending |
| Promotion lock verified before marker advance | yes | Pending |

Decision: Fail
