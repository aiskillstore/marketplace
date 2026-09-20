---
name: w-git-repair
description: Resolve common Git problems and conflicts with inspected commands.
disable-model-invocation: true
---

Help with conflicts, detached HEAD, upstream divergence, and similar local Git problems. Follow [git publish](references/git-publish.md). Do not rewrite published history unless the user asked.

1. Inspect `git status`, `git branch -vv`, and the relevant log. State the current problem in one sentence.
2. Propose the smallest safe commands. Explain what they change. Require explicit confirmation before commands that can discard local changes (`git reset --hard`, `git clean`, `git restore`). Require an explicit user request before history-rewriting commands (`git rebase`, `git commit --amend` of a published commit).
3. After an authorized command, re-inspect status and remaining conflicts. Never force-push or bypass hooks.
