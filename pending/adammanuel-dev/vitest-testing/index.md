# Vitest Testing Decision Tree

**Quick navigation to the right testing approach for your scenario.**

## 🎯 What Are You Testing?

### 🆕 New Feature or Function

**Test Type:** Unit Test (Black Box)

**Approach:**
1. ✅ Test via public API only
2. ✅ Use AAA pattern (Arrange-Act-Assert)
3. ✅ Apply F.I.R.S.T principles
4. ✅ Mock external dependencies

**Resources:**
- [Black Box Testing Strategy](strategies/black-box-testing.md)
- [AAA Pattern Guide](principles/aaa-pattern.md)
- [F.I.R.S.T Principles](principles/first-principles.md)
- [Test Doubles (Mocking)](patterns/test-doubles.md)

**Example:**
```typescript
// Testing a new feature: User registration
describe('UserService.register', () => {
  it('creates user with hashed password', async () => {
    // Arrange
    const service = new UserService(mockDb, mockEmailService);
    const userData = { email: 'test@example.com', password: 'plain123' };

    // Act
    const user = await service.register(userData);

    // Assert
    expect(user.email).toBe('test@example.com');
    expect(user.password).not.toBe('plain123'); // Hashed
    expect(mockEmailService.send).toHaveBeenCalled();
  });
});
```

---

### 🐛 Bug Fix

**Test Type:** Regression Test (Reproduce → Fix → Verify)

**Approach:**
1. ✅ Write failing test that reproduces the bug
2. ✅ Fix the implementation
3. ✅ Verify test passes
4. ✅ Add edge case tests

**Resources:**
- [Error Testing Patterns](patterns/error-testing.md)
- [Black Box Testing](strategies/black-box-testing.md)

**Example:**
```typescript
// Bug: Division by zero not handled
describe('Calculator.divide', () => {
  it('throws error when dividing by zero', () => {
    // This test fails initially (reproduces bug)
    const calc = new Calculator();
    expect(() => calc.divide(10, 0)).toThrow('Cannot divide by zero');
  });

  it('handles edge case: negative zero', () => {
    const calc = new Calculator();
    expect(() => calc.divide(10, -0)).toThrow('Cannot divide by zero');
  });
});
```

---

### 🔄 Refactoring Existing Code

**Test Type:** Existing Tests + Additional Coverage

**Approach:**
1. ✅ Ensure existing tests pass (green)
2. ✅ Identify untestable code patterns
3. ✅ Extract testable units (pure functions, injected dependencies)
4. ✅ Add tests for newly extracted units
5. ✅ Verify all tests still pass

**Resources:**
- [Testability Patterns](refactoring/testability-patterns.md)
- [Pure Functions Extraction](refactoring/pure-functions.md)
- [Dependency Injection](refactoring/dependency-injection.md)

**Example:**
```typescript
// Before: Hard to test (mixed concerns)
class OrderService {
  processOrder(order) {
    const total = this.calculateTotal(order); // Complex logic
    this.db.save(order); // Side effect
    this.email.send(order.customerEmail, total); // Side effect
  }
}

// After: Testable (extracted pure function)
function calculateOrderTotal(order) { /* pure logic */ }

class OrderService {
  processOrder(order) {
    const total = calculateOrderTotal(order); // Easy to test separately
    this.db.save(order);
    this.email.send(order.customerEmail, total);
  }
}

// Test the pure function exhaustively
describe('calculateOrderTotal', () => {
  it.each([
    [{ items: [{ price: 10, qty: 2 }] }, 20],
    [{ items: [{ price: 60, qty: 2 }], coupon: 0.1 }, 108],
  ])('calculates %o as %d', (order, expected) => {
    expect(calculateOrderTotal(order)).toBe(expected);
  });
});
```

---

### 🌐 API Endpoint or HTTP Client

**Test Type:** Integration Test (Contract Testing)

**Approach:**
1. ✅ Test the HTTP contract (request/response)
2. ✅ Test error scenarios (4xx, 5xx)
3. ✅ Mock external APIs
4. ✅ Verify request/response structure

**Resources:**
- [API Testing Patterns](patterns/api-testing.md)
- [Async Testing](patterns/async-testing.md)
- [Test Doubles](patterns/test-doubles.md)

**Example:**
```typescript
describe('UserAPI.fetchUser', () => {
  it('fetches user successfully', async () => {
    // Mock HTTP client
    const mockHttp = {
      get: vi.fn().mockResolvedValue({
        data: { id: '1', name: 'John' }
      })
    };

    const api = new UserAPI(mockHttp);
    const user = await api.fetchUser('1');

    expect(mockHttp.get).toHaveBeenCalledWith('/users/1');
    expect(user).toEqual({ id: '1', name: 'John' });
  });

  it('handles 404 error', async () => {
    const mockHttp = {
      get: vi.fn().mockRejectedValue({ status: 404 })
    };

    const api = new UserAPI(mockHttp);
    await expect(api.fetchUser('999')).rejects.toThrow('User not found');
  });
});
```

---

### ⚛️ React/Vue Component

**Test Type:** Component Test (User Interaction)

**Approach:**
1. ✅ Test from user's perspective
2. ✅ Query by accessible roles/labels
3. ✅ Test interactions (click, type, etc.)
4. ✅ Verify rendered output

**Resources:**
- [Component Testing Patterns](patterns/component-testing.md)
- [Async Testing](patterns/async-testing.md)

**Example:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';

