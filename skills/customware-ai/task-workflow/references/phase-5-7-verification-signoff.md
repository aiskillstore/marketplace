# Verification And Signoff

Use this reference for Phase 5, Phase 6, and Phase 7.

These phases prove the implementation through real browser interaction, the Phase 6 E2E coverage decision, and final artifact audit. They are internal verification gates, not user confirmation points.

This is a looped gate workstream: Phase 5, Phase 6, and Phase 7 are not complete until their artifacts pass their gates. A failing score, missing evidence, browser issue, weak test, stale gap, placeholder row, or incomplete final audit means stay in or return to the failing phase, repair the work, update the artifact, rescore, and repeat. Do not stop or ask the user to continue when a local repair is available.

## Verification Authority

Verification authority is:

1. the task body
2. Phase 1 implementation and verification plan
3. changed files and behavior from Phase 2 and Phase 3
4. Phase 4 unit-test coverage results
5. real browser behavior observed through standalone Playwright scripts
6. Phase 4 unit-test evidence and Phase 6 E2E evidence when a phase-owned coverage decision says durable coverage is warranted

Check/lint validation, builds, and tests are not substitutes for interactive Playwright verification.
Interactive Playwright verification is not a reason to create regression tests when the Phase 4 or Phase 6 coverage decision says durable tests are not warranted.

## Open Gaps Reconciliation

`task-workflow/open-gaps.md` is a gate artifact during verification.

- Phase 5 must resolve or update gaps about browser/runtime/manual verification.
- Phase 6 must resolve or update gaps about E2E coverage proof.
- Phase 7 must compare `open-gaps.md` against Phase 4, Phase 5, and Phase 6 artifacts. If a phase says a gap was fixed but `open-gaps.md` still lists it as `Open`, Phase 7 fails.
- Critical gaps must be `Resolved`, `Closed`, or explicitly reclassified with evidence before signoff. They cannot remain `Open`.
- Template placeholder rows such as `Pending | Pending | Pending` are not clean ledger evidence. Replace them with real gap rows or explicit `None currently recorded` rows before any verification gate passes.

## Progress Ledger Reconciliation

`task-workflow/progress.md` must stay current through verification and signoff.

- After compaction, resume, retry, reconnect, or new coding session, use `progress.md` and `CURRENT_PHASE.txt` to identify current status, then re-read the main `SKILL.md`, `open-gaps.md`, the current phase artifact, and the required current phase reference before choosing the next verification action.
- At every Phase 5, Phase 6, or Phase 7 start or promotion, re-read the required reference file or files for the current phase before doing phase work.
- Update it after each Phase 5 browser issue/fix/rerun, Phase 6 E2E coverage decision or E2E run, Phase 7 audit result, blocker, gate pass/fail, and promotion.
- It must summarize latest browser evidence, Phase 4 unit evidence, Phase 6 E2E evidence, fixed-wait review state, open gaps, current phase, earliest failing phase, and next local action.
- Its Current Phase Pointers must identify the current phase artifact, current reference, next local action, and only high-signal active files needed to resume immediately.
- Its Artifact Pointers must point to the phase-owned artifacts where unit evidence, Playwright scripts, screenshots, runtime logs, E2E files, and verification repair details live.
- Phase 7 cannot pass if `progress.md` says any phase remains pending, in progress, failing, or locally repairable.

## Verification Quality Discipline

<verification_quality_discipline>

Interactive scripts and E2E tests must wait on user-visible state or app signals.

### Do

- Prefer role/text locators, URL assertions, network-visible state, persisted data checks, and `expect` retries.
- Do not use fixed waits such as `waitForTimeout`, `setTimeout`, or `sleep(...)` in `task-workflow/playwright` or `tests/e2e`.
- Do not use fixed waits as "stabilization", "mutation timing", "dialog close", "navigation timing", "screenshot timing", "animation timing", or "followed by assertion" helpers. These labels do not make a fixed wait acceptable.
- Phase 5 and Phase 6 must inspect their interactive scripts and E2E tests before scoring the gate.
- Record the files inspected and whether they contain any fixed waits.

### Gate Rule

- If any fixed wait is present, the phase fails. Remove every fixed wait, replace it with a deterministic Playwright wait/assertion, rerun the affected script/test, and review the files again before passing.
- Remove debug-only Playwright scripts or include them in the fixed-wait review. Debug scripts under `task-workflow/playwright` are part of the verification surface.
- A click, form submit, fill action, mutation trigger, screenshot timing note, or "dialog animation" note is not assertion/state-wait evidence.
- Acceptable proof must cite a concrete post-action wait/assertion such as `locator.waitFor(...)`, `expect(locator).toBeVisible()`, `expect(locator).toContainText(...)`, `waitForURL(...)`, `waitForResponse(...)`, or a persisted-state assertion.
- The review is zero-tolerance: Phase 5, Phase 6, and Phase 7 pass only when the artifact states that inspected verification files contain no fixed waits and cites deterministic waits/assertions used instead.

</verification_quality_discipline>

## Server And Command Discipline

<server_command_discipline>

Verification phases must not stall on foreground servers or watchers.

### Lifecycle Ownership

- Default to `task-workflow/scripts/playwright-lifecycle.mjs` for Playwright scripts, browser probes, app-server startup, readiness, Playwright browser preflight, bounded command execution, output capture, and cleanup.
- The first Phase 5 browser command or Phase 6 Playwright/E2E command that needs a running app must establish lifecycle ownership before the browser/test runs. Do not point a script at an assumed existing `127.0.0.1` server first and then treat `fetch failed`, redirects, not-found data, stale DB state, stale build output, or wrong-port behavior as evidence for manual server management.
- In Phase 6, existing repo E2E tests still run through the helper by default: put `pnpm exec playwright test ...` inside the helper's `--run` while the helper owns setup, server startup, readiness, browser preflight, output capture, and cleanup.
- Use native Playwright with repo `webServer` ownership only when the helper cannot own the server for that exact command, such as a repo config that cannot target an already-running helper server and cannot have `webServer` bypassed for the selected spec. Record that reason before running the native command. A repo merely having a Playwright config, `webServer`, global setup, or existing E2E file is not enough.
- The helper runs each `--setup` command before server startup with bounded timeout and `task-workflow/runtime/setup-*.log`, starts the app server in the background, records `task-workflow/runtime/server.pid`, writes `task-workflow/runtime/server.log`, polls the supplied readiness URL, runs each `--run` command with bounded timeout and `task-workflow/runtime/run-*.log`, and stops the server process group after the run unless `--keep-server` is explicitly used and justified.
- Before choosing Phase 5 or Phase 6 setup/server commands, discover the repo's expected verification lifecycle from `AGENTS.md`, `package.json`, README/docs, Playwright config, and `tests/e2e` helpers. The expected pattern is a repo-owned setup command that prepares isolated E2E/test state and deterministic seed data, plus a repo-owned server command that starts the app against that isolated state. Use those commands when present. In older repos without named scripts, simulate the same pattern with the smallest repo-owned/test-only commands and record the mapping before running them.

