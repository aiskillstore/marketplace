# Functional Patterns for Node.js/TypeScript

## Overview
Functional programming patterns that promote testability, composability, and maintainability.

## Pure Functions

### Definition
A pure function:
- Always returns the same output for the same input
- Has no side effects (no I/O, no mutation)

### Examples

```typescript
// Pure: Deterministic, no side effects
const add = (a: number, b: number): number => a + b;

const calculateTotal = (items: OrderItem[]): number =>
  items.reduce((sum, item) => sum + item.price * item.quantity, 0);

const filterActiveUsers = (users: User[]): User[] =>
  users.filter((user) => user.isActive);

// Impure: Has side effects
const saveUser = async (user: User): Promise<void> => {
  await database.save(user); // I/O side effect
};

const logMessage = (msg: string): void => {
  console.log(msg); // Side effect
};

const generateId = (): string => {
  return crypto.randomUUID(); // Non-deterministic
};
```

### Pure Core, Impure Shell

```typescript
// Pure core - all business logic
const validateOrder = (order: Order): Result<Order, ValidationError> => {
  if (!order.items.length) return Result.fail({ code: 'EMPTY_ORDER' });
  if (order.total < 0) return Result.fail({ code: 'INVALID_TOTAL' });
  return Result.ok(order);
};

const calculateDiscount = (order: Order, user: User): number => {
  const baseDiscount = user.isPremium ? 0.15 : 0;
  const volumeDiscount = order.items.length > 10 ? 0.05 : 0;
  return baseDiscount + volumeDiscount;
};

const applyDiscount = (order: Order, discountRate: number): Order => ({
  ...order,
  total: order.total * (1 - discountRate),
});

// Impure shell - handles I/O
const processOrderHandler = (deps: Dependencies) => async (order: Order) => {
  const validation = validateOrder(order);
  if (validation.isFailure) return validation;

  const user = await deps.userRepo.findById(order.userId); // I/O
  const discount = calculateDiscount(validation.value, user);
  const discounted = applyDiscount(validation.value, discount);

  await deps.orderRepo.save(discounted); // I/O
  await deps.notifier.send(user.email, 'Order confirmed'); // I/O

  return Result.ok(discounted);
};
```

## Immutability

### Immutable Updates

```typescript
// Bad: Mutation
const addItemToCart = (cart: Cart, item: Item) => {
  cart.items.push(item);
  cart.total += item.price;
  return cart;
};

// Good: Immutable update
const addItemToCart = (cart: Cart, item: Item): Cart => ({
  ...cart,
  items: [...cart.items, item],
  total: cart.total + item.price,
});

// Good: Nested immutable update
const updateUserAddress = (user: User, address: Partial<Address>): User => ({
  ...user,
  address: {
    ...user.address,
    ...address,
  },
});

// Good: Using readonly types
type ReadonlyUser = {
  readonly id: string;
  readonly email: string;
  readonly addresses: readonly Address[];
};

// Good: Immutable array operations
const addItem = <T>(arr: readonly T[], item: T): readonly T[] => [...arr, item];
const removeAt = <T>(arr: readonly T[], index: number): readonly T[] =>
  arr.filter((_, i) => i !== index);
const updateAt = <T>(arr: readonly T[], index: number, item: T): readonly T[] =>
  arr.map((existing, i) => (i === index ? item : existing));
```

## Function Composition

### Pipe and Compose

```typescript
// Pipe: left to right
type Fn<A, B> = (a: A) => B;

const pipe = <A, B, C>(
  f: Fn<A, B>,
  g: Fn<B, C>
): Fn<A, C> => (a) => g(f(a));

const pipe3 = <A, B, C, D>(
  f: Fn<A, B>,
  g: Fn<B, C>,
  h: Fn<C, D>
): Fn<A, D> => (a) => h(g(f(a)));

// Usage
const processInput = pipe3(
  trim,
  toLowerCase,
  validateEmail
);

// Variadic pipe
const pipeAll = <T>(...fns: Array<(x: T) => T>) =>
  (initial: T): T => fns.reduce((acc, fn) => fn(acc), initial);

const processString = pipeAll(
  (s: string) => s.trim(),
  (s: string) => s.toLowerCase(),
  (s: string) => s.replace(/\s+/g, '-')
);
```

### Higher-Order Functions

```typescript
// Function that returns a function
const withLogging = <T extends (...args: any[]) => any>(fn: T) =>
  (...args: Parameters<T>): ReturnType<T> => {
    console.log('Calling with:', args);
    const result = fn(...args);
    console.log('Result:', result);
    return result;
  };

// Function that takes a function
const retry = <T>(
  fn: () => Promise<T>,
  attempts: number = 3
): Promise<T> =>
  fn().catch((error) =>
    attempts > 1 ? retry(fn, attempts - 1) : Promise.reject(error)
  );

// Currying
const multiply = (a: number) => (b: number): number => a * b;
const double = multiply(2);
const triple = multiply(3);

// Partial application
const createLogger = (prefix: string) =>
  (message: string): void => console.log(`[${prefix}] ${message}`);

const infoLog = createLogger('INFO');
const errorLog = createLogger('ERROR');
```

