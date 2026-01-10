# Common Architecture Mistakes

## 1. Framework Coupling

### The Mistake

Domain logic depends on framework/infrastructure:

```typescript
// Bad - Entity knows about ORM
@Entity()
class Order {
  @PrimaryGeneratedColumn()
  id: string;

  @Column()
  status: string;

  @OneToMany(() => OrderItem, item => item.order)
  items: OrderItem[];
}
```

### Why It's Bad

- Can't test without ORM
- Can't switch ORMs
- Domain polluted with infrastructure concerns
- Framework changes break domain

### The Fix

```typescript
// Domain entity - pure
class Order {
  constructor(
    public readonly id: OrderId,
    private items: OrderItem[],
    private status: OrderStatus
  ) {}
}

// ORM entity - separate
@Entity('orders')
class OrderOrmEntity {
  @PrimaryColumn()
  id: string;

  @Column()
  status: string;
}

// Mapper bridges the gap
class OrderMapper {
  toDomain(orm: OrderOrmEntity): Order { ... }
  toOrm(domain: Order): OrderOrmEntity { ... }
}
```

## 2. Business Logic in Controllers

### The Mistake

```typescript
// Bad - Controller does business logic
class OrderController {
  async createOrder(req: Request) {
    const { items, customerId } = req.body;

    // Business rules in controller!
    if (items.length === 0) {
      return res.status(400).json({ error: 'No items' });
    }

    const customer = await this.customerRepo.find(customerId);
    if (customer.hasOutstandingBalance()) {
      return res.status(400).json({ error: 'Outstanding balance' });
    }

    // More business logic...
    const total = items.reduce((sum, i) => sum + i.price, 0);
    if (total > customer.creditLimit) {
      return res.status(400).json({ error: 'Over credit limit' });
    }
  }
}
```

### Why It's Bad

- Can't reuse logic (CLI, events, other controllers)
- Can't unit test without HTTP
- Business rules scattered everywhere
- Hard to understand the domain

### The Fix

```typescript
// Use case contains business logic
class PlaceOrderUseCase {
  execute(command: PlaceOrderCommand): Result<OrderId, PlaceOrderError> {
    if (command.items.length === 0) {
      return err(PlaceOrderError.NoItems);
    }

    const customer = await this.customerRepo.find(command.customerId);
    if (customer.hasOutstandingBalance()) {
      return err(PlaceOrderError.OutstandingBalance);
    }

    const order = Order.create(command.items);
    if (order.total.exceeds(customer.creditLimit)) {
      return err(PlaceOrderError.OverCreditLimit);
    }

    await this.orderRepo.save(order);
    return ok(order.id);
  }
}

// Controller is thin
class OrderController {
  async createOrder(req: Request) {
    const result = await this.placeOrder.execute(req.body);
    return result.match({
      ok: (id) => res.json({ orderId: id }),
      err: (e) => res.status(400).json({ error: e })
    });
  }
}
```

## 3. Missing Abstractions

### The Mistake

```typescript
// Bad - Use case directly uses external service
class SendInvoiceUseCase {
  async execute(orderId: OrderId) {
    const order = await this.orderRepo.find(orderId);

    // Direct dependency on SendGrid
    await sendgrid.send({
      to: order.customer.email,
      template: 'invoice',
      data: { order }
    });
  }
}
```

### Why It's Bad

- Can't test without calling SendGrid
- Can't switch email providers
- Use case knows about email implementation details

### The Fix

```typescript
// Define what we need (port)
interface EmailSender {
  sendInvoice(email: Email, order: Order): Promise<void>;
}

// Use case uses abstraction
class SendInvoiceUseCase {
  constructor(private emailSender: EmailSender) {}

  async execute(orderId: OrderId) {
    const order = await this.orderRepo.find(orderId);
    await this.emailSender.sendInvoice(order.customer.email, order);
  }
}

// Adapter implements for specific provider
class SendGridEmailSender implements EmailSender {
  async sendInvoice(email: Email, order: Order) {
    await sendgrid.send({
      to: email.value,
      template: 'invoice',
      data: this.formatOrder(order)
    });
  }
}
```

## 4. Anemic Domain Model

### The Mistake

