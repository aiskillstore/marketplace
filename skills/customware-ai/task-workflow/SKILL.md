---
name: task-workflow
description: Canonical workflow for a task. Read and follow strictly end to end while working on the task.
---

# Task Workflow

## Strict Instruction Contract

This file is strict implementation instruction, not loose guidance and not optional reference material.

This is the canonical workflow for task execution. It is not one possible way to do the task; it is the required way.

If the Agent reads this skill, it must execute it exactly as written, in order, to the letter.

Required behavior:

- Do not reinterpret the steps.
- Do not reorder the steps.
- Do not skip the steps.
- Do not replace the steps with a simpler approach.
- Do not make assumptions that override this file.
- Do not treat broad similarity, intuition, or prior habits as permission to deviate.

If the Agent is uncertain, it must resolve that uncertainty inside the workflow defined here and not invent its own workflow.
If the skill says to perform a step, gate, checklist, review, or loop, that step is mandatory.
If the skill says a later phase is blocked, the Agent must treat it as blocked.
If the Agent cannot prove a phase passed in the required artifact, it must treat that phase as failed.

There is no successful stopping point before Phase 7. Stopping early can directly harm the user because they may depend on the completed workflow for job-critical work. It is a do-or-die situation: the user can be harmed if the run has not reached Phase 7 correctly, and the user can lose his job if the Agent stops early, signs off weak work, skips a gate, or damages live data. Treat premature stopping, partial signoff, live-data damage, or "mostly done" summaries as a serious failure of duty.

The first filesystem action in the target repo must be Phase 0 artifact reset and scaffolding.

Before `task-workflow/phase-0-artifact-reset.md` exists, the Agent may only:

- identify the target repo root
- read this `SKILL.md`
- read the task file
- create or replace `task-workflow/` artifacts from templates

Before Phase 1 passes, the Agent must not edit or generate implementation files, build outputs, databases, route types, migrations, tests, package files, or source files.

Production and live workspace databases, especially `.dbs/database.db`, are do-or-die user data. Deleting, resetting, reseeding, truncating, inspecting with ad hoc writes, or modifying them outside the app's legitimate migration command can destroy user work and can cause the user to lose his job. The only permitted production/live DB action is the repo's required app migration command for a real schema change. That exception does not permit "working on" the production DB: no manual query, data manipulation, seed, reset, fixture load, data repair, cleanup, delete, truncate, direct SQLite command, or debug mutation is allowed.

After Phase 1 passes and before any implementation edit, the Agent must set `task-workflow/CURRENT_PHASE.txt` to `phase-2-execution`.

If `CURRENT_PHASE.txt` still says `phase-0-artifact-reset` or `phase-1-task-research`, implementation files must remain unchanged.

If implementation files, generated app files, build outputs, or database files are changed before Phase 0 artifacts exist and Phase 1 passes, the run has failed and must be restarted from a clean fixture.

## Core Idea

Re-read this `SKILL.md` after every compaction before continuing work. Re-load the phase references and current task artifacts too. Do not rely on conversational memory.

This skill is a gated execution protocol, not a loose set of suggestions. It turns a task into a repeatable, artifact-driven workflow. The target app must be implemented from the task, target repo, and local codebase evidence, then proven through Phase 3 check/lint evidence, Phase 4 unit-test coverage decision, Phase 5 interactive Playwright verification, Phase 6 E2E coverage decision, and final audit.

Assume this skill may run fully autonomously and may be compacted mid-run. No human is expected to watch the run line by line. The artifact files are therefore the enforcement system. A phase is not complete because the Agent feels confident. A phase is complete only when its required artifact shows a real passing score and all critical items pass.

`task-workflow/progress.md` is the compact resume ledger. It must summarize the task, current phase, completed phase context, active work queue, verification state, and next local action. Hard rule: after compaction, resume, retry, reconnect, or new coding session, read it and `task-workflow/CURRENT_PHASE.txt` before doing any new work. Keep it current as work proceeds; it is the first file that should restore enough context to continue without conversation memory.

Never promote work from one phase to the next on optimism, partial evidence, a green build alone, or broad product similarity.

The workflow is intentionally looped. A failed gate means the Agent must rework that phase, update evidence, rerun the needed checks or verification, rescore the gate, and repeat until the gate passes. Quality gates are not reports to the user; they are control points that force more work before promotion.

## MITB Workspace Inputs

When running in a MITB sandbox, use these repo-relative workspace inputs:

- workflow skill: `.agents/skills/task-workflow/SKILL.md`
- task body: `.tasks/task.md`
- domain and brand context: `.tasks/domain.md`
- attached task files: `.tasks/files/`
- available skill files: `.agents/skills/`

`AGENTS.md` is the target repo's binding development-instructions file. It defines project-specific rules for architecture, type safety, tests, UX, commands, code style, docs, prohibited patterns, and completion. Phase 1 must extract the task-relevant rules from `AGENTS.md` before planning edits, including any required docs it points to. Later gates must verify the implementation follows those extracted rules.

Phase 1 must read `.tasks/domain.md`. It must enumerate `.tasks/files/` even when the folder is empty, then read or inspect every task attachment/supporting file in that folder before planning.

Available skills are kept under `.agents/skills/`. Discover available skills from the prompt's Skills section and `.agents/skills/`, then read only the selected skill `SKILL.md` files relevant to the current task. Do not bulk-read every skill file in `.agents/skills/`.

All Phase 1 input/reference files are read-only. This includes `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, every file under `.tasks/files/`, and every selected skill file under `.agents/skills/`. Treat files under `.tasks/` as canonical task inputs, not editable workspace artifacts. Do not rewrite, normalize, consolidate, clean up, trim, reformat, or "fix" these files unless the task explicitly asks to update that exact reference file. If a reference file appears inconsistent, record the ambiguity in `task-workflow/phase-1-task-research.md` or `task-workflow/open-gaps.md`; never resolve it by editing the reference input.

Record every `.tasks/files/` attachment/supporting file read or inspected, plus every selected skill path and why it was relevant, in `task-workflow/phase-1-task-research.md` and `task-workflow/progress.md`. After compaction or resume, re-read the selected relevant skill files listed in `progress.md` along with `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, and the relevant `.tasks/files/` attachments/supporting files recorded in Phase 1.

In MITB, `.tasks/task.md` or the prompt always provides the task completion command. Phase 7 must run the exact completed command only after every Phase 7 audit check passes. If any Phase 7 audit check fails, do not run task completion. Return to the earliest failing phase, repair the work, update evidence, rescore that phase, loop forward through the gates, and then re-enter Phase 7.

## Mandatory Process Shape

