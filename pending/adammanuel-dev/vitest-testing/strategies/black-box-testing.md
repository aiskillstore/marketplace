# Black Box Testing Strategy

**Testing software behavior through public interfaces without knowledge of internal implementation.**

Black box testing treats the system under test as a "black box" - you provide inputs and verify outputs without examining the internal workings. This approach creates robust, maintainable tests that remain valid through refactoring.

---

## 🎯 Core Principle

**Test WHAT the code does, not HOW it does it.**

### The Black Box Approach
- ✅ **Focus on:** Public API, inputs, outputs, observable behavior
- ❌ **Ignore:** Private methods, internal state, implementation details
- **Result:** Tests that survive refactoring

---

## 📊 When to Use Black Box Testing

### ✅ Use Black Box Testing For:
- **Public APIs** - Services, controllers, modules
- **User-facing behavior** - UI components, CLI tools
- **Contract testing** - API endpoints, library interfaces
- **Domain logic** - Business rules, calculations
- **Integration points** - External system boundaries

### ❌ Avoid Black Box Testing For:
- **Internal utilities** - Use white box or don't test separately
- **Private helpers** - Should be tested indirectly
- **Framework code** - Trust third-party libraries
- **Trivial getters/setters** - No logic to test

---

## 🔍 Black Box Testing Techniques

### 1. Equivalence Partitioning

Divide input data into logical groups where each group is expected to be processed similarly.

```typescript
describe('UserValidator.validateAge', () => {
  // Partition 1: Valid ages (18-120)
  it.each([
    18,  // Boundary: minimum valid
    25,  // Middle: typical valid
    65,  // Middle: typical valid
    120  // Boundary: maximum valid
  ])('accepts valid age: %i', (age) => {
    expect(validator.validateAge(age)).toBe(true)
  })

  // Partition 2: Too young (< 18)
  it.each([
    0,
    10,
    17   // Boundary: just below minimum
  ])('rejects age too young: %i', (age) => {
    expect(validator.validateAge(age)).toBe(false)
  })

  // Partition 3: Too old (> 120)
  it.each([
    121, // Boundary: just above maximum
    150,
    999
  ])('rejects age too old: %i', (age) => {
    expect(validator.validateAge(age)).toBe(false)
  })
})
```

### 2. Boundary Value Analysis

Test values at the edges of input ranges where errors often occur.

```typescript
describe('ShippingCalculator.calculate', () => {
  describe('Weight-based pricing boundaries', () => {
    // Boundary: 0-5 kg = $10
    it('charges $10 for weight at lower boundary (0.1 kg)', () => {
      expect(calculator.calculate(0.1)).toBe(10)
    })

    it('charges $10 for weight at upper boundary (5 kg)', () => {
      expect(calculator.calculate(5)).toBe(10)
    })

    // Boundary: 5-20 kg = $25
    it('charges $25 for weight just above boundary (5.1 kg)', () => {
      expect(calculator.calculate(5.1)).toBe(25)
    })

    it('charges $25 for weight at upper boundary (20 kg)', () => {
      expect(calculator.calculate(20)).toBe(25)
    })

    // Boundary: > 20 kg = $50
    it('charges $50 for weight just above boundary (20.1 kg)', () => {
      expect(calculator.calculate(20.1)).toBe(50)
    })
  })
})
```

### 3. Decision Table Testing

For complex logic involving multiple conditions, map all combinations.

```typescript
describe('LoanApproval.evaluate', () => {
  // Decision table:
  // Age >= 18 | Income >= $30k | Credit >= 650 | Approved?
  // -----------|----------------|---------------|----------
  // Yes        | Yes            | Yes           | Yes
  // Yes        | Yes            | No            | No
  // Yes        | No             | Yes           | No
  // No         | Yes            | Yes           | No

  it('approves when all criteria met', () => {
    const applicant = {
      age: 25,
      annualIncome: 50000,
      creditScore: 700
    }

    expect(loanApproval.evaluate(applicant)).toBe(true)
  })

  it('rejects when credit score too low', () => {
    const applicant = {
      age: 25,
      annualIncome: 50000,
      creditScore: 600 // Below threshold
    }

    expect(loanApproval.evaluate(applicant)).toBe(false)
  })

  it('rejects when income too low', () => {
    const applicant = {
      age: 25,
      annualIncome: 20000, // Below threshold
      creditScore: 700
    }

    expect(loanApproval.evaluate(applicant)).toBe(false)
  })

  it('rejects when age too young', () => {
    const applicant = {
      age: 17, // Below threshold
      annualIncome: 50000,
      creditScore: 700
    }

    expect(loanApproval.evaluate(applicant)).toBe(false)
  })
})
```

