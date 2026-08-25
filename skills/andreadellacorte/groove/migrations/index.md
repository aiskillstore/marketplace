# Migration Index

Ordered registry of all groove migrations. Each entry maps a from-version to a to-version with the migration file that handles the transition.

`groove update` reads this file to determine which migrations to run. It selects all rows where `To` > local `groove-version:` AND `To` <= installed version, then runs them in table order. The `From` field is informational only — it does not gate execution, so migrations apply correctly across any version gap.

## Format

| From | To | File | Description |
|---|---|---|---|
| 0.2.0 | 0.3.0 | 0.2.0-to-0.3.0.md | Add `last-version-check:` config key; write `.groove/.gitignore` from git strategy |
| 0.4.0 | 0.5.0 | 0.4.0-to-0.5.0.md | Remove `sessions:` config key; create session directories for native multi-session tracking |
| 0.5.3 | 0.6.0 | 0.5.3-to-0.6.0.md | Split flat `git:` into `git.memory/tasks/hooks` sub-keys; remove `finder:` and `sessions:`; move beans tasks to `.groove/tasks/` |
| 0.8.2 | 0.8.3 | 0.8.2-to-0.8.3.md | Move `last-version-check:` out of `index.md` into `.groove/.cache/last-version-check`; create `.cache/` directory; gitignore `.cache/*` |
| 0.8.3 | 0.8.4 | 0.8.3-to-0.8.4.md | Rewrite AGENTS.md sections to v0.8.x format: 2-line groove:prime bootstrap and 2-line groove:task stub |
| 0.8.6 | 0.8.7 | 0.8.6-to-0.8.7.md | Remove redundant beans prime line from groove:prime bootstrap in AGENTS.md |
| 0.8.7 | 0.8.8 | 0.8.7-to-0.8.8.md | Update groove:task stub wording: "to load" instead of "if you need" |
| 0.8.8 | 0.8.9 | 0.8.8-to-0.8.9.md | Move spec files from `<memory>/sessions/specs/` to `<memory>/specs/` |
| 0.8.9 | 0.9.0 | 0.8.9-to-0.9.0.md | Remove obsolete `.agents/skills/skills` directory (skills wrapper removed in 0.7.0) |
| 0.9.4 | 0.10.0 | 0.9.4-to-0.10.0.md | Standalone `daily`, `work`, `task`, `memory` skills removed. All workflow commands now individual `groove-*` skills. No `.groove/index.md` config changes needed. |
| 0.10.0 | 0.10.1 | 0.10.0-to-0.10.1.md | Add `recent_memory_days: 5` to `.groove/index.md`; update `AGENTS.md` prime stub to `/groove-utilities-prime`. |
| 0.11.4 | 0.11.5 | 0.11.4-to-0.11.5.md | Add optional `task.list_limit` and `task.analyse_limit` to `.groove/index.md` for task-list and task-analyse. |
| 0.11.7 | 0.12.0 | 0.11.7-to-0.12.0.md | Create `<memory>/learned/`; add `specs:` (required) and `groovebook:` (default andreadellacorte/groovebook) if absent. |
| 0.13.0 | 0.14.0 | 0.13.0-to-0.14.0.md | Restructure config: `tasks:` → `tasks.backend`, `task.*` → `tasks.*`, `recent_memory_days:` → `memory.review_days`, remove `memory:` and `specs:` (hardcoded). |
| 0.14.0 | 0.15.0 | 0.14.0-to-0.15.0.md | Run `/groove-admin-claude-hooks` to add `context-reprime` hook; run `/groove-admin-cursor-hooks` if `.cursor/` exists. |
| 0.16.1 | 0.17.0 | 0.16.1-to-0.17.0.md | Remove `groove:prime` and `groove:task` AGENTS.md stubs — session bootstrap now handled by native platform hooks. |
| 0.17.0 | 0.18.0 | 0.17.0-to-0.18.0.md | Reinstall Claude/Cursor hooks — fix SessionStart to run prime script directly, add version-check hook, remove stale context-reprime.sh. |
| 0.18.2 | 0.18.3 | 0.18.2-to-0.18.3.md | Rename `tasks.backend` → `tasks.storage` in `.groove/index.md`. |
| 0.18.3 | 0.18.4 | 0.18.3-to-0.18.4.md | Reinstall Claude/Cursor hooks — use `$CLAUDE_PROJECT_DIR`-prefixed paths so hooks work regardless of shell working directory. |
| 0.18.5 | 0.18.6 | 0.18.5-to-0.18.6.md | Create `.groove/memory/docs/` for `/groove-work-doc` parity with fresh install. |

## Notes

- Migrations are run in table order — order matters
- Each migration must be idempotent (safe to re-run if interrupted)
- After each successful migration, `groove-version:` in `.groove/index.md` is updated to the `To` version
- If the table is empty and versions match, `groove update` reports "already up to date"

## Adding a migration

Only add a migration when local user state must change — i.e. `.groove/index.md` keys, memory directory structure, or `AGENTS.md` sections. Skill renames, wording changes, and new commands do **not** need a migration.

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full versioning and migration guide.

Quick steps:
1. Create `migrations/<from>-to-<to>.md` following the outcome/criteria/constraints pattern
2. Add a row to the table above
3. Bump `metadata.version` in `skills/groove/SKILL.md`
4. Add an entry to `CHANGELOG.md`
