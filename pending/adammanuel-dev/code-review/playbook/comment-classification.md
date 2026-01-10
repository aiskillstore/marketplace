# Comment Classification Guide

<context>
This guide provides detailed taxonomy for code review comments. Using consistent classification reduces author-reviewer friction, sets clear expectations, and helps prioritize work. Every comment should have a classification tag.
</context>

## Why Classify Comments?

**Without classification:**
- Authors don't know what's blocking vs. optional
- Reviewers' intent is ambiguous
- Teams argue about nitpicks while critical issues lurk
- Review cycles drag on unnecessarily

**With classification:**
- Clear priority: What must be fixed vs. what's nice to have
- Reduced friction: Authors know reviewer's intent
- Faster resolution: Critical items addressed first
- Better relationships: Praise is explicit, not just implied

## Classification System

### [critical] - Must Fix Before Merge

**Definition:** Issues that would cause security vulnerabilities, data loss, system outages, or breaking changes without migration paths.

**When to use:**
- Security vulnerabilities (auth bypass, injection, XSS, etc.)
- Data corruption or loss risks
- Breaking API changes without migration
- Core logic incorrectly implemented (will fail in production)
- Missing critical functionality that makes feature broken

**When NOT to use:**
- Performance issues (unless causes outages)
- Missing tests (use `[issue]`)
- Style issues (use `[nit]`)
- Suggestions for better approaches (use `[suggestion]`)

**Examples:**

```markdown
[critical] This endpoint doesn't validate user permissions. Any authenticated user could access other users' private data.

**Fix:**
``​`typescript
if (currentUser.id !== targetUserId && !currentUser.hasRole('admin')) {
  throw new ForbiddenError('Cannot access other user data');
}
``​`
```

```markdown
[critical] SQL injection vulnerability. User input is concatenated directly into query.

**Current (vulnerable):**
``​`sql
const query = `SELECT * FROM users WHERE email = '${userInput}'`;
``​`

**Fixed:**
``​`typescript
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [userInput]);
``​`
```

```markdown
[critical] This deletes user data without checking if they have active subscriptions. Could cause billing errors and data inconsistency.

**Add check:**
``​`typescript
const activeSubscriptions = await getActiveSubscriptions(userId);
if (activeSubscriptions.length > 0) {
  throw new Error('Cannot delete user with active subscriptions');
}
``​`
```

**Tone:** Serious but helpful. Explain the impact and provide solutions.

---

### [issue] - Should Fix

**Definition:** Bugs that may not always manifest, missing error handling, significant logic errors, or missing important tests.

**When to use:**
- Logic bugs in edge cases
- Missing error handling
- Potential null/undefined crashes
- Missing tests for core functionality
- Incorrect behavior in uncommon scenarios
- Significant performance problems (N+1 queries, unnecessary loops)

**When NOT to use:**
- Minor performance improvements (use `[suggestion]`)
- Cosmetic issues (use `[nit]`)
- Architectural disagreements (use `[suggestion]` or `[question]`)

**Examples:**

```markdown
[issue] This will crash if the API returns an empty array. Add a safety check:

``​`typescript
if (!results || results.length === 0) {
  return defaultValue;
}
``​`
```

```markdown
[issue] No error handling for network failures. If the API is down, this will crash the app.

**Add try-catch:**
``​`typescript
try {
  const data = await fetchUserData(userId);
  return data;
} catch (error) {
  logger.error('Failed to fetch user data', { userId, error });
  throw new ServiceUnavailableError('Unable to fetch user data');
}
``​`
```

```markdown
[issue] The `createOrder` function has no tests. Please add tests covering:
- Successful order creation
- Invalid product ID
- Insufficient inventory
- Payment processing failure

These are critical paths that need test coverage.
```

```markdown
[issue] N+1 query problem. This will make a database call for each user in the loop (could be hundreds).

**Fix with a single query:**
``​`typescript
const userIds = orders.map(o => o.userId);
const users = await getUsersByIds(userIds);
const userMap = new Map(users.map(u => [u.id, u]));

orders.forEach(order => {
  order.user = userMap.get(order.userId);
});
``​`
```

**Tone:** Constructive. Explain the problem and suggest solutions.

---

### [suggestion] - Nice to Have

**Definition:** Improvements that would make code better but aren't necessary for correctness or safety.

**When to use:**
- Better patterns or approaches
- Performance optimizations (non-critical)
- Refactoring opportunities
- Code organization improvements
- Extracting reusable logic
- Simplification opportunities

**When NOT to use:**
- Critical bugs (use `[critical]` or `[issue]`)
- Required changes (use `[issue]`)
- Trivial style issues (use `[nit]`)

