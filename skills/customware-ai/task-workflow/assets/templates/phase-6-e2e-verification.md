# Phase 6 - E2E Coverage Decision And Verification

## E2E Coverage Decision Matrix

Use this order for each changed workflow: decide whether E2E is warranted; inspect connected existing E2E; remove unnecessary existing E2E; update connected existing E2E when it can carry the warranted workflow; add a new minimal E2E only when no existing E2E can carry a warranted core/complex workflow; otherwise record `N/A`.

> Strict default: no new E2E. A smoke checklist or reviewer expectation is not enough; the artifact must prove durable E2E risk and existing-first failure.

| Behavior/path | E2E warranted? | Critical/core workflow risk | Existing E2E inspected | Remove/simplify existing? | Update existing? | Add new? | Decision and minimal/core reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## Minimal Coverage Rationale

Small fixes, visual-only changes, copy/color/style changes, spacing/layout tuning, simple button wiring, isolated logic, and incidental UI behavior normally require no new or updated E2E. E2E is warranted only for critical user workflows, complex multi-step flows, persistence/navigation boundaries, permission boundaries, or high-risk regressions. Unit-level coverage decisions belong to Phase 4, not Phase 6.

| Change type/risk | Why E2E is or is not warranted | Phase 4 unit decision cited if relevant | Evidence |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

## Existing E2E Review

Inspect connected existing E2E tests for every changed workflow before choosing an action. Remove unnecessary E2E first, then update an existing flow when the task changes or extends that flow. Add a new E2E test only for a core workflow or when existing coverage cannot cleanly express the warranted path. Existing tests created by older agents are not grandfathered; passing status alone is not a reason to preserve them.

| Existing test file/flow | Connected workflow | Old/excess/agent-created? | Action: remove/simplify/update/preserve/unrelated | Reason | Evidence that file was read |
| --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending |

## Old Or Excess E2E Pruning Audit

Use this section for connected E2E tests that may be unnecessary, obsolete, duplicated, brittle, convoluted, or non-core/non-complex. If none are found, record the search/read evidence and `None found`.

| Candidate E2E | Why it might be unnecessary or excessive | Decision: remove/simplify/update/preserve | Critical-flow coverage after decision | Diff/readback evidence |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

## New E2E Burden Ledger

Complete one row for every new E2E file or case. If no new E2E is added, record `N/A` with the existing-E2E/update/remove evidence that made new coverage unnecessary.

| New E2E file/case | Critical/core workflow protected | Existing E2E read first | Why existing update/remove/`N/A` was insufficient | Minimal user path only? | Cheaper proof rejected | Bulk check: merged/reduced? |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## E2E Test Changes

Record every E2E add, update, removal, or explicit skip. Removed tests need a reason, readback/diff evidence, and a note about any remaining critical-flow coverage.

| Test file | Action: added/updated/removed/skipped | Existing-first outcome | Burden-ledger row or `N/A` | Why this action is warranted and minimal | Diff/readback or command evidence | Critical-flow coverage after change |
| --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## Functional Assertion Quality

E2E tests should prove actual core task functionality, not superficial styling or existence. Prefer assertions for user-visible outcomes, persisted state, navigation results, validation behavior, permissions, or end-to-end data flow. Avoid primary assertions about color, CSS class, incidental copy, or a button merely existing unless the task itself is specifically about that behavior and is critical enough for E2E.

| Test file | Functional outcome proved | User-visible/persisted assertion | Superficial checks avoided? |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

## Test Runs

Record the exact bounded E2E command and its exact output when an E2E command is warranted. If output is long, write it to a repo-local log file and cite that file here, plus the final pass/fail lines copied exactly into the artifact. If no E2E is warranted, record `N/A` and the coverage-decision evidence.

| Command | Timeout | Lifecycle helper/repo `webServer`/setup evidence | Result | Exact output or repo-local log path with final lines | Follow-up |
| --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending |

## Phase 3 Build Reuse

