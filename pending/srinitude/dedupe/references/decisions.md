# Decision log for dedupe

One dated line per decision, newest first. State the choice, reason, and evidence.

- 2026-08-05: PD-005 moved report fields, approval shape, apply checks, and degraded package verification to `references/report-mutation.md`; load before reports or mutation plans; owner `dedupe`; backlink in `SKILL.md`.
- 2026-08-05: PD-004 moved URL and skill identity policy to `references/url-skill.md`; load for those adapters; owner `dedupe`; backlink in `SKILL.md`.
- 2026-08-05: PD-003 moved file and record identity policy to `references/file-record.md`; load for those adapters; owner `dedupe`; backlink in `SKILL.md`.
- 2026-08-05: PD-002 moved text and list identity policy to `references/text-list.md`; load for those adapters; owner `dedupe`; backlink in `SKILL.md`.
- 2026-08-05: PD-001 moved the full pipeline, identity classes, canonical rules, count proof, and audit gates to `references/core-contract.md`; load for every command; owner `dedupe`; backlink in `SKILL.md`.
- 2026-08-05: exact identity, normalized equality, and similarity candidates remain separate because only the first two can form strict groups under disclosed rules; tests prove pairwise similarity does not reduce canonical counts.
- 2026-08-05: the deterministic inspector cannot mutate input. Generic mutation across six adapters cannot preserve authority, rollback, and side effects safely in one script; agent-level `apply` uses a reviewed plan and domain tools.
- 2026-08-05: required runtime composition loads `always-current-datetime`, `starting-point`, `outcome-bounded-work`, and `logic-audit` from their canonical owners instead of duplicating their procedures.
- 2026-08-05: the package supports text, file, record, URL, list, and skill adapters because the user fixed all six as required scope and no installed skill owned general deduplication.
- 2026-08-05: scaffold layout, checks, and task graph came from `references/generation-contract.md`; Skill Factory doctor reported ready before generation.
