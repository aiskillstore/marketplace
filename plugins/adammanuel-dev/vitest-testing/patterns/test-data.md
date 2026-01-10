# Test Data Management Patterns

**Comprehensive patterns for creating, organizing, and maintaining test data for reliable, maintainable tests.**

Managing test data effectively is crucial for writing maintainable and reliable tests. This guide provides patterns for creating consistent test data while avoiding duplication and brittleness.

---

## 🎯 Test Data Strategy

### Goals
- **Consistency** - Same data structure across related tests
- **Maintainability** - Easy to update when models change
- **Readability** - Clear what data represents
- **Isolation** - No shared state between tests
- **Flexibility** - Easy to customize for specific scenarios

### Anti-Patterns to Avoid
- ❌ **Hardcoding data in every test** - Duplication nightmare
- ❌ **Sharing mutable test data** - Tests interfere with each other
- ❌ **Magic values** - Unclear what `42` or `"test"` represents
- ❌ **Over-complex setup** - Tests become unreadable
- ❌ **Production data in tests** - Security and compliance risks

---

## 🏭 Test Data Factories

Centralized way to create test objects with sensible defaults while allowing customization.

### Basic Factory Pattern

```typescript
// factories/user.factory.ts
import { faker } from '@faker-js/faker'

export interface User {
  id: string
  email: string
  name: string
  age: number
  role: 'admin' | 'user' | 'moderator'
  createdAt: Date
  preferences: {
    theme: 'light' | 'dark'
    notifications: boolean
    language: string
  }
}

export class UserFactory {
  private static counter = 0

  // Create single user with optional overrides
  static create(overrides: Partial<User> = {}): User {
    const id = overrides.id || `user-${++this.counter}`

    return {
      id,
      email: `${id}@example.com`,
      name: faker.person.fullName(),
      age: faker.number.int({ min: 18, max: 80 }),
      role: 'user',
      createdAt: new Date(),
      preferences: {
        theme: 'light',
        notifications: true,
        language: 'en'
      },
      ...overrides,
      // Handle nested object overrides
      preferences: {
        theme: 'light',
        notifications: true,
        language: 'en',
        ...(overrides.preferences || {})
      }
    }
  }

  // Create multiple users
  static createMany(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, () => this.create(overrides))
  }

  // Preset variations for common scenarios
  static createAdmin(overrides: Partial<User> = {}): User {
    return this.create({
      role: 'admin',
      email: `admin-${++this.counter}@example.com`,
      ...overrides
    })
  }

  static createNewUser(overrides: Partial<User> = {}): User {
    return this.create({
      createdAt: new Date(),
      preferences: {
        theme: 'light',
        notifications: true,
        language: 'en'
      },
      ...overrides
    })
  }

  static createLegacyUser(overrides: Partial<User> = {}): User {
    const twoYearsAgo = new Date()
    twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2)

    return this.create({
      createdAt: twoYearsAgo,
      preferences: {
        theme: 'light',
        notifications: false,
        language: 'en'
      },
      ...overrides
    })
  }

  // Reset counter for test isolation
  static reset(): void {
    this.counter = 0
  }
}
```

### Using Factories in Tests

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { UserFactory } from './factories/user.factory'

describe('User service', () => {
  beforeEach(() => {
    UserFactory.reset() // Ensure consistent IDs across tests
  })

  it('processes regular user', () => {
    const user = UserFactory.create({ name: 'John Doe' })

    expect(user.name).toBe('John Doe')
    expect(user.role).toBe('user')
    expect(user.id).toBe('user-1')
  })

  it('handles admin privileges', () => {
    const admin = UserFactory.createAdmin()

    expect(admin.role).toBe('admin')
    expect(admin.email).toContain('admin')
  })

  it('processes multiple users', () => {
    const users = UserFactory.createMany(5, { age: 25 })

    expect(users).toHaveLength(5)
    expect(users.every(u => u.age === 25)).toBe(true)
  })
})
```

---

## 🏗️ Builder Pattern

Fluent interface for constructing complex test objects step by step.

### Builder Implementation

```typescript
// builders/order.builder.ts
export class OrderBuilder {
  private order: any = {
    id: 'order-1',
    customerId: 'customer-1',
    items: [],
    status: 'pending',
    totalAmount: 0,
    shipping: {
      method: 'standard',
      address: null,
      cost: 0
    },
    payment: {
      method: 'credit_card',
      status: 'pending'
    },
    createdAt: new Date(),
    updatedAt: new Date()
  }

