# Jest Quick Reference

## Common Matchers

### Equality
```typescript
expect(value).toBe(expected);           // Strict equality (===)
expect(value).toEqual(expected);        // Deep equality
expect(value).toStrictEqual(expected);  // Deep + type equality
```

### Truthiness
```typescript
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();
```

### Numbers
```typescript
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3);
expect(value).toBeLessThan(5);
expect(value).toBeLessThanOrEqual(5);
expect(value).toBeCloseTo(0.3, 5);      // Floating point
```

### Strings
```typescript
expect(string).toMatch(/regex/);
expect(string).toContain('substring');
expect(string).toHaveLength(5);
```

### Arrays/Iterables
```typescript
expect(array).toContain(item);
expect(array).toContainEqual(item);     // Deep equality
expect(array).toHaveLength(3);
expect(array).toEqual(expect.arrayContaining([1, 2]));
```

### Objects
```typescript
expect(object).toHaveProperty('key');
expect(object).toHaveProperty('key', value);
expect(object).toMatchObject({ key: value });
expect(object).toEqual(expect.objectContaining({ key: value }));
```

### Functions/Errors
```typescript
expect(fn).toThrow();
expect(fn).toThrow(Error);
expect(fn).toThrow('error message');
expect(fn).toThrow(/regex/);
```

---

## Mock Functions

### Creating Mocks
```typescript
const mockFn = jest.fn();
const mockFn = jest.fn(() => 'default');
const mockFn = jest.fn().mockReturnValue('value');
const mockFn = jest.fn().mockResolvedValue('async');
const mockFn = jest.fn().mockRejectedValue(new Error());
```

### Mock Implementations
```typescript
mockFn.mockImplementation(fn);
mockFn.mockImplementationOnce(fn);
mockFn.mockReturnValue(value);
mockFn.mockReturnValueOnce(value);
mockFn.mockResolvedValue(value);
mockFn.mockResolvedValueOnce(value);
```

### Mock Assertions
```typescript
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenLastCalledWith(arg);
expect(mockFn).toHaveBeenNthCalledWith(1, arg);
expect(mockFn).toHaveReturnedWith(value);
```

### Mock Properties
```typescript
mockFn.mock.calls;           // [[arg1, arg2], [arg3]]
mockFn.mock.results;         // [{ type: 'return', value: 1 }]
mockFn.mock.instances;       // [mockInstance]
```

### Clearing Mocks
```typescript
mockFn.mockClear();          // Clear calls/results
mockFn.mockReset();          // Clear + remove implementation
mockFn.mockRestore();        // Restore original (spies only)
jest.clearAllMocks();
jest.resetAllMocks();
```

---

## Module Mocking

### Basic Module Mock
```typescript
jest.mock('./module');
jest.mock('./module', () => ({
  fn: jest.fn(),
  value: 'mocked',
}));
```

### Partial Mock
```typescript
jest.mock('./module', () => ({
  ...jest.requireActual('./module'),
  specificFn: jest.fn(),
}));
```

### Manual Mocks
```
__mocks__/
  moduleName.ts    // Auto-used when jest.mock('moduleName')
```

### Mocking Node Modules
```typescript
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;
```

---

## Timer Mocks

```typescript
jest.useFakeTimers();
jest.useRealTimers();

jest.advanceTimersByTime(1000);
jest.runAllTimers();
jest.runOnlyPendingTimers();
jest.advanceTimersToNextTimer();

jest.setSystemTime(new Date('2024-01-01'));
jest.getRealSystemTime();
```

---

## Async Testing

### Promises
```typescript
// Return promise
test('async', () => {
  return promise.then(data => expect(data).toBe('value'));
});

// Async/await
test('async', async () => {
  const data = await asyncFn();
  expect(data).toBe('value');
});

// Resolves/rejects
test('async', async () => {
  await expect(asyncFn()).resolves.toBe('value');
  await expect(asyncFn()).rejects.toThrow();
});
```

### Callbacks
```typescript
test('callback', done => {
  asyncFn(data => {
    expect(data).toBe('value');
    done();
  });
});
```

---

## Test Lifecycle

```typescript
beforeAll(() => {});      // Once before all tests
afterAll(() => {});       // Once after all tests
beforeEach(() => {});     // Before each test
afterEach(() => {});      // After each test
```

---

## Test Organization

```typescript
describe('group', () => {
  describe('nested', () => {
    test('test', () => {});
    it('alias for test', () => {});
  });
});

test.only('run only this', () => {});
test.skip('skip this', () => {});
test.todo('implement later');

test.each([
  [1, 2, 3],
  [2, 3, 5],
])('add(%i, %i) = %i', (a, b, expected) => {
  expect(a + b).toBe(expected);
});
```

---

## CLI Commands

```bash
# Run tests
jest
jest --watch              # Watch mode
jest --watchAll           # Watch all files
jest path/to/test         # Specific test
jest --testNamePattern="pattern"

# Debug
jest --verbose
jest --detectOpenHandles
jest --runInBand          # Sequential
jest --debug

# Coverage
jest --coverage
jest --coverageThreshold='{"global":{"lines":80}}'
jest --collectCoverageFrom='src/**/*.ts'

# Other
jest --clearCache
jest --listTests
jest --showConfig
```

---

## Configuration (jest.config.js)

```javascript
module.exports = {
  // Test environment
  testEnvironment: 'node',       // or 'jsdom'
  
  // Test files
  testMatch: ['**/*.test.ts'],
  testPathIgnorePatterns: ['/node_modules/'],
  
  // Transform
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  
  // Modules
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  
  // Setup
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  
  // Coverage
  collectCoverageFrom: ['src/**/*.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80 },
  },
};
```

---

## React Testing Library

### Queries
```typescript
// Single element (throws if not found)
getByRole, getByLabelText, getByText, getByTestId

// Single element (returns null)
queryByRole, queryByLabelText, queryByText

// Async (waits for element)
findByRole, findByLabelText, findByText

// Multiple elements
getAllByRole, queryAllByRole, findAllByRole
```

### User Events
```typescript
import userEvent from '@testing-library/user-event';

const user = userEvent.setup();
await user.click(element);
await user.type(input, 'text');
await user.clear(input);
await user.selectOptions(select, 'value');
await user.tab();
```

### Async Utilities
```typescript
await waitFor(() => expect(element).toBeVisible());
await waitForElementToBeRemoved(element);
```
