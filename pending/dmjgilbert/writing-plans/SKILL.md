---
name: writing-plans
description: Create detailed implementation plans with granular tasks. Use before implementing features or complex changes.
---

# Writing Implementation Plans

Create detailed plans for engineers with minimal codebase familiarity. Break work into granular, testable tasks following TDD principles.

## When to Use

- Before implementing new features
- Before complex refactoring
- When work spans multiple files/components
- When coordinating multi-agent work

## Plan Location

Save all plans to: `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Plan Structure

### Header (Required)

```markdown
# Plan: [Feature Name]

**Goal:** [One sentence describing what this achieves]

**Architecture:** [2-3 sentences on approach]

**Tech Stack:** [Relevant technologies]

**Files Affected:**

- `path/to/file1.ts` - [what changes]
- `path/to/file2.ts` - [what changes]
```

### Task Format

Each task = single 2-5 minute action:

```markdown
## Task 1: [Descriptive Name]

**Action:** Create | Modify | Test

**Files:**

- Create: `src/components/Button.tsx`
- Test: `src/components/Button.test.tsx`

**Steps:**

1. Write failing test for [behavior]
2. Verify test fails with expected error
3. Implement minimal code to pass
4. Verify test passes
5. Commit: `test(button): add click handler test`

**Verification:**

- [ ] Test fails initially
- [ ] Test passes after implementation
- [ ] No other tests broken
```

### Task Granularity

Each step should be:

- Single action (one file, one change)
- Independently verifiable
- Following TDD (test first)
- Committable

**Too big:** "Implement authentication system"
**Right size:** "Write failing test for login validation"

## Design Principles

- **DRY** - Don't Repeat Yourself
- **YAGNI** - You Aren't Gonna Need It (no speculative features)
- **TDD** - Test first, always

## After Writing Plan

Offer execution options:

1. **Subagent-Driven:** Execute in current session with fresh subagent per task
2. **Parallel Session:** User opens new session with executing-plans skill

## Example Plan

```markdown
# Plan: Add User Avatar Component

**Goal:** Display user avatar with fallback initials

**Architecture:** React component with image loading state, fallback to initials derived from user name

**Tech Stack:** React, TypeScript, Tailwind CSS

**Files Affected:**

- `src/components/Avatar.tsx` - new component
- `src/components/Avatar.test.tsx` - tests
- `src/components/index.ts` - export

## Task 1: Create Avatar Test File

**Action:** Create
**Files:** `src/components/Avatar.test.tsx`

**Steps:**

1. Create test file with describe block
2. Write failing test: renders initials when no image
3. Verify test fails (component doesn't exist)

**Verification:**

- [ ] Test file created
- [ ] Test fails with "Cannot find module"

## Task 2: Create Basic Avatar Component

**Action:** Create
**Files:** `src/components/Avatar.tsx`

**Steps:**

1. Create component that renders initials
2. Accept `name` prop, extract initials
3. Verify test from Task 1 passes

**Verification:**

- [ ] Component renders
- [ ] Test passes
- [ ] Initials display correctly
```
