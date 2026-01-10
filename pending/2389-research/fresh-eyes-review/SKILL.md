---
name: fresh-eyes-review
description: This skill should be used as a mandatory final sanity check before git commit, PR creation, or declaring work done. Triggers on "commit", "push", "PR", "pull request", "done", "finished", "complete", "ship", "deploy", "ready to merge". Catches security vulnerabilities, logic errors, and business rule bugs that slip through despite passing tests.
---

# Fresh-Eyes Review

## Core Principle

**"NO COMMIT WITHOUT FRESH-EYES REVIEW FIRST"**

This represents a final quality gate executed *after* implementation completion, passing tests, and peer review. The discipline applies universally, even without explicit skill activation.

## Key Distinctions

Fresh-eyes review differs fundamentally from testing and code review:

| Approach | Focus | Blind Spots |
|----------|-------|-------------|
| **Testing** | Validates expected behavior | Can't test for unknown edge cases |
| **Code review** | Patterns and quality | Reviewer trusts author's intent |
| **Fresh-eyes** | Deliberate re-reading with psychological distance | Catches what you thought was correct |

**Critical insight**: "100% test coverage and passing scenarios" can coexist with "critical bugs" waiting discovery.

## Required Process

### Step 1 - Announce Commitment

Explicitly declare: "Starting fresh-eyes review of [N] files. This will take 2-5 minutes."

This announcement creates accountability and reframes your mindset from implementation to audit.

### Step 2 - Security Vulnerability Checklist

Review all touched files for security issues:

| Vulnerability | What to Check |
|---------------|---------------|
| **SQL Injection** | All database queries use parameterized statements, never string concatenation |
| **XSS** | All user-provided content is escaped before rendering in HTML |
| **Path Traversal** | File paths are validated, `../` sequences rejected or normalized |
| **Command Injection** | Shell commands don't include unsanitized user input |
| **IDOR** | Resources are access-controlled, not just unguessable IDs |
| **Auth Bypass** | Every protected endpoint checks authentication and authorization |

**Example finding:**
```typescript
// Before: SQL injection vulnerability
const user = await db.query(`SELECT * FROM users WHERE id = '${userId}'`);

// After: Parameterized query
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

### Step 3 - Logic Error Checklist

| Error Type | What to Check |
|------------|---------------|
| **Off-by-one** | Array indices, loop bounds, pagination limits |
| **Race conditions** | Concurrent access to shared state, async operations |
| **Null/undefined** | Every `.` chain could throw; defensive checks present? |
| **Type coercion** | `==` vs `===`, implicit conversions |
| **State mutations** | Unexpected side effects on input parameters? |
| **Error swallowing** | Empty catch blocks, ignored promise rejections |

**Example finding:**
```typescript
// Before: Off-by-one in pagination
const hasMore = results.length < pageSize;

// After: Correct boundary
const hasMore = results.length === pageSize;
```

### Step 4 - Business Rule Checklist

| Check | Questions |
|-------|-----------|
| **Calculations** | Do formulas match requirements exactly? Currency rounding correct? |
| **Conditions** | AND vs OR logic correct? Negations applied properly? |
| **Edge cases** | Empty input, single item, maximum values, zero values? |
| **Error messages** | User-friendly? Leak no sensitive information? |
| **Default values** | Sensible defaults when optional fields omitted? |

**Example finding:**
```typescript
// Before: Tax calculation uses wrong rounding
const tax = price * 0.08;

// After: Proper currency rounding
const tax = Math.round(price * 0.08 * 100) / 100;
```

### Step 5 - Performance Checklist

| Issue | What to Check |
|-------|---------------|
| **N+1 queries** | Loops that make database calls should be batched |
| **Unbounded loops** | Maximum iterations, timeout protection |
| **Memory leaks** | Event listeners removed, streams closed, references cleared |
| **Missing indexes** | Queries filter/sort on indexed columns? |
| **Large payloads** | Pagination implemented? Response size bounded? |

### Step 6 - Fix Immediately

Address findings before declaring completion:
1. Make the fix
2. Add test covering the issue (if not present)
3. Re-run full test suite
4. Re-run linter/type checker

### Step 7 - Declare Results

Mandatory announcement:

```
Fresh-eyes complete. [N] issues found and fixed:
- [Brief description of each issue and fix]
```

Include this even for zero findings—it proves execution.

## Time Commitment

| File Count | Expected Duration |
|------------|-------------------|
| 1-3 files | 2 minutes |
| 4-10 files | 3-4 minutes |
| 10+ files | 5 minutes max |

**Warning signs:**
- Faster than 2 minutes suggests insufficient depth
- More than 5 minutes indicates scope creep—stay focused on the changed code

## Resistance Patterns to Reject

The following rationalizations must be explicitly rejected:

| Rationalization | Reality |
|-----------------|---------|
| "Tests are comprehensive" | Tests validate design, not correctness |
| "I'm confident it's correct" | Confidence is inversely correlated with bugs |
| "Partner is waiting" | 3 minutes now saves 3 hours debugging later |
| "Production is blocked" | Rushing causes the outages being rushed to fix |
| "Senior dev already approved" | They reviewed intent, not implementation details |
| "It's just a small change" | Small changes cause large outages |

**These circumstances represent precisely when critical bugs escape into production.**

## Example Workflow

```
User: "I'm done implementing the auth feature, let me commit"
Assistant: [Triggers fresh-eyes-review skill]

Starting fresh-eyes review of 4 files. This will take 2-5 minutes.

[Reviews auth.ts for security]
- Found: Missing input validation on email field
- Fixed: Added email format validation

[Reviews handler.ts for logic]
- Found: Off-by-one error in pagination
- Fixed: Changed < to <= in boundary check

[Reviews db.ts for performance]
- No issues found

[Reviews api.ts for business rules]
- No issues found

Re-running tests... All tests pass

Fresh-eyes complete. 2 issues found and fixed.
```