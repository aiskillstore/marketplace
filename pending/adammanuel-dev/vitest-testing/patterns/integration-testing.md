# Integration Testing Patterns

**Comprehensive patterns for testing how multiple units work together.**

Integration tests verify that different parts of your system work correctly when combined. They test the boundaries between components, external services, and infrastructure.

---

## 🎯 When to Use Integration Tests

### ✅ Use Integration Tests For:
- **API endpoints** - Request/response contracts
- **Database operations** - Queries, transactions, migrations
- **External services** - Third-party APIs, payment gateways
- **Module boundaries** - How components interact
- **File system operations** - Reading/writing files
- **Message queues** - Pub/sub, event streaming
- **Configuration loading** - Environment-specific setup

### ❌ Don't Use Integration Tests For:
- **Business logic** - Use unit tests (faster)
- **Validation rules** - Unit tests suffice
- **Pure calculations** - No integration needed
- **Full user flows** - Use E2E tests
- **Every function** - Only integration points

**Rule of Thumb:** Integration tests verify the contract between components, not the logic within them.

---

## 🗄️ Database Integration Testing

### Setup Test Database

```typescript
// test/helpers/test-database.ts
import { Database } from './database'

export class TestDatabase {
  private db: Database

  async setup() {
    // Create test database
    this.db = await Database.connect({
      host: 'localhost',
      database: 'test_db',
      user: 'test_user'
    })

    // Run migrations
    await this.db.migrate.latest()
  }

  async cleanup() {
    // Clear all tables
    await this.db.raw('TRUNCATE TABLE users CASCADE')
    await this.db.raw('TRUNCATE TABLE orders CASCADE')
  }

  async teardown() {
    await this.db.destroy()
  }

  getDb() {
    return this.db
  }
}

// test/integration/user-repository.test.ts
describe('UserRepository Integration', () => {
  let testDb: TestDatabase

  beforeAll(async () => {
    testDb = new TestDatabase()
    await testDb.setup()
  })

  afterAll(async () => {
    await testDb.teardown()
  })

  beforeEach(async () => {
    await testDb.cleanup()
  })

  it('creates user and retrieves from database', async () => {
    const repo = new UserRepository(testDb.getDb())

    // Create user
    const user = await repo.create({
      email: 'test@example.com',
      name: 'Test User'
    })

    expect(user.id).toBeDefined()

    // Retrieve from database
    const retrieved = await repo.findById(user.id)

    expect(retrieved).toEqual(user)
  })

  it('handles unique constraint violations', async () => {
    const repo = new UserRepository(testDb.getDb())

    await repo.create({
      email: 'duplicate@example.com',
      name: 'First'
    })

    await expect(
      repo.create({
        email: 'duplicate@example.com',
        name: 'Second'
      })
    ).rejects.toThrow('Email already exists')
  })
})
```

---

## 🌐 API Endpoint Integration Testing

### Testing Express/Fastify Routes

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import request from 'supertest'
import { app } from '../src/app'
import { TestDatabase } from './helpers/test-database'

describe('POST /api/users (Integration)', () => {
  let testDb: TestDatabase

  beforeAll(async () => {
    testDb = new TestDatabase()
    await testDb.setup()
  })

  afterAll(async () => {
    await testDb.teardown()
  })

  beforeEach(async () => {
    await testDb.cleanup()
  })

  it('creates user and returns 201', async () => {
    const userData = {
      email: 'newuser@example.com',
      name: 'New User',
      password: 'SecurePass123!'
    }

    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(201)

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'newuser@example.com',
      name: 'New User'
    })

    expect(response.body.password).toBeUndefined()

    // Verify in database
    const user = await testDb.getDb()
      .table('users')
      .where({ email: 'newuser@example.com' })
      .first()

    expect(user).toBeDefined()
    expect(user.password_hash).toBeDefined()
  })

  it('returns 400 for invalid email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'invalid-email',
        name: 'Test',
        password: 'pass'
      })
      .expect(400)

    expect(response.body.error).toContain('Invalid email')
  })

  it('returns 409 for duplicate email', async () => {
    const userData = {
      email: 'duplicate@example.com',
      name: 'User',
      password: 'pass123'
    }

    // Create first user
    await request(app).post('/api/users').send(userData).expect(201)

    // Attempt duplicate
    const response = await request(app)
      .post('/api/users')
      .send(userData)
      .expect(409)

    expect(response.body.error).toContain('already exists')
  })
})
```

---

## 🔌 External Service Integration

### Testing Third-Party API Integration

```typescript
describe('PaymentService Integration', () => {
  // Use test API keys
  const testApiKey = process.env.STRIPE_TEST_KEY

  it('processes payment with Stripe', async () => {
    const paymentService = new PaymentService({ apiKey: testApiKey })

    const result = await paymentService.charge({
      amount: 1000, // $10.00
      currency: 'usd',
      source: 'tok_visa' // Stripe test token
    })

    expect(result.status).toBe('succeeded')
    expect(result.amount).toBe(1000)
    expect(result.id).toMatch(/^ch_/)
  })

  it('handles declined cards', async () => {
    const paymentService = new PaymentService({ apiKey: testApiKey })

    await expect(
      paymentService.charge({
        amount: 1000,
        source: 'tok_chargeDeclined' // Test token for declined
      })
    ).rejects.toThrow('Your card was declined')
  })
})
```

### Mocking External Services

```typescript
import nock from 'nock'

