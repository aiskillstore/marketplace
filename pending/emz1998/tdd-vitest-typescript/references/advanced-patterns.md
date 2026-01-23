# Advanced Testing Patterns

This reference provides advanced patterns for complex testing scenarios with Vitest and TypeScript.

## Testing Patterns by Domain

### State Management Testing

```typescript
import { describe, it, expect, beforeEach } from 'vitest';

describe('State Store', () => {
  let store: StateStore;

  beforeEach(() => {
    store = new StateStore();
  });

  it('updates state immutably', () => {
    const initialState = store.getState();
    store.update({ count: 1 });
    const newState = store.getState();
    
    expect(newState).not.toBe(initialState);
    expect(newState.count).toBe(1);
  });

  it('notifies subscribers on state change', () => {
    const listener = vi.fn();
    store.subscribe(listener);
    
    store.update({ count: 1 });
    
    expect(listener).toHaveBeenCalledWith(
      expect.objectContaining({ count: 1 }),
      expect.any(Object)
    );
  });
});
```

### Event-Driven Architecture

```typescript
describe('Event Bus', () => {
  let eventBus: EventBus;

  beforeEach(() => {
    eventBus = new EventBus();
  });

  it('delivers events to all subscribers', () => {
    const handler1 = vi.fn();
    const handler2 = vi.fn();
    
    eventBus.on('test-event', handler1);
    eventBus.on('test-event', handler2);
    
    eventBus.emit('test-event', { data: 'test' });
    
    expect(handler1).toHaveBeenCalledWith({ data: 'test' });
    expect(handler2).toHaveBeenCalledWith({ data: 'test' });
  });

  it('allows unsubscribing from events', () => {
    const handler = vi.fn();
    const unsubscribe = eventBus.on('test-event', handler);
    
    unsubscribe();
    eventBus.emit('test-event');
    
    expect(handler).not.toHaveBeenCalled();
  });
});
```

### Repository Pattern

```typescript
describe('UserRepository', () => {
  let repository: UserRepository;
  let mockDb: MockDatabase;

  beforeEach(() => {
    mockDb = createMockDatabase();
    repository = new UserRepository(mockDb);
  });

  describe('findById', () => {
    it('returns user when found', async () => {
      const mockUser = { id: 1, name: 'John' };
      mockDb.query.mockResolvedValue([mockUser]);
      
      const result = await repository.findById(1);
      
      expect(result).toEqual(mockUser);
      expect(mockDb.query).toHaveBeenCalledWith(
        'SELECT * FROM users WHERE id = ?',
        [1]
      );
    });

    it('returns null when not found', async () => {
      mockDb.query.mockResolvedValue([]);
      
      const result = await repository.findById(999);
      
      expect(result).toBeNull();
    });
  });
});
```

### Builder Pattern for Test Data

```typescript
class UserBuilder {
  private user: Partial<User> = {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    role: 'user',
    isActive: true,
  };

  withId(id: number): this {
    this.user.id = id;
    return this;
  }

  withEmail(email: string): this {
    this.user.email = email;
    return this;
  }

  asAdmin(): this {
    this.user.role = 'admin';
    return this;
  }

  inactive(): this {
    this.user.isActive = false;
    return this;
  }

  build(): User {
    return this.user as User;
  }
}

// Usage in tests
describe('User permissions', () => {
  it('allows admin to delete posts', () => {
    const admin = new UserBuilder().asAdmin().build();
    expect(canDeletePost(admin, post)).toBe(true);
  });

  it('prevents inactive users from posting', () => {
    const user = new UserBuilder().inactive().build();
    expect(canCreatePost(user)).toBe(false);
  });
});
```

## Advanced Mocking Strategies

### Factory Function Mocking

```typescript
// Module: userFactory.ts
export function createUser(data: UserData): User {
  return {
    id: generateId(),
    createdAt: new Date(),
    ...data,
  };
}

// Test
import { vi } from 'vitest';
import * as userFactory from './userFactory';

vi.mock('./userFactory', () => ({
  createUser: vi.fn((data) => ({
    id: 'test-id',
    createdAt: new Date('2024-01-01'),
    ...data,
  })),
}));

it('creates user with predictable ID', () => {
  const user = createUserAccount({ name: 'John' });
  expect(user.id).toBe('test-id');
});
```

