---
name: sync-before-work
description: Safely fetch and incorporate the latest remote default branch before an AI agent starts changing code. Use before the first edit in every code-changing task, when entering an existing worktree or feature branch, when a branch may be behind main or master, and before substantial work resumes after a pause. Detect dirty trees, detached HEADs, published branches, linked worktrees, and conflicts; default to merge for shared branches and never push, reset, stash, switch branches, or guess conflict resolutions.
---

# Sync Before Work

Start every code-changing task from the latest remote default branch without risking existing work.

## Start-of-task gate

Run this gate once before the first file edit, generated artifact, commit, migration, or dependency change. Skip it for read-only explanation, diagnosis, or review.

1. Resolve this skill's directory from the loaded `SKILL.md` path.
2. Run:

   ```bash
   node <skill-directory>/scripts/sync-before-work.mjs --apply --json
   ```

3. Continue only when the status is one of:
   - `up_to_date`
   - `fast_forwarded`
   - `merged`
   - `rebased` when the user explicitly requested rebase
4. For every other status, stop the code-changing task and report the message. Do not work around a safety refusal.
5. Summarize any merge or fast-forward before beginning implementation.

The command fetches live remote state in `--apply` mode. Do not substitute a stale local comparison.

## Strategy rules

- Use the default `merge` strategy for feature branches, pushed branches, open PRs, and uncertain ownership.
- Use `--strategy rebase` only when the user explicitly requests it and the branch is unpublished. The script refuses rebasing a published branch.
- On the default branch, allow only a fast-forward. Stop if local and remote histories diverged.
- Pass `--remote <name>` or `--base <branch>` only when repository evidence or the user identifies a nonstandard source.

## Safety rules

- Never stash or discard a dirty tree automatically.
- Never switch branches or leave the current worktree.
- Never push or force-push.
- Never reset history.
- Never continue after the script aborts a conflict.
- Never resolve semantic conflicts automatically.
- Preserve user changes and unrelated work.

For command options and machine-readable statuses, read [references/CLI.md](references/CLI.md). For invariants and decision logic, read [references/SAFETY-CONTRACT.md](references/SAFETY-CONTRACT.md).

## Additional checks

Use preview mode when the user requests inspection without branch changes:

```bash
node <skill-directory>/scripts/sync-before-work.mjs --preview --json
```

Use local-only check mode when network access is unavailable:

```bash
node <skill-directory>/scripts/sync-before-work.mjs --check --json
```

Treat `--check` as potentially stale because it does not fetch.

For long-running tasks, rerun the start-of-task gate before opening a PR or handing off if the default branch may have moved.
