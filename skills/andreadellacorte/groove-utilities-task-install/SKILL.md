---
name: groove-utilities-task-install
description: "Set up task backend and configuration."
license: MIT
allowed-tools: Read Write Edit Glob Grep Bash(git:*) Bash(beans:*) Bash(gh:*) Bash(linear:*) Bash(npx:*) AskUserQuestion
metadata:
  author: andreadellacorte
---

# groove-utilities-task-install

## Outcome

The configured task backend is installed and verified reachable. User is informed of what was installed and how to use it.

## Acceptance Criteria

- Backend CLI is available in PATH after install
- User is shown a confirmation with the installed version or a reachability check
- No-op if `tasks.storage: none`

## Constraints

- Read `tasks.storage` from `.groove/index.md` to determine backend (if the key is still named `tasks.backend` from an older config, treat it as the storage value). If the key is missing or invalid, you may pause and use **`AskUserQuestion`** so the user can choose a backend (`beans`, `linear`, `github`, or `none`); then ensure `.groove/index.md` is updated accordingly (via `/groove-admin-config` or an equivalent edit) before continuing.
- If `tasks.storage: none`, print friendly no-op message and exit
- **Installation source of truth:** Do **not** embed OS-specific install commands in this skill. You **must** follow the **official installation instructions** from the upstream project for the user’s OS (read that page and run what it specifies). Link only:
  - **`beans`:** [hmans/beans](https://github.com/hmans/beans) — Installation section
  - **`linear`:** [schpet/linear-cli](https://github.com/schpet/linear-cli) — install section (third-party CLI; not Linear’s hosted docs)
  - **`github`:** [GitHub CLI](https://cli.github.com)
- After the CLI is on PATH per those instructions, run a reachability check (`beans version`, `linear --version` / `linear --help`, or `gh version` / `gh auth status` as appropriate)
- If the CLI is already installed before you start, report current version and skip fetching install instructions
- If `tasks.storage: beans` and `.beans.yml` does not exist at git root:
  - Run `beans init` to initialise the task store and generate `.beans.yml` with beans defaults
  - Derive `[PROJECT_PREFIX]` from the git repo name (last path component of `git remote get-url origin`, stripped of `.git`, uppercased, non-alphanumeric stripped) — e.g. `groove` → `GRV`; fall back to the directory name if no remote
  - Update the `prefix:` field in the generated `.beans.yml` to the derived prefix (e.g. `GRV-`)
  - Set `path:` in `.beans.yml` to `.groove/tasks` so the task store lives under groove (aligned with `git.tasks` and `.groove/.gitignore`). Create `.groove/tasks` if it does not exist. If the default `.beans` directory was created and is non-empty, move its contents into `.groove/tasks` and remove the empty `.beans` directory.
  - Report the path written and the prefix used