<mandatory_process_shape>

This workflow shape is not optional:

1. Clear old workflow artifacts for this repo and copy fresh artifact templates.
2. Read the task, root `AGENTS.md`, `.tasks/domain.md`, every task attachment/supporting file in `.tasks/files/`, only relevant available skill files from `.agents/skills/`, and relevant project docs. Extract the task-relevant development rules from `AGENTS.md` before planning. These instruction, task, domain, attachment, and skill-reference files are read-only unless the task explicitly asks to edit them.
3. Research the codebase and record the implementation plan.
4. Execute the primary implementation.
5. Execute a second gap-closure pass.
6. Run second-pass integrity review and repo check/lint validation.
7. Make the unit-test coverage decision: add, update, remove, or explicitly skip unit tests.
8. Verify interactively with standalone Playwright scripts.
9. Make the E2E coverage decision: add, update, remove, or explicitly skip E2E tests.
10. Recheck every phase artifact and sign off only when all gates pass.

If the work skips one of those phase boundaries, the run is off track.

### Phase Ownership Matrix

| Phase | Owns | Required evidence |
| --- | --- | --- |
| Phase 0 | artifact reset and scaffold | fresh artifacts, helper scripts, marker, no source edits |
| Phase 1 | task intake and research | task/domain/attachments/AGENTS/selected skills read, codebase research, implementation plan |
| Phase 2 | primary implementation | scoped work packets, file evidence, readback/diff/search proof |
| Phase 3 | second execution, integrity, check/lint validation | connected-surface review, repo check, focused lint when useful, build, reusable build evidence |
| Phase 4 | unit-test coverage decision | add/update/remove/skip decision, existing-test inspection, minimal unit command or `N/A` |
| Phase 5 | interactive Playwright verification | Stage 1 behavior proof, Stage 2 UI/responsive proof, screenshots, lifecycle evidence |
| Phase 6 | E2E coverage decision | add/update/remove/skip decision, connected E2E inspection, minimal E2E command or `N/A` |
| Phase 7 | final audit and signoff | artifact integrity review, current evidence, MITB completion command after audit |

</mandatory_process_shape>

## Looped Gate Contract

Every phase follows the same loop:

1. Re-read the required reference file or files for the phase from the Phase Reference Map.
2. Perform the phase work.
3. Update the phase artifact with concrete evidence.
4. Score the phase against its gate.
5. If the gate fails, stay in the same phase, repair the failing work or missing evidence, and repeat this loop.
6. If the gate passes, write the promotion-lock evidence, advance `task-workflow/CURRENT_PHASE.txt`, and immediately start the next phase.

This loop is mandatory for Phase 0, Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, and Phase 7.

Do not lower a gate threshold to escape the loop.
Do not summarize failure as progress when the next local repair is available.
Do not wait for the user to tell you to continue when the phase can be repaired locally.
Do not move forward with a weak artifact because the implementation "probably works".

The only acceptable end state is Phase 7 passed with every earlier phase still passing. The only acceptable non-Phase-7 stop is a real external blocker that cannot be solved locally and is fully recorded in the current phase artifact and `task-workflow/open-gaps.md`.

## Autonomous Run Contract

<autonomous_run_contract>

Treat these rules as always active.

### Gate And Artifact Rules

- Every phase must end with an objective gate.
- Every gate must be recorded in the phase-owned artifact file.
- Every gate must have both a numeric threshold and critical-item pass requirement.
- If a gate fails, remain in that phase and keep iterating.
- A failed gate means "repair and loop", not "stop and report".
- Successful gates must immediately promote to the next phase when the next phase is locally available.
- `task-workflow/CURRENT_PHASE.txt` is only a resume pointer. It is not proof that earlier phases passed.
- `task-workflow/progress.md` is the compact resume ledger. It is not proof that gates passed, but it must stay current enough to resume the run after compaction.
- After every phase start, meaningful Phase 2 work packet, phase gate result, blocker discovery, and phase promotion, update `task-workflow/progress.md` with the current phase, earliest failing phase if any, last completed gate, next local action, and a compact summary of relevant context.
- Keep the `Current Phase Pointers`, `Phase Artifact Index`, and `Artifact Pointers` in `task-workflow/progress.md` current. They must point to the current phase artifact, current phase reference, and high-signal active files only. Do not duplicate full researched-file, edited-file, Playwright, screenshot, log, or test inventories from phase artifacts into `progress.md`.
- After compaction, resume, retry, reconnect, or new coding session, re-read this `SKILL.md`, `task-workflow/progress.md`, `task-workflow/CURRENT_PHASE.txt`, the current phase artifact, `task-workflow/open-gaps.md`, and the required current phase reference file or files before choosing the next action. If they disagree, inspect the phase artifacts and continue from the earliest failing phase.
- A phase may advance the current phase marker only after its phase-owned artifact has `Decision: Pass`, a passing score, all critical items passing, and no placeholder `Pending` rows in the gate or required evidence sections.
- The current phase marker must be written before work belonging to that phase begins. The marker is not merely cleanup after phase work.
- Before writing the next phase marker, re-open the current phase artifact and verify the promotion lock in writing inside that artifact.
- Immediately after writing a new phase marker, read the required reference file or files for that new phase before doing any work in that phase.
- If `CURRENT_PHASE.txt` points past the earliest failing phase artifact, artifact gates win. Correct `CURRENT_PHASE.txt` back to the earliest failing phase and continue there.
- When filling artifact templates, preserve auditable evidence for every required semantic category. Exact row wording may be condensed only if the same evidence remains clear and scorable.
- `task-workflow/open-gaps.md` is a gate artifact. A later phase may not claim a gap is resolved unless the gap ledger is updated in the same phase.
- A gap cannot remain `Open` after the phase named in its owner or next-action field has passed. If the later phase completed the work, move the gap to `Resolved Gaps`; if the gap is not real, reclassify or close it with evidence.
- `task-workflow/open-gaps.md` must not contain template placeholder rows such as `Pending` after Phase 0. If there are no gaps, replace placeholder rows with explicit `None currently recorded` rows.
- Phase 7 cannot pass while any critical gap remains `Open`, stale, or contradicted by another phase artifact.

### Verification File Rules

- Phase 5 and Phase 6 must review the interactive scripts and E2E tests for fixed waits before passing.
- A fixed wait in `task-workflow/playwright` or `tests/e2e` is a gate failure. Do not justify it. Replace it with deterministic Playwright waits/assertions such as `locator.waitFor(...)`, `expect(locator)...`, `waitForURL(...)`, `waitForResponse(...)`, or persisted-state assertions, then rerun verification.
- Phase 5, Phase 6, and Phase 7 may pass only when their artifacts document that the inspected verification files contain no fixed waits and cite the deterministic waits/assertions used instead.
- If later work reveals missing evidence from an earlier phase, return to that earlier phase, repair it, and re-pass the gate.

