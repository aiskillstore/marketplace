# Code Review Feedback Template

## Review Summary

**PR Title**: [Title]
**PR Number**: #[Number]
**Author**: [Author Name]
**Reviewer**: [Your Name]
**Review Date**: YYYY-MM-DD

**Overall Assessment**: ✅ Approve / 💬 Comment / 🔄 Request Changes

---

## Executive Summary

<!-- High-level assessment in 2-3 sentences -->

[Brief summary of what the PR does well and main areas for improvement]

---

## Detailed Feedback

### 🎉 Strengths

<!-- Highlight positive aspects of the code -->

1. **[Aspect]**: [Specific praise]
   - Example: Excellent error handling in `processPayment` function
   - The try/catch blocks handle all edge cases gracefully

2. **[Aspect]**: [Specific praise]

3. **[Aspect]**: [Specific praise]

---

### 🔴 Blocking Issues

<!-- Issues that must be fixed before merge -->

#### Issue 1: [Title]

**Severity**: 🔴 Critical / 🟠 High
**Location**: `file/path.ts:123-145`
**Label**: `bug` / `security` / `breaking`

**Problem:**
[Detailed description of the issue]

**Impact:**
[What happens if this is not fixed]

**Suggested Fix:**
```typescript
// Before (current code)
const user = await getUser(userId);
return user.email; // Crashes if user is null

// After (suggested fix)
const user = await getUser(userId);
if (!user) {
  throw new UserNotFoundError(userId);
}
return user.email;
```

**Additional Context:**
[Any relevant background information]

---

#### Issue 2: [Title]

[Same structure as Issue 1]

---

### 🟡 Suggestions

<!-- Improvements that enhance quality but are not blocking -->

#### Suggestion 1: [Title]

**Severity**: 🟡 Medium / 🟢 Low
**Location**: `file/path.ts:67-89`
**Label**: `suggestion` / `refactor`

**Current Code:**
```typescript
// Example of current implementation
```

**Suggested Improvement:**
```typescript
// Proposed improvement
```

**Reasoning:**
[Why this change improves the code - readability, performance, maintainability, etc.]

**Effort**: Low / Medium / High

---

### ❓ Questions

<!-- Clarification questions for the author -->

