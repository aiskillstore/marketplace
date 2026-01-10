# Hexagonal Architecture (Ports & Adapters)

## Origin

Created by Alistair Cockburn. Also known as:
- Ports & Adapters
- Onion Architecture (similar concept)

## Core Concept

**Allow an application to be equally driven by users, programs, automated tests, or batch scripts, and to be developed and tested in isolation from its eventual runtime devices and databases.**

## The Hexagon

```
                         HTTP API
                            │
                    ┌───────▼───────┐
                    │   Controller  │ ◄── Driving Adapter
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  Inbound Port │ ◄── Interface
                    └───────┬───────┘
                            │
            ┌───────────────▼───────────────┐
            │                               │
            │        APPLICATION CORE       │
            │                               │
            │   ┌───────────────────────┐   │
            │   │      Use Cases        │   │
            │   └───────────────────────┘   │
            │   ┌───────────────────────┐   │
            │   │    Domain Model       │   │
            │   └───────────────────────┘   │
            │                               │
            └───────────────┬───────────────┘
                            │
                    ┌───────▼───────┐
                    │ Outbound Port │ ◄── Interface
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  Repository   │ ◄── Driven Adapter
                    └───────┬───────┘
                            │
                        Database
```

## Ports

**Ports are interfaces** that define how the application interacts with the outside world.

### Inbound Ports (Primary/Driving)

Define what the application **offers** to the outside world.

```typescript
// Inbound port - what the application can do
interface OrderService {
  placeOrder(command: PlaceOrderCommand): Promise<OrderId>;
  cancelOrder(orderId: OrderId): Promise<void>;
  getOrderStatus(orderId: OrderId): Promise<OrderStatus>;
}
```

### Outbound Ports (Secondary/Driven)

Define what the application **needs** from the outside world.

```typescript
// Outbound port - what the application needs
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
}

interface PaymentGateway {
  charge(amount: Money, method: PaymentMethod): Promise<PaymentResult>;
  refund(paymentId: PaymentId): Promise<RefundResult>;
}
```

## Adapters

**Adapters are implementations** that connect ports to the outside world.

### Driving Adapters (Primary)

**Use** the application through inbound ports.

```typescript
// REST adapter driving the application
class OrderController {
  constructor(private orderService: OrderService) {}

  async createOrder(req: Request): Promise<Response> {
    const command = this.parseCommand(req.body);
    const orderId = await this.orderService.placeOrder(command);
    return Response.json({ orderId: orderId.value });
  }
}

// CLI adapter driving the same application
class OrderCLI {
  constructor(private orderService: OrderService) {}

  async placeOrder(args: string[]): Promise<void> {
    const command = this.parseArgs(args);
    const orderId = await this.orderService.placeOrder(command);
    console.log(`Order created: ${orderId.value}`);
  }
}
```

### Driven Adapters (Secondary)

**Implement** outbound ports for specific technologies.

```typescript
// Postgres adapter implementing the port
class PostgresOrderRepository implements OrderRepository {
  constructor(private db: Database) {}

  async save(order: Order): Promise<void> {
    await this.db.query(
      'INSERT INTO orders (id, customer_id, status) VALUES ($1, $2, $3)',
      [order.id.value, order.customerId.value, order.status]
    );
  }

  async findById(id: OrderId): Promise<Order | null> {
    const row = await this.db.queryOne(
      'SELECT * FROM orders WHERE id = $1',
      [id.value]
    );
    return row ? this.mapToDomain(row) : null;
  }
}

// In-memory adapter for testing
class InMemoryOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.orders.set(order.id.value, order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    return this.orders.get(id.value) ?? null;
  }
}
```

## Dependency Direction

```
Driving Adapters → Inbound Ports ← Application Core → Outbound Ports ← Driven Adapters
       │                                                      │
       └──────────────── Dependencies point INWARD ───────────┘
```

- Adapters depend on ports (interfaces)
- Application core defines ports
- Application core never depends on adapters

## The Power of Ports

Because the core depends only on interfaces:

1. **Testability** - Use in-memory adapters in tests
2. **Swappability** - Change databases without touching core
3. **Parallel development** - Teams work on adapters independently
4. **Technology independence** - Core logic survives tech changes

## Composing the Application

Wire adapters to ports at application startup:

```typescript
// Composition root - where everything is wired
function createApplication() {
  // Create driven adapters (what app needs)
  const orderRepository = new PostgresOrderRepository(db);
  const paymentGateway = new StripePaymentAdapter(stripeClient);

  // Create application core (use cases)
  const orderService = new OrderServiceImpl(
    orderRepository,
    paymentGateway
  );

  // Create driving adapters (how app is used)
  const orderController = new OrderController(orderService);
  const orderCLI = new OrderCLI(orderService);

  return { orderController, orderCLI };
}
```

## Port Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Inbound Port | Describes capability | `OrderService`, `UserAuthenticator` |
| Outbound Port | Describes need | `OrderRepository`, `EmailSender`, `PaymentGateway` |
| Driving Adapter | Technology + function | `RestOrderController`, `GraphQLOrderResolver` |
| Driven Adapter | Technology + port | `PostgresOrderRepository`, `StripePaymentGateway` |

## Common Mistakes

1. **Ports that leak technology**
   - Bad: `interface SqlOrderRepository`
   - Good: `interface OrderRepository`

2. **Adapters with business logic**
   - Bad: Validation rules in controller
   - Good: Validation in domain or use case

3. **Application depending on adapter**
   - Bad: Use case imports `PostgresOrderRepository`
   - Good: Use case imports `OrderRepository` interface

4. **Missing ports**
   - Bad: Use case directly calls `fetch()` for external API
   - Good: Use case calls `ExternalServicePort`
