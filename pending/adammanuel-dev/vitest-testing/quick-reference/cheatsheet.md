# Vitest Testing Cheatsheet

**Quick reference for the most common Vitest patterns and matchers.**

---

## 🚀 Getting Started

```bash
# Install Vitest
npm install -D vitest

# Run tests
vitest

# Run with UI
vitest --ui

# Run with coverage
vitest --coverage

# Update snapshots
vitest -u
```

---

## 📝 Basic Test Structure

```typescript
import { describe, it, expect } from 'vitest'

describe('Feature name', () => {
  it('should do something', () => {
    // Arrange
    const input = 5

    // Act
    const result = add(input, 3)

    // Assert
    expect(result).toBe(8)
  })
})
```

---

## ✅ Essential Matchers

### Equality
```typescript
expect(value).toBe(5)                    // Strict equality (===)
expect(value).toEqual({id: 1})           // Deep equality
expect(value).toStrictEqual({id: 1})     // Strict deep equality (checks undefined)
```

### Truthiness
```typescript
expect(value).toBeTruthy()               // Truthy value
expect(value).toBeFalsy()                // Falsy value
expect(value).toBeNull()                 // null
expect(value).toBeUndefined()            // undefined
expect(value).toBeDefined()              // Not undefined
```

### Numbers
```typescript
expect(value).toBeGreaterThan(3)         // > 3
expect(value).toBeGreaterThanOrEqual(3)  // >= 3
expect(value).toBeLessThan(5)            // < 5
expect(value).toBeLessThanOrEqual(5)     // <= 5
expect(value).toBeCloseTo(0.3, 2)        // Floating point equality (2 decimal places)
expect(value).toBeNaN()                  // NaN
```

### Strings
```typescript
expect(string).toMatch(/pattern/)        // Regex match
expect(string).toMatch('substring')      // String contains
expect(string).toContain('sub')          // Contains substring
expect(string).toHaveLength(5)           // Length is 5
```

### Arrays & Iterables
```typescript
expect(array).toContain(item)            // Array contains item
expect(array).toContainEqual({id: 1})    // Array contains object (deep equality)
expect(array).toHaveLength(3)            // Length is 3
expect(array).toEqual([1, 2, 3])         // Deep equality
```

### Objects
```typescript
expect(object).toHaveProperty('key')     // Has property
expect(object).toHaveProperty('key', 'value')  // Has property with value
expect(object).toMatchObject({ name: 'John' }) // Contains subset
expect(object).toEqual({ name: 'John' })       // Exact match
```

### Exceptions
```typescript
expect(() => throwingFn()).toThrow()                    // Throws any error
expect(() => throwingFn()).toThrow('error message')     // Throws with message
expect(() => throwingFn()).toThrow(/pattern/)           // Throws with pattern
expect(() => throwingFn()).toThrow(ErrorClass)          // Throws specific error
```

### Async/Promises
```typescript
await expect(promise).resolves.toBe(value)      // Promise resolves to value
await expect(promise).rejects.toThrow()         // Promise rejects
await expect(asyncFn()).resolves.toEqual({})    // Async function resolves
```

### Negation
```typescript
expect(value).not.toBe(5)                // Negate any matcher
expect(array).not.toContain(item)        // Not in array
```

---

## 🎭 Mocking

### Mock Functions
```typescript
const mockFn = vi.fn()                          // Create mock
const mockFn = vi.fn(() => 'return value')      // With implementation
const mockFn = vi.fn().mockReturnValue(42)      // Return value
const mockFn = vi.fn().mockResolvedValue(42)    // Async return
const mockFn = vi.fn().mockRejectedValue(error) // Async error

// Assertions
expect(mockFn).toHaveBeenCalled()               // Called at least once
expect(mockFn).toHaveBeenCalledTimes(3)         // Called exactly 3 times
expect(mockFn).toHaveBeenCalledWith(arg1, arg2) // Called with specific args
expect(mockFn).toHaveBeenLastCalledWith(arg)    // Last call with args
expect(mockFn).toHaveReturnedWith(value)        // Returned specific value

// Mock implementation
mockFn.mockImplementation((x) => x * 2)         // Set implementation
mockFn.mockImplementationOnce(() => 'once')     // One-time implementation

// Clear mocks
mockFn.mockClear()                              // Clear call history
mockFn.mockReset()                              // Clear history + implementation
mockFn.mockRestore()                            // Restore original (for spies)
```

### Module Mocking
```typescript
// Mock entire module
vi.mock('./module', () => ({
  namedExport: vi.fn(),
  default: vi.fn()
}))

// Partial mock
vi.mock('./module', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    specificFunction: vi.fn()
  }
})

// Spy on existing function
vi.spyOn(object, 'method')
vi.spyOn(object, 'method').mockReturnValue(42)
```

### Timer Mocking
```typescript
vi.useFakeTimers()                              // Use fake timers
vi.useRealTimers()                              // Restore real timers

vi.setSystemTime(new Date('2024-01-01'))        // Set specific time
vi.advanceTimersByTime(1000)                    // Advance by 1 second
vi.runAllTimers()                               // Run all pending timers
vi.runOnlyPendingTimers()                       // Run only currently pending

await vi.advanceTimersByTimeAsync(1000)         // Async version
await vi.runAllTimersAsync()                    // Async version
```

