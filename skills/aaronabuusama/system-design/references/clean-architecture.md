# Clean Architecture

## Core Principle

**The Dependency Rule:** Source code dependencies must point only inward, toward higher-level policies.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frameworks & Drivers                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Interface Adapters                 │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │              Application Business Rules      │    │    │
│  │  │  ┌─────────────────────────────────────┐    │    │    │
│  │  │  │       Enterprise Business Rules      │    │    │    │
│  │  │  │            (Entities)                │    │    │    │
│  │  │  └─────────────────────────────────────┘    │    │    │
│  │  │                (Use Cases)                   │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │          (Controllers, Gateways, Presenters)         │    │
│  └─────────────────────────────────────────────────────┘    │
│                  (Web, DB, Devices, UI, External)            │
└─────────────────────────────────────────────────────────────┘
```

## The Four Layers

### 1. Entities (Enterprise Business Rules)

The innermost circle. Contains:
- Business objects with critical business rules
- Could be used by many applications in the enterprise
- Least likely to change when something external changes

```typescript
// Entity example
class Order {
  private readonly items: OrderItem[];
  private status: OrderStatus;

  // Business rule: orders can only be cancelled if not shipped
  cancel(): void {
    if (this.status === OrderStatus.Shipped) {
      throw new OrderCannotBeCancelledError();
    }
    this.status = OrderStatus.Cancelled;
  }

  // Business rule: total includes tax
  get total(): Money {
    return this.items
      .reduce((sum, item) => sum.add(item.subtotal), Money.zero())
      .withTax(this.taxRate);
  }
}
```

### 2. Use Cases (Application Business Rules)

Contains application-specific business rules:
- Orchestrate flow of data to/from entities
- Direct entities to use their business rules
- Encapsulate all use cases of the system

```typescript
// Use case example
class PlaceOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private inventoryService: InventoryService,
    private paymentGateway: PaymentGateway
  ) {}

  async execute(command: PlaceOrderCommand): Promise<PlaceOrderResult> {
    // 1. Validate inventory
    await this.inventoryService.reserve(command.items);

    // 2. Process payment
    const payment = await this.paymentGateway.charge(command.payment);

    // 3. Create order (entity does validation)
    const order = Order.create(command.items, payment);

    // 4. Persist
    await this.orderRepository.save(order);

    return { orderId: order.id };
  }
}
```

### 3. Interface Adapters

Convert data between use cases/entities and external formats:
- Controllers (handle incoming requests)
- Presenters (format outgoing responses)
- Gateways (abstract external services)

```typescript
// Controller example
class OrderController {
  constructor(private placeOrder: PlaceOrderUseCase) {}

  async handlePost(req: Request): Promise<Response> {
    // Convert HTTP request to use case command
    const command = this.parseRequest(req);

    // Execute use case
    const result = await this.placeOrder.execute(command);

    // Convert result to HTTP response
    return this.formatResponse(result);
  }
}
```

### 4. Frameworks & Drivers

The outermost layer:
- Database implementations
- Web frameworks
- UI frameworks
- External services

**Key insight:** This layer is where all the details go. The web is a detail. The database is a detail.

## Crossing Boundaries

Data crosses boundaries via simple data structures:
- DTOs (Data Transfer Objects)
- Request/Response models

**Never pass entity objects across boundaries.** Convert to DTOs.

```typescript
// Crossing boundary example
interface OrderDTO {
  id: string;
  items: ItemDTO[];
  total: number;
  status: string;
}

class OrderPresenter {
  present(order: Order): OrderDTO {
    return {
      id: order.id.value,
      items: order.items.map(this.presentItem),
      total: order.total.amount,
      status: order.status.toString()
    };
  }
}
```

## What Belongs Where

| Layer | Contains | Depends On |
|-------|----------|------------|
| Entities | Domain models, business rules | Nothing |
| Use Cases | Application workflows, orchestration | Entities |
| Adapters | Controllers, repositories, gateways | Use Cases, Entities |
| Frameworks | Implementations, configuration | All inner layers |

## Testing Benefits

Clean Architecture makes testing straightforward:

| Layer | Test Type | Mocking |
|-------|-----------|---------|
| Entities | Unit | None needed |
| Use Cases | Unit | Mock ports |
| Adapters | Integration | Mock external services |
| Frameworks | E2E | Full system |

## Common Violations

1. **Entity depends on framework**
   - Bad: Entity uses ORM decorators
   - Good: Entity is pure, repository handles mapping

2. **Use case knows about HTTP**
   - Bad: Use case returns Response object
   - Good: Use case returns domain result, controller formats

3. **Business logic in controller**
   - Bad: Controller has if/else business rules
   - Good: Controller delegates to use case

4. **Database leaking into domain**
   - Bad: Entity has `@Column()` decorator
   - Good: Entity is pure, mapper handles DB

## Key Insight

> "The center of your application is not the database. Nor is it one or more of the frameworks you may be using. The center of your application is the use cases of your application."
> — Robert C. Martin
