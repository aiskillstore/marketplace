# Testing Anti-Patterns and How to Avoid Them

Common mistakes in testing and their solutions for Vitest + TypeScript.

## Anti-Pattern 1: Testing Implementation Details

### ❌ Bad: Coupled to Implementation

```typescript
class UserService {
  private validateEmail(email: string): boolean {
    return /^.+@.+\..+$/.test(email);
  }

  createUser(email: string) {
    if (this.validateEmail(email)) {
      return { id: 1, email };
    }
    throw new Error('Invalid email');
  }
}

// Bad test - tests private method
it('validates email format', () => {
  const service = new UserService();
  // @ts-ignore - accessing private method
  expect(service.validateEmail('test@example.com')).toBe(true);
});
```

### ✅ Good: Test Public Behavior

```typescript
describe('UserService', () => {
  it('creates user with valid email', () => {
    const service = new UserService();
    const user = service.createUser('test@example.com');
    expect(user.email).toBe('test@example.com');
  });

  it('rejects invalid email format', () => {
    const service = new UserService();
    expect(() => service.createUser('invalid')).toThrow('Invalid email');
  });
});
```

**Why**: Testing implementation details makes tests fragile. Refactoring breaks tests even when behavior is unchanged.

## Anti-Pattern 2: Overly Complex Test Setup

### ❌ Bad: Massive Setup

```typescript
describe('OrderService', () => {
  it('processes order', async () => {
    // 50+ lines of setup
    const db = await setupDatabase();
    await db.insertUsers([...]);
    await db.insertProducts([...]);
    const paymentGateway = new PaymentGateway({...});
    await paymentGateway.configure({...});
    const emailService = new EmailService({...});
    const logger = new Logger({...});
    const cache = new Cache({...});
    const service = new OrderService(db, paymentGateway, emailService, logger, cache);
    
    // Actual test
    const result = await service.processOrder(orderId);
    expect(result.status).toBe('completed');
  });
});
```

### ✅ Good: Helper Functions and Factories

```typescript
// testHelpers.ts
export async function createTestOrderService(overrides = {}) {
  const db = await createTestDatabase();
  const paymentGateway = createMockPaymentGateway();
  const emailService = createMockEmailService();
  
  return new OrderService({
    db,
    paymentGateway,
    emailService,
    ...overrides,
  });
}

// In test
describe('OrderService', () => {
  it('processes order', async () => {
    const service = await createTestOrderService();
    const result = await service.processOrder(orderId);
    expect(result.status).toBe('completed');
  });
});
```

**Why**: Complex setup obscures test intent and makes tests hard to maintain.

## Anti-Pattern 3: Testing Multiple Concerns

### ❌ Bad: Multiple Assertions on Different Things

```typescript
it('user lifecycle', async () => {
  // Tests creation
  const user = await createUser({ name: 'John' });
  expect(user.id).toBeDefined();
  
  // Tests update
  const updated = await updateUser(user.id, { name: 'Jane' });
  expect(updated.name).toBe('Jane');
  
  // Tests deletion
  await deleteUser(user.id);
  const deleted = await findUser(user.id);
  expect(deleted).toBeNull();
  
  // Tests listing
  const users = await listUsers();
  expect(users).not.toContainEqual(user);
});
```

### ✅ Good: One Concern Per Test

```typescript
describe('User management', () => {
  it('creates user with generated ID', async () => {
    const user = await createUser({ name: 'John' });
    expect(user.id).toBeDefined();
  });

  it('updates user name', async () => {
    const user = await createUser({ name: 'John' });
    const updated = await updateUser(user.id, { name: 'Jane' });
    expect(updated.name).toBe('Jane');
  });

  it('removes deleted user from listing', async () => {
    const user = await createUser({ name: 'John' });
    await deleteUser(user.id);
    const users = await listUsers();
    expect(users).not.toContainEqual(user);
  });
});
```

**Why**: Single-concern tests are easier to understand, debug, and maintain.

## Anti-Pattern 4: Flaky Tests Due to Timing

### ❌ Bad: Arbitrary Delays

```typescript
it('updates UI after data loads', async () => {
  triggerDataLoad();
  await new Promise(resolve => setTimeout(resolve, 100));
  expect(getUIState()).toBe('loaded');
});
```

### ✅ Good: Wait for Conditions

