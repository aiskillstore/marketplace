# Clean Architecture (Layered & Onion Architecture)

## What is Clean Architecture?

Clean Architecture, popularized by Robert C. Martin, organizes code into concentric layers with strict separation of concerns. The rule is that **inner layers know nothing of outer layers** (dependency inversion principle). This pattern is excellent for AI-generated code because it provides a clear recipe for structuring any feature.

## Core Principles

### 1. Dependency Inversion

Inner layers (domain) never depend on outer layers (infrastructure). Dependencies always point inward.

```
┌─────────────────────────────────────────────┐
│  Interfaces & Controllers (outermost)       │
├─────────────────────────────────────────────┤
│  Interface Adapters (Presenters, Gateways)  │
├─────────────────────────────────────────────┤
│  Application Services & Use Cases           │
├─────────────────────────────────────────────┤
│  Domain Entities & Business Rules (core)    │
└─────────────────────────────────────────────┘
     ↑ Dependencies flow inward only ↑
```

### 2. Each Layer Has One Responsibility

- **Domain Layer**: Pure business rules (no external dependencies)
- **Application Layer**: Use cases and orchestration
- **Interface Adapters**: Controllers, presenters, gateways
- **Infrastructure Layer**: Database, web frameworks, external APIs

### 3. Testability

Each layer can be tested independently by replacing outer dependencies with test doubles.

### 4. Flexibility

You can swap infrastructure implementations (swap PostgreSQL for MongoDB) without touching domain logic.

## Why Clean Architecture Helps AI Agents

This pattern is excellent for AI-generated code because it provides a **clear recipe for structuring any feature**. Each piece of logic has a designated place:

- "Business validation goes in the domain or use-case layer, not in the controller"
- "Database access only occurs in repository implementations in the infrastructure layer"
- "Controllers convert HTTP requests to use-case calls"

Engineers using AI have found that Clean/Onion architecture gave a "solid foundation that AI could easily understand and maintain," thanks to its clear separation and dependency rules. The AI doesn't have to guess where code should go; the project structure itself guides it.

### How Clean Architecture Improves AI Output

When an AI is instructed to follow Clean Architecture, the likelihood of correct output increases because the generation task is broken down. You can prompt the AI to implement one layer at a time:

- "Write the domain service for X"
- "Implement the repository adapter for Y"
- "Create the controller that uses this use case"

And it will adhere to the boundaries. This compartmentalization means **fewer errors in integrating pieces**, since each piece conforms to a known interface or contract.

## The Four Layers

### Layer 1: Domain Layer (Core)

Plain TypeScript classes with business logic and definitions. No external dependencies.

```typescript
/**
 * Domain Entity
 * Encapsulates business logic and rules
 */
class Order {
  private _id: string;
  private _items: OrderItem[] = [];
  private _status: OrderStatus;
  private _customerId: string;

  constructor(customerId: string) {
    this._id = generateId();
    this._customerId = customerId;
    this._status = OrderStatus.PENDING;
  }

  /**
   * Business rule: add line item with validation
   */
  addLineItem(productId: string, quantity: number, price: Money): void {
    if (quantity <= 0) {
      throw new Error('Quantity must be positive');
    }

    if (this._status !== OrderStatus.PENDING) {
      throw new Error('Cannot add items to a confirmed order');
    }

    const item = new OrderItem(productId, quantity, price);
    this._items.push(item);
  }

  /**
   * Business rule: calculate total
   */
  calculateTotal(): Money {
    return this._items.reduce(
      (total, item) => total.add(item.getSubtotal()),
      Money.zero()
    );
  }

  confirm(): void {
    if (this._items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this._status = OrderStatus.CONFIRMED;
  }

  get id(): string {
    return this._id;
  }

  get status(): OrderStatus {
    return this._status;
  }

  get items(): OrderItem[] {
    return [...this._items]; // defensive copy
  }
}
```

### Layer 2: Application Layer

Use cases that orchestrate domain operations. Define ports (interfaces) for external interactions.

```typescript
/**
 * Repository Port (interface)
 * Defined in application layer, implemented in infrastructure
 */
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}

/**
 * Use Case Service
 * Orchestrates domain objects to fulfill business requirement
 */
class ConfirmOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private paymentService: PaymentServicePort,
    private notificationService: NotificationServicePort
  ) {}

  async execute(orderId: string, paymentInfo: PaymentInfo): Promise<OrderDTO> {
    // Retrieve aggregate
    const order = await this.orderRepository.findById(orderId);
    if (!order) {
      throw new OrderNotFoundError(orderId);
    }

    // Apply business rule
    order.confirm();

    // Delegate to external services via ports
    const paymentResult = await this.paymentService.processPayment(
      paymentInfo,
      order.calculateTotal()
    );

    if (!paymentResult.success) {
      throw new PaymentFailedError(paymentResult.reason);
    }

    // Persist
    await this.orderRepository.save(order);

    // Notify
    await this.notificationService.sendConfirmation(order);

    // Return DTO (not domain object)
    return new OrderDTO(order);
  }
}
```