1. **Q:** Why did you choose to use a Map instead of an object in `UserCache`?
   - **Context**: [Relevant context]
   - **Concern**: [What you're unsure about]

2. **Q:** [Question text]

---

### 💡 Nitpicks (Optional)

<!-- Minor, non-blocking suggestions -->

1. **nitpick [non-blocking]**: Consider renaming `userData` to `userProfile`
   - Location: `src/user/service.ts:45`
   - Reason: More specific and aligns with domain language

2. **nitpick [non-blocking]**: Add blank line between imports and code
   - Location: Multiple files
   - Reason: Improves readability

---

## Specific File Reviews

### `src/services/payment.ts`

**Overall**: ✅ Looks good / ⚠️ Needs work

**Line-by-Line Comments:**

**Lines 23-45: processPayment function**
```
praise: Excellent use of async/await here!

The error handling is comprehensive and the retry logic
is a great addition for handling transient failures.
```

**Lines 67-89: calculateTotal function**
```
issue: Missing validation for negative prices

If a product has a negative price (data corruption scenario),
this will calculate an incorrect total.

Add validation:
```typescript
if (items.some(item => item.price < 0)) {
  throw new InvalidPriceError('Product price cannot be negative');
}
```
```

**Lines 120-135: refundPayment function**
```
question: Should we add idempotency here?

If this function is called multiple times for the same payment,
will it create duplicate refunds? Consider adding an idempotency
check using the payment ID.
```

---

### `src/tests/payment.test.ts`

**Overall**: ✅ Looks good / ⚠️ Needs work

**Comments:**
- ✅ Good coverage of happy path scenarios
- ⚠️ Missing tests for error scenarios (API timeout, invalid response)
- 💡 Consider adding parameterized tests for different payment amounts

---

## Test Coverage Review

**Current Coverage**: X%
**Target Coverage**: Y%
**Gap**: ±Z%

**Well-Tested:**
- ✅ Happy path scenarios
- ✅ Input validation
- ✅ [Other areas]

**Needs More Tests:**
- ⚠️ Error handling paths
- ⚠️ Edge cases (null, empty, max values)
- ⚠️ Integration with payment gateway

**Suggested Tests:**
```typescript
describe('processPayment', () => {
  it('should retry on transient failures', async () => {
    // Test implementation
  });

  it('should throw on permanent failures', async () => {
    // Test implementation
  });

  it('should handle timeout gracefully', async () => {
    // Test implementation
  });
});
```

---

## Performance Review

**Concerns**: ✅ None / ⚠️ Some / 🔴 Major

**Observations:**
- [ ] No obvious performance issues
- [ ] Database queries are optimized (no N+1)
- [ ] Caching is used appropriately
- [ ] No memory leaks detected

**Performance Notes:**
[Specific observations about performance]

**Suggested Improvements:**
[If any performance optimizations are recommended]

---

## Security Review

**Concerns**: ✅ None / ⚠️ Some / 🔴 Critical

**Security Checklist:**
- [ ] Input validation and sanitization
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Authentication checks on protected routes
- [ ] Authorization checks (users can only access their own data)
- [ ] No hardcoded secrets or API keys
- [ ] Sensitive data encrypted
- [ ] HTTPS enforced

**Security Notes:**
[Specific security observations]

---

## Documentation Review

**Documentation Quality**: ✅ Good / ⚠️ Needs Work / 🔴 Missing

**Checklist:**
- [ ] Code has inline comments for complex logic
- [ ] Public APIs are documented (JSDoc/docstrings)
- [ ] README updated (if applicable)
- [ ] CHANGELOG updated (if applicable)
- [ ] Migration guide provided (if breaking changes)

**Documentation Gaps:**
[List any missing or unclear documentation]

---

## Architecture & Design

**Alignment with Architecture**: ✅ Good / ⚠️ Concerns / 🔴 Conflicts

**Observations:**
- Does this PR follow existing patterns?
- Are there any architectural concerns?
- Does it introduce new patterns (are they justified)?
- Is there unnecessary coupling?

**Suggestions:**
[Any architectural improvements]

---

## Checklist for Author

Before marking as resolved, ensure:

- [ ] All blocking issues addressed
- [ ] Questions answered
- [ ] Tests added for new code
- [ ] Documentation updated
- [ ] Self-review completed
- [ ] CI/CD checks passing

---

## Next Steps

### Immediate Actions Required

1. **[Action 1]**: [Description]
   - Owner: Author
   - Priority: High
   - Estimated time: [X hours/days]

2. **[Action 2]**: [Description]

### Follow-Up Work (Optional)

- [ ] [Follow-up item 1] - Create issue #[number]
- [ ] [Follow-up item 2] - Create issue #[number]

---

## Timeline

- **Review Requested**: [Date]
- **Initial Review Completed**: [Date]
- **Changes Requested**: [Date]
- **Re-Review Needed**: Yes / No
- **Target Merge Date**: [Date]

---

## Additional Notes

[Any other context, thoughts, or suggestions for the author]

---

## Review Decision

<!-- Choose one -->

### ✅ Approve

**Reasoning**: [Why this PR is ready to merge]

**Conditions** (if any):
- [ ] [Condition that must be met before merge]

---

### 💬 Comment

**Reasoning**: [Why you're providing comments without blocking]

**Non-Blocking Suggestions**: X
**Questions**: Y

---

### 🔄 Request Changes

**Reasoning**: [Why changes are required before merge]

**Blocking Issues**: X
**Required Changes**: [Summary]

**Estimated Rework Time**: [X hours/days]

---

**Reviewer Signature**: [Your Name]
**Date**: YYYY-MM-DD

---

## For Re-Review

<!-- Fill this out when re-reviewing after changes -->

**Changes Reviewed**: [Date]
**Status**: ✅ All issues addressed / 🔄 Some issues remain

**Remaining Issues:**
- [ ] [Issue description]

**New Comments:**
[Any new feedback after reviewing changes]

**Final Decision**: ✅ Approve / 🔄 Request additional changes
