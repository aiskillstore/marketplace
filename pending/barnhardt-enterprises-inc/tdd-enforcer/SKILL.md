---
name: tdd-enforcer
description: Use when implementing new features. Enforces TDD workflow - write tests FIRST, then implementation. Ensures AAA pattern, proper coverage, and quality test design.
allowed-tools: Read, Grep, Bash
---

# TDD Workflow Enforcer

## When to Use
- Implementing new features
- Adding functionality
- Fixing bugs
- Refactoring code

## TDD Process (MANDATORY)

### 1. Write Tests FIRST (RED Phase)
- Define behavior through tests
- Use AAA pattern (Arrange, Act, Assert)
- Tests MUST fail initially
- Clear test names describe expected behavior

### 2. Verify Tests Fail (Confirmation)
- Run tests: `npm test`
- Confirm failure for the RIGHT reason
- Test should fail because feature doesn't exist, not because of syntax error

### 3. Write Implementation (GREEN Phase)
- Write minimal code to pass tests
- No gold plating or extra features
- Focus solely on making tests pass

### 4. Verify Tests Pass (Validation)
- Run tests: `npm test`
- All new tests must be green
- All existing tests must still pass

### 5. Refactor (REFACTOR Phase)
- Improve code quality
- Remove duplication
- Enhance readability
- Tests stay green throughout

## Coverage Requirements

- Overall: 75%+
- Business Logic (src/services/): 90%+
- Utilities (src/utils/): 90%+
- UI Components: 60%+
- E2E tests for critical user flows

## AAA Pattern (Arrange, Act, Assert)

```typescript
describe('AuthService', () => {
  describe('register', () => {
    it('should create user with hashed password', async () => {
      // ARRANGE: Setup test data
      const userData = {
        email: 'test@example.com',
        password: 'Pass123!',
      }

      // ACT: Execute the behavior
      const result = await authService.register(userData)

      // ASSERT: Verify outcome
      expect(result.id).toBeDefined()
      expect(result.email).toBe(userData.email)
      expect(result).not.toHaveProperty('password') // Never return password
    })

    it('should reject weak passwords', async () => {
      // ARRANGE
      const userData = {
        email: 'test@example.com',
        password: '123', // Too weak
      }

      // ACT & ASSERT
      await expect(authService.register(userData)).rejects.toThrow(
        'Password must be at least 8 characters'
      )
    })
  })
})
```

## Test Structure

### Describe Blocks
```typescript
// ✅ DO: Organize by module/class
describe('UserService', () => {
  // ✅ DO: Organize by method
  describe('findById', () => {
    it('should return user when found', () => {})
    it('should return null when not found', () => {})
    it('should throw error for invalid id', () => {})
  })

  describe('create', () => {
    it('should create user with valid data', () => {})
    it('should validate email format', () => {})
    it('should hash password before saving', () => {})
  })
})
```

### Test Names
```typescript
// ✅ DO: Descriptive test names
it('should return 400 when email is invalid', () => {})
it('should hash password with bcrypt before saving', () => {})
it('should send welcome email after registration', () => {})

// ❌ DON'T: Vague test names
it('works', () => {})
it('test user creation', () => {})
it('should work correctly', () => {})
```

## Testing Different Layers

### Unit Tests (Business Logic)

```typescript
// src/services/auth.service.test.ts
import { AuthService } from './auth.service'
import { prismaMock } from '../test/prisma-mock'
import bcrypt from 'bcrypt'

describe('AuthService', () => {
  describe('login', () => {
    it('should return user and token for valid credentials', async () => {
      // ARRANGE
      const hashedPassword = await bcrypt.hash('password123', 10)
      const mockUser = {
        id: '1',
        email: 'user@test.com',
        password: hashedPassword,
      }
      prismaMock.user.findUnique.mockResolvedValue(mockUser)

      // ACT
      const result = await authService.login({
        email: 'user@test.com',
        password: 'password123',
      })

      // ASSERT
      expect(result.user.email).toBe('user@test.com')
      expect(result.token).toBeDefined()
      expect(result.user).not.toHaveProperty('password')
    })

    it('should throw error for wrong password', async () => {
      // ARRANGE
      const hashedPassword = await bcrypt.hash('password123', 10)
      const mockUser = {
        id: '1',
        email: 'user@test.com',
        password: hashedPassword,
      }
      prismaMock.user.findUnique.mockResolvedValue(mockUser)

      // ACT & ASSERT
      await expect(
        authService.login({
          email: 'user@test.com',
          password: 'wrongpassword',
        })
      ).rejects.toThrow('Invalid credentials')
    })
  })
})
```

### Integration Tests (API Routes)

```typescript
// src/app/api/auth/register/route.test.ts
import { POST } from './route'

describe('POST /api/auth/register', () => {
  it('should create user and return 201', async () => {
    // ARRANGE
    const request = new Request('http://localhost/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: 'newuser@test.com',
        password: 'SecurePass123!',
        name: 'Test User',
      }),
    })

    // ACT
    const response = await POST(request)
    const data = await response.json()

    // ASSERT
    expect(response.status).toBe(201)
    expect(data.user.email).toBe('newuser@test.com')
    expect(data.token).toBeDefined()
    expect(data.user).not.toHaveProperty('password')
  })

  it('should return 400 for invalid email', async () => {
    // ARRANGE
    const request = new Request('http://localhost/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: 'invalid-email',
        password: 'SecurePass123!',
      }),
    })

    // ACT
    const response = await POST(request)
    const data = await response.json()

    // ASSERT
    expect(response.status).toBe(400)
    expect(data.error).toContain('email')
  })
})
```

