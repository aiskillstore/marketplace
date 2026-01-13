---
name: project-planner
description: "Detects stale project plans and suggests session commands. Triggers on: sync plan, update plan, check status, plan is stale, track progress, project planning."
allowed-tools: "Read Glob TodoWrite"
---

# Project Planner Skill

Lightweight awareness layer for `docs/PLAN.md`. Detects when plans need attention and points to `/save` and `/sync` commands.

## Purpose

This skill does NOT manage plans directly. It:
- Detects when `docs/PLAN.md` exists or is missing
- Identifies stale plans (no recent updates vs git activity)
- Suggests appropriate session commands

All plan operations go through `/save` (persist) and `/sync` (restore/status).

## Detection Logic

### Plan Missing
```
No docs/PLAN.md found
-> Suggest: /save to create initial plan from conversation
```

### Plan Stale
```
docs/PLAN.md last modified: 5 days ago
git log shows: 12 commits since then
-> Suggest: /sync --git to update from commits
```

### Uncommitted Work
```
git status shows: 5 modified files
docs/PLAN.md "In Progress" section outdated
-> Suggest: /sync --status to review
```

### Session Start
```
Resuming work on project with docs/PLAN.md
-> Suggest: /sync to restore state
```

## Quick Reference

| Situation | Suggestion |
|-----------|------------|
| No plan exists | `/save` after discussing goals |
| Plan is stale | `/sync --git` |
| Need to see plan | `/sync --status` |
| Update progress | `/save "notes"` |
| Start fresh | `/save --archive` |

## Staleness Heuristics

A plan is considered **stale** when:
- Last modified > 3 days ago AND
- Git shows commits since last modification AND
- Commits relate to plan topics (feat:, fix:, refactor:)

A plan **needs review** when:
- Session just started
- Significant uncommitted changes exist
- User mentions progress or completion

## Notes

- This skill only suggests, never modifies
- `/sync` reads state, `/save` writes state
- Single source of truth: `docs/PLAN.md`
