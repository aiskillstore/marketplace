# Testing Pyramid Strategy

**Strategic approach to balancing different types of tests for optimal coverage and speed.**

The testing pyramid is a testing strategy that suggests the ideal distribution of different test types. It helps teams write effective test suites that are fast, maintainable, and provide confidence.

---

## 🔺 The Testing Pyramid

```
                    /\
                   /  \
                  / E2E \              5-10%
                 /  Tests \            • Slow (seconds)
                /──────────\           • Expensive to maintain
               /            \          • Full user flows
              /              \         • Critical paths only
             /                \
            /  Integration     \      15-20%
           /     Tests          \     • Medium speed (100ms-1s)
          /                      \    • API contracts
         /                        \   • Database queries
        /                          \  • Module integration
       /                            \
      /                              \
     /          Unit Tests            \ 70-80%
    /________________________________\ • Fast (< 10ms)
                                       • Isolated & focused
                                       • Business logic
                                       • Black box approach
```

---

## 🎯 Pyramid Levels Explained

### Level 1: Unit Tests (Base - 70-80%)

**Purpose:** Test individual units of code in isolation

**Characteristics:**
- **Speed:** < 10ms per test (most < 1ms)
- **Isolation:** No real database, network, or file system
- **Focus:** Single function, class, or module
- **Dependencies:** All mocked

**What to Test:**
- ✅ Pure functions and calculations
- ✅ Business logic and domain rules
- ✅ Validation and transformation
- ✅ Error handling and edge cases
- ✅ Utility functions

**Example:**
```typescript
describe('DiscountCalculator (Unit)', () => {
  it('applies 20% discount correctly', () => {
    // Arrange
    const calculator = new DiscountCalculator()

    // Act
    const result = calculator.calculate(100, 0.20)

    // Assert
    expect(result).toBe(80)
  })
})
```

**Why so many?**
- Fast feedback (run on every save)
- Easy to debug (isolated failures)
- Cheap to maintain (stable APIs)
- High value per minute of execution

---

### Level 2: Integration Tests (Middle - 15-20%)

**Purpose:** Test how multiple units work together

**Characteristics:**
- **Speed:** 100ms - 1s per test
- **Integration:** Real database, file system, or multiple modules
- **Focus:** Interaction between components
- **Dependencies:** Some real, some mocked

**What to Test:**
- ✅ API endpoint contracts
- ✅ Database queries and transactions
- ✅ Module integration points
- ✅ External service integration
- ✅ Configuration and setup

**Example:**
```typescript
describe('UserAPI Integration', () => {
  let db: TestDatabase

  beforeEach(async () => {
    db = await createTestDatabase()
  })

  it('creates user and stores in database', async () => {
    // Arrange
    const api = new UserAPI(db)
    const userData = { email: 'test@example.com', name: 'Test' }

    // Act
    const response = await api.post('/users', userData)

    // Assert
    expect(response.status).toBe(201)

    // Verify in real database
    const user = await db.users.findByEmail('test@example.com')
    expect(user).toBeDefined()
    expect(user.name).toBe('Test')
  })
})
```

**Why fewer than unit tests?**
- Slower (database/network calls)
- Harder to maintain (more moving parts)
- More expensive to run
- Harder to debug (multiple components)

---

### Level 3: E2E Tests (Top - 5-10%)

**Purpose:** Test complete user workflows from UI to database

**Characteristics:**
- **Speed:** Seconds to minutes per test
- **Coverage:** Full application stack
- **Focus:** Critical user journeys
- **Dependencies:** All real (production-like environment)

**What to Test:**
- ✅ Critical user flows (login, checkout, payment)
- ✅ Happy paths for main features
- ✅ Integration of entire system
- ✅ Browser-specific behavior
- ✅ Visual regressions

**Example:**
```typescript
describe('E2E: User Registration Flow', () => {
  it('allows user to register and login', async () => {
    // Arrange
    await page.goto('http://localhost:3000/register')

    // Act
    await page.fill('[name="email"]', 'newuser@example.com')
    await page.fill('[name="password"]', 'SecurePass123!')
    await page.fill('[name="name"]', 'New User')
    await page.click('button[type="submit"]')

    // Wait for redirect
    await page.waitForURL('**/dashboard')

    // Assert
    expect(page.url()).toContain('/dashboard')
    expect(await page.textContent('h1')).toBe('Welcome, New User')
  })
})
```

