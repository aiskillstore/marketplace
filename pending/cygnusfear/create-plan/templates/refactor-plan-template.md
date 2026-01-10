# Refactor: [What's Being Refactored]

## Summary
[2-3 sentences: What code is being refactored and why]

## Type
Refactor

## Status
Todo

---

## Context

### Why Refactor?
[Technical debt, maintainability issues, or architectural improvements needed]

### Current Problems
[Specific issues with current implementation]

### Desired Outcome
[How code will be better after refactoring]

---

## CLAUDE.md Compliance

### Naming Conventions
- [Relevant naming rules]

### Architecture Requirements
- [Architectural patterns to follow]

### Type Requirements
- [Type guidelines]

---

## Existing Types

### Types to Reuse
- `TypeName` from `path/to/file.ts` - Usage

### Types to Consolidate
- [Types that can be merged or simplified]

### Type Guidelines
- ❌ No `any` types
- ❌ Eliminate `unknown` where possible
- ✅ Strengthen typing

---

## Impact Analysis

### Files to Modify
- `path/to/file.ts` - Refactoring changes

### Files to Consolidate
- Merge `file1.ts` + `file2.ts` → `file-new.ts`

### Files to Delete
- `path/to/redundant-file.ts` - No longer needed

### Dependencies Affected
- [What needs updating due to refactor]

### Breaking Changes
- [Any API changes, how to handle]

---

## Implementation Steps

### Step 1: [Preparation]
**File**: `path/to/file.ts`
**Action**: [What to do]
**Why**: [Reason]
**Details**:
- [Detail]

### Step 2: [Core Refactoring]
[Continue pattern]

### Step 3: [Cleanup]
[Remove old code]

---

## REMOVAL SPECIFICATION

### Code to Remove

#### From `path/to/file.ts`
- **Lines X-Y**: `[old implementation]`
  - **Why**: Being replaced by refactored version
  - **Replacement**: Step X
  - **Dependencies**: [What calls this]

#### Files to Delete
- `path/to/old-pattern-file.ts`
  - **Why**: Consolidated into new structure
  - **Replacement**: [Where functionality moved]

### Removal Checklist
- [ ] Old implementations removed
- [ ] Redundant files deleted
- [ ] Dead code eliminated
- [ ] All references updated

---

## Anti-Patterns to Avoid

❌ **Never Include**:
- Keeping old code "temporarily"
- Both old and new implementations running
- Gradual migration code
- Backward compatibility layers

✅ **Always Do**:
- Complete refactor in one pass
- Delete old code immediately
- Update all usages together

---

## Validation Criteria

### Pre-Implementation
- [ ] Current code fully understood
- [ ] Better pattern identified
- [ ] All usages found
- [ ] Impact assessed

### Post-Implementation
- [ ] All steps completed
- [ ] Old code removed
- [ ] TypeScript passes
- [ ] Linting passes
- [ ] Tests pass
- [ ] Behavior unchanged (unless intentional)
- [ ] Code quality improved
