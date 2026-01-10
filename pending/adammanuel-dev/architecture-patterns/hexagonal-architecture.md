# Hexagonal Architecture (Ports & Adapters)

## What is Hexagonal Architecture?

Hexagonal Architecture, also known as **Ports and Adapters**, is closely related to Clean Architecture but emphasizes isolating external integrations. In Hexagonal design, your **core business logic defines Port interfaces** for any outside interaction (database, web services, message queues), and **Adapter classes implement those interfaces** to handle the external communication.

The core (inside the hexagon) doesn't depend on any external tech details—it only knows the ports.

```
         ┌─────────────────────────────┐
         │   Web Controller Adapter    │
         └──────────────┬──────────────┘
                        │
         ┌──────────────▼──────────────┐
         │  HTTP Port (Input)          │
         └──────────────┬──────────────┘
                        │
    ┌───────────────────┼────────────────────┐
    │                   │                    │
    │  ┌────────────────▼─────────────────┐  │
    │  │                                  │  │
    │  │      CORE BUSINESS LOGIC         │  │
    │  │                                  │  │
    │  └────────────────▲─────────────────┘  │
    │                   │                    │
    └───────────────────┼────────────────────┘
                        │
     ┌──────────────────┴──────────────────┐
     │                                     │
  ┌──▼──────────────┐           ┌──────────▼──┐
  │ Database Port   │           │ API Port    │
  └──┬──────────────┘           └──────┬──────┘
     │                                 │
  ┌──▼──────────────┐           ┌──────▼──────┐
  │ MongoDB Adapter │           │ REST Adapter│
  └─────────────────┘           └─────────────┘
```

## Why Hexagonal is AI-Friendly

This pattern provides a **very clear blueprint** for the AI whenever some external interaction is needed. Instead of letting the AI scatter API calls or SQL queries wherever, you can explicitly prompt:

- "Define a port interface for X"
- "Implement an adapter for X that uses technology Y"

AI coding agents can follow this pattern well, producing code that is easier to swap out or fix later. It also aligns with how AI "thinks" in terms of completing patterns—if the AI sees that every database access goes via a `SomethingRepository` interface, it will likely continue that pattern consistently.

**Hexagonal Architecture thus reduces the cognitive load on the AI** by standardizing how to extend the system. As developers note, Hexagonal and DDD together yield "clear patterns, separation of concerns, rich domain models," making the codebase highly maintainable and adaptable—properties beneficial not only for humans but for AI generating code as well.

## Core Concepts

### 1. The Hexagon (Core)

The core contains pure business logic with no knowledge of external systems. It's where all the important domain rules live.

```typescript
/**
 * Core business logic
 * No external dependencies
 */
class UserAccount {
  private _id: string;
  private _email: Email;
  private _balance: Money;
  private _status: AccountStatus;

  constructor(email: Email) {
    this._id = generateId();
    this._email = email;
    this._balance = Money.zero();
    this._status = AccountStatus.ACTIVE;
  }

  deposit(amount: Money): void {
    if (amount.isNegative()) {
      throw new Error('Cannot deposit negative amount');
    }
    this._balance = this._balance.add(amount);
  }

  withdraw(amount: Money): void {
    if (amount.isGreaterThan(this._balance)) {
      throw new Error('Insufficient funds');
    }
    this._balance = this._balance.subtract(amount);
  }

  // Pure business logic - no I/O
  getAvailableBalance(): Money {
    return this._balance;
  }

  get id(): string {
    return this._id;
  }

  get email(): Email {
    return this._email;
  }
}
```

### 2. Ports (Interfaces)

Ports define contracts for external interactions. They're part of the core, but implementation lives outside.

```typescript
/**
 * Port: defines what the core needs from persistence
 * Lives in domain layer, but no implementation details
 */
interface AccountRepository {
  findById(id: string): Promise<UserAccount | null>;
  save(account: UserAccount): Promise<void>;
  delete(id: string): Promise<void>;
}

/**
 * Port: defines what the core needs from external API
 */
interface NotificationPort {
  sendEmail(to: string, subject: string, body: string): Promise<void>;
}

/**
 * Port: defines what the core needs from an external payment processor
 */
interface PaymentGatewayPort {
  processPayment(amount: Money, accountId: string): Promise<PaymentResult>;
}
```

### 3. Adapters (Implementations)

Adapters implement ports and handle the messy details of external systems.

