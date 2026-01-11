# TDD Workflow Skill

## Overview
Test-Driven Development methodology for Node.js/TypeScript projects.

## The RED-GREEN-REFACTOR Cycle

### RED Phase: Design Failing Tests

Write tests BEFORE implementation:

1. **Identify Behavior**: What should the code do?
2. **Design Test Cases**: Cover all scenarios
3. **Write Tests**: Use AAA pattern
4. **Run Tests**: Confirm they FAIL
5. **Verify Failure**: Tests fail for the RIGHT reason

### GREEN Phase: Minimal Implementation

Make tests pass with minimal code:

1. **Focus**: One failing test at a time
2. **Implement**: Just enough to pass
3. **Verify**: Run tests, confirm GREEN
4. **Iterate**: Next failing test
5. **Complete**: All tests passing

### REFACTOR Phase: Improve Design

Improve code while keeping tests green:

1. **Review**: Identify code smells
2. **Plan**: Choose refactoring
3. **Apply**: Make the change
4. **Verify**: Tests still GREEN
5. **Repeat**: Until quality gates met

## AAA Pattern

```typescript
describe('Calculator', () => {
  it('should add two numbers correctly', () => {
    // Arrange - Set up test conditions
    const calculator = createCalculator();

    // Act - Execute the behavior
    const result = calculator.add(2, 3);

    // Assert - Verify the outcome
    expect(result).toBe(5);
  });
});
```

## Test Naming Convention

Format: `should {expectedBehavior} when {scenario}`

Examples:
```typescript
it('should return empty array when input is empty', ...);
it('should throw ValidationError when email is invalid', ...);
it('should emit event when state changes', ...);
```

## Test Categories

### Unit Tests
- Test pure functions and logic
- No I/O, no side effects
- Fast execution
- High isolation

```typescript
describe('validateEmail', () => {
  it('should return true for valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });
});
```

### Integration Tests
- Test module boundaries
- Include I/O operations
- Test with real (or fake) dependencies

```typescript
describe('UserService', () => {
  it('should persist user to database', async () => {
    const db = createTestDatabase();
    const service = createUserService({ db });

    await service.createUser({ email: 'test@example.com' });

    const user = await db.users.findFirst();
    expect(user.email).toBe('test@example.com');
  });
});
```

### Contract Tests
- Verify API contracts
- Type safety at boundaries
- Response shape validation

```typescript
describe('API Contract', () => {
  it('should return user with expected shape', async () => {
    const response = await api.getUser('1');

    expect(response).toMatchObject({
      id: expect.any(String),
      email: expect.any(String),
      createdAt: expect.any(Date),
    });
  });
});
```

## Test Doubles

### Stub
Returns canned data:
```typescript
const stubApi = {
  getUser: () => Promise.resolve({ id: '1', name: 'Test' }),
};
```

### Mock
Verifies interactions:
```typescript
const mockLogger = {
  info: jest.fn(),
  error: jest.fn(),
};
// Later: expect(mockLogger.info).toHaveBeenCalledWith('message');
```

### Fake
Working implementation:
```typescript
const createFakeDatabase = () => {
  const store = new Map();
  return {
    save: (entity) => store.set(entity.id, entity),
    findById: (id) => store.get(id),
  };
};
```

### Spy
Records calls:
```typescript
const spy = jest.spyOn(service, 'notify');
await service.process();
expect(spy).toHaveBeenCalledTimes(1);
```

## Test Organization

```
src/
  services/
    user-service.ts
    user-service.test.ts      # Co-located unit tests
  api/
    handlers.ts
    handlers.test.ts
tests/
  integration/                 # Integration tests
    user-flow.test.ts
  fixtures/                    # Shared test data
    users.ts
  helpers/                     # Test utilities
    test-context.ts
```

## Anti-Patterns

### Testing Implementation Details
```typescript
// Bad - testing internal state
expect(service._cache.size).toBe(1);

// Good - testing behavior
expect(service.getCachedValue('key')).toBe('value');
```

### Overly Specific Assertions
```typescript
// Bad - brittle
expect(result).toEqual({
  id: '123',
  name: 'Test',
  createdAt: new Date('2024-01-01'),
  updatedAt: new Date('2024-01-01'),
});

// Good - flexible
expect(result).toMatchObject({
  id: expect.any(String),
  name: 'Test',
});
```

### Test Interdependence
```typescript
// Bad - tests depend on order
let user;
it('should create user', () => { user = createUser(); });
it('should update user', () => { updateUser(user); }); // Depends on previous

// Good - independent tests
it('should update user', () => {
  const user = createUser();
  updateUser(user);
});
```
