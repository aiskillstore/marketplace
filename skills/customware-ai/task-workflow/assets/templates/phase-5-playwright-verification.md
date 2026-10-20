# Phase 5 - Interactive Playwright Verification

## App Launch

| Field | Value |
| --- | --- |
| Launch command | Pending |
| Lifecycle helper command | Pending |
| First app/browser command lifecycle owner | Pending |
| URL | Pending |
| Playwright scripts | Pending |
| Server PID | Pending |
| Server log | Pending |
| Readiness proof | Pending |
| Runtime command logs | Pending |
| Browser preflight result | Pending |
| Initial command timeout | Pending |
| Timeout/quiet-run triage, if any | Pending |

## Phase 3 Build Reuse

Reuse the Phase 3 passing build unless code, config, package/dependency files, migrations/build inputs, generated assets, stale output, or incompatible verification tooling invalidated it after Phase 3. Do not rebuild only because Phase 5 is starting or a server command needs a production bundle.

| Item | Evidence |
| --- | --- |
| Phase 3 build evidence reviewed | Pending |
| Reused Phase 3 build or rebuild reason | Pending |
| If rebuilt, command/log and invalidating change | Pending |

## Server And Command Discipline

| Check | Status | Evidence |
| --- | --- | --- |
| Correct lifecycle owner recorded before command: helper by default; repo `webServer` or manual fallback only with reason/diagnostics made before the command | Pending | Pending |
| First browser/app-server run established lifecycle ownership before testing, with no reliance on an assumed existing server | Pending | Pending |
| App server started by the recorded lifecycle owner, not as an unbounded foreground command | Pending | Pending |
| Server readiness checked by the recorded lifecycle owner before browser interaction | Pending | Pending |
| Browser preflight passed, or mismatch failed early without `playwright install` | Pending | Pending |
| Playwright scripts run as bounded helper commands | Pending | Pending |
| Runtime logs preserved under `task-workflow/runtime/` | Pending | Pending |
| Pre-server setup, if needed, ran through lifecycle `--setup` or justified repo/fallback setup without manual chain bundling | Pending | Pending |
| Repo E2E/end-to-end config owned test DB paths for helper/setup/server/run commands | Pending | Pending |
| Playwright/custom fixture writes used repo-owned test DB paths | Pending | Pending |
| Fetch/stale DB/stale build/wrong-port issues were diagnosed through lifecycle logs/readiness before any fallback | Pending | Pending |
| First-run targeted script/probe used `15000`-`20000` ms timeout, or task-specific reason for a different first timeout is recorded | Pending | Pending |
| Longer timeout, if used, followed timer-only/no-useful-output failure plus helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage | Pending | Pending |
| Useful failure evidence was diagnosed directly instead of retried with a larger timeout | Pending | Pending |
| Manual fallback, if used, captured PID/log/readiness/cleanup evidence under `task-workflow/runtime/`; otherwise N/A | Pending | Pending |
| Background server cleaned up by helper or explicitly handed to next bounded command | Pending | Pending |
| Cleanup method recorded and bounded | Pending | Pending |

## Production Database Safety

Production/live workspace databases, especially `.dbs/database.db`, are not scratch files. Deleting, resetting, reseeding, truncating, manipulating, or corrupting them can destroy user work and can cause the user to lose his job. Phase 5 may use only isolated test/E2E state proved by repo-owned config. The production/live DB may not be touched for Playwright setup, fixture setup, seed, reset, debug, cleanup, manual queries, direct SQLite, data repair, or any data manipulation.

| Check | Status | Evidence |
| --- | --- | --- |
| Every setup/server/run command that mentions DB/data state was reviewed before running | Pending | Pending |
| Production/live DB paths, including `.dbs/database.db` or equivalent default user-data DB, were not deleted/reset/seeded/truncated/migrated/opened with write risk | Pending | Pending |
| Playwright fixture/setup data used isolated repo-owned test/E2E config, not production/live DB | Pending | Pending |
| No raw `rm`, `sqlite3`, seed, reset, fixture, cleanup, or direct DB command targeted production/live DB | Pending | Pending |
| No manual query, data manipulation, data repair, delete, or truncate touched production/live DB | Pending | Pending |
| If the task created/changed a migration, Phase 2/3 artifact already records production/live app migration evidence; Phase 5 did not rerun it as test setup | Pending | Pending |

