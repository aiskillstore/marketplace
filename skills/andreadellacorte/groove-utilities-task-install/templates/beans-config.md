# .beans.yml Template

Scaffold this file at the git root as `.beans.yml` when setting up beans backend for the first time.

```yaml
beans:
  path: .groove/tasks
  prefix: [PROJECT_PREFIX]-
  id_length: 4
  default_status: todo
  default_type: task
```

**Notes:**
- Replace `[PROJECT_PREFIX]` with a short uppercase abbreviation of the repo name (e.g. `GRV` for groove)
- `path` is where beans stores task files — `.groove/tasks` keeps them inside the groove directory, controlled by `git.tasks` strategy
- `id_length: 4` gives IDs like `GRV-0001`
- After creating this file, run `beans list` to verify beans is configured correctly
- **Excluding completed/scrapped work:** use mainline beans' native lingo — `beans list --no-status completed --no-status scrapped` for a tidy working view, and `beans archive` (via `/groove-utilities-task-archive`) to move terminal beans into `.beans/archive/`. groove's task views already use these, so no extra config key is needed.