### Write And Command Rules

- After every file write, patch, generated-file creation, or artifact update that matters to a gate, perform a readback check before relying on it. Use `sed`, `rg`, `ls`, `git diff`, or the repo's normal inspection command to prove the file exists and contains the intended change.
- If a write/edit tool reports an invalid write, missing file, failed patch, partial output, or uncertain result, stop that work packet, repair the write with a supported edit method, read it back, and only then continue. Do not proceed as if a failed write happened.
- Commands must be bounded. Do not leave long-lived servers, watchers, or interactive commands running in the foreground as the active tool call.
- Production/live workspace databases must never be used as test or verification state. In this skill, "production database" means `.dbs/database.db`, any repo-declared live/default user-data database, or any database path used by the normal app outside an isolated test/E2E config. The only allowed action on `.dbs/database.db` or any production/live database is the repo's required application migration command for a real schema change, run in the phase that owns that migration and recorded as migration evidence. This is a narrow migration-execution exception, not permission to work on the production DB. If the task creates or changes a migration, running the repo's app migration command against the production/live default DB is mandatory after the migration exists and before Phase 3 promotes; the user uses the completed app immediately, so unapplied migrations make the delivered change invisible or broken. No other production/live DB action is allowed: no manual query, data manipulation, seed, reset, fixture, Playwright, E2E, probe, debugging, cleanup, `rm`, truncate, direct SQLite, custom data repair, or data inspection with write risk. If the command might touch production data and the artifact cannot prove it is the repo migration command for a real schema change or an isolated test DB operation, do not run it.
- Outside Phase 5 and Phase 6, if a temporary dev server is needed for an API/runtime probe, use `task-workflow/scripts/server-probe.mjs`. It owns PID capture, readiness, bounded probe commands, runtime logs, and PID-only cleanup. Server readiness is usually 5-10 seconds; use 15-20 seconds as the normal budget and 30 seconds as the maximum startup-readiness limit. Broad process-name cleanup is only for explicit sandbox-owned recovery when PID/port cleanup is impossible and the artifact records why.
- In Phase 5 and Phase 6, the first browser, Playwright, or E2E command that needs a running app must establish lifecycle ownership through `task-workflow/scripts/playwright-lifecycle.mjs` by default. Do not run against an assumed existing server first and then infer that `fetch failed`, stale data, redirects, or wrong build output means manual server management is needed.
- Existing repo E2E tests are not a reason to bypass the helper. Run `pnpm exec playwright test ...` through the helper's `--run` by default. Use native Playwright with repo `webServer` ownership only when the helper cannot own the server for that exact command after a diagnosed reason, and record that reason before running it.
- The helper's `--env` is not a database-path override mechanism. Never set `E2E_DATABASE_FILE_PATH`, `DATABASE_PATH`, `DB_PATH`, or any similar database file/path variable in helper, setup, server, or run commands. The agent must not change the repo's internal E2E/end-to-end database file path. Test database paths must come from the repo's checked-in E2E/end-to-end config or the already-materialized environment. `.dbs/database.db` is the live workspace/production database; production databases must never be used for testing. Using `.dbs/database.db` for Playwright, E2E, fixtures, seed, reset, inspection, cleanup, or debugging is a critical failure even if it appears only in `task-workflow/`. The user can lose his job if this database is deleted or corrupted.
- Expected verification lifecycle pattern: discover the repo-owned setup and server commands from `AGENTS.md`, `package.json`, README/docs, Playwright config, and `tests/e2e` helpers before running Phase 5 or Phase 6. Prefer a repo-owned setup command that prepares isolated E2E/test state by resetting only the test DB, applying test-targeted migrations, and seeding deterministic verification data, plus a repo-owned server command that starts the app against that isolated state. If the target repo has no named scripts for this pattern, simulate the same pattern with the smallest repo-owned/test-only commands and record the mapping before running them; never replace the pattern with production DB writes, raw DB path overrides, or manual cleanup chains.
- Do not compose manual server cleanup, fixed sleep, DB-delete, server-start, and Playwright command chains in Phase 5 or Phase 6. Put pre-server setup such as isolated test DB reset, test migration, test seed, or test database preparation into lifecycle `--setup "..."` for helper-owned runs. Treat setup plus server startup as reusable for the current verification batch: prefer one helper-owned run with the needed script/spec commands, or rerun setup only after code, migrations, fixtures, DB state, build inputs, or the prior setup output changed. Do not repeatedly delete/recreate the DB or restart the server before each targeted script/spec just because another E2E command is next. If cleanup is needed, do it as a separate recorded recovery step before the helper run, then run the helper alone. If server state, database state, port ownership, or build freshness looks wrong, diagnose through the current lifecycle owner logs/readiness first and rerun through that owner after any code/setup fix. If the helper times out or produces no useful output, treat that as lifecycle/setup evidence, inspect `task-workflow/runtime/server.log`, `task-workflow/runtime/setup-*.log`, readiness output, and `task-workflow/runtime/run-*.log`, then change the setup, server command, ready URL, test command, fixture, or diagnostic before rerunning. If the helper fails once or twice with a diagnosed lifecycle/tooling issue after a corrected invocation, record the helper logs and switch to the smallest fallback that can prove the task: repo Playwright `webServer`, explicit PID/port cleanup, or manual server management with captured PID/log/readiness/cleanup evidence. Broad process-name cleanup is only a recorded sandbox recovery after PID/port cleanup is impossible.
- Do not run `playwright install`, `playwright install chromium`, or equivalent browser downloads during task verification. The managed lifecycle helper sets `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` when available and fails early if the project Playwright version does not match the sandbox browser cache.

### Phase-Owned Command Rules

