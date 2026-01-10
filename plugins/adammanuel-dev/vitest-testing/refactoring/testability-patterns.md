# Refactoring for Testability

**Transform hard-to-test code into testable code through proven refactoring patterns.**

Code that's hard to test is often poorly designed. These patterns show you how to refactor common anti-patterns into testable, maintainable code.

---

## 🎯 Signs Your Code Needs Refactoring for Testability

### Red Flags
- ❌ Can't test without touching database/filesystem/network
- ❌ Need to use reflection to access private methods
- ❌ Tests require complex setup with many mocks
- ❌ Can't test one piece of logic without testing everything
- ❌ Must run tests in specific order
- ❌ Tests are slow (> 100ms per test)
- ❌ Difficult to create test data
- ❌ Tests break when refactoring

**If you see these signs, apply the patterns below.**

---

## 🏗️ Pattern 1: Extract Pure Functions

**Problem:** Complex logic mixed with side effects makes testing difficult.

**Solution:** Extract pure logic into separate functions that are easy to test.

### Before: Hard to Test

```typescript
class OrderService {
  constructor(private db: Database, private emailer: EmailService) {}

  async processOrder(order: Order) {
    // Mixed logic and side effects
    let total = 0
    for (const item of order.items) {
      total += item.price * item.quantity
    }

    // Apply discount logic
    if (order.coupon) {
      total *= (1 - order.coupon.discount)
    }

    // Apply bulk discount
    if (total > 100) {
      total *= 0.9 // 10% bulk discount
    }

    // Side effects: database and email
    await this.db.save({ ...order, total })
    await this.emailer.send(order.customerEmail, total)

    return total
  }
}

// Hard to test: Must mock database and emailer just to test calculation logic
```

### After: Testable

```typescript
// Pure function - easy to test exhaustively
export function calculateOrderTotal(order: Order): number {
  let total = order.items.reduce(
    (sum, item) => sum + (item.price * item.quantity),
    0
  )

  // Apply coupon discount
  if (order.coupon) {
    total *= (1 - order.coupon.discount)
  }

  // Apply bulk discount
  if (total > 100) {
    total *= 0.9
  }

  return total
}

class OrderService {
  constructor(private db: Database, private emailer: EmailService) {}

  async processOrder(order: Order) {
    // Use pure function
    const total = calculateOrderTotal(order)

    // Side effects isolated
    await this.db.save({ ...order, total })
    await this.emailer.send(order.customerEmail, total)

    return total
  }
}
```

### Testing Strategy

```typescript
// Test pure function exhaustively - no mocks needed
describe('calculateOrderTotal', () => {
  it.each([
    [{ items: [{ price: 10, quantity: 2 }] }, 20],
    [{ items: [{ price: 10, quantity: 2 }], coupon: { discount: 0.1 } }, 18],
    [{ items: [{ price: 60, quantity: 2 }] }, 108], // With bulk discount
    [{ items: [{ price: 60, quantity: 2 }], coupon: { discount: 0.1 } }, 97.2], // Both discounts
  ])('calculates total for %o as %d', (order, expected) => {
    expect(calculateOrderTotal(order)).toBeCloseTo(expected, 2)
  })
})

// Test orchestration with mocks (minimal logic to test)
describe('OrderService.processOrder', () => {
  it('saves and notifies', async () => {
    const mockDb = { save: vi.fn().mockResolvedValue(undefined) }
    const mockEmailer = { send: vi.fn().mockResolvedValue(undefined) }
    const service = new OrderService(mockDb, mockEmailer)

    const order = { items: [{ price: 10, quantity: 1 }], customerEmail: 'test@example.com' }

    await service.processOrder(order)

    expect(mockDb.save).toHaveBeenCalledWith(
      expect.objectContaining({ total: 10 })
    )
    expect(mockEmailer.send).toHaveBeenCalledWith('test@example.com', 10)
  })
})
```

---

## 🔌 Pattern 2: Dependency Injection

**Problem:** Hard-coded dependencies make testing impossible without real implementations.

**Solution:** Inject dependencies through constructor or parameters.

