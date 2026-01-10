---
name: code-review-standards
description: Code review framework and criteria. References security-sentinel for security checks. Use when performing code reviews or defining review standards.
allowed-tools: Read, Grep
---

# Code Review Standards

## When to Use
- Reviewing pull requests
- Performing code reviews
- Defining review criteria
- Establishing review process

## Overview

Code review standards ensure consistent, thorough reviews that catch bugs before they reach production. This skill aggregates criteria from specialized skills.

## Review Framework

### 4-Level Severity Classification

1. **CRITICAL** 🔴 - Must fix before merge
   - Security vulnerabilities
   - Data loss risks
   - Authentication bypasses
   - SQL injection risks

2. **HIGH** 🟠 - Should fix before merge
   - TypeScript strict mode violations
   - Missing error handling
   - Performance issues (N+1 queries)
   - Missing input validation

3. **MEDIUM** 🟡 - Fix soon (can merge with plan)
   - Code quality issues
   - Missing tests
   - Poor naming
   - Missing documentation

4. **LOW** 🟢 - Nice to have
   - Style suggestions
   - Optimization opportunities
   - Refactoring ideas

---

## Review Checklist

### 1. Correctness
→ See: [correctness-criteria.md](./correctness-criteria.md)

- [ ] Logic is correct for all test cases
- [ ] Edge cases handled (null, empty, max, min)
- [ ] Error conditions properly handled
- [ ] Return types match function signatures
- [ ] Async operations properly awaited
- [ ] No race conditions
- [ ] No off-by-one errors

---

### 2. Security
→ See: [security-sentinel skill](../security-sentinel/SKILL.md)
→ See: [security-checklist.md](./security-checklist.md)

**CRITICAL - Must check every review:**

- [ ] No hardcoded secrets
- [ ] Input validation with Zod (ALL inputs)
- [ ] Authentication checked on protected routes
- [ ] Authorization enforced (resource ownership)
- [ ] SQL injection prevented (using Drizzle)
- [ ] XSS prevented (no dangerouslySetInnerHTML without sanitization)
- [ ] CSRF protection on state-changing operations
- [ ] No sensitive data in logs
- [ ] Passwords hashed (bcrypt, 12+ rounds)
- [ ] JWTs properly verified

**For complete security criteria:**
→ [security-sentinel/SKILL.md](../security-sentinel/SKILL.md)

---

### 3. TypeScript Quality
→ See: [typescript-strict-guard skill](../typescript-strict-guard/SKILL.md)

- [ ] No `any` types
- [ ] No `@ts-ignore` without extensive comment
- [ ] No `!` non-null assertions without comment
- [ ] Explicit types on all function parameters
- [ ] Explicit return types on all functions
- [ ] Type guards used for unknown types
- [ ] Proper use of generics
- [ ] No implicit any

---

### 4. Testing
→ See: [quality-gates/test-patterns.md](../quality-gates/test-patterns.md)

- [ ] Tests exist for new code
- [ ] Tests follow AAA pattern
- [ ] Coverage meets thresholds (75%/90%)
- [ ] UI tests verify DOM state (not just mocks)
- [ ] E2E tests for visual changes
- [ ] No skipped tests without reason
- [ ] Tests are independent
- [ ] Tests clean up after themselves

---

### 5. Performance
→ See: [performance-criteria.md](./performance-criteria.md)

- [ ] No N+1 query problems
- [ ] Database queries optimized
- [ ] Async operations parallelized where possible
- [ ] Large datasets paginated
- [ ] Images optimized
- [ ] No unnecessary re-renders
- [ ] Expensive calculations memoized

---

### 6. Code Quality
→ See: [maintainability-rules.md](./maintainability-rules.md)

- [ ] No console.log in production code
- [ ] No commented-out code
- [ ] No TODO without GitHub issue
- [ ] Functions have single responsibility
- [ ] Variable names are descriptive
- [ ] No dead code
- [ ] No duplicated logic
- [ ] Proper error messages

---

### 7. Architecture Compliance
→ See: [architecture-patterns skill](../architecture-patterns/SKILL.md)

- [ ] Correct pattern chosen for problem
- [ ] Pattern implemented correctly
- [ ] No pattern violations
- [ ] Follows Next.js best practices
- [ ] Server vs Client Components correct
- [ ] State management appropriate

---

## Review Process

### Step 1: Pre-Review (2 minutes)

1. Read PR description
2. Understand what changed and why
3. Check CI/CD status (tests, build, coverage)
4. Identify high-risk areas (auth, payments, data handling)

### Step 2: Security Review (5 minutes)

**For ALL PRs:**
- Check for hardcoded secrets
- Verify input validation
- Check authentication/authorization

**For Auth/API/Data PRs:**
- Run security-sentinel skill
- Review OWASP Top 10 criteria
- Check for injection risks

→ [security-checklist.md](./security-checklist.md)

### Step 3: Code Review (10-20 minutes)

1. **Correctness**: Does it work as intended?
2. **TypeScript**: Strict mode compliance?
3. **Testing**: Adequate coverage and quality?
4. **Performance**: Any obvious issues?
5. **Quality**: Readable, maintainable code?
6. **Architecture**: Follows established patterns?

### Step 4: Write Feedback (5 minutes)

Use severity levels and templates:
→ [review-templates.md](./review-templates.md)

