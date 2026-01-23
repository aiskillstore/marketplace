---
name: tdd-vitest-typescript
description: Test-Driven Development (TDD) using Vitest and TypeScript. Use when the user requests help with TDD, writing tests before code, test-first development, Vitest test setup, TypeScript testing patterns, unit testing, integration testing, or following the Red-Green-Refactor cycle with Vitest.
---

# TDD with Vitest and TypeScript

Guide Claude through Test-Driven Development workflows using Vitest and TypeScript.

## Core TDD Cycle: Red-Green-Refactor

Always follow this three-phase cycle:

1. **Red**: Write a failing test that defines desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code quality while keeping tests green

### Workflow Pattern

```typescript
// 1. RED: Write the test first
describe('Calculator', () => {
  it('adds two numbers', () => {
    const calc = new Calculator();
    expect(calc.add(2, 3)).toBe(5);
  });
});

// Run test → Watch it fail (Red)
// 2. GREEN: Implement minimal code
class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}

// Run test → Watch it pass (Green)
// 3. REFACTOR: Improve if needed while keeping tests green
```

## Vitest Setup and Configuration

### Basic Vitest Config

Create `vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // or 'jsdom' for DOM testing
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});
```

### TypeScript Configuration

Ensure `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"],
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

## Test File Organization

### Naming Conventions

- Test files: `*.test.ts` or `*.spec.ts`
- Place tests adjacent to source files or in `__tests__` directories
- Match test file names to source files: `calculator.ts` → `calculator.test.ts`

### Structure Pattern

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('FeatureName', () => {
  // Setup
  beforeEach(() => {
    // Runs before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  describe('specific behavior', () => {
    it('does something specific', () => {
      // Arrange
      const input = setupTestData();
      
      // Act
      const result = performAction(input);
      
      // Assert
      expect(result).toBe(expected);
    });
  });
});
```

## TypeScript Testing Patterns

### Type-Safe Test Data

```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

function createTestUser(overrides?: Partial<User>): User {
  return {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    ...overrides,
  };
}

it('processes user data', () => {
  const user = createTestUser({ name: 'Custom Name' });
  expect(processUser(user)).toBeDefined();
});
```

### Testing Generic Functions

```typescript
describe('generic array utilities', () => {
  it('filters array by predicate', () => {
    const numbers = [1, 2, 3, 4, 5];
    const result = filter(numbers, (n: number) => n > 3);
    expect(result).toEqual([4, 5]);
  });
});
```

### Testing Async/Promise Code

```typescript
describe('async operations', () => {
  it('fetches user data', async () => {
    const user = await fetchUser(1);
    expect(user.id).toBe(1);
  });

  it('handles errors', async () => {
    await expect(fetchUser(-1)).rejects.toThrow('Invalid ID');
  });
});
```

## Mocking and Stubbing

### Module Mocks

```typescript
import { vi } from 'vitest';
import { fetchData } from './api';

vi.mock('./api');

describe('data processing', () => {
  it('processes fetched data', async () => {
    vi.mocked(fetchData).mockResolvedValue({ data: 'test' });
    
    const result = await processData();
    expect(result).toBe('processed: test');
  });
});
```

### Function Spies

```typescript
describe('event handling', () => {
  it('calls callback on event', () => {
    const callback = vi.fn();
    const handler = new EventHandler(callback);
    
    handler.trigger('test-event');
    
    expect(callback).toHaveBeenCalledWith('test-event');
    expect(callback).toHaveBeenCalledTimes(1);
  });
});
```

### Partial Mocks

```typescript
import * as utils from './utils';

vi.spyOn(utils, 'helperFunction').mockReturnValue('mocked');

it('uses mocked helper', () => {
  const result = mainFunction();
  expect(utils.helperFunction).toHaveBeenCalled();
  expect(result).toContain('mocked');
});
```

## Common Testing Patterns