  withId(id: string): OrderBuilder {
    this.order.id = id
    return this
  }

  forCustomer(customerId: string): OrderBuilder {
    this.order.customerId = customerId
    return this
  }

  withItem(product: string, quantity: number, price: number): OrderBuilder {
    this.order.items.push({ product, quantity, price })
    this.recalculateTotal()
    return this
  }

  withItems(items: Array<{ product: string; quantity: number; price: number }>): OrderBuilder {
    this.order.items = [...this.order.items, ...items]
    this.recalculateTotal()
    return this
  }

  withStatus(status: string): OrderBuilder {
    this.order.status = status
    return this
  }

  withShipping(method: string, address: any, cost: number = 0): OrderBuilder {
    this.order.shipping = { method, address, cost }
    this.recalculateTotal()
    return this
  }

  withPayment(method: string, status: string = 'pending'): OrderBuilder {
    this.order.payment = { method, status }
    return this
  }

  asCompleted(): OrderBuilder {
    this.order.status = 'completed'
    this.order.payment.status = 'paid'
    this.order.completedAt = new Date()
    return this
  }

  asCancelled(reason?: string): OrderBuilder {
    this.order.status = 'cancelled'
    this.order.cancelledAt = new Date()
    if (reason) {
      this.order.cancellationReason = reason
    }
    return this
  }

  private recalculateTotal(): void {
    const itemsTotal = this.order.items.reduce(
      (sum: number, item: any) => sum + item.price * item.quantity,
      0
    )
    this.order.totalAmount = itemsTotal + (this.order.shipping?.cost || 0)
  }

  build() {
    return { ...this.order }
  }

  // Static factory methods for common scenarios
  static aSmallOrder(): OrderBuilder {
    return new OrderBuilder()
      .withItem('Widget', 1, 9.99)
      .withShipping('standard', { city: 'New York' }, 5.00)
  }

  static aLargeOrder(): OrderBuilder {
    return new OrderBuilder()
      .withItems([
        { product: 'Laptop', quantity: 2, price: 999.99 },
        { product: 'Mouse', quantity: 3, price: 29.99 },
        { product: 'Keyboard', quantity: 2, price: 79.99 }
      ])
      .withShipping('express', { city: 'San Francisco' }, 25.00)
  }
}
```

### Using Builders in Tests

```typescript
describe('Order processing', () => {
  it('calculates order total correctly', () => {
    const order = new OrderBuilder()
      .withItem('Book', 2, 15.99)
      .withItem('Pen', 5, 2.99)
      .withShipping('standard', { city: 'Boston' }, 10.00)
      .build()

    expect(order.totalAmount).toBe(31.98 + 14.95 + 10.00)
  })

  it('handles cancelled orders', () => {
    const order = OrderBuilder
      .aLargeOrder()
      .asCancelled('Customer request')
      .build()

    expect(order.status).toBe('cancelled')
    expect(order.cancellationReason).toBe('Customer request')
    expect(order.cancelledAt).toBeDefined()
  })

  it('builds complex orders fluently', () => {
    const order = new OrderBuilder()
      .forCustomer('cust-123')
      .withItem('Product A', 3, 50.00)
      .withItem('Product B', 1, 100.00)
      .withShipping('express', { city: 'Chicago' }, 15.00)
      .withPayment('paypal', 'paid')
      .asCompleted()
      .build()

    expect(order.customerId).toBe('cust-123')
    expect(order.items).toHaveLength(2)
    expect(order.totalAmount).toBe(265.00)
    expect(order.status).toBe('completed')
  })
})
```

---

## 📁 Fixture Management

Reusable test data loaded from files, useful for integration tests.

### Fixture Loader

```typescript
// fixtures/database.fixtures.ts
import { readFile, writeFile } from 'fs/promises'
import { join } from 'path'

