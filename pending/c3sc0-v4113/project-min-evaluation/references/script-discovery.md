# Script discovery edge cases

- `packageManager` looks like `pnpm@10.4.1`; use the name before `@`. It wins over lockfiles.
- More than one lockfile and no `packageManager`: report the conflict and ask which manager the project uses.
- Workspaces: run the scripts in the root `package.json`; run package-level scripts only for packages the change touched.
- `check` often aggregates other scripts. Still run the individual scripts first so a failure names its source.
- `doctor` usually runs React Doctor; a score regression or new warning counts as a failure.
- A script that needs an unavailable service (database, browser) is reported as not run, with the reason; it is never reported as passed.
