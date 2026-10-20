# Startup And Research

Use this reference for Phase 0 and Phase 1.

These phases establish the task workspace and produce the accepted implementation plan. They are internal gates, not user confirmation points. When a gate passes, continue automatically. When a gate fails, repair the phase and rerun the gate automatically.

This is a looped gate workstream: Phase 0 and Phase 1 are not complete until their artifacts pass their gates. A failing score, missing evidence, stale placeholder, or blocked promotion means stay in the same phase, repair the work, update the artifact, rescore, and repeat. Do not stop or ask the user to continue when a local repair is available.

## Startup Authority

<startup_authority>

The artifact trail is the source of truth for the run.

Phase 0 exists so a new task never inherits stale proof from an older task. The agent owns artifact creation directly by copying templates from `assets/templates/` and the managed lifecycle helpers from `assets/scripts/`; no scaffold script is required.

`task-workflow/progress.md` is the compact resume ledger. It must be reset with the rest of `task-workflow/`, copied from template, and updated in Phase 0 before promotion. Hard rule: after compaction or resume, use `progress.md` and `CURRENT_PHASE.txt` to identify current status, then read `SKILL.md`, `open-gaps.md`, the current phase artifact, and the required current phase reference before choosing the next action.

At every phase start or promotion, read the required reference file or files for the new `CURRENT_PHASE.txt` marker before doing phase work. Phase 0 and Phase 1 both use this reference.

### MITB Inputs

When running in MITB, use repo-relative inputs from the target repo:

- task body: `.tasks/task.md`
- domain and brand context: `.tasks/domain.md`
- attached task files: `.tasks/files/`
- available skill files: `.agents/skills/`
- workflow skill: `.agents/skills/task-workflow/SKILL.md`

### Required Reads

`AGENTS.md` is the target repo's binding development-instructions file. It controls project-specific architecture, type safety, test expectations, UX standards, commands, code style, docs, prohibited patterns, and completion rules. Extract the task-relevant rules from it before planning, and read any docs it explicitly requires for the task.

Phase 1 must enumerate `.tasks/files/` even when it is empty and read or inspect every task attachment/supporting file before planning. Available skill files are stored under `.agents/skills/`: select and read only relevant skill `SKILL.md` files from `.agents/skills/`. Do not bulk-read every skill file under `.agents/skills/`.

### Read-Only Inputs

The Phase 1 inputs are read-only. `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, selected skill files under `.agents/skills/`, and other reference files must be read, cited, and summarized only. Do not write to them. Do not rewrite, normalize, consolidate, trim, clean up, reformat, or "fix" these files. This is especially strict for files under `.tasks/`: they are canonical MITB task inputs, not workflow artifacts. If they conflict or look stale, record the issue in the Phase 1 artifact or `open-gaps.md` and keep going from the safest interpretation.

### Source-Edit Boundary

Do not inspect implementation files in app, server, tests, packages, src, or equivalent source directories before Phase 0 artifacts exist.
Do not edit implementation files before Phase 1 passes.
Do not generate build outputs, route typegen, databases, migrations, or source artifacts before Phase 1 passes.
Do not edit implementation files after Phase 1 passes until `task-workflow/CURRENT_PHASE.txt` says `phase-2-execution`.
When filling phase artifacts, keep evidence auditable. If a template row is condensed, the same semantic evidence must still be present.

</startup_authority>

## Phase 0: Artifact Reset And Scaffolding

Phase 0 is the first action after reading `SKILL.md`.

1. Identify the target repo root.
2. Delete only the existing `task-workflow/` directory in the target repo. Treat it as stale previous-task state; do not reuse old artifacts for the new task.
3. Recreate:
   - `task-workflow/`
   - `task-workflow/playwright/`
   - `task-workflow/screenshots/`
   - `task-workflow/scripts/`
   - `task-workflow/runtime/`
   - `task-workflow/CURRENT_PHASE.txt`
4. Copy the templates from `assets/templates/` into `task-workflow/`:
   - `progress.md`
   - `phase-0-artifact-reset.md`
   - `phase-1-task-research.md`
   - `phase-2-execution.md`
   - `phase-3-second-execution.md`
   - `phase-4-unit-coverage.md`
   - `phase-5-playwright-verification.md`
   - `phase-6-e2e-verification.md`
   - `phase-7-final-signoff.md`
   - `open-gaps.md`
5. Copy managed helper assets into `task-workflow/scripts/`:
   - `assets/scripts/playwright-lifecycle.mjs` to `task-workflow/scripts/playwright-lifecycle.mjs`
   - `assets/scripts/server-probe.mjs` to `task-workflow/scripts/server-probe.mjs`
6. Set `task-workflow/CURRENT_PHASE.txt` to `phase-0-artifact-reset`.
7. Fill `task-workflow/phase-0-artifact-reset.md` with:
   - repo root
   - task file or task source
   - skill path
   - reset evidence
   - copied template evidence
   - copied lifecycle helper evidence
   - marker before promotion: `phase-0-artifact-reset`
   - confirmation that no implementation files were edited
8. Fill `task-workflow/progress.md` with the task source, current phase, Phase 0 reset summary, seeded Resume Instructions, seeded Refs for `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, the task attachment location, the `.agents/skills/` location, Current Phase Pointers, Phase Artifact Index, Artifact Pointers, and next local action.
9. After every other Phase 0 gate row passes, set `task-workflow/CURRENT_PHASE.txt` to `phase-1-task-research`.
10. Re-read this required reference for Phase 1 before doing Phase 1 work.
11. Update `task-workflow/progress.md` so current phase, current phase reference, and next local action match Phase 1.
12. Re-open `task-workflow/phase-0-artifact-reset.md`, record marker after promotion as `phase-1-task-research`, then mark the Phase 0 decision.

