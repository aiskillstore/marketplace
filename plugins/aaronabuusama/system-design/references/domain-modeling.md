# Domain Modeling

## Purpose

Domain modeling captures the essential concepts, relationships, and rules of the business in code.

## Building Blocks

### Entities

Objects defined by identity, not attributes. Two entities with same attributes but different IDs are different.

```typescript
class Order {
  constructor(
    public readonly id: OrderId,  // Identity
    private items: OrderItem[],
    private status: OrderStatus
  ) {}

  // Behavior that enforces business rules
  addItem(item: OrderItem): void {
    if (this.status !== OrderStatus.Draft) {
      throw new CannotModifySubmittedOrderError();
    }
    this.items.push(item);
  }
}

// Two orders with same items are NOT the same order
const order1 = new Order(OrderId.create(), items, status);
const order2 = new Order(OrderId.create(), items, status);
// order1 !== order2 (different identities)
```

### Value Objects

Objects defined by attributes, not identity. Two value objects with same attributes are equal.

```typescript
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: Currency
  ) {
    if (amount < 0) throw new InvalidMoneyError();
  }

  // Immutable - operations return new instances
  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new CurrencyMismatchError();
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount &&
           this.currency === other.currency;
  }
}

// Two Money with same values ARE equal
const price1 = new Money(100, Currency.USD);
const price2 = new Money(100, Currency.USD);
// price1.equals(price2) === true
```

### Aggregates

Cluster of entities and value objects with a single root. The root is the only entry point.

```typescript
// Order is the aggregate root
class Order {
  private items: OrderItem[];  // Contained in aggregate
  private shipping: ShippingInfo;  // Value object

  // All access goes through the root
  addItem(product: ProductId, quantity: number): void {
    const item = new OrderItem(product, quantity, this.id);
    this.items.push(item);
  }

  // Items cannot be accessed directly from outside
  getItems(): ReadonlyArray<OrderItem> {
    return [...this.items];  // Return copy
  }
}

// OrderItem cannot exist without Order
class OrderItem {
  constructor(
    public readonly productId: ProductId,
    public readonly quantity: number,
    public readonly orderId: OrderId  // Reference to root
  ) {}
}
```

**Aggregate Rules:**
1. Only the root has global identity
2. External objects can only reference the root
3. Deleting root deletes everything inside
4. Invariants are enforced within aggregate boundaries

### Domain Events

Something that happened in the domain that domain experts care about.

```typescript
class OrderPlaced implements DomainEvent {
  constructor(
    public readonly orderId: OrderId,
    public readonly customerId: CustomerId,
    public readonly totalAmount: Money,
    public readonly occurredAt: Date = new Date()
  ) {}
}

class Order {
  private events: DomainEvent[] = [];

  place(): void {
    if (this.status !== OrderStatus.Draft) {
      throw new OrderAlreadyPlacedError();
    }
    this.status = OrderStatus.Placed;
    this.events.push(new OrderPlaced(this.id, this.customerId, this.total));
  }

  pullEvents(): DomainEvent[] {
    const events = this.events;
    this.events = [];
    return events;
  }
}
```

### Domain Services

Operations that don't naturally belong to an entity or value object.

```typescript
// Involves multiple aggregates - doesn't belong to either
class TransferService {
  transfer(
    from: Account,
    to: Account,
    amount: Money
  ): void {
    from.withdraw(amount);
    to.deposit(amount);
  }
}
```

**When to use:**
- Operation involves multiple aggregates
- Operation is a domain concept but not an entity
- Operation is stateless

## Modeling Process

### 1. Event Storming

List domain events (past tense, business language):

```
- OrderPlaced
- OrderShipped
- PaymentReceived
- InventoryReserved
- CustomerRegistered
```

### 2. Identify Commands

What triggers each event?

```
PlaceOrder → OrderPlaced
ShipOrder → OrderShipped
ProcessPayment → PaymentReceived
```

### 3. Find Aggregates

Group commands and events that must be consistent:

```
Order Aggregate:
  Commands: PlaceOrder, CancelOrder, AddItem
  Events: OrderPlaced, OrderCancelled, ItemAdded

Payment Aggregate:
  Commands: ProcessPayment, Refund
  Events: PaymentReceived, PaymentRefunded
```

### 4. Define Boundaries

Which data must be immediately consistent?

```
Within Order aggregate (immediate consistency):
  - Order status
  - Order items
  - Order total

Between Order and Payment (eventual consistency):
  - Order payment status
  - Payment order reference
```

## Ubiquitous Language

Use the same terms everywhere:

| Avoid | Use Instead |
|-------|-------------|
| User | Customer, Admin, Guest (specific) |
| Item | Product, LineItem, SKU (context-specific) |
| Status | OrderStatus, PaymentStatus (qualified) |
| Create | Place (order), Register (customer), Submit (application) |

## Modeling Questions

Ask these when modeling:

### Identity
- "Can two [things] with identical attributes be different?"
- "Does this need to be tracked over time?"

### Boundaries
- "What must be immediately consistent?"
- "If I delete X, what else must go?"

### Behavior
- "What operations change this?"
- "What rules must always be true?"

### Events
- "What would the business want to know happened?"
- "What triggers reactions in other parts of the system?"

## Common Mistakes

### 1. Anemic Domain Model

```typescript
// Bad - entity is just data
class Order {
  id: string;
  items: Item[];
  status: string;
}

// Service does all the work
class OrderService {
  addItem(order: Order, item: Item) {
    if (order.status !== 'draft') throw new Error();
    order.items.push(item);
  }
}

// Good - entity has behavior
class Order {
  private items: Item[];
  private status: OrderStatus;

  addItem(item: Item): void {
    if (this.status !== OrderStatus.Draft) {
      throw new CannotModifySubmittedOrderError();
    }
    this.items.push(item);
  }
}
```

### 2. Big Aggregate

```typescript
// Bad - too much in one aggregate
class Customer {
  orders: Order[];      // Could be thousands
  payments: Payment[];  // Could be thousands
  addresses: Address[];
}

// Good - separate aggregates, reference by ID
class Customer {
  addresses: Address[];  // Small, always loaded together
}

class Order {
  customerId: CustomerId;  // Reference, not containment
}
```

### 3. Wrong Aggregate Root

```typescript
// Bad - LineItem as root
class LineItem {
  order: Order;  // References parent
}

// Good - Order as root
class Order {
  items: LineItem[];  // Contains children
}
```

## Key Insight

> The goal is not to model reality. The goal is to model the problem domain in a way that helps solve business problems.