## Phase 5 Coverage Plan

Phase 5 is the main user-facing verification phase. Use multiple focused Playwright scripts, probes, viewport passes, screenshots, or clean reruns when needed to prove changed flows and UI correctness. The limit is relevance to the changed or adjacent surfaces, not the smallest possible number of browser checks.

| Coverage area | Planned script/probe/viewport evidence | Why this is needed for the changed UX | Scope boundary so this does not become a broad unrelated audit |
| --- | --- | --- | --- |
| Main changed user flow | Pending | Pending | Pending |
| Relevant bad case or non-ideal user action | Pending | Pending | Pending |
| Surrounding shared UI or adjacent workflow | Pending | Pending | Pending |
| Responsive/visual correctness | Pending | Pending | Pending |

## Stage 1 - Functional Behavior

Prove the changed behavior works through real user interaction. Keep this stage focused on the changed surface and directly related nearby behavior.

| Flow/route/state | User action sequence | Expected user-visible result | Script/evidence | Result/fix |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

## Stage 1 - Relevant User-Perspective Stress Coverage

Exercise relevant non-ideal behavior a real user could do while using the changed feature: invalid inputs, cancel/close paths, repeated clicks where relevant, out-of-order actions, navigation away/back, empty states, and nearby controls.

| Scenario | User action | Expected user-visible result | Script/evidence | Result/fix |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

## Surrounding Feature Smoke

Check nearby UI/features sharing the changed surface so the task did not break unrelated but adjacent behavior.

| Surrounding feature | Why at risk | Script/evidence | Result |
| --- | --- | --- | --- |
| Pending | Pending | Pending | Pending |

## Stage 2 - Responsive UI And Visual Quality