## Phase 0 Score

Score `task-workflow/phase-0-artifact-reset.md` against `10` items:

- `2` previous-task artifact reset items
- `4` required artifact and resume-ledger items, including the phase marker, progress ledger, and hard resume rule
- `2` required directory creation items
- `1` task and repo identity item
- `1` no-source-edit discipline item

Critical failures:

- any implementation file edited before Phase 0 passes
- any build output, route typegen, database, migration, test output, or source artifact generated before Phase 1 passes
- old previous-task `task-workflow/` reused instead of reset
- missing required artifact file
- missing `task-workflow/scripts/playwright-lifecycle.mjs`
- missing `task-workflow/scripts/server-probe.mjs`
- missing or stale `task-workflow/progress.md`
- Phase 0 artifact does not record the progress-ledger hard resume rule
- copied templates replaced by loose prose
- `CURRENT_PHASE.txt` missing or wrong after the gate

Pass gate:

- score is `10/10`
- all required artifacts exist
- old previous-task workflow artifacts were cleared
- no app/source files were edited
- marker before promotion was `phase-0-artifact-reset`
- marker after promotion is `phase-1-task-research`

If this gate fails, stay in Phase 0.

## Phase 1: Task Intake And Codebase Research

1. Set `task-workflow/CURRENT_PHASE.txt` to `phase-1-task-research`.
2. Read the complete task body. In MITB, `.tasks/task.md` is the canonical task workspace and may include completion commands; read it even if the prompt also includes the task text.
3. Immediately read the target repo root `AGENTS.md` as binding development instructions. Extract task-relevant rules for architecture, type safety, tests, UX, commands, code style, docs, prohibited patterns, and completion.
4. Read `.tasks/domain.md`. This is the MITB domain and brand context. Also discover and read other repo-local domain files only when they are relevant to the task.
5. Enumerate `.tasks/files/`, even if it is empty.
6. Read or inspect every task attachment/supporting file in `.tasks/files/` before planning. For binary or media files, use the appropriate local inspection method and record what was learned; do not treat a directory listing as reading the file.
7. Discover available skill files from the prompt's Skills section and `.agents/skills/`.
8. Select only task-relevant skills. Use the task description, domain file, prompt-provided skill descriptions, and filenames or directory names inside `.agents/skills/` to choose candidates. If metadata is needed, inspect lightweight metadata for candidates, then read only selected relevant skill `SKILL.md` files from `.agents/skills/`.
9. Do not bulk-read every skill body under `.agents/skills/`. Irrelevant skills waste context and can pollute the task plan.
10. Keep every instruction, task, domain, task-file, attachment, and selected skill reference read-only. If an apparent correction is needed, record it as a gap; do not edit the reference file.
11. Record every task attachment/supporting file read or inspected, every selected relevant skill file, and the reason each was relevant in `task-workflow/phase-1-task-research.md`.
12. Read any other docs or local instructions required by `AGENTS.md` or the task domain.
13. Cite target repo instruction, domain, task file, task files folder, task attachments, and selected local skill files with repo-relative paths only. Do not depend on the task file to list them, and do not record sandbox-specific absolute paths for these files.
14. Inspect the existing codebase before planning edits.
15. Identify the affected routes, components, services, schemas, stores, tests, scripts, config, and docs.
16. Record the exact files and patterns that should be reused.
17. Record assumptions, constraints, non-goals, and risks.
18. Write an ordered implementation plan.
19. Write the verification and test plan.
20. Do not edit implementation files before this phase gate passes.
21. Update `task-workflow/progress.md` with the compact task summary, repo instructions read, domain/context files read, task attachments/supporting files read, selected relevant skill files, implementation direction, verification plan, risks, current phase artifact/reference pointers, only high-signal active files if needed, and next local action.
22. Update the Refs section in `task-workflow/progress.md` so future compaction/resume reads `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, relevant task attachments/supporting files from `.tasks/files/`, and only the relevant skill files selected from `.agents/skills/` in Phase 1.
23. After every Phase 1 gate requirement passes, set `task-workflow/CURRENT_PHASE.txt` to `phase-2-execution`.
24. Re-read `references/phase-2-4-execution-integrity.md` before doing Phase 2 work.
25. Update `task-workflow/progress.md` so current phase, current phase reference, and next local action match Phase 2.
26. Record that Phase 2 was promoted only after Phase 1 passed and the required Phase 2 reference was loaded.

## Research Surface

Research must be specific enough that another agent could execute from the artifact alone.

Record:

- task goal and user-visible outcome
- technical goal
- in-scope and out-of-scope work
- repo instructions and docs read
- task-relevant development rules extracted from `AGENTS.md`
- repo-local domain files read, including `.tasks/domain.md`
- every task attachment/supporting file from `.tasks/files/` read or inspected, with what it contributed to the plan
- selected relevant local skill files from `.agents/skills/` read, with reasons for selection
- repo-relative paths for target repo instruction, task, domain, task attachments/supporting files, and selected skill files
- affected architecture
- existing repo patterns to reuse
- files or directories inspected
- implementation plan in execution order
- verification and test plan
- risks, assumptions, and unresolved questions

The Phase 1 artifact is not notes after the fact. It is the plan that controls Phase 2.

## Phase 1 Score

Score `task-workflow/phase-1-task-research.md` against `30` items:

- `6` task understanding items
- `6` instruction and documentation items
- `8` codebase research items
- `6` ordered implementation plan items
- `4` risk and verification-plan items

Critical failures:

- task body not read completely
- root `AGENTS.md` not read and cited
- task-relevant `AGENTS.md` development rules not extracted before planning
- `task-workflow/progress.md` not updated with enough context, current phase pointers, phase artifact index, and artifact pointers to resume Phase 2 after compaction
- `.tasks/domain.md` not read and cited
- relevant repo-local domain files or relevant local skill files from `.agents/skills/` not read and cited
- `.tasks/files/` not enumerated, even if empty
- any task attachment/supporting file in `.tasks/files/` not read or inspected before planning
- irrelevant skill files in `.agents/skills/` bulk-read instead of selecting only task-relevant skills
- selected relevant skill files from `.agents/skills/` are not recorded in `task-workflow/progress.md` for compaction/resume reread
- `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, selected skill files under `.agents/skills/`, or other reference inputs edited without an explicit task requirement to edit that exact file
- `task-workflow/progress.md` does not point to the Phase 1 artifact for researched files and planned edit targets
- target repo instruction/task/domain/task-file/skill files recorded only as sandbox absolute paths instead of repo-relative paths
- codebase not inspected before implementation planning
- plan does not cite concrete files or directories
- planned work ignores tests, verification, or docs when they are required by the task
- planned work violates or omits applicable `AGENTS.md` development rules
- implementation files edited before Phase 1 passes
- implementation files edited while `CURRENT_PHASE.txt` still says `phase-1-task-research`
- Phase 1 artifact omits the task understanding, instructions/docs read, codebase research, implementation plan, or verification plan while claiming pass