- Phase 2 completes implementation packets with strict artifact, readback, diff, search, and narrow unblock-command evidence. Defer routine check, lint, build, unit/Vitest, E2E, Playwright, and repo combined check commands such as `pnpm run check` to their owning later phases unless a concrete compile/type issue blocks the current packet and is recorded before the command.
- Phase 3 reviews connected places, closes missed implementation gaps, performs implementation integrity review, then owns the ordered check/build checkpoint: repo check, focused lint when useful, and build when the repo has a separate build. Use targeted diagnostics or narrow fix checks only to prove a specific issue group. When a broad check/build command fails, inspect enough output to identify visible issue groups, fix every locally-fixable group before rerunning that broad command, and record only the groups/fixes/rerun reason. Do not rerun a broad command after each tiny fix when other visible issue groups remain. Do not keep huge command logs unless a temporary log is needed for triage; delete temporary full-output logs after extracting issue groups. Record unit/E2E coverage questions for the owning later phase.
- Phase 4 owns unit-test coverage. It decides whether unit, service, component, or integration-style coverage is warranted; then adds, updates, removes, or explicitly skips that coverage. It may remove existing unit tests when they protect non-core, non-complex, obsolete, or convoluted behavior and the artifact explains why removal improves the test suite. Phase 4 does not rerun check, lint, or build when Phase 3 evidence is current.
- Later phases reuse Phase 3 build evidence unless code, config, dependency/build inputs, migrations, generated assets, stale output, or incompatible verification tooling invalidates it. Do not rebuild in Phase 4, Phase 5, Phase 6, or Phase 7 only to prepare, reconfirm, or feel safe.
- Phase 6 owns E2E coverage. It decides whether E2E coverage is warranted; then adds, updates, removes, or explicitly skips that coverage. It may remove existing E2E tests when they protect non-core, non-complex, obsolete, brittle, or convoluted behavior and the artifact explains why removal improves the test suite.
- If unit, E2E, or browser work happens before its owning phase, do not fail the task solely for that timing. Carry the artifact, diff, and command output into the owning phase and make the owning phase's remove/update/add/skip decision current before promotion.

### Minimal Test And Rerun Rules

> Tests are production code. Extra tests are not harmless evidence; they are maintenance load, false confidence risk, and future workflow drag.

Phase 4 and Phase 6 must treat test work as a pruning and minimal-coverage decision, not as a "more tests is safer" step.

| Rule | Required behavior |
| --- | --- |
| Existing tests are not grandfathered | If an older agent added unnecessary, obsolete, brittle, convoluted, duplicated, or non-core tests, the owning phase must remove or simplify them when they are connected to the current changed behavior. |
| New tests are exceptions | Add a new test only after proving the behavior is stable/core and no connected existing test can carry the warranted assertion cleanly. |
| Passing extra tests is not quality evidence | A large passing count does not improve the gate. The gate values necessary coverage, useful assertions, and removal of bad tests. |
| Test bulk is a warning | If added tests cause max-lines, fixture churn, helper churn, slow commands, broad reruns, or new maintenance structure, stop and re-evaluate whether the tests should be merged, reduced, updated in place, or removed. Do not solve self-created test bulk by adding more structure unless the artifact proves every test remains necessary. |
| Every new test needs a burden ledger | For each new unit or E2E test case/file, record the core risk, the connected existing tests inspected, why update/remove/`N/A` was insufficient, why the assertion is minimal, and what cheaper proof was rejected. |

- Keep tests minimal. Prefer the fewest tests that protect core behavior or critical workflows. Too many tests for incidental behavior are a codebase problem, not a quality signal.
- For E2E, run only new, changed, or directly connected specs that are warranted by the Phase 6 decision. Never run the unfiltered full E2E suite unless the task explicitly asks for full E2E or a concrete written repo instruction names full E2E/all-spec execution for this exact task; a repo having a Playwright suite, `webServer`, or "run tests" script is not enough. After warranted targeted or connected E2E evidence passes and no related code, test, config, fixture, migration, or build input changed, do not add a full E2E run as final confidence, final signoff, state discovery, or reviewer-satisfaction evidence.
- For a single targeted Playwright script or E2E spec, timeout increases are not a retry strategy. Start with the smallest practical timeout: `15000`-`20000` ms for Phase 5 launch/page-state/custom-script probes and up to `30000` ms for first-run Phase 6 targeted E2E where Playwright runner startup adds overhead. If the run fails with any useful error, assertion output, not-found state, console/runtime error, route error, fixture/DB miss, or helper diagnostic, use that evidence to diagnose; do not retry with a larger timeout. A larger timeout is allowed only when the first run ended only because the timer expired with no useful response or explanation, and only after helper logs, readiness, URL, not-found/error state, required DB/fixture records, server runtime logs, browser console, and network/page state prove the app and test are in the correct state to run. Only then may one rerun use `60000` ms, and never more than `120000` ms for one targeted script/spec. If a single targeted run needs more than two minutes, stop increasing timeouts; split the verifier or diagnose lifecycle, setup, fixture, page-state, console, network, or test-design failure first.
- Do not rerun tests only for confidence. Rerun when quality evidence can change: related implementation changed, the test changed, config/environment changed, previous output was incomplete/stale, or the next run gathers a narrower diagnostic needed to fix a real failure.
- Before rerunning an identical failing test command, record what changed since the previous run or what new evidence the rerun will collect. If nothing changed and the prior output is complete, inspect logs, DOM/state, traces, screenshots, or persisted data first, then change the implementation, test, command scope, or diagnostic strategy before running again. A suspected pre-existing or order-dependent failure is not a reason to broaden to a full suite; prove it with the narrow failing spec/test plus logs/state/trace evidence, then fix it if it is in scope or record it as an unrelated defended gap.
- Phase 5 and Phase 6 artifacts must record timeout values and any quiet-run/timeout triage before the gate can pass. A first-run targeted Playwright command longer than the Phase 5/Phase 6 budgets, or any longer rerun without recorded timer-only failure plus clean state triage, is a gate failure.
- If a command appears hung or idle and the next workflow action is locally available, stop the command, record the evidence in the current phase artifact or gap ledger, and continue with the bounded recovery path.

### Continuation Rules

- Every phase gate is an internal control point, not a user confirmation checkpoint.
- If a phase gate passes, continue directly into the next phase without asking whether to continue.
- If a phase gate fails, rework the phase, rerun the gate, and keep looping without asking the user for permission to continue.
- The purpose of the gate, redo, verification, and rework loop is to remove the need for user confirmation during execution and let the Agent complete the run autonomously.
- A failed phase artifact is a repair ticket, not a stopping point. Do not leave a phase with `Decision: Fail`, `Score: 0/...`, pending gate rows, or unresolved locally-fixable warnings and then produce a final response.
- If a dependency, launch detail, or local setup issue blocks progress, resolve it with the most direct logical solution that preserves the workflow and continue.
- Do not lower the skill's strictness, skip gates, or change direction because of an environment issue that can be solved inside the target repo or sandbox.
- Do not stop after any phase to summarize progress and ask whether to continue.
- Do not stop after implementation, build, lint, tests, Playwright verification, or E2E work if any later phase is still unpassed and locally available.
- Do not assume the user will catch a shortcut. The Agent must prevent the shortcut itself.

