# Blitz Pitfalls and Gotchas

## Agent Resume Errors

Claude agents cannot resume after API disconnection. If an agent fails mid-task:

1. Check its worktree state:
   ```bash
   cd .worktrees/NAME && git status
   ```
2. Spawn fresh agent with context of what's already done
3. The new agent picks up from the current state

## Reviews as Comments vs Formal Reviews

`gh api` posts reviews as PR comments, not GitHub's formal review system.

**Implications:**
- Won't trigger "Changes requested" status
- Won't block merge via branch protection
- Fine for self-review workflow

**If formal reviews needed:** Use the GitHub web UI or different API endpoint.

## Worktree Directory Confusion

Agents may drift to wrong directory during execution.

**Prevention:**
- Always specify absolute paths in prompts
- Verify with `pwd` in agent's first command
- Use `cd /absolute/path &&` prefix for safety

**Example prompt prefix:**
```
Working directory: /Users/name/project/.worktrees/feature-x
First, verify: cd /Users/name/project/.worktrees/feature-x && pwd
```

## Background Processes Accumulating

Long-running agents spawn background processes (dev servers, watchers, etc.).

**Monitor with:**
```bash
ps aux | grep -E "(node|cargo|npm)"
```

**Clean up orphans after workflow completes.**

## Stale Worktree References

If worktree directory was deleted manually (rm -rf instead of git worktree remove):

```bash
git worktree prune  # Cleans stale references
```

## Merge Conflicts During Rebase

When rebasing onto updated main causes conflicts:

```bash
# During rebase
git rebase origin/main

# If conflicts appear:
# 1. Open conflicted files, resolve conflicts
# 2. Stage resolved files
git add <resolved-files>

# 3. Continue rebase
git rebase --continue

# 4. Force push (safe)
git push --force-with-lease
```

**If too messy:** Abort and restart
```bash
git rebase --abort
git reset --hard origin/fix/NAME  # Reset to remote state
```

## Agent Quality Loop Stuck

If an agent keeps scoring below 10/10 after multiple iterations:

1. Review the feedback being given - is it actionable?
2. Check if the issue is actually fixable (may need deferral)
3. Consider human intervention for complex edge cases
4. Document the blocker and move on

## Worktree Already Exists

```bash
fatal: '.worktrees/NAME' already exists
```

**Solutions:**
- Use different slug name
- Remove existing: `git worktree remove .worktrees/NAME`
- Or prune if stale: `git worktree prune`

## Branch Already Exists

```bash
fatal: a branch named 'fix/NAME' already exists
```

**Solutions:**
- Delete the branch: `git branch -D fix/NAME`
- Or use different branch name
- Check if work already exists on that branch
