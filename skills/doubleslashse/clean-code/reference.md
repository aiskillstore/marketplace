# Clean Code Reference

## Naming Conventions

### Variables and Constants
```typescript
// Booleans: use is/has/can/should prefix
const isActive = true;
const hasPermission = user.role === 'admin';
const canEdit = hasPermission && isActive;
const shouldNotify = user.preferences.notifications;

// Collections: use plural nouns
const users: User[] = [];
const orderItems: OrderItem[] = [];
const userIdToOrderMap: Map<string, Order> = new Map();

// Functions: use verb + noun
const fetchUsers = () => { ... };
const calculateTotal = (items: Item[]) => { ... };
const validateEmail = (email: string) => { ... };

// Constants: SCREAMING_SNAKE_CASE for true constants
const MAX_RETRY_ATTEMPTS = 3;
const API_BASE_URL = 'https://api.example.com';
const DEFAULT_TIMEOUT_MS = 5000;
```

### Functions
```typescript
// Descriptive names that indicate behavior
const sendWelcomeEmail = (user: User) => { ... };
const parseConfigFromEnv = () => { ... };
const convertCelsiusToFahrenheit = (celsius: number) => { ... };

// Predicate functions: start with is/has/can
const isValidEmail = (email: string): boolean => { ... };
const hasRequiredPermissions = (user: User): boolean => { ... };
const canAccessResource = (user: User, resource: Resource): boolean => { ... };
```

### Types and Interfaces
```typescript
// Types: PascalCase, descriptive
type UserId = string;
type EmailAddress = string;
type OrderStatus = 'pending' | 'processing' | 'completed' | 'cancelled';

// Interfaces: describe shape, often with -able, -like suffixes for behaviors
interface Serializable {
  serialize(): string;
}

interface UserLike {
  id: string;
  email: string;
}

// Result types: clearly indicate success/failure
type CreateUserResult = Result<User, CreateUserError>;
type FetchOrdersResult = Result<Order[], FetchError>;
```

## Function Design

### Single Level of Abstraction
```typescript
// Bad: Mixed abstraction levels
const processOrder = async (order: Order) => {
  // High level
  const validated = validateOrder(order);

  // Low level implementation detail
  for (const item of order.items) {
    if (item.quantity <= 0) {
      throw new Error('Invalid quantity');
    }
  }

  // High level again
  await saveOrder(validated);
};

// Good: Consistent abstraction
const processOrder = async (order: Order) => {
  const validated = validateOrder(order);
  const priced = calculatePricing(validated);
  const saved = await saveOrder(priced);
  await notifyUser(saved);
  return saved;
};
```

### Guard Clauses
```typescript
// Bad: Deep nesting
const processUser = (user: User | null) => {
  if (user) {
    if (user.isActive) {
      if (user.hasVerifiedEmail) {
        // Do the actual work
        return doWork(user);
      } else {
        throw new Error('Email not verified');
      }
    } else {
      throw new Error('User inactive');
    }
  } else {
    throw new Error('User required');
  }
};

// Good: Guard clauses
const processUser = (user: User | null) => {
  if (!user) throw new Error('User required');
  if (!user.isActive) throw new Error('User inactive');
  if (!user.hasVerifiedEmail) throw new Error('Email not verified');

  return doWork(user);
};
```

### Small Functions
```typescript
// Bad: 100+ line function
const handleRequest = async (req: Request) => {
  // 100 lines of mixed concerns...
};

// Good: Composed small functions
const handleRequest = async (req: Request) => {
  const input = parseInput(req);
  const validated = validateInput(input);
  const processed = await processInput(validated);
  return formatResponse(processed);
};

const parseInput = (req: Request): RawInput => { /* 5-10 lines */ };
const validateInput = (input: RawInput): Result<ValidInput, Error> => { /* 5-10 lines */ };
const processInput = async (input: ValidInput): Promise<Output> => { /* 5-10 lines */ };
const formatResponse = (output: Output): Response => { /* 5-10 lines */ };
```

## Error Handling

### Typed Errors
```typescript
// Define error types
type ValidationError = {
  code: 'VALIDATION_ERROR';
  field: string;
  message: string;
};

type NotFoundError = {
  code: 'NOT_FOUND';
  resource: string;
  id: string;
};

type AuthError = {
  code: 'UNAUTHORIZED' | 'FORBIDDEN';
  reason: string;
};

type AppError = ValidationError | NotFoundError | AuthError;

// Handle exhaustively
const handleError = (error: AppError): Response => {
  switch (error.code) {
    case 'VALIDATION_ERROR':
      return { status: 400, body: { field: error.field, message: error.message } };
    case 'NOT_FOUND':
      return { status: 404, body: { message: `${error.resource} not found` } };
    case 'UNAUTHORIZED':
    case 'FORBIDDEN':
      return { status: error.code === 'UNAUTHORIZED' ? 401 : 403, body: { reason: error.reason } };
  }
};
```

