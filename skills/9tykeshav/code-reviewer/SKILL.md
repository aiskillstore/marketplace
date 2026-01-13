---
name: code-reviewer
description: Use when asked to review MERN stack code - comprehensive code reviewer that checks project health, security, maintainability, performance, testing, and architecture. Combines general code quality analysis with MERN-specific expertise.
---

# Code Reviewer

## Overview

Comprehensive code review: General intelligence + MERN specialization.

**Philosophy:** Check project health FIRST, then dive into code. A 6,000-line file is a problem regardless of what's in it.

## Review Workflow

### Phase 0: Project Health (Do This First)

Before reading any code, assess project health:

1. **Build status:** Run `tsc --noEmit` or check for compilation errors
2. **Project docs:** Read README, any STATUS/BUGS/TODO files - look for deployment blockers
3. **Test health:** Do tests exist? Check `package.json` scripts, look for test directories
4. **File sizes:** `find src -name "*.ts" -o -name "*.tsx" | xargs wc -l | sort -n | tail -20`
5. **Dependencies:** Check for `npm audit` issues, unusual deps (Angular in React?)

**Stop here if:** Build is broken, docs say "DO NOT DEPLOY", or critical blockers found. Report immediately.

### Phase 1: Scope Detection

1. Identify scope from context:
   - Full repo → Broad review, sample key files
   - Feature/PR → All changed files
   - Single file → Deep dive
2. Detect layers: React? Express? MongoDB? Node.js?
3. If ambiguous → ask user

### Phase 2: Review by Priority

| Priority | Focus | Severity |
|----------|-------|----------|
| 0. Blockers | Build failures, "DO NOT DEPLOY", broken deploys | STOP |
| 1. Security | Injection, auth, secrets, XSS | Critical |
| 2. Maintainability | God files, complexity, duplication | Critical/Important |
| 3. Performance | N+1, missing indexes, re-renders | Important |
| 4. Testing | No tests, low coverage, flaky tests | Important |
| 5. Best Practices | Error handling, async patterns | Suggestion |
| 6. Architecture | API design, state management | Suggestion |

Load reference files ON-DEMAND when you hit MERN-specific edge cases.

### Phase 3: Report

Use the output format below. Offer to fix starting with Critical.

## Output Format

```markdown
# MERN Code Review

## Project Health
- Build: [Compiles / X errors / Not checked]
- Tests: [X passing / X failing / None found]
- Blockers: [Any deployment blockers from docs]
- Large files: [Files >500 lines]

## Scope
[What was reviewed]

## Summary
- Files reviewed: X
- Issues: X Critical, X Important, X Suggestions

## Critical (Must Fix)
### [C1] Category: Title
**File:** `path:line`
**Why:** [1-2 sentences]
**Fix:** [Code or instruction]

## Important (Should Fix)
### [I1] Category: Title
...

## Suggestions
- `file:line` - Note

## What's Good
- [Positive observations]

## Verdict
[Ready to deploy / Blocked / Needs fixes] - [1 sentence reason]

---
**Ready to fix these?** Starting with Critical issues.
```

## Checklists

**Minimum required checks.** Report other issues you find during review.

### Blockers (Check First)
- [ ] Project compiles without errors
- [ ] No "DO NOT DEPLOY" or similar warnings in docs
- [ ] No critical security advisories in `npm audit`

### Security
- [ ] No `$where`, `$ne`, `$regex` with user input (NoSQL injection/ReDoS)
- [ ] No `dangerouslySetInnerHTML` without DOMPurify
- [ ] JWT in httpOnly cookies, not localStorage
- [ ] Secrets in env vars, not hardcoded (check config files too, not just code)
- [ ] Helmet middleware configured
- [ ] CORS properly restricted
- [ ] Rate limiting on auth endpoints
- [ ] Input validation on all endpoints
- [ ] No `eval()` or `new Function()` with user input

### Maintainability
- [ ] No file >500 lines (god files)
- [ ] No function >50 lines
- [ ] No class/component with >20 methods
- [ ] No deep nesting (>4 levels)
- [ ] No copy-paste blocks >10 lines (DRY)
- [ ] Clear naming (no cryptic abbreviations)
- [ ] Consistent code style

### Performance
- [ ] No N+1 queries (use populate/$lookup)
- [ ] Indexes on frequently queried fields
- [ ] `.lean()` for read-only Mongoose queries
- [ ] No `fs.readFileSync` in request handlers
- [ ] React.memo on expensive components
- [ ] useCallback/useMemo where beneficial
- [ ] Pagination on list endpoints

### Testing
- [ ] Tests exist for critical paths (auth, payments, core flows)
- [ ] Test coverage reasonable (>50% for services)
- [ ] No skipped/commented-out tests
- [ ] Tests actually assert behavior (not just "doesn't crash")
- [ ] Mocks don't hide real integration issues

### Best Practices
- [ ] Async errors handled (try/catch or error middleware)
- [ ] useEffect cleanup functions present
- [ ] No floating promises (unhandled async)
- [ ] Middleware order correct (body-parser before routes, error handler last)
- [ ] Environment variables validated at startup
- [ ] Graceful shutdown handlers

### Architecture
- [ ] Consistent API response format
- [ ] Service layer between controllers and DB
- [ ] Types aligned frontend/backend
- [ ] No circular dependencies
- [ ] Clear module boundaries
- [ ] No god components (React >300 lines)
- [ ] State management appropriate for complexity

## Red Flags (Immediate Critical)

These are automatic Critical issues:

- `eval()`, `new Function()` with user input
- Hardcoded secrets/credentials in code
- `dangerouslySetInnerHTML` without sanitization
- JWT/auth tokens in localStorage
- Missing auth middleware on protected routes
- `$where` clause with user input
- File >1000 lines
- "DO NOT DEPLOY" in project docs
- `npm audit` critical vulnerabilities

## Scope Calibration

| Scope | Phase 0 | Code Depth | Focus |
|-------|---------|------------|-------|
| Single file | Skip | Deep | All checklists on that file |
| Last commit | Quick | Medium | Changed lines + immediate context |
| Feature/PR | Quick | Medium | All changed files |
| Full repo | Full | Broad | Sample key files, architecture |

## Reference Files

Load ONLY when you encounter MERN-specific patterns you need to verify:

| When to Load | Reference |
|--------------|-----------|
| NoSQL query security question | [security.md](reference/security.md) |
| React hooks/re-render issue | [react.md](reference/react.md) |
| Express middleware question | [express.md](reference/express.md) |
| MongoDB schema/index question | [mongodb.md](reference/mongodb.md) |
| Node.js async/memory issue | [nodejs.md](reference/nodejs.md) |
| API design/auth flow question | [fullstack.md](reference/fullstack.md) |

**Do NOT load all references upfront.** They're for edge cases, not general review.

## Don't

- Don't claim "no issues found" without actually searching for them
- Don't report on code you haven't read
- Don't classify style issues as Critical

## Examples

### God File Detection
```
Found: EventService.ts - 6,165 lines
→ Critical [C1] Maintainability: God file
→ Recommend split into: EventQueryService, EventBookingService,
   EventGuestService, EventInviteService (~500 lines each)
```

### Missing Health Check
```
Found: CURRENT_STATUS_AND_BUGS.md contains "DO NOT DEPLOY"
→ Critical [C1] Blocker: Deployment blocked by known issues
→ Fix TypeScript errors in EditEventModal.tsx before proceeding
```

### Security + Specific Fix
```
Found: No Helmet middleware in index.ts
→ Critical [C2] Security: Missing security headers
→ Fix: npm install helmet && app.use(helmet())
```
