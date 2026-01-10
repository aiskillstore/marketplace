---
name: testing-strategy
description: Comprehensive testing strategy using Vitest for unit/integration tests and Playwright for E2E tests with best practices and coverage targets
version: 1.0.0
author: AI-Vibe-Prompts
tags: [testing, vitest, playwright, quality, tdd, e2e]
auto_invoke: true
---

# Testing Strategy Skill

## Objective

Implement comprehensive testing strategy covering unit, integration, and E2E tests using modern tools (Vitest, Playwright) with clear coverage targets and best practices.

## When to Use This Skill

Auto-invoke when:
- User mentions "test", "testing", "coverage", "TDD", "E2E"
- Setting up new project
- Adding new features (need tests)
- Debugging test failures
- Improving test coverage

## Testing Pyramid

```
        /\
       /E2E\         Few, slow, expensive
      /------\
     /  Integ \      Some, moderate speed
    /----------\
   / Unit Tests \    Many, fast, cheap
  /--------------\
```

**Distribution**:
- **70%** Unit Tests - Fast, isolated, cheap
- **20%** Integration Tests - Moderate speed, test interactions
- **10%** E2E Tests - Slow, expensive, critical user flows

## Test Types

### 1. Unit Tests (Vitest)

**What**: Test individual functions/components in isolation

**Tools**: Vitest, React Testing Library

**Coverage Target**: 80%+

**Setup**:
```bash
npm install -D vitest @vitest/ui @testing-library/react @testing-library/jest-dom
```

**Config** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80
      }
    }
  }
})
```

**Example** (`Button.test.tsx`):
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

**Commands**:
```bash
npm run test              # Run all tests
npm run test:watch        # Watch mode
npm run test:ui           # Visual UI
npm run test:coverage     # With coverage
```

### 2. Integration Tests (Vitest)

**What**: Test component interactions, API calls, state management

**Example** (`UserProfile.test.tsx`):
```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { UserProfile } from './UserProfile'

// Mock API
vi.mock('./api', () => ({
  fetchUser: vi.fn(() => Promise.resolve({
    id: 1,
    name: 'John Doe',
    email: 'john@example.com'
  }))
}))

describe('UserProfile Integration', () => {
  it('fetches and displays user data', async () => {
    render(<UserProfile userId="1" />)
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('john@example.com')).toBeInTheDocument()
    })
  })
})
```

### 3. E2E Tests (Playwright)

**What**: Test complete user flows in real browser

**Tools**: Playwright

**Coverage Target**: Critical paths only

**Setup**:
```bash
npm install -D @playwright/test
npx playwright install
```

**Config** (`playwright.config.ts`):
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 13'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

**Example** (`e2e/auth.spec.ts`):
```typescript
import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('user can sign up and log in', async ({ page }) => {
    // Sign up
    await page.goto('/signup')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.click('button[type="submit"]')
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText('Welcome')
    
    // Log out
    await page.click('[aria-label="User menu"]')
    await page.click('text=Logout')
    
    // Should redirect to home
    await expect(page).toHaveURL('/')
    
    // Log back in
    await page.goto('/login')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL(/\/dashboard/)
  })
})
```

**Commands**:
```bash
npx playwright test                    # Run all E2E
npx playwright test --ui               # Interactive mode
npx playwright test --headed           # Show browser
npx playwright test --project=chromium # Specific browser
npx playwright show-report             # View last report
```

## Testing Best Practices

### AAA Pattern
```typescript
// Arrange
const user = { id: 1, name: 'John' }
const mockFetch = vi.fn()

// Act
const result = await fetchUser(mockFetch, 1)

// Assert
expect(result).toEqual(user)
expect(mockFetch).toHaveBeenCalledWith('/api/users/1')
```

### Test Naming
```typescript
// Good: descriptive, explains what and when
it('displays error message when API returns 404', () => {})
it('disables submit button when form is invalid', () => {})

// Bad: vague, unclear
it('works', () => {})
it('test 1', () => {})
```

### One Assertion Per Test (Guideline)
```typescript
// Prefer focused tests
it('renders user name', () => {
  render(<User name="John" />)
  expect(screen.getByText('John')).toBeInTheDocument()
})

it('renders user email', () => {
  render(<User email="john@example.com" />)
  expect(screen.getByText('john@example.com')).toBeInTheDocument()
})