### Database And Server Safety

- Database file paths are not a lifecycle-helper option. Do not set `E2E_DATABASE_FILE_PATH`, `DATABASE_PATH`, `DB_PATH`, or any similar database file/path variable with helper `--env`, `--setup`, `--server`, `--run`, native Playwright commands, or custom scripts. Do not change the repo's internal E2E/end-to-end database file path. Use the target repo's checked-in E2E/end-to-end database config or already-materialized environment. `.dbs/database.db` is the live workspace/production database, not a test database; production databases must never be used for testing. Any Playwright/E2E/end-to-end fixture write, reset, migration, seed, direct SQLite access, inspection-with-write-risk, cleanup, debugging, manual query, or data manipulation against `.dbs/database.db` is a critical failure.
- Treat production/live database safety as job-critical. Deleting, resetting, reseeding, truncating, or corrupting the production database can destroy user work and can cause the user to lose his job. This is not an acceptable verification risk, even in a sandbox, because the workflow trains agents to touch live user data.
- The only allowed production/live database action is the app's required migration command for a real schema change. This does not permit working on `.dbs/database.db` or any production/live DB. If the task creates or changes a migration, that migration must already have been run against the production/live default DB in the owning implementation/static-check phase, recorded as migration evidence, and not mixed with seed/reset/fixture/test cleanup. Verification phases may use only isolated test/E2E database state proved by repo-owned config.
- Before any Phase 5 or Phase 6 command that mentions `db`, `database`, `sqlite`, `migrate`, `seed`, `fixture`, `reset`, `.dbs`, `rm`, `truncate`, or similar data-state words, record the target database path/source in the phase artifact. If the target is production/live, unknown, or only assumed safe, do not run the command.
- Do not assume a backgrounded process started successfully just because the command returned. A server is ready only after the helper records a successful readiness result.
- Do not compose manual server cleanup, fixed sleep, DB-delete, server-start, and Playwright command chains in Phase 5 or Phase 6. Put pre-server setup such as isolated test DB reset, test migration, test seed, or test fixture preparation into lifecycle `--setup "..."` for helper-owned runs. Treat setup plus server startup as reusable for the current verification batch: prefer one helper-owned run with the needed script/spec commands, or rerun setup only after code, migrations, fixtures, DB state, build inputs, or the prior setup output changed. Do not repeatedly delete/recreate the DB or restart the server before each targeted script/spec just because another E2E command is next. If cleanup is needed, do it as a separate recorded recovery step before the helper run, then run the helper alone. If the helper times out or produces no useful output, treat that as lifecycle/setup evidence, inspect `task-workflow/runtime/server.log`, `task-workflow/runtime/setup-*.log`, readiness output, and `task-workflow/runtime/run-*.log`, then change the setup, server command, ready URL, test command, fixture, or diagnostic before rerunning. If the helper fails once or twice with a diagnosed lifecycle/tooling issue after a corrected invocation, record the helper logs and switch to the smallest fallback that can prove the task: repo Playwright `webServer`, explicit PID/port cleanup, or manual server management with captured PID/log/readiness/cleanup evidence.
- Do not run `playwright install`, `playwright install chromium`, or equivalent browser downloads during task verification. The helper sets `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` when present and fails early when the project Playwright version does not match the sandbox browser cache.
- Do not leave `pnpm dev`, `npm run dev`, `vite`, `next dev`, test watchers, or similar long-lived commands as the active foreground tool call.
- If the server or test command hangs, stop it, capture the log/error evidence, update the current phase artifact or `open-gaps.md`, and continue with the smallest local recovery path.
- If the server appears stale, wrong, or on the wrong port, diagnose through the lifecycle owner: helper runtime logs/readiness first, then repo Playwright `webServer` output/config only for commands where `webServer` owns lifecycle. If a build or DB fixture changed, restart by rerunning the lifecycle owner with the corrected `--setup` or server command. Do not switch to broad process cleanup unless PID/port cleanup is impossible and the artifact records the recovery reason.
- If manual fallback is genuinely needed, keep ownership explicit: write the PID/log path under `task-workflow/runtime/`, prove readiness with a bounded check, and clean up the captured PID/process group. Do not use `nohup`, `disown`, or a background server without PID/readiness evidence as the normal fallback.
- Bash readiness polling inside the lifecycle helper is acceptable. The fixed-wait ban applies to Playwright scripts and E2E tests under `task-workflow/playwright` or `tests/e2e`, not the helper's bounded readiness loop.

</server_command_discipline>

## Playwright Failure Triage

When a Phase 5 script or Phase 6 targeted spec fails, diagnose the failure type before rerunning.

- If a selector/action/assertion times out, first prove the page is in the expected state: URL, no not-found/error screen, required DB or fixture record exists, server log has no route/runtime error, and browser console has no fatal error. Do not rerun the same script while the page state is wrong; fix setup, seed, route, or app state first.
- If the helper times out, exits with no useful output, or appears hung, inspect helper setup/server/run logs and readiness evidence before rerunning. The next run must change setup, server command, ready URL, test command, fixture, timeout reason, or diagnostic output.
- If the page state is correct and the assertion is valid, fix implementation or test code, then rerun the smallest affected script/spec.
- Timeout increases are not a retry strategy. Start with the smallest practical timeout: `15000`-`20000` ms for Phase 5 launch/page-state/custom-script probes and up to `30000` ms for first-run Phase 6 targeted E2E where Playwright runner startup adds overhead. If the run fails with any useful error, assertion output, not-found state, console/runtime error, route error, fixture/DB miss, or helper diagnostic, use that evidence to diagnose; do not retry with a larger timeout. A larger timeout is allowed only when the first run ended only because the timer expired with no useful response or explanation, and only after helper logs, readiness, URL, not-found/error state, required DB/fixture records, server runtime logs, browser console, and network/page state prove the app and test are in the correct state to run. Only then may one rerun use `60000` ms, and never more than `120000` ms for one targeted script/spec. If a single targeted run needs more than two minutes, split the verifier or diagnose lifecycle, setup, fixture, page-state, console, network, or test-design failure instead of increasing the timeout.
- Record the timeout value, result, whether useful failure evidence existed, triage checks, and any longer-rerun reason in the current Phase 5 or Phase 6 artifact. A phase cannot pass with only a narrative claim that the run was slow or quiet.

