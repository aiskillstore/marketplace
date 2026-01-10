# F.I.R.S.T Testing Principles

**The foundation of effective unit testing: Fast, Isolated, Repeatable, Self-Checking, and Timely.**

These five principles define what makes a good unit test. Following F.I.R.S.T ensures your test suite remains a valuable asset rather than becoming a maintenance burden.

---

## ⚡ Fast

**Principle:** Tests should run in milliseconds, encouraging frequent execution during development.

**Target:** < 100ms per test (most should be < 10ms)

### Why It Matters
- **Faster feedback loop** - Issues are found and fixed immediately
- **Encourages frequent testing** - Developers run tests more often
- **Prevents propagation** - Bugs don't spread into the codebase
- **Maintains flow state** - No waiting interrupts development

### ✅ Good Example: Fast Test

```typescript
import { describe, it, expect } from 'vitest';
import { calculateDiscount, validateEmail } from './utils';

describe('calculateDiscount', () => {
  it('applies 20% discount correctly', () => {
    // Pure function, no I/O - runs in < 1ms
    const result = calculateDiscount(100, 0.2);
    expect(result).toBe(80);
  });

  it('handles zero discount', () => {
    const result = calculateDiscount(100, 0);
    expect(result).toBe(100);
  });

  it('rejects negative discount', () => {
    expect(() => calculateDiscount(100, -0.1)).toThrow('Invalid discount');
  });
});

describe('validateEmail', () => {
  it('validates correct email format', () => {
    // Simple regex check - runs in < 1ms
    expect(validateEmail('test@example.com')).toBe(true);
  });

  it('rejects invalid email format', () => {
    expect(validateEmail('invalid-email')).toBe(false);
  });
});
```

**Why it's fast:**
- No I/O operations (database, network, file system)
- Pure functions with simple logic
- Minimal data setup

### ❌ Bad Example: Slow Test

```typescript
import { describe, it, expect } from 'vitest';
import { db } from './database';
import { emailService } from './services';

describe('UserService (SLOW)', () => {
  it('creates user in database', async () => {
    // Real database connection - runs in 100-500ms
    const user = await db.users.create({
      email: 'test@example.com',
      password: 'hashedpass123'
    });

    expect(user.id).toBeDefined();
    expect(user.email).toBe('test@example.com');

    // Real email service call - runs in 200-1000ms
    await emailService.sendWelcome(user.email);
  });

  it('fetches user from database', async () => {
    // Another real DB call
    const user = await db.users.findByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});
```

**Why it's slow:**
- Real database connection (100-500ms per query)
- Network calls to email service (200-1000ms)
- Multiple I/O operations compound

### 🔧 Refactoring for Speed

**Before: Slow (real dependencies)**
```typescript
class UserService {
  constructor(private db: Database, private emailer: EmailService) {}

  async createUser(data: UserData) {
    const user = await this.db.users.create(data); // SLOW
    await this.emailer.sendWelcome(user.email);    // SLOW
    return user;
  }
}

// Slow test - must use real DB and email service
it('creates user', async () => {
  const service = new UserService(realDb, realEmailer);
  const user = await service.createUser(userData); // 300-1500ms
  expect(user).toBeDefined();
});
```

**After: Fast (mocked dependencies)**
```typescript
class UserService {
  constructor(private db: Database, private emailer: EmailService) {}

  async createUser(data: UserData) {
    const user = await this.db.users.create(data);
    await this.emailer.sendWelcome(user.email);
    return user;
  }
}

// Fast test - mocked dependencies
it('creates user', async () => {
  const mockDb = {
    users: {
      create: vi.fn().mockResolvedValue({ id: '1', ...userData })
    }
  };
  const mockEmailer = {
    sendWelcome: vi.fn().mockResolvedValue(undefined)
  };

  const service = new UserService(mockDb, mockEmailer);
  const user = await service.createUser(userData); // < 5ms

  expect(user).toEqual({ id: '1', ...userData });
  expect(mockEmailer.sendWelcome).toHaveBeenCalledWith(userData.email);
});
```

---

## 🔒 Isolated

**Principle:** Tests a single unit in isolation, using test doubles to eliminate reliance on external systems.

**Goal:** Failures pinpoint the exact location of the problem within the unit, not in complex interactions.

### Why It Matters
- **Clear failure diagnosis** - Know exactly what broke
- **Independent execution** - Tests can run in any order
- **No shared state** - Tests don't affect each other
- **Faster debugging** - Isolated failures are easier to fix

### ✅ Good Example: Isolated Test

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OrderService } from './order-service';