### 4. State Transition Testing

For stateful systems, test valid and invalid state transitions.

```typescript
describe('Order state transitions', () => {
  it('transitions from pending to confirmed', () => {
    const order = new Order({ status: 'pending' })

    order.confirm()

    expect(order.status).toBe('confirmed')
  })

  it('transitions from confirmed to shipped', () => {
    const order = new Order({ status: 'confirmed' })

    order.ship({ carrier: 'UPS', tracking: '123' })

    expect(order.status).toBe('shipped')
    expect(order.tracking).toBeDefined()
  })

  it('prevents invalid transition from shipped to confirmed', () => {
    const order = new Order({ status: 'shipped' })

    expect(() => order.confirm()).toThrow(InvalidStateTransitionError)
  })

  it('allows cancellation from pending or confirmed', () => {
    const pendingOrder = new Order({ status: 'pending' })
    pendingOrder.cancel()
    expect(pendingOrder.status).toBe('cancelled')

    const confirmedOrder = new Order({ status: 'confirmed' })
    confirmedOrder.cancel()
    expect(confirmedOrder.status).toBe('cancelled')
  })

  it('prevents cancellation from shipped status', () => {
    const order = new Order({ status: 'shipped' })

    expect(() => order.cancel()).toThrow('Cannot cancel shipped order')
  })
})
```

---

## 💡 Black Box Testing Examples

### Example 1: API Endpoint

```typescript
describe('POST /api/users (Black Box)', () => {
  it('creates user with valid data', async () => {
    // Arrange
    const userData = {
      email: 'test@example.com',
      name: 'Test User',
      password: 'SecurePass123!'
    }

    // Act
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })

    // Assert
    expect(response.status).toBe(201)
    const user = await response.json()
    expect(user).toMatchObject({
      id: expect.any(String),
      email: 'test@example.com',
      name: 'Test User'
    })
    expect(user.password).toBeUndefined() // Never expose password
  })

  it('validates email format', async () => {
    const invalidData = {
      email: 'invalid-email',
      name: 'Test',
      password: 'Pass123!'
    }

    const response = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(invalidData)
    })

    expect(response.status).toBe(400)
    const error = await response.json()
    expect(error.message).toContain('Invalid email format')
  })

  it('rejects duplicate email', async () => {
    // First user
    await createUser({ email: 'duplicate@example.com' })

    // Attempt duplicate
    const response = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify({
        email: 'duplicate@example.com',
        name: 'Another User',
        password: 'Pass123!'
      })
    })

    expect(response.status).toBe(409)
    const error = await response.json()
    expect(error.message).toContain('Email already exists')
  })
})
```

### Example 2: Domain Model

```typescript
describe('BankAccount (Domain Black Box)', () => {
  describe('Invariant: Balance cannot go negative', () => {
    it('prevents withdrawal exceeding balance', () => {
      // Arrange
      const account = new BankAccount(50)

      // Act
      const withdraw = () => account.withdraw(100)

      // Assert
      expect(withdraw).toThrow(InsufficientFundsError)
      expect(withdraw).toThrow('Insufficient funds: attempted to withdraw 100 but balance is 50')
      expect(account.balance).toBe(50) // Balance unchanged
    })

    it('allows withdrawal up to balance', () => {
      // Arrange
      const account = new BankAccount(100)

      // Act
      account.withdraw(100)

      // Assert
      expect(account.balance).toBe(0)
    })
  })

  describe('Business Rule: Premium accounts have no transfer fees', () => {
    it('applies fee for standard account transfers', () => {
      const source = new BankAccount(100, { isPremium: false })
      const dest = new BankAccount(0)

      source.transferTo(dest, 50)

      // $50 transfer + $2 fee (4%)
      expect(source.balance).toBe(48)
      expect(dest.balance).toBe(50)
    })

    it('no fee for premium account transfers', () => {
      const source = new BankAccount(100, { isPremium: true })
      const dest = new BankAccount(0)

      source.transferTo(dest, 50)

      // No fee for premium accounts
      expect(source.balance).toBe(50)
      expect(dest.balance).toBe(50)
    })
  })
})
```

