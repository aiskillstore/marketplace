# BDD Integration (Given/When/Then)

**Integrating Behavior-Driven Development's "Given/When/Then" language with Arrange-Act-Assert for clear, behavior-focused tests.**

Behavior-Driven Development (BDD) and the Arrange-Act-Assert (AAA) pattern are complementary approaches. BDD provides human-readable language for defining behavior, while AAA offers structured test implementation. They map perfectly to each other.

---

## 🎯 The Synergy: GWT ↔ AAA

BDD's "Given/When/Then" and AAA are essentially the same pattern expressed for different audiences.

### Perfect One-to-One Mapping

| BDD Keyword | AAA Keyword | Purpose | Audience |
|-------------|-------------|---------|----------|
| **Given** | **Arrange** | Establish preconditions and state | Business + Developers |
| **When** | **Act** | Execute the behavior under test | Business + Developers |
| **Then** | **Assert** | Verify the outcome | Business + Developers |

**Key Insight:** Use BDD language for communication with stakeholders, AAA structure for test implementation.

---

## 📝 BDD "Given/When/Then" Language

### Given (Preconditions)

**Describes the initial context or pre-conditions of the scenario.**

**Focus:** The starting state

**Examples:**
- Given a user with insufficient funds
- Given an expired session token
- Given a shopping cart with 3 items
- Given the system is under high load

### When (Action/Event)

**Describes the specific action or event that triggers the behavior being tested.**

**Focus:** The action/event

**Examples:**
- When the user attempts to withdraw funds
- When the user tries to access protected resources
- When the user proceeds to checkout
- When 100 concurrent requests arrive

### Then (Expected Outcome)

**Describes the expected outcome or result of the action.**

**Focus:** The verifiable result

**Examples:**
- Then an InsufficientFundsError is thrown
- Then access is denied with a 401 status
- Then the order total includes tax and shipping
- Then the system responds within 500ms

---

## 🔄 Using GWT with AAA

### Method 1: GWT in Test Names

Use Given/When/Then structure in test names for clear documentation.

```typescript
import { describe, it, expect } from 'vitest'
import { BankAccount, InsufficientFundsError } from './bank-account'

describe('BankAccount', () => {
  it('Given_InsufficientFunds_When_WithdrawalAttempted_Then_ErrorThrown', () => {
    // Arrange (Given)
    const account = new BankAccount(50)

    // Act (When)
    const withdraw = () => account.withdraw(100)

    // Assert (Then)
    expect(withdraw).toThrow(InsufficientFundsError)
    expect(account.balance).toBe(50)
  })

  it('Given_SufficientFunds_When_WithdrawalMade_Then_BalanceUpdated', () => {
    // Arrange (Given)
    const account = new BankAccount(100)

    // Act (When)
    account.withdraw(30)

    // Assert (Then)
    expect(account.balance).toBe(70)
  })
})
```

### Method 2: GWT in Comments

Use comments to mark AAA sections with BDD language.

```typescript
describe('User Authentication', () => {
  it('rejects login with invalid credentials', async () => {
    // GIVEN / ARRANGE: a user with specific credentials
    const authService = new AuthService(mockUserRepo, mockTokenService)
    const validEmail = 'user@example.com'
    const invalidPassword = 'wrongpassword'

    // WHEN / ACT: authentication is attempted with invalid password
    const attempt = () => authService.login(validEmail, invalidPassword)

    // THEN / ASSERT: authentication fails with specific error
    await expect(attempt()).rejects.toThrow('Invalid credentials')
    expect(mockTokenService.create).not.toHaveBeenCalled()
  })
})
```

### Method 3: Descriptive Test Names

Use natural language that reads like a specification.

```typescript
describe('Order Processing', () => {
  describe('When customer has premium membership', () => {
    it('applies free shipping to orders', async () => {
      // Given
      const customer = createPremiumCustomer()
      const order = createOrder({ items: [{ price: 50 }] })

      // When
      const processed = await orderService.process(order, customer)

      // Then
      expect(processed.shipping.cost).toBe(0)
      expect(processed.shipping.method).toBe('free')
    })

    it('provides priority support access', async () => {
      // Given
      const customer = createPremiumCustomer()

      // When
      const supportLevel = await supportService.getSupportLevel(customer)

      // Then
      expect(supportLevel).toBe('priority')
    })
  })
})
```

---

## 🎨 Complete Examples

### Example 1: E-Commerce Checkout