export class DatabaseFixtures {
  private static fixturesPath = join(__dirname, 'data')

  // Load JSON fixtures
  static async loadUsers(): Promise<any[]> {
    const data = await readFile(
      join(this.fixturesPath, 'users.json'),
      'utf-8'
    )
    return JSON.parse(data)
  }

  static async loadProducts(): Promise<any[]> {
    const data = await readFile(
      join(this.fixturesPath, 'products.json'),
      'utf-8'
    )
    return JSON.parse(data)
  }

  // Load and transform fixtures
  static async loadTestScenario(scenario: string): Promise<any> {
    const data = await readFile(
      join(this.fixturesPath, 'scenarios', `${scenario}.json`),
      'utf-8'
    )

    const parsed = JSON.parse(data)

    // Transform dates from strings to Date objects
    return this.transformDates(parsed)
  }

  private static transformDates(obj: any): any {
    if (obj === null || obj === undefined) return obj

    if (typeof obj === 'string') {
      // Check if it's a date string
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(obj)) {
        return new Date(obj)
      }
      return obj
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.transformDates(item))
    }

    if (typeof obj === 'object') {
      const transformed: any = {}
      for (const [key, value] of Object.entries(obj)) {
        transformed[key] = this.transformDates(value)
      }
      return transformed
    }

    return obj
  }

  // Create database snapshot
  static async createSnapshot(name: string, data: any): Promise<void> {
    const snapshotPath = join(this.fixturesPath, 'snapshots', `${name}.json`)
    await writeFile(snapshotPath, JSON.stringify(data, null, 2))
  }

  // Load database snapshot
  static async loadSnapshot(name: string): Promise<any> {
    const snapshotPath = join(this.fixturesPath, 'snapshots', `${name}.json`)
    const data = await readFile(snapshotPath, 'utf-8')
    return JSON.parse(data)
  }
}
```

### Using Fixtures in Tests

```typescript
describe('Integration tests', () => {
  let testData: any

  beforeAll(async () => {
    // Load complex test scenario once
    testData = await DatabaseFixtures.loadTestScenario('e-commerce-flow')
  })

  it('processes order with fixtures', async () => {
    const { users, products, orders } = testData

    // Use loaded fixtures in test
    const result = await processOrder(orders[0], users[0], products)

    expect(result.success).toBe(true)
  })

  it('validates product catalog from fixtures', async () => {
    const products = await DatabaseFixtures.loadProducts()

    expect(products).toHaveLength(50)
    expect(products.every(p => p.price > 0)).toBe(true)
  })
})
```

---

## 🌱 Seed Data Generation

Generate large volumes of realistic test data for performance and load testing.

### Seed Generator

```typescript
// generators/seed-generator.ts
import { faker } from '@faker-js/faker'

export class SeedGenerator {
  // Generate interconnected data with relationships
  static generateEcommerceData(config: {
    userCount: number
    productCount: number
    orderCount: number
  }) {
    const users = this.generateUsers(config.userCount)
    const products = this.generateProducts(config.productCount)
    const orders = this.generateOrders(config.orderCount, users, products)

    return { users, products, orders }
  }

  private static generateUsers(count: number) {
    return Array.from({ length: count }, (_, i) => ({
      id: `user-${i + 1}`,
      email: faker.internet.email(),
      name: faker.person.fullName(),
      phone: faker.phone.number(),
      address: {
        street: faker.location.streetAddress(),
        city: faker.location.city(),
        state: faker.location.state(),
        zip: faker.location.zipCode(),
        country: faker.location.country()
      },
      createdAt: faker.date.past({ years: 2 }),
      lastLoginAt: faker.date.recent({ days: 30 }),
      isActive: faker.datatype.boolean({ probability: 0.9 }),
      preferences: {
        newsletter: faker.datatype.boolean({ probability: 0.6 }),
        smsAlerts: faker.datatype.boolean({ probability: 0.3 })
      }
    }))
  }