**Why so few?**
- Very slow (full application startup)
- Expensive to maintain (UI changes break tests)
- Hard to debug (many possible failure points)
- Should only cover critical paths

---

## 📊 Distribution Guidelines

### Ideal Ratio

```
Unit Tests:        70-80% of total tests
Integration Tests: 15-20% of total tests
E2E Tests:         5-10% of total tests
```

### Why This Distribution?

**Fast Feedback Loop:**
- 1000 unit tests run in ~10 seconds
- 100 integration tests run in ~100 seconds
- 10 E2E tests run in ~60 seconds
- **Total:** ~3 minutes for comprehensive coverage

**Optimal Cost/Benefit:**
- Unit tests: High value, low cost
- Integration tests: Medium value, medium cost
- E2E tests: High value for critical paths, high cost

---

## ⚖️ Anti-Pattern: Inverted Pyramid

```
      ❌ DON'T DO THIS

         /\
        /  \      ← Many E2E tests (slow, brittle)
       /────\
      /      \    ← Some integration tests
     /────────\
    /          \  ← Few unit tests (missing fast tests)
   /____________\

Problems:
- Test suite takes hours to run
- Hard to identify failures
- Expensive to maintain
- Fragile (breaks often)
- Developers stop running tests
```

---

## 🎯 Applying the Pyramid

### Example: E-Commerce Application

**Unit Tests (70-80%):**
```typescript
// Business logic
describe('PriceCalculator', () => {
  it('calculates total with tax', () => {
    const calc = new PriceCalculator()
    expect(calc.calculate(100, 0.08)).toBe(108)
  })
})

// Validation
describe('OrderValidator', () => {
  it('validates order has items', () => {
    expect(() => validator.validate({ items: [] }))
      .toThrow('Order must have items')
  })
})

// Domain logic
describe('Order', () => {
  it('calculates total from items', () => {
    const order = new Order()
    order.addItem({ price: 10, quantity: 2 })
    expect(order.total).toBe(20)
  })
})
```

**Integration Tests (15-20%):**
```typescript
// API endpoint
describe('POST /api/orders', () => {
  it('creates order and stores in database', async () => {
    const response = await request(app)
      .post('/api/orders')
      .send({ items: [...], customerId: '123' })

    expect(response.status).toBe(201)

    const order = await db.orders.findById(response.body.id)
    expect(order).toBeDefined()
  })
})

// Database operations
describe('OrderRepository', () => {
  it('persists order with items', async () => {
    const repo = new OrderRepository(testDb)
    const order = await repo.save({ items: [...] })

    const retrieved = await repo.findById(order.id)
    expect(retrieved.items).toHaveLength(2)
  })
})
```

**E2E Tests (5-10%):**
```typescript
// Critical user flow
describe('E2E: Checkout Flow', () => {
  it('completes purchase from cart to confirmation', async () => {
    // Add item to cart
    await page.click('[data-product-id="123"]')
    await page.click('button:has-text("Add to Cart")')

    // Go to checkout
    await page.click('a:has-text("Checkout")')

    // Fill payment info
    await page.fill('[name="cardNumber"]', '4242424242424242')
    await page.fill('[name="expiry"]', '12/25')
    await page.fill('[name="cvv"]', '123')

    // Complete purchase
    await page.click('button:has-text("Place Order")')

    // Verify confirmation
    await expect(page.locator('h1')).toContainText('Order Confirmed')
  })
})
```

---

## 🚦 Coverage Strategy

### Unit Test Coverage: 80-100%
**Focus on:**
- All business logic
- All validation functions
- All utility functions
- All error scenarios
- All edge cases

**Example Coverage:**
```typescript
// Ensure comprehensive unit coverage
describe('DiscountCalculator', () => {
  it.each([
    [100, 0.0, 100],    // No discount
    [100, 0.2, 80],     // 20% discount
    [100, 0.5, 50],     // 50% discount
    [100, 1.0, 0],      // 100% discount
  ])('calculates %i with %f discount as %i', (price, discount, expected) => {
    expect(calculate(price, discount)).toBe(expected)
  })

  it('rejects negative discount', () => {
    expect(() => calculate(100, -0.1)).toThrow()
  })

  it('rejects discount > 100%', () => {
    expect(() => calculate(100, 1.1)).toThrow()
  })
})
```

### Integration Test Coverage: 50-70%
**Focus on:**
- Critical integration points
- Database operations
- API contracts
- Error handling between layers