```typescript
describe('Checkout Process', () => {
  describe('Given a cart with items', () => {
    describe('When user proceeds to checkout', () => {
      it('Then calculates tax based on shipping address', async () => {
        // Given (Arrange)
        const cart = new ShoppingCart([
          { id: '1', price: 100, quantity: 2 },
          { id: '2', price: 50, quantity: 1 }
        ])
        const shippingAddress = {
          state: 'CA', // 8% tax rate
          city: 'San Francisco',
          zip: '94102'
        }

        // When (Act)
        const checkout = await checkoutService.calculate(cart, shippingAddress)

        // Then (Assert)
        expect(checkout.subtotal).toBe(250)
        expect(checkout.tax).toBe(20) // 8% of 250
        expect(checkout.total).toBe(270)
      })

      it('Then applies available coupon discounts', async () => {
        // Given
        const cart = new ShoppingCart([{ id: '1', price: 100, quantity: 1 }])
        const coupon = { code: 'SAVE20', discount: 0.20 }

        // When
        const checkout = await checkoutService.calculate(cart, address, coupon)

        // Then
        expect(checkout.subtotal).toBe(100)
        expect(checkout.discount).toBe(20)
        expect(checkout.total).toBe(80)
      })
    })
  })
})
```

### Example 2: API Rate Limiting

```typescript
describe('API Rate Limiter', () => {
  describe('Given a user with standard tier', () => {
    describe('When making requests within rate limit', () => {
      it('Then all requests succeed', async () => {
        // Given
        const user = { id: 'user-1', tier: 'standard', limit: 100 }
        const rateLimiter = new RateLimiter()

        // When
        const results = await Promise.all(
          Array.from({ length: 50 }, () =>
            rateLimiter.checkLimit(user.id, user.limit)
          )
        )

        // Then
        expect(results.every(r => r.allowed)).toBe(true)
      })
    })

    describe('When exceeding rate limit', () => {
      it('Then subsequent requests are rejected', async () => {
        // Given
        const user = { id: 'user-2', tier: 'standard', limit: 10 }
        const rateLimiter = new RateLimiter()

        // When - Make requests beyond limit
        const results = await Promise.all(
          Array.from({ length: 15 }, () =>
            rateLimiter.checkLimit(user.id, user.limit)
          )
        )

        // Then
        const allowed = results.filter(r => r.allowed).length
        const rejected = results.filter(r => !r.allowed).length

        expect(allowed).toBeLessThanOrEqual(10)
        expect(rejected).toBeGreaterThan(0)
      })
    })
  })
})
```

### Example 3: Domain Model Invariants

```typescript
describe('Order Domain Model', () => {
  describe('Given an order in "pending" status', () => {
    describe('When attempting to ship the order', () => {
      it('Then transitions to "shipped" status', () => {
        // Given
        const order = new Order({ status: 'pending', items: [...] })

        // When
        order.ship({ carrier: 'UPS', trackingNumber: '123' })

        // Then
        expect(order.status).toBe('shipped')
        expect(order.shippedAt).toBeInstanceOf(Date)
        expect(order.tracking).toEqual({
          carrier: 'UPS',
          trackingNumber: '123'
        })
      })
    })

    describe('When attempting to ship without items', () => {
      it('Then throws InvalidOrderStateError', () => {
        // Given
        const order = new Order({ status: 'pending', items: [] })

        // When
        const ship = () => order.ship({ carrier: 'UPS', trackingNumber: '123' })

        // Then
        expect(ship).toThrow(InvalidOrderStateError)
        expect(ship).toThrow('Cannot ship order without items')
      })
    })
  })

  describe('Given an order already shipped', () => {
    describe('When attempting to cancel the order', () => {
      it('Then throws InvalidOrderStateError', () => {
        // Given
        const order = new Order({ status: 'shipped', items: [...] })

        // When
        const cancel = () => order.cancel('Customer request')

        // Then
        expect(cancel).toThrow(InvalidOrderStateError)
        expect(cancel).toThrow('Cannot cancel shipped order')
      })
    })
  })
})
```

---

## 🏢 Domain-Driven Design Alignment

BDD's Given/When/Then naturally aligns with Domain-Driven Design principles.

### 1. Ubiquitous Language

**DDD Principle:** Use domain language consistently across code, tests, and business discussions.

**BDD Implementation:**
```typescript
describe('Loan Application (Domain)', () => {
  // Use business terms from ubiquitous language
  it('Given_ApplicantWithGoodCredit_When_ApplicationSubmitted_Then_AutoApproved', () => {
    // Given: Use domain concepts
    const applicant = new Applicant({
      creditScore: 750, // Domain concept
      annualIncome: 80000,
      employmentYears: 5
    })

    // When: Use domain language
    const application = applicant.submitLoanApplication({
      amount: 50000,
      term: 60,
      purpose: 'home-improvement'
    })

    // Then: Verify business rules
    expect(application.status).toBe('auto-approved')
    expect(application.requiresManualReview).toBe(false)
  })
})
```

