# Repository Template

## Port Interface

```typescript
// src/application/ports/outbound/[Entity]Repository.ts

import type { [Entity], [Entity]Id } from '../../../domain';

export interface [Entity]Repository {
  // Commands
  save(entity: [Entity]): Promise<void>;
  delete(id: [Entity]Id): Promise<void>;

  // Queries
  findById(id: [Entity]Id): Promise<[Entity] | null>;
  exists(id: [Entity]Id): Promise<boolean>;

  // Domain-specific queries
  findBy[Criteria]([criteria]: [CriteriaType]): Promise<[Entity][]>;
}
```

## Complete Example: OrderRepository

### Port Interface

```typescript
// src/application/ports/outbound/OrderRepository.ts

import type { Order, OrderId, CustomerId, OrderStatus } from '../../../domain';

export interface OrderRepository {
  // Commands
  save(order: Order): Promise<void>;
  delete(id: OrderId): Promise<void>;

  // Basic queries
  findById(id: OrderId): Promise<Order | null>;
  exists(id: OrderId): Promise<boolean>;

  // Domain-specific queries
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
  findByStatus(status: OrderStatus): Promise<Order[]>;
  findPendingOlderThan(date: Date): Promise<Order[]>;

  // Aggregate queries (for read models)
  countByStatus(status: OrderStatus): Promise<number>;
}
```

### Adapter Implementation

```typescript
// src/infrastructure/persistence/PostgresOrderRepository.ts

import { Database } from 'bun:sqlite'; // or your DB client
import type { Order, OrderId, CustomerId, OrderStatus } from '../../domain';
import type { OrderRepository } from '../../application/ports/outbound';
import { OrderMapper } from './mappers/OrderMapper';

interface OrderRow {
  id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  total_currency: string;
  payment_transaction_id: string | null;
  created_at: string;
  updated_at: string;
}

export class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly db: Database) {}

  async save(order: Order): Promise<void> {
    const row = OrderMapper.toRow(order);

    // Upsert pattern
    this.db.run(
      `INSERT INTO orders (id, customer_id, status, total_amount, total_currency, payment_transaction_id, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT (id) DO UPDATE SET
         status = excluded.status,
         total_amount = excluded.total_amount,
         total_currency = excluded.total_currency,
         payment_transaction_id = excluded.payment_transaction_id,
         updated_at = excluded.updated_at`,
      [
        row.id,
        row.customer_id,
        row.status,
        row.total_amount,
        row.total_currency,
        row.payment_transaction_id,
        row.created_at,
        row.updated_at,
      ]
    );

    // Save items (if aggregate includes them)
    await this.saveItems(order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    const row = this.db.query<OrderRow, [string]>(
      'SELECT * FROM orders WHERE id = ?'
    ).get(id.value);

    if (!row) return null;

    const items = await this.loadItems(id);
    return OrderMapper.toDomain(row, items);
  }

  async findByCustomer(customerId: CustomerId): Promise<Order[]> {
    const rows = this.db.query<OrderRow, [string]>(
      'SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC'
    ).all(customerId.value);

    return Promise.all(
      rows.map(async (row) => {
        const items = await this.loadItems(OrderId.from(row.id));
        return OrderMapper.toDomain(row, items);
      })
    );
  }

  async findByStatus(status: OrderStatus): Promise<Order[]> {
    const rows = this.db.query<OrderRow, [string]>(
      'SELECT * FROM orders WHERE status = ? ORDER BY created_at'
    ).all(status);

    return Promise.all(
      rows.map(async (row) => {
        const items = await this.loadItems(OrderId.from(row.id));
        return OrderMapper.toDomain(row, items);
      })
    );
  }

  async findPendingOlderThan(date: Date): Promise<Order[]> {
    const rows = this.db.query<OrderRow, [string, string]>(
      `SELECT * FROM orders
       WHERE status = 'pending' AND created_at < ?
       ORDER BY created_at`
    ).all(date.toISOString());

    return Promise.all(
      rows.map(async (row) => {
        const items = await this.loadItems(OrderId.from(row.id));
        return OrderMapper.toDomain(row, items);
      })
    );
  }

  async delete(id: OrderId): Promise<void> {
    this.db.run('DELETE FROM order_items WHERE order_id = ?', [id.value]);
    this.db.run('DELETE FROM orders WHERE id = ?', [id.value]);
  }

  async exists(id: OrderId): Promise<boolean> {
    const result = this.db.query<{ count: number }, [string]>(
      'SELECT COUNT(*) as count FROM orders WHERE id = ?'
    ).get(id.value);

    return (result?.count ?? 0) > 0;
  }

  async countByStatus(status: OrderStatus): Promise<number> {
    const result = this.db.query<{ count: number }, [string]>(
      'SELECT COUNT(*) as count FROM orders WHERE status = ?'
    ).get(status);

    return result?.count ?? 0;
  }

  private async saveItems(order: Order): Promise<void> {
    // Delete existing items
    this.db.run('DELETE FROM order_items WHERE order_id = ?', [order.id.value]);

    // Insert current items
    for (const item of order.items) {
      this.db.run(
        `INSERT INTO order_items (id, order_id, product_id, quantity, unit_price_amount, unit_price_currency)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [
          item.id.value,
          order.id.value,
          item.productId,
          item.quantity,
          item.unitPrice.amount,
          item.unitPrice.currency,
        ]
      );
    }
  }

  private async loadItems(orderId: OrderId): Promise<OrderItem[]> {
    const rows = this.db.query<OrderItemRow, [string]>(
      'SELECT * FROM order_items WHERE order_id = ?'
    ).all(orderId.value);

    return rows.map(OrderItemMapper.toDomain);
  }
}
```

### Mapper

```typescript
// src/infrastructure/persistence/mappers/OrderMapper.ts