### Class Mocking

```typescript
import { vi } from 'vitest';

// Create mock class implementation
class MockEmailService {
  send = vi.fn().mockResolvedValue({ success: true });
  validate = vi.fn().mockReturnValue(true);
}

describe('User Service', () => {
  let emailService: MockEmailService;
  let userService: UserService;

  beforeEach(() => {
    emailService = new MockEmailService();
    userService = new UserService(emailService);
  });

  it('sends welcome email on registration', async () => {
    await userService.register({ email: 'test@example.com' });
    
    expect(emailService.send).toHaveBeenCalledWith({
      to: 'test@example.com',
      subject: 'Welcome',
      body: expect.any(String),
    });
  });
});
```

### Conditional Mock Behavior

```typescript
describe('API with retry logic', () => {
  it('retries on failure then succeeds', async () => {
    const mockFetch = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ data: 'success' });

    const result = await fetchWithRetry(mockFetch);
    
    expect(mockFetch).toHaveBeenCalledTimes(3);
    expect(result).toEqual({ data: 'success' });
  });
});
```

### Mocking Date/Time

```typescript
import { vi } from 'vitest';

describe('time-dependent features', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('expires session after timeout', () => {
    const session = new Session();
    expect(session.isValid()).toBe(true);
    
    vi.advanceTimersByTime(30 * 60 * 1000); // 30 minutes
    
    expect(session.isValid()).toBe(false);
  });

  it('schedules callback for future', () => {
    const callback = vi.fn();
    scheduleTask(callback, 1000);
    
    expect(callback).not.toHaveBeenCalled();
    vi.advanceTimersByTime(1000);
    expect(callback).toHaveBeenCalled();
  });
});
```

## Testing Async Patterns

### Promise Chains

```typescript
describe('promise chains', () => {
  it('processes data through multiple steps', async () => {
    const result = await fetchUser(1)
      .then(user => loadProfile(user.id))
      .then(profile => enhanceProfile(profile));
    
    expect(result.enhanced).toBe(true);
  });

  it('handles rejection in chain', async () => {
    await expect(
      fetchUser(-1)
        .then(user => loadProfile(user.id))
    ).rejects.toThrow('User not found');
  });
});
```

### Parallel Async Operations

```typescript
describe('parallel operations', () => {
  it('fetches multiple resources concurrently', async () => {
    const [users, posts, comments] = await Promise.all([
      fetchUsers(),
      fetchPosts(),
      fetchComments(),
    ]);
    
    expect(users).toHaveLength(10);
    expect(posts).toHaveLength(50);
    expect(comments).toHaveLength(200);
  });

  it('handles partial failures with allSettled', async () => {
    const results = await Promise.allSettled([
      fetchUsers(),
      fetchPosts(), // This fails
      fetchComments(),
    ]);
    
    expect(results[0].status).toBe('fulfilled');
    expect(results[1].status).toBe('rejected');
    expect(results[2].status).toBe('fulfilled');
  });
});
```

### Testing Race Conditions

```typescript
describe('concurrent access', () => {
  it('handles simultaneous updates correctly', async () => {
    const resource = new SharedResource();
    
    const updates = await Promise.all([
      resource.update({ field: 'value1' }),
      resource.update({ field: 'value2' }),
      resource.update({ field: 'value3' }),
    ]);
    
    // Verify last update wins or optimistic locking works
    const final = await resource.read();
    expect(['value1', 'value2', 'value3']).toContain(final.field);
  });
});
```

## Testing Error Boundaries

### Custom Error Types

```typescript
class ValidationError extends Error {
  constructor(
    message: string,
    public field: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

describe('form validation', () => {
  it('throws ValidationError for invalid email', () => {
    expect(() => validateEmail('invalid'))
      .toThrow(ValidationError);
  });

  it('includes field name in error', () => {
    try {
      validateEmail('invalid');
    } catch (error) {
      expect(error).toBeInstanceOf(ValidationError);
      expect((error as ValidationError).field).toBe('email');
    }
  });
});
```

### Error Recovery