// Over complex tests
it('renders user data', () => {
  // Multiple unrelated assertions
})
```

### Mock External Dependencies
```typescript
// Mock API calls
vi.mock('./api', () => ({
  fetchUser: vi.fn()
}))

// Mock environment
vi.stubEnv('API_URL', 'http://test-api.com')

// Mock timers
vi.useFakeTimers()
const now = new Date('2024-01-01')
vi.setSystemTime(now)
```

## Coverage Strategy

### What to Test

✅ **Do Test**:
- Business logic
- Edge cases and error handling
- User interactions
- API integration
- State management
- Validation logic
- Critical user flows (E2E)

❌ **Don't Test**:
- Third-party libraries
- Framework internals
- Constants
- Simple getters/setters
- Generated code

### Coverage Targets

**Minimum**:
- Lines: 80%
- Functions: 80%
- Branches: 75%
- Statements: 80%

**Ideal**:
- Critical paths: 100%
- Business logic: 95%+
- UI components: 85%+
- Utilities: 90%+

### Run Coverage
```bash
npm run test:coverage

# View in browser
open coverage/index.html
```

## Testing Workflow

### 1. TDD Approach (Recommended)
```
1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat
```

### 2. Test-After (Pragmatic)
```
1. Implement feature
2. Write tests
3. Achieve 80%+ coverage
4. Refactor with confidence
```

### 3. Pre-Commit Testing
```bash
# Run before every commit
npm run test:quick        # Fast unit tests
npm run lint
npm run typecheck

# Run before push
npm run test             # All unit/integration
npm run test:coverage    # Verify coverage

# Run before deploy
npm run test:e2e         # Full E2E suite
```

## Test Organization

### Directory Structure
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx      # Co-located
│   │   └── Button.stories.tsx   # Storybook
│   └── ...
tests/
├── setup.ts                      # Test setup
├── utils/                        # Test utilities
│   ├── renderWithProviders.tsx  # Custom render
│   └── mockData.ts              # Test fixtures
└── __mocks__/                   # Global mocks
e2e/
├── auth.spec.ts
├── checkout.spec.ts
└── fixtures/                    # E2E test data
```

### Naming Conventions
- Unit/Integration: `*.test.ts` or `*.test.tsx`
- E2E: `*.spec.ts`
- Setup: `setup.ts`, `vitest.config.ts`

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'
      
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test:coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
  
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
      
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

## Debugging Tests

### Vitest
```bash
# Run single test file
npm run test -- Button.test.tsx

# Run tests matching pattern
npm run test -- --grep "Button renders"

# Debug in VS Code
# Add breakpoint, press F5
```

### Playwright
```bash
# Debug mode
npx playwright test --debug

# Specific test
npx playwright test auth.spec.ts --debug

# Trace viewer
npx playwright show-trace trace.zip
```

## Common Testing Patterns

### Testing Async Code
```typescript
it('fetches user data', async () => {
  const { result } = renderHook(() => useUser(1))
  
  await waitFor(() => {
    expect(result.current.data).toEqual({ id: 1, name: 'John' })
  })
})
```

### Testing Error States
```typescript
it('displays error when fetch fails', async () => {
  vi.mocked(fetchUser).mockRejectedValue(new Error('Network error'))
  
  render(<UserProfile userId="1" />)
  
  await waitFor(() => {
    expect(screen.getByText(/error/i)).toBeInTheDocument()
  })
})
```

### Testing Forms
```typescript
it('submits form with valid data', async () => {
  const handleSubmit = vi.fn()
  render(<LoginForm onSubmit={handleSubmit} />)
  
  await userEvent.type(screen.getByLabelText('Email'), 'test@example.com')
  await userEvent.type(screen.getByLabelText('Password'), 'password123')
  await userEvent.click(screen.getByRole('button', { name: /submit/i }))
  
  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  })
})
```

## Integration with Other Skills

- `quality-gates` - Run tests as quality check
- `git-workflow` - Tests in pre-commit hooks
- `codebase-analysis` - Identify untested code

## Package.json Scripts

```json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed",
    "test:all": "npm run test:coverage && npm run test:e2e"
  }
}
```

## Version History

- **1.0.0** (2025-01-03): Initial testing strategy with Vitest and Playwright
