# AAA Pattern (Arrange-Act-Assert)

**A standard, highly effective way to structure unit tests for maximum readability and maintainability.**

The Arrange-Act-Assert (AAA) pattern provides a clear, consistent template that makes tests easy to read, write, and maintain. By explicitly separating setup, execution, and verification, AAA helps enforce behavior-focused unit testing principles.

---

## 🎯 The Three Phases

Every unit test should be clearly divided into these three distinct sections:

```typescript
it('descriptive test name', () => {
  // --- ARRANGE ---
  // Set up test data and system state

  // --- ACT ---
  // Execute the behavior being tested

  // --- ASSERT ---
  // Verify the expected outcome
});
```

---

## 1️⃣ Arrange

**Purpose:** Set up the state of the system under test (SUT) and its environment to prepare for the test scenario.

**Goal:** Get everything ready so when the code is called, test conditions are exactly as required by the business rule.

### Actions in Arrange Phase
- Instantiate the class being tested
- Create necessary input objects or test data
- Set property values or initial states
- Set up test doubles (mocks, stubs, fakes) for dependencies
- Define what mocks should return if methods are called

### ✅ Good Example

```typescript
describe('ShippingCalculator', () => {
  it('calculates shipping cost with tax', () => {
    // --- ARRANGE ---
    // Create the system under test
    const calculator = new ShippingCalculator();

    // Prepare test data
    const order = {
      weight: 5,
      destination: 'CA',
      items: [
        { price: 20, quantity: 2 },
        { price: 15, quantity: 1 }
      ]
    };

    // Set up expected values
    const expectedShipping = 10;
    const expectedTax = 5.5; // CA tax rate
    const expectedTotal = expectedShipping + expectedTax;

    // --- ACT ---
    const result = calculator.calculate(order);

    // --- ASSERT ---
    expect(result.shipping).toBe(expectedShipping);
    expect(result.tax).toBe(expectedTax);
    expect(result.total).toBe(expectedTotal);
  });
});
```

### ✅ Arrange with Mocks

```typescript
describe('OrderService', () => {
  it('processes order and sends confirmation email', async () => {
    // --- ARRANGE ---
    // Set up mocks for dependencies
    const mockDb = {
      orders: { save: vi.fn().mockResolvedValue({ id: 'order-123' }) },
      inventory: { reserve: vi.fn().mockResolvedValue(true) }
    };

    const mockEmailService = {
      send: vi.fn().mockResolvedValue({ messageId: 'msg-456' })
    };

    // Create system under test with mocked dependencies
    const orderService = new OrderService(mockDb, mockEmailService);

    // Prepare test data
    const orderData = {
      customerId: 'cust-1',
      items: [{ productId: 'prod-1', quantity: 2 }],
      total: 100
    };

    // --- ACT ---
    const result = await orderService.processOrder(orderData);

    // --- ASSERT ---
    expect(mockDb.orders.save).toHaveBeenCalledWith(
      expect.objectContaining({ customerId: 'cust-1', total: 100 })
    );
    expect(mockEmailService.send).toHaveBeenCalledWith(
      expect.objectContaining({ to: orderData.customerId })
    );
    expect(result.success).toBe(true);
  });
});
```

---

## 2️⃣ Act

**Purpose:** Execute the specific public method or behavior of the SUT that is relevant to the test scenario.

**Goal:** Perform the single action being tested.

### Rules for Act Phase
- **One action** - Typically just one line of code
- **Call public API** - Never call private methods directly
- **Capture result** - Store return value or exception

### ✅ Good Example

```typescript
describe('UserValidator', () => {
  it('validates email format', () => {
    // --- ARRANGE ---
    const validator = new UserValidator();
    const validEmail = 'test@example.com';

    // --- ACT ---
    const isValid = validator.validateEmail(validEmail);

    // --- ASSERT ---
    expect(isValid).toBe(true);
  });
});
```

### ✅ Act with Error Handling

