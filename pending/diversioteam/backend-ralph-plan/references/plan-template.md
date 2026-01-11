# PLAN.md Template for Backend RALPH Plans

This template extends the base `plan-directory` PLAN.md with quality tracking
tables and Ralph execution instructions.

---

# {{PLAN_TITLE}}

> **Status:** `in-progress`
> **Created:** {{DATE}}
> **Last Updated:** {{DATE}}

## Quick Start

```
/plan-directory:run {{PLAN_SLUG}}
```

Or with custom iteration limit:
```
/plan-directory:run {{PLAN_SLUG}} --max-iterations {{MAX_ITERATIONS}}
```

## Overview

{{OVERVIEW}}

## Goals

{{GOALS}}

## Locked Decisions

{{LOCKED_DECISIONS}}

## Execution Order

| Order | Task | Dependencies | Critical Path |
|-------|------|--------------|---------------|
{{EXECUTION_ORDER_ROWS}}

## Tasks

| # | Task | Status | File |
|---|------|--------|------|
{{TASK_ROWS}}

## Progress

**Completed: 0/{{TASK_COUNT}} tasks (0%)**

```
[░░░░░░░░░░] 0%
```

## Task Completion Tracker

Track quality gate results for each task.

| Task | Status | Lint | Types | Tests | Coverage | Regression |
|------|--------|------|-------|-------|----------|------------|
{{TRACKER_ROWS}}

**Legend:**
- Lint: `{{LINT_CMD}}` passes
- Types: `{{TYPE_CMD}}` passes
- Tests: Task tests pass (count in parentheses)
- Coverage: ≥{{COVERAGE_TARGET}}% on new code
- Regression: ALL previous tests still pass

## Quality Gates

Every task must pass these gates before proceeding:

| Gate | Command | Requirement |
|------|---------|-------------|
| Pre-commit | `/pre-commit` | All hooks pass |
| Lint | `{{LINT_CMD}} {{APP_PATH}}{{MODULE_PATH}}` | Zero errors |
| Types | `{{TYPE_CMD}} {{APP_PATH}}{{MODULE_PATH}}` | Zero errors |
| Tests | `{{TEST_CMD}} -k {{TEST_FILTER}} {{TEST_CONFIG}}` | 100% pass |
| Coverage | `--cov={{APP_PATH}}{{MODULE_PATH}}` | ≥{{COVERAGE_TARGET}}% |
| Django | `{{DJANGO_CMD}} check` | No issues |

## Final Validation Checklist

Run when all tasks are complete:

**Task Completion:**
{{TASK_COMPLETION_CHECKLIST}}

**Quality Gates:**
- [ ] `{{LINT_CMD}} {{APP_PATH}}{{MODULE_PATH}}` → zero errors
- [ ] `{{TYPE_CMD}} {{APP_PATH}}{{MODULE_PATH}}` → zero errors
- [ ] `{{TEST_CMD}} {{APP_PATH}}tests/{{MODULE_PATH}} -k {{TEST_FILTER}} {{TEST_CONFIG}}` → all pass
- [ ] `{{DJANGO_CMD}} check` → no issues
- [ ] `{{DJANGO_CMD}} migrate --check` → no pending migrations

**Code Quality:**
- [ ] `! grep -rE "TODO|FIXME|XXX|HACK|noqa|type: ignore" {{APP_PATH}}{{MODULE_PATH}}` → no matches

**Documentation:**
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Complex logic has inline comments

## Follow-ups (Not in Scope)

{{FOLLOWUPS}}

## Notes

{{NOTES}}