**Examples:**

```markdown
[suggestion] Consider using `Array.map()` for better readability:

**Current:**
``​`typescript
const names = [];
for (const user of users) {
  names.push(user.name);
}
``​`

**Suggested:**
``​`typescript
const names = users.map(u => u.name);
``​`

But the current approach works fine—your call!
```

```markdown
[suggestion] This validation logic is duplicated in three places. Consider extracting into a shared utility:

``​`typescript
// utils/validation.ts
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
``​`

Then reuse in all three components. Not blocking, but would reduce duplication.
```

```markdown
[suggestion] This function is doing three distinct things. Consider splitting for better testability:

1. `validateOrderData(order)` - Validation logic
2. `calculateOrderTotal(order)` - Pricing logic
3. `saveOrder(order)` - Persistence logic

This would make unit testing each concern easier. But if you prefer keeping it together for this use case, that's fine too.
```

```markdown
[suggestion] Consider caching this API response. It's called frequently but data rarely changes. Could improve performance and reduce API costs.

``​`typescript
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function getCachedData(key) {
  if (cache.has(key) && Date.now() - cache.get(key).timestamp < CACHE_TTL) {
    return cache.get(key).data;
  }

  const data = await fetchData(key);
  cache.set(key, { data, timestamp: Date.now() });
  return data;
}
``​`

Not required, but could be a good optimization if performance becomes an issue.
```

**Tone:** Helpful and deferential. Make it clear author can choose.

---

### [nit] - Purely Cosmetic

**Definition:** Trivial issues that have no impact on functionality. Style preferences, typos, formatting.

**When to use:**
- Typos in comments or strings
- Formatting (should be automated, but if not...)
- Minor naming preferences
- Whitespace
- Comment wording

**When NOT to use:**
- Anything that affects behavior (use `[issue]`)
- Significant naming issues (use `[suggestion]`)

**Best practice: Batch multiple nits into one comment.** Don't leave 10 separate nit comments.

**Examples:**

```markdown
[nit] A few minor items (all non-blocking):
- Line 23: Typo in comment: "recieve" → "receive"
- Line 45: Extra blank line
- Line 67: Variable `data` could be more specific like `userData`
- Line 89: Inconsistent quote style (single vs double)

Feel free to fix or ignore—none of these block approval.
```

```markdown
[nit] Function name `doProcessing` could be more descriptive, like `processUserRegistration`. But it's clear enough in context.
```

**Tone:** Light and non-blocking. Make it very clear these don't matter.

**Warning:** Overuse of `[nit]` comments creates friction. If you have more than 3-4 nits, batch them or let them go. Prefer automating style via linting.

---

### [question] - Seeking Clarification

**Definition:** You're asking for understanding, not asserting something is wrong.

**When to use:**
- Understanding author's intent
- Asking about edge cases
- Requesting explanation of approach
- Verifying assumptions
- Curious about design decisions

**When NOT to use:**
- When you know something is wrong (use `[issue]` or `[critical]`)
- When you want to suggest an alternative (use `[suggestion]`)

**Examples:**

```markdown
[question] How does this handle the case where the user's session expires mid-request? Do we redirect to login or attempt token refresh?

I'm asking because I want to understand the edge case handling—not saying it's wrong.
```

```markdown
[question] Curious about the choice to use a Set instead of an Array here. Is it for O(1) lookups, or is there another reason?

Just trying to understand the data structure choice for my own learning.
```

```markdown
[question] I see we're using the builder pattern here. Is this establishing a new pattern for the codebase, or following an existing convention?

Want to make sure I understand the architectural direction.
```

```markdown
[question] Does this function need to handle the case where `config` is undefined? Or is that guaranteed to be set by the initialization logic?

Trying to understand the assumptions about input.
```

**Tone:** Genuinely curious, not accusatory. Make it clear you're seeking to learn, not implying wrongness.

**Helpful:** If author's response reveals the code is confusing, suggest adding a comment.

```markdown
[question] How does the retry logic work here?

*Author responds with detailed explanation*

Thanks for explaining! That makes sense. Would you consider adding a comment explaining the retry strategy? Future maintainers would benefit from that context.
```

---

### [praise] - Calling Out Good Work

**Definition:** Highlighting excellent patterns, clever solutions, or good practices.

**When to use:**
- Excellent design decisions
- Clever optimizations
- Great test coverage
- Clear, maintainable code
- Good documentation
- Thoughtful error handling

**When NOT to use:**
- Sarcastically (obviously)
- For trivial things that should be standard

**Examples:**

```markdown
[praise] Excellent use of the factory pattern here! Much cleaner than the previous approach and makes testing way easier.
```