## Result Pattern (Monadic Error Handling)

### Basic Result Type

```typescript
type Result<T, E> =
  | { readonly _tag: 'Ok'; readonly value: T }
  | { readonly _tag: 'Err'; readonly error: E };

const ok = <T>(value: T): Result<T, never> => ({ _tag: 'Ok', value });
const err = <E>(error: E): Result<never, E> => ({ _tag: 'Err', error });

const isOk = <T, E>(result: Result<T, E>): result is { _tag: 'Ok'; value: T } =>
  result._tag === 'Ok';

const isErr = <T, E>(result: Result<T, E>): result is { _tag: 'Err'; error: E } =>
  result._tag === 'Err';
```

### Result Operations

```typescript
// Map: transform success value
const map = <T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U
): Result<U, E> =>
  isOk(result) ? ok(fn(result.value)) : result;

// MapError: transform error value
const mapError = <T, E, F>(
  result: Result<T, E>,
  fn: (error: E) => F
): Result<T, F> =>
  isErr(result) ? err(fn(result.error)) : result;

// FlatMap (chain): compose Result-returning functions
const flatMap = <T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Result<U, E>
): Result<U, E> =>
  isOk(result) ? fn(result.value) : result;

// Match: exhaustive handling
const match = <T, E, R>(
  result: Result<T, E>,
  handlers: { ok: (value: T) => R; err: (error: E) => R }
): R =>
  isOk(result) ? handlers.ok(result.value) : handlers.err(result.error);
```

### Chaining Results

```typescript
type ValidationError = { field: string; message: string };
type ProcessingError = { code: string; details: string };
type AppError = ValidationError | ProcessingError;

const validateInput = (input: unknown): Result<ValidInput, ValidationError> => {
  // ...
};

const processData = (input: ValidInput): Result<ProcessedData, ProcessingError> => {
  // ...
};

const formatOutput = (data: ProcessedData): Output => {
  // ...
};

// Compose the pipeline
const handleRequest = (input: unknown): Result<Output, AppError> => {
  const validated = validateInput(input);
  if (isErr(validated)) return validated;

  const processed = processData(validated.value);
  if (isErr(processed)) return processed;

  return ok(formatOutput(processed.value));
};

// Or with flatMap
const handleRequestFunctional = (input: unknown): Result<Output, AppError> =>
  flatMap(validateInput(input), (valid) =>
    map(processData(valid), formatOutput)
  );
```

## Option/Maybe Pattern

```typescript
type Option<T> =
  | { readonly _tag: 'Some'; readonly value: T }
  | { readonly _tag: 'None' };

const some = <T>(value: T): Option<T> => ({ _tag: 'Some', value });
const none: Option<never> = { _tag: 'None' };

const isSome = <T>(opt: Option<T>): opt is { _tag: 'Some'; value: T } =>
  opt._tag === 'Some';

const isNone = <T>(opt: Option<T>): opt is { _tag: 'None' } =>
  opt._tag === 'None';

// Operations
const mapOption = <T, U>(opt: Option<T>, fn: (value: T) => U): Option<U> =>
  isSome(opt) ? some(fn(opt.value)) : none;

const getOrElse = <T>(opt: Option<T>, defaultValue: T): T =>
  isSome(opt) ? opt.value : defaultValue;

const fromNullable = <T>(value: T | null | undefined): Option<T> =>
  value != null ? some(value) : none;

// Usage
const findUser = (id: string): Option<User> => {
  const user = users.find((u) => u.id === id);
  return fromNullable(user);
};

const getUserEmail = (id: string): string =>
  getOrElse(
    mapOption(findUser(id), (user) => user.email),
    'unknown@example.com'
  );
```

## Dependency Injection via Functions

```typescript
// Define dependencies as a type
type Dependencies = {
  userRepo: UserRepository;
  orderRepo: OrderRepository;
  logger: Logger;
  clock: () => Date; // Even time can be injected
};

// Create service factory
const createOrderService = (deps: Dependencies) => ({
  createOrder: async (data: CreateOrderData): Promise<Result<Order, OrderError>> => {
    const user = await deps.userRepo.findById(data.userId);
    if (!user) {
      return err({ code: 'USER_NOT_FOUND', userId: data.userId });
    }

    const order: Order = {
      id: generateId(),
      ...data,
      createdAt: deps.clock(),
      status: 'pending',
    };

    deps.logger.info({ orderId: order.id }, 'Creating order');
    await deps.orderRepo.save(order);

    return ok(order);
  },
});

// Test with fake dependencies
describe('OrderService', () => {
  it('should create order', async () => {
    const deps: Dependencies = {
      userRepo: { findById: jest.fn().mockResolvedValue({ id: '1' }) },
      orderRepo: { save: jest.fn() },
      logger: { info: jest.fn() },
      clock: () => new Date('2024-01-01'),
    };

    const service = createOrderService(deps);
    const result = await service.createOrder({ userId: '1', items: [] });

    expect(isOk(result)).toBe(true);
  });
});
```
