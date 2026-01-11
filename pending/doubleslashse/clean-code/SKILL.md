# Clean Code Skill for Node.js/TypeScript

## Overview
Clean code principles adapted for TypeScript-first, functional development.

## DRY - Don't Repeat Yourself

### Principle
Every piece of knowledge should have a single, unambiguous representation.

### Violations

```typescript
// Bad: Duplicated validation logic
const validateUserEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

// Bad: Magic numbers everywhere
if (password.length < 8) { ... }
if (retries > 3) { ... }
if (timeout > 30000) { ... }
```

### Correct

```typescript
// Good: Single source of truth
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const validateEmail = (email: string): boolean => EMAIL_REGEX.test(email);

// Good: Named constants
const PASSWORD_MIN_LENGTH = 8;
const MAX_RETRIES = 3;
const REQUEST_TIMEOUT_MS = 30_000;

if (password.length < PASSWORD_MIN_LENGTH) { ... }
if (retries > MAX_RETRIES) { ... }
if (timeout > REQUEST_TIMEOUT_MS) { ... }
```

### Extract Shared Logic

```typescript
// Before: Duplicated fetch logic
const fetchUsers = async () => {
  const response = await fetch('/api/users');
  if (!response.ok) throw new Error('Failed to fetch');
  return response.json();
};

const fetchOrders = async () => {
  const response = await fetch('/api/orders');
  if (!response.ok) throw new Error('Failed to fetch');
  return response.json();
};

// After: Extracted common logic
const fetchJson = async <T>(url: string): Promise<T> => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to fetch: ${url}`);
  return response.json();
};

const fetchUsers = () => fetchJson<User[]>('/api/users');
const fetchOrders = () => fetchJson<Order[]>('/api/orders');
```

## KISS - Keep It Simple

### Principle
Prefer simple solutions over clever ones. Complexity should be justified.

### Violations

```typescript
// Bad: Overly clever one-liner
const transform = (arr: number[]) =>
  arr.reduce((acc, val, idx) => ({ ...acc, [idx]: val ** 2 }), {});

// Bad: Premature abstraction
interface DataTransformer<T, U> {
  transform(input: T): U;
  validate(input: T): boolean;
  normalize(input: T): T;
}

class UserNameTransformer implements DataTransformer<User, string> {
  // 50 lines for a simple name extraction...
}
```

### Correct

```typescript
// Good: Clear and readable
const squareValues = (arr: number[]): Record<number, number> => {
  const result: Record<number, number> = {};
  for (let i = 0; i < arr.length; i++) {
    result[i] = arr[i] ** 2;
  }
  return result;
};

// Good: Simple function for simple task
const getUserFullName = (user: User): string =>
  `${user.firstName} ${user.lastName}`;
```

### Simplify Conditionals

```typescript
// Before: Complex nested conditions
const getDiscount = (user: User, order: Order) => {
  if (user.isPremium) {
    if (order.total > 100) {
      if (order.items.length > 5) {
        return 0.25;
      }
      return 0.20;
    }
    return 0.15;
  } else {
    if (order.total > 200) {
      return 0.10;
    }
    return 0;
  }
};

// After: Early returns, clear conditions
const getDiscount = (user: User, order: Order): number => {
  if (!user.isPremium) {
    return order.total > 200 ? 0.10 : 0;
  }

  if (order.total <= 100) return 0.15;
  if (order.items.length > 5) return 0.25;
  return 0.20;
};
```

## YAGNI - You Aren't Gonna Need It

### Principle
Don't build features until they're actually needed.

### Violations

```typescript
// Bad: Configurable everything "just in case"
interface UserServiceConfig {
  maxRetries: number;
  retryDelay: number;
  cacheEnabled: boolean;
  cacheTTL: number;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
  metricsEnabled: boolean;
  circuitBreakerThreshold: number;
  // ... 20 more options never used
}