</autonomous_run_contract>

## Final Response Guard

Before producing any final response, stopping message, or ending an OpenCode turn with control returned to the user, run this guard against the artifact files:

1. `task-workflow/CURRENT_PHASE.txt` must be `phase-7-final-signoff`.
2. `task-workflow/progress.md` must say the current phase is `phase-7-final-signoff`, the last completed gate is Phase 7, and there is no next local action except final response.
3. `task-workflow/progress.md` must include current phase pointers, a phase artifact index, and artifact pointers that identify where detailed evidence lives.
4. `task-workflow/progress.md` must not duplicate full file inventories from phase artifacts; it may list only high-signal active files needed for immediate resume.
5. `task-workflow/progress.md` must list the repo-relative instruction/context files to re-read after compaction, including `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, relevant task attachments/supporting files from `.tasks/files/`, and only the relevant available skill files from `.agents/skills/` selected in Phase 1.
6. Every required phase artifact must have `Decision: Pass`.
7. Every required score must meet its threshold.
8. Every gate row must contain concrete evidence instead of `Pending` or template defaults.
9. `task-workflow/open-gaps.md` must have no critical open gaps, no stale open gaps owned by passed phases, and no placeholder rows.
10. Phase 5, Phase 6, and Phase 7 must record fixed-wait review evidence showing the inspected verification files contain no fixed waits.
11. Phase 5 and Phase 7 must record screenshot existence proof for every screenshot path cited in Phase 5.
12. When Phase 4 requires a unit command or Phase 6 requires an E2E command, that phase and Phase 7 must record the exact command output or a repo-local log file containing the exact output plus the final pass/fail lines. When no unit/E2E test is warranted, the owning phase and Phase 7 must record the `N/A` coverage decision. When tests are removed, the owning phase and Phase 7 must record the removal reason and diff/readback evidence.
13. Phase 5, Phase 6, and Phase 7 must record timeout values and timeout/quiet-run triage evidence for every timed-out, quiet, or longer-rerun Playwright/E2E command.
14. Phase 3 and Phase 7 must verify changed app/server source contains no lasting `console.*`. Temporary `console.*` is allowed only during Phase 5 interactive testing when it directly helps debug browser/runtime behavior by reading console output, and it must be removed before the Phase 5 rerun, Phase 3 re-pass, or Phase 7 signoff.
15. Phase 7 final quality scorecard must be at least `8/10` in every category.
16. Phase 7 must record an artifact integrity review that re-opens every phase artifact and verifies the artifact exists, its decision is `Pass`, its score meets threshold, required evidence rows are complete, and it does not contradict `CURRENT_PHASE.txt`, `progress.md`, or `open-gaps.md`.
17. The MITB completed command from `.tasks/task.md` or the prompt must run only after all Phase 7 audit checks pass. Treat it as the final external task action: plan and run all checks, tests, builds, server probes, and verification commands before task completion. If any Phase 7 check fails before completion, the agent must loop back to the earliest failing phase and must not call task completion.

If any item fails and the problem can be solved locally, continue the workflow from the earliest failing phase. Do not answer as if the task is complete.
If an actual external blocker prevents completion, record the blocker in the current phase artifact and `open-gaps.md`, including commands run, files inspected, why local recovery cannot solve it, and the smallest next action.

## OpenCode Turn Continuity Guard

When running inside OpenCode or another tool-driven coding session, the Agent must not end its assistant turn just because a command finished, a check passed, lint started, files were edited, or a phase artifact is temporarily failing.

After every tool result, before returning control to the user, check:

- Is `CURRENT_PHASE.txt` earlier than `phase-7-final-signoff`?
- Does any required phase artifact still say `Decision: Fail`?
- Does the current phase gate still contain `Pending`, `0/...`, or missing evidence?
- Is the next required workflow action locally available?

If the answer to any of the first three is yes and the next action is locally available, immediately continue with that next action in the same run. Do not stop at a narrative checkpoint such as "now run lint", "check passes", "next I will update the artifact", or "remaining work is...".

The only valid stopping states are:

- Phase 7 passed and the final response guard passed.
- A real external blocker is fully recorded in the current artifact and `open-gaps.md`.

If the session is long, keep the phase artifacts current and continue dispatching the next tool/action. Do not rely on the user to type "continue" to finish an unblocked phase.

## Critical Output Invariant

These are hard constraints:

- The target app must be a real interactive app, not a static mockup.
- The implementation must be authored in the target repo as real routes, layouts, components, state, styling, backend contracts, services, queries, migrations, and tests when required by Phase 4 or Phase 6 coverage decisions.
- Primary pages or views must be implemented as real router routes or repo-native route modules, not as an in-memory page-state switch inside one large component.
- Visible controls required or implied by the task must become real target controls with matching states and persisted behavior when persistence is required.
- Backend/data work must follow the repo's existing service, contract, query, and persistence boundaries.
- Frontend runtime code must not import server-only runtime modules.
- Reusable UI styling belongs in shared primitives, component-local styling, or existing design tokens, not fake global one-off component classes.
- Phase 3 check/lint evidence, Phase 4 unit-test work, Phase 5 interactive Playwright verification, and Phase 6 E2E work are separate gates. None is a substitute for another.
- The Agent must review the app part by part, route by route, state by state, and flow by flow.
- If a critical visible action, route, data mutation, or verification path remains fake, broken, or unreviewed, the run has not passed.
- Existing tests must not be deleted merely to make the new task pass. If obsolete tests are removed, replace their useful coverage or document why the old coverage no longer applies.
- Type assertions, broad casts, and warning suppression are not acceptable substitutes for correct contracts and narrowed types.
- Final signoff must score at least `8/10` in each quality category: functional result, skill compliance/artifact integrity, code quality/maintainability, test quality, and overall result.

## Reference Loading Rules

<reference_loading_rules>

Do not load every reference file by default.

### Compaction And Resume Reload Rule

After compaction, resume, retry, reconnect, or a new coding session, use `task-workflow/progress.md` and `task-workflow/CURRENT_PHASE.txt` to identify the current status, then re-read:

1. this main `SKILL.md`
2. `task-workflow/progress.md`
3. `task-workflow/CURRENT_PHASE.txt`
4. the current phase artifact
5. `task-workflow/open-gaps.md`
6. the required reference file or files for the current phase from the Phase Reference Map
7. the repo-relative instruction/context files listed in `progress.md`

Do not rely on conversation memory after compaction. `progress.md` and `CURRENT_PHASE.txt` identify where the run is, but they do not replace the main skill, current phase reference, current phase artifact, or gap ledger. The run may continue only after those files have been reloaded.

### Phase Start Reference Rule

Every time a phase starts, including immediately after a phase promotion, read the required reference file or files for that new phase before doing phase work.

If `CURRENT_PHASE.txt` changes, the next local action is to load the reference file or files named for the new marker in the Phase Reference Map. Phase work before that read is invalid.

On a fresh run:

1. Read this `SKILL.md`.
2. Start Phase 0.
3. Load only `references/phase-0-1-startup-research.md`.

After compaction, resume, retry, reconnect, or new coding session:

1. Re-read this `SKILL.md`.
2. Read `task-workflow/progress.md`.
3. Read `task-workflow/CURRENT_PHASE.txt`.
4. Read the current phase artifact and `task-workflow/open-gaps.md`.
5. Re-read the instruction/context files listed in `progress.md`, including `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, the relevant attachments/supporting files recorded from `.tasks/files/`, and only the selected relevant skill files from `.agents/skills/`.
6. If `progress.md`, `CURRENT_PHASE.txt`, and the phase artifacts disagree, continue from the earliest failing phase artifact.
7. Load only the reference file that owns the current phase.
8. Load `references/playwright-interactive.md` only when the current phase reference requires interactive Playwright work.