```typescript
it('updates UI after data loads', async () => {
  triggerDataLoad();
  await waitFor(() => {
    expect(getUIState()).toBe('loaded');
  });
});

// Or with explicit promises
it('updates UI after data loads', async () => {
  const loadPromise = triggerDataLoad();
  await loadPromise;
  expect(getUIState()).toBe('loaded');
});
```

**Why**: Arbitrary delays lead to flaky tests that sometimes pass and sometimes fail.

## Anti-Pattern 5: Shared Mutable State

### ❌ Bad: Tests Depend on Order

```typescript
let sharedUser: User;

describe('User operations', () => {
  it('creates user', async () => {
    sharedUser = await createUser({ name: 'John' });
    expect(sharedUser.id).toBeDefined();
  });

  it('updates user', async () => {
    // Depends on previous test
    await updateUser(sharedUser.id, { name: 'Jane' });
    expect(sharedUser.name).toBe('Jane');
  });
});
```

### ✅ Good: Isolated Test State

```typescript
describe('User operations', () => {
  let user: User;

  beforeEach(async () => {
    user = await createUser({ name: 'John' });
  });

  it('creates user with ID', () => {
    expect(user.id).toBeDefined();
  });

  it('updates user name', async () => {
    const updated = await updateUser(user.id, { name: 'Jane' });
    expect(updated.name).toBe('Jane');
  });
});
```

**Why**: Independent tests can run in any order and are easier to debug.

## Anti-Pattern 6: Excessive Mocking

### ❌ Bad: Mocking Everything

```typescript
it('processes payment', () => {
  const mockValidator = vi.fn().mockReturnValue(true);
  const mockFormatter = vi.fn().mockReturnValue('$10.00');
  const mockLogger = vi.fn();
  const mockCache = { get: vi.fn(), set: vi.fn() };
  const mockDb = { query: vi.fn() };
  const mockGateway = { charge: vi.fn().mockResolvedValue({ success: true }) };
  
  const service = new PaymentService(
    mockValidator,
    mockFormatter,
    mockLogger,
    mockCache,
    mockDb,
    mockGateway
  );
  
  // Test becomes meaningless
  await service.processPayment({ amount: 10 });
  expect(mockGateway.charge).toHaveBeenCalled();
});
```

### ✅ Good: Mock External Dependencies Only

```typescript
describe('PaymentService', () => {
  it('charges payment gateway with correct amount', async () => {
    const mockGateway = { charge: vi.fn().mockResolvedValue({ success: true }) };
    const service = new PaymentService({ gateway: mockGateway });
    
    await service.processPayment({ amount: 1000 }); // cents
    
    expect(mockGateway.charge).toHaveBeenCalledWith({
      amount: 1000,
      currency: 'USD',
    });
  });
});
```

**Why**: Over-mocking tests behavior you've defined, not actual code behavior.

## Anti-Pattern 7: Vague Test Names

### ❌ Bad: Unclear Intent

```typescript
it('works', () => { /* ... */ });
it('test 1', () => { /* ... */ });
it('should do the thing', () => { /* ... */ });
it('handles case', () => { /* ... */ });
```

### ✅ Good: Descriptive Names

```typescript
it('returns 404 when user not found', () => { /* ... */ });
it('creates order with items and calculates total', () => { /* ... */ });
it('rejects login with invalid credentials', () => { /* ... */ });
it('sends email notification when payment succeeds', () => { /* ... */ });
```

**Why**: Clear test names serve as documentation and make failures easier to diagnose.

## Anti-Pattern 8: Not Testing Edge Cases

### ❌ Bad: Happy Path Only

```typescript
describe('divide', () => {
  it('divides two numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });
});
```

### ✅ Good: Cover Edge Cases

```typescript
describe('divide', () => {
  it('divides two positive numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('divides negative numbers', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('handles decimal results', () => {
    expect(divide(5, 2)).toBe(2.5);
  });

  it('throws on division by zero', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('handles very large numbers', () => {
    expect(divide(Number.MAX_SAFE_INTEGER, 2)).toBeDefined();
  });
});
```

**Why**: Edge cases are where bugs hide. Test boundaries, nulls, empty values, and errors.

## Anti-Pattern 9: Copy-Paste Test Code

### ❌ Bad: Duplicated Test Logic

