# Entity Template

## Basic Structure

```typescript
// src/domain/entities/[EntityName].ts

import { [EntityName]Id } from '../value-objects';
import { [DomainEvent] } from '../events';
import { [DomainError] } from '../errors';

export class [EntityName] {
  private events: DomainEvent[] = [];

  private constructor(
    public readonly id: [EntityName]Id,
    private /* mutable state fields */
  ) {}

  // Factory method - the only way to create
  static create(props: Create[EntityName]Props): [EntityName] {
    // Validation
    // Initialize with default state
    // Return new instance
  }

  // Reconstitution from persistence (no validation, no events)
  static reconstitute(props: [EntityName]Props): [EntityName] {
    return new [EntityName](/* ... */);
  }

  // Behavior methods that enforce invariants
  doSomething(/* args */): void {
    this.ensureCanDoSomething();
    // Mutate state
    // Record event
  }

  // Query methods (no side effects)
  get someValue(): SomeType {
    return /* derived or direct value */;
  }

  // Event handling
  pullEvents(): DomainEvent[] {
    const events = this.events;
    this.events = [];
    return events;
  }

  private recordEvent(event: DomainEvent): void {
    this.events.push(event);
  }

  // Private invariant checks
  private ensureCanDoSomething(): void {
    if (/* invariant violated */) {
      throw new [DomainError]();
    }
  }
}
```

## Complete Example: Order Entity

```typescript
// src/domain/entities/Order.ts

import { OrderId, CustomerId, Money } from '../value-objects';
import { OrderItem } from './OrderItem';
import { OrderPlaced, OrderCancelled, ItemAdded } from '../events';
import { OrderNotEditableError, EmptyOrderError, OrderAlreadyCancelledError } from '../errors';

export enum OrderStatus {
  Draft = 'draft',
  Placed = 'placed',
  Paid = 'paid',
  Shipped = 'shipped',
  Delivered = 'delivered',
  Cancelled = 'cancelled',
}

export interface CreateOrderProps {
  customerId: CustomerId;
  items?: OrderItem[];
}

export interface OrderProps {
  id: OrderId;
  customerId: CustomerId;
  items: OrderItem[];
  status: OrderStatus;
  paymentTransactionId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export class Order {
  private events: DomainEvent[] = [];

  private constructor(
    public readonly id: OrderId,
    public readonly customerId: CustomerId,
    private _items: OrderItem[],
    private _status: OrderStatus,
    private _paymentTransactionId: string | undefined,
    public readonly createdAt: Date,
    private _updatedAt: Date
  ) {}

  // ===== Factory Methods =====

  static create(props: CreateOrderProps): Order {
    const now = new Date();
    return new Order(
      OrderId.generate(),
      props.customerId,
      props.items ?? [],
      OrderStatus.Draft,
      undefined,
      now,
      now
    );
  }

  static reconstitute(props: OrderProps): Order {
    return new Order(
      props.id,
      props.customerId,
      props.items,
      props.status,
      props.paymentTransactionId,
      props.createdAt,
      props.updatedAt
    );
  }

  // ===== Commands (Behavior) =====

  addItem(item: OrderItem): void {
    this.ensureEditable();
    this._items.push(item);
    this._updatedAt = new Date();
    this.recordEvent(new ItemAdded(this.id, item));
  }

  removeItem(productId: string): void {
    this.ensureEditable();
    const index = this._items.findIndex(i => i.productId === productId);
    if (index !== -1) {
      this._items.splice(index, 1);
      this._updatedAt = new Date();
    }
  }

  place(): void {
    this.ensureEditable();
    if (this._items.length === 0) {
      throw new EmptyOrderError(this.id);
    }
    this._status = OrderStatus.Placed;
    this._updatedAt = new Date();
    this.recordEvent(new OrderPlaced(this.id, this.customerId, this.total));
  }

  markPaid(transactionId: string): void {
    if (this._status !== OrderStatus.Placed) {
      throw new Error('Order must be placed before payment');
    }
    this._paymentTransactionId = transactionId;
    this._status = OrderStatus.Paid;
    this._updatedAt = new Date();
  }

  ship(): void {
    if (this._status !== OrderStatus.Paid) {
      throw new Error('Order must be paid before shipping');
    }
    this._status = OrderStatus.Shipped;
    this._updatedAt = new Date();
  }

  cancel(): void {
    if (this._status === OrderStatus.Cancelled) {
      throw new OrderAlreadyCancelledError(this.id);
    }
    if (this._status === OrderStatus.Shipped || this._status === OrderStatus.Delivered) {
      throw new Error('Cannot cancel shipped or delivered order');
    }
    this._status = OrderStatus.Cancelled;
    this._updatedAt = new Date();
    this.recordEvent(new OrderCancelled(this.id));
  }

  // ===== Queries =====

  get status(): OrderStatus {
    return this._status;
  }

  get items(): ReadonlyArray<OrderItem> {
    return [...this._items];
  }

  get itemCount(): number {
    return this._items.reduce((sum, item) => sum + item.quantity, 0);
  }

  get total(): Money {
    return this._items.reduce(
      (sum, item) => sum.add(item.subtotal),
      Money.zero('USD')
    );
  }

  get paymentTransactionId(): string | undefined {
    return this._paymentTransactionId;
  }

  get updatedAt(): Date {
    return this._updatedAt;
  }

  get isEditable(): boolean {
    return this._status === OrderStatus.Draft;
  }

  get isCancellable(): boolean {
    return this._status !== OrderStatus.Shipped &&
           this._status !== OrderStatus.Delivered &&
           this._status !== OrderStatus.Cancelled;
  }

  // ===== Events =====

  pullEvents(): DomainEvent[] {
    const events = this.events;
    this.events = [];
    return events;
  }

  private recordEvent(event: DomainEvent): void {
    this.events.push(event);
  }

  // ===== Invariant Checks =====

  private ensureEditable(): void {
    if (!this.isEditable) {
      throw new OrderNotEditableError(this.id, this._status);
    }
  }
}
```