Phase reference map:

| Current phase marker | Reference to load |
| --- | --- |
| missing `task-workflow/` | `references/phase-0-1-startup-research.md` |
| `phase-0-artifact-reset` | `references/phase-0-1-startup-research.md` |
| `phase-1-task-research` | `references/phase-0-1-startup-research.md` |
| `phase-2-execution` | `references/phase-2-4-execution-integrity.md` |
| `phase-3-second-execution` | `references/phase-2-4-execution-integrity.md` |
| `phase-4-unit-coverage` | `references/phase-2-4-execution-integrity.md` |
| `phase-5-playwright-verification` | `references/phase-5-7-verification-signoff.md` and `references/playwright-interactive.md` |
| `phase-6-e2e-verification` | `references/phase-5-7-verification-signoff.md` |
| `phase-7-final-signoff` | `references/phase-5-7-verification-signoff.md` |

The phase references are grouped by connected workstream, not one file per phase. This matches the reference skill pattern: `SKILL.md` holds the strict global protocol and the reference files hold detailed process for the current workstream.

</reference_loading_rules>

## Operating Modes

<operating_modes>

### Validation Mode

Use this when improving or testing the skill itself.

- Use a throwaway target repo copy.
- Preserve all workflow artifacts.
- Judge repeatability across fresh runs.
- If the same failure repeats, improve the reusable skill before running again.

### Delivery Mode

Use this when the user wants the real target app or task completed.

- Work inside the provided target repo.
- Treat the task file as the source of truth.
- Do not sign off until every gate in this file and the phase references has passed in writing.

</operating_modes>

## Required Artifacts

These are mandatory:

- `task-workflow/`
- `task-workflow/phase-0-artifact-reset.md`
- `task-workflow/phase-1-task-research.md`
- `task-workflow/phase-2-execution.md`
- `task-workflow/phase-3-second-execution.md`
- `task-workflow/phase-4-unit-coverage.md`
- `task-workflow/phase-5-playwright-verification.md`
- `task-workflow/phase-6-e2e-verification.md`
- `task-workflow/phase-7-final-signoff.md`
- `task-workflow/progress.md`
- `task-workflow/open-gaps.md`
- `task-workflow/CURRENT_PHASE.txt`
- `task-workflow/playwright/`
- `task-workflow/screenshots/`
- `task-workflow/scripts/`
- `task-workflow/scripts/playwright-lifecycle.mjs`
- `task-workflow/scripts/server-probe.mjs`
- `task-workflow/runtime/`

The templates in `assets/templates/` are enforcement artifacts. Copy their structure directly. If a required table is replaced by prose or stripped down until rows are no longer auditable, the run fails.

## Multi-Phase Protocol

<multi_phase_protocol>

Follow the phases in order:

### Phase 0: Artifact Reset And Scaffolding

Delete the previous task's `task-workflow/` artifacts, recreate the required artifact files from templates, and prove no implementation files were edited.

Detailed process: `references/phase-0-1-startup-research.md`.

### Phase 1: Task Intake And Codebase Research

Read the task, root `AGENTS.md`, `.tasks/domain.md`, every task attachment/supporting file in `.tasks/files/`, only relevant available skill files from `.agents/skills/`, relevant docs, and codebase. Treat `AGENTS.md` as binding development instructions; extract its task-relevant rules before planning. These are reference inputs: read and cite them, but do not edit them. Record task understanding, development rules, task files read or inspected, selected skills, affected files, patterns to reuse, risks, and an ordered implementation plan.

Detailed process: `references/phase-0-1-startup-research.md`.

### Phase 2: Primary Execution

Execute the researched plan in order, keep changes scoped, and record implementation evidence.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 3: Second Execution, Integrity, And Check/Lint Validation

Review the implementation as a continuation pass, close missing or weak work, propagate consistency to associated UI/API/data surfaces, run implementation integrity review, and complete the ordered check/build checkpoint. Do not write or run unit/Vitest or E2E tests in Phase 3.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 4: Unit Test Coverage Decision And Verification

Decide whether unit, service, component, or integration-style tests are needed. Add, update, remove, or explicitly skip that coverage, then run only the warranted unit-level commands. Remove tests that are unnecessary, obsolete, convoluted, or protecting non-core/non-complex behavior.

Detailed process: `references/phase-2-4-execution-integrity.md`.

### Phase 5: Interactive Playwright Verification

Use standalone interactive Playwright scripts in two stages. Stage 1 proves the changed behavior works through real user interaction. Stage 2 verifies UI quality: no broken, cramped, overlapping, clipped, ill-placed, or non-responsive UI on the affected surfaces. Treat responsive design as a first-class Phase 5 guarantee, equal to proving the task's functional changes work. Some whitespace is fine, but standard desktop viewports such as `1920x1080` must not look broken, clipped, overlapped, unusable, or excessively sparse. Large desktop viewports such as `2560x1440` may have some extra whitespace, but not broad empty regions that make the UI feel unfinished. Very large 4K/ultrawide whitespace is acceptable when the layout is intentionally constrained and still coherent.

The Phase 4/Phase 6 test-minimality rules do not shrink Phase 5. Phase 5 is the main user-facing verification phase and may take the time needed to cover changed flows, relevant bad cases, surrounding UI, responsive breakpoints, screenshots, and visual correctness. Use multiple focused Playwright scripts, probes, viewport passes, or reruns when needed to prove the affected user experience is correct; keep them scoped to the changed and adjacent surfaces, but do not reduce Phase 5 to a shallow smoke check.

