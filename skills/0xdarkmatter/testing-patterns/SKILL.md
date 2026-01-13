---
name: testing-patterns
description: "Cross-language testing strategies and patterns. Triggers on: test pyramid, unit test, integration test, e2e test, TDD, BDD, test coverage, mocking strategy, test doubles, test isolation."
compatibility: "Language-agnostic patterns. Framework-specific details in references."
allowed-tools: "Read Write Bash"
---

# Testing Patterns

Universal testing strategies and patterns applicable across languages.

## The Test Pyramid

```
        /\
       /  \     E2E Tests (few, slow, expensive)
      /    \    - Full system tests
     /------\   - Real browser/API calls
    /        \
   /  Integ   \ Integration Tests (some)
  /   Tests    \ - Service boundaries
 /--------------\ - Database, APIs
/                \
/   Unit Tests    \ Unit Tests (many, fast, cheap)
------------------  - Single function/class
                    - Mocked dependencies
```

## Test Types

### Unit Tests
```
Scope:      Single function/method/class
Speed:      Milliseconds
Dependencies: All mocked
When:       Every code change
Coverage:   80%+ of codebase
```

### Integration Tests
```
Scope:      Multiple components together
Speed:      Seconds
Dependencies: Real databases, mocked external APIs
When:       PR/merge, critical paths
Coverage:   Key integration points
```

### End-to-End Tests
```
Scope:      Full user journey
Speed:      Minutes
Dependencies: Real system (or staging)
When:       Pre-deploy, nightly
Coverage:   Critical user flows only
```

## Test Naming Convention

```
test_<unit>_<scenario>_<expected>

Examples:
- test_calculate_total_with_discount_returns_reduced_price
- test_user_login_with_invalid_password_returns_401
- test_order_submit_when_out_of_stock_raises_error
```

## Arrange-Act-Assert (AAA)

```python
def test_calculate_discount():
    # Arrange - Set up test data and dependencies
    cart = Cart()
    cart.add_item(Item(price=100))
    discount = Discount(percent=10)

    # Act - Execute the code under test
    total = cart.calculate_total(discount)

    # Assert - Verify the results
    assert total == 90
```

## Test Doubles

| Type | Purpose | Example |
|------|---------|---------|
| **Stub** | Returns canned data | `stub.get_user.returns(fake_user)` |
| **Mock** | Verifies interactions | `mock.send_email.assert_called_once()` |
| **Spy** | Records calls, uses real impl | `spy.on(service, 'save')` |
| **Fake** | Working simplified impl | `FakeDatabase()` instead of real DB |
| **Dummy** | Placeholder, never used | `null` object for required param |

## Test Isolation Strategies

### Database Isolation
```
Option 1: Transaction rollback (fast)
- Start transaction before test
- Rollback after test

Option 2: Truncate tables (medium)
- Clear all data between tests

Option 3: Separate database (slow)
- Each test gets fresh database
```

### External Service Isolation
```
Option 1: Mock at boundary
- Replace HTTP client with mock

Option 2: Fake server
- WireMock, MSW, VCR cassettes

Option 3: Contract testing
- Pact, consumer-driven contracts
```

## What to Test

### MUST Test
- Business logic and calculations
- Input validation and error handling
- Security-sensitive code (auth, permissions)
- Edge cases and boundary conditions

### SHOULD Test
- Integration points (DB, APIs)
- State transitions
- Configuration handling

### AVOID Testing
- Framework internals
- Third-party library behavior
- Simple getters/setters
- Private implementation details

## Test Quality Checklist

- [ ] Tests are independent (no order dependency)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests are fast (unit < 100ms, integration < 5s)
- [ ] Tests have clear names describing behavior
- [ ] Tests cover happy path AND error cases
- [ ] Tests don't repeat production logic
- [ ] Mocks are minimal (only external boundaries)

## Additional Resources

- `./references/tdd-workflow.md` - Test-Driven Development cycle
- `./references/mocking-strategies.md` - When and how to mock
- `./references/test-data-patterns.md` - Fixtures, factories, builders
- `./references/ci-testing.md` - Testing in CI/CD pipelines

## Scripts

- `./scripts/coverage-check.sh` - Run coverage and fail if below threshold