describe('OrderService', () => {
  let mockDb: any;
  let mockPayment: any;
  let mockEmail: any;
  let service: OrderService;

  beforeEach(() => {
    // Fresh mocks for each test - complete isolation
    mockDb = {
      orders: { save: vi.fn().mockResolvedValue({ id: 'order-1' }) },
      inventory: { reserve: vi.fn().mockResolvedValue(true) }
    };

    mockPayment = {
      charge: vi.fn().mockResolvedValue({ success: true, chargeId: 'ch-1' })
    };

    mockEmail = {
      sendConfirmation: vi.fn().mockResolvedValue(undefined)
    };

    // Each test gets a fresh instance
    service = new OrderService(mockDb, mockPayment, mockEmail);
  });

  it('processes order successfully', async () => {
    const order = { items: [{ id: '1', qty: 2 }], total: 100 };

    const result = await service.processOrder(order);

    // Verify interactions with mocks
    expect(mockDb.inventory.reserve).toHaveBeenCalled();
    expect(mockPayment.charge).toHaveBeenCalledWith(100);
    expect(mockDb.orders.save).toHaveBeenCalled();
    expect(result.success).toBe(true);
  });

  it('handles payment failure', async () => {
    // This test is completely isolated from the previous one
    mockPayment.charge.mockResolvedValue({ success: false, error: 'Declined' });

    const order = { items: [{ id: '1', qty: 2 }], total: 100 };

    const result = await service.processOrder(order);

    expect(result.success).toBe(false);
    expect(mockDb.orders.save).not.toHaveBeenCalled(); // Order not saved
  });
});
```

**Why it's isolated:**
- Fresh mocks in `beforeEach` - no shared state
- No real database, payment, or email dependencies
- Tests can run in any order or in parallel
- Each test verifies one unit's behavior

### ❌ Bad Example: Not Isolated

```typescript
import { describe, it, expect } from 'vitest';
import { db } from './database'; // Shared global database

describe('UserService (NOT ISOLATED)', () => {
  // Tests share the same database - NOT ISOLATED
  it('creates user', async () => {
    const user = await db.users.create({ email: 'test@example.com' });
    expect(user.id).toBeDefined();
  });

  it('finds user by email', async () => {
    // This test DEPENDS on the previous test creating the user
    const user = await db.users.findByEmail('test@example.com');
    expect(user).toBeDefined(); // Fails if run in isolation
  });

  it('deletes user', async () => {
    // This test DEPENDS on both previous tests
    await db.users.delete('test@example.com');
    const user = await db.users.findByEmail('test@example.com');
    expect(user).toBeNull();
  });
});
```

**Problems:**
- Tests must run in specific order
- Shared database state couples tests
- Can't run tests in parallel
- Unclear which test caused a failure

### 🔧 Isolating External Dependencies

```typescript
// Mock external modules
vi.mock('./database', () => ({
  db: {
    users: {
      create: vi.fn(),
      findByEmail: vi.fn(),
      delete: vi.fn()
    }
  }
}));

// Now tests are isolated
describe('UserService (ISOLATED)', () => {
  beforeEach(() => {
    // Clear mocks before each test
    vi.clearAllMocks();
  });

  it('creates user', async () => {
    db.users.create.mockResolvedValue({ id: '1', email: 'test@example.com' });

    const result = await userService.create('test@example.com');
    expect(result.id).toBe('1');
  });

  it('finds user by email', async () => {
    // Independent - doesn't rely on previous test
    db.users.findByEmail.mockResolvedValue({ id: '2', email: 'test@example.com' });

    const result = await userService.findByEmail('test@example.com');
    expect(result.id).toBe('2');
  });
});
```

---

## 🔁 Repeatable

**Principle:** Produces the same result every time it runs, provided the code hasn't changed.

**Goal:** Eliminate "flaky" or non-deterministic results, building trust in the test suite.

### Why It Matters
- **Builds trust** - Developers believe test failures indicate real problems
- **No false positives** - Failures always mean bugs, not randomness
- **Reliable CI/CD** - Tests don't randomly fail in pipelines
- **Debugging confidence** - Reproducible failures are fixable

### ✅ Good Example: Repeatable Test

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('OrderService', () => {
  beforeEach(() => {
    // Control time - makes tests repeatable
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2024-01-15T10:00:00Z'));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('creates order with current timestamp', () => {
    const service = new OrderService();
    const order = service.createOrder({ items: [] });

    // Always the same result because time is controlled
    expect(order.createdAt).toBe('2024-01-15T10:00:00.000Z');
  });

  it('expires orders after 24 hours', () => {
    const service = new OrderService();
    const order = service.createOrder({ items: [] });

    // Advance time by 24 hours
    vi.advanceTimersByTime(24 * 60 * 60 * 1000);

    expect(service.isExpired(order)).toBe(true);
  });
});

describe('generateUserId', () => {
  it('generates deterministic IDs in tests', () => {
    // Mock random to make it deterministic
    vi.spyOn(Math, 'random').mockReturnValue(0.123456);

    const id = generateUserId();

    expect(id).toBe('user-123456'); // Always the same
  });
});
```