**Format:**
```markdown
## 🔴 CRITICAL Issues

- [ ] [Security] Hardcoded API key in auth.ts:45
  - **Risk**: API key exposed in version control
  - **Fix**: Move to environment variable
  - **File**: src/lib/auth.ts:45

## 🟠 HIGH Issues

- [ ] [TypeScript] Using `any` type in processData()
  - **Issue**: No type safety
  - **Fix**: Define explicit interface
  - **File**: src/utils/process.ts:12

## 🟡 MEDIUM Issues

- [ ] [Testing] Missing tests for error cases
  - **Coverage**: Only happy path tested
  - **Needed**: Test null input, invalid format
  - **File**: tests/unit/process.test.ts

## 🟢 LOW Issues / Suggestions

- Consider extracting helper function for readability
```

### Step 5: Verdict

**Choose one:**

- ✅ **APPROVE** - No critical/high issues
- 🔄 **REQUEST CHANGES** - Critical or multiple high issues
- 💬 **COMMENT** - Questions or low/medium issues only

---

## Review Templates

### Security Issue Template

```markdown
🔴 **[Security] [Vulnerability Type]**

**Location**: `src/path/file.ts:123`

**Issue**: [Description of vulnerability]

**Risk**: [What could go wrong]

**Fix**:
```typescript
// Suggested fix
```

**Reference**: [OWASP link or skill reference]
```

### TypeScript Issue Template

```markdown
🟠 **[TypeScript] [Issue Type]**

**Location**: `src/path/file.ts:45`

**Issue**: [What's wrong]

**Fix**:
```typescript
// Current (bad)
function process(data: any) { }

// Suggested (good)
function process(data: ProcessData): ProcessedResult { }
```

**Reference**: typescript-strict-guard skill
```

### Performance Issue Template

```markdown
🟡 **[Performance] [Issue Type]**

**Location**: `src/path/file.ts:78`

**Issue**: N+1 query problem in getUserProjects()

**Impact**: Linear time complexity, slow for large datasets

**Fix**:
```typescript
// Use join instead of separate queries
const projects = await db
  .select()
  .from(projectsTable)
  .leftJoin(usersTable, eq(projectsTable.userId, usersTable.id))
```
```

---

## Common Review Patterns

### Code Smells

**Long Functions**
```typescript
// 🔴 BAD: 100+ line function
function processEverything() {
  // ... 100 lines
}

// ✅ GOOD: Extracted helpers
function processEverything() {
  const validated = validateInput()
  const processed = processData(validated)
  const saved = saveToDatabase(processed)
  return saved
}
```

**Deeply Nested Logic**
```typescript
// 🔴 BAD: 4+ levels of nesting
if (user) {
  if (user.projects) {
    if (user.projects.length > 0) {
      if (user.projects[0].status === 'active') {
        // ...
      }
    }
  }
}

// ✅ GOOD: Early returns
if (!user) return
if (!user.projects || user.projects.length === 0) return
if (user.projects[0].status !== 'active') return
// ...
```

**Magic Numbers**
```typescript
// 🔴 BAD: Unexplained numbers
setTimeout(callback, 3600000)

// ✅ GOOD: Named constants
const ONE_HOUR_MS = 60 * 60 * 1000
setTimeout(callback, ONE_HOUR_MS)
```

---

## Progressive Disclosure

1. **SKILL.md** (this file) - Review framework overview
2. **security-checklist.md** - OWASP Top 10 checklist
3. **performance-criteria.md** - Performance review criteria
4. **maintainability-rules.md** - Code quality rules
5. **review-templates.md** - Feedback templates

---

## Integration with Other Skills

Code review aggregates criteria from:
- **security-sentinel** - Security vulnerability checks
- **typescript-strict-guard** - Type safety validation
- **quality-gates** - Quality checkpoint framework
- **architecture-patterns** - Pattern compliance
- **nextjs-15-specialist** - Next.js best practices

---

## Example Review

```markdown
# Code Review: Add User Authentication

## Summary
Adds JWT-based authentication with login/logout endpoints.

## 🔴 CRITICAL Issues

### 1. Hardcoded JWT Secret
**File**: `src/lib/auth.ts:12`
**Issue**: JWT secret is hardcoded as "secret123"
**Risk**: Anyone can forge JWTs
**Fix**:
```typescript
- const secret = "secret123"
+ const secret = process.env.JWT_SECRET
+ if (!secret) throw new Error('JWT_SECRET not set')
```

## 🟠 HIGH Issues

### 2. Missing Input Validation
**File**: `src/app/api/auth/login/route.ts:15`
**Issue**: User input not validated before use
**Fix**: Add Zod schema validation
```typescript
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

const validated = loginSchema.parse(body)
```

## 🟡 MEDIUM Issues

### 3. Missing Tests
**File**: `tests/integration/auth.test.ts`
**Issue**: No tests for error cases
**Needed**:
- Test invalid email format
- Test wrong password
- Test expired JWT

## Verdict

🔄 **REQUEST CHANGES** - Fix critical and high issues before merge.

Once fixed, this will be a solid authentication implementation.
```

---

## See Also

- security-checklist.md - OWASP Top 10 checklist
- performance-criteria.md - Performance review guide
- maintainability-rules.md - Code quality rules
- review-templates.md - Feedback templates
- ../security-sentinel/SKILL.md - Security patterns
- ../quality-gates/SKILL.md - Quality framework