### 2. Testing Aggregates

**DDD Principle:** Aggregates enforce business invariants.

**BDD Implementation:**
```typescript
describe('Order Aggregate', () => {
  describe('Invariant: Order total must match sum of items', () => {
    it('Given_ItemsAdded_When_TotalCalculated_Then_MatchesSum', () => {
      // Given
      const order = new Order()
      order.addItem(new OrderItem({ price: 10, quantity: 2 }))
      order.addItem(new OrderItem({ price: 15, quantity: 1 }))

      // When
      order.calculateTotal()

      // Then
      expect(order.total).toBe(35)
    })
  })

  describe('Invariant: Cannot add items to completed order', () => {
    it('Given_CompletedOrder_When_ItemAdded_Then_ThrowsError', () => {
      // Given
      const order = new Order({ status: 'completed' })

      // When
      const addItem = () => order.addItem(new OrderItem({ price: 10, quantity: 1 }))

      // Then
      expect(addItem).toThrow(InvalidOrderStateError)
    })
  })
})
```

### 3. Testing Domain Events

**DDD Principle:** Domain events represent something that happened in the domain.

**BDD Implementation:**
```typescript
describe('User Registration Domain Events', () => {
  it('Given_NewUser_When_Registered_Then_EmitsUserRegisteredEvent', () => {
    // Given
    const userService = new UserService(eventPublisher)
    const userData = { email: 'new@example.com', name: 'New User' }

    // When
    userService.register(userData)

    // Then
    expect(eventPublisher.publish).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'UserRegistered',
        data: expect.objectContaining({
          email: 'new@example.com'
        })
      })
    )
  })
})
```

### 4. Testing Bounded Contexts

**DDD Principle:** Each bounded context has its own model and language.

**BDD Implementation:**
```typescript
// Ordering Context
describe('Ordering Context', () => {
  it('Given_CartWithItems_When_CheckedOut_Then_CreatesOrder', () => {
    // "Order" in Ordering Context means purchase order
    const cart = new ShoppingCart([...])
    const order = checkoutService.createOrder(cart)
    expect(order).toBeInstanceOf(PurchaseOrder)
  })
})

// Fulfillment Context
describe('Fulfillment Context', () => {
  it('Given_PurchaseOrder_When_Fulfilled_Then_CreatesShipment', () => {
    // "Order" in Fulfillment Context means shipment order
    const purchaseOrder = { items: [...] }
    const shipment = fulfillmentService.createShipment(purchaseOrder)
    expect(shipment).toBeInstanceOf(ShipmentOrder)
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Use domain language** in Given/When/Then descriptions
- **Test one behavior** per test case
- **Make tests readable** by non-technical stakeholders
- **Structure with AAA** for implementation clarity
- **Name tests descriptively** using business terminology
- **Focus on behavior** not implementation

### ❌ Don't

- **Test implementation details** - focus on observable behavior
- **Use technical jargon** in Given/When/Then
- **Test multiple scenarios** in one test
- **Write vague descriptions** - be specific
- **Skip the structure** - always use Given/When/Then
- **Forget the "why"** - tests should explain business rules

---

## 🔗 Related Patterns

- **[AAA Pattern](aaa-pattern.md)** - Technical structure for BDD tests
- **[Black Box Testing](../strategies/black-box-testing.md)** - Testing behavior, not implementation
- **[F.I.R.S.T Principles](first-principles.md)** - Quality attributes for all tests

---

## 🎓 Summary

**Key Takeaways:**

1. **Perfect Mapping** - Given/When/Then maps 1:1 to Arrange/Act/Assert
2. **Two Audiences** - BDD for stakeholders, AAA for developers
3. **Living Documentation** - Tests become executable specifications
4. **Domain Alignment** - Natural fit with Domain-Driven Design
5. **Behavior Focus** - Emphasizes what the system does, not how

**Integration Pattern:**
```typescript
describe('Business Feature', () => {
  it('Given_[Context]_When_[Action]_Then_[Outcome]', () => {
    // GIVEN / ARRANGE: Setup state

    // WHEN / ACT: Execute behavior

    // THEN / ASSERT: Verify outcome
  })
})
```

**Remember:** BDD and AAA are complementary, not competing. Use both to write tests that are clear to stakeholders and maintainable for developers.

---

**Next Steps:**
- Review [Cucumber/Gherkin](https://cucumber.io/docs/gherkin/) for full BDD frameworks
- Explore [SpecFlow](https://specflow.org/) for .NET
- Practice [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