## Entity ID Value Object

```typescript
// src/domain/value-objects/OrderId.ts

export class OrderId {
  private constructor(public readonly value: string) {}

  static generate(): OrderId {
    return new OrderId(crypto.randomUUID());
  }

  static from(value: string): OrderId {
    if (!value || value.trim() === '') {
      throw new Error('OrderId cannot be empty');
    }
    return new OrderId(value);
  }

  equals(other: OrderId): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}
```

## Testing Entity

```typescript
// src/domain/entities/Order.test.ts

import { describe, test, expect } from 'bun:test';
import { Order, OrderStatus } from './Order';
import { CustomerId, Money } from '../value-objects';
import { OrderItem } from './OrderItem';

describe('Order', () => {
  const customerId = CustomerId.from('customer-123');

  const createItem = (price: number = 100): OrderItem =>
    OrderItem.create({
      productId: 'product-1',
      quantity: 1,
      unitPrice: Money.of(price, 'USD'),
    });

  describe('create', () => {
    test('creates order in draft status', () => {
      const order = Order.create({ customerId });

      expect(order.status).toBe(OrderStatus.Draft);
      expect(order.items).toHaveLength(0);
    });
  });

  describe('addItem', () => {
    test('adds item to draft order', () => {
      const order = Order.create({ customerId });
      const item = createItem();

      order.addItem(item);

      expect(order.items).toHaveLength(1);
    });

    test('throws when order is not editable', () => {
      const order = Order.create({ customerId, items: [createItem()] });
      order.place();

      expect(() => order.addItem(createItem())).toThrow();
    });
  });

  describe('place', () => {
    test('changes status to placed', () => {
      const order = Order.create({ customerId, items: [createItem()] });

      order.place();

      expect(order.status).toBe(OrderStatus.Placed);
    });

    test('throws when order is empty', () => {
      const order = Order.create({ customerId });

      expect(() => order.place()).toThrow(EmptyOrderError);
    });

    test('records OrderPlaced event', () => {
      const order = Order.create({ customerId, items: [createItem()] });

      order.place();
      const events = order.pullEvents();

      expect(events).toHaveLength(1);
      expect(events[0]).toBeInstanceOf(OrderPlaced);
    });
  });

  describe('total', () => {
    test('calculates sum of item subtotals', () => {
      const order = Order.create({ customerId });
      order.addItem(createItem(100));
      order.addItem(createItem(200));

      expect(order.total.amount).toBe(300);
    });
  });
});
```