### E2E Test Coverage: 10-30%
**Focus on:**
- Critical user paths
- Main features only
- Don't duplicate unit test coverage

---

## 🎨 The Ice Cream Cone Anti-Pattern

```
❌ ANTI-PATTERN TO AVOID

         /\
        /  \      ← Lots of manual testing
       /    \
      /──────\    ← Many E2E tests (slow)
     /        \
    /          \  ← Some integration tests
   /            \
  /   Few Units  \ ← Very few unit tests
 /________________\

Problems:
- Requires manual testing for confidence
- E2E tests are slow and brittle
- Minimal automation
- High cost, low value
```

---

## 📋 Pyramid Checklist

Use this to audit your test suite:

### ✅ Healthy Test Suite
- [ ] 70-80% unit tests (fast, isolated)
- [ ] 15-20% integration tests (medium speed)
- [ ] 5-10% E2E tests (slow but comprehensive)
- [ ] < 5 minutes total test execution time
- [ ] Unit tests run on every save
- [ ] Integration tests run pre-commit
- [ ] E2E tests run in CI/CD
- [ ] Clear test categories (unit, integration, e2e)

### ❌ Warning Signs
- [ ] Tests take > 15 minutes to run
- [ ] More E2E tests than unit tests
- [ ] Most tests need real database
- [ ] Can't run tests locally
- [ ] Tests are skipped frequently
- [ ] No clear test categorization

---

## 🔄 Migrating from Inverted Pyramid

### Step 1: Identify Current Distribution
```bash
# Count tests by type
grep -r "describe(" tests/ | wc -l        # Total
grep -r "real database" tests/ | wc -l    # Integration
grep -r "playwright\|cypress" tests/ | wc -l  # E2E
```

### Step 2: Extract Unit Tests
```typescript
// Before: Integration test doing too much
it('creates order (integration)', async () => {
  const db = await createRealDatabase()
  const api = new OrderAPI(db)

  // Testing calculation logic with real DB
  const response = await api.createOrder({
    items: [{ price: 10, quantity: 2 }]
  })

  expect(response.total).toBe(20)
})

// After: Split into unit + integration
// Unit test (fast)
describe('calculateOrderTotal (unit)', () => {
  it('calculates total from items', () => {
    const total = calculateOrderTotal([
      { price: 10, quantity: 2 }
    ])
    expect(total).toBe(20)
  })
})

// Integration test (focused on integration concern)
describe('OrderAPI (integration)', () => {
  it('persists order to database', async () => {
    const db = await createTestDatabase()
    const api = new OrderAPI(db)

    const response = await api.createOrder({
      items: [{ price: 10, quantity: 2 }]
    })

    const saved = await db.orders.findById(response.id)
    expect(saved).toBeDefined()
  })
})
```

### Step 3: Convert E2E to Unit Where Possible
```typescript
// Before: E2E for logic testing
test('E2E: Discount calculation', async () => {
  await page.goto('/shop')
  await page.fill('[name="quantity"]', '5')
  await page.selectOption('[name="discount"]', '20')
  await page.click('button:has-text("Calculate")')

  await expect(page.locator('.total')).toContainText('$40')
})

// After: Unit test for logic
describe('calculatePrice (unit)', () => {
  it('applies 20% discount to quantity 5', () => {
    expect(calculatePrice(5, 10, 0.20)).toBe(40)
  })
})

// Keep E2E for critical flow only
test('E2E: Complete checkout flow', async () => {
  // Only test the full purchase journey
  await completeCheckoutFlow()
  await expect(page.locator('h1')).toContainText('Order Confirmed')
})
```

---

## 🎯 When to Use Each Level

### Use Unit Tests For:
- ✅ Pure functions
- ✅ Business logic
- ✅ Validation rules
- ✅ Calculations
- ✅ Data transformation
- ✅ Error handling
- ✅ Domain models

**Speed:** < 10ms
**Reference:** [Black Box Testing](../strategies/black-box-testing.md)

### Use Integration Tests For:
- ✅ API endpoints
- ✅ Database queries
- ✅ File operations
- ✅ External service integration
- ✅ Module boundaries
- ✅ Configuration loading

**Speed:** 100ms - 1s
**Reference:** [integration-testing.md](../patterns/integration-testing.md)

### Use E2E Tests For:
- ✅ User registration and login
- ✅ Payment processing
- ✅ Core business workflows
- ✅ Critical user journeys
- ❌ NOT for every feature variation

