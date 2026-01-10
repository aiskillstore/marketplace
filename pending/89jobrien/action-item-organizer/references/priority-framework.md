---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: action-item-organizer
---

# Priority Classification Framework

This document provides comprehensive guidance for classifying action items into priority levels (P0-P3) across different domains.

## Core Priority Definitions

### P0 - Blockers (Critical)

Items that MUST be resolved before proceeding with deployment, merge, or next phase.

**Characteristics:**

- Prevents critical functionality
- Poses immediate security threat
- Causes data loss or corruption
- Violates compliance requirements
- Blocks other team members
- Creates production outage risk

**Time Sensitivity:** Immediate (hours, not days)

**Examples:**

- Security vulnerability exposing user data
- Critical bug causing system crashes
- Missing authentication on public API
- Data corruption in production database
- Compliance violation (GDPR, HIPAA, etc.)
- Broken build preventing deployment

### P1 - High Priority

Significant issues that should be addressed promptly but don't block immediate progress.

**Characteristics:**

- Major quality concerns
- Significant performance impact
- Important security concerns (not critical)
- Functional correctness issues
- High technical debt
- Affects user experience significantly

**Time Sensitivity:** Days to 1 week

**Examples:**

- SQL injection vulnerability in admin panel
- N+1 query problem causing slow page loads
- Missing error handling for critical operations
- Architectural issues affecting scalability
- Major code duplication across modules
- Incomplete test coverage for core features

### P2 - Medium Priority

Important improvements that enhance the system but aren't urgent.

**Characteristics:**

- Code quality improvements
- Moderate refactoring needs
- Documentation gaps
- Minor performance optimizations
- Test coverage improvements
- Usability enhancements

**Time Sensitivity:** Weeks to 1 month

**Examples:**

- Refactor complex function into smaller units
- Add JSDoc comments to public API
- Optimize database query (not causing issues yet)
- Improve error messages for clarity
- Add integration tests for new feature
- Update dependencies to latest versions

### P3 - Low Priority (Future)

Nice-to-have improvements and optimizations.

**Characteristics:**

- Code style and consistency
- Future enhancements
- Exploratory tasks
- Minor optimizations
- Cosmetic improvements
- Technical debt with low impact

**Time Sensitivity:** Months or backlog

**Examples:**

- Rename variables for consistency
- Add code comments for clarity
- Explore alternative libraries
- Micro-optimizations
- Refactor for future extensibility
- Update code style to match new standard

## Domain-Specific Priority Guides

### Security Issues

| Issue Type | Default Priority | Can be Lower If... | Must be Higher If... |
|------------|------------------|-------------------|---------------------|
| Public API without auth | P0 | Only used internally, behind VPN | Contains PII or financial data |
| SQL injection | P0 | Limited to admin users | Affects public endpoints |
| XSS vulnerability | P1 | Non-critical page | Can steal credentials |
| Hardcoded credentials | P0 | Development environment only | Production credentials |
| Missing input validation | P1 | Internal tools only | User-facing forms |
| Insecure randomness | P2 | Non-security context | Used for tokens/passwords |
| Missing rate limiting | P1 | Internal API | Public authentication endpoint |
| Outdated dependencies | P2 | No known vulnerabilities | Known critical CVE |

### Performance Issues

| Issue Type | Default Priority | Can be Lower If... | Must be Higher If... |
|------------|------------------|-------------------|---------------------|
| N+1 query problem | P1 | Small dataset (<100 rows) | Public-facing page |
| Missing database index | P1 | Table has <1000 rows | Slow query affecting UX |
| Memory leak | P0 | Development environment | Production server |
| Inefficient algorithm | P2 | Small input size | Used in hot path |
| Large bundle size | P2 | Internal tool | Customer-facing app |
| Blocking operations | P1 | Low traffic endpoint | High traffic API |
| Unnecessary re-renders | P2 | Simple component | Complex dashboard |

### Code Quality Issues

| Issue Type | Default Priority | Can be Lower If... | Must be Higher If... |
|------------|------------------|-------------------|---------------------|
| Code duplication | P2 | Small block (< 5 lines) | Business logic duplicated |
| Complex function | P2 | Well-tested, stable | Frequently modified |
| Missing error handling | P1 | Internal script | User-facing feature |
| Poor naming | P3 | Private function | Public API |
| Deeply nested logic | P2 | Rare edge case | Core business logic |
| Magic numbers | P3 | Used once | Used multiple times |
| Large file/class | P2 | Well-organized | Confusing to navigate |

### Testing Issues

| Issue Type | Default Priority | Can be Lower If... | Must be Higher If... |
|------------|------------------|-------------------|---------------------|
| No unit tests | P1 | Simple CRUD | Complex business logic |
| Flaky tests | P0 | Isolated test | Blocking CI/CD |
| No integration tests | P1 | Well-tested components | Critical user flow |
| Missing edge cases | P2 | Unlikely scenario | Known production issue |
| No error path tests | P1 | Trivial operation | Complex error handling |
| Low coverage | P2 | New experimental code | Core production code |

