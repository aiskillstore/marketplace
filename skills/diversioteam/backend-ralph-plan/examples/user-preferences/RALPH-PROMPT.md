# User Preferences - Ralph Execution Prompt

You are working through a structured plan. Your goal is to complete ALL 4 tasks.

## First: Orient Yourself

Before doing anything, check your progress:

```bash
# What iteration is this?
head -5 .claude/ralph-loop.local.md

# What's already been done?
git log --oneline -10

# What's the current plan status?
grep -A 20 "## Tasks" PLAN.md
```

Read PLAN.md to understand:
- Which tasks are `completed`
- Which task is `in-progress`
- What comes next

**Do not repeat work that's already committed.** Check git history first.

## Your Mission

Complete all 4 tasks in `PLAN.md`:

1. **001 - Preferences Model** (foundation)
2. **002 - Preferences Service** (depends on 001)
3. **003 - API Endpoints** (depends on 001, 002)
4. **004 - Caching Layer** (depends on 002)

Work on one task at a time. Follow the execution order.

## For Each Task

### Before Starting
- Read the task file (e.g., `001-preferences-model.md`)
- Understand the Goal, Scope, and Checklist
- Check if any work was already done (git log, existing files)

### While Working
- Implement each checklist item
- Write tests as you go
- Check off items in the task file as you complete them

### After Completing
Run the verification checklist:

```bash
# 1. Pre-commit
/pre-commit

# 2. Lint
.bin/ruff check accounts/preferences/ --fix
.bin/ruff format accounts/preferences/

# 3. Types
.bin/ty accounts/preferences/

# 4. Django checks
.bin/django check

# 5. Tests
.bin/pytest accounts/tests/preferences/ -k "preferences" --dc=TestLocalApp -v

# 6. Coverage
.bin/pytest accounts/tests/preferences/ -k "preferences" --dc=TestLocalApp \
  --cov=accounts/preferences/ --cov-report=term-missing

# 7. No shortcuts
grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" accounts/preferences/ \
  && echo "❌ Found shortcuts - remove them" || echo "✓ Clean"
```

**If ANY check fails:** Fix it before proceeding. Do not skip.

### Commit and Update
```bash
# Commit the task
git add -A
git commit -m "Complete 00X - Task Name

- What was implemented
- Tests added

Plan: user-preferences"

# Update PLAN.md
# - Mark task as `completed` in Tasks table
# - Fill in Tracker row (Lint ✓, Types ✓, etc.)
# - Update Progress percentage
```

### Move to Next Task
Immediately proceed to the next `pending` task.

## Forbidden Actions

Never:
- Skip verification steps
- Leave TODO/FIXME comments
- Proceed with failing tests
- Use `noqa` or `type: ignore`
- Commit without running tests
- Move to next task before current is 100% complete
- Output the completion promise when tasks remain

## If You're Stuck

1. Re-read the task file requirements
2. Check existing patterns in `accounts/` directory
3. Read test failures carefully
4. Try a different approach
5. Document the blocker in the task file's `## Blockers` section

**Do not lie to exit.** If genuinely blocked, add a Blockers section and continue
trying. The loop will bring you back with fresh context.

## When ALL 4 Tasks Are Complete

1. Verify final state:
```bash
# All tasks completed?
grep "completed" PLAN.md | wc -l  # Should be 4

# All gates pass?
.bin/ruff check accounts/preferences/
.bin/ty accounts/preferences/
.bin/pytest -k "preferences" --dc=TestLocalApp
.bin/django check

# No shortcuts?
! grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" accounts/preferences/  # Should return 0 (no matches)
```

2. Output the completion promise:
```
<promise>ALL 4 USER-PREFERENCES TASKS COMPLETE</promise>
```

**Only output this when genuinely complete.** The loop verifies the promise text exactly.
