---
name: orchestrating-parallel-agents
description: Spawns multiple AI coding agents to work on related GitHub issues concurrently using git worktrees. Use when breaking down a large feature into multiple issues, running parallel agents with --print flag, or managing wave-based execution of related tasks.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite
---

# Orchestrating Parallel Agents

Spawn multiple Claude agents to work on related issues concurrently using git worktrees.

## Philosophy

- **Issues ARE the prompts** - Write issues with enough context for autonomous work
- **Maximize parallelism** - Group independent work into waves
- **Fail fast** - Complete git/PR manually if agents can't
- **Trust but verify** - Review diffs, resolve conflicts manually

## Workflow Checklist

Copy and track progress:

```
Parallel Agent Orchestration:
- [ ] 1. Break feature into issues (1-3 files each)
- [ ] 2. Organize into waves (independent → dependent)
- [ ] 3. Pre-approve git permissions in settings.local.json
- [ ] 4. Spawn wave with --print flag
- [ ] 5. Monitor progress
- [ ] 6. Complete stragglers manually
- [ ] 7. Merge PRs (rebase between same-file conflicts)
- [ ] 8. Cleanup worktrees
```

## Issue Template

Each issue should be completable in isolation:

```markdown
## Problem
What's broken or missing.

## Solution
High-level approach.

## Files to Modify
- `path/to/file` - what changes

## Implementation
Code snippets or pseudocode.

## Acceptance Criteria
- [ ] Testable outcomes
```

**Key:** Include file paths and code examples. Agents work best with concrete starting points.

## Wave Organization

```
Wave 1: Independent changes (no shared files)
Wave 2: Changes that may touch same files (expect conflicts)
Wave 3: Integration/testing (depends on all above)
```

**Rule:** Same-file issues go in different waves OR same agent.

## Pre-approve Permissions

Add to `.claude/settings.local.json` for non-interactive `--print` mode:

```json
"Bash(git -C /absolute/path/to/worktree add:*)",
"Bash(git -C /absolute/path/to/worktree commit:*)",
"Bash(git -C /absolute/path/to/worktree push:*)"
```

## Spawn Agents

```bash
for issue in 101 102 103; do
  (claude --print "/worktree-issue $issue" > "issue-${issue}.log" 2>&1) &
done
```

## Monitor

```bash
ps aux | grep "claude.*worktree" | wc -l  # Running agents
git worktree list                          # Worktrees created
tail -f issue-*.log                        # Live logs
```

## Complete Stragglers

If agent finishes code but fails on git:

```bash
git -C <worktree> add -A
git -C <worktree> commit -m "feat: description"
git -C <worktree> push -u origin <branch>
gh pr create --head <branch> --title "..." --body "Closes #N"
```

## Merge with Conflicts

```bash
gh pr merge N --squash --delete-branch
```

If conflicts after prior merges:

```bash
cd <worktree> && git fetch origin main && git rebase origin/main
# resolve conflicts
git push --force-with-lease
```

## Cleanup

```bash
git worktree remove <path>
git branch -D <branch>
git worktree prune
```

## Quick Reference

| Tip | Why |
|-----|-----|
| 1-3 files per issue | Higher success rate |
| Include "Files to Modify" | Agents find code faster |
| Backend-first waves | Fewer frontend conflicts |
| Merge same-file PRs sequentially | Rebase between each |

| Problem | Solution |
|---------|----------|
| Agent stuck on permissions | Complete git manually |
| Merge conflict | Rebase, resolve, force-push |
| Agent went off-scope | Reject PR, clarify issue |
| Too many conflicts | Smaller waves, sequential merge |