```typescript
/**
 * Adapter: Implements repository port using MongoDB
 */
class MongoAccountRepository implements AccountRepository {
  constructor(private mongoClient: MongoClient) {}

  async findById(id: string): Promise<UserAccount | null> {
    const doc = await this.mongoClient.collection('accounts').findOne({ _id: id });

    if (!doc) {
      return null;
    }

    // Reconstruct core domain object
    const account = new UserAccount(new Email(doc.email));
    doc.balance && account.deposit(Money.fromCents(doc.balance));
    return account;
  }

  async save(account: UserAccount): Promise<void> {
    const document = {
      _id: account.id,
      email: account.email.value,
      balance: account.getAvailableBalance().cents(),
      savedAt: new Date()
    };

    await this.mongoClient.collection('accounts').updateOne(
      { _id: account.id },
      { $set: document },
      { upsert: true }
    );
  }

  async delete(id: string): Promise<void> {
    await this.mongoClient.collection('accounts').deleteOne({ _id: id });
  }
}

/**
 * Adapter: Implements notification port using SendGrid
 */
class SendGridNotificationAdapter implements NotificationPort {
  constructor(private sendgridClient: SendGridClient) {}

  async sendEmail(to: string, subject: string, body: string): Promise<void> {
    const message = {
      to,
      from: 'noreply@company.com',
      subject,
      text: body
    };

    await this.sendgridClient.send(message);
  }
}

/**
 * Adapter: Implements payment gateway port using Stripe
 */
class StripePaymentAdapter implements PaymentGatewayPort {
  constructor(private stripeClient: StripeClient) {}

  async processPayment(amount: Money, accountId: string): Promise<PaymentResult> {
    try {
      const charge = await this.stripeClient.charges.create({
        amount: amount.cents(),
        currency: 'usd',
        idempotencyKey: accountId // Prevent duplicate charges
      });

      return {
        success: true,
        transactionId: charge.id,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        timestamp: new Date()
      };
    }
  }
}
```

## Application Layer: Use Cases with Ports

```typescript
/**
 * Use case: Deposit money into account
 * Uses ports (no knowledge of specific implementations)
 */
class DepositMoneyUseCase {
  constructor(
    private accountRepository: AccountRepository,
    private notificationPort: NotificationPort
  ) {}

  async execute(accountId: string, amount: Money): Promise<AccountDTO> {
    // Get account from repository (abstracted)
    const account = await this.accountRepository.findById(accountId);
    if (!account) {
      throw new AccountNotFoundError(accountId);
    }

    // Apply business rule
    account.deposit(amount);

    // Persist (abstracted - could be MongoDB, PostgreSQL, etc.)
    await this.accountRepository.save(account);

    // Notify (abstracted - could be email, SMS, etc.)
    await this.notificationPort.sendEmail(
      account.email.value,
      'Deposit Received',
      `Your deposit of $${amount.dollars()} has been processed.`
    );

    return new AccountDTO(account);
  }
}
```

## Real-World Example: Order Processing

### Define Ports

```typescript
interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

interface ShippingServicePort {
  calculateShippingCost(destination: Address): Promise<Money>;
  scheduleShipment(orderId: string, destination: Address): Promise<string>;
}

interface InventoryServicePort {
  reserveItems(orderId: string, items: OrderItem[]): Promise<void>;
  releaseReservation(orderId: string): Promise<void>;
}

interface PaymentProcessorPort {
  charge(amount: Money, paymentMethod: string): Promise<TransactionId>;
  refund(transactionId: string): Promise<void>;
}
```

### Core Domain Logic

```typescript
class Order {
  private _id: string;
  private _items: OrderItem[] = [];
  private _status: OrderStatus = OrderStatus.PENDING;
  private _destination: Address;
  private _shippingCost: Money = Money.zero();

  constructor(destination: Address) {
    this._id = generateId();
    this._destination = destination;
  }

  addItem(item: OrderItem): void {
    if (this._status !== OrderStatus.PENDING) {
      throw new Error('Cannot modify confirmed order');
    }
    this._items.push(item);
  }

  setShippingCost(cost: Money): void {
    this._shippingCost = cost;
  }

  calculateTotal(): Money {
    const itemsTotal = this._items.reduce(
      (sum, item) => sum.add(item.subtotal()),
      Money.zero()
    );
    return itemsTotal.add(this._shippingCost);
  }

  confirm(): void {
    if (this._items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this._status = OrderStatus.CONFIRMED;
  }

  markAsShipped(): void {
    if (this._status !== OrderStatus.CONFIRMED) {
      throw new Error('Only confirmed orders can be shipped');
    }
    this._status = OrderStatus.SHIPPED;
  }

  // Getters...
  get id(): string { return this._id; }
  get status(): OrderStatus { return this._status; }
  get items(): OrderItem[] { return [...this._items]; }
}
```