### Documentation Issues

| Issue Type | Default Priority | Can be Lower If... | Must be Higher If... |
|------------|------------------|-------------------|---------------------|
| Missing API docs | P1 | Internal API | Public/external API |
| Outdated README | P2 | Stable project | Frequent onboarding |
| No inline comments | P3 | Self-explanatory code | Complex algorithm |
| Missing architecture docs | P2 | Small project | Large codebase |
| No deployment guide | P1 | Single maintainer | Team deployment |
| Incomplete error codes | P2 | Internal tool | Customer-facing API |

## Priority Decision Framework

When in doubt, use this decision tree:

```
Does this prevent deployment or cause production issues?
├─ Yes → P0
└─ No → Continue

Does this affect security, data integrity, or core functionality?
├─ Yes → P0 or P1 (based on severity)
└─ No → Continue

Does this significantly impact user experience or performance?
├─ Yes → P1
└─ No → Continue

Does this affect code quality, maintainability, or technical debt?
├─ Yes → P2
└─ No → P3
```

## Priority Modifiers

Consider these factors that can adjust priority up or down:

### Increase Priority If

- Affects production environment
- Impacts many users
- Blocks other team members
- Has compliance implications
- Creates security risk
- Difficult to fix later
- Causes data loss/corruption

### Decrease Priority If

- Only affects development environment
- Rare edge case
- Internal tooling only
- Easy to fix later
- Low impact on users
- Workaround exists
- Not blocking any work

## Common Priority Mistakes

### Priority Inflation

Don't mark everything as P0. Reserve P0 for true blockers.

Bad: All 20 code review findings marked as P0
Good: 2 security issues are P0, rest distributed across P1-P3

### Priority Deflation

Don't downplay serious issues to avoid work.

Bad: SQL injection marked as P3 because it's "internal only"
Good: SQL injection is P0 or P1 regardless of scope

### Ignoring Context

Consider the broader context, not just the code.

Bad: Missing tests marked P2 for critical payment processing
Good: Missing tests marked P0 for critical payment processing

### Inconsistent Standards

Apply the same priority criteria consistently.

Bad: Same issue is P0 in file A but P2 in file B
Good: Same issue type gets same priority regardless of location

## Multi-Dimensional Priority Scoring

For complex prioritization, consider scoring across dimensions:

```
Impact Score (1-5):
- How many users affected?
- How severe is the impact?
- What's the business risk?

Urgency Score (1-5):
- How time-sensitive is this?
- Is there a deadline?
- Is it blocking other work?

Effort Score (1-5):
- How complex to fix?
- What's the time estimate?
- What dependencies exist?

Final Priority:
- High Impact + High Urgency → P0
- High Impact + Medium Urgency → P1
- Medium Impact + High Urgency → P1
- Medium Impact + Medium Urgency → P2
- Low Impact or Low Urgency → P2 or P3
```

## Priority Review Triggers

Re-evaluate priorities when:

- Approaching a release deadline
- Production incident occurs
- Business priorities shift
- New security vulnerability discovered
- Team capacity changes
- Dependencies are updated
- User feedback indicates different severity

## Examples by Domain

### E-commerce Application

P0:

- Checkout process broken
- Payment processing fails
- User authentication bypassed
- Prices displayed incorrectly

P1:

- Search results incomplete
- Product images not loading
- Email notifications not sent
- Admin panel slow to load

P2:

- Product sorting could be improved
- Missing product reviews
- Checkout flow could be smoother
- Analytics tracking incomplete

P3:

- UI polish and animations
- Additional product filters
- Admin UI improvements
- Code refactoring for maintainability

### Internal Dashboard

P0:

- Data displayed is incorrect
- User cannot log in
- Dashboard completely broken
- Data export corrupts data

P1:

- Slow query affecting page load
- Missing error handling
- Critical feature not working
- Data refresh is slow

P2:

- UI could be more intuitive
- Additional filters needed
- Export format improvements
- Code organization

P3:

- Color scheme updates
- Additional chart types
- Keyboard shortcuts
- Code comments

## Priority Communication

When communicating priorities to stakeholders:

**P0 Communication:**
"This MUST be fixed before we can deploy. It poses immediate risk."

**P1 Communication:**
"This should be addressed in the current sprint. It's important but not blocking."

**P2 Communication:**
"This should be scheduled in the next 1-2 sprints. It improves quality."

**P3 Communication:**
"This can be added to the backlog for future consideration."

## Conclusion

Priority classification is both an art and a science. Use this framework as a guide, but always apply judgment based on:

- Business context
- Team capacity
- Project timeline
- Risk tolerance
- User impact

When in doubt, err on the side of higher priority and discuss with the team.
