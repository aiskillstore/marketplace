# Port & Adapter Interface Templates

## Inbound Port (Use Case Interface)

```typescript
// src/application/ports/inbound/PlaceOrderUseCase.ts

import type { OrderId } from '../../../domain/value-objects';

// Command - input data
export interface PlaceOrderCommand {
  readonly customerId: string;
  readonly items: Array<{
    productId: string;
    quantity: number;
  }>;
  readonly shippingAddress: {
    street: string;
    city: string;
    postalCode: string;
    country: string;
  };
}

// Result - output data (success case)
export interface PlaceOrderResult {
  readonly orderId: string;
  readonly estimatedDelivery: Date;
}

// Error - output data (failure cases)
export type PlaceOrderError =
  | { type: 'CUSTOMER_NOT_FOUND' }
  | { type: 'INSUFFICIENT_INVENTORY'; productId: string }
  | { type: 'PAYMENT_FAILED'; reason: string }
  | { type: 'INVALID_ADDRESS' };

// Port interface
export interface PlaceOrderUseCase {
  execute(
    command: PlaceOrderCommand
  ): Promise<PlaceOrderResult | PlaceOrderError>;
}
```

## Outbound Port (Repository)

```typescript
// src/application/ports/outbound/OrderRepository.ts

import type { Order, OrderId, CustomerId } from '../../../domain';

export interface OrderRepository {
  // Commands
  save(order: Order): Promise<void>;
  delete(id: OrderId): Promise<void>;

  // Queries
  findById(id: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
  findPending(): Promise<Order[]>;

  // Existence check (avoids loading full entity)
  exists(id: OrderId): Promise<boolean>;
}
```

## Outbound Port (External Service Gateway)

```typescript
// src/application/ports/outbound/PaymentGateway.ts

import type { Money, PaymentMethod } from '../../../domain';

export interface ChargeRequest {
  readonly amount: Money;
  readonly method: PaymentMethod;
  readonly idempotencyKey: string;
}

export interface ChargeResult {
  readonly transactionId: string;
  readonly status: 'succeeded' | 'pending' | 'failed';
  readonly chargedAt: Date;
}

export interface RefundRequest {
  readonly transactionId: string;
  readonly amount?: Money; // Partial refund if specified
  readonly reason?: string;
}

export interface RefundResult {
  readonly refundId: string;
  readonly status: 'succeeded' | 'pending' | 'failed';
}

export interface PaymentGateway {
  charge(request: ChargeRequest): Promise<ChargeResult>;
  refund(request: RefundRequest): Promise<RefundResult>;
  getTransaction(transactionId: string): Promise<ChargeResult | null>;
}
```

## Outbound Port (Event Publisher)

```typescript
// src/application/ports/outbound/EventPublisher.ts

import type { DomainEvent } from '../../../domain';

export interface EventPublisher {
  publish(event: DomainEvent): Promise<void>;
  publishAll(events: DomainEvent[]): Promise<void>;
}
```

## Outbound Port (Notification Service)

```typescript
// src/application/ports/outbound/NotificationService.ts

export interface EmailNotification {
  readonly to: string;
  readonly subject: string;
  readonly body: string;
  readonly html?: string;
}

export interface NotificationService {
  sendEmail(notification: EmailNotification): Promise<void>;
}
```

## Driven Adapter (Repository Implementation)

```typescript
// src/infrastructure/persistence/PostgresOrderRepository.ts

import type { Order, OrderId, CustomerId } from '../../domain';
import type { OrderRepository } from '../../application/ports/outbound';
import { OrderMapper } from './mappers/OrderMapper';

export class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly db: Database) {}

  async save(order: Order): Promise<void> {
    const row = OrderMapper.toRow(order);
    await this.db.query(
      `INSERT INTO orders (id, customer_id, status, total, created_at)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (id) DO UPDATE SET
         status = EXCLUDED.status,
         total = EXCLUDED.total`,
      [row.id, row.customerId, row.status, row.total, row.createdAt]
    );
  }

  async findById(id: OrderId): Promise<Order | null> {
    const row = await this.db.queryOne(
      'SELECT * FROM orders WHERE id = $1',
      [id.value]
    );
    return row ? OrderMapper.toDomain(row) : null;
  }

  async findByCustomer(customerId: CustomerId): Promise<Order[]> {
    const rows = await this.db.query(
      'SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC',
      [customerId.value]
    );
    return rows.map(OrderMapper.toDomain);
  }

  async findPending(): Promise<Order[]> {
    const rows = await this.db.query(
      "SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at"
    );
    return rows.map(OrderMapper.toDomain);
  }

  async delete(id: OrderId): Promise<void> {
    await this.db.query('DELETE FROM orders WHERE id = $1', [id.value]);
  }

  async exists(id: OrderId): Promise<boolean> {
    const result = await this.db.queryOne(
      'SELECT 1 FROM orders WHERE id = $1',
      [id.value]
    );
    return result !== null;
  }
}
```

## Driven Adapter (External Service Implementation)

```typescript
// src/infrastructure/external/stripe/StripePaymentGateway.ts

import type {
  PaymentGateway,
  ChargeRequest,
  ChargeResult,
  RefundRequest,
  RefundResult,
} from '../../../application/ports/outbound';

export class StripePaymentGateway implements PaymentGateway {
  constructor(private readonly stripeClient: Stripe) {}

  async charge(request: ChargeRequest): Promise<ChargeResult> {
    const intent = await this.stripeClient.paymentIntents.create({
      amount: request.amount.cents,
      currency: request.amount.currency.toLowerCase(),
      payment_method: this.mapPaymentMethod(request.method),
      idempotency_key: request.idempotencyKey,
      confirm: true,
    });

    return {
      transactionId: intent.id,
      status: this.mapStatus(intent.status),
      chargedAt: new Date(intent.created * 1000),
    };
  }

  async refund(request: RefundRequest): Promise<RefundResult> {
    const refund = await this.stripeClient.refunds.create({
      payment_intent: request.transactionId,
      amount: request.amount?.cents,
      reason: request.reason as Stripe.RefundCreateParams.Reason,
    });

    return {
      refundId: refund.id,
      status: this.mapRefundStatus(refund.status),
    };
  }

  async getTransaction(transactionId: string): Promise<ChargeResult | null> {
    try {
      const intent = await this.stripeClient.paymentIntents.retrieve(
        transactionId
      );
      return {
        transactionId: intent.id,
        status: this.mapStatus(intent.status),
        chargedAt: new Date(intent.created * 1000),
      };
    } catch {
      return null;
    }
  }

  private mapStatus(status: string): ChargeResult['status'] {
    // Map Stripe status to our domain status
  }

  private mapRefundStatus(status: string | null): RefundResult['status'] {
    // Map Stripe refund status to our domain status
  }

  private mapPaymentMethod(method: PaymentMethod): string {
    // Map domain payment method to Stripe format
  }
}
```

## Driving Adapter (HTTP Controller)

```typescript
// src/interfaces/http/controllers/OrderController.ts

import type { PlaceOrderUseCase } from '../../../application/ports/inbound';

export class OrderController {
  constructor(private readonly placeOrder: PlaceOrderUseCase) {}

  async create(req: Request): Promise<Response> {
    const body = await req.json();

    const result = await this.placeOrder.execute({
      customerId: body.customerId,
      items: body.items,
      shippingAddress: body.shippingAddress,
    });

    if ('type' in result) {
      // Error case
      return new Response(JSON.stringify({ error: result }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Success case
    return new Response(JSON.stringify(result), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
```