Detailed process: `references/phase-5-7-verification-signoff.md` and `references/playwright-interactive.md`.

### Phase 6: E2E Coverage Decision And Verification

Make the E2E coverage decision. Review existing E2E coverage first, update it when a warranted core flow already belongs there, add new E2E tests only for critical or complex workflows that cannot be cleanly covered by existing tests, remove unwanted E2E tests that protect non-core/non-complex or convoluted flows, and avoid E2E for small, visual-only, or incidental UI changes.

Detailed process: `references/phase-5-7-verification-signoff.md`.

### Phase 7: Final Audit And Signoff

Re-read every artifact, confirm all previous gates still pass after the last edit, review the final diff, run the required MITB completed command only after all Phase 7 audit checks pass, and sign off only if the artifact trail proves completion.

Phase 7 is an evidence validator for missed work, not a validation rerun phase. If a required check, build, test, Playwright run, E2E run, or other phase-owned command was already completed correctly in its owning phase and the evidence is current, Phase 7 must only verify that evidence. Rerun a command only when the owning phase missed the required command, the recorded evidence is missing/incomplete/stale, or later changes invalidated it; otherwise never rerun checks, builds, tests, Playwright, or E2E in Phase 7.

Detailed process: `references/phase-5-7-verification-signoff.md`.

The phase references are not optional expansion material. They are the detailed execution instructions for the current workstream.

</multi_phase_protocol>

## Disallowed Shortcuts And Automatic Fails

<automatic_fails>

These automatically fail the run:

### Phase Boundary And Artifact Fails

- editing app/source files before Phase 1 passes
- editing app/source files before Phase 0 artifacts exist
- editing implementation/source files while `task-workflow/CURRENT_PHASE.txt` still says `phase-0-artifact-reset` or `phase-1-task-research`
- passing Phase 2 while `task-workflow/phase-2-execution.md` does not record that the marker was set to `phase-2-execution` before source edits
- skipping artifact reset
- failing to copy the artifact templates before implementation work
- failing to create, read after compaction, or keep `task-workflow/progress.md` current enough to resume the run
- after compaction, retry, reconnect, or a new coding session, continuing work before using `task-workflow/progress.md` and `task-workflow/CURRENT_PHASE.txt` to identify status, then re-reading `SKILL.md`, the current phase artifact, `open-gaps.md`, and the required current phase reference file or files
- after a phase marker changes, starting work in the new phase before reading the required reference file or files for that phase
- failing to record and re-read the selected repo-relative instruction/context files in `task-workflow/progress.md`, including `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, relevant task attachments/supporting files from `.tasks/files/`, and relevant available skill files from `.agents/skills/`
- reading `AGENTS.md` only as context instead of extracting and following the task-relevant development rules it defines
- editing `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, selected skill files under `.agents/skills/`, or `AGENTS.md` without the user/task explicitly requesting an edit to that exact reference file
- leaving the `task-workflow/progress.md` Current Phase Pointers, Phase Artifact Index, or Artifact Pointers stale, missing, or contradicting phase artifacts
- using `task-workflow/progress.md` as a duplicate file inventory instead of pointing to the owning phase artifacts for details
- omitting required semantic evidence from a phase artifact while claiming that phase passed
- advancing `task-workflow/CURRENT_PHASE.txt` while the current or any previous phase artifact still says `Decision: Fail`
- advancing `task-workflow/CURRENT_PHASE.txt` while the current or any previous phase artifact still has placeholder `Pending` gate evidence
- leaving artifact templates mostly blank while claiming success
- passing Phase 5 while any screenshot path cited in the artifact is missing or not verified with existence proof
- passing Phase 6 while required E2E runs are only described and the exact command output is not recorded in the artifact or in a cited repo-local log file
- running Phase 5 or Phase 6 Playwright/E2E commands without the correct lifecycle owner recorded: helper by default, repo Playwright `webServer` or manual fallback only with a recorded reason/diagnostic made before the command
- deleting, resetting, reseeding, truncating, directly modifying, or using the production/live workspace database as test/verification state; this includes `.dbs/database.db`, repo default user-data DB paths, and any equivalent live DB path
- running any production/live DB action other than the repo's required app migration command for a real schema change; prohibited actions include manual queries, data manipulation, seed, reset, fixture, Playwright, E2E, debug, cleanup, direct SQLite, custom data repair, delete, or truncate against `.dbs/database.db` or any equivalent live DB path
- running a production database migration except as the app's required migration for a real schema change, in the owning phase, with explicit migration evidence
- passing Phase 3 after creating or changing a migration without applying it through the repo's app migration command against the production/live default DB and recording the target, command, reason, and output

### Test Hygiene And Coverage Fails

- adding or requiring unit tests for small fixes, minor UI adjustments, copy changes, color/style changes, spacing/layout tuning, or simple button wiring without a concrete core-behavior or risk reason
- adding unit tests for trivial component branches, incidental button clicks, visual-only changes, or one-off UI behavior instead of reserving unit tests for core stable behavior
- keeping unnecessary, obsolete, convoluted, or non-core/non-complex unit tests after Phase 4 identifies them as removable
- adding unit tests without a per-test necessity ledger proving existing tests could not be updated, the behavior is stable/core, and every new assertion is minimal
- preserving old agent-created unit tests as "already there" when connected evidence shows they are unnecessary, duplicated, brittle, convoluted, or non-core/non-complex
- adding enough unit tests to require test-file splitting, helper churn, fixture churn, or broad reruns without first reducing or removing unnecessary test coverage and recording why the remaining bulk is necessary
- adding a new E2E test for behavior that is not a critical/core workflow, not a complex flow, or can be cleanly covered by updating existing E2E coverage
- keeping unnecessary, obsolete, brittle, convoluted, or non-core/non-complex E2E tests after Phase 6 identifies them as removable
- adding E2E tests without a per-test necessity ledger proving existing E2E could not be updated, the workflow is critical/core or complex enough for E2E, and every new assertion is minimal
- preserving old agent-created E2E tests as "already there" when connected evidence shows they are unnecessary, duplicated, brittle, convoluted, or non-core/non-complex
- starting with a broad/full unit or Vitest suite in Phase 4 before the warranted targeted/connected unit-level tests, when any are warranted, have passed
- running the full unit/Vitest suite more than once without a concrete artifact reason from target repo instructions, changed global/shared infrastructure, or incomplete/stale output
- running broad/full unit or Vitest without Phase 4 artifact evidence that warranted targeted/connected tests already passed and this is the one final sanity check, or that the task/repo/global change explicitly requires the broader scope
- running routine check, lint, or build after every small Phase 2 edit instead of preserving packet evidence and using Phase 3 as the ordered check/build checkpoint
- running repo combined check commands such as `pnpm run check` in Phase 2 without a concrete compile/type blocker recorded before the command
- rerunning check, lint, or build before all visible locally-fixable issue groups from the prior output are fixed; truncated `tail`/`head` output alone is not enough if it hides issue groups, and temporary full-output logs must be deleted after extraction
- rerunning build in Phase 4, Phase 5, Phase 6, or Phase 7 when Phase 3 build evidence is current and no invalidating change is recorded