### Use Case Using Ports

```typescript
class PlaceOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private shippingService: ShippingServicePort,
    private inventoryService: InventoryServicePort,
    private paymentProcessor: PaymentProcessorPort
  ) {}

  async execute(
    destination: Address,
    items: OrderItem[],
    paymentMethod: string
  ): Promise<OrderDTO> {
    // 1. Create order
    const order = new Order(destination);
    items.forEach(item => order.addItem(item));

    // 2. Calculate shipping (uses port - could be different implementations)
    const shippingCost = await this.shippingService.calculateShippingCost(destination);
    order.setShippingCost(shippingCost);

    // 3. Reserve inventory (uses port - abstracted)
    try {
      await this.inventoryService.reserveItems(order.id, items);
    } catch (error) {
      throw new InventoryNotAvailableError(error.message);
    }

    // 4. Process payment (uses port - abstracted)
    let transactionId: string;
    try {
      transactionId = await this.paymentProcessor.charge(
        order.calculateTotal(),
        paymentMethod
      );
    } catch (error) {
      // Rollback reservation
      await this.inventoryService.releaseReservation(order.id);
      throw new PaymentFailedError(error.message);
    }

    // 5. Confirm order with business rules
    order.confirm();

    // 6. Schedule shipment (uses port - abstracted)
    const trackingNumber = await this.shippingService.scheduleShipment(
      order.id,
      destination
    );
    order.setTrackingNumber(trackingNumber);

    // 7. Persist (uses port - abstracted)
    await this.orderRepository.save(order);

    return new OrderDTO(order);
  }
}
```

### Implement Adapters for Different Technologies

```typescript
// Switch databases without changing core logic
class PostgresOrderRepository implements OrderRepository {
  constructor(private db: Database) {}

  async save(order: Order): Promise<void> {
    await this.db.query('INSERT INTO orders ...', [order.id, ...]);
  }
}

class MockOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.orders.set(order.id, order);
  }

  async findById(id: string): Promise<Order | null> {
    return this.orders.get(id) ?? null;
  }
}

// Switch shipping providers without changing core logic
class FedExShippingAdapter implements ShippingServicePort {
  constructor(private fedexClient: FedExAPI) {}

  async calculateShippingCost(destination: Address): Promise<Money> {
    const quote = await this.fedexClient.getRates(destination);
    return Money.fromCents(quote.standardShippingCents);
  }

  async scheduleShipment(orderId: string, destination: Address): Promise<string> {
    const shipment = await this.fedexClient.createShipment({
      orderId,
      destination: destination.toFedExFormat()
    });
    return shipment.trackingNumber;
  }
}

class UPSShippingAdapter implements ShippingServicePort {
  constructor(private upsClient: UPSAPI) {}

  async calculateShippingCost(destination: Address): Promise<Money> {
    const quote = await this.upsClient.getRate(destination);
    return Money.fromCents(quote.groundRate);
  }

  async scheduleShipment(orderId: string, destination: Address): Promise<string> {
    const shipment = await this.upsClient.schedulePickup({
      packages: [{ orderId }],
      destination
    });
    return shipment.trackingCode;
  }
}
```

## Testability Benefits

The core logic can be tested without any external dependencies:

```typescript
describe('PlaceOrderUseCase', () => {
  let useCase: PlaceOrderUseCase;
  let mockOrderRepo: MockOrderRepository;
  let mockShippingService: MockShippingService;
  let mockInventoryService: MockInventoryService;
  let mockPaymentProcessor: MockPaymentProcessor;

  beforeEach(() => {
    // Use mock implementations
    mockOrderRepo = new MockOrderRepository();
    mockShippingService = new MockShippingService();
    mockInventoryService = new MockInventoryService();
    mockPaymentProcessor = new MockPaymentProcessor();

    useCase = new PlaceOrderUseCase(
      mockOrderRepo,
      mockShippingService,
      mockInventoryService,
      mockPaymentProcessor
    );
  });

  it('should place order successfully with all steps', async () => {
    const destination = new Address('123 Main', 'Springfield', 'IL', '62701');
    const items = [new OrderItem('PROD-1', 2, Money.fromDollars(10))];

    const result = await useCase.execute(destination, items, 'card-token');

    expect(result.status).toBe(OrderStatus.CONFIRMED);
    expect(mockOrderRepo.saved()).toBe(1);
    expect(mockPaymentProcessor.chargesCalled()).toBe(1);
  });

  it('should rollback inventory when payment fails', async () => {
    mockPaymentProcessor.simulateFailure('Card declined');

    const destination = new Address('123 Main', 'Springfield', 'IL', '62701');
    const items = [new OrderItem('PROD-1', 2, Money.fromDollars(10))];

    await expect(
      useCase.execute(destination, items, 'invalid-card')
    ).rejects.toThrow(PaymentFailedError);

    expect(mockInventoryService.reservationsCancelled()).toBe(1);
  });
});
```