```typescript
describe('BankAccount', () => {
  it('throws error when withdrawing more than balance', () => {
    // --- ARRANGE ---
    const account = new BankAccount(50);
    const withdrawAmount = 100;

    // --- ACT ---
    // Wrap in function for exception testing
    const withdraw = () => account.withdraw(withdrawAmount);

    // --- ASSERT ---
    expect(withdraw).toThrow('Insufficient funds');
    expect(account.balance).toBe(50); // Balance unchanged
  });
});
```

### ✅ Act with Async/Await

```typescript
describe('UserService', () => {
  it('fetches user by ID', async () => {
    // --- ARRANGE ---
    const mockApi = {
      get: vi.fn().mockResolvedValue({ id: '1', name: 'John' })
    };
    const service = new UserService(mockApi);

    // --- ACT ---
    const user = await service.getUserById('1');

    // --- ASSERT ---
    expect(user).toEqual({ id: '1', name: 'John' });
    expect(mockApi.get).toHaveBeenCalledWith('/users/1');
  });
});
```

---

## 3️⃣ Assert

**Purpose:** Verify that the action in the Act phase produced the expected result or behavior.

**Goal:** Check if the SUT's behavior meets the requirements defined in the Arrange phase.

### What to Assert
- Return value matches expectation
- Final state of SUT has changed as expected
- Methods on mocked dependencies were called correctly
- Exceptions were thrown (or not thrown)

### ✅ Good Example: Value Assertions

```typescript
describe('Calculator', () => {
  it('adds two numbers correctly', () => {
    // --- ARRANGE ---
    const calculator = new Calculator();

    // --- ACT ---
    const result = calculator.add(5, 3);

    // --- ASSERT ---
    expect(result).toBe(8);
  });

  it('returns zero when adding zero', () => {
    // --- ARRANGE ---
    const calculator = new Calculator();

    // --- ACT ---
    const result = calculator.add(5, 0);

    // --- ASSERT ---
    expect(result).toBe(5);
  });
});
```

### ✅ Good Example: State Assertions

```typescript
describe('ShoppingCart', () => {
  it('adds item to cart', () => {
    // --- ARRANGE ---
    const cart = new ShoppingCart();
    const item = { id: '1', name: 'Widget', price: 10 };

    // --- ACT ---
    cart.addItem(item);

    // --- ASSERT ---
    expect(cart.items).toHaveLength(1);
    expect(cart.items[0]).toEqual(item);
    expect(cart.total).toBe(10);
  });
});
```

### ✅ Good Example: Mock Interaction Assertions

```typescript
describe('NotificationService', () => {
  it('sends email when order is placed', async () => {
    // --- ARRANGE ---
    const mockEmailer = {
      send: vi.fn().mockResolvedValue({ success: true })
    };
    const service = new NotificationService(mockEmailer);
    const order = { id: 'order-1', customerEmail: 'test@example.com' };

    // --- ACT ---
    await service.notifyOrderPlaced(order);

    // --- ASSERT ---
    expect(mockEmailer.send).toHaveBeenCalledTimes(1);
    expect(mockEmailer.send).toHaveBeenCalledWith({
      to: 'test@example.com',
      template: 'order-confirmation',
      data: expect.objectContaining({ orderId: 'order-1' })
    });
  });
});
```

### ✅ Good Example: Exception Assertions

```typescript
describe('PaymentService', () => {
  it('throws error for invalid card number', async () => {
    // --- ARRANGE ---
    const service = new PaymentService();
    const invalidCard = '1234'; // Too short

    // --- ACT ---
    const charge = () => service.charge(invalidCard, 100);

    // --- ASSERT ---
    expect(charge).toThrow('Invalid card number');
  });
});
```

---

## 🎨 Complete AAA Examples

### Example 1: Simple Pure Function

```typescript
import { describe, it, expect } from 'vitest';
import { calculateDiscount } from './pricing';

describe('calculateDiscount', () => {
  it('applies 20% discount to original price', () => {
    // --- ARRANGE ---
    const originalPrice = 100;
    const discountRate = 0.2;
    const expectedPrice = 80;

    // --- ACT ---
    const finalPrice = calculateDiscount(originalPrice, discountRate);

    // --- ASSERT ---
    expect(finalPrice).toBe(expectedPrice);
  });
});
```

