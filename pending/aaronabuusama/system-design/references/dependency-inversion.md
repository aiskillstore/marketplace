# Dependency Inversion Principle

## The Principle

> A. High-level modules should not depend on low-level modules. Both should depend on abstractions.
> B. Abstractions should not depend on details. Details should depend on abstractions.

## Without Dependency Inversion

```typescript
// High-level module depends on low-level module
class OrderService {
  private repository = new PostgresOrderRepository(); // Direct dependency!

  async placeOrder(command: PlaceOrderCommand): Promise<void> {
    const order = Order.create(command);
    await this.repository.save(order); // Coupled to Postgres
  }
}
```

Problems:
- Can't test without a database
- Can't switch databases
- OrderService must change if PostgresOrderRepository changes

## With Dependency Inversion

```typescript
// 1. Define abstraction (port)
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}

// 2. High-level module depends on abstraction
class OrderService {
  constructor(private repository: OrderRepository) {} // Depends on interface

  async placeOrder(command: PlaceOrderCommand): Promise<void> {
    const order = Order.create(command);
    await this.repository.save(order); // Works with any implementation
  }
}

// 3. Low-level module implements abstraction
class PostgresOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    // Postgres-specific implementation
  }
}

// 4. Composition root wires them together
const repository = new PostgresOrderRepository();
const service = new OrderService(repository);
```

## The Inversion

**Traditional:**
```
OrderService → PostgresOrderRepository
(high-level)     (low-level)
```

**Inverted:**
```
OrderService → OrderRepository ← PostgresOrderRepository
(high-level)   (abstraction)     (low-level)
```

The dependency arrow is **inverted** - low-level now depends on high-level's abstraction.

## Implementation Techniques

### 1. Constructor Injection

```typescript
class OrderService {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly paymentGateway: PaymentGateway,
    private readonly eventPublisher: EventPublisher
  ) {}
}
```

**Pros:** Dependencies visible, immutable, easy to test
**Cons:** Can lead to large constructors

### 2. Interface Segregation

Split large interfaces into focused ones:

```typescript
// Instead of one large interface
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
  findByDateRange(start: Date, end: Date): Promise<Order[]>;
  generateReport(): Promise<ReportData>;
}

// Split into focused interfaces
interface OrderWriter {
  save(order: Order): Promise<void>;
}

interface OrderReader {
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
}

interface OrderReporter {
  findByDateRange(start: Date, end: Date): Promise<Order[]>;
  generateReport(): Promise<ReportData>;
}
```

### 3. Factory Pattern

When you need to create dependencies at runtime:

```typescript
interface OrderFactory {
  create(command: CreateOrderCommand): Order;
}

class OrderService {
  constructor(
    private orderFactory: OrderFactory,
    private orderRepository: OrderRepository
  ) {}

  async placeOrder(command: CreateOrderCommand): Promise<OrderId> {
    const order = this.orderFactory.create(command);
    await this.orderRepository.save(order);
    return order.id;
  }
}
```

## Testing Benefits

```typescript
// Test with fake implementation
class FakeOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();
  public saveCalled = false;

  async save(order: Order): Promise<void> {
    this.saveCalled = true;
    this.orders.set(order.id.value, order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    return this.orders.get(id.value) ?? null;
  }
}

// Test
test('placeOrder saves order', async () => {
  const fakeRepo = new FakeOrderRepository();
  const service = new OrderService(fakeRepo);

  await service.placeOrder(createTestCommand());

  expect(fakeRepo.saveCalled).toBe(true);
});
```

## Abstraction Ownership

**Who owns the interface?**

The **consumer** (high-level module) owns the abstraction, not the implementer.

```
┌─────────────────────────────────────┐
│      Application Layer              │
│  ┌───────────────────────────────┐  │
│  │   OrderService                │  │
│  │        │                      │  │
│  │        ▼                      │  │
│  │   OrderRepository (interface) │  │ ◄── Interface defined HERE
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
                    ▲
                    │ implements
┌─────────────────────────────────────┐
│      Infrastructure Layer           │
│  ┌───────────────────────────────┐  │
│  │   PostgresOrderRepository     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## When NOT to Invert

Not every dependency needs inversion:

- **Stable dependencies** - Standard library, well-established utilities
- **Value objects** - Immutable data structures
- **Pure functions** - No side effects

Focus inversion on:
- I/O operations (database, network, file system)
- External services
- Anything that makes testing hard

## Common Mistakes

### 1. Interface Mimics Implementation

```typescript
// Bad - interface mirrors Postgres concepts
interface OrderRepository {
  executeQuery(sql: string): Promise<any>;
  beginTransaction(): Promise<void>;
}

// Good - interface reflects domain needs
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}
```

### 2. Leaky Abstraction

```typescript
// Bad - PostgresError leaks through
interface OrderRepository {
  save(order: Order): Promise<void>; // throws PostgresError
}

// Good - domain-specific error
interface OrderRepository {
  save(order: Order): Promise<void>; // throws OrderPersistenceError
}
```

### 3. Interface Per Implementation

```typescript
// Bad - defeats the purpose
interface PostgresOrderRepository { ... }
interface MongoOrderRepository { ... }

// Good - one interface, multiple implementations
interface OrderRepository { ... }
class PostgresOrderRepository implements OrderRepository { ... }
class MongoOrderRepository implements OrderRepository { ... }
```

## Key Insight

> The abstraction should be designed from the perspective of the consumer (high-level module), not the provider (low-level module).
