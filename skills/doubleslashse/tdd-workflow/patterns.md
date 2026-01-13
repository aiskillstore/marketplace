# TDD Patterns for Node.js/TypeScript

## Test Data Builders

### Builder Pattern
```typescript
class UserBuilder {
  private user: Partial<User> = {
    id: 'test-id',
    email: 'test@example.com',
    name: 'Test User',
  };

  withEmail(email: string): this {
    this.user.email = email;
    return this;
  }

  withName(name: string): this {
    this.user.name = name;
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

// Usage
const user = new UserBuilder().withEmail('custom@test.com').build();
```

### Factory Function Pattern
```typescript
const createTestUser = (overrides: Partial<User> = {}): User => ({
  id: 'test-id',
  email: 'test@example.com',
  name: 'Test User',
  createdAt: new Date(),
  ...overrides,
});

// Usage
const user = createTestUser({ email: 'custom@test.com' });
```

### Object Mother Pattern
```typescript
const TestUsers = {
  admin: (): User => createTestUser({ role: 'admin' }),
  guest: (): User => createTestUser({ role: 'guest' }),
  withExpiredSession: (): User => createTestUser({
    sessionExpiresAt: new Date(Date.now() - 1000),
  }),
};

// Usage
const admin = TestUsers.admin();
```

## Test Context Pattern

```typescript
interface TestContext {
  db: FakeDatabase;
  logger: MockLogger;
  service: UserService;
}

const createTestContext = (): TestContext => {
  const db = createFakeDatabase();
  const logger = createMockLogger();
  const service = createUserService({ db, logger });

  return { db, logger, service };
};

describe('UserService', () => {
  let ctx: TestContext;

  beforeEach(() => {
    ctx = createTestContext();
  });

  it('should create user', async () => {
    await ctx.service.createUser({ email: 'test@example.com' });
    expect(ctx.db.users.count()).toBe(1);
  });
});
```

## Parameterized Tests

```typescript
describe('validateEmail', () => {
  const validEmails = [
    'user@example.com',
    'user.name@example.com',
    'user+tag@example.com',
  ];

  const invalidEmails = [
    '',
    'no-at-sign',
    '@no-local',
    'no-domain@',
  ];

  it.each(validEmails)('should accept valid email: %s', (email) => {
    expect(validateEmail(email).isSuccess).toBe(true);
  });

  it.each(invalidEmails)('should reject invalid email: %s', (email) => {
    expect(validateEmail(email).isFailure).toBe(true);
  });
});
```

## Async Testing Patterns

### Promise Testing
```typescript
it('should resolve with user data', async () => {
  const result = await service.fetchUser('1');
  expect(result).toEqual({ id: '1', name: 'Test' });
});

it('should reject with error for invalid id', async () => {
  await expect(service.fetchUser('invalid'))
    .rejects.toThrow('User not found');
});
```

### Event Testing
```typescript
it('should emit user.created event', async () => {
  const events: string[] = [];
  service.on('user.created', (e) => events.push(e.userId));

  await service.createUser({ email: 'test@example.com' });

  expect(events).toContain('test-user-id');
});
```

### Stream Testing
```typescript
it('should process all items from stream', async () => {
  const items: string[] = [];
  const stream = createItemStream();

  for await (const item of stream) {
    items.push(item);
  }

  expect(items).toHaveLength(10);
});
```

### Timer Testing
```typescript
describe('debounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should delay execution', () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 100);

    debounced();
    expect(fn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(1);
  });
});
```

## Fake Repository Pattern

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}

const createFakeUserRepository = (): UserRepository => {
  const store = new Map<string, User>();

  return {
    findById: async (id) => store.get(id) ?? null,
    save: async (user) => { store.set(user.id, user); },
    delete: async (id) => { store.delete(id); },
  };
};
```

## Snapshot Testing

```typescript
describe('formatReport', () => {
  it('should format report correctly', () => {
    const report = formatReport({
      title: 'Sales Report',
      items: [{ name: 'Item 1', value: 100 }],
    });

    expect(report).toMatchSnapshot();
  });
});
```

## Error Testing

```typescript
describe('error handling', () => {
  it('should return failure result for validation error', () => {
    const result = validateUser({ email: 'invalid' });

    expect(result.isFailure).toBe(true);
    expect(result.error).toMatchObject({
      code: 'VALIDATION_ERROR',
      field: 'email',
    });
  });

  it('should throw for unexpected errors', async () => {
    const db = { query: () => { throw new Error('Connection lost'); } };
    const service = createService({ db });

    await expect(service.execute())
      .rejects.toThrow('Connection lost');
  });
});
```

## Test Isolation with Dependency Injection

```typescript
// Production code
export const createOrderService = (deps: {
  db: Database;
  paymentGateway: PaymentGateway;
  notifier: Notifier;
  logger: Logger;
}) => ({
  async processOrder(order: Order) {
    deps.logger.info({ orderId: order.id }, 'Processing order');

    const payment = await deps.paymentGateway.charge(order.total);
    if (payment.failed) {
      return Result.fail(payment.error);
    }

    await deps.db.orders.save({ ...order, status: 'paid' });
    await deps.notifier.send(order.userId, 'Order confirmed');

    return Result.ok({ orderId: order.id, status: 'confirmed' });
  },
});

// Test code
describe('OrderService', () => {
  const createTestDeps = () => ({
    db: createFakeDatabase(),
    paymentGateway: { charge: jest.fn().mockResolvedValue({ success: true }) },
    notifier: { send: jest.fn() },
    logger: { info: jest.fn(), error: jest.fn() },
  });

  it('should process order successfully', async () => {
    const deps = createTestDeps();
    const service = createOrderService(deps);

    const result = await service.processOrder(createTestOrder());

    expect(result.isSuccess).toBe(true);
    expect(deps.notifier.send).toHaveBeenCalled();
  });
});
```
