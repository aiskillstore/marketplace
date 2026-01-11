# SOLID Principles: Real-World Examples

## E-Commerce Order System Refactoring

### Before: SOLID Violations

```typescript
// violations.ts - Everything in one place
import { prisma } from './db';
import { sendEmail } from './email';
import { stripe } from './stripe';

class OrderService {
  // SRP Violation: Handles validation, payment, persistence, notification
  async createOrder(userId: string, items: CartItem[]) {
    // Validation inline
    if (!items.length) {
      throw new Error('Cart is empty');
    }

    for (const item of items) {
      if (item.quantity <= 0) {
        throw new Error('Invalid quantity');
      }
      if (item.price < 0) {
        throw new Error('Invalid price');
      }
    }

    const user = await prisma.user.findFirst({ where: { id: userId } });
    if (!user) {
      throw new Error('User not found');
    }

    // Calculate total inline
    const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    // Apply discount - OCP Violation: Must modify to add discounts
    let discount = 0;
    if (user.membershipType === 'gold') {
      discount = total * 0.15;
    } else if (user.membershipType === 'silver') {
      discount = total * 0.10;
    } else if (user.membershipType === 'bronze') {
      discount = total * 0.05;
    }

    const finalTotal = total - discount;

    // Payment - DIP Violation: Direct Stripe dependency
    const payment = await stripe.charges.create({
      amount: Math.round(finalTotal * 100),
      currency: 'usd',
      source: user.paymentMethodId,
    });

    if (payment.status !== 'succeeded') {
      throw new Error('Payment failed');
    }

    // Save order - DIP Violation: Direct Prisma dependency
    const order = await prisma.order.create({
      data: {
        userId,
        items: JSON.stringify(items),
        total: finalTotal,
        paymentId: payment.id,
        status: 'completed',
      },
    });

    // Notification - DIP Violation: Direct email dependency
    await sendEmail({
      to: user.email,
      subject: 'Order Confirmation',
      body: `Your order #${order.id} has been placed.`,
    });

    return order;
  }
}
```

### After: SOLID Compliant

```typescript
// types.ts - Define abstractions
export type Result<T, E> =
  | { isSuccess: true; value: T }
  | { isSuccess: false; error: E };

export const Result = {
  ok: <T>(value: T): Result<T, never> => ({ isSuccess: true, value }),
  fail: <E>(error: E): Result<never, E> => ({ isSuccess: false, error }),
};

export type CartItem = {
  productId: string;
  quantity: number;
  price: number;
};

export type Order = {
  id: string;
  userId: string;
  items: CartItem[];
  total: number;
  status: 'pending' | 'completed' | 'failed';
};

export type User = {
  id: string;
  email: string;
  membershipType: 'gold' | 'silver' | 'bronze' | 'none';
  paymentMethodId: string;
};

// errors.ts - Typed errors
export type OrderError =
  | { code: 'EMPTY_CART' }
  | { code: 'INVALID_QUANTITY'; productId: string }
  | { code: 'INVALID_PRICE'; productId: string }
  | { code: 'USER_NOT_FOUND'; userId: string }
  | { code: 'PAYMENT_FAILED'; reason: string }
  | { code: 'SAVE_FAILED'; reason: string };
```

```typescript
// validation.ts - SRP: Only validation
import { Result, CartItem, OrderError } from './types';

export const validateCart = (
  items: CartItem[]
): Result<CartItem[], OrderError> => {
  if (!items.length) {
    return Result.fail({ code: 'EMPTY_CART' });
  }

  for (const item of items) {
    if (item.quantity <= 0) {
      return Result.fail({ code: 'INVALID_QUANTITY', productId: item.productId });
    }
    if (item.price < 0) {
      return Result.fail({ code: 'INVALID_PRICE', productId: item.productId });
    }
  }

  return Result.ok(items);
};
```

```typescript
// pricing.ts - SRP: Only pricing, OCP: Extensible strategies
import { CartItem, User } from './types';

type DiscountStrategy = (total: number) => number;

const discountStrategies: Record<string, DiscountStrategy> = {
  gold: (total) => total * 0.15,
  silver: (total) => total * 0.10,
  bronze: (total) => total * 0.05,
  none: () => 0,
};

// OCP: Easy to add new membership types
export const registerDiscountStrategy = (
  membershipType: string,
  strategy: DiscountStrategy
) => {
  discountStrategies[membershipType] = strategy;
};

export const calculateTotal = (items: CartItem[]): number =>
  items.reduce((sum, item) => sum + item.price * item.quantity, 0);

export const applyDiscount = (total: number, user: User): number => {
  const discount = discountStrategies[user.membershipType]?.(total) ?? 0;
  return total - discount;
};
```

```typescript
// repositories.ts - ISP: Focused interfaces
import { User, Order } from './types';

// ISP: Clients depend only on what they need
export type UserReader = {
  findById: (id: string) => Promise<User | null>;
};

export type OrderWriter = {
  save: (order: Omit<Order, 'id'>) => Promise<Order>;
};

// Implementations
export const createPrismaUserReader = (prisma: PrismaClient): UserReader => ({
  findById: (id) => prisma.user.findFirst({ where: { id } }),
});

