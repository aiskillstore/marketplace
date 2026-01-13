# Task Templates for Agent Coordination

Use these templates when creating tasks for autonomous coding agents.

---

## Bug Fix Task

```markdown
# Bug: [Brief description]

## Problem

[Clear description of what is broken]

- Expected behavior: [What should happen]
- Actual behavior: [What currently happens]
- Impact: [Users affected, frequency]

## Context

- First reported: [Date/source]
- Related issues: #123, #456
- Affected files: `src/components/Login.tsx`

## Reproduction Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Investigation Guidance

1. Check [specific file/function]
2. Look for [specific pattern/error]
3. Verify [specific condition]

## Acceptance Criteria

- [ ] Bug no longer reproducible with repro steps
- [ ] Root cause identified and fixed
- [ ] Regression test added
- [ ] No new warnings/errors introduced
- [ ] CI passes

## Out of Scope

- Refactoring unrelated code
- Performance optimizations
- UI polish beyond the fix
```

---

## Feature Task

```markdown
# Feature: [Brief description]

## Overview

[What this feature does and why it's needed]

## User Story

As a [role], I want [capability] so that [benefit].

## Requirements

### Must Have

- [ ] Requirement 1
- [ ] Requirement 2

### Nice to Have

- [ ] Optional enhancement

## Technical Approach

1. [Implementation step 1]
2. [Implementation step 2]
3. [Implementation step 3]

## Files to Modify

- `src/components/NewFeature.tsx` - New component
- `src/api/endpoints.ts` - Add endpoint
- `src/types/index.ts` - Add types

## Dependencies

- Requires: [Any prerequisites]
- API endpoint: [If applicable]

## Acceptance Criteria

- [ ] Feature works as described
- [ ] Unit tests cover main paths
- [ ] Documentation updated
- [ ] No performance regression
- [ ] CI passes

## Out of Scope

- [Explicitly list what NOT to do]
```

---

## Chore/Refactor Task

```markdown
# Chore: [Brief description]

## Motivation

[Why this maintenance work is needed]

- Technical debt addressed: [Specific debt]
- Benefit: [Improvement gained]

## Scope

### Include

- [File/module 1]
- [File/module 2]

### Exclude

- [What not to touch]

## Approach

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Verification

- [ ] Existing tests pass
- [ ] No behavior changes
- [ ] Code review approved
- [ ] CI passes

## Risks

- [Potential risk and mitigation]
```

---

## Investigation Task

```markdown
# Investigate: [Brief description]

## Question

[What needs to be understood/discovered]

## Context

- Triggered by: [Issue/observation]
- Deadline: [If time-sensitive]

## Investigation Areas

1. [Area to investigate]
2. [Area to investigate]
3. [Area to investigate]

## Expected Deliverables

- [ ] Summary of findings
- [ ] Root cause identified (if applicable)
- [ ] Recommended next steps
- [ ] Follow-up tasks created (if needed)

## Resources

- Relevant logs: [Location]
- Related code: [Files]
- Documentation: [Links]
```

---

## Migration Task

```markdown
# Migration: [Brief description]

## Overview

[What is being migrated and why]

## Current State

- Version/system: [Current]
- Issues: [Problems with current]

## Target State

- Version/system: [Target]
- Benefits: [Improvements]

## Migration Steps

1. [ ] [Step 1]
2. [ ] [Step 2]
3. [ ] [Step 3]

## Rollback Plan

1. [How to revert if needed]

## Verification

- [ ] All functionality works post-migration
- [ ] Performance acceptable
- [ ] No data loss
- [ ] Rollback tested

## Timeline

- Start: [Date]
- Expected completion: [Date]
- Rollback window: [Duration]
```

---

## Quick Reference: Task Title Prefixes

| Prefix         | Use When                             |
| -------------- | ------------------------------------ |
| `Bug:`         | Something is broken                  |
| `Feature:`     | New capability                       |
| `Chore:`       | Maintenance, deps, config            |
| `Refactor:`    | Code improvement, no behavior change |
| `Docs:`        | Documentation only                   |
| `Test:`        | Test coverage improvement            |
| `Investigate:` | Research, discovery                  |
| `Migration:`   | Version/system upgrade               |

---

## Tips for Writing Agent-Friendly Tasks

### Be Specific

```text
Bad:  "Fix the login bug"
Good: "Bug: Login button unresponsive on Safari iOS - check touch event handlers in LoginButton.tsx"
```

### Include File Paths

```text
Bad:  "Update the API"
Good: "Feature: Add /api/users/export endpoint in src/routes/users.ts"
```

### Define Done Clearly

```text
Bad:  "Make it work"
Good: "Acceptance Criteria:
       - [ ] Endpoint returns CSV
       - [ ] Auth required
       - [ ] Rate limited to 10/min
       - [ ] Test coverage >80%"
```

### Set Boundaries

```text
Bad:  "Improve the codebase"
Good: "Chore: Extract validation logic from UserForm.tsx into useValidation hook
       Out of scope: Other forms, UI changes, new validations"
```