### Result Pattern
```typescript
type Result<T, E> =
  | { isSuccess: true; isFailure: false; value: T }
  | { isSuccess: false; isFailure: true; error: E };

const Result = {
  ok: <T>(value: T): Result<T, never> => ({
    isSuccess: true,
    isFailure: false,
    value,
  }),
  fail: <E>(error: E): Result<never, E> => ({
    isSuccess: false,
    isFailure: true,
    error,
  }),
};

// Usage
const divide = (a: number, b: number): Result<number, 'DIVISION_BY_ZERO'> => {
  if (b === 0) return Result.fail('DIVISION_BY_ZERO');
  return Result.ok(a / b);
};

const result = divide(10, 2);
if (result.isSuccess) {
  console.log(result.value); // 5
} else {
  console.log(result.error); // 'DIVISION_BY_ZERO'
}
```

### Async Error Handling
```typescript
// Good: Explicit error handling with Result
const fetchUser = async (id: string): Promise<Result<User, FetchError>> => {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      return Result.fail({ code: 'HTTP_ERROR', status: response.status });
    }
    const data = await response.json();
    return Result.ok(data);
  } catch (error) {
    return Result.fail({ code: 'NETWORK_ERROR', message: String(error) });
  }
};

// Chain results
const processUser = async (id: string): Promise<Result<ProcessedUser, AppError>> => {
  const userResult = await fetchUser(id);
  if (userResult.isFailure) return userResult;

  const validationResult = validateUser(userResult.value);
  if (validationResult.isFailure) return validationResult;

  return Result.ok(transform(validationResult.value));
};
```

## Immutability

```typescript
// Bad: Mutation
const addItem = (cart: Cart, item: Item) => {
  cart.items.push(item); // Mutates original
  cart.total += item.price;
  return cart;
};

// Good: Immutable update
const addItem = (cart: Cart, item: Item): Cart => ({
  ...cart,
  items: [...cart.items, item],
  total: cart.total + item.price,
});

// Good: Using immer for complex updates
import { produce } from 'immer';

const addItem = (cart: Cart, item: Item): Cart =>
  produce(cart, (draft) => {
    draft.items.push(item);
    draft.total += item.price;
  });
```

## Dependency Injection

```typescript
// Bad: Hardcoded dependencies
import { db } from './database';
import { logger } from './logger';

const createUser = async (data: CreateUserData) => {
  logger.info('Creating user');
  return db.users.create({ data });
};

// Good: Injected dependencies
type Dependencies = {
  db: Database;
  logger: Logger;
};

const createUserService = (deps: Dependencies) => ({
  create: async (data: CreateUserData) => {
    deps.logger.info('Creating user');
    return deps.db.users.create({ data });
  },
});

// Wire up at composition root
const userService = createUserService({
  db: prismaClient,
  logger: pinoLogger,
});
```

## Async/Await Best Practices

```typescript
// Bad: Mixing async patterns
const fetchData = () => {
  return fetch('/api/data')
    .then((res) => res.json())
    .then((data) => {
      return new Promise((resolve) => {
        setTimeout(() => resolve(data), 100);
      });
    });
};

// Good: Consistent async/await
const fetchData = async () => {
  const response = await fetch('/api/data');
  const data = await response.json();
  await delay(100);
  return data;
};

// Good: Parallel execution when possible
const fetchAllData = async () => {
  const [users, orders, products] = await Promise.all([
    fetchUsers(),
    fetchOrders(),
    fetchProducts(),
  ]);
  return { users, orders, products };
};

// Good: Error handling
const fetchWithFallback = async <T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>
): Promise<T> => {
  try {
    return await primary();
  } catch {
    return await fallback();
  }
};
```

## Code Organization

```typescript
// File structure: group by feature
src/
  users/
    user.types.ts      // Types
    user.service.ts    // Business logic
    user.repository.ts // Data access
    user.handler.ts    // HTTP layer
    user.test.ts       // Tests
  orders/
    order.types.ts
    order.service.ts
    ...

// Barrel exports for clean imports
// users/index.ts
export { createUserService } from './user.service';
export type { User, CreateUserData } from './user.types';

// Usage
import { createUserService, User } from './users';
```