### Before: Hard to Test

```typescript
class UserService {
  // Hard-coded dependencies
  async createUser(data: UserData) {
    const db = new PostgresDatabase() // Can't mock
    const mailer = new SendGridMailer() // Can't mock
    const logger = console // Can't mock

    try {
      const user = await db.users.create(data)
      await mailer.sendWelcome(user.email)
      logger.log(`User created: ${user.id}`)
      return user
    } catch (error) {
      logger.error('Failed to create user', error)
      throw error
    }
  }
}
```

### After: Testable

```typescript
// Define interfaces for dependencies
interface Database {
  users: {
    create(data: UserData): Promise<User>
  }
}

interface Mailer {
  sendWelcome(email: string): Promise<void>
}

interface Logger {
  log(message: string): void
  error(message: string, error: Error): void
}

class UserService {
  // Inject dependencies
  constructor(
    private db: Database,
    private mailer: Mailer,
    private logger: Logger
  ) {}

  async createUser(data: UserData) {
    try {
      const user = await this.db.users.create(data)
      await this.mailer.sendWelcome(user.email)
      this.logger.log(`User created: ${user.id}`)
      return user
    } catch (error) {
      this.logger.error('Failed to create user', error)
      throw error
    }
  }
}
```

### Testing Strategy

```typescript
describe('UserService.createUser', () => {
  it('creates user and sends welcome email', async () => {
    // Arrange - inject test doubles
    const mockDb = {
      users: {
        create: vi.fn().mockResolvedValue({ id: '123', email: 'test@example.com' })
      }
    }
    const mockMailer = {
      sendWelcome: vi.fn().mockResolvedValue(undefined)
    }
    const mockLogger = {
      log: vi.fn(),
      error: vi.fn()
    }

    const service = new UserService(mockDb, mockMailer, mockLogger)

    // Act
    const user = await service.createUser({ email: 'test@example.com' })

    // Assert
    expect(mockDb.users.create).toHaveBeenCalledWith({ email: 'test@example.com' })
    expect(mockMailer.sendWelcome).toHaveBeenCalledWith('test@example.com')
    expect(mockLogger.log).toHaveBeenCalledWith('User created: 123')
    expect(user.id).toBe('123')
  })

  it('logs error when creation fails', async () => {
    const error = new Error('Database error')
    const mockDb = {
      users: { create: vi.fn().mockRejectedValue(error) }
    }
    const mockLogger = { log: vi.fn(), error: vi.fn() }

    const service = new UserService(mockDb, {} as Mailer, mockLogger)

    await expect(service.createUser({ email: 'test@example.com' }))
      .rejects.toThrow('Database error')

    expect(mockLogger.error).toHaveBeenCalledWith('Failed to create user', error)
  })
})
```

---

## 🧩 Pattern 3: Extract Complex Class

**Problem:** Complex private method in a class is hard to test without accessing internals.

**Solution:** Extract the logic into its own class with a public API.

### Before: Hard to Test

```typescript
class ShippingService {
  async shipItem(item: Item, destination: string) {
    const shippingCost = this.calculateInternationalRate(
      item.weight,
      destination,
      item.value
    )
    // ... more logic
  }

  // Complex private logic - can't test without reflection
  private calculateInternationalRate(
    weight: number,
    country: string,
    value: number
  ): number {
    let rate = 10.0

    // Complex business rules
    if (country === 'CA') {
      rate += weight * 1.5
      if (value > 500) {
        rate += value * 0.1 // Import duty
      }
    } else if (country === 'MEX') {
      rate += weight * 2.0
      // ... more rules
    }
    // ... many more country-specific rules

    return rate
  }
}
```

### After: Testable

```typescript
// Extracted into its own class with public API
export class InternationalRateCalculator {
  calculate(weight: number, country: string, value: number): number {
    let rate = 10.0

    if (country === 'CA') {
      rate += weight * 1.5
      if (value > 500) {
        rate += value * 0.1
      }
    } else if (country === 'MEX') {
      rate += weight * 2.0
    }

    return rate
  }
}

class ShippingService {
  constructor(private rateCalculator: InternationalRateCalculator) {}

  async shipItem(item: Item, destination: string) {
    const shippingCost = this.rateCalculator.calculate(
      item.weight,
      destination,
      item.value
    )
    // ... more logic
  }
}
```

