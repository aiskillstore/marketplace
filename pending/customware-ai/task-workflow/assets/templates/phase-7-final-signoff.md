# Phase 7 - Final Audit And Signoff

## Phase Gate Recap

| Phase | Artifact | Score | Decision | Still current |
| --- | --- | --- | --- | --- |
| 0 | `task-workflow/phase-0-artifact-reset.md` | Pending | Fail | Pending |
| 1 | `task-workflow/phase-1-task-research.md` | Pending | Fail | Pending |
| 2 | `task-workflow/phase-2-execution.md` | Pending | Fail | Pending |
| 3 | `task-workflow/phase-3-second-execution.md` | Pending | Fail | Pending |
| 4 | `task-workflow/phase-4-unit-coverage.md` | Pending | Fail | Pending |
| 5 | `task-workflow/phase-5-playwright-verification.md` | Pending | Fail | Pending |
| 6 | `task-workflow/phase-6-e2e-verification.md` | Pending | Fail | Pending |

## Final Diff Review

| Area | Files | Summary |
| --- | --- | --- |
| Pending | Pending | Pending |

## Final Verification

| Proof | Evidence |
| --- | --- |
| Final checks current after last code change, verified from owning-phase evidence without rerun unless missing/stale/invalidated | Pending |
| Open critical gaps resolved | Pending |
| Stale/deferred open gaps reconciled | Pending |
| Extracted `AGENTS.md` development rules followed | Pending |
| Phase 3 implementation integrity and static-check evidence is current | Pending |
| Phase 4 unit coverage decision is current: add, update, remove, or defended `N/A` | Pending |
| Phase 4 old/excess unit-test pruning audit and new-test burden ledger, if tests were added, are present | Pending |
| Phase 4 unit command output, defended `N/A`, or removed-test rationale and diff/readback evidence is present | Pending |
| Phase 6 E2E coverage decision is current: add, update, remove, or defended `N/A` | Pending |
| Phase 6 old/excess E2E pruning audit and new-E2E burden ledger, if E2E was added, are present | Pending |
| Phase 6 E2E command output, defended `N/A`, or removed-test rationale and diff/readback evidence is present | Pending |
| Phase 6 E2E command scope matches the coverage decision or an exact full-E2E requirement | Pending |
| Phase 6 E2E reruns have material change, stale-output, or diagnostic reasons | Pending |
| Rerun ledger records material reasons for repeated commands | Pending |
| Phase 5/6 correct lifecycle-owner evidence current | Pending |
| Phase 5/6 reused DB/setup/server lifecycle across related verification commands unless invalidated by changed state or lifecycle diagnostics | Pending |
| Phase 5/6 timeout values and timeout/quiet-run triage evidence current | Pending |
| Phase 5 responsive-quality evidence current and first-class when UI changed | Pending |
| Phase 5 UI-quality issues are resolved or defended with responsive evidence | Pending |
| Phase 5/6 browser preflight and lifecycle evidence current | Pending |
| Runtime logs cited for managed server or verification commands where output is too long | Pending |
| Changed app/server logging review is current after Phase 5 | Pending |
| Task summary accurate | Pending |
| `progress.md` agrees with Phase 7 and has no remaining local action | Pending |
| `progress.md` Phase Artifact Index and Artifact Pointers identify where final gate, verification, log, and test details live | Pending |

## MITB Task Completion Command

Run this only after all prior Phase 7 audit checks are clean. Prefer the exact `Completed:` command from `.tasks/task.md`; otherwise use the exact command supplied in the prompt. Do not synthesize project/task identifiers when the task file or prompt provides them. If any Phase 7 audit check fails, do not run this command; loop back to the earliest failing phase first. Treat this as the final external task action. Phase 7 must verify existing owning-phase evidence for checks, tests, builds, server probes, browser probes, and verification commands; run one only if the owning phase missed it, the evidence is missing/incomplete/stale, or later changes invalidated it.

| Item | Evidence |
| --- | --- |
| Completion command source | Pending |
| Exact completed command | Pending |
| Command run after Phase 7 audit checks passed | Pending |
| Command result/output | Pending |

## Open Gaps Audit

| Gap table | Remaining open items | Stale or contradicted? | Evidence |
| --- | --- | --- | --- |
| Critical Gaps | Pending | Pending | Pending |
| Non-Critical Gaps | Pending | Pending | Pending |
| Placeholder rows | Pending | Pending | Pending |

## Artifact Integrity Review

Re-open every required phase artifact. Do not infer pass status from memory or from this recap table.

| Artifact | Exists? | Decision and score pass? | Required evidence complete? | Contradictions? | Evidence |
| --- | --- | --- | --- | --- | --- |
| `task-workflow/phase-0-artifact-reset.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-1-task-research.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-2-execution.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-3-second-execution.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-4-unit-coverage.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-5-playwright-verification.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/phase-6-e2e-verification.md` | Pending | Pending | Pending | Pending | Pending |
| `task-workflow/progress.md` | Pending | Current and consistent | Final action ready | Pending | Pending |

## Fixed Wait Review Recap

| Source | Review present? | Current after last edit? | Deterministic waits confirmed? | Evidence |
| --- | --- | --- | --- | --- |
| Phase 5 interactive scripts | Pending | Pending | Pending | Pending |
| Phase 6 E2E files | Pending | Pending | Pending | Pending |

## Verification Evidence Recap