```typescript
it('validates email for user creation', () => {
  expect(() => createUser('invalid')).toThrow('Invalid email');
  expect(() => createUser('test@')).toThrow('Invalid email');
  expect(() => createUser('@example.com')).toThrow('Invalid email');
});

it('validates email for user update', () => {
  expect(() => updateUser(1, { email: 'invalid' })).toThrow('Invalid email');
  expect(() => updateUser(1, { email: 'test@' })).toThrow('Invalid email');
  expect(() => updateUser(1, { email: '@example.com' })).toThrow('Invalid email');
});
```

### ✅ Good: Reusable Test Utilities

```typescript
function expectInvalidEmail(fn: () => void) {
  expect(fn).toThrow('Invalid email');
}

describe.each(['invalid', 'test@', '@example.com'])('email validation', (invalidEmail) => {
  it(`rejects "${invalidEmail}" in user creation`, () => {
    expectInvalidEmail(() => createUser(invalidEmail));
  });

  it(`rejects "${invalidEmail}" in user update`, () => {
    expectInvalidEmail(() => updateUser(1, { email: invalidEmail }));
  });
});
```

**Why**: DRY principle applies to tests too. Reduce duplication with helpers and parametric tests.

## Anti-Pattern 10: Ignoring Test Failures

### ❌ Bad: Skipping Failing Tests

```typescript
it.skip('this test is flaky, will fix later', () => {
  // Failing test that's been disabled
});

it('important feature', () => {
  try {
    expectComplexBehavior();
  } catch (e) {
    // Silently swallow failures
  }
});
```

### ✅ Good: Fix or Remove

```typescript
// If test is truly flaky, investigate and fix the root cause
it('processes concurrent requests correctly', async () => {
  // Use proper synchronization instead of skipping
  const results = await Promise.all([
    processRequest('a'),
    processRequest('b'),
  ]);
  expect(results).toHaveLength(2);
});

// If feature is temporarily broken, mark it appropriately
it.todo('implement cache invalidation');

// Or create a ticket and remove the test until it's prioritized
```

**Why**: Skipped tests give false confidence. Either fix them or remove them.

## Anti-Pattern 11: Not Using TypeScript Types

### ❌ Bad: Losing Type Safety

```typescript
it('creates user', async () => {
  const result: any = await createUser({ name: 'John' });
  expect(result.id).toBeDefined();
  expect(result.name).toBe('John');
});
```

### ✅ Good: Leverage TypeScript

```typescript
it('creates user', async () => {
  const result: User = await createUser({ name: 'John' });
  expect(result.id).toBeDefined();
  expect(result.name).toBe('John');
  // TypeScript ensures result has correct shape
});

// Even better: Use type-safe test utilities
function expectValidUser(user: User) {
  expect(user).toMatchObject({
    id: expect.any(Number),
    name: expect.any(String),
    email: expect.any(String),
    createdAt: expect.any(Date),
  });
}
```

**Why**: TypeScript catches type errors at compile time, preventing runtime test failures.

## Anti-Pattern 12: Testing Framework Code

### ❌ Bad: Testing Library Behavior

```typescript
it('array map works', () => {
  const result = [1, 2, 3].map(x => x * 2);
  expect(result).toEqual([2, 4, 6]);
});

it('Promise.all works', async () => {
  const results = await Promise.all([
    Promise.resolve(1),
    Promise.resolve(2),
  ]);
  expect(results).toEqual([1, 2]);
});
```

### ✅ Good: Test Your Code Only

```typescript
it('doubles all numbers in array', () => {
  const result = doubleNumbers([1, 2, 3]);
  expect(result).toEqual([2, 4, 6]);
});

it('fetches multiple users concurrently', async () => {
  const users = await fetchUsersById([1, 2, 3]);
  expect(users).toHaveLength(3);
});
```

**Why**: Trust standard library and framework code. Test your business logic.

## Best Practices Summary

1. **Test behavior, not implementation**
2. **Keep setup simple with helpers**
3. **One concern per test**
4. **Avoid timing-dependent tests**
5. **Ensure test isolation**
6. **Mock only external dependencies**
7. **Write descriptive test names**
8. **Test edge cases and errors**
9. **DRY with reusable test utilities**
10. **Fix or remove failing tests**
11. **Use TypeScript's type system**
12. **Test your code, not the framework**