// Bad: Premature generalization
const createGenericCRUDService = <T extends Entity>(
  repository: Repository<T>,
  validator: Validator<T>,
  transformer: Transformer<T>,
  hooks: Hooks<T>,
  cache: Cache<T>,
) => { ... };
// Used only for User entity
```

### Correct

```typescript
// Good: Build what you need now
const createUserService = (db: Database) => ({
  findById: (id: string) => db.users.findFirst({ where: { id } }),
  create: (data: CreateUserData) => db.users.create({ data }),
});

// Good: Add features when needed
// v1: Simple implementation
const fetchData = async (url: string) => {
  const response = await fetch(url);
  return response.json();
};

// v2: Add retry only when you actually need it
const fetchDataWithRetry = async (url: string, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      return response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
    }
  }
};
```

## Clean Code Checklist

### Naming

```typescript
// Bad
const d = new Date();
const u = getUser();
const doStuff = () => { ... };

// Good
const createdAt = new Date();
const currentUser = getUser();
const sendNotification = () => { ... };
```

### Functions

```typescript
// Bad: Does multiple things
const processUser = async (user: User) => {
  // Validate
  // Transform
  // Save
  // Notify
  // Log
  // 100 lines...
};

// Good: Single purpose, small
const validateUser = (user: User): Result<User, ValidationError> => { ... };
const saveUser = (db: Database) => (user: User): Promise<User> => { ... };
const notifyUser = (notifier: Notifier) => (user: User): Promise<void> => { ... };
```

### Error Handling

```typescript
// Bad: Swallowing errors
try {
  await riskyOperation();
} catch (e) {
  console.log('error');
}

// Bad: Generic error
throw new Error('Something went wrong');

// Good: Typed errors with context
type OperationError =
  | { code: 'VALIDATION_FAILED'; field: string; message: string }
  | { code: 'NOT_FOUND'; resourceId: string }
  | { code: 'PERMISSION_DENIED'; userId: string; action: string };

const performOperation = (): Result<Data, OperationError> => {
  if (!isValid(input)) {
    return Result.fail({
      code: 'VALIDATION_FAILED',
      field: 'email',
      message: 'Invalid email format',
    });
  }
  // ...
};
```

### Comments

```typescript
// Bad: Obvious comments
// Increment counter
counter++;

// Add user to array
users.push(user);

// Good: Explain WHY, not WHAT
// Skip validation for admin users per security policy SEC-123
if (user.role === 'admin') return true;

// Using insertion sort because array is nearly sorted (< 10 elements typically)
insertionSort(items);
```

### Formatting

```typescript
// Bad: Inconsistent, hard to scan
const config={debug:true,timeout:1000,retries:3};

// Good: Consistent, easy to scan
const config = {
  debug: true,
  timeout: 1000,
  retries: 3,
};
```

## Code Organization

### Layered Structure

```
src/
  api/                 # HTTP layer (Express/Fastify handlers)
    routes/
    middleware/
  services/            # Business logic (pure when possible)
  repositories/        # Data access
  types/               # Shared type definitions
  utils/               # Pure utility functions
```

### Pure Core, Impure Shell

```typescript
// Pure core - easy to test
const calculateOrderTotal = (items: OrderItem[]): number =>
  items.reduce((sum, item) => sum + item.price * item.quantity, 0);

const validateOrder = (order: Order): Result<Order, ValidationError> => {
  if (!order.items.length) return Result.fail({ code: 'EMPTY_ORDER' });
  return Result.ok(order);
};

// Impure shell - handles I/O
const createOrderHandler = (deps: Dependencies) =>
  async (req: Request, res: Response) => {
    const validation = validateOrder(req.body);
    if (validation.isFailure) {
      return res.status(400).json(validation.error);
    }

    const total = calculateOrderTotal(validation.value.items);
    const saved = await deps.orderRepo.save({ ...validation.value, total });

    return res.status(201).json(saved);
  };
```