Example helper shape:

```bash
node task-workflow/scripts/playwright-lifecycle.mjs \
  --setup "pnpm run prepare:e2e" \
  --server "pnpm run start:e2e" \
  --ready-url "http://127.0.0.1:4444" \
  --run "node task-workflow/playwright/verify-main-flow.mjs" \
  --command-timeout-ms 20000
```

For E2E:

```bash
node task-workflow/scripts/playwright-lifecycle.mjs \
  --setup "pnpm run prepare:e2e" \
  --server "pnpm run start:e2e" \
  --ready-url "http://127.0.0.1:4444" \
  --run "pnpm exec playwright test tests/e2e/changed-flow.spec.ts --reporter=line" \
  --command-timeout-ms 30000
```

`prepare:e2e` and `start:e2e` are example names for the expected repo-owned isolated setup/server pattern. Use those exact commands when the repo provides them. In older repos, map the example to equivalent repo-owned commands or task-local setup that preserves the same isolation. Do not copy these examples with a raw production `db:migrate`, `seed`, `rm .dbs/database.db`, or any command that writes the live/default database.

## Phase 5: Interactive Playwright Verification

Phase 5 has two required evidence stages:

| Stage | Must prove | Scope |
| --- | --- | --- |
| Stage 1 | the changed behavior works through real user interaction | primary changed route, touched controls, relevant bad cases, nearby shared UI |
| Stage 2 | the UI is visually sound and responsive | no broken, cramped, overlapping, clipped, ill-placed, unreadable, unusable, or non-responsive affected UI |

> Phase 5 is intentionally thorough. The Phase 4/Phase 6 test-minimality rules restrict durable automated tests; they do not weaken interactive browser verification. Use as many focused Playwright scripts, probes, viewport passes, screenshots, and clean reruns as needed to prove the changed user experience is functionally correct and visually sound. The constraint is relevance and lifecycle discipline, not fewest checks.