describe('LoginForm', () => {
  it('submits credentials when form is valid', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    // User types email and password
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' }
    });

    // User clicks submit
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Verify submission
    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

---

### 🏪 State Management (Redux/Zustand)

**Test Type:** State Transition Test

**Approach:**
1. ✅ Test state transitions via actions
2. ✅ Test selectors separately
3. ✅ Mock async side effects
4. ✅ Verify state shape

**Resources:**
- [State Management Examples](examples/state-management/)
- [Async Testing](patterns/async-testing.md)

**Example:**
```typescript
describe('userSlice', () => {
  it('updates user on login success', () => {
    const initialState = { user: null, loading: false };

    const action = userSlice.actions.loginSuccess({
      id: '1',
      name: 'John'
    });

    const newState = userSlice.reducer(initialState, action);

    expect(newState).toEqual({
      user: { id: '1', name: 'John' },
      loading: false
    });
  });
});
```

---

### 🔐 Authentication/Authorization

**Test Type:** Security-Critical Test (Comprehensive)

**Approach:**
1. ✅ Test all authentication flows
2. ✅ Test authorization boundaries
3. ✅ Test token validation/expiry
4. ✅ Test security edge cases

**Resources:**
- [Authentication Example](examples/authentication/)
- [Error Testing](patterns/error-testing.md)
- [Async Testing](patterns/async-testing.md)

**Example:**
```typescript
describe('AuthService', () => {
  it('authenticates user with valid credentials', async () => {
    const authService = new AuthService(mockUserRepo, mockTokenService);
    const result = await authService.login('user@test.com', 'validpass');

    expect(result).toMatchObject({
      token: expect.any(String),
      user: { email: 'user@test.com' }
    });
  });

  it('rejects authentication with invalid credentials', async () => {
    const authService = new AuthService(mockUserRepo, mockTokenService);

    await expect(
      authService.login('user@test.com', 'wrongpass')
    ).rejects.toThrow('Invalid credentials');
  });

  it('rejects expired tokens', async () => {
    const expiredToken = 'expired.jwt.token';
    mockTokenService.verify.mockRejectedValue(new Error('Token expired'));

    await expect(
      authService.verifyToken(expiredToken)
    ).rejects.toThrow('Token expired');
  });
});
```

---

### 🧩 Complex Business Logic / Domain Model

**Test Type:** Domain Test (Behavior-Focused)

**Approach:**
1. ✅ Test business rules via public methods
2. ✅ Test invariants (rules that must always hold)
3. ✅ Test domain events
4. ✅ Use domain language in tests

**Resources:**
- [BDD Integration](principles/bdd-integration.md)
- [Black Box Testing](strategies/black-box-testing.md)
- [Architecture Alignment](integration/architecture-alignment.md)

**Example:**
```typescript
describe('BankAccount (Domain Model)', () => {
  describe('Invariant: Balance cannot go negative', () => {
    it('prevents withdrawal exceeding balance', () => {
      // Given an account with $50
      const account = new BankAccount(50);

      // When attempting to withdraw $100
      const withdraw = () => account.withdraw(100);

      // Then it should throw InsufficientFundsError
      expect(withdraw).toThrow(InsufficientFundsError);
      expect(account.balance).toBe(50); // Balance unchanged
    });
  });

  describe('Business Rule: Premium accounts have no transfer fees', () => {
    it('applies no fee for premium account transfers', () => {
      const account = new BankAccount(100, { isPremium: true });
      const destination = new BankAccount(0);

      account.transferTo(destination, 50);

      expect(account.balance).toBe(50); // No fee deducted
      expect(destination.balance).toBe(50);
    });
  });
});
```

---

## 🤔 Special Scenarios

### When Code is Hard to Test

**You're probably dealing with:**
- Mixed concerns (logic + side effects)
- Tightly coupled dependencies
- Global state or singletons
- Complex private methods

**Solution:**
1. See [Testability Patterns](refactoring/testability-patterns.md)
2. Extract pure functions
3. Inject dependencies
4. Isolate side effects

### When to Test Implementation Details

**Rarely acceptable:**
- Highly complex core algorithms
- Performance-critical sections
- Legacy code characterization
- Security-critical internals

**Guidance:**
- See [Implementation Details Strategy](strategies/implementation-details.md)
- Prefer extracting to testable class first
- Document why you're testing internals

### When Tests Are Slow

**Common causes:**
- Real database/network calls
- Large test data setup
- Too many tests
- Sequential instead of parallel

**Solutions:**
- Use in-memory implementations
- Mock external dependencies
- Reduce test data to minimum
- Run tests in parallel
- See [F.I.R.S.T Principles](principles/first-principles.md#fast)

---

## 📋 Quick Checklists

### ✅ Every Test Should Be:
- [ ] **Fast** - Runs in < 100ms
- [ ] **Isolated** - No shared state between tests
- [ ] **Repeatable** - Same result every time
- [ ] **Self-Checking** - Automated assertions
- [ ] **Timely** - Written with/before code

### ✅ Every Test Should Have:
- [ ] **Clear name** - Describes behavior being tested
- [ ] **AAA structure** - Arrange, Act, Assert sections
- [ ] **One assertion focus** - Tests one thing
- [ ] **No logic** - No if/for/while in tests
- [ ] **Mocked dependencies** - Isolated from externals

### ✅ Avoid:
- [ ] Testing private methods directly
- [ ] Testing framework code (React, etc.)
- [ ] Testing third-party libraries
- [ ] Snapshot tests for business logic
- [ ] Complex test setup/fixtures

---

## 🚀 Next Steps

After identifying your scenario above:

1. **Read the relevant strategy/pattern** from the resources
2. **Review the code example** in the scenario section
3. **Check complete examples** for full implementation
4. **Apply AAA pattern** to structure your test
5. **Verify F.I.R.S.T principles** are met

**Need syntax help?** → [Cheatsheet](quick-reference/cheatsheet.md)

**Need to refactor first?** → [Testability Patterns](refactoring/testability-patterns.md)

**Want a complete example?** → [Examples Directory](examples/)