### Example 2: Service with Dependencies

```typescript
import { describe, it, expect, vi } from 'vitest';
import { UserService } from './user-service';

describe('UserService.createUser', () => {
  it('creates user and sends welcome email', async () => {
    // --- ARRANGE ---
    const mockDatabase = {
      users: {
        create: vi.fn().mockResolvedValue({
          id: 'user-123',
          email: 'new@example.com',
          createdAt: '2024-01-15T10:00:00Z'
        })
      }
    };

    const mockEmailService = {
      sendWelcome: vi.fn().mockResolvedValue({ sent: true })
    };

    const userService = new UserService(mockDatabase, mockEmailService);

    const userData = {
      email: 'new@example.com',
      name: 'New User',
      password: 'securepass123'
    };

    // --- ACT ---
    const createdUser = await userService.createUser(userData);

    // --- ASSERT ---
    // Verify database interaction
    expect(mockDatabase.users.create).toHaveBeenCalledWith(
      expect.objectContaining({
        email: 'new@example.com',
        name: 'New User'
      })
    );

    // Verify email was sent
    expect(mockEmailService.sendWelcome).toHaveBeenCalledWith('new@example.com');

    // Verify return value
    expect(createdUser).toEqual({
      id: 'user-123',
      email: 'new@example.com',
      createdAt: '2024-01-15T10:00:00Z'
    });
  });
});
```

### Example 3: Error Handling

```typescript
import { describe, it, expect } from 'vitest';
import { BankAccount, InsufficientFundsError } from './bank-account';

describe('BankAccount.withdraw', () => {
  it('throws InsufficientFundsError when balance is too low', () => {
    // --- ARRANGE ---
    const initialBalance = 50;
    const account = new BankAccount(initialBalance);
    const withdrawAmount = 100;

    // --- ACT ---
    const attemptWithdraw = () => account.withdraw(withdrawAmount);

    // --- ASSERT ---
    expect(attemptWithdraw).toThrow(InsufficientFundsError);
    expect(attemptWithdraw).toThrow('Insufficient funds: attempted to withdraw 100 but balance is 50');
    expect(account.balance).toBe(initialBalance); // Balance unchanged
  });

  it('allows withdrawal when balance is sufficient', () => {
    // --- ARRANGE ---
    const initialBalance = 100;
    const account = new BankAccount(initialBalance);
    const withdrawAmount = 50;

    // --- ACT ---
    account.withdraw(withdrawAmount);

    // --- ASSERT ---
    expect(account.balance).toBe(50);
  });
});
```

---

## ❌ Common Anti-Patterns

### Anti-Pattern 1: Multiple Acts

```typescript
// ❌ BAD: Multiple actions in one test
it('handles user lifecycle', async () => {
  // Arrange
  const service = new UserService();

  // Act 1
  const user = await service.create({ email: 'test@example.com' });

  // Act 2
  await service.activate(user.id);

  // Act 3
  await service.delete(user.id);

  // Assert
  expect(service.users).toHaveLength(0);
});

// ✅ GOOD: One action per test
it('creates user', async () => {
  const service = new UserService();
  const user = await service.create({ email: 'test@example.com' });
  expect(user.id).toBeDefined();
});

it('activates user', async () => {
  const service = new UserService();
  const user = await service.create({ email: 'test@example.com' });

  await service.activate(user.id);

  expect(user.status).toBe('active');
});
```

### Anti-Pattern 2: Logic in Tests

```typescript
// ❌ BAD: Logic in test (if, for, while)
it('validates all users', () => {
  const users = [/* test data */];

  for (const user of users) {
    if (user.age > 18) {
      expect(validator.validate(user)).toBe(true);
    } else {
      expect(validator.validate(user)).toBe(false);
    }
  }
});

// ✅ GOOD: Use test.each for parameterized tests
it.each([
  [{ age: 20 }, true],
  [{ age: 16 }, false],
  [{ age: 18 }, false],
])('validates user %o as %s', (user, expected) => {
  expect(validator.validate(user)).toBe(expected);
});
```