### Layer 3: Interface Adapters

Controllers and presenters that translate between external world and use cases.

```typescript
/**
 * Controller
 * Converts HTTP request to use case input
 * Converts use case output to HTTP response
 */
class OrderController {
  constructor(private confirmOrderUseCase: ConfirmOrderUseCase) {}

  async confirmOrder(
    req: Request,
    res: Response
  ): Promise<void> {
    try {
      const { orderId } = req.params;
      const { cardToken, expiryDate } = req.body;

      // Validate input
      if (!orderId || !cardToken) {
        res.status(400).json({
          error: 'Missing required fields: orderId, cardToken'
        });
        return;
      }

      // Create DTO for use case
      const paymentInfo = new PaymentInfo(cardToken, expiryDate);

      // Execute use case
      const orderDTO = await this.confirmOrderUseCase.execute(
        orderId,
        paymentInfo
      );

      // Return response
      res.status(200).json(orderDTO);
    } catch (error) {
      this.handleError(error, res);
    }
  }

  private handleError(error: Error, res: Response): void {
    if (error instanceof OrderNotFoundError) {
      res.status(404).json({ error: 'Order not found' });
    } else if (error instanceof PaymentFailedError) {
      res.status(402).json({ error: 'Payment failed' });
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}
```

### Layer 4: Infrastructure Layer

Database implementations, HTTP clients, external service integrations.

```typescript
/**
 * Repository Implementation
 * Implements the port defined in application layer
 */
class MongoOrderRepository implements OrderRepository {
  constructor(private db: MongoClient) {}

  async save(order: Order): Promise<void> {
    const document = {
      _id: order.id,
      customerId: order.customerId,
      status: order.status,
      items: order.items.map(item => ({
        productId: item.productId,
        quantity: item.quantity,
        price: item.price.value
      })),
      total: order.calculateTotal().value,
      createdAt: new Date()
    };

    await this.db.collection('orders').insertOne(document);
  }

  async findById(id: string): Promise<Order | null> {
    const document = await this.db.collection('orders').findOne({ _id: id });

    if (!document) {
      return null;
    }

    // Reconstruct domain object from persistence
    const order = new Order(document.customerId);
    document.items.forEach(item => {
      order.addLineItem(
        item.productId,
        item.quantity,
        Money.fromValue(item.price)
      );
    });

    return order;
  }
}

/**
 * Payment Service Adapter
 * Implements payment port using external API
 */
class StripePaymentAdapter implements PaymentServicePort {
  constructor(private stripeClient: StripeClient) {}

  async processPayment(
    paymentInfo: PaymentInfo,
    amount: Money
  ): Promise<PaymentResult> {
    try {
      const charge = await this.stripeClient.charges.create({
        amount: amount.cents(),
        currency: 'usd',
        source: paymentInfo.cardToken
      });

      return {
        success: true,
        transactionId: charge.id
      };
    } catch (error) {
      return {
        success: false,
        reason: error.message
      };
    }
  }
}
```

## File Structure for Clean Architecture

```
src/
├── domain/
│   ├── entities/
│   │   ├── Order.ts
│   │   ├── OrderItem.ts
│   │   └── Customer.ts
│   ├── value-objects/
│   │   ├── Money.ts
│   │   └── OrderStatus.ts
│   ├── services/
│   │   └── OrderCalculationService.ts
│   └── errors/
│       ├── DomainError.ts
│       └── ValidationError.ts
├── application/
│   ├── use-cases/
│   │   ├── ConfirmOrderUseCase.ts
│   │   ├── CancelOrderUseCase.ts
│   │   └── GetOrderDetailsUseCase.ts
│   ├── ports/
│   │   ├── OrderRepository.ts
│   │   ├── PaymentServicePort.ts
│   │   └── NotificationServicePort.ts
│   ├── dto/
│   │   ├── OrderDTO.ts
│   │   └── PaymentInfo.ts
│   └── errors/
│       ├── ApplicationError.ts
│       ├── OrderNotFoundError.ts
│       └── PaymentFailedError.ts
├── interfaces/
│   ├── http/
│   │   ├── OrderController.ts
│   │   ├── routes.ts
│   │   └── middleware/
│   │       └── errorHandler.ts
│   └── cli/
│       └── OrderCLI.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── MongoOrderRepository.ts
│   │   └── PostgresOrderRepository.ts
│   ├── adapters/
│   │   ├── StripePaymentAdapter.ts
│   │   ├── SendGridNotificationAdapter.ts
│   │   └── TwilioSmsAdapter.ts
│   ├── database/
│   │   ├── mongoClient.ts
│   │   └── migrations/
│   └── config/
│       └── dependencies.ts
└── main.ts
```

## Dependency Injection Setup