export const createPrismaOrderWriter = (prisma: PrismaClient): OrderWriter => ({
  save: async (order) => prisma.order.create({ data: order }),
});
```

```typescript
// payment.ts - DIP: Abstract payment gateway
import { Result } from './types';

export type PaymentResult =
  | { success: true; paymentId: string }
  | { success: false; reason: string };

export type PaymentGateway = {
  charge: (amount: number, paymentMethodId: string) => Promise<PaymentResult>;
};

// Stripe implementation
export const createStripeGateway = (stripe: Stripe): PaymentGateway => ({
  charge: async (amount, paymentMethodId) => {
    try {
      const payment = await stripe.charges.create({
        amount: Math.round(amount * 100),
        currency: 'usd',
        source: paymentMethodId,
      });
      return payment.status === 'succeeded'
        ? { success: true, paymentId: payment.id }
        : { success: false, reason: 'Payment declined' };
    } catch (error) {
      return { success: false, reason: error.message };
    }
  },
});

// Test fake
export const createFakePaymentGateway = (): PaymentGateway => ({
  charge: async () => ({ success: true, paymentId: 'fake-payment-id' }),
});
```

```typescript
// notification.ts - DIP: Abstract notifier
export type Notifier = {
  sendOrderConfirmation: (email: string, orderId: string) => Promise<void>;
};

export const createEmailNotifier = (emailService: EmailService): Notifier => ({
  sendOrderConfirmation: async (email, orderId) => {
    await emailService.send({
      to: email,
      subject: 'Order Confirmation',
      body: `Your order #${orderId} has been placed.`,
    });
  },
});

export const createNoopNotifier = (): Notifier => ({
  sendOrderConfirmation: async () => {},
});
```

```typescript
// order-service.ts - Composed, SOLID compliant
import { Result, Order, OrderError, CartItem } from './types';
import { validateCart } from './validation';
import { calculateTotal, applyDiscount } from './pricing';
import { UserReader, OrderWriter } from './repositories';
import { PaymentGateway } from './payment';
import { Notifier } from './notification';

type OrderServiceDeps = {
  userReader: UserReader;
  orderWriter: OrderWriter;
  paymentGateway: PaymentGateway;
  notifier: Notifier;
};

export const createOrderService = (deps: OrderServiceDeps) => ({
  createOrder: async (
    userId: string,
    items: CartItem[]
  ): Promise<Result<Order, OrderError>> => {
    // Validate cart
    const validation = validateCart(items);
    if (validation.isFailure) return validation;

    // Get user
    const user = await deps.userReader.findById(userId);
    if (!user) {
      return Result.fail({ code: 'USER_NOT_FOUND', userId });
    }

    // Calculate pricing
    const subtotal = calculateTotal(items);
    const total = applyDiscount(subtotal, user);

    // Process payment
    const payment = await deps.paymentGateway.charge(total, user.paymentMethodId);
    if (!payment.success) {
      return Result.fail({ code: 'PAYMENT_FAILED', reason: payment.reason });
    }

    // Save order
    const order = await deps.orderWriter.save({
      userId,
      items,
      total,
      status: 'completed',
    });

    // Notify user (fire and forget)
    deps.notifier.sendOrderConfirmation(user.email, order.id).catch(() => {});

    return Result.ok(order);
  },
});
```

```typescript
// order-service.test.ts - Easy to test
import { createOrderService } from './order-service';

describe('OrderService', () => {
  const createTestDeps = () => ({
    userReader: {
      findById: jest.fn().mockResolvedValue({
        id: '1',
        email: 'test@example.com',
        membershipType: 'gold',
        paymentMethodId: 'pm-123',
      }),
    },
    orderWriter: {
      save: jest.fn().mockResolvedValue({ id: 'order-1' }),
    },
    paymentGateway: {
      charge: jest.fn().mockResolvedValue({ success: true, paymentId: 'pay-1' }),
    },
    notifier: {
      sendOrderConfirmation: jest.fn(),
    },
  });

  it('should create order with gold discount', async () => {
    const deps = createTestDeps();
    const service = createOrderService(deps);

    const result = await service.createOrder('1', [
      { productId: 'p1', quantity: 2, price: 100 },
    ]);

    expect(result.isSuccess).toBe(true);
    expect(deps.paymentGateway.charge).toHaveBeenCalledWith(170, 'pm-123'); // 200 - 15%
  });

  it('should return failure for empty cart', async () => {
    const deps = createTestDeps();
    const service = createOrderService(deps);

    const result = await service.createOrder('1', []);

    expect(result.isFailure).toBe(true);
    if (result.isFailure) {
      expect(result.error.code).toBe('EMPTY_CART');
    }
  });

  it('should return failure when payment fails', async () => {
    const deps = createTestDeps();
    deps.paymentGateway.charge.mockResolvedValue({
      success: false,
      reason: 'Insufficient funds',
    });
    const service = createOrderService(deps);

    const result = await service.createOrder('1', [
      { productId: 'p1', quantity: 1, price: 100 },
    ]);

    expect(result.isFailure).toBe(true);
    if (result.isFailure) {
      expect(result.error.code).toBe('PAYMENT_FAILED');
    }
  });
});
```
