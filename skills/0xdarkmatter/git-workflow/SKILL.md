---
name: git-workflow
description: "Enhanced git operations using lazygit, gh (GitHub CLI), and delta. Triggers on: stage changes, create PR, review PR, check issues, git diff, commit interactively, GitHub operations, rebase, stash, bisect."
compatibility: "Requires git, gh (GitHub CLI), lazygit, and delta. Network access needed for GitHub operations."
allowed-tools: "Bash"
---

# Git Workflow

Streamline git operations with visual tools and GitHub CLI integration.

## Tools

| Tool | Command | Use For |
|------|---------|---------|
| lazygit | `lazygit` | Interactive git TUI |
| gh | `gh pr create` | GitHub CLI operations |
| delta | `git diff \| delta` | Beautiful diff viewing |

## lazygit Essentials

```bash
# Open interactive TUI
lazygit

# Key bindings:
# Space - stage/unstage file
# c     - commit
# p     - push
# P     - pull
# b     - branch operations
# r     - rebase menu
# s     - stash menu
# ?     - help
```

## GitHub CLI (gh) Essentials

```bash
# Pull Requests
gh pr create --title "Feature: Add X" --body "Description"
gh pr create --web           # Open in browser
gh pr list                   # List open PRs
gh pr view 123               # View PR details
gh pr checkout 123           # Check out PR locally
gh pr merge 123 --squash     # Squash and merge

# Issues
gh issue create --title "Bug: X"
gh issue list --label bug

# Repository
gh repo view --web           # Open in browser

# Actions
gh workflow run deploy.yml
gh run list --workflow=ci.yml
```

## Delta (Beautiful Diffs)

```bash
# View diff with syntax highlighting
git diff | delta

# Side-by-side view
git diff | delta --side-by-side

# Configure as default pager
git config --global core.pager delta
```

## Quick Reference

| Task | Command |
|------|---------|
| Interactive git | `lazygit` |
| Create PR | `gh pr create` |
| Merge PR | `gh pr merge --squash` |
| Beautiful diff | `git diff \| delta` |
| Interactive rebase | `git rebase -i HEAD~N` |
| Stash changes | `git stash push -m "msg"` |
| Apply stash | `git stash pop` |
| Find bug commit | `git bisect start` |
| Cherry-pick | `git cherry-pick <hash>` |
| Parallel worktree | `git worktree add <path> <branch>` |
| Recover commits | `git reflog` |

## When to Use

- Interactive staging of changes
- Creating pull requests from terminal
- Reviewing PRs and issues
- Visual diff viewing
- Cleaning up commit history (rebase)
- Temporary work saving (stash)
- Bug hunting (bisect)
- Parallel feature work (worktrees)
- Recovering lost work (reflog)

## Additional Resources

For detailed patterns, load:
- `./references/rebase-patterns.md` - Interactive rebase workflows
- `./references/stash-patterns.md` - Stash operations and workflows
- `./references/advanced-git.md` - Bisect, cherry-pick, worktrees, reflog, conflicts
