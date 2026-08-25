# .groove/index.md Template

Scaffold this file at `.groove/index.md` (relative to git root) on first run of any groove skill.

```markdown
---
groove-version: 0.1.0
groovebook: andreadellacorte/groovebook
tasks:
  storage: beans
  list_limit: 15
  analyse_limit: 30
memory:
  review_days: 5
git:
  memory: ignore-all
  tasks: ignore-all
  hooks: commit-all
---
```

**Config keys:**

| Key | Default | Values | Purpose |
|---|---|---|---|
| `groove-version` | `0.1.0` | semver string | Tracks which groove version this config was last migrated to |
| `groovebook` | `andreadellacorte/groovebook` | `<owner>/<repo>` or blank | Shared learning commons repo; enables `groove-groovebook-publish` and `groove-groovebook-review`. Blank = disabled. |
| `tasks.storage` | `beans` | `beans \| linear \| github \| none` | Task tracking backend |
| `tasks.list_limit` | `15` | positive integer | Maximum tasks shown by `/groove-utilities-task-list` |
| `tasks.analyse_limit` | `30` | positive integer | Maximum tasks shown by `/groove-utilities-task-analyse` |
| `memory.review_days` | `5` | positive integer | Number of recent business days (Mon–Fri) reviewed at startup, including memory file status and git activity |
| `git.memory` | `ignore-all` | `ignore-all \| hybrid \| commit-all` | Git strategy for memory logs |
| `git.tasks` | `ignore-all` | `ignore-all \| commit-all` | Git strategy for task files in `.groove/tasks/` |
| `git.hooks` | `commit-all` | `ignore-all \| commit-all` | Git strategy for hooks in `.groove/hooks/` |

**Hardcoded paths** (not configurable):

| Path | Purpose |
|---|---|
| `.groove/memory/` | Base path for memory log files |
| `.groove/memory/specs/` | Where specs are saved and read |