Pass gate:

- score is at least `28/30`
- every critical research item passes
- the plan cites concrete files or directories
- `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, every task attachment/supporting file in `.tasks/files/`, relevant repo-local domain files, and selected relevant local skill files from `.agents/skills/` are read or inspected and cited with repo-relative paths
- task-relevant development rules from `AGENTS.md` are recorded and reflected in the plan
- reference inputs, especially `.tasks/*`, remain unchanged unless the task explicitly required editing that exact reference file
- `task-workflow/progress.md` lists `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, relevant task attachments/supporting files from `.tasks/files/`, and selected relevant skill files from `.agents/skills/` for reread after compaction
- `task-workflow/progress.md` points to the Phase 1 artifact for researched files/directories and planned edit targets
- the plan distinguishes implementation, tests, docs, and verification work
- no known ambiguity remains unhandled
- `CURRENT_PHASE.txt` is promoted to `phase-2-execution` only after Phase 1 passes

If this gate fails, stay in Phase 1.

## Promotion Rule

Phase 2 is blocked until Phase 1 passes in writing.

Before setting `task-workflow/CURRENT_PHASE.txt` to `phase-2-execution`, re-open:

- `task-workflow/phase-0-artifact-reset.md`
- `task-workflow/phase-1-task-research.md`
- `task-workflow/progress.md`

Both phase artifacts must show `Decision: Pass`, passing scores, all critical items passing, and no placeholder `Pending` rows in required evidence or gate sections. `progress.md` must identify Phase 2 as the current phase, summarize Phase 0 and Phase 1, brief the created artifact files, and state the next local action.

After this promotion, Phase 2 implementation is allowed only because the marker now says `phase-2-execution`. If any source file changes while the current marker still says `phase-1-task-research`, the run has failed.

Do not stop after research to ask whether to continue. The gate exists so the agent can continue autonomously once the research artifact is strong enough.
