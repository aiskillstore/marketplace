# Fix: [Bug Description]

## Summary
[2-3 sentences: What bug is being fixed and its impact]

## Type
Fix

## Status
Todo

---

## Context

### Bug Description
[Detailed description of the bug]

### Current Behavior
[What happens now (incorrect behavior)]

### Expected Behavior
[What should happen (correct behavior)]

### Root Cause
[Technical reason for the bug]

---

## CLAUDE.md Compliance

### Naming Conventions
- [Any relevant naming rules]

### Architecture Requirements
- [Relevant architectural patterns]

### Type Requirements
- [Type-related guidelines]

---

## Existing Types

### Types to Reuse
- `TypeName` from `path/to/file.ts` - Purpose

### Type Issues Contributing to Bug
- [Any type-related causes of the bug]

### Type Improvements
- [How to strengthen typing to prevent similar bugs]

---

## Impact Analysis

### Files to Modify
- `path/to/buggy-file.ts` - Fix implementation

### Root Cause Location
- `path/to/file.ts:line` - Where bug originates

### Affected Code Paths
- [What execution paths hit this bug]

### Side Effects
- [Any other code affected by the fix]

---

## Implementation Steps

### Step 1: [Fix Root Cause]
**File**: `path/to/file.ts`
**Action**: [Specific fix]
**Why**: [How this addresses root cause]
**Details**:
- [Implementation detail]

### Step 2: [Update Related Code]
[Address any side effects]

### Step 3: [Add Safeguards]
[Prevent similar bugs in future]

---

## REMOVAL SPECIFICATION

### Code to Remove

#### From `path/to/file.ts`
- **Lines X-Y**: `[buggy code]`
  - **Why**: Contains the bug
  - **Replacement**: Step 1 implementation
  - **Dependencies**: [What calls this]

### Removal Checklist
- [ ] Buggy code removed
- [ ] All instances of bug pattern fixed
- [ ] No related issues remain

---

## Anti-Patterns to Avoid

❌ **Never Include**:
- Workarounds instead of proper fix
- Keeping buggy code with flags
- Temporary patches
- "Good enough" solutions

✅ **Always Do**:
- Fix root cause properly
- Remove buggy code completely
- Add prevention measures
- Verify complete fix

---

## Validation Criteria

### Pre-Implementation
- [ ] Bug reproduced
- [ ] Root cause identified
- [ ] Fix approach validated
- [ ] Side effects considered

### Post-Implementation
- [ ] Bug no longer reproduces
- [ ] All test cases pass
- [ ] TypeScript passes
- [ ] Linting passes
- [ ] No regressions
- [ ] Prevention measures added

### Test Cases
- [ ] Original bug scenario
- [ ] Edge cases
- [ ] Related scenarios
- [ ] Regression tests