**Speed:** 5s - 60s
**Reference:** [e2e-testing.md](../patterns/e2e-testing.md)

---

## 📊 Real-World Example: Test Suite Breakdown

### Example Project: Task Management App

**Total Tests: 500**

#### Unit Tests: 400 (80%)
```typescript
// Task validation (50 tests)
describe('TaskValidator', () => {
  it.each([...])('validates task properties', ...)
})

// Date calculations (30 tests)
describe('DueDateCalculator', () => {
  it('calculates days until due', ...)
})

// Priority sorting (40 tests)
describe('TaskSorter', () => {
  it('sorts by priority and date', ...)
})

// Permission checks (60 tests)
describe('PermissionChecker', () => {
  it('allows owner to edit', ...)
})

// ... 220 more unit tests for business logic
```

#### Integration Tests: 80 (16%)
```typescript
// API endpoints (30 tests)
describe('POST /api/tasks', () => {
  it('creates task in database', async () => {...})
})

// Database queries (25 tests)
describe('TaskRepository', () => {
  it('finds tasks by status', async () => {...})
})

// Authentication flow (15 tests)
describe('Auth integration', () => {
  it('validates JWT and loads user', async () => {...})
})

// WebSocket integration (10 tests)
describe('Real-time updates', () => {
  it('broadcasts task updates', async () => {...})
})
```

#### E2E Tests: 20 (4%)
```typescript
// Critical flows only
describe('E2E: Task Management', () => {
  it('creates, edits, and completes task', async () => {...})
  it('shares task and collaborates', async () => {...})
  it('handles offline mode', async () => {...})
})

describe('E2E: Authentication', () => {
  it('registers, verifies email, and logs in', async () => {...})
})

describe('E2E: Payment', () => {
  it('upgrades to premium and processes payment', async () => {...})
})
```

**Execution Time:**
- Unit: 400 tests × 5ms = 2 seconds
- Integration: 80 tests × 500ms = 40 seconds
- E2E: 20 tests × 10s = 200 seconds (3.3 minutes)
- **Total: ~4 minutes**

---

## 🚀 Benefits of Pyramid Approach

### 1. Fast Feedback
- Unit tests run on every file save (< 1 second)
- Immediate feedback during development
- Catch errors before committing

### 2. Precise Failure Location
- Unit test failure → Exact function/line
- Integration test failure → Which integration point
- E2E test failure → Which user flow

### 3. Maintainability
- Unit tests rarely break from UI changes
- Fewer E2E tests = less maintenance burden
- Clear test boundaries

### 4. Development Speed
- Fast tests encourage TDD
- Quick iterations
- Developer confidence

---

## 📋 Best Practices

### ✅ Do

- **Start with unit tests** - Build solid foundation
- **Add integration selectively** - Only for integration concerns
- **Minimize E2E tests** - Only critical flows
- **Run unit tests constantly** - On every save
- **Run integration pre-commit** - Before pushing
- **Run E2E in CI/CD** - Before deployment
- **Categorize tests clearly** - unit/, integration/, e2e/

### ❌ Don't

- **Test logic in E2E** - Use unit tests instead
- **Skip unit tests** - Most important layer
- **Over-use integration** - Slower than needed
- **Test every scenario in E2E** - Too expensive
- **Mix test types** - Keep boundaries clear
- **Ignore pyramid balance** - Monitor ratios

---

## 🔗 Related Guides

- **[F.I.R.S.T Principles](first-principles.md)** - Unit test quality
- **[Integration Testing](../patterns/integration-testing.md)** - Middle layer
- **[E2E Testing](../patterns/e2e-testing.md)** - Top layer
- **[Test Strategy](https://martinfowler.com/bliki/TestPyramid.html)** - Original concept

---

## 🎓 Summary

**Key Takeaways:**

1. **70-80% Unit Tests** - Fast, focused, isolated
2. **15-20% Integration Tests** - Module boundaries
3. **5-10% E2E Tests** - Critical paths only
4. **Fast Feedback** - Most tests run in seconds
5. **Clear Boundaries** - Don't mix test types

**The Pyramid Principle:**
> "The higher up the pyramid you go, the fewer tests you should have, because they become slower, more expensive, and harder to maintain."

**Remember:** A well-balanced test pyramid provides fast feedback, precise failure location, and confidence without excessive maintenance burden.

---

**Next Steps:**
- Categorize existing tests into pyramid levels
- Identify E2E tests that should be unit tests
- Achieve pyramid balance over time
- Monitor test execution times