**Why it's repeatable:**
- Controlled time via `vi.useFakeTimers()`
- Mocked randomness
- No dependency on external state
- Same inputs → same outputs

### ❌ Bad Example: Flaky Test

```typescript
import { describe, it, expect } from 'vitest';

describe('OrderService (FLAKY)', () => {
  it('creates order with timestamp', async () => {
    const service = new OrderService();
    const order = service.createOrder({ items: [] });

    // FLAKY: Uses real Date.now() - different every run
    const now = new Date().toISOString();
    expect(order.createdAt).toBe(now); // Will fail randomly due to timing
  });

  it('generates unique user ID', () => {
    const service = new UserService();

    // FLAKY: Uses Math.random() - different every run
    const id1 = service.generateId();
    const id2 = service.generateId();

    expect(id1).not.toBe(id2); // Might fail if random collision
  });

  it('fetches user from API', async () => {
    // FLAKY: Depends on network and external API
    const response = await fetch('https://api.example.com/user/123');
    const user = await response.json();

    expect(user.name).toBe('John'); // Fails if API is down or data changes
  });
});
```

**Problems:**
- Real time (`Date.now()`) varies between runs
- Real randomness (`Math.random()`) is unpredictable
- Network calls fail due to connectivity/API changes
- Can't reproduce failures reliably

### 🔧 Making Tests Repeatable

```typescript
// Control time
vi.useFakeTimers();
vi.setSystemTime(new Date('2024-01-15'));

// Control randomness
vi.spyOn(Math, 'random').mockReturnValue(0.5);

// Control external APIs
vi.mock('./api-client', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: '1', name: 'John' })
}));

// Now all tests are deterministic and repeatable
```

---

## ✔️ Self-Checking

**Principle:** Automatically determines if it passed or failed via assertions, without manual human inspection.

**Goal:** Full automation within CI/CD pipelines, providing immediate, objective feedback on code health.

### Why It Matters
- **Zero manual effort** - No human verification needed
- **Instant feedback** - Know immediately if code works
- **CI/CD integration** - Automated quality gates
- **Scales infinitely** - Thousands of tests, zero manual work

### ✅ Good Example: Self-Checking Test

```typescript
import { describe, it, expect } from 'vitest';

describe('UserValidator', () => {
  it('validates email format', () => {
    const validator = new UserValidator();

    // Self-checking: Clear pass/fail criteria
    expect(validator.isValidEmail('test@example.com')).toBe(true);
    expect(validator.isValidEmail('invalid-email')).toBe(false);
    expect(validator.isValidEmail('')).toBe(false);
  });

  it('validates password strength', () => {
    const validator = new UserValidator();

    // Multiple assertions - all self-checking
    expect(validator.isStrongPassword('Abc123!@#')).toBe(true);
    expect(validator.isStrongPassword('weak')).toBe(false);
    expect(validator.isStrongPassword('12345678')).toBe(false);
    expect(validator.isStrongPassword('NoNumbers!')).toBe(false);
  });

  it('throws error for invalid user data', () => {
    const validator = new UserValidator();

    // Self-checking error assertion
    expect(() => {
      validator.validate({ email: 'bad', password: '123' });
    }).toThrow('Invalid email format');
  });
});
```

**Why it's self-checking:**
- Uses `expect()` assertions
- Clear pass/fail criteria
- No manual verification needed
- Automated reporting

### ❌ Bad Example: Manual Verification Required

```typescript
import { describe, it } from 'vitest';

describe('UserService (NOT SELF-CHECKING)', () => {
  it('creates user', async () => {
    const service = new UserService();
    const user = await service.create({ email: 'test@example.com' });

    // No assertions - requires manual inspection
    console.log('Created user:', user);
    console.log('Email:', user.email);
    console.log('ID:', user.id);

    // Developer must manually verify the output
  });

  it('calculates total', () => {
    const calculator = new Calculator();
    const result = calculator.add(5, 3);

    // Comment instead of assertion
    // Result should be 8

    // No assertion - test always passes even if wrong
  });
});
```

**Problems:**
- No automated pass/fail
- Requires manual log inspection
- Always "passes" even when broken
- Can't run in CI/CD effectively

---

## ⏱️ Timely / Maintainable

**Principle:** Easy to write and maintain relative to the code being tested. Written when the code is written.

**Goal:** Test suite remains a valuable asset as software evolves, not a burden that gets neglected.

### Why It Matters
- **Prevents test rot** - Tests stay current with code
- **Living documentation** - Tests explain how code works
- **Encourages testing** - Easy tests get written
- **Reduces technical debt** - Maintainable tests prevent deletion