1. Set `task-workflow/CURRENT_PHASE.txt` to `phase-5-playwright-verification`.
2. Read `references/playwright-interactive.md`.
3. Confirm `references/phase-5-7-verification-signoff.md` and `references/playwright-interactive.md` are loaded as the required current phase references before Phase 5 work starts.
4. Confirm `task-workflow/scripts/playwright-lifecycle.mjs` exists and is readable.
5. Write standalone Playwright scripts under `task-workflow/playwright/`. Multiple scripts are acceptable when they keep the evidence clearer, separate functional and responsive concerns, or isolate failure triage.
6. Run the scripts through `task-workflow/scripts/playwright-lifecycle.mjs` with the repo's normal local app command, a readiness URL, bounded command timeout, runtime logs, and production/live database safety proof. First-run Phase 5 script/probe timeout should be `15000`-`20000` ms.
7. Stage 1 - functional behavior: drive the changed feature through real user interactions and prove the task behavior works. Verify primary routes, forms, buttons, menus, dialogs, tables, navigation, save flows, and error states touched or implied by the task.
8. In Stage 1, exercise only the relevant bad cases and non-ideal user behavior: invalid submissions, empty states, cancel/close paths, repeated clicks where relevant, out-of-order actions, navigating away/back, and nearby controls a real user could click while using the feature.
9. In Stage 1, smoke-test surrounding UI/features that share the changed surface, such as adjacent navigation, list/detail transitions, filters/search, dialogs, menus, sidebars, and nearby actions that could be accidentally broken by the implementation.
10. Stage 2 - UI and responsive quality: verify the affected UI is not broken, cramped, overlapping, clipped, ill-placed, unreadable, unusable, or non-responsive. Check mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` desktop viewports when the task changes UI. Treat this as equal to proving the task's functional changes work: Phase 5 fails if either Stage 1 behavior or Stage 2 UI quality is broken. Standard desktop/1080p screens must not have excessive dead space that makes the app look abandoned or sparse. `2560x1440` may have some extra whitespace, but not broad empty regions that make the UI feel unfinished. 4K/ultrawide whitespace is acceptable when the layout is intentionally constrained and still coherent.
11. Keep Phase 5 scripts focused on proving the changed behavior and affected UI quality. Do not turn Phase 5 into a broad app audit unrelated to the changed surface.
12. Capture screenshots under `task-workflow/screenshots/` for the main changed flows and responsive evidence.
13. Verify every screenshot path cited in the Phase 5 artifact exists before scoring the gate. Record the file-existence command/readback proof in `task-workflow/phase-5-playwright-verification.md`.
14. If Phase 5 finds a broken flow, bad-case failure, surrounding-feature regression, missing screenshot file, or responsive/UI-quality issue, Phase 5 fails. Record it in the artifact and `open-gaps.md`, return to the earliest affected phase, usually Phase 2 for source fixes, then re-pass Phase 3 check/lint evidence and Phase 4 unit coverage before re-entering Phase 5.
15. Fix discovered issues and rerun the scripts from clean Node.js processes through the lifecycle helper. Use a longer timeout only after a timer-only/no-useful-output failure and recorded clean triage proves the app and test are valid to rerun.
16. Review the interactive scripts and E2E tests created so far for fixed waits and record the files inspected plus the result.
17. Update `task-workflow/open-gaps.md` for every browser/runtime/manual-verification gap closed, defended, or still open.
18. Update `task-workflow/progress.md` with browser evidence summary, a pointer to `task-workflow/phase-5-playwright-verification.md` for Playwright/screenshot/log details, fixed-wait review state, open gaps, and next local action.
19. Replace all `open-gaps.md` placeholder rows with real rows or explicit `None currently recorded` rows.
20. Record Stage 1 functional behavior coverage, Stage 2 UI/responsive quality coverage, relevant bad-case coverage, surrounding-feature smoke, screenshots, screenshot existence proof, lifecycle helper command, readiness proof, runtime log paths, production/live database non-use proof, timeout/quiet-run triage, cleanup result, issues, fixes, open-gap status, and fixed-wait review evidence.
21. After the Phase 5 gate passes, set `task-workflow/CURRENT_PHASE.txt` to `phase-6-e2e-verification`.
22. Re-read `references/phase-5-7-verification-signoff.md` before doing Phase 6 work.
23. Update `task-workflow/progress.md` so current phase, current phase reference, and next local action match Phase 6.

## Required Interactive Evidence

The artifact must cite real evidence for the two Phase 5 stages:

- launch command and local URL
- lifecycle helper command
- readiness proof and runtime log path
- proof that no command used, deleted, reset, seeded, migrated, inspected-with-write-risk, or directly modified the production/live database
- Playwright script path
- Stage 1 route or state exercised
- Stage 1 interaction performed
- Stage 1 expected user-visible result
- Stage 1 bad case, non-ideal user action, or surrounding feature checked when relevant
- Stage 2 viewport checked, including dimensions such as mobile, tablet, desktop, `1920x1080`, or `2560x1440`
- Stage 2 UI quality result for overlap, cramped layout, clipping, placement, readability, usability, responsiveness, navigation access, tap/click targets, dialogs/menus, horizontal scroll, controls outside the viewport, and desktop dead-space
- screenshot path when visual proof matters
- screenshot existence proof for every screenshot path cited
- issue found
- fix made
- rerun result

Screenshots alone do not prove controls work. A control that matters to the task must be clicked, filled, selected, submitted, or otherwise exercised with real browser input.

Phase 5 is not a happy-path-only check, but it is scoped to the changed surface. Think like a real user who may click nearby controls, enter invalid data, abandon a flow, resize the viewport, use the feature on mobile, or do steps in an unexpected order. If that breaks the task flow or affected nearby UI, fix it before Phase 5 passes.

## Phase 5 Score

Score `task-workflow/phase-5-playwright-verification.md` against `50` items:

- `8` app launch and script discipline items
- `8` Stage 1 functional route/state coverage items
- `8` Stage 1 interaction and relevant bad-case coverage items
- `8` surrounding feature smoke items
- `8` Stage 2 responsive mobile/tablet/desktop/1080p/2560px UI-quality items
- `5` screenshot/evidence items
- `5` fix-and-rerun items

Critical failures:

- standalone Playwright script not created
- app not launched through the repo's local command
- app server launched as an unbounded foreground command
- lifecycle helper not used for Phase 5 app startup and script execution, except after recorded helper failure and a justified fallback
- first app/browser command ran against an assumed existing server instead of establishing helper/repo lifecycle ownership
- manual cleanup, fixed `sleep`, DB-delete, or server-start command chain used instead of the lifecycle helper before a diagnosed helper failure
- any Phase 5 command deletes, resets, reseeds, truncates, migrates, directly opens with write risk, or modifies the production/live workspace database, including `.dbs/database.db` or equivalent default user-data DB
- Phase 5 artifact lacks proof that DB/fixture/setup commands targeted only isolated repo-owned test/E2E state
- production/live DB access is treated as harmless because the run is a sandbox, because the file is local, or because the command appears under `task-workflow/`
- first-run targeted Phase 5 Playwright script/probe uses a timeout above `20000` ms without a task-specific artifact reason
- Phase 5 timeout is increased after useful failure evidence, or after timer-only/no-output failure without recorded helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage proving the app and script are valid to rerun
- timeout/quiet-run triage is missing from the Phase 5 artifact after any timed-out, quiet, or longer-rerun command
- `playwright install` or equivalent browser download attempted during verification
- server PID/log/readiness proof not recorded
- Stage 1 main touched route or flow not exercised
- Phase 5 reduced to a shallow smoke check when changed user-facing behavior or UI required real interaction, bad-case, surrounding-feature, or responsive evidence
- Stage 1 relevant bad cases and non-ideal user actions not exercised for the changed flow
- surrounding UI/features sharing the changed surface not smoke-tested
- Stage 2 mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` responsive behavior not checked for the affected UI when UI changed
- critical Stage 2 UI issue remains unresolved, such as cramped layout, overlapping controls, clipped content, ill-placed controls, inaccessible controls, broken navigation, unreadable text, unusable dialogs/menus, accidental horizontal scrolling, controls outside the viewport, excessive dead space on normal desktop/1080p screens, or broad unfinished-looking empty regions at `2560x1440`
- screenshot path cited but file does not exist
- screenshot paths are cited without file-existence proof in the artifact
- discovered critical UI/runtime issue remains unresolved
- Phase 5-discovered issue was not routed back to the earliest affected phase, then through Phase 3 check/lint evidence and Phase 4 unit coverage before rechecking
- script uses DOM shortcuts as a substitute for normal user interaction
- script contains any fixed wait in the audited files
- fixed-wait review not recorded
- fixed-wait review finds any occurrence in `task-workflow/playwright` or `tests/e2e`
- browser-verification gaps remain stale in `task-workflow/open-gaps.md`
- `task-workflow/open-gaps.md` still contains template placeholder rows

Pass gate:

