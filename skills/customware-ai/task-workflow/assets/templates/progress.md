# Progress Ledger

This file is the compact resume state for the task. Hard rule: re-read it after every compaction, resume, retry, reconnect, or new coding session before continuing work.

## Resume Instructions

- Use this file and `CURRENT_PHASE.txt` to identify current status after compaction, resume, retry, reconnect, or new coding session; then re-read `SKILL.md`, `open-gaps.md`, the current phase artifact, and the current phase reference before choosing the next action.
- When `CURRENT_PHASE.txt` changes, re-read the required current phase reference before doing any work in the new phase.
- Re-read the refs below after compaction, resume, retry, reconnect, or new coding session; keep paths repo-relative and update this section when Phase 1 selects task-relevant skill files.
- Treat refs as read-only unless the task explicitly asks to edit that exact reference file. This is especially strict for `.tasks/task.md`, `.tasks/domain.md`, `.tasks/files/`, and selected skill files under `.agents/skills/`.
- If this file disagrees with phase artifacts, trust the earliest failing phase artifact and repair this file.

## Refs

These are starting refs. Edit notes as the task clarifies which files are relevant.

| Ref | Path | Use | Notes |
| --- | --- | --- | --- |
| Repo instructions | `AGENTS.md` | Binding development instructions for this repo | Read in Phase 1 and after compaction/resume; extract task-relevant rules before planning |
| Task file | `.tasks/task.md` | Canonical task body and completion command source | Read in Phase 1 and after compaction/resume |
| Domain file | `.tasks/domain.md` | Domain, brand, and product context | Read in Phase 1 and after compaction/resume |
| Task files folder | `.tasks/files/` | Task attachments and supporting inputs | Enumerate in Phase 1; read or inspect every task attachment/supporting file before planning |
| Task attachments/supporting files | Pending | Task-provided files that must influence the plan | Replace with repo-relative file paths after Phase 1 reads or inspects them |
| Skill files folder | `.agents/skills/` | Available skill files; select only relevant skill files | Do not bulk-read irrelevant skill files |

## Resume Pointer

| Field | Value |
| --- | --- |
| Current phase | Pending |
| Current phase artifact | Pending |
| Current phase reference | Pending |
| Earliest failing phase, if any | Pending |
| Last completed gate | Pending |
| Next local action | Pending |
| External blocker, if any | Pending |
| Last updated | Pending |

## Task Snapshot

| Item | Summary |
| --- | --- |
| Task goal | Pending |
| Target repo | Pending |
| Key constraints | Pending |
| Current implementation direction | Pending |
| MITB task completion command | Pending |

## Current Phase Pointers

Keep this section compact. Do not copy full file inventories from phase artifacts. Point to the phase artifact for details and list only high-signal active files needed to resume immediately.

| Pointer | Path or value | Why it matters |
| --- | --- | --- |
| Current phase artifact | Pending | Detailed evidence and file lists for the current phase |
| Current phase reference | Pending | Detailed process to follow now |
| Key active files | Pending | Only files needed to resume the next local action quickly |
| Last command or verification proof | Pending | Latest useful proof, not full logs |

## Phase Artifact Index

Update status and notes only. Full evidence belongs in each phase artifact.

| Phase | Status | Phase artifact | Phase reference | Compact note |
| --- | --- | --- | --- | --- |
| 0 - Artifact reset | Pending | `task-workflow/phase-0-artifact-reset.md` | `references/phase-0-1-startup-research.md` | Pending |
| 1 - Research | Pending | `task-workflow/phase-1-task-research.md` | `references/phase-0-1-startup-research.md` | Pending |
| 2 - Primary execution | Pending | `task-workflow/phase-2-execution.md` | `references/phase-2-4-execution-integrity.md` | Pending |
| 3 - Second execution and check/lint validation | Pending | `task-workflow/phase-3-second-execution.md` | `references/phase-2-4-execution-integrity.md` | Pending |
| 4 - Unit coverage | Pending | `task-workflow/phase-4-unit-coverage.md` | `references/phase-2-4-execution-integrity.md` | Pending |
| 5 - Playwright verification | Pending | `task-workflow/phase-5-playwright-verification.md` | `references/phase-5-7-verification-signoff.md`; `references/playwright-interactive.md` | Pending |
| 6 - E2E coverage | Pending | `task-workflow/phase-6-e2e-verification.md` | `references/phase-5-7-verification-signoff.md` | Pending |
| 7 - Final signoff | Pending | `task-workflow/phase-7-final-signoff.md` | `references/phase-5-7-verification-signoff.md` | Pending |

