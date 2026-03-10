---
name: testing-strategies
description: Design comprehensive testing strategies for software quality assurance. Use when planning test coverage, implementing test pyramids, or setting up testing infrastructure. Handles unit testing, integration testing, E2E testing, TDD, and testing best practices.
metadata:
  tags: testing, test-strategy, TDD, unit-test, integration-test, E2E, test-pyramid
  platforms: Claude, ChatGPT, Gemini
---


# Testing Strategies


## When to use this skill

- **New project**: define a testing strategy
- **Quality issues**: bugs happen frequently
- **Before refactoring**: build a safety net
- **CI/CD setup**: automated tests

## Instructions

### Step 1: Understand the Test Pyramid

```
       /\
      /E2E\          ← few (slow, expensive)
     /______\
    /        \
   /Integration\    ← medium
  /____________\
 /              \
/   Unit Tests   \  ← many (fast, inexpensive)
/________________\
```

**Ratio guide**:
- Unit: 70%
- Integration: 20%
- E2E: 10%

### Step 2: Unit testing strategy

**Given-When-Then pattern**:
```typescript
describe('calculateDiscount', () => {
  it('should apply 10% discount for orders over $100', () => {
    // Given: setup
    const order = { total: 150, customerId: '123' };

    // When: perform action
    const discount = calculateDiscount(order);

    // Then: verify result
    expect(discount).toBe(15);
  });

  it('should not apply discount for orders under $100', () => {
    const order = { total: 50, customerId: '123' };
    const discount = calculateDiscount(order);
    expect(discount).toBe(0);
  });

  it('should throw error for invalid order', () => {
    const order = { total: -10, customerId: '123' };
    expect(() => calculateDiscount(order)).toThrow('Invalid order');
  });
});
```

**Mocking strategy**:
```typescript
// Mock external dependencies
jest.mock('../services/emailService');
import { sendEmail } from '../services/emailService';

describe('UserService', () => {
  it('should send welcome email on registration', async () => {
    // Arrange
    const mockSendEmail = sendEmail as jest.MockedFunction<typeof sendEmail>;
    mockSendEmail.mockResolvedValueOnce(true);

    // Act
    await userService.register({ email: 'test@example.com', password: 'pass' });

    // Assert
    expect(mockSendEmail).toHaveBeenCalledWith({
      to: 'test@example.com',
      subject: 'Welcome!',
      body: expect.any(String)
    });
  });
});
```

### Step 3: Integration Testing

**API endpoint tests**:
```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db.user.deleteMany();  // Clean DB
  });

  it('should create user with valid data', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'test@example.com',
        username: 'testuser',
        password: 'Password123!'
      });

    expect(response.status).toBe(201);
    expect(response.body.user).toMatchObject({
      email: 'test@example.com',
      username: 'testuser'
    });

    // Verify it was actually saved to the DB
    const user = await db.user.findUnique({ where: { email: 'test@example.com' } });
    expect(user).toBeTruthy();
  });

  it('should reject duplicate email', async () => {
    // Create first user
    await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', username: 'user1', password: 'Pass123!' });

    // Attempt duplicate
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', username: 'user2', password: 'Pass123!' });

    expect(response.status).toBe(409);
  });
});
```

### Step 4: E2E Testing (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test('should complete full registration process', async ({ page }) => {
    // 1. Visit homepage
    await page.goto('http://localhost:3000');

    // 2. Click Sign Up button
    await page.click('text=Sign Up');

    // 3. Fill out form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'Password123!');

    // 4. Submit
    await page.click('button[type="submit"]');

    // 5. Confirm success message
    await expect(page.locator('text=Welcome')).toBeVisible();

    // 6. Confirm redirect to dashboard
    await expect(page).toHaveURL('http://localhost:3000/dashboard');

    // 7. Confirm user info is displayed
    await expect(page.locator('text=testuser')).toBeVisible();
  });

  test('should show error for invalid email', async ({ page }) => {
    await page.goto('http://localhost:3000/signup');
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'Password123!');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid email')).toBeVisible();
  });
});
```

### Step 5: TDD (Test-Driven Development)

**Red-Green-Refactor Cycle**:

```typescript
// 1. RED: write a failing test
describe('isPalindrome', () => {
  it('should return true for palindrome', () => {
    expect(isPalindrome('racecar')).toBe(true);
  });
});

// 2. GREEN: minimal code to pass the test
function isPalindrome(str: string): boolean {
  return str === str.split('').reverse().join('');
}

// 3. REFACTOR: improve the code
function isPalindrome(str: string): boolean {
  const cleaned = str.toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleaned === cleaned.split('').reverse().join('');
}

// 4. Additional test cases
it('should ignore case and spaces', () => {
  expect(isPalindrome('A man a plan a canal Panama')).toBe(true);
});

it('should return false for non-palindrome', () => {
  expect(isPalindrome('hello')).toBe(false);
});
```

## Output format

### Testing strategy document

```markdown
## Testing Strategy

### Coverage Goals
- Unit Tests: 80%
- Integration Tests: 60%
- E2E Tests: Critical user flows

### Test Execution
- Unit: Every commit (local + CI)
- Integration: Every PR
- E2E: Before deployment

### Tools
- Unit: Jest
- Integration: Supertest
- E2E: Playwright
- Coverage: Istanbul/nyc

### CI/CD Integration
- GitHub Actions: Run all tests on PR
- Fail build if coverage < 80%
- E2E tests on staging environment
```

## Constraints

### Required rules (MUST)

1. **Test isolation**: each test is independent
2. **Fast feedback**: unit tests should be fast (<1 min)
3. **Deterministic**: same input → same result

### Prohibited items (MUST NOT)

1. **Test dependencies**: do not let test A depend on test B
2. **Production DB**: do not use a real DB in tests
3. **Sleep/Timeout**: avoid time-based tests

## Best practices

1. **AAA pattern**: Arrange-Act-Assert
2. **Test names**: "should ... when ..."
3. **Edge Cases**: boundary values, null, empty values
4. **Happy Path + Sad Path**: both success/failure scenarios

## References

- [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Jest](https://jestjs.io/)
- [Playwright](https://playwright.dev/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Compatible platforms**: Claude, ChatGPT, Gemini

### Related skills
- [backend-testing](../backend-testing/SKILL.md)
- [code-review](../code-review/SKILL.md)

### Tags
`#testing` `#test-strategy` `#TDD` `#unit-test` `#integration-test` `#E2E` `#code-quality`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
