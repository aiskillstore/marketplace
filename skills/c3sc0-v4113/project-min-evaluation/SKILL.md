---
name: project-min-evaluation
description: "Trigger: done, complete, finish, before commit, quality check, verify. Run the project's own minimum quality scripts before claiming work is complete."
license: Apache-2.0
metadata:
  author: purrfold
  version: "1.0"
---

# Project Minimum Evaluation

## Activation Contract

Load this skill before reporting implementation work as complete, before committing, or when asked to verify quality.

## Hard Rules

1. Detect the package manager from the project; never hardcode a runner.
2. Run only scripts defined in `package.json` `scripts`; report expected scripts that are missing instead of inventing commands.
3. Run from the repository root, in the order below, and do not skip a failing step to reach a later one.
4. Never claim completion while a check fails or was not run.

## Decision Gates

| Project signal | Runner |
| --- | --- |
| `packageManager` field in `package.json` | use the manager it names |
| `pnpm-lock.yaml` | `pnpm run <script>` |
| `bun.lock` or `bun.lockb` | `bun run <script>` |
| `package-lock.json`, or no other signal | `npm run <script>` |

| Script | Run when |
| --- | --- |
| `lint` | always, if defined |
| `typecheck` | always, if defined |
| `format:check` | always, if defined |
| `test` | always, if defined |
| `doctor` | always, if defined |
| `check` | always, if defined (aggregate gate) |
| `test:e2e` | only when end-to-end behavior changed |

## Execution Steps

1. Read `package.json` and the lockfiles to choose the runner.
2. Collect the scripts from the table that exist in `scripts`.
3. Run each existing script in table order with the chosen runner.
4. Stop at the first failure, fix it, and rerun from that script.

## Output Contract

Report each script as passed, failed, or not defined. For a failure or a check that cannot run, give the exact command, the exact error, and the unverified scope.

## References

- [references/script-discovery.md](references/script-discovery.md) — detection edge cases.
