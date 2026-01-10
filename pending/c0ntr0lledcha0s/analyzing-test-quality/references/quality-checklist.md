# Test Quality Checklist

Use this checklist to evaluate test quality. Check each item and note issues.

---

## Structure & Organization

### Test Naming
- [ ] Names describe behavior being tested
- [ ] Names include scenario and expected outcome
- [ ] Consistent naming convention across codebase
- [ ] No generic names like "test1" or "should work"

### Test Structure
- [ ] Uses AAA (Arrange-Act-Assert) or GWT pattern
- [ ] One logical assertion per test
- [ ] Proper describe/context nesting
- [ ] Related tests grouped together
- [ ] Setup/teardown used appropriately

### File Organization
- [ ] Test files mirror source structure
- [ ] Shared utilities in dedicated folder
- [ ] Fixtures/factories clearly organized
- [ ] Mocks in __mocks__ directories (if applicable)

---

## Coverage Quality

### Scenario Coverage
- [ ] Happy path tested
- [ ] Error cases tested
- [ ] Edge cases tested
- [ ] Boundary conditions tested
- [ ] Null/undefined handling tested

### Integration Points
- [ ] External API calls tested
- [ ] Database operations tested
- [ ] File system operations tested
- [ ] Third-party integrations tested

### Security Scenarios
- [ ] Input validation tested
- [ ] Authentication flows tested
- [ ] Authorization checks tested
- [ ] XSS prevention tested (if applicable)

---

## Reliability

### Determinism
- [ ] No random values without seeding
- [ ] No date/time dependencies without mocking
- [ ] No external network calls
- [ ] No file system dependencies

### Isolation
- [ ] Tests don't share mutable state
- [ ] Order-independent execution
- [ ] Proper cleanup in afterEach/afterAll
- [ ] Database state reset between tests

### Async Handling
- [ ] Proper use of async/await
- [ ] No arbitrary delays (setTimeout)
- [ ] Proper wait conditions
- [ ] Timeout handling tested

---

## Maintainability

### Readability
- [ ] Clear variable names
- [ ] No magic numbers/strings
- [ ] Comments for complex logic
- [ ] Consistent formatting

### DRY Principles
- [ ] Reusable fixtures/factories
- [ ] Shared test utilities
- [ ] No copy-paste tests
- [ ] Appropriate abstraction level

### Simplicity
- [ ] Tests aren't overly complex
- [ ] Clear dependency setup
- [ ] Focused assertions
- [ ] No unnecessary mocking

---

## Anti-Patterns to Avoid

### Critical Issues
- [ ] No flaky tests (timing issues)
- [ ] No test pollution (shared state)
- [ ] No assertion roulette (unrelated assertions)
- [ ] No mystery guests (hidden dependencies)

### Code Smells
- [ ] No over-mocking
- [ ] No eager tests (testing multiple things)
- [ ] No slow tests without good reason
- [ ] No conditional logic in tests

---

## Performance

### Execution Speed
- [ ] Unit tests run in < 1 second each
- [ ] Integration tests run in < 5 seconds each
- [ ] Total suite runs in reasonable time
- [ ] Proper use of beforeAll vs beforeEach

### Resource Usage
- [ ] Expensive operations mocked
- [ ] Database connections pooled/reused
- [ ] File operations minimized
- [ ] Memory leaks prevented

---

## Scoring Guide

Rate each section:
- ✅ **Excellent** (90-100%): All items checked, no issues
- ⚠️ **Good** (70-89%): Most items checked, minor issues
- 🟡 **Needs Work** (50-69%): Several issues identified
- ❌ **Critical** (<50%): Major issues requiring attention

### Section Scores

| Section | Score | Notes |
|---------|-------|-------|
| Structure & Organization | | |
| Coverage Quality | | |
| Reliability | | |
| Maintainability | | |
| Anti-Patterns | | |
| Performance | | |

**Overall Score**: ___ / 100

---

## Common Fixes

### Quick Wins
1. Add descriptive test names
2. Extract shared setup to beforeEach
3. Use factories for test data
4. Remove arbitrary delays

### Medium Effort
1. Add missing error case tests
2. Implement proper mocking
3. Fix shared state issues
4. Add timeout handling

### Larger Refactoring
1. Reorganize test file structure
2. Create test utilities library
3. Implement integration test suite
4. Set up mutation testing