```markdown
[praise] This error message is fantastic. It clearly explains what went wrong and how to fix it. Users will actually understand what happened instead of being confused.
```

```markdown
[praise] Love the comprehensive test coverage here, especially the edge case tests for empty arrays and null values. This gives me high confidence the code is correct.
```

```markdown
[praise] Great call extracting this into a shared utility. I can already think of two other places in the codebase that could use this.
```

```markdown
[praise] The type safety here is excellent. TypeScript will catch errors at compile time that would have been runtime bugs in the old code.
```

**Tone:** Genuine and specific. Don't just say "good job"—explain what's good and why.

**Impact:** Praise reinforces good patterns and builds positive team culture. Don't skip it.

---

## Combining Classifications

**You can use multiple classifications in one comment:**

```markdown
[issue] This will crash if `user` is null. Add a null check.

[suggestion] While you're at it, consider extracting the validation logic into a helper function since it's used in three places.
```

**Or keep them separate for clarity:**

```markdown
[issue] Missing null check on line 45. This could crash.

---

[suggestion] Separately, consider extracting the validation logic into a shared utility.
```

## Anti-Patterns

### ❌ Unclassified Comments

**Bad:**
> This could be better.

**What's wrong:** Author doesn't know if this blocks merge or is optional.

**Good:**
> [suggestion] Consider using a Map instead of an Array for O(1) lookups. Not required, but could improve performance if the dataset grows.

---

### ❌ Everything is [critical]

**Bad:**
> [critical] Variable naming is inconsistent
> [critical] Missing JSDoc comment
> [critical] Could use const instead of let

**What's wrong:** Dilutes meaning of "critical". Creates alert fatigue.

**Good:** Reserve `[critical]` for actual critical issues. Use `[nit]` or `[suggestion]` for these.

---

### ❌ No Explanation

**Bad:**
> [issue] This is wrong.

**What's wrong:** Doesn't explain why it's wrong or how to fix.

**Good:**
> [issue] This will fail when the array is empty. Add a check:
> ```typescript
> if (items.length === 0) return defaultValue;
> ```

---

### ❌ Aggressive Tone

**Bad:**
> [critical] This is a terrible approach. Why would you do this?

**What's wrong:** Hostile tone damages relationships.

**Good:**
> [issue] I'm concerned this approach might cause performance problems with large datasets. Could we discuss alternatives like pagination or caching?

---

### ❌ Blocking on Nits

**Bad:**
> Requesting changes because of typo in comment on line 45.

**What's wrong:** Delays merge for trivial issue.

**Good:**
> [nit] Typo on line 45: "recieve" → "receive"
>
> Everything else looks great! Approving now—feel free to fix the typo or leave it.

---

## Classification Decision Tree

```
Is this a security vulnerability, data loss risk, or breaking change?
├─ YES → [critical]
└─ NO → Continue

Will this cause incorrect behavior or crashes?
├─ YES → [issue]
└─ NO → Continue

Would this make code better but isn't necessary for correctness?
├─ YES → [suggestion]
└─ NO → Continue

Is this a cosmetic issue (typos, formatting, minor naming)?
├─ YES → [nit] (batch with others)
└─ NO → Continue

Are you asking a question to understand, not asserting wrongness?
├─ YES → [question]
└─ NO → Continue

Is this highlighting something good?
└─ YES → [praise]
```

---

## Examples by Category

### Security Issues
- [critical] SQL injection
- [critical] Missing authentication
- [critical] XSS vulnerability
- [issue] Missing rate limiting
- [issue] Sensitive data in logs

### Logic Issues
- [critical] Core algorithm incorrect
- [issue] Missing null check
- [issue] Edge case not handled
- [suggestion] Simplify complex conditional

### Testing
- [issue] No tests for critical function
- [issue] Test doesn't verify behavior
- [suggestion] Add edge case tests
- [praise] Excellent test coverage

### Performance
- [issue] N+1 query problem
- [issue] Unnecessary loop causing slowdown
- [suggestion] Consider caching
- [suggestion] Use more efficient data structure

### Code Quality
- [suggestion] Extract duplicated logic
- [suggestion] Simplify nested conditionals
- [nit] Rename variable for clarity
- [nit] Add comment explaining complex logic

### Documentation
- [issue] Public API missing JSDoc
- [suggestion] Add comment for complex algorithm
- [nit] Typo in comment
- [praise] Clear, helpful documentation

---

**Remember:** Classification is a tool for communication. The goal is to make your intent clear, reduce friction, and help authors prioritize work effectively. When in doubt, err on the side of being less severe—`[suggestion]` instead of `[issue]`, `[issue]` instead of `[critical]`.
