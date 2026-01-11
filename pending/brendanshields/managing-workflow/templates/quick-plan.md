# Quick Plan Template

Use for simple features (bug fixes, single-file changes, small enhancements).

## Template

```markdown
# Plan: {title}

## Approach

{1-2 sentences describing the solution}

## Changes

| File | Change | Reason |
|------|--------|--------|
| {path} | {what changes} | {why} |

## Tasks

- [ ] T001: {primary task} [P1]
- [ ] T002: {secondary task if any} [P2]
- [ ] T003: Verify change works [P1]

## Risks

{Any risks or considerations, or "None - straightforward change"}
```

## When to Use

- Bug fixes with clear cause
- Single file changes
- Config updates
- Documentation updates
- Small refactors (< 3 files)

## When NOT to Use

- New features with multiple components
- Architecture changes
- Changes affecting > 5 files
- Anything needing design decisions

## Example

```markdown
# Plan: Fix login timeout error

## Approach

Increase session timeout from 30s to 120s and add retry logic.

## Changes

| File | Change | Reason |
|------|--------|--------|
| src/auth/session.ts | Increase timeout constant | 30s too short for slow networks |
| src/auth/login.ts | Add retry on timeout | Graceful recovery |

## Tasks

- [ ] T001: Update SESSION_TIMEOUT to 120000 [P1]
- [ ] T002: Add retry logic with max 3 attempts [P1]
- [ ] T003: Test with slow network simulation [P1]

## Risks

None - backward compatible change
```