import {
  Order,
  OrderId,
  CustomerId,
  OrderStatus,
  OrderItem,
  Money,
} from '../../../domain';

interface OrderRow {
  id: string;
  customer_id: string;
  status: string;
  total_amount: number;
  total_currency: string;
  payment_transaction_id: string | null;
  created_at: string;
  updated_at: string;
}

export class OrderMapper {
  static toDomain(row: OrderRow, items: OrderItem[]): Order {
    return Order.reconstitute({
      id: OrderId.from(row.id),
      customerId: CustomerId.from(row.customer_id),
      items,
      status: row.status as OrderStatus,
      paymentTransactionId: row.payment_transaction_id ?? undefined,
      createdAt: new Date(row.created_at),
      updatedAt: new Date(row.updated_at),
    });
  }

  static toRow(order: Order): OrderRow {
    return {
      id: order.id.value,
      customer_id: order.customerId.value,
      status: order.status,
      total_amount: order.total.amount,
      total_currency: order.total.currency,
      payment_transaction_id: order.paymentTransactionId ?? null,
      created_at: order.createdAt.toISOString(),
      updated_at: order.updatedAt.toISOString(),
    };
  }
}
```

### Fake for Testing

```typescript
// src/infrastructure/persistence/__fakes__/FakeOrderRepository.ts

import type { Order, OrderId, CustomerId, OrderStatus } from '../../../domain';
import type { OrderRepository } from '../../../application/ports/outbound';

export class FakeOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();

  // Track calls for assertions
  public savedOrders: Order[] = [];
  public deletedIds: OrderId[] = [];

  async save(order: Order): Promise<void> {
    this.savedOrders.push(order);
    this.orders.set(order.id.value, order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    return this.orders.get(id.value) ?? null;
  }

  async findByCustomer(customerId: CustomerId): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(
      (o) => o.customerId.equals(customerId)
    );
  }

  async findByStatus(status: OrderStatus): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(
      (o) => o.status === status
    );
  }

  async findPendingOlderThan(date: Date): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(
      (o) => o.status === 'pending' && o.createdAt < date
    );
  }

  async delete(id: OrderId): Promise<void> {
    this.deletedIds.push(id);
    this.orders.delete(id.value);
  }

  async exists(id: OrderId): Promise<boolean> {
    return this.orders.has(id.value);
  }

  async countByStatus(status: OrderStatus): Promise<number> {
    return Array.from(this.orders.values()).filter(
      (o) => o.status === status
    ).length;
  }

  // Test helpers
  givenOrder(order: Order): void {
    this.orders.set(order.id.value, order);
  }

  clear(): void {
    this.orders.clear();
    this.savedOrders = [];
    this.deletedIds = [];
  }
}
```

## Query Method Naming Conventions

| Pattern | Use Case | Example |
|---------|----------|---------|
| `findById` | Single entity by ID | `findById(id): Entity \| null` |
| `findBy[Field]` | Multiple by single field | `findByCustomer(customerId): Entity[]` |
| `findBy[Criteria]` | Complex criteria | `findPendingOlderThan(date): Entity[]` |
| `exists` | Existence check | `exists(id): boolean` |
| `count[By...]` | Aggregate count | `countByStatus(status): number` |
| `findAll` | All entities (use sparingly) | `findAll(): Entity[]` |

## Anti-Patterns to Avoid

```typescript
// BAD: Exposing database concepts
interface OrderRepository {
  query(sql: string): Promise<any[]>;
  beginTransaction(): Promise<void>;
}

// BAD: Returning ORM entities
interface OrderRepository {
  findById(id: string): Promise<OrderOrmEntity>;
}

// BAD: Generic repository
interface Repository<T> {
  save(entity: T): Promise<void>;
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  delete(id: string): Promise<void>;
}

// GOOD: Domain-specific repository
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findPendingForCustomer(customerId: CustomerId): Promise<Order[]>;
}
```