Reuse the Phase 3 passing build unless code, config, package/dependency files, migrations/build inputs, generated assets, stale output, or incompatible verification tooling invalidated it after Phase 3. Do not rebuild only because Phase 6 is starting, E2E needs a production bundle, or final confidence would feel safer.

| Item | Evidence |
| --- | --- |
| Phase 3 build evidence reviewed | Pending |
| Reused Phase 3 build or rebuild reason | Pending |
| If rebuilt, command/log and invalidating change | Pending |

## Test Selection And Retry Ledger

Record every meaningful E2E command, including reruns. Use the smallest useful scope first. List the connected specs covered. Never run the unfiltered full E2E suite unless the task explicitly asks for full E2E or a concrete written repo instruction names full E2E/all-spec execution for this exact task. A repo having one large E2E file, a Playwright `webServer`, or generic "run tests" guidance is not enough. If no E2E is warranted, record `N/A` and do not run an E2E command.

| Command | Scope: targeted/connected-multi-spec/explicit-full | Why this scope and connected specs covered; exact full-suite requirement if explicit-full | Previous related failure | Changed or new evidence before rerun | Timeout/quiet-run triage before longer rerun | Outcome | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending |

## Server And Command Discipline

| Check | Status | Evidence |
| --- | --- | --- |
| Correct lifecycle owner recorded before command: helper by default; repo `webServer` or manual fallback only with reason/diagnostics made before the command | Pending | Pending |
| First E2E command established lifecycle ownership before testing, with no reliance on an assumed existing server | Pending | Pending |
| Existing repo E2E command was run through helper `--run`, or repo `webServer` ownership exception was recorded before native Playwright | Pending | Pending |
| Test server, if needed, started by the helper with PID/log, or by a justified repo `webServer`/fallback owner | Pending | Pending |
| Server readiness, if needed, checked by the recorded lifecycle owner before E2E execution | Pending | Pending |
| Browser preflight passed, or mismatch failed early without `playwright install` | Pending | Pending |
| Tests run as bounded commands, not watchers | Pending | Pending |
| Runtime logs preserved under `task-workflow/runtime/` | Pending | Pending |
| Pre-server setup, if needed, ran through lifecycle `--setup` or justified repo/fallback setup | Pending | Pending |
| Repo E2E/end-to-end config owned test DB paths for helper/setup/server/run commands | Pending | Pending |
| E2E/end-to-end fixture setup, reset, migration, SQLite access, or custom scripts used repo-owned test DB paths | Pending | Pending |
| DB/setup/server lifecycle reused across related E2E commands unless code, test, config, fixture, migration, build input, or lifecycle diagnostics invalidated it | Pending | Pending |
| Fetch/stale DB/stale build/wrong-port issues were diagnosed through lifecycle logs/readiness before any fallback | Pending | Pending |
| First-run targeted E2E used timeout at or below `30000` ms, or task-specific reason for a different first timeout is recorded | Pending | Pending |
| Longer timeout, if used, followed timer-only/no-useful-output failure plus helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage | Pending | Pending |
| Useful failure evidence was diagnosed directly instead of retried with a larger timeout | Pending | Pending |
| Manual fallback, if used, captured PID/log/readiness/cleanup evidence under `task-workflow/runtime/`; otherwise N/A | Pending | Pending |
| Background server cleaned up after tests | Pending | Pending |
| Cleanup method recorded and bounded | Pending | Pending |

## Production Database Safety

Production/live workspace databases, especially `.dbs/database.db`, are not scratch files. Deleting, resetting, reseeding, truncating, manipulating, or corrupting them can destroy user work and can cause the user to lose his job. Phase 6 may use only isolated test/E2E state proved by repo-owned config. The production/live DB may not be touched for E2E setup, fixture setup, seed, reset, debug, cleanup, manual queries, direct SQLite, data repair, or any data manipulation.

