# SOLID Principles for Node.js/TypeScript

## Overview
SOLID principles adapted for functional and TypeScript-first development.

## S - Single Responsibility Principle

A module/function should have only one reason to change.

### Violation
```typescript
// Bad: Does validation, processing, and notification
const processOrder = async (order: Order) => {
  // Validation
  if (!order.items.length) throw new Error('Empty order');
  if (order.total < 0) throw new Error('Invalid total');

  // Processing
  const processed = { ...order, status: 'processed' };
  await db.orders.save(processed);

  // Notification
  await emailService.send(order.userId, 'Order confirmed');

  return processed;
};
```

### Correct
```typescript
// Good: Separate responsibilities
const validateOrder = (order: Order): Result<Order, ValidationError> => {
  if (!order.items.length) return Result.fail(emptyOrderError());
  if (order.total < 0) return Result.fail(invalidTotalError());
  return Result.ok(order);
};

const saveOrder = (db: Database) =>
  async (order: Order): Promise<Order> => {
    const processed = { ...order, status: 'processed' };
    await db.orders.save(processed);
    return processed;
  };

const notifyUser = (notifier: Notifier) =>
  async (userId: string, message: string): Promise<void> => {
    await notifier.send(userId, message);
  };

// Compose in orchestrator
const processOrder = async (order: Order) => {
  const validation = validateOrder(order);
  if (validation.isFailure) return validation;

  const saved = await saveOrder(db)(validation.value);
  await notifyUser(emailService)(saved.userId, 'Order confirmed');

  return Result.ok(saved);
};
```

## O - Open/Closed Principle

Open for extension, closed for modification.

### Violation
```typescript
// Bad: Must modify function to add new discount types
const calculateDiscount = (type: string, amount: number): number => {
  if (type === 'percentage') return amount * 0.1;
  if (type === 'fixed') return 10;
  if (type === 'loyalty') return amount * 0.15;
  return 0;
};
```

### Correct
```typescript
// Good: Extend via new strategies without modifying existing code
type DiscountStrategy = (amount: number) => number;

const discountStrategies: Record<string, DiscountStrategy> = {
  percentage: (amount) => amount * 0.1,
  fixed: () => 10,
  loyalty: (amount) => amount * 0.15,
};

// Easy to extend
discountStrategies.holiday = (amount) => amount * 0.25;

const calculateDiscount = (type: string, amount: number): number =>
  discountStrategies[type]?.(amount) ?? 0;
```

## L - Liskov Substitution Principle

Subtypes must be substitutable for their base types.

### Violation
```typescript
// Bad: Square breaks Rectangle contract
class Rectangle {
  constructor(public width: number, public height: number) {}
  setWidth(w: number) { this.width = w; }
  setHeight(h: number) { this.height = h; }
  area() { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(w: number) {
    this.width = w;
    this.height = w; // Breaks expectation!
  }
}
```

### Correct
```typescript
// Good: Use composition and explicit types
type Shape = {
  area: () => number;
};

const createRectangle = (width: number, height: number): Shape => ({
  area: () => width * height,
});

const createSquare = (side: number): Shape => ({
  area: () => side * side,
});
```

## I - Interface Segregation Principle

Clients should not depend on interfaces they don't use.

### Violation
```typescript
// Bad: Fat interface
interface DataService {
  read(id: string): Promise<Data>;
  write(data: Data): Promise<void>;
  delete(id: string): Promise<void>;
  backup(): Promise<void>;
  restore(): Promise<void>;
  migrate(): Promise<void>;
}

// Client only needs read
const reportGenerator = (service: DataService) => {
  // Only uses service.read(), but depends on entire interface
};
```

### Correct
```typescript
// Good: Segregated interfaces
type Reader<T> = {
  read: (id: string) => Promise<T>;
};

type Writer<T> = {
  write: (data: T) => Promise<void>;
};

type Deletable = {
  delete: (id: string) => Promise<void>;
};

// Client depends only on what it needs
const reportGenerator = (reader: Reader<ReportData>) => {
  // Only depends on read capability
};

// Compose interfaces as needed
type DataService = Reader<Data> & Writer<Data> & Deletable;
```

## D - Dependency Inversion Principle

Depend on abstractions, not concretions.

### Violation
```typescript
// Bad: Direct dependency on implementation
import { PrismaClient } from '@prisma/client';

const createUserService = () => {
  const prisma = new PrismaClient(); // Hardcoded!

  return {
    findUser: (id: string) => prisma.user.findFirst({ where: { id } }),
  };
};
```

### Correct
```typescript
// Good: Depend on abstraction
type UserRepository = {
  findById: (id: string) => Promise<User | null>;
  save: (user: User) => Promise<User>;
};

const createUserService = (repo: UserRepository) => ({
  findUser: (id: string) => repo.findById(id),
  createUser: async (data: CreateUserData) => {
    const user = { id: generateId(), ...data };
    return repo.save(user);
  },
});

// Inject implementation
const prismaRepo: UserRepository = {
  findById: (id) => prisma.user.findFirst({ where: { id } }),
  save: (user) => prisma.user.create({ data: user }),
};

const service = createUserService(prismaRepo);
```

## SOLID in Practice

### Factory Function Pattern
```typescript
// Follows all SOLID principles
type Dependencies = {
  userRepo: UserRepository;
  orderRepo: OrderRepository;
  paymentGateway: PaymentGateway;
  logger: Logger;
};

const createOrderProcessor = (deps: Dependencies) => {
  const validateOrder = (order: Order): Result<Order, ValidationError> => {
    // Single responsibility: validation only
  };

  const processPayment = async (order: Order): Promise<Result<Payment, PaymentError>> => {
    // Single responsibility: payment only
  };

  return {
    process: async (order: Order): Promise<Result<ProcessedOrder, OrderError>> => {
      const validation = validateOrder(order);
      if (validation.isFailure) return validation;

      const payment = await processPayment(validation.value);
      if (payment.isFailure) return payment;

      // Compose results
      return Result.ok({ order: validation.value, payment: payment.value });
    },
  };
};
```

### Testing SOLID Code
```typescript
describe('OrderProcessor', () => {
  it('should process valid order', async () => {
    // Easy to test due to dependency injection
    const deps = {
      userRepo: createFakeUserRepo(),
      orderRepo: createFakeOrderRepo(),
      paymentGateway: { charge: jest.fn().mockResolvedValue(Result.ok({})) },
      logger: { info: jest.fn() },
    };

    const processor = createOrderProcessor(deps);
    const result = await processor.process(createTestOrder());

    expect(result.isSuccess).toBe(true);
  });
});
```