---

## 🔄 Setup & Teardown

```typescript
import { beforeAll, afterAll, beforeEach, afterEach } from 'vitest'

beforeAll(async () => {
  // Runs once before all tests in the file
})

afterAll(async () => {
  // Runs once after all tests in the file
})

beforeEach(() => {
  // Runs before each test
})

afterEach(() => {
  // Runs after each test
  vi.clearAllMocks()  // Common: clear all mocks
})
```

---

## 🎨 Test Organization

### describe blocks
```typescript
describe('Feature', () => {
  describe('Sub-feature', () => {
    it('test case', () => {
      // Test
    })
  })
})
```

### Test modifiers
```typescript
it.only('runs only this test', () => {})        // Focus: only run this
it.skip('skips this test', () => {})            // Skip this test
it.todo('implement this later')                 // Mark as TODO

// Conditional
it.skipIf(condition)('test', () => {})          // Skip if condition
it.runIf(condition)('test', () => {})           // Run if condition
```

### Parameterized tests
```typescript
it.each([
  [1, 2, 3],
  [2, 3, 5],
  [3, 4, 7]
])('adds %i + %i = %i', (a, b, expected) => {
  expect(a + b).toBe(expected)
})

// With objects
it.each([
  { input: 'hello', expected: 5 },
  { input: 'world', expected: 5 }
])('length of $input is $expected', ({ input, expected }) => {
  expect(input.length).toBe(expected)
})
```

---

## ⚡ Async Testing

```typescript
// Async/await (preferred)
it('async test', async () => {
  const result = await asyncFunction()
  expect(result).toBe(expected)
})

// Promise assertions
it('promise test', async () => {
  await expect(promise).resolves.toBe(value)
  await expect(promise).rejects.toThrow()
})

// Wait for conditions
import { waitFor } from '@testing-library/react'

await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument()
})
```

---

## 📸 Snapshot Testing

```typescript
// File snapshot
it('snapshot test', () => {
  expect(component).toMatchSnapshot()
})

// Inline snapshot
it('inline snapshot', () => {
  expect(data).toMatchInlineSnapshot(`
    {
      "id": 1,
      "name": "Test",
    }
  `)
})

// Update snapshots
// Run: vitest -u
```

---

## 🎯 Custom Matchers

```typescript
// Extend expect
expect.extend({
  toBeEven(received) {
    return {
      pass: received % 2 === 0,
      message: () => `Expected ${received} to be even`
    }
  }
})

// Use custom matcher
expect(4).toBeEven()
```

---

## 🧪 Testing Library Integration

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

it('renders component', () => {
  render(<MyComponent />)

  // Query
  const button = screen.getByRole('button', { name: /submit/i })
  const input = screen.getByLabelText(/email/i)

  // Interact
  fireEvent.click(button)

  // Or with userEvent (preferred)
  const user = userEvent.setup()
  await user.click(button)
  await user.type(input, 'test@example.com')

  // Assert
  expect(button).toBeInTheDocument()
})
```

---

## 🚦 Coverage

```bash
# Run with coverage
vitest --coverage

# Coverage configuration in vite.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.test.ts', 'node_modules/']
    }
  }
})
```

---

## 🎨 Common Patterns

### Testing Error Cases
```typescript
it('throws error for invalid input', () => {
  expect(() => fn(invalidInput)).toThrow('Invalid input')
})
```

### Testing with Mocks
```typescript
it('calls API correctly', async () => {
  const mockApi = {
    get: vi.fn().mockResolvedValue({ data: 'test' })
  }

  const result = await service.fetchData(mockApi)

  expect(mockApi.get).toHaveBeenCalledWith('/endpoint')
  expect(result).toBe('test')
})
```

### Testing State Changes
```typescript
it('updates state correctly', () => {
  const obj = { count: 0 }

  obj.count++

  expect(obj.count).toBe(1)
})
```

---

## 📋 Quick Reference Links

- **Full API:** [vitest.dev/api](https://vitest.dev/api)
- **Matchers:** [vitest.dev/api/expect](https://vitest.dev/api/expect)
- **Mocking:** [vitest.dev/api/vi](https://vitest.dev/api/vi)
- **Config:** [vitest.dev/config](https://vitest.dev/config)

---

## 💡 Pro Tips

1. **Use `it.each`** for testing multiple similar cases
2. **Clear mocks** in `afterEach` to avoid test interference
3. **Use `await`** for all async operations
4. **Test behavior**, not implementation
5. **Keep tests simple** - one assertion focus per test
6. **Use descriptive test names** - describe what's being tested
7. **Run tests in watch mode** for fast feedback

---

**For detailed guidance, see:**
- [F.I.R.S.T Principles](../principles/first-principles.md)
- [AAA Pattern](../principles/aaa-pattern.md)
- [Test Doubles](../patterns/test-doubles.md)
- [Component Testing](../patterns/component-testing.md)
