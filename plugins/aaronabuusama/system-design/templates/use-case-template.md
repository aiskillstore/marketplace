# Use Case Template

## Structure

```typescript
// src/application/use-cases/[UseCaseName]/[UseCaseName].ts

import type { [Entity] } from '../../../domain';
import type { [Repository] } from '../../ports/outbound';

// 1. Command (input)
export interface [UseCaseName]Command {
  readonly /* input fields */;
}

// 2. Result (success output)
export interface [UseCaseName]Result {
  readonly /* output fields */;
}

// 3. Error (failure cases)
export type [UseCaseName]Error =
  | { type: 'ERROR_TYPE_1'; /* context */ }
  | { type: 'ERROR_TYPE_2'; /* context */ };

// 4. Port interface (optional - can be in ports/inbound/)
export interface [UseCaseName]UseCase {
  execute(command: [UseCaseName]Command): Promise<[UseCaseName]Result | [UseCaseName]Error>;
}

// 5. Implementation
export class [UseCaseName]Impl implements [UseCaseName]UseCase {
  constructor(
    private readonly /* injected ports */
  ) {}

  async execute(command: [UseCaseName]Command): Promise<[UseCaseName]Result | [UseCaseName]Error> {
    // 1. Validate command
    // 2. Load required entities
    // 3. Execute domain logic
    // 4. Persist changes
    // 5. Publish events
    // 6. Return result
  }
}
```

## Complete Example: PlaceOrder

```typescript
// src/application/use-cases/PlaceOrder/PlaceOrder.ts

import { Order, OrderId } from '../../../domain/entities';
import { Money } from '../../../domain/value-objects';
import type { OrderRepository, CustomerRepository, InventoryService, PaymentGateway, EventPublisher } from '../../ports/outbound';

// Command
export interface PlaceOrderCommand {
  readonly customerId: string;
  readonly items: ReadonlyArray<{
    readonly productId: string;
    readonly quantity: number;
  }>;
  readonly paymentMethodId: string;
}

// Result
export interface PlaceOrderResult {
  readonly orderId: string;
  readonly total: number;
  readonly currency: string;
}

// Errors
export type PlaceOrderError =
  | { type: 'CUSTOMER_NOT_FOUND' }
  | { type: 'EMPTY_ORDER' }
  | { type: 'PRODUCT_NOT_FOUND'; productId: string }
  | { type: 'INSUFFICIENT_INVENTORY'; productId: string; available: number; requested: number }
  | { type: 'PAYMENT_FAILED'; reason: string };

// Implementation
export class PlaceOrderUseCase {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly customerRepository: CustomerRepository,
    private readonly inventoryService: InventoryService,
    private readonly paymentGateway: PaymentGateway,
    private readonly eventPublisher: EventPublisher
  ) {}

  async execute(command: PlaceOrderCommand): Promise<PlaceOrderResult | PlaceOrderError> {
    // 1. Validate command
    if (command.items.length === 0) {
      return { type: 'EMPTY_ORDER' };
    }

    // 2. Load customer
    const customer = await this.customerRepository.findById(command.customerId);
    if (!customer) {
      return { type: 'CUSTOMER_NOT_FOUND' };
    }

    // 3. Check inventory
    for (const item of command.items) {
      const availability = await this.inventoryService.checkAvailability(
        item.productId,
        item.quantity
      );
      if (!availability.available) {
        return {
          type: 'INSUFFICIENT_INVENTORY',
          productId: item.productId,
          available: availability.currentStock,
          requested: item.quantity,
        };
      }
    }

    // 4. Create order (domain logic)
    const order = Order.create({
      customerId: customer.id,
      items: command.items,
    });

    // 5. Process payment
    const paymentResult = await this.paymentGateway.charge({
      amount: order.total,
      method: { id: command.paymentMethodId },
      idempotencyKey: order.id.value,
    });

    if (paymentResult.status === 'failed') {
      return { type: 'PAYMENT_FAILED', reason: paymentResult.failureReason ?? 'Unknown' };
    }

    // 6. Mark order as paid
    order.markPaid(paymentResult.transactionId);

    // 7. Reserve inventory
    await this.inventoryService.reserve(order.id, command.items);

    // 8. Persist order
    await this.orderRepository.save(order);

    // 9. Publish domain events
    await this.eventPublisher.publishAll(order.pullEvents());

    // 10. Return result
    return {
      orderId: order.id.value,
      total: order.total.amount,
      currency: order.total.currency,
    };
  }
}
```