### Example 3: Calculator Service

```typescript
describe('DiscountCalculator (Black Box)', () => {
  it('calculates 20% discount correctly', () => {
    const result = calculator.applyDiscount(100, 0.20)
    expect(result).toBe(80)
  })

  it('handles zero discount', () => {
    const result = calculator.applyDiscount(100, 0)
    expect(result).toBe(100)
  })

  it('handles 100% discount', () => {
    const result = calculator.applyDiscount(100, 1.0)
    expect(result).toBe(0)
  })

  it('rejects negative discount', () => {
    expect(() => calculator.applyDiscount(100, -0.1))
      .toThrow('Discount must be between 0 and 1')
  })

  it('rejects discount over 100%', () => {
    expect(() => calculator.applyDiscount(100, 1.1))
      .toThrow('Discount must be between 0 and 1')
  })

  it('handles decimal precision correctly', () => {
    const result = calculator.applyDiscount(99.99, 0.15)
    expect(result).toBeCloseTo(84.99, 2)
  })
})
```

---

## 🚫 What NOT to Test (White Box Territory)

```typescript
// ❌ BAD: Testing private method
class UserService {
  private hashPassword(password: string): string {
    return bcrypt.hashSync(password, 10)
  }
}

// Don't test this directly
it('hashes password', () => {
  const service = new UserService()
  const hashed = service['hashPassword']('plain') // BAD: Accessing private
  expect(hashed).not.toBe('plain')
})

// ✅ GOOD: Test through public API
it('stores hashed password when creating user', async () => {
  const service = new UserService()
  const user = await service.createUser({
    email: 'test@example.com',
    password: 'plaintext'
  })

  // Verify behavior: password is hashed
  expect(user.password).not.toBe('plaintext')
  expect(user.password).toMatch(/^\$2[ayb]\$.{56}$/) // bcrypt format
})
```

---

## 🎨 Black Box vs White Box

| Aspect | Black Box | White Box |
|--------|-----------|-----------|
| **Focus** | Behavior | Implementation |
| **Knowledge** | Public API only | Internal structure |
| **Test Target** | Inputs → Outputs | Code paths, branches |
| **Robustness** | High (survives refactoring) | Low (breaks on refactoring) |
| **Maintenance** | Low | High |
| **Best For** | Business logic, APIs | Complex algorithms, edge cases |

---

## 📋 Best Practices

### ✅ Do

- **Test public interfaces** only
- **Focus on observable behavior** - what users see
- **Use domain language** in tests
- **Test edge cases** and boundaries
- **Verify error handling** - exceptions, error messages
- **Test state changes** - before/after comparisons

### ❌ Don't

- **Test private methods** - test through public API instead
- **Assert on internal state** unless exposed publicly
- **Depend on implementation** details
- **Test framework internals** - trust they work
- **Over-specify** - test behavior, not exact steps
- **Mock what you don't own** - wrap and test wrapper

---

## 🔗 Related Strategies

- **[Implementation Details](implementation-details.md)** - When white box testing is acceptable
- **[F.I.R.S.T Principles](../principles/first-principles.md)** - Quality attributes
- **[AAA Pattern](../principles/aaa-pattern.md)** - Structure for black box tests
- **[BDD Integration](../principles/bdd-integration.md)** - Behavior-focused testing

---

## 🎓 Summary

**Key Takeaways:**

1. **Public API Focus** - Test only through public interfaces
2. **Input/Output Testing** - Verify behavior based on inputs and outputs
3. **Implementation Independence** - Tests survive refactoring
4. **Specification-Based** - Derive tests from requirements, not code
5. **User Perspective** - Test from the viewpoint of API consumers

**The Black Box Mindset:**
> "If I can't observe it through the public API, I shouldn't test it directly."

**Remember:** Black box testing creates robust, maintainable tests that document behavior and remain valid through implementation changes. It's the preferred approach for most testing scenarios.

---

**Next Steps:**
- Practice [Equivalence Partitioning](https://en.wikipedia.org/wiki/Equivalence_partitioning)
- Learn [Boundary Value Analysis](https://en.wikipedia.org/wiki/Boundary-value_analysis)
- Explore [Decision Table Testing](https://en.wikipedia.org/wiki/Decision_table)
