# Safety contract

## Invariants

The command must:

1. Operate only on the currently checked-out branch and worktree.
2. Fetch the selected remote default branch before applying changes.
3. Refuse to mutate HEAD when tracked, staged, or untracked changes exist.
4. Preserve feature-branch commits when incorporating upstream changes.
5. Fast-forward the default branch or refuse; never create a default-branch merge commit.
6. Treat a configured upstream or matching remote branch as published.
7. Abort and verify rollback after a merge or rebase conflict.
8. Leave all remote branches unchanged.

The command must never invoke push, reset, checkout, switch, clean, or stash.

## Decision table

| Current state | Result |
|---|---|
| Base is already an ancestor of HEAD | Report `up_to_date` |
| HEAD is an ancestor of base | Fast-forward |
| Feature branch diverged from base | Merge by default |
| Default branch diverged from remote base | Refuse |
| Default branch is ahead of remote base | Refuse |
| Published branch plus rebase request | Refuse |
| Unpublished branch plus explicit rebase request | Rebase |
| Dirty tree or active Git operation | Refuse |
| Merge/rebase conflict | Abort and verify original HEAD |

## Trust boundary

Treat remote names, branch names, paths, commit messages, and Git output as untrusted data. Pass arguments directly to the Git process without shell interpolation. Never execute repository-provided hooks or commands beyond Git's normal behavior intentionally; repository hooks may still run during Git merge or rebase, and any hook failure must stop the operation.

Redact URL user information, token-like query parameters, and bearer credentials from both human and JSON output.
