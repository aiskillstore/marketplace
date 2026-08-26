# CLI reference

## Usage

```text
sync-before-work [--check | --preview | --apply] [options]
```

Run the bundled file with Node.js 20 or newer:

```bash
node scripts/sync-before-work.mjs --apply --json
```

## Modes

| Mode | Fetches | Changes HEAD | Purpose |
|---|---:|---:|---|
| `--check` | No | No | Inspect cached remote refs |
| `--preview` | Yes | No | Report the operation required now |
| `--apply` | Yes | When safe | Synchronize the current branch |

Default mode is `--check`.

## Options

- `--remote <name>`: override the selected remote. Otherwise use `origin`, then the sole configured remote.
- `--base <branch>`: override remote default-branch detection.
- `--strategy merge|rebase`: default to `merge`. Rebase is restricted to unpublished branches.
- `--json`: emit one JSON object to stdout.
- `--help`: display usage.
- `--version`: display the CLI version.

## Successful statuses

- `up_to_date`: current HEAD already contains the fetched base.
- `fast_forwarded`: current branch advanced without a merge commit.
- `merged`: fetched base merged into a divergent feature branch.
- `rebased`: unpublished branch rebased after explicit selection.
- `would_fast_forward`, `would_merge`, `would_rebase`: preview or check result; no HEAD change occurred.

## Blocking statuses

- `blocked_dirty`: staged, unstaged, or untracked files exist.
- `detached_head`: no current branch exists.
- `operation_in_progress`: merge, rebase, cherry-pick, revert, or sequencer state already exists.
- `blocked_shared_rebase`: the branch has an upstream or matching remote branch.
- `blocked_ahead_default`: local default branch contains commits absent from its remote.
- `blocked_diverged_default`: local default branch diverged and cannot fast-forward.
- `conflict_aborted`: the attempted merge or rebase conflicted and was rolled back.
- `recovery_failed`: rollback could not be verified; inspect manually before continuing.
- `remote_unknown`, `base_unknown`, `base_missing`, `fetch_failed`, `git_error`, `sync_failed`: configuration, network, or Git failures.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Successful inspection or synchronization |
| `2` | Invalid context or arguments |
| `3` | Safety policy blocked the operation |
| `4` | Conflict detected and aborted |
| `5` | Git or network command failed |
| `6` | Automatic recovery could not be verified |
