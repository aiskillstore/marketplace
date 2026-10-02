---
name: git
description: "Manages Git commits, branches, conflict resolution, and recovery. Use when the task requires Git operations or history analysis; follow the repository workflow."
---

# Git

Git is a content-addressed history of snapshots. Most "scary" situations are recoverable because commits aren't deleted immediately — `git reflog` is your safety net. Optimize for a history that's easy to read and bisect.

## Commit hygiene

- One logical change per commit; keep them small and self-contained (each should build/pass tests).
- Stage intentionally: `git add -p` to split unrelated changes.
- Write good messages — **Conventional Commits**: `type(scope): summary` (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`).
  - Imperative mood, ≤ ~50-char subject, blank line, then *why* in the body (not just *what*).
- Never commit secrets, large binaries, build artifacts, or `node_modules` — that's what `.gitignore` is for.

```
feat(auth): add refresh-token rotation

Access tokens now expire in 15m and rotate on refresh to limit
replay if one leaks. Closes #142.
```

## Branching

- Short-lived feature branches off `main`; branch names like `feat/login`, `fix/cors-headers`.
- Keep `main` releasable. Integrate often to avoid drift and giant merges.
- Pull with `--ff-only` or rebase to avoid noise: `git pull --rebase`.

## Merge vs rebase

- **Rebase** local, unpushed work to keep history linear: `git rebase main` (replays your commits on top).
- **Merge** to integrate shared branches and preserve context (often a PR squash-merge).
- **Golden rule: never rebase/force-push history others have based work on** (shared `main`/release branches). Rebase only your own private branches.
- If you must overwrite a pushed *personal* branch, use `git push --force-with-lease` (refuses if someone else pushed).

## Inspect history

- `git status`, `git log --oneline --graph --decorate`, `git diff` / `--staged`.
- `git blame <file>` and `git log -p <file>` to trace why a line exists.
- `git bisect` to binary-search the commit that introduced a bug.

## Undo / recover (most are safe)

- Unstage: `git restore --staged <file>`. Discard working changes: `git restore <file>` (destructive — be sure).
- Amend last commit (message or forgotten file): `git commit --amend` (only if not yet shared).
- Undo a public commit safely: `git revert <sha>` (new inverse commit — never rewrites shared history).
- Move branch pointer: `git reset --soft` (keep changes staged) / `--mixed` (keep unstaged) / `--hard` (discard — careful).
- Stash WIP: `git stash push -m "msg"` / `git stash pop`.
- **Lost a commit?** `git reflog` shows where HEAD has been; `git checkout`/`reset` to that SHA to recover.

## Conflicts

- Resolve hunk by hunk; keep the *intended* behavior, not just "accept theirs/mine".
- Build + test after resolving, before continuing the merge/rebase.
- `git rerere` can auto-reuse recorded resolutions for repeated conflicts.

## Collaboration & safety

- Keep PRs small and focused; describe *why* and how to verify.
- Protect `main` (require review/CI; block force-push). Don't push directly to a CI/CD-connected branch unless that's the agreed flow.
- Use signed commits/tags where required; tag releases with annotated tags (`git tag -a v1.2.0 -m`).
- `.gitignore` + (optionally) a secret-scanning pre-commit hook to stop leaks early.

## Reference

- Pro Git book (git-scm.com/book); `git help <command>`.
- Conventional Commits spec (conventionalcommits.org); Atlassian Git tutorials.