  private static generateProducts(count: number) {
    const categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']

    return Array.from({ length: count }, (_, i) => ({
      id: `product-${i + 1}`,
      sku: faker.string.alphanumeric(8).toUpperCase(),
      name: faker.commerce.productName(),
      description: faker.commerce.productDescription(),
      category: faker.helpers.arrayElement(categories),
      price: parseFloat(faker.commerce.price({ min: 5, max: 1000 })),
      cost: parseFloat(faker.commerce.price({ min: 2, max: 500 })),
      stock: faker.number.int({ min: 0, max: 500 }),
      images: Array.from(
        { length: faker.number.int({ min: 1, max: 5 }) },
        () => faker.image.url()
      ),
      attributes: {
        weight: faker.number.float({ min: 0.1, max: 50, precision: 0.1 }),
        dimensions: {
          length: faker.number.int({ min: 1, max: 100 }),
          width: faker.number.int({ min: 1, max: 100 }),
          height: faker.number.int({ min: 1, max: 100 })
        }
      },
      isAvailable: faker.datatype.boolean({ probability: 0.85 }),
      createdAt: faker.date.past({ years: 1 })
    }))
  }

  private static generateOrders(count: number, users: any[], products: any[]) {
    return Array.from({ length: count }, (_, i) => {
      const user = faker.helpers.arrayElement(users)
      const itemCount = faker.number.int({ min: 1, max: 5 })
      const items = Array.from({ length: itemCount }, () => {
        const product = faker.helpers.arrayElement(products)
        const quantity = faker.number.int({ min: 1, max: 3 })
        return {
          productId: product.id,
          productName: product.name,
          price: product.price,
          quantity,
          subtotal: product.price * quantity
        }
      })

      const subtotal = items.reduce((sum, item) => sum + item.subtotal, 0)
      const tax = subtotal * 0.08
      const shipping = subtotal > 50 ? 0 : 9.99

      return {
        id: `order-${i + 1}`,
        orderNumber: faker.string.alphanumeric(10).toUpperCase(),
        userId: user.id,
        items,
        subtotal,
        tax,
        shipping,
        total: subtotal + tax + shipping,
        status: faker.helpers.arrayElement([
          'pending',
          'processing',
          'shipped',
          'delivered',
          'cancelled'
        ]),
        paymentMethod: faker.helpers.arrayElement([
          'credit_card',
          'paypal',
          'stripe'
        ]),
        shippingAddress: user.address,
        notes: faker.datatype.boolean({ probability: 0.2 })
          ? faker.lorem.sentence()
          : null,
        createdAt: faker.date.recent({ days: 90 }),
        updatedAt: faker.date.recent({ days: 30 })
      }
    })
  }

  // Generate time-series data
  static generateTimeSeriesData(
    startDate: Date,
    endDate: Date,
    intervalMinutes: number
  ) {
    const data = []
    const current = new Date(startDate)

    while (current <= endDate) {
      data.push({
        timestamp: new Date(current),
        value: faker.number.float({ min: 0, max: 100, precision: 0.01 }),
        volume: faker.number.int({ min: 100, max: 10000 }),
        metadata: {
          source: faker.helpers.arrayElement(['sensor-1', 'sensor-2', 'sensor-3']),
          quality: faker.number.float({ min: 0.8, max: 1, precision: 0.01 })
        }
      })

      current.setMinutes(current.getMinutes() + intervalMinutes)
    }

    return data
  }
}
```

### Using Seed Data in Tests

```typescript
describe('Load testing with seed data', () => {
  it('handles large dataset', () => {
    const data = SeedGenerator.generateEcommerceData({
      userCount: 1000,
      productCount: 500,
      orderCount: 5000
    })

    expect(data.users).toHaveLength(1000)
    expect(data.products).toHaveLength(500)
    expect(data.orders).toHaveLength(5000)

    // Test that relationships are valid
    const userIds = new Set(data.users.map(u => u.id))
    const productIds = new Set(data.products.map(p => p.id))

    for (const order of data.orders) {
      expect(userIds.has(order.userId)).toBe(true)
      for (const item of order.items) {
        expect(productIds.has(item.productId)).toBe(true)
      }
    }
  })
})
```

---

## 🔧 State Management for Tests

Managing application state during tests for isolation and reproducibility.

### Test State Manager

```typescript
// test-helpers/state-manager.ts
export class TestStateManager {
  private originalState: Map<string, any> = new Map()
  private mocks: any[] = []