## File Structure for Hexagonal Architecture

```
src/
├── core/
│   ├── entities/
│   │   ├── Order.ts
│   │   ├── Account.ts
│   │   └── User.ts
│   ├── ports/
│   │   ├── OrderRepository.ts
│   │   ├── ShippingServicePort.ts
│   │   ├── PaymentProcessorPort.ts
│   │   └── NotificationPort.ts
│   ├── use-cases/
│   │   ├── PlaceOrderUseCase.ts
│   │   ├── ConfirmOrderUseCase.ts
│   │   └── CancelOrderUseCase.ts
│   ├── value-objects/
│   │   ├── Money.ts
│   │   ├── Address.ts
│   │   └── OrderStatus.ts
│   └── errors/
│       └── DomainError.ts
├── adapters/
│   ├── repositories/
│   │   ├── MongoOrderRepository.ts
│   │   ├── PostgresOrderRepository.ts
│   │   └── MockOrderRepository.ts
│   ├── shipping/
│   │   ├── FedExShippingAdapter.ts
│   │   ├── UPSShippingAdapter.ts
│   │   └── MockShippingService.ts
│   ├── payment/
│   │   ├── StripePaymentAdapter.ts
│   │   ├── PayPalPaymentAdapter.ts
│   │   └── MockPaymentProcessor.ts
│   └── notification/
│       ├── SendGridNotificationAdapter.ts
│       ├── TwilioSmsAdapter.ts
│       └── MockNotificationService.ts
├── controllers/
│   └── OrderController.ts
├── config/
│   └── dependencies.ts
└── main.ts
```

## Dependency Injection for Hexagonal

```typescript
/**
 * Composition root
 * Wire up core with specific adapters
 */
class ApplicationFactory {
  static createOrderController(config: AppConfig): OrderController {
    // Create adapters based on configuration
    const orderRepository = config.database === 'mongodb'
      ? new MongoOrderRepository(config.mongoUrl)
      : new PostgresOrderRepository(config.postgresUrl);

    const shippingService = config.shippingProvider === 'fedex'
      ? new FedExShippingAdapter(config.fedexKey)
      : new UPSShippingAdapter(config.upsKey);

    const paymentProcessor = config.paymentProvider === 'stripe'
      ? new StripePaymentAdapter(config.stripeKey)
      : new PayPalPaymentAdapter(config.paypalKey);

    const notificationService = new SendGridNotificationAdapter(
      config.sendgridKey
    );

    // Inject into use case
    const placeOrderUseCase = new PlaceOrderUseCase(
      orderRepository,
      shippingService,
      new RealInventoryService(),
      paymentProcessor
    );

    // Return controller with use case
    return new OrderController(placeOrderUseCase);
  }

  static createTestController(): OrderController {
    // For testing, use mock adapters
    const orderRepository = new MockOrderRepository();
    const shippingService = new MockShippingService();
    const paymentProcessor = new MockPaymentProcessor();
    const notificationService = new MockNotificationService();

    const placeOrderUseCase = new PlaceOrderUseCase(
      orderRepository,
      shippingService,
      new MockInventoryService(),
      paymentProcessor
    );

    return new OrderController(placeOrderUseCase);
  }
}
```

## Tips for AI-Generated Hexagonal Code

1. **Start with core** - Have AI generate domain entities first
2. **Define ports upfront** - Create all port interfaces before asking for adapters
3. **Generate one adapter at a time** - Ask AI to implement each adapter separately
4. **Show pattern examples** - Reference one adapter implementation when asking for others
5. **Use mocks for testing** - Ask AI to create mock implementations alongside real ones
6. **Inject dependencies** - Use constructor injection rather than globals or singletons

## Key Takeaways

- **Core logic is isolated** from external systems
- **Ports define contracts** that adapters implement
- **Easy to swap implementations** without changing core
- **Highly testable** because core can use mock adapters
- **AI can focus on one adapter** at a time
- **Clear separation** between core logic and infrastructure
- **Flexibility** to support multiple external systems simultaneously