## Artifact Pointers

Keep pointers only. Do not duplicate detailed lists already recorded in phase artifacts.

| Artifact group | Path(s) | Details live in | Status / notes |
| --- | --- | --- | --- |
| Resume and gap files | `task-workflow/CURRENT_PHASE.txt`; `task-workflow/open-gaps.md`; `task-workflow/progress.md` | current marker, gap ledger, this resume index | Pending |
| Phase artifacts | See Phase Artifact Index | phase-owned gate files | Pending |
| Playwright evidence | `task-workflow/playwright/`; `task-workflow/screenshots/` | `task-workflow/phase-5-playwright-verification.md` | Pending |
| Managed Playwright lifecycle helper | `task-workflow/scripts/playwright-lifecycle.mjs`; `task-workflow/runtime/` | `task-workflow/phase-5-playwright-verification.md`; `task-workflow/phase-6-e2e-verification.md`; `task-workflow/phase-7-final-signoff.md` | Pending |
| Managed server probe helper | `task-workflow/scripts/server-probe.mjs`; `task-workflow/runtime/` | `task-workflow/phase-2-execution.md`; `task-workflow/phase-3-second-execution.md` when a narrow runtime probe is required | Pending |
| Check/build checkpoint | repo-native check/lint/build output or `task-workflow/runtime/` logs | `task-workflow/phase-3-second-execution.md` | Pending |
| Production/live DB safety | DB/migration/setup evidence in execution and verification artifacts | `task-workflow/phase-2-execution.md`; `task-workflow/phase-3-second-execution.md`; `task-workflow/phase-5-playwright-verification.md`; `task-workflow/phase-6-e2e-verification.md` | Pending |
| Unit evidence | `task-workflow/runtime/` or exact pasted command output | `task-workflow/phase-4-unit-coverage.md` | Pending |
| E2E evidence | `task-workflow/runtime/` or exact pasted command output | `task-workflow/phase-6-e2e-verification.md` | Pending |
| Task completion evidence | `.tasks/task.md`; `/workspace/mitb/task_complete.mjs` | `task-workflow/phase-7-final-signoff.md` | Pending |

## Resume Rules

- After compaction, resume, retry, reconnect, or new coding session, use this file and `CURRENT_PHASE.txt` to identify current status, then re-read `SKILL.md`, `open-gaps.md`, the current phase artifact, and the current phase reference.
- After any phase promotion or marker change, read the required phase reference from the Phase Artifact Index before starting work in that phase.
- After compaction, resume, retry, reconnect, or new coding session, also re-read the repo-relative files listed in `Refs`, including `AGENTS.md`, `.tasks/task.md`, `.tasks/domain.md`, relevant task attachments/supporting files from `.tasks/files/`, and only the relevant skill files selected from `.agents/skills/` in Phase 1.
- If this file and `CURRENT_PHASE.txt` disagree, inspect the phase artifacts and continue from the earliest failing phase.
- Use Current Phase Pointers and Phase Artifact Index to find the detailed phase artifact and reference before choosing the next action.
- Use Artifact Pointers only to locate artifact groups; read the owning phase artifact for details.
- This file is a summary and resume map, not proof by itself. Phase artifacts and gate decisions remain the proof.
- Do not produce a final response while this file says any phase is `Pending`, `Fail`, `In progress`, or locally repairable.