### Playwright And E2E Command Fails

- running native `pnpm exec playwright test ...` in Phase 6 instead of running it through `task-workflow/scripts/playwright-lifecycle.mjs --run ...`, unless repo `webServer` ownership is required and recorded before the command
- running the unfiltered full Playwright/E2E suite when the task did not explicitly ask for full E2E and no concrete written repo instruction names full E2E/all-spec execution for this exact task
- running `rm`, `seed`, `migrate`, `sqlite3`, `tsx server/db/seed`, fixture setup, or any DB cleanup command from Phase 5/6 unless the artifact first proves the command targets an isolated repo-owned test/E2E database and not production/live user data
- starting a first-run targeted Phase 5 Playwright script above `20000` ms or a first-run targeted Phase 6 E2E above `30000` ms without a task-specific artifact reason
- increasing a Playwright/E2E timeout after any useful failure evidence, or increasing it after a timer-only/no-output failure without recorded helper-log/readiness/URL/DB-fixture/server-log/browser-console/network/page-state triage proving the app and test are valid to rerun
- rerunning tests only for confidence, or blindly rerunning the same failing test command without recording a material implementation, test, config, environment, output-staleness, or diagnostic reason
- running `playwright install`, `playwright install chromium`, or equivalent browser downloads during task verification instead of using the sandbox browser cache or recording the helper's browser-preflight mismatch

### Continuity And Evidence Fails

- passing Phase 3 or Phase 7 while changed app/server source still contains `console.*` outside the active Phase 5 debug loop
- producing a final response or stopping summary while `CURRENT_PHASE.txt` is before `phase-7-final-signoff`
- producing a final response or stopping summary while any required artifact still says `Decision: Fail`, has a failing score, or contains pending gate evidence
- ending an OpenCode turn mid-phase while the next workflow action is locally available
- editing Phase 2 source files while `task-workflow/phase-2-execution.md` execution log remains blank or all `Pending`
- completing multiple Phase 2 implementation packets before updating their execution-log rows with file evidence
- replacing evidence tables with prose
- skipping the second execution pass
- treating Phase 3 check/lint evidence as a substitute for Phase 4 unit-test coverage decisions, Phase 5 interactive Playwright verification, or Phase 6 E2E coverage decisions
- treating Playwright verification as a substitute for warranted Phase 4 or Phase 6 test work
- running Phase 5 interactive Playwright verification or Phase 6 E2E coverage work as a substitute for completing the Phase 2 gate
- leaving a long-lived dev server, watcher, or interactive command in the foreground until the session stalls
- relying on a file write or patch without readback evidence when the file matters to a gate
- continuing after a failed, invalid, or uncertain write result without repairing and rereading the target file

### Final Signoff Fails

- signing off while critical open gaps remain
- signing off while `task-workflow/open-gaps.md` contains stale open gaps that a passed later phase claims to have resolved
- signing off while `task-workflow/open-gaps.md` still contains template placeholder rows such as `Pending`
- passing Phase 5, Phase 6, or Phase 7 without recorded fixed-wait review evidence
- passing Phase 5, Phase 6, or Phase 7 while fixed waits remain in `task-workflow/playwright` or `tests/e2e`
- passing Phase 7 without a recorded artifact integrity review of every phase artifact
- signing off while any final quality scorecard category is below `8/10`
- deleting existing tests without equivalent replacement coverage or a written artifact defense
- using broad unsafe casts or warning suppression to bypass the type system without a narrow evidence-backed reason
- relying on conversation memory after compaction instead of using `progress.md` and `CURRENT_PHASE.txt` for status and re-reading this skill, required phase reference files, and artifacts
- failing to enumerate `.tasks/files/` even when it is empty
- failing to read or inspect every task attachment/supporting file in `.tasks/files/` before Phase 1 planning
- bulk-reading every skill file in `.agents/skills/` instead of selecting and reading only task-relevant skills
- planning, implementing, verifying, or signing off work that violates the extracted `AGENTS.md` development rules
- running a MITB task completion command before all Phase 7 audit checks pass
- failing to loop back to the earliest failing phase when any Phase 7 audit check fails
- failing to run the required MITB completed command after all Phase 7 audit checks pass
- asking the user whether to continue between phases when the next phase is unblocked

</automatic_fails>

## Reference Map

- `references/phase-0-1-startup-research.md`: artifact reset, template copying, task intake, and codebase research.
- `references/phase-2-4-execution-integrity.md`: primary execution, second execution, gap closure, and integrity checks.
- `references/phase-5-7-verification-signoff.md`: interactive Playwright verification, E2E coverage decisions, and final audit.
- `references/playwright-interactive.md`: how this skill uses standalone interactive Playwright scripts.
- `assets/templates/phase-0-artifact-reset.md`
- `assets/templates/phase-1-task-research.md`
- `assets/templates/phase-2-execution.md`
- `assets/templates/phase-3-second-execution.md`
- `assets/templates/phase-4-unit-coverage.md`
- `assets/templates/phase-5-playwright-verification.md`
- `assets/templates/phase-6-e2e-verification.md`
- `assets/templates/phase-7-final-signoff.md`
- `assets/templates/progress.md`
- `assets/templates/open-gaps.md`
- `assets/scripts/playwright-lifecycle.mjs`: managed server/readiness/Playwright execution helper copied into `task-workflow/scripts/` during Phase 0.
- `assets/scripts/server-probe.mjs`: managed API/runtime server probe helper copied into `task-workflow/scripts/` during Phase 0 for pre-Phase-5 server checks.

## Non-Negotiables

- Use the phase gates exactly.
- Keep the artifacts auditable.
- Return to earlier phases when evidence is weak.
- Do not edit source files before Phase 0 and Phase 1 gates pass.
- Do not sign off before interactive Playwright verification and regression test gates pass.

## Completion Standard

The task is complete only when Phase 7 passes.
If the task cannot be completed, the final artifact must identify the exact blocking condition, the phase where it occurred, commands run, files inspected, and the smallest next action needed.