## Test Template

```typescript
// src/application/use-cases/PlaceOrder/PlaceOrder.test.ts

import { describe, test, expect, beforeEach } from 'bun:test';
import { PlaceOrderUseCase, PlaceOrderCommand } from './PlaceOrder';
import { FakeOrderRepository } from '../../../infrastructure/persistence/__fakes__/FakeOrderRepository';
import { FakeCustomerRepository } from '../../../infrastructure/persistence/__fakes__/FakeCustomerRepository';
import { FakeInventoryService } from '../../../infrastructure/external/__fakes__/FakeInventoryService';
import { FakePaymentGateway } from '../../../infrastructure/external/__fakes__/FakePaymentGateway';
import { FakeEventPublisher } from '../../../infrastructure/external/__fakes__/FakeEventPublisher';

describe('PlaceOrderUseCase', () => {
  let useCase: PlaceOrderUseCase;
  let orderRepository: FakeOrderRepository;
  let customerRepository: FakeCustomerRepository;
  let inventoryService: FakeInventoryService;
  let paymentGateway: FakePaymentGateway;
  let eventPublisher: FakeEventPublisher;

  beforeEach(() => {
    orderRepository = new FakeOrderRepository();
    customerRepository = new FakeCustomerRepository();
    inventoryService = new FakeInventoryService();
    paymentGateway = new FakePaymentGateway();
    eventPublisher = new FakeEventPublisher();

    useCase = new PlaceOrderUseCase(
      orderRepository,
      customerRepository,
      inventoryService,
      paymentGateway,
      eventPublisher
    );
  });

  const validCommand: PlaceOrderCommand = {
    customerId: 'customer-123',
    items: [{ productId: 'product-1', quantity: 2 }],
    paymentMethodId: 'pm-123',
  };

  test('successfully places order', async () => {
    // Arrange
    customerRepository.add({ id: 'customer-123', name: 'Test' });
    inventoryService.setAvailable('product-1', 10);
    paymentGateway.willSucceed();

    // Act
    const result = await useCase.execute(validCommand);

    // Assert
    expect('orderId' in result).toBe(true);
    expect(orderRepository.savedOrders).toHaveLength(1);
    expect(eventPublisher.publishedEvents).toHaveLength(1);
  });

  test('returns error when customer not found', async () => {
    // Arrange - no customer added

    // Act
    const result = await useCase.execute(validCommand);

    // Assert
    expect(result).toEqual({ type: 'CUSTOMER_NOT_FOUND' });
  });

  test('returns error when inventory insufficient', async () => {
    // Arrange
    customerRepository.add({ id: 'customer-123', name: 'Test' });
    inventoryService.setAvailable('product-1', 1); // Only 1 available, need 2

    // Act
    const result = await useCase.execute(validCommand);

    // Assert
    expect(result).toEqual({
      type: 'INSUFFICIENT_INVENTORY',
      productId: 'product-1',
      available: 1,
      requested: 2,
    });
  });

  test('returns error when payment fails', async () => {
    // Arrange
    customerRepository.add({ id: 'customer-123', name: 'Test' });
    inventoryService.setAvailable('product-1', 10);
    paymentGateway.willFail('Card declined');

    // Act
    const result = await useCase.execute(validCommand);

    // Assert
    expect(result).toEqual({
      type: 'PAYMENT_FAILED',
      reason: 'Card declined',
    });
  });
});
```

## Fake Implementation Template

```typescript
// src/infrastructure/persistence/__fakes__/FakeOrderRepository.ts

import type { Order, OrderId } from '../../../domain';
import type { OrderRepository } from '../../../application/ports/outbound';

export class FakeOrderRepository implements OrderRepository {
  public savedOrders: Order[] = [];
  private orders = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.savedOrders.push(order);
    this.orders.set(order.id.value, order);
  }

  async findById(id: OrderId): Promise<Order | null> {
    return this.orders.get(id.value) ?? null;
  }

  async findByCustomer(): Promise<Order[]> {
    return Array.from(this.orders.values());
  }

  async findPending(): Promise<Order[]> {
    return Array.from(this.orders.values()).filter(
      o => o.status === 'pending'
    );
  }

  async delete(id: OrderId): Promise<void> {
    this.orders.delete(id.value);
  }

  async exists(id: OrderId): Promise<boolean> {
    return this.orders.has(id.value);
  }

  // Test helpers
  clear(): void {
    this.savedOrders = [];
    this.orders.clear();
  }
}
```