| Check | Status | Evidence |
| --- | --- | --- |
| Every setup/server/run command that mentions DB/data state was reviewed before running | Pending | Pending |
| Production/live DB paths, including `.dbs/database.db` or equivalent default user-data DB, were not deleted/reset/seeded/truncated/migrated/opened with write risk | Pending | Pending |
| E2E fixture/setup data used isolated repo-owned test/E2E config, not production/live DB | Pending | Pending |
| No raw `rm`, `sqlite3`, seed, reset, fixture, cleanup, or direct DB command targeted production/live DB | Pending | Pending |
| No manual query, data manipulation, data repair, delete, or truncate touched production/live DB | Pending | Pending |
| If the task created/changed a migration, Phase 2/3 artifact already records production/live app migration evidence; Phase 6 did not rerun it as test setup | Pending | Pending |

## Fixed Wait Review

Inspect the Playwright scripts and E2E tests used in this phase.

Record:

- files inspected
- whether any fixed waits were found
- deterministic waits/assertions used instead

This review is zero-tolerance. If any fixed wait is present, Phase 6 fails. Remove every fixed wait, replace it with deterministic Playwright waits/assertions such as `locator.waitFor`, `expect(locator)...`, `waitForURL`, `waitForResponse`, or persisted-state assertions, rerun the script/test, and review the files again before passing.

Do not justify fixed waits as stabilization, mutation timing, dialog close, navigation timing, screenshot timing, animation timing, or followed-by-assertion helpers. There is no allowed fixed-wait list.

| Command result | Fixed wait count | Disposition |
| --- | --- | --- |
| Pending | Pending | Pending |

If matches were found and removed, record the replacement proof here.

| Removed file:line | Replacement wait/assertion | Rerun evidence |
| --- | --- | --- |
| None found yet | N/A | Replace this row if the audit finds and removes matches |

## Coverage Gaps

| Gap | Reason | Risk |
| --- | --- | --- |
| Pending | Pending | Pending |

## Timeout And Quiet-Run Triage

Record every timed-out, quiet, or longer-timeout E2E/helper run. A longer rerun is allowed only after a timer-only/no-useful-output failure and clean triage proving the app and spec are valid to rerun.

| Command | Timeout | Result/useful evidence? | Triage checked: helper logs, readiness, URL, not-found/error state, DB/fixture, server log, browser console, network/page state | Rerun/fix decision |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

## E2E Quality Review

| Check | Status | Evidence |
| --- | --- | --- |
| Existing E2E tests preserved, updated, removed, or defended | Pending | Pending |
| Connected existing E2E tests inspected before remove/update/add/`N/A` decisions | Pending | Pending |
| Existing E2E flow updated or removed when warranted behavior belongs there or old coverage is no longer useful | Pending | Pending |
| Old/excess connected E2E tests removed, simplified, updated, or explicitly defended | Pending | Pending |
| New E2E tests, if any, have a complete burden ledger | Pending | Pending |
| New E2E bulk was merged/reduced or explicitly justified per case | Pending | Pending |
| New E2E test added only when the workflow was core/complex and no existing flow could cover it | Pending | Pending |
| Removed E2E tests have rationale, diff/readback evidence, and remaining critical-flow coverage notes | Pending | Pending |
| Identified unnecessary, obsolete, brittle, convoluted, or non-core/non-complex E2E tests were removed or defended | Pending | Pending |
| Exact command output recorded for required E2E runs, or `N/A` coverage-decision/removal evidence recorded | Pending | Pending |
| New/updated tests assert user-visible or persisted state when tests were warranted | Pending | Pending |
| New/updated E2E tests prove real core task functionality | Pending | Pending |
| Superficial color/class/existence-only checks avoided | Pending | Pending |
| Tests avoid brittle implementation details | Pending | Pending |
| Fixed wait review completed and clean | Pending | Pending |
| Coverage gaps reflected in `open-gaps.md` | Pending | Pending |
| Server/command discipline passed | Pending | Pending |
| Correct lifecycle owner managed startup/readiness/cleanup | Pending | Pending |
| First E2E command established lifecycle ownership before testing | Pending | Pending |
| Browser preflight/lifecycle evidence recorded | Pending | Pending |
| Test selection and retry ledger complete | Pending | Pending |
| Connected-spec ledger covers each E2E command; explicit full-suite command cites task request or concrete exact-task repo requirement | Pending | Pending |
| Full E2E rerun, if used after targeted/connected E2E passed, cites related code/test/config/fixture/migration/build-input invalidation | Pending | Pending |
| Suspected pre-existing/order-dependent failures were diagnosed with narrow evidence before any broader command was considered | Pending | Pending |
| Repeated E2E commands have material change, stale-output, or diagnostic reasons | Pending | Pending |
| First-run targeted E2E timeout was at or below `30000` ms or justified | Pending | Pending |
| Longer timeout, if used, has timer-only/no-useful-output failure plus clean triage evidence | Pending | Pending |
| Timeout/quiet-run triage recorded for every timed-out, quiet, or longer-rerun command | Pending | Pending |
| Cleanup method recorded and bounded | Pending | Pending |

