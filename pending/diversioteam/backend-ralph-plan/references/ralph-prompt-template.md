# RALPH-PROMPT.md Template

Replace all `{{PLACEHOLDER}}` values with actual project values.

---

# {{PLAN_TITLE}} - Ralph Execution Prompt

You are working through a structured implementation plan with {{TASK_COUNT}} tasks.

## Step 1: Orient Yourself (Do This First Every Iteration)

Before writing any code, understand where you are:

```bash
# What iteration is this?
head -5 .claude/ralph-loop.local.md

# What's already been done? (Your previous work is here)
git log --oneline -15

# Current plan status
grep -E "^\| [0-9]+" PLAN.md
```

Read `PLAN.md` to identify:
- Which tasks show `completed` ✓
- Which task is `in-progress` (this is your current focus)
- If no task is `in-progress`, start the first `pending` one

**Critical:** Do not repeat work that's already committed. Check git history.

## Step 2: Work on Current Task

### Find your task
```bash
# Find the in-progress or first pending task
grep -l "in-progress\|pending" *.md | head -1
```

### Read the task file completely
Understand:
- **Goal** - What you're building
- **Dependencies** - What must exist first
- **Scope** - What's in/out
- **Checklist** - Specific implementation steps
- **Tests** - What tests to write
- **Completion Criteria** - Definition of done

### Implement incrementally
1. Work through checklist items one by one
2. Write tests alongside implementation
3. Check off items in the task file as you complete them
4. Run tests frequently to catch issues early

## Step 3: Verify Before Marking Complete

After implementing, run ALL verification steps:

```bash
# 1. Pre-commit hooks
/pre-commit
# ❌ STOP if fails - fix all issues

# 2. Linting
{{LINT_CMD}} {{APP_PATH}}{{MODULE_PATH}} --fix
{{FORMAT_CMD}} {{APP_PATH}}{{MODULE_PATH}}
# ❌ STOP if errors remain

# 3. Type checking
{{TYPE_CMD}} {{APP_PATH}}{{MODULE_PATH}}
# ❌ STOP if type errors

# 4. Django checks
{{DJANGO_CMD}} check
# ❌ STOP if issues

# 5. ALL feature tests (not just this task)
{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}} -v
# ❌ STOP if ANY test fails

# 6. Coverage check
{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}} \
  --cov={{APP_PATH}}{{MODULE_PATH}} --cov-report=term-missing
# ❌ STOP if coverage < {{COVERAGE_TARGET}}%

# 7. No shortcuts
grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" {{APP_PATH}}{{MODULE_PATH}} \
  && echo "❌ Found shortcuts - remove them" || echo "✓ Clean"
```

**If any check fails:** Fix it. Do not proceed with failures.

## Step 4: Commit and Update Progress

Only after ALL verifications pass:

```bash
# Stage changes
git add -A

# Commit with descriptive message
git commit -m "Complete {{TASK_NUM}} - {{TASK_NAME}}

- {{WHAT_WAS_IMPLEMENTED}}
- {{TESTS_ADDED}}
- Coverage: {{COVERAGE}}%

Plan: {{PLAN_SLUG}}"
```

Then update `PLAN.md`:
1. Change task status from `in-progress` to `completed`
2. Fill in Task Completion Tracker row (✓ for each passing gate)
3. Update Progress percentage and bar

## Step 5: Proceed to Next Task

Immediately start the next `pending` task. Do not stop.

Loop back to Step 2 for the next task.

## Forbidden Actions

You must NEVER:
- Skip any verification step
- Leave TODO/FIXME/XXX/HACK comments in code
- Proceed when tests are failing
- Use `noqa` or `type: ignore` to silence errors
- Use `Any` type hints in business logic (external API payloads excepted)
- Commit without running all tests
- Move to next task before current passes all gates
- Output completion promise with tasks remaining

## Handling Blockers

If genuinely stuck on a task:

1. **Document it** - Add `## Blockers` section to the task file:
   ```markdown
   ## Blockers
   - **Blocked by:** [Description of what's blocking]
   - **Attempted:** [What you tried]
   - **Needs:** [What would unblock this]
   ```

2. **Check if you can skip** - If task dependencies allow, mark as blocked
   and move to an independent task

3. **Keep trying** - The loop will bring you back with fresh context.
   Sometimes stepping away and returning helps.

**Never lie to exit.** Do not output the completion promise to escape.
The loop is designed to persist until genuine completion.

## Completion: When ALL {{TASK_COUNT}} Tasks Are Done

After the final task passes verification:

### Final Validation
```bash
# All tasks completed?
grep -c "completed" PLAN.md  # Should be {{TASK_COUNT}}

# Full test suite
{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}}

# All quality gates
{{LINT_CMD}} {{APP_PATH}}{{MODULE_PATH}}
{{TYPE_CMD}} {{APP_PATH}}{{MODULE_PATH}}
{{DJANGO_CMD}} check
{{DJANGO_CMD}} migrate --check

# Zero shortcuts
! grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" {{APP_PATH}}{{MODULE_PATH}}
# ↑ Must return 0 (no matches found)
```

### Signal Completion
Only when ALL checks pass:

```
<promise>ALL {{TASK_COUNT}} {{PLAN_SLUG_UPPER}} TASKS COMPLETE</promise>
```

**The promise text must match exactly.** Only output when genuinely done.