```typescript
/**
 * Wire up dependencies
 * Typically done in a composition root at application startup
 */
class ApplicationContainer {
  private mongoClient: MongoClient;
  private orderRepository: OrderRepository;
  private paymentService: PaymentServicePort;
  private notificationService: NotificationServicePort;

  constructor(config: AppConfig) {
    // Infrastructure
    this.mongoClient = new MongoClient(config.mongoUrl);
    this.paymentService = new StripePaymentAdapter(
      new StripeClient(config.stripeKey)
    );
    this.notificationService = new SendGridAdapter(
      new SendGridClient(config.sendGridKey)
    );

    // Repositories
    this.orderRepository = new MongoOrderRepository(this.mongoClient);
  }

  // Factory methods for use cases
  getConfirmOrderUseCase(): ConfirmOrderUseCase {
    return new ConfirmOrderUseCase(
      this.orderRepository,
      this.paymentService,
      this.notificationService
    );
  }

  getOrderController(): OrderController {
    return new OrderController(this.getConfirmOrderUseCase());
  }
}
```

## Clean Architecture vs. Simpler Approaches

### ❌ Problematic: Mixed Concerns

```typescript
// Everything in one file - hard to test, extend, or maintain
app.post('/order/confirm', async (req, res) => {
  try {
    const order = await db.query(
      'SELECT * FROM orders WHERE id = ?',
      [req.params.orderId]
    );

    // Validation mixed with database calls
    if (!order || order.rows.length === 0) {
      return res.status(404).json({ error: 'Not found' });
    }

    // Business logic mixed with HTTP and external calls
    const total = order.rows[0].items.reduce((sum, item) => sum + item.price, 0);
    const chargeResult = await stripe.charges.create({
      amount: total * 100,
      currency: 'usd',
      source: req.body.cardToken
    });

    // Updates without validation
    await db.query('UPDATE orders SET status = ? WHERE id = ?', [
      'CONFIRMED',
      order.rows[0].id
    ]);

    // Notification mixed in
    await sendgrid.send({
      to: order.rows[0].customer_email,
      subject: 'Order confirmed'
    });

    res.json(order.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
```

### ✅ Clean: Separated Concerns

```typescript
// Domain: Pure business logic
class Order {
  confirm(): void {
    if (this._items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this._status = OrderStatus.CONFIRMED;
  }
}

// Application: Orchestration
class ConfirmOrderUseCase {
  async execute(orderId: string, paymentInfo: PaymentInfo): Promise<void> {
    const order = await this.orderRepository.findById(orderId);
    order.confirm(); // Business rule
    await this.paymentService.process(paymentInfo, order.total);
    await this.orderRepository.save(order);
  }
}

// Interface: HTTP conversion
class OrderController {
  async confirmOrder(req: Request, res: Response): Promise<void> {
    const result = await this.confirmOrderUseCase.execute(
      req.params.orderId,
      req.body.paymentInfo
    );
    res.json(result);
  }
}
```

## Tips for AI-Generated Clean Architecture Code

1. **Implement one layer at a time** - Ask the AI to create domain entities first, then use cases, then adapters
2. **Start with interfaces** - Define repository and service ports before implementing them
3. **Use dependency injection** - Show the AI an example of how dependencies are wired
4. **Reference existing patterns** - Point to similar use cases or repositories as examples
5. **Test each layer independently** - Request unit tests that mock external dependencies

## Common Mistakes to Avoid

### Mistake: Business Logic in Controllers

```typescript
// ❌ Wrong
app.post('/order/confirm', async (req, res) => {
  if (req.body.total <= 0) { // Business logic in controller!
    res.status(400).send('Invalid total');
  }
  // ...
});

// ✅ Right
// Business logic in domain or use case
class Order {
  confirm(): void {
    if (this._total.value <= 0) {
      throw new ValidationError('Invalid total');
    }
    // ...
  }
}
```

### Mistake: Domain Depending on Infrastructure

```typescript
// ❌ Wrong
class Order {
  async save(): Promise<void> {
    // Domain shouldn't know about database!
    await db.collection('orders').insertOne(this.toJSON());
  }
}

// ✅ Right
// Domain is pure, repository handles persistence
class Order {
  // Domain has no side effects
  confirm(): void {
    this._status = OrderStatus.CONFIRMED;
  }
}

// Infrastructure handles persistence
class MongoOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    await this.db.collection('orders').insertOne(order.toJSON());
  }
}
```

### Mistake: Using Domain Objects as DTOs

```typescript
// ❌ Wrong - exposes domain details
app.get('/order/:id', async (req, res) => {
  const order = await orderRepository.findById(req.params.id);
  res.json(order); // Exposes internal state
});

// ✅ Right - use DTOs
app.get('/order/:id', async (req, res) => {
  const order = await orderRepository.findById(req.params.id);
  res.json(new OrderDTO(order)); // Only expose what clients need
});
```

## Key Takeaways

- **Clear layers** make it obvious where code should go
- **Dependency inversion** keeps domain pure and testable
- **Ports** provide clear contracts between layers
- **One layer at a time** AI implementation reduces errors
- **Flexibility** to swap implementations without touching domain
- **Testability** improves because each layer can be tested independently