### Anti-Pattern 3: Missing Arrange

```typescript
// ❌ BAD: Act and Assert mixed, unclear setup
it('calculates total', () => {
  expect(calculator.add(5, 3)).toBe(8);
});

// ✅ GOOD: Clear AAA structure
it('calculates total', () => {
  // Arrange
  const calculator = new Calculator();
  const a = 5;
  const b = 3;
  const expected = 8;

  // Act
  const result = calculator.add(a, b);

  // Assert
  expect(result).toBe(expected);
});
```

---

## 🎯 AAA Best Practices

### 1. Use Comments to Mark Sections

```typescript
it('test name', () => {
  // --- ARRANGE ---
  const sut = new SystemUnderTest();

  // --- ACT ---
  const result = sut.doSomething();

  // --- ASSERT ---
  expect(result).toBe(expected);
});
```

### 2. Keep Each Phase Focused

- **Arrange:** Only setup code
- **Act:** Only the single action being tested
- **Assert:** Only verification code

### 3. Extract Complex Arrange to Helper Functions

```typescript
// Helper function for complex setup
function createUserWithOrders(orderCount: number) {
  const user = new User({ id: '1', email: 'test@example.com' });
  const orders = Array.from({ length: orderCount }, (_, i) => ({
    id: `order-${i}`,
    userId: user.id,
    total: 100
  }));
  return { user, orders };
}

it('calculates user total spending', () => {
  // --- ARRANGE ---
  const { user, orders } = createUserWithOrders(5);
  const service = new AnalyticsService();

  // --- ACT ---
  const totalSpending = service.calculateTotalSpending(user, orders);

  // --- ASSERT ---
  expect(totalSpending).toBe(500);
});
```

### 4. One Logical Assert per Test

```typescript
// Multiple assertions are OK if they verify different facets of the same outcome
it('creates order with correct structure', () => {
  // Arrange
  const service = new OrderService();

  // Act
  const order = service.createOrder({ items: [{ id: '1', qty: 1 }] });

  // Assert - all verify the same outcome (order creation)
  expect(order.id).toBeDefined();
  expect(order.items).toHaveLength(1);
  expect(order.status).toBe('pending');
  expect(order.createdAt).toBeInstanceOf(Date);
});
```

---

## 📋 AAA Checklist

Use this checklist to verify your tests follow AAA:

### Arrange
- [ ] All test data and mocks are set up
- [ ] System under test is instantiated
- [ ] Expected values are defined
- [ ] No actual behavior execution yet

### Act
- [ ] Single, focused action
- [ ] Calls public API (not private methods)
- [ ] Result is captured

### Assert
- [ ] Verifies expected outcome
- [ ] Uses clear assertions
- [ ] No additional actions performed
- [ ] Focused on one logical assertion

---

## 🔗 Related Patterns

- **[F.I.R.S.T Principles](first-principles.md)** - AAA helps achieve Fast, Isolated, Repeatable tests
- **[BDD Integration](bdd-integration.md)** - AAA maps to Given/When/Then
- **[Black Box Testing](../strategies/black-box-testing.md)** - AAA structure for behavior testing
- **[Test Doubles](../patterns/test-doubles.md)** - Mocks used in Arrange phase

---

## 🎓 Summary

The AAA pattern provides:
- **Readability** - Consistent structure makes tests easy to understand
- **Maintainability** - Clear separation makes updates easier
- **Focus** - One action per test keeps tests simple
- **Documentation** - Tests tell a clear story: setup → action → result

**Remember:** Every test should have exactly one Act phase. If you find yourself with multiple Act phases, split into separate tests.

---

**Next Steps:**
- Integrate with [BDD Given/When/Then](bdd-integration.md)
- Apply to [Complete Examples](../examples/)
- Use for [Refactoring Tests](../refactoring/testability-patterns.md)
