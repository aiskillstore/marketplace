---
name: Fundamentals Gate
description: Verify code quality standards are met - naming, structure, DRY principles. Issues result in SUGGESTIONS for improvement.
---

# Gate 5: Fundamentals Review

> "Good code is not just code that works. It's code that others can work with."

## Purpose

This gate checks general code quality against engineering standards. Issues are SUGGESTIONS, not blockers — they're polish, not problems.

## Gate Status

- **PASS** — Code quality is solid
- **SUGGESTIONS** — Minor improvements recommended

---

## Gate Questions

### Question 1: Naming Clarity
> "Would a new developer understand what `[variable/function]` does from its name alone?"

**Looking for:**
- Descriptive, intention-revealing names
- No abbreviations or single letters
- Boolean prefixes (is, has, can)
- Function verbs (get, set, handle)

### Question 2: Function Focus
> "Can you describe what this function does in one sentence without using 'and'?"

**Looking for:**
- Single responsibility
- Reasonable size (under 30 lines)
- Clear input/output relationship
- No hidden side effects

### Question 3: Code Reuse
> "I see this pattern in a few places. Is it intentional duplication or should it be extracted?"

**Looking for:**
- Awareness of duplication
- Appropriate abstraction (rule of three)
- Not over-engineering for one-time use

---

## Fundamentals Checklist

### Naming
- [ ] Variables are descriptive (no `temp`, `data`, `x`)
- [ ] Booleans prefixed with `is`, `has`, `can`, `should`
- [ ] Functions start with verbs
- [ ] No unnecessary abbreviations
- [ ] Consistent naming patterns

### Functions
- [ ] Single responsibility
- [ ] Under 30 lines (generally)
- [ ] Fewer than 4 parameters
- [ ] Early returns instead of deep nesting
- [ ] No magic numbers (use named constants)

### Structure
- [ ] Related code grouped together
- [ ] Appropriate file organization
- [ ] Clear separation of concerns
- [ ] Consistent formatting

### Comments
- [ ] Explain WHY, not WHAT
- [ ] No commented-out code (delete it)
- [ ] No obvious comments (`// increment counter`)
- [ ] Complex logic documented

---

## Response Templates

### If PASS

```
✅ FUNDAMENTALS GATE: PASSED

Code quality is solid:
- Naming is clear and consistent
- Functions are focused
- Good structure overall

All gates passed! Let's move to code review...
```

### If SUGGESTIONS

```
💡 FUNDAMENTALS GATE: SUGGESTIONS

A few polish items for consideration:

**Suggestion 1: [Naming]**
`const d = new Date()` → `const createdAt = new Date()`
Why: Descriptive names help future readers

**Suggestion 2: [Function size]**
`processOrder()` is 80 lines. Consider splitting into:
- `validateOrder()`
- `calculateTotal()`
- `saveOrder()`

**Suggestion 3: [Magic number]**
`if (status === 2)` → `if (status === STATUS.ACTIVE)`
Why: Named constants are self-documenting

These are suggestions, not blockers. The code works — this is about polish.
Proceed to code review? Or address these first?
```

---

## Common Issues to Check

### 1. Unclear Naming
```
❌ const d = new Date();
   const temp = getUser();
   const flag = true;

✅ const createdAt = new Date();
   const currentUser = getUser();
   const isAuthenticated = true;
```

### 2. Magic Numbers
```
❌ if (status === 2) { ... }
   setTimeout(fn, 86400000);

✅ const STATUS = { ACTIVE: 2, INACTIVE: 1 };
   if (status === STATUS.ACTIVE) { ... }

   const ONE_DAY_MS = 24 * 60 * 60 * 1000;
   setTimeout(fn, ONE_DAY_MS);
```

### 3. Deep Nesting
```
❌ function check(user) {
     if (user) {
       if (user.active) {
         if (user.role === 'admin') {
           return true;
         }
       }
     }
     return false;
   }

✅ function check(user) {
     if (!user) return false;
     if (!user.active) return false;
     if (user.role !== 'admin') return false;
     return true;
   }
```

### 4. God Functions
```
❌ function processOrder(order) {
     // 100+ lines of validation, calculation, saving, emailing...
   }

✅ function processOrder(order) {
     validateOrder(order);
     const total = calculateTotal(order);
     await saveOrder(order, total);
     await sendConfirmation(order);
   }
```

### 5. Meaningless Comments
```
❌ // Increment counter
   counter++;

   // Get user
   const user = getUser();

✅ // Rate limit: max 100 requests per minute per user
   if (requestCount >= 100) {
     throw new RateLimitError();
   }
```

---

## Socratic Fundamentals Questions

Instead of pointing out fixes, ask:

1. "What does `d` stand for? Would a new developer know?"
2. "What does the number 2 mean in this context?"
3. "Can you describe this function without saying 'and'?"
4. "I see this pattern three times — is that intentional?"
5. "Would you understand this comment in 6 months?"

---

## Standards Reference

See detailed patterns in:
- `/standards/global/naming-conventions.md`
- `/standards/global/error-handling.md`
- `/standards/frontend/component-architecture.md`

---

## Naming Quick Reference

| Type | Pattern | Example |
|------|---------|---------|
| Variable | camelCase, descriptive | `userEmail`, `isLoading` |
| Boolean | is/has/can/should prefix | `isActive`, `hasPermission` |
| Function | verb + noun | `getUser()`, `handleSubmit()` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_URL` |
| Class | PascalCase | `UserService`, `ApiClient` |

---

## When to Skip Suggestions

Not every suggestion needs addressing:

- **Prototype code** — Polish can wait
- **Time pressure** — Ship working code, polish later
- **Minimal impact** — If it's just style preference
- **Existing patterns** — Match codebase conventions even if imperfect

Fundamentals are about growth, not perfection. Note suggestions for learning, but don't block shipping.