## Gate

| Metric | Required | Actual |
| --- | --- | --- |
| Score | >= 24/30 | 0/30 |
| Critical E2E items, or defended `N/A` decision | all pass | Pending |
| E2E coverage decision recorded, including `N/A` when no E2E is warranted | yes | Pending |
| Connected existing E2E tests inspected before remove/update/add/`N/A` decisions | yes | Pending |
| Existing E2E coverage updated or removed when warranted by the coverage decision | yes | Pending |
| New E2E tests added only when existing tests cannot cleanly cover a core/complex workflow | yes | Pending |
| Old/excess connected E2E tests removed, simplified, updated, or explicitly defended | yes | Pending |
| New E2E tests, if any, have a complete burden ledger | yes | Pending |
| New E2E bulk was merged/reduced or explicitly justified per case | yes | Pending |
| Removed E2E tests have rationale, diff/readback evidence, and remaining critical-flow coverage notes | yes | Pending |
| New/affected critical behavior covered or defended | yes | Pending |
| Tests assert meaningful functional outcomes | yes | Pending |
| Superficial/flaky one-off checks avoided | yes | Pending |
| Required tests pass, no E2E was warranted, or unrelated failure evidenced | yes | Pending |
| Exact E2E command output recorded in artifact or cited repo-local log when a command was required; otherwise `N/A` decision/removal evidence recorded | yes | Pending |
| Phase 3 build reused, or rebuild reason and output recorded | yes | Pending |
| Open gaps for E2E coverage updated | yes | Pending |
| `open-gaps.md` finalized with real rows or explicit none rows | yes | Pending |
| E2E quality review passed | yes | Pending |
| Test selection and retry ledger complete | yes | Pending |
| E2E command scope matches the coverage decision or an exact full-E2E requirement | yes | Pending |
| Repeated E2E commands have material change, stale-output, or diagnostic reasons | yes | Pending |
| Fixed wait review completed and clean | yes | Pending |
| Server/command discipline passed | yes | Pending |
| Production/live database safety evidence is recorded and clean | yes | Pending |
| Repo-owned test database configuration evidence recorded | yes | Pending |
| Correct lifecycle owner managed startup/readiness/cleanup | yes | Pending |
| First E2E command established lifecycle ownership before testing | yes | Pending |
| Existing repo E2E ran through lifecycle helper by default, or native Playwright exception was recorded before command | yes | Pending |
| First-run targeted E2E timeout was at or below `30000` ms or justified | yes | Pending |
| Longer timeout, if used, has timer-only/no-useful-output failure plus clean triage evidence | yes | Pending |
| Timeout/quiet-run triage recorded for every timed-out, quiet, or longer-rerun command | yes | Pending |
| Lifecycle fallback, if used, has recorded helper diagnostics and ownership evidence | yes | Pending |
| DB/setup/server lifecycle reuse or invalidation reason recorded | yes | Pending |
| Browser preflight/lifecycle evidence recorded | yes | Pending |
| Cleanup method recorded and bounded | yes | Pending |
| `progress.md` current and points to Phase 7 next action | yes | Pending |
| `progress.md` points to this Phase 6 artifact for E2E files and repair details | yes | Pending |
| `progress.md` Phase Artifact Index and Artifact Pointers current | yes | Pending |
| Promotion lock verified before marker advance | yes | Pending |

Decision: Fail