### Testing Strategy

```typescript
// Test calculator exhaustively - black box
describe('InternationalRateCalculator', () => {
  const calculator = new InternationalRateCalculator()

  it('calculates CA rate with import duty', () => {
    const rate = calculator.calculate(10, 'CA', 600)

    const expected = 10 + (10 * 1.5) + (600 * 0.1) // 10 + 15 + 60 = 85
    expect(rate).toBe(expected)
  })

  it('calculates CA rate without import duty', () => {
    const rate = calculator.calculate(10, 'CA', 400)

    const expected = 10 + (10 * 1.5) // 10 + 15 = 25
    expect(rate).toBe(expected)
  })

  it('calculates MEX rate', () => {
    const rate = calculator.calculate(10, 'MEX', 100)

    const expected = 10 + (10 * 2.0) // 10 + 20 = 30
    expect(rate).toBe(expected)
  })
})

// Test orchestration - verify calculator is used
describe('ShippingService', () => {
  it('uses rate calculator', async () => {
    const mockCalculator = {
      calculate: vi.fn().mockReturnValue(50)
    }
    const service = new ShippingService(mockCalculator)

    await service.shipItem({ weight: 10, value: 100 }, 'CA')

    expect(mockCalculator.calculate).toHaveBeenCalledWith(10, 'CA', 100)
  })
})
```

---

## 🎭 Pattern 4: Wrap External Libraries

**Problem:** Direct use of external libraries makes code hard to test and couples you to the library.

**Solution:** Create a thin wrapper around the library with an interface.

### Before: Hard to Test

```typescript
import axios from 'axios'

class UserService {
  async fetchUser(id: string) {
    // Directly coupled to axios
    const response = await axios.get(`/users/${id}`)
    return response.data
  }

  async createUser(data: UserData) {
    const response = await axios.post('/users', data)
    return response.data
  }
}

// Must mock axios globally - affects all tests
```

### After: Testable

```typescript
// Define interface for HTTP client
interface HttpClient {
  get<T>(url: string): Promise<T>
  post<T>(url: string, data: any): Promise<T>
}

// Wrapper for axios
class AxiosHttpClient implements HttpClient {
  async get<T>(url: string): Promise<T> {
    const response = await axios.get(url)
    return response.data
  }

  async post<T>(url: string, data: any): Promise<T> {
    const response = await axios.post(url, data)
    return response.data
  }
}

class UserService {
  constructor(private http: HttpClient) {}

  async fetchUser(id: string) {
    return this.http.get<User>(`/users/${id}`)
  }

  async createUser(data: UserData) {
    return this.http.post<User>('/users', data)
  }
}
```

### Testing Strategy

```typescript
describe('UserService', () => {
  it('fetches user by ID', async () => {
    const mockHttp = {
      get: vi.fn().mockResolvedValue({ id: '123', name: 'John' }),
      post: vi.fn()
    }

    const service = new UserService(mockHttp)
    const user = await service.fetchUser('123')

    expect(mockHttp.get).toHaveBeenCalledWith('/users/123')
    expect(user).toEqual({ id: '123', name: 'John' })
  })
})
```

---

## ⏰ Pattern 5: Control Time

**Problem:** Code that depends on `Date.now()` or `new Date()` produces non-deterministic results.

**Solution:** Inject a clock interface.

### Before: Hard to Test

```typescript
class TokenService {
  generateToken(userId: string): string {
    const expiresAt = Date.now() + 3600000 // 1 hour from now
    return jwt.sign({ userId, expiresAt }, SECRET)
  }

  isTokenExpired(token: string): boolean {
    const { expiresAt } = jwt.verify(token, SECRET)
    return Date.now() > expiresAt
  }
}

// Tests produce different results based on when they run
```

### After: Testable