### Testing Classes

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepository: MockRepository;

  beforeEach(() => {
    mockRepository = new MockRepository();
    service = new UserService(mockRepository);
  });

  it('creates user with valid data', async () => {
    const userData = { name: 'John', email: 'john@example.com' };
    
    const user = await service.createUser(userData);
    
    expect(user.id).toBeDefined();
    expect(mockRepository.save).toHaveBeenCalledWith(
      expect.objectContaining(userData)
    );
  });
});
```

### Testing Pure Functions

```typescript
describe('pure utility functions', () => {
  it('capitalizes first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
    expect(capitalize('')).toBe('');
    expect(capitalize('WORLD')).toBe('WORLD');
  });
});
```

### Testing Error Handling

```typescript
describe('error scenarios', () => {
  it('throws on invalid input', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('returns error result', () => {
    const result = parseJSON('invalid json');
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});
```

### Parametric Tests

```typescript
import { describe, it, expect } from 'vitest';

describe.each([
  { input: 2, expected: 4 },
  { input: 3, expected: 9 },
  { input: 4, expected: 16 },
])('square function', ({ input, expected }) => {
  it(`squares ${input} to ${expected}`, () => {
    expect(square(input)).toBe(expected);
  });
});
```

## Test Coverage Guidelines

### Running Coverage

```bash
vitest --coverage
```

### Coverage Targets

- Aim for 80%+ coverage on business logic
- 100% coverage on critical paths (authentication, payments, etc.)
- Don't obsess over 100% everywhere—focus on meaningful tests

### What to Test

**Always test:**
- Business logic and domain rules
- Error handling and edge cases
- Public APIs and interfaces
- Data transformations

**Consider skipping:**
- Simple getters/setters
- Framework/library code
- Trivial type definitions
- Configuration files

## TDD Best Practices

### Write Tests First

Always start with the test, not the implementation:

```typescript
// ❌ BAD: Writing implementation first
class Calculator {
  add(a: number, b: number) { return a + b; }
}

// ✅ GOOD: Test first
it('adds two numbers', () => {
  expect(new Calculator().add(2, 3)).toBe(5);
});
```

### One Assertion Per Test

Keep tests focused:

```typescript
// ❌ BAD: Multiple concerns
it('user operations', () => {
  const user = createUser();
  expect(user.id).toBeDefined();
  expect(updateUser(user)).toBeTruthy();
  expect(deleteUser(user.id)).toBeUndefined();
});

// ✅ GOOD: Single concern
it('creates user with ID', () => {
  const user = createUser();
  expect(user.id).toBeDefined();
});

it('updates existing user', () => {
  const user = createUser();
  expect(updateUser(user)).toBeTruthy();
});
```

### Test Behavior, Not Implementation

```typescript
// ❌ BAD: Testing implementation details
it('calls internal helper method', () => {
  const service = new Service();
  const spy = vi.spyOn(service as any, '_internalHelper');
  service.process();
  expect(spy).toHaveBeenCalled();
});

// ✅ GOOD: Testing behavior
it('processes data correctly', () => {
  const service = new Service();
  const result = service.process(inputData);
  expect(result).toEqual(expectedOutput);
});
```

### Keep Tests Fast

- Use mocks for external dependencies (databases, APIs, file system)
- Avoid sleep/setTimeout in tests
- Run expensive setup once with beforeAll when safe

### Descriptive Test Names

```typescript
// ❌ BAD: Vague
it('works', () => { /* ... */ });

// ✅ GOOD: Descriptive
it('returns empty array when no users match filter criteria', () => {
  /* ... */
});
```

## Common TDD Workflow

### Starting a New Feature

1. Write a high-level test describing the feature:

```typescript
describe('User Registration', () => {
  it('creates new user account with valid email', async () => {
    const result = await registerUser({
      email: 'new@example.com',
      password: 'secure123',
    });
    
    expect(result.success).toBe(true);
    expect(result.user.email).toBe('new@example.com');
  });
});
```

2. Run test → See it fail (Red)
3. Implement minimal code → See it pass (Green)
4. Add edge case tests:

```typescript
it('rejects registration with existing email', async () => {
  await registerUser({ email: 'existing@example.com', password: 'pass' });
  
  const result = await registerUser({
    email: 'existing@example.com',
    password: 'pass2',
  });
  
  expect(result.success).toBe(false);
  expect(result.error).toContain('Email already registered');
});

it('rejects weak passwords', async () => {
  const result = await registerUser({
    email: 'new@example.com',
    password: '123',
  });
  
  expect(result.success).toBe(false);
  expect(result.error).toContain('Password too weak');
});
```

5. Refactor implementation while keeping tests green

### Debugging Failed Tests

When tests fail unexpectedly:

1. Check test isolation—are tests interfering with each other?
2. Verify mocks are properly reset between tests
3. Use `it.only()` to run single test
4. Add console.log or debugger statements
5. Check async timing issues

## Integration Testing with Vitest

### Testing Multiple Units Together

```typescript
describe('Order Processing Integration', () => {
  let database: TestDatabase;
  let paymentGateway: MockPaymentGateway;
  let orderService: OrderService;

  beforeEach(async () => {
    database = await TestDatabase.create();
    paymentGateway = new MockPaymentGateway();
    orderService = new OrderService(database, paymentGateway);
  });

  afterEach(async () => {
    await database.cleanup();
  });

  it('completes order flow from cart to confirmation', async () => {
    const user = await database.createUser();
    const cart = await orderService.createCart(user.id);
    await orderService.addItem(cart.id, { productId: 1, quantity: 2 });
    
    paymentGateway.simulateSuccess();
    const order = await orderService.checkout(cart.id);
    
    expect(order.status).toBe('confirmed');
    expect(order.items).toHaveLength(1);
  });
});
```

## Watch Mode

Vitest runs in watch mode by default during development:

```bash
vitest
```

This automatically re-runs tests when files change, enabling rapid TDD cycles.

## Quick Reference: Common Matchers

```typescript
// Equality
expect(value).toBe(5);                    // Strict equality (===)
expect(value).toEqual({ a: 1 });          // Deep equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeLessThan(10);
expect(value).toBeCloseTo(0.3);           // Floating point

// Strings
expect(string).toMatch(/pattern/);
expect(string).toContain('substring');

// Arrays
expect(array).toContain(item);
expect(array).toHaveLength(3);

// Objects
expect(object).toHaveProperty('key');
expect(object).toMatchObject({ a: 1 });   // Partial match

// Exceptions
expect(() => fn()).toThrow();
expect(() => fn()).toThrow('Error message');
expect(async () => fn()).rejects.toThrow();

// Functions
expect(fn).toHaveBeenCalled();
expect(fn).toHaveBeenCalledWith(arg1, arg2);
expect(fn).toHaveBeenCalledTimes(2);
```

## Tips for Effective TDD

1. **Start simple**: Begin with the simplest test case, not the most complex
2. **Take small steps**: Write one test, make it pass, refactor, repeat
3. **Trust the process**: Resist urge to write implementation before tests
4. **Refactor fearlessly**: With good test coverage, refactoring is safe
5. **Keep tests maintainable**: Tests are code too—keep them clean and DRY
6. **Run tests frequently**: Vitest's watch mode makes this effortless
7. **Write tests for bugs**: When you find a bug, write a test that exposes it first

## When to Use This Skill

Apply TDD when:
- Building new features from scratch
- Fixing bugs (write failing test first)
- Refactoring existing code
- Learning a new API or library
- Working on critical business logic

TDD is especially valuable for:
- Pure functions and algorithms
- Business logic and domain models
- Data transformations
- API endpoints and services
