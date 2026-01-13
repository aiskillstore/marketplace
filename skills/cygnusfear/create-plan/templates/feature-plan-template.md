# [Feature Name]

## Summary
[2-3 sentences: What feature is being added and why it's needed]

## Type
Feature

## Status
Todo

---

## Context

### Why This Feature?
[Business or technical motivation]

### Current State
[What exists now that this feature builds upon or replaces]

### Desired State
[What will exist after implementation]

---

## CLAUDE.md Compliance

### Naming Conventions
- [Relevant naming rules from CLAUDE.md]

### Architecture Requirements
- [Relevant architectural patterns]

### Type Requirements
- [Type-related guidelines]

### Other Guidelines
- [Any other applicable rules]

---

## Existing Types

### Types to Reuse
- `TypeName` from `path/to/file.ts` - Purpose

### Types to Create
- `NewType` - Why needed (only if no existing type works)

### Type Guidelines
- ❌ No `any` types
- ❌ No `unknown` without justification
- ✅ Strict typing everywhere

---

## Impact Analysis

### Files to Modify
- `path/to/file.ts` - What changes and why

### Files to Create
- `path/to/new-file.ts` - Purpose and justification

### Files to Delete
- `path/to/old-file.ts` - Reason for removal

### Dependencies Affected
- [What depends on changed code]

### Breaking Changes
- [Any breaking changes and mitigation]

---

## Implementation Steps

### Step 1: [First Task]
**File**: `path/to/file.ts`
**Action**: [Specific action]
**Why**: [Reason]
**Details**:
- [Implementation detail]

### Step 2: [Next Task]
[Continue pattern]

---

## REMOVAL SPECIFICATION

### Code to Remove

#### From `path/to/file.ts`
- **Lines X-Y**: `[code snippet]`
  - **Why**: [Reason]
  - **Replacement**: [What replaces it]
  - **Dependencies**: [What uses it]

#### Files to Delete
- `path/to/old-file.ts`
  - **Why**: [Reason]
  - **Replacement**: [Where functionality moved]
  - **Dependencies**: [What imports it]

### Removal Checklist
- [ ] All deprecated functions removed
- [ ] All old files deleted
- [ ] All imports updated
- [ ] All references updated
- [ ] No dead code remains

---

## Anti-Patterns to Avoid

❌ **Never Include**:
- Feature flags for this change
- Fallback to old implementation
- Migration period code
- Gradual rollout mechanisms

✅ **Always Do**:
- Complete, clean implementation
- Full removal of old code
- All changes at once

---

## Validation Criteria

### Pre-Implementation
- [ ] CLAUDE.md reviewed
- [ ] Existing types identified
- [ ] Impact analyzed
- [ ] Naming verified

### Post-Implementation
- [ ] All steps completed
- [ ] REMOVAL SPEC satisfied
- [ ] TypeScript passes
- [ ] Linting passes
- [ ] Tests pass
- [ ] No `any` types
- [ ] CLAUDE.md compliant
