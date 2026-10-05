# Read-only Check Policy

The audit must preserve the target project's files, dependencies, services, databases, and infrastructure. A familiar command name is not enough to prove that a repository script is read-only.

## Allowed by the bundled collector

The collector may invoke only local executables already present under `node_modules/.bin`:

- `eslint <scope> --no-fix --no-cache`;
- `tsc --noEmit --pretty false --incremental false`.

It does not invoke `npm run`, `pnpm run`, `yarn`, or `bun` scripts because lifecycle hooks and wrapper scripts can hide writes or external actions. It does not download a missing executable.

## Agent-run checks

An agent may run another project-native check only after reading the exact script and its pre/post lifecycle hooks. The command must not:

- include `--fix`, `--write`, snapshot updates, coverage output, code generation, or build emission;
- install, update, prune, or audit-fix dependencies;
- run migrations, seeds, deployment, container, Kubernetes, or cloud commands;
- contact production-like databases, queues, caches, vendors, or other shared mutable services;
- rewrite lockfiles, generated contracts, formatting, or source files.

Tests are not assumed safe from their name. Inspect configuration, setup files, environment loading, global hooks, and dependency targets before running them. When safety cannot be established cheaply, mark the check **not run** and explain the missing evidence.

## Working-tree verification

Record `git status --short` before checks. After checks, compare it again. If a supposedly read-only check changed the tree:

1. stop further checks;
2. report the exact new paths and command;
3. do not delete or revert anything without the user's permission;
4. classify the gate as invalid until rerun safely.

Existing dirty files belong to the user and must not be attributed to the audit.