### Component Tests (UI)

```typescript
// src/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  it('should call onSubmit with email and password', async () => {
    // ARRANGE
    const mockOnSubmit = vi.fn().mockResolvedValue(undefined)
    render(<LoginForm onSubmit={mockOnSubmit} />)

    // ACT
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'user@test.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))

    // ASSERT
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        email: 'user@test.com',
        password: 'password123',
      })
    })
  })

  it('should display error message when login fails', async () => {
    // ARRANGE
    const mockOnSubmit = vi
      .fn()
      .mockRejectedValue(new Error('Invalid credentials'))
    render(<LoginForm onSubmit={mockOnSubmit} />)

    // ACT
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'user@test.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    })
    fireEvent.click(screen.getByRole('button', { name: /login/i }))

    // ASSERT
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    })
  })

  it('should disable submit button while loading', async () => {
    // ARRANGE
    const mockOnSubmit = vi
      .fn()
      .mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    render(<LoginForm onSubmit={mockOnSubmit} />)

    // ACT
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'user@test.com' },
    })
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    })
    const submitButton = screen.getByRole('button', { name: /login/i })
    fireEvent.click(submitButton)

    // ASSERT
    expect(submitButton).toBeDisabled()
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })
})
```

### E2E Tests (Critical Flows)

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can register and login', async ({ page }) => {
    // ARRANGE
    const email = `test-${Date.now()}@example.com`
    const password = 'SecurePass123!'

    // ACT: Register
    await page.goto('/register')
    await page.fill('[name="email"]', email)
    await page.fill('[name="password"]', password)
    await page.fill('[name="confirmPassword"]', password)
    await page.click('button[type="submit"]')

    // ASSERT: Redirected to dashboard
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')

    // ACT: Logout
    await page.click('[data-testid="user-menu"]')
    await page.click('text=Logout')

    // ASSERT: Redirected to login
    await expect(page).toHaveURL('/login')

    // ACT: Login
    await page.fill('[name="email"]', email)
    await page.fill('[name="password"]', password)
    await page.click('button[type="submit"]')

    // ASSERT: Back to dashboard
    await expect(page).toHaveURL('/dashboard')
  })
})
```

## Test Quality Requirements

### ✅ DO: Test behavior, not implementation
```typescript
// ✅ DO
it('should display error message when login fails', async () => {
  // Test what the user sees
  await expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
})

// ❌ DON'T
it('should call setError with "Invalid credentials"', async () => {
  // Testing implementation detail
  expect(setError).toHaveBeenCalledWith('Invalid credentials')
})
```

### ✅ DO: Test edge cases
```typescript
it('should handle empty input', () => {})
it('should handle very long input (> 1000 chars)', () => {})
it('should handle special characters in email', () => {})
it('should handle concurrent requests', () => {})
```

### ✅ DO: Test error conditions
```typescript
it('should handle database connection failure', () => {})
it('should handle network timeout', () => {})
it('should handle invalid JSON response', () => {})
```

### ✅ DO: Use test data builders
```typescript
// Test data builders for cleaner tests
const userBuilder = {
  default: () => ({
    email: 'test@example.com',
    password: 'Pass123!',
    name: 'Test User',
  }),
  withEmail: (email: string) => ({
    ...userBuilder.default(),
    email,
  }),
  withoutName: () => ({
    email: 'test@example.com',
    password: 'Pass123!',
  }),
}

it('should create user with default data', () => {
  const user = userBuilder.default()
  // ...
})

it('should create user without name', () => {
  const user = userBuilder.withoutName()
  // ...
})
```

## Coverage Verification

```bash
# Run tests with coverage
npm run test:coverage

# Check coverage thresholds
npm test -- --coverage --coverageThreshold='{"global":{"lines":75,"functions":75,"branches":75}}'
```

## Common TDD Mistakes

### ❌ DON'T: Write implementation first
```typescript
// Wrong order
1. Write function
2. Write tests
3. Tests pass (or fix tests to pass)
```

### ✅ DO: Write tests first
```typescript
// Correct order (TDD)
1. Write test (RED)
2. Verify test fails
3. Write minimal implementation (GREEN)
4. Verify test passes
5. Refactor (REFACTOR)
```

### ❌ DON'T: Test implementation details
```typescript
// Bad: Testing internal state
expect(component.state.loading).toBe(true)

// Good: Testing observable behavior
expect(screen.getByTestId('spinner')).toBeInTheDocument()
```

### ❌ DON'T: Write one giant test
```typescript
// Bad: One test does everything
it('should handle entire user flow', () => {
  // 100 lines of test code
})

// Good: Split into focused tests
it('should validate email format', () => {})
it('should hash password', () => {})
it('should create user in database', () => {})
it('should send welcome email', () => {})
```

## Checklist Before Committing

- [ ] All new features have tests written FIRST
- [ ] Tests failed initially (RED)
- [ ] Implementation makes tests pass (GREEN)
- [ ] Code refactored for quality (REFACTOR)
- [ ] Coverage thresholds met (75%+ overall, 90%+ business logic)
- [ ] All tests use AAA pattern
- [ ] Test names are descriptive
- [ ] Edge cases tested
- [ ] Error conditions tested
- [ ] E2E tests for critical user flows