  // Save current state before tests
  saveState(key: string, value: any): void {
    if (!this.originalState.has(key)) {
      this.originalState.set(key, structuredClone(value))
    }
  }

  // Restore specific state
  restoreState(key: string): any {
    if (this.originalState.has(key)) {
      return structuredClone(this.originalState.get(key))
    }
    return undefined
  }

  // Restore all state
  restoreAll(): void {
    const entries = Array.from(this.originalState.entries()).reverse()
    for (const [key, value] of entries) {
      if (key.startsWith('env.')) {
        const envKey = key.substring(4)
        process.env[envKey] = value
      } else if (key.startsWith('global.')) {
        const globalKey = key.substring(7)
        ;(global as any)[globalKey] = value
      }
    }
  }

  // Track mocks for cleanup
  addMock(mock: any): void {
    this.mocks.push(mock)
  }

  // Clean up all mocks
  clearMocks(): void {
    for (const mock of this.mocks) {
      if (typeof mock.mockRestore === 'function') {
        mock.mockRestore()
      } else if (typeof mock.restore === 'function') {
        mock.restore()
      }
    }
    this.mocks = []
  }

  // Full cleanup
  cleanup(): void {
    this.restoreAll()
    this.clearMocks()
    this.originalState.clear()
  }

  // Create isolated test environment
  static createIsolatedEnvironment() {
    const manager = new TestStateManager()

    // Save critical global state
    manager.saveState('env.NODE_ENV', process.env.NODE_ENV)
    manager.saveState('env.API_URL', process.env.API_URL)
    manager.saveState('global.fetch', global.fetch)

    return {
      manager,
      setup: (overrides: Record<string, any> = {}) => {
        for (const [key, value] of Object.entries(overrides)) {
          if (key.startsWith('env.')) {
            process.env[key.substring(4)] = value
          } else if (key.startsWith('global.')) {
            ;(global as any)[key.substring(7)] = value
          }
        }
      },
      cleanup: () => manager.cleanup()
    }
  }
}
```

### Using State Manager in Tests

```typescript
describe('Stateful component tests', () => {
  const testEnv = TestStateManager.createIsolatedEnvironment()

  beforeEach(() => {
    testEnv.setup({
      'env.API_URL': 'http://test-api.local',
      'env.FEATURE_FLAG': 'enabled'
    })
  })

  afterEach(() => {
    testEnv.cleanup()
  })

  it('uses test environment', () => {
    expect(process.env.API_URL).toBe('http://test-api.local')
    expect(process.env.FEATURE_FLAG).toBe('enabled')
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Use factories** for consistent object creation
- **Reset state** between tests with `beforeEach`
- **Use realistic data** with faker.js
- **Document test data** with clear variable names
- **Create preset variations** for common scenarios
- **Isolate test data** - no shared mutable state

### ❌ Don't

- **Hardcode data** in every test
- **Share test data** between unrelated tests
- **Use production data** in tests
- **Create overly complex** builders/factories
- **Forget to reset** factories between tests
- **Mix test data** with test logic

---

## 🔗 Related Patterns

- **[Test Doubles](test-doubles.md)** - Mock factories
- **[F.I.R.S.T Principles](../principles/first-principles.md)** - Repeatable tests need consistent data
- **[Performance Testing](performance-testing.md)** - Seed data for load tests

---

**Next Steps:**
- Install [@faker-js/faker](https://fakerjs.dev/)
- Review [Test Data Builders](https://www.natpryce.com/articles/000714.html)
- Explore [Fixture Patterns](https://martinfowler.com/bliki/ObjectMother.html)