describe('WeatherService Integration', () => {
  afterEach(() => {
    nock.cleanAll()
  })

  it('fetches weather data from API', async () => {
    // Mock external API
    nock('https://api.weather.com')
      .get('/current')
      .query({ city: 'New York' })
      .reply(200, {
        temperature: 72,
        conditions: 'Sunny'
      })

    const service = new WeatherService()
    const weather = await service.getCurrent('New York')

    expect(weather).toEqual({
      temperature: 72,
      conditions: 'Sunny'
    })
  })

  it('handles API timeout', async () => {
    nock('https://api.weather.com')
      .get('/current')
      .delay(5000) // Delay 5 seconds
      .reply(200, {})

    const service = new WeatherService({ timeout: 1000 })

    await expect(service.getCurrent('New York'))
      .rejects.toThrow('Request timeout')
  })
})
```

---

## 📁 File System Integration

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mkdir, writeFile, rm } from 'fs/promises'
import { join } from 'path'
import { FileService } from '../src/file-service'

describe('FileService Integration', () => {
  const testDir = join(__dirname, 'test-files')

  beforeEach(async () => {
    await mkdir(testDir, { recursive: true })
  })

  afterEach(async () => {
    await rm(testDir, { recursive: true, force: true })
  })

  it('reads and parses JSON file', async () => {
    const testFile = join(testDir, 'data.json')
    await writeFile(testFile, JSON.stringify({ value: 42 }))

    const fileService = new FileService()
    const data = await fileService.readJSON(testFile)

    expect(data).toEqual({ value: 42 })
  })

  it('handles missing files', async () => {
    const fileService = new FileService()
    const nonExistent = join(testDir, 'missing.json')

    await expect(fileService.readJSON(nonExistent))
      .rejects.toThrow('File not found')
  })
})
```

---

## 🔄 Transaction Testing

```typescript
describe('OrderService Transaction Integration', () => {
  let testDb: TestDatabase

  beforeAll(async () => {
    testDb = new TestDatabase()
    await testDb.setup()
  })

  beforeEach(async () => {
    await testDb.cleanup()
  })

  it('rolls back transaction on error', async () => {
    const service = new OrderService(testDb.getDb())

    // Create scenario that will fail midway
    const mockPayment = vi.fn().mockRejectedValue(new Error('Payment failed'))

    try {
      await service.createOrderWithPayment(
        { items: [{ productId: '1', quantity: 2 }] },
        mockPayment
      )
    } catch (error) {
      // Expected to fail
    }

    // Verify rollback - no order in database
    const orders = await testDb.getDb().table('orders').select()
    expect(orders).toHaveLength(0)

    // Verify inventory not changed
    const product = await testDb.getDb().table('products').where({ id: '1' }).first()
    expect(product.stock).toBe(100) // Original stock
  })

  it('commits transaction on success', async () => {
    const service = new OrderService(testDb.getDb())

    const mockPayment = vi.fn().mockResolvedValue({ id: 'charge-123' })

    const order = await service.createOrderWithPayment(
      { items: [{ productId: '1', quantity: 2 }] },
      mockPayment
    )

    // Verify order persisted
    const savedOrder = await testDb.getDb().table('orders').where({ id: order.id }).first()
    expect(savedOrder).toBeDefined()

    // Verify inventory updated
    const product = await testDb.getDb().table('products').where({ id: '1' }).first()
    expect(product.stock).toBe(98) // Reduced by 2
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Use real database** for database tests
- **Use test containers** for isolation (Docker)
- **Clean up after tests** - No data pollution
- **Test integration points** - Module boundaries
- **Mock external services** - Unless testing integration
- **Test transactions** - Rollback behavior
- **Run in CI/CD** - Every commit

### ❌ Don't

- **Test business logic** - Use unit tests
- **Skip cleanup** - Causes test interference
- **Use production database** - Always test database
- **Test every combination** - Too slow
- **Ignore performance** - Integration tests should be < 1s
- **Run constantly** - Too slow for TDD

---

## 🔗 Related Patterns

- **[Testing Pyramid](../principles/testing-pyramid.md)** - Integration in middle (15-20%)
- **[API Testing](api-testing.md)** - HTTP integration
- **[E2E Testing](e2e-testing.md)** - Full stack integration
- **[Async Testing](async-testing.md)** - Handle async integrations

---

**Next Steps:**
- Setup [Testcontainers](https://testcontainers.com/) for database isolation
- Review [Supertest](https://github.com/visionmedia/supertest) for HTTP testing
- Explore [Nock](https://github.com/nock/nock) for HTTP mocking