### ✅ Good Example: Timely & Maintainable

```typescript
import { describe, it, expect } from 'vitest';
import { calculateShipping } from './shipping';

describe('calculateShipping', () => {
  // Test written immediately when function was created

  it('calculates standard shipping', () => {
    // Clear, descriptive name explains business rule
    const cost = calculateShipping({ weight: 5, zone: 'domestic' });
    expect(cost).toBe(10);
  });

  it('applies international surcharge', () => {
    // Test name is self-documenting
    const cost = calculateShipping({ weight: 5, zone: 'international' });
    expect(cost).toBe(25); // 10 base + 15 surcharge
  });

  it('applies bulk discount for heavy items', () => {
    // Business rule clearly stated
    const cost = calculateShipping({ weight: 50, zone: 'domestic' });
    expect(cost).toBe(45); // Bulk discount applied
  });
});
```

**Why it's timely/maintainable:**
- Written with the code (not after)
- Clear test names serve as documentation
- Simple assertions easy to update
- Tests explain business rules

### ❌ Bad Example: Hard to Maintain

```typescript
import { describe, it, expect } from 'vitest';

describe('test1', () => {
  // Test written weeks after code - requirements forgotten

  it('test case A', () => {
    // Unclear name - what is being tested?
    const result = complexFunction(
      { a: 1, b: 2, c: 3, d: 4, e: 5 }, // Cryptic test data
      [1, 2, 3, 4, 5],
      { x: true, y: false, z: null }
    );

    // Magic number - why 42?
    expect(result.value).toBe(42);

    // Many assertions - which one matters?
    expect(result.status).toBe('active');
    expect(result.metadata.nested.value).toBe(true);
    expect(result.tags).toContain('processed');
  });
});
```

**Problems:**
- Unclear test purpose
- Cryptic test data
- Magic numbers without explanation
- Hard to update when requirements change

### 🔧 Writing Maintainable Tests

```typescript
describe('ShippingCalculator', () => {
  // Use descriptive test data
  const DOMESTIC_5KG_ORDER = { weight: 5, zone: 'domestic' };
  const INTERNATIONAL_5KG_ORDER = { weight: 5, zone: 'international' };

  // Use constants for expected values
  const DOMESTIC_BASE_RATE = 10;
  const INTERNATIONAL_SURCHARGE = 15;

  it('applies base rate for domestic shipping', () => {
    const cost = calculateShipping(DOMESTIC_5KG_ORDER);
    expect(cost).toBe(DOMESTIC_BASE_RATE);
  });

  it('adds international surcharge', () => {
    const cost = calculateShipping(INTERNATIONAL_5KG_ORDER);
    expect(cost).toBe(DOMESTIC_BASE_RATE + INTERNATIONAL_SURCHARGE);
  });
});
```

---

## 📋 F.I.R.S.T Checklist

Use this checklist for every test you write:

### Fast
- [ ] Test runs in < 100ms (ideally < 10ms)
- [ ] No real database, file system, or network calls
- [ ] Uses mocks/stubs for external dependencies
- [ ] Minimal test data setup

### Isolated
- [ ] Test doesn't depend on other tests
- [ ] Fresh setup in `beforeEach` if needed
- [ ] Can run in any order or in parallel
- [ ] No shared global state

### Repeatable
- [ ] Produces same result every run
- [ ] No reliance on real time (uses `vi.useFakeTimers()`)
- [ ] No reliance on randomness (mocks `Math.random()`)
- [ ] No reliance on external APIs (mocks network calls)

### Self-Checking
- [ ] Uses `expect()` assertions
- [ ] No manual log inspection required
- [ ] Clear pass/fail criteria
- [ ] Automated reporting

### Timely / Maintainable
- [ ] Written with/before the code
- [ ] Clear, descriptive test name
- [ ] Simple, readable assertions
- [ ] Well-documented test data

---

## 🎯 Summary

| Principle | Goal | Common Violations |
|-----------|------|-------------------|
| **Fast** | < 100ms per test | Real DB/network calls, heavy computation |
| **Isolated** | Independent execution | Shared state, test order dependencies |
| **Repeatable** | Same result every time | Real time, randomness, external APIs |
| **Self-Checking** | Automated pass/fail | Manual log inspection, no assertions |
| **Timely** | Easy to maintain | Written late, unclear names, magic numbers |

**Remember:** Tests that violate F.I.R.S.T become maintenance burdens and eventually get deleted. Following F.I.R.S.T ensures your test suite remains valuable over time.

---

**Next Steps:**
- Apply [AAA Pattern](aaa-pattern.md) to structure your tests
- Use [Black Box Testing](../strategies/black-box-testing.md) for behavior focus
- See [Test Doubles](../patterns/test-doubles.md) for mocking strategies