| Evidence type | Required proof | Present and current? | Evidence |
| --- | --- | --- | --- |
| Phase 5 screenshots | Every screenshot path cited in Phase 5 exists | Pending | Pending |
| Phase 5 responsive quality | Required viewports include mobile, tablet, desktop, standard `1920x1080`, and large `2560x1440` when UI changed; evidence shows responsive quality passed as a first-class guarantee with no broken UI, excessive 1080p dead space, or unfinished-looking 2560px empty regions | Pending | Pending |
| Phase 4 unit evidence | Unit coverage decision records remove/update/add/`N/A`; old/excess pruning audit is complete; every new test has a burden-ledger row; exact command output is recorded when a command was required; removed tests include rationale and diff/readback evidence | Pending | Pending |
| Phase 6 E2E evidence | E2E coverage decision records remove/update/add/`N/A`; old/excess pruning audit is complete; every new E2E has a burden-ledger row; exact E2E command output is recorded when a command was required; removed E2E tests include rationale and diff/readback evidence | Pending | Pending |
| Coverage selection and retry evidence | Phase 4 unit ledger and Phase 6 E2E ledger separately explain scope, `N/A` decisions, removals, rerun basis, outcomes, and next actions | Pending | Pending |
| Managed lifecycle evidence | Phase 5/6 records the correct lifecycle owner: helper by default, repo Playwright `webServer` or manual fallback only with reason/diagnostics; readiness, browser preflight, cleanup, and runtime logs are cited | Pending | Pending |
| DB/setup/server reuse evidence | Phase 5/6 does not repeatedly reset DB, rerun migrate/seed, or restart the server between related E2E commands without an invalidating state change or lifecycle diagnostic | Pending | Pending |
| Timeout/quiet-run triage evidence | Phase 5/6 records timeout values and triage for every timed-out, quiet, or longer-rerun Playwright/E2E command; no longer timeout is used without timer-only/no-useful-output failure plus clean state triage | Pending | Pending |
| Browser preflight | Phase 5/6 browser preflight and lifecycle evidence is current | Pending | Pending |
| Changed app/server logging | Changed logging uses the repo-approved logging or telemetry path after Phase 5 | Pending | Pending |

## Quality Scorecard

| Category | Required | Actual | Evidence |
| --- | --- | --- | --- |
| Functional result | >= 8/10 | 0/10 | Pending |
| Skill compliance/artifact integrity | >= 8/10 | 0/10 | Pending |
| Code quality/maintainability | >= 8/10 | 0/10 | Pending |
| Test quality | >= 8/10 | 0/10 | Pending |
| Development-instruction compliance | >= 8/10 | 0/10 | Pending |
| Overall result | >= 8/10 | 0/10 | Pending |

## Gate

| Metric | Required | Actual |
| --- | --- | --- |
| Score | 20/20 | 0/20 |
| All previous gates passed | yes | Pending |
| Artifacts auditable | yes | Pending |
| Critical gaps resolved, closed, or reclassified with evidence | yes | Pending |
| Open gaps reconciled with phase artifacts | yes | Pending |
| Gap ledger finalized with real rows or explicit none rows | yes | Pending |
| Fixed wait reviews current and clean | yes | Pending |
| Phase 5 cited screenshots exist | yes | Pending |
| Phase 5 responsive-quality evidence current and first-class when UI changed | yes | Pending |
| Phase 5 UI-quality issues resolved or defended with responsive evidence | yes | Pending |
| Phase 4 unit-test command output recorded when a command was required, defended `N/A` recorded when none was warranted, or removed-test rationale and diff/readback evidence recorded | yes | Pending |
| Phase 6 E2E command output recorded when a command was required, defended `N/A` recorded when none was warranted, or removed-test rationale and diff/readback evidence recorded | yes | Pending |
| Phase 4/6 old-excess test pruning audits are complete and new-test burden ledgers exist when tests were added | yes | Pending |
| Phase 3 implementation integrity and static-check evidence current | yes | Pending |
| Phase 7 did not rerun checks/builds/tests/Playwright/E2E unless owning-phase evidence was missing, incomplete, stale, or invalidated | yes | Pending |
| Phase 4 unit coverage ledger current | yes | Pending |
| Phase 6 E2E coverage ledger current | yes | Pending |
| Phase 6 E2E command scope matches coverage decision or exact full-E2E requirement | yes | Pending |
| Phase 6 E2E reruns have material change, stale-output, or diagnostic reasons | yes | Pending |
| Rerun ledger records material reasons for repeated commands | yes | Pending |
| Phase 5/6 correct lifecycle-owner evidence recorded | yes | Pending |
| Phase 5/6 DB/setup/server lifecycle reuse or invalidation reason recorded | yes | Pending |
| Phase 5/6 timeout/quiet-run triage evidence recorded for every timed-out, quiet, or longer-rerun Playwright/E2E command | yes | Pending |
| Longer Playwright/E2E timeout, if used, has timer-only failure and clean-state triage evidence | yes | Pending |
| Browser preflight/lifecycle evidence recorded for Phase 5/6 | yes | Pending |
| Artifact integrity review completed and clean | yes | Pending |
| Quality scorecard all >= 8/10 | yes | Pending |
| Extracted `AGENTS.md` development rules verified | yes | Pending |
| Changed logging uses repo-approved logging or telemetry path after Phase 5 | yes | Pending |
| Verification current | yes | Pending |
| MITB completed command run after clean final audit | yes | Pending |
| `progress.md` final state agrees with Phase 7 | yes | Pending |
| `progress.md` Current Phase Pointers final state is current | yes | Pending |
| `progress.md` Phase Artifact Index and Artifact Pointers final state is current | yes | Pending |
| Promotion lock verified before final signoff | yes | Pending |

Decision: Fail