```typescript
// Bad - Entity is just a data bag
class Order {
  id: string;
  customerId: string;
  items: Item[];
  status: string;
  total: number;
}

// Service has all the logic
class OrderService {
  addItem(order: Order, item: Item) {
    order.items.push(item);
    order.total += item.price;
  }

  submit(order: Order) {
    order.status = 'submitted';
  }
}
```

### Why It's Bad

- Business rules not encapsulated
- Anyone can put entity in invalid state
- Rules duplicated across services
- Hard to understand what operations are valid

### The Fix

```typescript
// Good - Entity protects its invariants
class Order {
  private constructor(
    public readonly id: OrderId,
    private items: OrderItem[],
    private _status: OrderStatus
  ) {}

  static create(customerId: CustomerId): Order {
    return new Order(
      OrderId.generate(),
      [],
      OrderStatus.Draft
    );
  }

  addItem(item: OrderItem): void {
    this.ensureDraft();
    this.items.push(item);
  }

  submit(): void {
    this.ensureDraft();
    if (this.items.length === 0) {
      throw new CannotSubmitEmptyOrderError();
    }
    this._status = OrderStatus.Submitted;
  }

  private ensureDraft(): void {
    if (this._status !== OrderStatus.Draft) {
      throw new OrderNotEditableError();
    }
  }

  get total(): Money {
    return this.items.reduce(
      (sum, item) => sum.add(item.subtotal),
      Money.zero()
    );
  }
}
```

## 5. Wrong Aggregate Boundaries

### The Mistake

```typescript
// Bad - Customer aggregate is too big
class Customer {
  id: CustomerId;
  name: string;
  orders: Order[];        // Could be millions
  payments: Payment[];    // Could be millions
  reviews: Review[];      // Could be thousands
}
```

### Why It's Bad

- Loading customer loads everything
- Concurrent modifications conflict
- Performance degrades over time
- Transactions span too much data

### The Fix

```typescript
// Good - Small, focused aggregates
class Customer {
  id: CustomerId;
  name: CustomerName;
  email: Email;
  // Only data that must be consistent with customer
}

class Order {
  id: OrderId;
  customerId: CustomerId;  // Reference, not containment
  items: OrderItem[];
}

class Payment {
  id: PaymentId;
  orderId: OrderId;  // Reference
  customerId: CustomerId;  // Reference
}
```

**Aggregate sizing rule:** If you wouldn't delete it when deleting the root, it's probably a separate aggregate.

## 6. Leaky Abstractions

### The Mistake

```typescript
// Bad - Port exposes database concepts
interface OrderRepository {
  findByQuery(sql: string): Promise<Order[]>;
  beginTransaction(): Promise<Transaction>;
  executeInTransaction(tx: Transaction, fn: () => void): Promise<void>;
}
```

### Why It's Bad

- Implementation details leak to domain
- Can't switch storage technologies
- Domain code becomes database-aware

### The Fix

```typescript
// Good - Port expresses domain needs
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findPendingForCustomer(customerId: CustomerId): Promise<Order[]>;
}

// Transaction handling is infrastructure concern
interface UnitOfWork {
  execute<T>(fn: () => Promise<T>): Promise<T>;
}
```

## 7. Premature Abstraction

### The Mistake

```typescript
// Bad - Abstraction before second use case
interface MessageSender<T> {
  send(message: T): Promise<void>;
}

interface EmailMessage { ... }
interface SmsMessage { ... }
interface PushMessage { ... }

class GenericMessageService<T> {
  constructor(private sender: MessageSender<T>) {}
  // Used exactly once, for email
}
```

### Why It's Bad

- Complexity without benefit
- Wrong abstraction (guessed, not discovered)
- Harder to understand
- Will probably be refactored anyway

### The Fix

Wait for the second use case. Then abstract.

```typescript
// Good - Start simple
class EmailSender {
  sendInvoice(email: Email, order: Order): Promise<void>;
}

// When SMS is needed, THEN abstract
interface NotificationSender {
  sendOrderConfirmation(recipient: Recipient, order: Order): Promise<void>;
}
```

## Detection Questions

Ask yourself:

1. "Can I test this without external services?" (If no → missing abstraction)
2. "Where is this business rule defined?" (If scattered → anemic model)
3. "What happens if I change the database?" (If domain changes → framework coupling)
4. "Can I reuse this logic?" (If no → logic in wrong place)
5. "What gets deleted with this?" (If not everything → wrong boundary)