Verify the main changed flow and affected nearby UI on mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` desktop when UI changed. Responsive quality is a first-class Phase 5 pass condition, equal to the task's functional behavior working. Check for broken, cramped, overlapping, clipped, ill-placed, unreadable, unusable, or non-responsive UI; also check navigation access, tap/click targets, dialogs/menus, accidental horizontal scroll, controls outside the viewport, screenshots, and whether normal desktop/1080p has excessive dead space. Some whitespace is fine. `2560x1440` may have some extra whitespace, but not broad empty regions that make the UI feel unfinished. Large empty areas are acceptable on 4K/ultrawide only when the layout is intentionally constrained and still coherent.

| Viewport | Flow/area | Overlap/cramped/clipped/readability result | Responsive/nav/tap/dialog result | Screenshot/evidence | Fix/rerun |
| --- | --- | --- | --- | --- | --- |
| Mobile, e.g. 390x844 | Pending | Pending | Pending | Pending | Pending |
| Tablet, e.g. 768x1024 | Pending | Pending | Pending | Pending | Pending |
| Desktop, e.g. 1440x900 | Pending | Pending | Pending | Pending | Pending |
| Standard desktop, 1920x1080 | Pending | Pending | Pending | Pending | Pending |
| Large desktop, 2560x1440 | Pending | Pending | Pending | Pending | Pending |

## Screenshot Existence Audit

Every screenshot path cited anywhere in this artifact must exist when the Phase 5 gate is scored. Verify cited paths with a bounded file-read/listing command and record the proof here.

| Screenshot path cited | Existence proof command/output | Result |
| --- | --- | --- |
| Pending | Pending | Pending |

## Issues Found And Fixed

| Issue | Fix | Evidence |
| --- | --- | --- |
| Pending | Pending | Pending |

## Timeout And Quiet-Run Triage

Record every timed-out, quiet, or longer-timeout Playwright/helper run. A longer rerun is allowed only after a timer-only/no-useful-output failure and clean triage proving the app and script are valid to rerun.

| Command | Timeout | Result/useful evidence? | Triage checked: helper logs, readiness, URL, not-found/error state, DB/fixture, server log, browser console, network/page state | Rerun/fix decision |
| --- | --- | --- | --- | --- |
| Pending | Pending | Pending | Pending | Pending |

## Fixed Wait Review

Inspect the Playwright scripts used in this phase and any E2E tests created so far.

Record:

- files inspected
- whether any fixed waits were found
- deterministic waits/assertions used instead

This review is zero-tolerance. If any fixed wait is present, Phase 5 fails. Remove every fixed wait, replace it with deterministic Playwright waits/assertions such as `locator.waitFor`, `expect(locator)...`, `waitForURL`, `waitForResponse`, or persisted-state assertions, rerun the script/test, and review the files again before passing.

Do not justify fixed waits as stabilization, mutation timing, dialog close, navigation timing, screenshot timing, animation timing, or followed-by-assertion helpers. There is no allowed fixed-wait list.

| Command result | Fixed wait count | Disposition |
| --- | --- | --- |
| Pending | Pending | Pending |

If matches were found and removed, record the replacement proof here.

| Removed file:line | Replacement wait/assertion | Rerun evidence |
| --- | --- | --- |
| None found yet | N/A | Replace this row if the audit finds and removes matches |

## Gate

| Metric | Required | Actual |
| --- | --- | --- |
| Score | >= 44/50 | 0/50 |
| Critical Playwright items | all pass | Pending |
| Phase 5 coverage plan proves the run was thorough enough for changed user-facing flows and UI | yes | Pending |
| Stage 1 main touched/implied flows covered | yes | Pending |
| Stage 1 relevant bad cases and non-ideal user behavior covered | yes | Pending |
| Surrounding feature smoke completed | yes | Pending |
| Stage 2 mobile/tablet/desktop/1080p/2560px responsive UI verified when UI changed | yes | Pending |
| Stage 2 responsive UI quality passes as a first-class guarantee alongside task functionality | yes | Pending |
| Broken/cramped/overlapping/clipped/ill-placed/unusable/non-responsive UI issues resolved or defended | yes | Pending |
| Screenshot paths exist | yes | Pending |
| Screenshot existence audit completed for every cited path | yes | Pending |
| Phase 3 build reused, or rebuild reason and output recorded | yes | Pending |
| Production/live database safety evidence is recorded and clean | yes | Pending |
| Critical UI/runtime issues resolved or defended | yes | Pending |
| Phase 5 failures routed to the earliest affected phase, then Phase 3 check/lint evidence and Phase 4 unit coverage were re-passed before rechecking | yes | Pending |
| Open gaps for interactive verification updated | yes | Pending |
| `open-gaps.md` finalized with real rows or explicit none rows | yes | Pending |
| Audited Playwright/E2E files use deterministic waits/assertions | yes | Pending |
| Fixed wait review completed and clean | yes | Pending |
| Server/command discipline passed | yes | Pending |
| Repo-owned test database configuration evidence recorded | yes | Pending |
| Correct lifecycle owner managed startup/readiness/cleanup | yes | Pending |
| First app/browser command established lifecycle ownership before testing | yes | Pending |
| First-run targeted script/probe timeout was `15000`-`20000` ms or justified | yes | Pending |
| Longer timeout, if used, has timer-only/no-useful-output failure plus clean triage evidence | yes | Pending |
| Timeout/quiet-run triage recorded for every timed-out, quiet, or longer-rerun command | yes | Pending |
| Lifecycle fallback, if used, has recorded helper diagnostics and ownership evidence | yes | Pending |
| Browser preflight/lifecycle evidence recorded | yes | Pending |
| Cleanup method recorded and bounded | yes | Pending |
| `progress.md` current and points to Phase 6 next action | yes | Pending |
| `progress.md` points to this Phase 5 artifact for Playwright scripts, screenshots, logs, and repair details | yes | Pending |
| `progress.md` Phase Artifact Index and Artifact Pointers current | yes | Pending |
| Promotion lock verified before marker advance | yes | Pending |

Decision: Fail