```typescript
describe('error recovery', () => {
  it('falls back to default on error', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));
    
    const result = await fetchWithFallback(mockFetch, 'default value');
    
    expect(result).toBe('default value');
  });

  it('logs errors for monitoring', async () => {
    const logger = vi.fn();
    const service = new Service({ logger });
    
    await service.processWithErrorHandling(invalidData);
    
    expect(logger).toHaveBeenCalledWith(
      expect.objectContaining({
        level: 'error',
        message: expect.any(String),
      })
    );
  });
});
```

## Performance Testing

### Timing Assertions

```typescript
describe('performance requirements', () => {
  it('completes within time limit', async () => {
    const start = performance.now();
    
    await processLargeDataset(data);
    
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(1000); // Under 1 second
  });
});
```

### Memory Leak Detection

```typescript
describe('memory management', () => {
  it('cleans up resources after use', () => {
    const resource = new ExpensiveResource();
    const initialMemory = process.memoryUsage().heapUsed;
    
    resource.doWork();
    resource.dispose();
    
    global.gc(); // Requires --expose-gc flag
    const finalMemory = process.memoryUsage().heapUsed;
    
    expect(finalMemory).toBeLessThan(initialMemory * 1.1);
  });
});
```

## Snapshot Testing

### When to Use Snapshots

```typescript
describe('component rendering', () => {
  it('matches snapshot for default state', () => {
    const rendered = renderComponent(<UserCard user={testUser} />);
    expect(rendered).toMatchSnapshot();
  });

  it('matches snapshot for loading state', () => {
    const rendered = renderComponent(<UserCard loading />);
    expect(rendered).toMatchSnapshot();
  });
});
```

### Inline Snapshots

```typescript
it('formats currency correctly', () => {
  expect(formatCurrency(1234.56, 'USD')).toMatchInlineSnapshot(
    `"$1,234.56"`
  );
});
```

## Test Organization Strategies

### Page Object Pattern (for UI/API testing)

```typescript
class UserPage {
  constructor(private client: TestClient) {}

  async createUser(data: UserData) {
    return this.client.post('/users', data);
  }

  async getUser(id: number) {
    return this.client.get(`/users/${id}`);
  }

  async updateUser(id: number, data: Partial<UserData>) {
    return this.client.patch(`/users/${id}`, data);
  }
}

describe('User API', () => {
  let userPage: UserPage;

  beforeEach(() => {
    userPage = new UserPage(createTestClient());
  });

  it('performs full user lifecycle', async () => {
    const created = await userPage.createUser({ name: 'John' });
    const fetched = await userPage.getUser(created.id);
    expect(fetched.name).toBe('John');
  });
});
```

### Shared Test Helpers

```typescript
// testHelpers.ts
export function expectValidUser(user: any) {
  expect(user).toMatchObject({
    id: expect.any(Number),
    email: expect.stringMatching(/^.+@.+\..+$/),
    createdAt: expect.any(Date),
  });
}

export function expectValidationError(error: any, field: string) {
  expect(error).toBeInstanceOf(ValidationError);
  expect(error.field).toBe(field);
}

// In tests
it('creates valid user', async () => {
  const user = await createUser(validData);
  expectValidUser(user);
});
```

## Database Testing

### In-Memory Database

```typescript
import { beforeEach, afterEach } from 'vitest';

describe('database operations', () => {
  let db: TestDatabase;

  beforeEach(async () => {
    db = await TestDatabase.create(':memory:');
    await db.migrate();
  });

  afterEach(async () => {
    await db.close();
  });

  it('persists user to database', async () => {
    const user = await db.users.create({ name: 'John' });
    const found = await db.users.findById(user.id);
    expect(found?.name).toBe('John');
  });
});
```

### Transaction Testing

```typescript
describe('transactions', () => {
  it('rolls back on error', async () => {
    await expect(async () => {
      await db.transaction(async (tx) => {
        await tx.users.create({ name: 'John' });
        throw new Error('Rollback');
      });
    }).rejects.toThrow();

    const users = await db.users.findAll();
    expect(users).toHaveLength(0);
  });
});
```

## Contract Testing

```typescript
describe('API contract', () => {
  it('matches expected response schema', async () => {
    const response = await fetchUser(1);
    
    expect(response).toMatchObject({
      id: expect.any(Number),
      name: expect.any(String),
      email: expect.any(String),
      profile: expect.objectContaining({
        bio: expect.any(String),
        avatar: expect.any(String),
      }),
    });
  });
});
```