```typescript
interface Clock {
  now(): number
}

class SystemClock implements Clock {
  now(): number {
    return Date.now()
  }
}

class TokenService {
  constructor(private clock: Clock) {}

  generateToken(userId: string): string {
    const expiresAt = this.clock.now() + 3600000
    return jwt.sign({ userId, expiresAt }, SECRET)
  }

  isTokenExpired(token: string): boolean {
    const { expiresAt } = jwt.verify(token, SECRET)
    return this.clock.now() > expiresAt
  }
}
```

### Testing Strategy

```typescript
describe('TokenService', () => {
  it('generates token with correct expiration', () => {
    const fixedTime = 1000000000000
    const mockClock = { now: () => fixedTime }

    const service = new TokenService(mockClock)
    const token = service.generateToken('user-123')

    const decoded = jwt.verify(token, SECRET)
    expect(decoded.expiresAt).toBe(fixedTime + 3600000)
  })

  it('detects expired tokens', () => {
    let currentTime = 1000000000000
    const mockClock = { now: () => currentTime }

    const service = new TokenService(mockClock)
    const token = service.generateToken('user-123')

    // Token not expired initially
    expect(service.isTokenExpired(token)).toBe(false)

    // Advance time past expiration
    currentTime += 3600001
    expect(service.isTokenExpired(token)).toBe(true)
  })
})
```

---

## 📋 Pattern Summary

| Pattern | When to Use | Benefits |
|---------|-------------|----------|
| **Extract Pure Functions** | Mixed logic and side effects | Easy to test exhaustively, no mocks needed |
| **Dependency Injection** | Hard-coded dependencies | Full control in tests, easy to mock |
| **Extract Complex Class** | Complex private methods | Test complex logic as black box |
| **Wrap External Libraries** | Direct library usage | Decouple from library, easy to mock |
| **Control Time** | Time-dependent code | Deterministic tests, control time |

---

## 🎯 Refactoring Workflow

### Step 1: Identify Pain Points
- What makes this code hard to test?
- Which pattern addresses this pain?

### Step 2: Write Characterization Tests
```typescript
// Capture current behavior before refactoring
it('characterizes current behavior', () => {
  const result = legacyFunction(input)
  expect(result).toMatchSnapshot()
})
```

### Step 3: Apply Pattern
- Extract pure functions
- Inject dependencies
- Create interfaces
- Extract classes

### Step 4: Write Proper Tests
Replace characterization tests with behavior-focused tests.

### Step 5: Verify
- All tests pass
- Code is easier to test
- No behavior changes

---

## 📋 Best Practices

### ✅ Do

- **Separate logic from side effects**
- **Inject all dependencies**
- **Create interfaces for dependencies**
- **Extract complex logic into classes**
- **Make pure functions when possible**
- **Test at appropriate boundaries**

### ❌ Don't

- **Over-engineer** - apply patterns when needed
- **Extract everything** - keep simple code simple
- **Create excessive interfaces** - balance flexibility with simplicity
- **Ignore code smells** - hard to test = bad design
- **Refactor without tests** - add characterization tests first

---

## 🔗 Related Patterns

- **[Black Box Testing](../strategies/black-box-testing.md)** - Test refactored code through public API
- **[Test Doubles](../patterns/test-doubles.md)** - Mock injected dependencies
- **[Pure Functions](pure-functions.md)** - Detailed pure function patterns
- **[Dependency Injection](dependency-injection.md)** - Advanced DI patterns

---

## 🎓 Summary

**Key Takeaways:**

1. **Hard to test = Bad design** - Use testability as a design signal
2. **Separate concerns** - Logic separate from side effects
3. **Inject dependencies** - Never hard-code dependencies
4. **Extract complexity** - Complex logic → separate class
5. **Control randomness** - Time, random numbers, external state

**The Refactoring Mindset:**
> "If it's hard to test, refactor it to be easy to test. The refactored code will be better designed."

**Remember:** Testability improvements make code better in all ways - more modular, more reusable, easier to understand, and easier to maintain.

---

**Next Steps:**
- Review [Refactoring Catalog](https://refactoring.com/catalog/)
- Read [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/)
- Practice [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