- score is at least `44/50`
- every critical Playwright item passes
- Stage 1 proves every main touched or implied user flow with interactive evidence
- Stage 1 proves relevant bad cases, non-ideal user actions, and surrounding features with interactive evidence
- Phase 5 coverage plan explains the focused scripts/probes/viewports used and why they are enough for the changed user-facing scope
- Stage 2 verifies mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` responsive behavior for the affected UI when UI changed
- Stage 2 UI quality passes as a first-class guarantee alongside the task's functional behavior
- screenshots cited in the artifact exist
- screenshot existence proof is recorded for every screenshot path cited
- no unresolved critical UI/runtime issue remains
- browser-verification gaps in `task-workflow/open-gaps.md` are resolved, updated, or defended
- fixed-wait review is recorded and clean
- `task-workflow/open-gaps.md` has no placeholder `Pending` rows
- any background server started for the phase is cleaned up or explicitly handed to the next bounded command
- production/live database safety proof is recorded and clean

If this gate fails, stay in Phase 5.

## Phase 6: E2E Coverage Decision And Verification

1. Set `task-workflow/CURRENT_PHASE.txt` to `phase-6-e2e-verification`.
2. Confirm this reference is loaded as the required current phase reference before Phase 6 work starts.
3. For each changed workflow, decide whether E2E coverage is warranted. E2E is warranted only for a critical user workflow, complex multi-step flow, persistence/navigation boundary, permission boundary, or high-risk regression. Small fixes, visual-only changes, copy/color/style changes, spacing/layout tuning, simple button wiring, and incidental UI behavior normally require no new or updated E2E. Default to `N/A`, update existing, or remove/simplify existing E2E unless the artifact proves a durable E2E risk.
4. Inspect connected existing E2E tests for every changed workflow before choosing remove, update, add, or `N/A`. Identify whether the changed feature belongs in an existing flow, regression suite, or user journey.
5. Remove, merge, or simplify existing E2E tests when they are unnecessary, obsolete, duplicated, brittle, convoluted, or protect non-core/non-complex flows. This includes tests added by older agents. Record why removal improves the E2E suite and preserve useful critical-flow coverage elsewhere only when still needed.
6. Update an existing E2E test first when the warranted behavior extends an existing workflow or could affect existing functionality already covered there.
7. Add a new E2E test only when the task introduces or changes a core workflow that cannot be cleanly covered by an existing E2E test and the New E2E Burden Ledger proves every new case is necessary.
8. Do not use E2E to cover isolated non-UI logic. Record E2E `N/A` for that path and cite the Phase 4 unit-test decision when relevant.
9. Select the smallest useful E2E command that proves only the warranted E2E coverage. Start with new, changed, or directly connected E2E specs and maintain a connected-spec ledger. Never run the unfiltered full E2E suite unless the task explicitly asks for full E2E or a concrete written repo instruction names full E2E/all-spec execution for this exact task; "target repo instructions" must name full E2E or an equivalent all-spec command, not merely say to run tests. If warranted targeted or multi-spec commands already ran the connected specs and no related code, test, config, fixture, migration, or build input changed, that is the evidence; do not add a full E2E run for final confidence, final signoff, state discovery, or reviewer-satisfaction.
10. Record every meaningful E2E command with its scope, why that scope was selected, any previous related failure, what changed since that failure, outcome, and next action.
11. Do not rerun E2E tests only for confidence. Rerun when related implementation changed, the E2E test changed, config/environment changed, previous output was incomplete/stale, or the next run gathers a narrower diagnostic needed to fix a real failure.
12. Before rerunning the exact same failing E2E command, record what changed since the previous run or what new evidence the rerun will collect. If nothing changed and the previous output is complete, inspect logs, DOM/state, traces, screenshots, or persisted data first, then change the implementation, E2E test, command scope, or diagnostic strategy before running again.
13. When E2E tests are warranted, run the existing, updated, new, and connected tests needed to prove existing functionality still works and the new additions work with it. Use `task-workflow/scripts/playwright-lifecycle.mjs` as the default lifecycle owner for Playwright and app-server startup, including existing repo E2E specs. Put the native E2E command inside helper `--run`. Use native Playwright with repo `webServer` only when the helper cannot own the server for that exact command, or after the helper has failed once or twice with recorded diagnostics. Before setup/server selection, discover the repo's expected isolated verification setup and server commands. If setup is required before a helper-owned server starts, pass it with `--setup` instead of chaining setup, server start, and test execution in one shell command. First-run targeted Phase 6 E2E timeout should be at most `30000` ms. Keep one setup/server lifecycle for the related verification batch when the DB/build/server inputs remain valid; do not reset DB, rerun migrations/seed, or restart the server between targeted specs unless the previous run changed or invalidated isolated test/E2E state. Never reset, seed, inspect, or migrate the production/live database for E2E. When a failing E2E run suggests stale DB, stale server, wrong build, redirect, missing fixture data, not-found page state, selector timeout, or no useful helper output, inspect helper run/server/setup logs plus page state before rerunning through the same lifecycle owner. Use a longer timeout only after a timer-only/no-useful-output failure and recorded clean triage proves the app and test are valid to rerun.
14. Fix failures and rerun with the smallest command that can prove the fix.
15. Record the exact command output for every required E2E run. If output is long, write it to a repo-local log file, cite that path, and copy the final pass/fail lines exactly into `task-workflow/phase-6-e2e-verification.md`. If no E2E is warranted, record `N/A` with the coverage-decision evidence instead of command output.
16. Review the interactive scripts and any E2E tests used in this phase for fixed waits and record the files inspected plus the result. If no E2E test was used, record `N/A` for E2E test inspection.
17. Update `task-workflow/open-gaps.md` for every E2E coverage gap closed, defended, or still open.
18. Update `task-workflow/progress.md` with a pointer to `task-workflow/phase-6-e2e-verification.md` for E2E-file and E2E-repair details, removed-test rationale, command results summary, fixed-wait review state, coverage gaps, artifact pointer updates, and next local action.
19. Replace all `open-gaps.md` placeholder rows with real rows or explicit `None currently recorded` rows.
20. Record the E2E coverage decision matrix, connected existing E2E tests inspected for every changed workflow, old-agent/excess-E2E pruning decision, E2E tests removed, E2E tests updated, E2E tests added, New E2E Burden Ledger, commands, exact command output evidence, production/live database non-use proof, outcomes, E2E-selection/retry evidence, fixed-wait review evidence, and remaining coverage gaps. If no E2E is warranted, record `N/A` with the reason and do not create an E2E test.
21. After the Phase 6 gate passes, set `task-workflow/CURRENT_PHASE.txt` to `phase-7-final-signoff`.
22. Re-read `references/phase-5-7-verification-signoff.md` before doing Phase 7 work.
23. Update `task-workflow/progress.md` so current phase, current phase reference, and next local action match Phase 7.

## E2E Coverage Decision

<e2e_coverage_decision>

Prefer no E2E change unless durable E2E coverage is warranted. Use this decision order for every changed workflow: decide whether E2E is warranted; inspect connected existing E2E; remove unnecessary existing E2E; update connected existing E2E when it can carry the warranted workflow; add a new minimal E2E only when no existing E2E can carry a warranted core/complex workflow; otherwise record `N/A`.

> Strict default: no new E2E. A task-provided smoke checklist is not automatic permission to add a new E2E file; first decide whether the checklist is already covered by existing E2E, Phase 5 Playwright evidence, or a smaller update to an existing flow.

### Decision Order

| Step | Action |
| --- | --- |
| 1 | decide whether E2E is warranted for a core, critical, complex, persistence, navigation, permission, or high-risk workflow |
| 2 | inspect connected existing E2E tests before adding anything new |
| 3 | remove unnecessary, obsolete, duplicated, brittle, convoluted, or non-core/non-complex E2E tests |
| 4 | update an existing E2E test when it already owns the workflow |
| 5 | add one minimal new E2E test only when existing coverage cannot carry a warranted workflow |
| 6 | record `N/A` when E2E is not warranted |

### New E2E Burden Ledger

Before adding any new E2E file or case, record a burden ledger entry in `task-workflow/phase-6-e2e-verification.md`.

| Required proof | Meaning |
| --- | --- |
| Critical/core workflow | The case protects a real user journey, persistence/navigation boundary, permission boundary, or high-risk regression. |
| Existing-E2E inventory | Specific connected E2E specs were read, not merely searched. |
| Existing-first rejection | The artifact explains why updating, removing, or preserving an existing E2E cannot carry the warranted path. |
| Minimal path | The case proves the fewest user steps needed for the durable risk; visual, incidental, copy, class, and existence-only assertions are excluded. |
| Bulk check | More than one new E2E case or any new E2E file requires per-case proof that cases cannot be merged or moved into an existing spec. |

If this ledger is missing, generic, or says the test was added because it "locks behavior", "matches the smoke checklist", "adds confidence", or "reviewer may expect it", the E2E is not warranted.

### Command Scope

When E2E is warranted, choose the smallest E2E proof that protects the behavior:

- targeted E2E for one affected critical or complex user flow
- new, changed, or directly connected E2E specs only by default
- multi-spec E2E only when multiple changed or adjacent flows must be protected together
- full Playwright E2E only when the task explicitly asks for full E2E or a concrete written repo instruction names full E2E/all-spec execution for this exact task; do not run it for confidence, final signoff, reviewer-satisfaction, state discovery, suspected pre-existing/order-dependent failures, because many specs appear relevant, or because the repo has one E2E spec file containing many tests. Diagnose those cases with the narrow failing spec/test plus logs, DOM/state, trace, screenshot, or persisted data evidence.
- remove an existing E2E test when it is unnecessary, obsolete, duplicated, brittle, convoluted, or protects a non-core/non-complex flow; old agent-created tests are not grandfathered
- update an existing E2E test when warranted behavior modifies or extends an existing user workflow
- add a new E2E test only for a genuinely core workflow or when existing E2E coverage cannot cleanly express the warranted path
- E2E tests for user-visible multi-step flows

### Assertion Quality

E2E coverage must protect actual core task functionality. Prefer assertions that prove a user-visible outcome, persisted state, navigation result, saved record, validation behavior, permission behavior, or end-to-end data flow. Avoid tests whose main value is checking superficial styling, color, class names, incidental copy, or whether a button exists without proving a critical workflow works.

When updating an existing E2E test, keep its original regression value. The updated test must prove existing functionality still works and that the new or changed behavior integrates with that flow.

Do not add flaky one-off assertions just to claim coverage. A useful E2E test should fail when the task's real user workflow breaks and should remain stable when harmless styling or layout details change.

If no E2E coverage is warranted, record the reason. If warranted coverage is not practical, record the reason, risk, and remaining manual proof. Do not use either exception for convenience.

</e2e_coverage_decision>

## Phase 6 Score

Score `task-workflow/phase-6-e2e-verification.md` against `30` items:

- `8` coverage-decision items
- `8` meaningful functional assertion items
- `6` E2E execution or `N/A` coverage-decision items
- `4` failure-fix/rerun items
- `4` coverage-gap documentation items

Critical failures:

- changed critical/core workflow has no E2E coverage and no defensible reason
- connected existing-E2E inspection/action evidence is missing before a new E2E test is added
- new E2E test added when an existing E2E flow should have been updated instead
- new E2E test added without a complete burden ledger proving critical/core workflow, existing-E2E inventory, existing-first rejection, minimal path, and bulk reduction
- existing functionality affected by the task is not protected by the updated or affected E2E run
- new/updated tests do not prove actual task functionality, persisted state, navigation result, validation behavior, or end-to-end data flow
- tests are primarily superficial checks such as color, CSS class, incidental copy, or button existence without proving feature behavior
- E2E test added for a small, visual-only, incidental, or non-core change without a concrete risk reason
- unnecessary, obsolete, duplicated, brittle, convoluted, or non-core/non-complex E2E test remains after Phase 6 identifies it as removable
- connected old agent-created E2E tests are preserved without a remove/update/preserve decision and reason
- E2E removal lacks reason, diff/readback evidence, or effect on remaining critical-flow coverage
- tests depend on brittle implementation details instead of user-visible or persisted outcomes
- warranted E2E test added but not run
- Playwright/E2E command bypasses `task-workflow/scripts/playwright-lifecycle.mjs` before a diagnosed helper failure or a recorded pre-command reason that repo `webServer` ownership is required for that exact command
- first E2E command depends on an assumed existing server instead of establishing helper/repo lifecycle ownership
- Playwright/E2E command uses manual cleanup, fixed `sleep`, DB-delete, or server-start command chains instead of lifecycle `--setup` plus managed server/run steps before a diagnosed helper failure
- any Playwright/E2E/script/helper command sets `E2E_DATABASE_FILE_PATH`, `DATABASE_PATH`, `DB_PATH`, or any similar database file/path override instead of using repo-owned E2E/end-to-end config
- any Playwright/E2E/end-to-end fixture setup, reset, seed, migration, direct SQLite access, cleanup, inspection-with-write-risk, or custom script points at `.dbs/database.db` or any equivalent production/live default user-data DB
- reviewer or artifact treats a database-path violation as ignorable because it appears in `task-workflow/`, is "only local", or is "only sandbox"; workflow artifacts that mutate sandbox state are runtime-critical and train agents to destroy live data
- any production/live database write occurs outside the app's required migration command for a real schema change, in the owning phase, with explicit migration evidence
- first-run targeted Phase 6 E2E uses a timeout above `30000` ms without a task-specific artifact reason
- Phase 6 timeout is increased after useful failure evidence, or after timer-only/no-output failure without recorded helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage proving the app and spec are valid to rerun
- timeout/quiet-run triage is missing from the Phase 6 artifact after any timed-out, quiet, or longer-rerun command
- unfiltered full Playwright/E2E suite is run without an explicit task request for full E2E or a concrete written repo instruction naming full E2E/all-spec execution for this exact task
- unfiltered full Playwright/E2E suite is run after targeted/connected E2E already passed and no related code, test, config, fixture, migration, or build input changed
- repeated DB reset/migrate/seed or server restart is used between related E2E commands without a recorded invalidating state change or lifecycle diagnostic
- E2E tests are rerun only for confidence, or the same failing E2E command is rerun blindly without material implementation, test, config, environment, output-staleness, or diagnostic reason
- `playwright install` or equivalent browser download attempted during E2E verification
- relevant E2E failure caused by this task remains unresolved
- artifact records a pass for a required E2E run without command evidence
- artifact records a pass for a required E2E run with only a described or documented result and no exact command output or cited repo-local log containing exact output
- existing E2E tests deleted without replacement critical-flow coverage or written defense
- audited Playwright or E2E files contain any fixed wait
- fixed-wait review not recorded
- fixed-wait review finds any occurrence in `task-workflow/playwright` or `tests/e2e`
- E2E coverage gaps remain stale in `task-workflow/open-gaps.md`
- `task-workflow/open-gaps.md` still contains template placeholder rows

Pass gate:

- score is at least `24/30`
- every critical E2E item passes, or no E2E command was warranted and the `N/A` decision is defended
- E2E coverage decision is recorded, including `N/A` when no E2E is warranted
- connected existing E2E tests were inspected before remove/update/add/`N/A` decisions
- existing E2E tests are updated or removed when warranted by the coverage decision
- new E2E tests are added only when existing coverage cannot cleanly cover the core/complex workflow
- new E2E tests, if any, have a complete burden ledger and minimal path proof
- connected old or excessive E2E tests were removed, simplified, updated, or explicitly defended
- new or affected critical behavior has E2E coverage or a documented reason why not
- tests assert meaningful functional outcomes rather than superficial style or existence checks
- required E2E runs pass, no E2E was warranted, or remaining failures are unrelated and evidenced
- E2E command selection and retry evidence is recorded
- exact E2E command output is recorded in the artifact or in a cited repo-local log file when a command was required; otherwise the `N/A` decision is recorded
- E2E coverage gaps in `task-workflow/open-gaps.md` are resolved, updated, or defended
- fixed-wait review is recorded and clean
- `task-workflow/open-gaps.md` has no placeholder `Pending` rows

If this gate fails, stay in Phase 6.

## Phase 7: Final Audit And Signoff

1. Set `task-workflow/CURRENT_PHASE.txt` to `phase-7-final-signoff`.
2. Confirm this reference is loaded as the required current phase reference before Phase 7 work starts.
3. Re-read every phase artifact.
4. Confirm every previous gate passed and remains current.
5. Confirm `task-workflow/open-gaps.md` has no unresolved critical gap.
6. Confirm no open gap is stale or contradicted by Phase 5, Phase 6, or test evidence.
7. Confirm `task-workflow/open-gaps.md` has no placeholder `Pending` rows.
8. Re-read `task-workflow/progress.md` and confirm it matches `CURRENT_PHASE.txt`, every phase decision, the gap ledger, Current Phase Pointers, Phase Artifact Index, Artifact Pointers, and the next local action.
9. Re-read the fixed-wait review evidence from Phase 5 and Phase 6, re-open the inspected verification files if they changed, and confirm the review is still current.
10. Re-read the screenshot existence audit from Phase 5 and verify every screenshot path cited in Phase 5 still exists.
11. Re-read Phase 4 unit-test evidence and Phase 6 E2E evidence. Confirm each phase records its remove/update/add/`N/A` decision, old/excess test pruning audit, new-test burden ledger when tests were added, exact command output when a command was required, and removal rationale plus diff/readback evidence when tests were removed.
12. Inspect changed app/server source for `console.*` again. Temporary `console.*` used to debug Phase 5 browser/runtime behavior must be removed before Phase 7 signs off; lasting logging must use the repo-approved logging or telemetry path.
13. Record an artifact integrity review by re-opening each phase artifact and checking its decision, score, required evidence, timeout/quiet-run triage where applicable, and consistency with `CURRENT_PHASE.txt`, `progress.md`, and `open-gaps.md`.
14. Review the final diff.
15. Treat Phase 7 as evidence validation for missed work, not as a command rerun phase. Re-run only commands whose owning phase missed the required command, whose earlier proof is missing/incomplete/stale, whose earlier proof was invalidated by later edits or changed test/config state, or whose rerun is explicitly required for this exact task by the task or repo instructions. If unit evidence is missing or invalidated, return to Phase 4; if E2E evidence is missing or invalidated, return to Phase 6. Do not rerun checks, builds, tests, Playwright, or E2E when the owning-phase evidence is current, and do not add full unit/Vitest or full Playwright runs only to feel more confident.
16. Score the final result in all quality categories.
17. Confirm the final implementation follows the task-relevant development rules extracted from `AGENTS.md`.
18. Confirm task completion summary is accurate.
19. Locate the required MITB completed command. Prefer the exact `Completed:` command in `.tasks/task.md`; otherwise use the exact command supplied in the prompt. The expected MITB shape is `node /workspace/mitb/task_complete.mjs --projectId "<projectId>" --taskId "<taskId>" --status completed --summary "<summary>"`.
20. If any Phase 7 audit check fails, do not run the completed command. Set `task-workflow/CURRENT_PHASE.txt` to the earliest failing phase, repair the work, update evidence, rescore, loop forward through the gates, and re-enter Phase 7.
21. Run the completed command only after every prior Phase 7 audit check is clean. Record the exact command and result in `task-workflow/phase-7-final-signoff.md` and `task-workflow/progress.md`.
22. Treat the completed command as the final external task action. Before task completion, verify that required check, lint, build, unit test, E2E test, app server, server probe, browser probe, and verification evidence already exists in the owning phase artifacts, or loop back to the owning phase only for missing, incomplete, stale, or invalidated evidence.
23. Do not synthesize project/task identifiers when `.tasks/task.md` or the prompt already provides the command.
24. Update `task-workflow/progress.md` so the last completed gate is Phase 7, the Current Phase Pointers, Phase Artifact Index, and Artifact Pointers are current, task-completion evidence is recorded, and the only next action is final response.
25. Sign off only when the artifact proves the whole workflow passed and the completed command has run successfully.

## Final Audit Checklist

Confirm:

- every phase artifact exists
- every previous phase decision is `Pass`
- every gate score still satisfies its threshold
- required evidence tables remain intact
- artifact integrity review passes for every phase artifact
- no artifact is mostly template placeholders
- `task-workflow/progress.md` matches Phase 7, has no pending current action, and does not contradict any phase artifact
- no critical open gap remains
- no stale open gap remains
- no `open-gaps.md` placeholder row remains
- Phase 5 and Phase 6 fixed-wait reviews are present and current
- every screenshot path cited in Phase 5 exists and has recorded existence proof
- Phase 4 records exact unit-test command output, defended `N/A`, or removed-test rationale and diff/readback evidence
- Phase 6 records exact E2E command output, defended `N/A`, or removed-test rationale and diff/readback evidence
- Phase 4 and Phase 6 record old/excess test pruning audits and new-test burden ledgers when tests were added
- changed app/server source contains no `console.*` after Phase 5
- final diff matches the task scope
- final implementation follows the task-relevant development rules extracted from `AGENTS.md`
- final quality scorecard is at least `8/10` in every category
- final verification is current after the last source edit
- MITB completed command from `.tasks/task.md` or the prompt was run after every Phase 7 audit check passed
- final response can cite changed files, commands/tests run, and final gate status

## Phase 7 Score

Score `task-workflow/phase-7-final-signoff.md` against `20` items:

- `6` previous-gate-currentness items
- `4` artifact integrity items
- `4` final diff review items
- `4` final verification-currentness items
- `2` final summary and MITB completion-command items

Critical failures:

- any previous phase gate failed or stale
- critical open gap remains
- stale open gap remains after the phase that claimed to resolve it
- `task-workflow/open-gaps.md` still contains template placeholder rows
- fixed-wait reviews are missing, stale, non-clean, or contradicted by files under `task-workflow/playwright` or `tests/e2e`
- Phase 5 cites screenshot paths that do not exist or lack recorded existence proof
- Phase 4 lacks unit-test command output evidence, defended `N/A`, or removed-test rationale and diff/readback evidence
- Phase 6 lacks E2E command output evidence, defended `N/A`, or removed-test rationale and diff/readback evidence
- changed app/server logging review is missing or contradicts repo-approved logging/telemetry rules
- artifact integrity review is missing, incomplete, or records a failing decision, failing score, missing artifact, placeholder gate evidence, or contradiction between artifacts
- Phase 5 or Phase 6 had a timed-out, quiet, or longer-rerun Playwright/E2E command without recorded timeout value and triage evidence
- final implementation violates or fails to verify an extracted `AGENTS.md` development rule
- any final quality category is below `8/10`
- final source edit happened after last relevant verification
- final artifact mostly repeats claims without evidence
- MITB completed command was not run after every Phase 7 audit check passed
- MITB completed command was run before previous phase gates and final audit checks passed
- Phase 7 found a failing check but did not loop back to the earliest failing phase before task completion
- task completion command was synthesized incorrectly when `.tasks/task.md` or the prompt provided the exact command

Pass gate:

- score is `20/20`
- all previous phase gates passed
- all required artifacts exist and remain auditable
- artifact integrity review is recorded and passes for every phase artifact
- final implementation follows the extracted `AGENTS.md` development rules
- no unresolved critical gap remains
- no stale open gap remains
- no open-gap placeholder row remains
- fixed-wait reviews are present and current
- every screenshot cited in Phase 5 exists
- unit-test command output, defended `N/A`, or removed-test rationale and diff/readback evidence is present for Phase 4
- E2E command output, defended `N/A`, or removed-test rationale and diff/readback evidence is present for Phase 6
- changed app/server logging review is current after Phase 5
- every final quality category is at least `8/10`
- final checks and tests are current after the last code change
- MITB completed command was run successfully after all prior final-audit checks passed
- final summary cites the main files changed and verification performed

If this gate fails, return to the failing earlier phase.

## Promotion Rule

The task is complete only when Phase 7 passes.

Before setting `task-workflow/CURRENT_PHASE.txt` to any later verification or signoff marker, re-open all prior phase artifacts through the current phase.

Promotion requirements:

- every prior phase artifact has `Decision: Pass`
- the current phase artifact has `Decision: Pass`
- every required score meets its threshold
- all critical items pass
- no required evidence table is still a template placeholder
- no required gate row still says `Pending`
- `task-workflow/open-gaps.md` has no placeholder `Pending` rows
- `task-workflow/open-gaps.md` has no critical or stale open gap
- fixed-wait review requirements are satisfied for Phase 5 and Phase 6 before final signoff
- screenshot existence proof is satisfied for Phase 5 before final signoff
- unit-test command output, defended `N/A`, or removed-test rationale and diff/readback evidence is satisfied for Phase 4 before final signoff
- E2E command output, defended `N/A`, or removed-test rationale and diff/readback evidence is satisfied for Phase 6 before final signoff
- changed app/server logging review is current after Phase 5
- artifact integrity review is recorded and clean
- verification evidence is current after the last source edit
- `task-workflow/progress.md` is current and agrees with Phase 7 signoff
- MITB completed command has run successfully after the final audit checks passed

If any artifact fails this check, do not advance the marker. Set `task-workflow/CURRENT_PHASE.txt` to the earliest failing phase and continue there.

Do not ask the user whether to continue between Phase 5, Phase 6, and Phase 7. The gates decide whether to continue, rework, or return to an earlier phase.
