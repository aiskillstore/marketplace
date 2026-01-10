# Error Testing Patterns

**Comprehensive patterns for testing error scenarios, exceptions, and edge cases.**

Error handling is critical for robust applications. Testing error scenarios ensures your code fails gracefully and provides useful feedback to users and developers.

---

## 🎯 Core Principles

### Test Error Scenarios As Thoroughly As Happy Paths

**Why:**
- Errors reveal how your system handles failure
- Poor error handling causes production incidents
- Error messages guide debugging
- Error boundaries prevent cascading failures

**What to Test:**
- Expected exceptions for invalid input
- Error messages are clear and actionable
- State remains consistent after errors
- Resources are cleaned up
- Error codes/types are correct

---

## ⚠️ Testing Synchronous Errors

### Basic Error Testing

```typescript
import { describe, it, expect } from 'vitest'

describe('Error handling', () => {
  it('throws error for invalid input', () => {
    function divide(a: number, b: number): number {
      if (b === 0) {
        throw new Error('Cannot divide by zero')
      }
      return a / b
    }

    // Wrap in arrow function for error testing
    expect(() => divide(10, 0)).toThrow()
    expect(() => divide(10, 0)).toThrow('Cannot divide by zero')
    expect(() => divide(10, 0)).toThrow(/divide by zero/)
  })

  it('throws specific error type', () => {
    class ValidationError extends Error {
      constructor(message: string) {
        super(message)
        this.name = 'ValidationError'
      }
    }

    function validateAge(age: number): void {
      if (age < 0) {
        throw new ValidationError('Age cannot be negative')
      }
    }

    expect(() => validateAge(-1)).toThrow(ValidationError)
    expect(() => validateAge(-1)).toThrow('Age cannot be negative')
  })
})
```

### Testing Error Messages

```typescript
describe('Error messages', () => {
  it('provides helpful error messages', () => {
    function withdraw(balance: number, amount: number): number {
      if (amount > balance) {
        throw new Error(
          `Insufficient funds: attempted to withdraw ${amount} but balance is ${balance}`
        )
      }
      return balance - amount
    }

    expect(() => withdraw(50, 100)).toThrow(
      'Insufficient funds: attempted to withdraw 100 but balance is 50'
    )
  })

  it('includes context in error messages', () => {
    function parseJSON(json: string, context: string): any {
      try {
        return JSON.parse(json)
      } catch (error) {
        throw new Error(`Failed to parse JSON in ${context}: ${error.message}`)
      }
    }

    expect(() => parseJSON('invalid', 'user-config'))
      .toThrow(/Failed to parse JSON in user-config/)
  })
})
```

---

## 🌐 Testing Async Errors

### Promise Rejections

```typescript
describe('Async error handling', () => {
  it('handles promise rejection', async () => {
    async function fetchUser(id: string) {
      if (id === 'invalid') {
        throw new Error('User not found')
      }
      return { id, name: 'John' }
    }

    await expect(fetchUser('invalid')).rejects.toThrow('User not found')
  })

  it('handles API errors', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'))
    global.fetch = mockFetch

    async function getData() {
      const response = await fetch('/api/data')
      if (!response.ok) throw new Error('Request failed')
      return response.json()
    }

    await expect(getData()).rejects.toThrow('Network error')
  })
})
```

### Try-Catch Testing

```typescript
describe('Try-catch error handling', () => {
  it('catches and transforms errors', async () => {
    async function safeOperation() {
      try {
        await riskyOperation()
        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.message
        }
      }
    }

    const mockRisky = vi.fn().mockRejectedValue(new Error('Operation failed'))
    global.riskyOperation = mockRisky

    const result = await safeOperation()

    expect(result).toEqual({
      success: false,
      error: 'Operation failed'
    })
  })

  it('re-throws specific errors', async () => {
    class CriticalError extends Error {}
    class RecoverableError extends Error {}

    async function operation() {
      try {
        await riskyOperation()
      } catch (error) {
        if (error instanceof CriticalError) {
          throw error // Re-throw critical errors
        }
        // Swallow recoverable errors
      }
    }

    global.riskyOperation = vi.fn().mockRejectedValue(new CriticalError('Critical'))

    await expect(operation()).rejects.toThrow(CriticalError)
  })
})
```

---

## 🔐 Testing Validation Errors

### Input Validation

```typescript
describe('Input validation', () => {
  function validateUserData(data: any): void {
    if (!data.email) {
      throw new ValidationError('Email is required')
    }
    if (!data.email.includes('@')) {
      throw new ValidationError('Invalid email format')
    }
    if (!data.password || data.password.length < 8) {
      throw new ValidationError('Password must be at least 8 characters')
    }
  }

  it('validates required fields', () => {
    expect(() => validateUserData({}))
      .toThrow('Email is required')
  })

  it('validates email format', () => {
    expect(() => validateUserData({ email: 'invalid' }))
      .toThrow('Invalid email format')
  })

  it('validates password length', () => {
    expect(() => validateUserData({
      email: 'test@example.com',
      password: 'short'
    })).toThrow('Password must be at least 8 characters')
  })

  it('passes valid data', () => {
    expect(() => validateUserData({
      email: 'test@example.com',
      password: 'SecurePass123'
    })).not.toThrow()
  })
})
```

### Multiple Validation Errors

```typescript
class ValidationResult {
  constructor(public errors: string[] = []) {}

  addError(message: string): void {
    this.errors.push(message)
  }

  isValid(): boolean {
    return this.errors.length === 0
  }
}

function validateOrder(order: any): ValidationResult {
  const result = new ValidationResult()

  if (!order.customerId) {
    result.addError('Customer ID is required')
  }
  if (!order.items || order.items.length === 0) {
    result.addError('Order must have at least one item')
  }
  if (order.total < 0) {
    result.addError('Total cannot be negative')
  }

  return result
}

describe('Order validation', () => {
  it('returns multiple validation errors', () => {
    const invalidOrder = {
      items: [],
      total: -10
    }

    const result = validateOrder(invalidOrder)

    expect(result.isValid()).toBe(false)
    expect(result.errors).toContain('Customer ID is required')
    expect(result.errors).toContain('Order must have at least one item')
    expect(result.errors).toContain('Total cannot be negative')
    expect(result.errors).toHaveLength(3)
  })

  it('returns no errors for valid order', () => {
    const validOrder = {
      customerId: 'cust-1',
      items: [{ id: '1', qty: 1 }],
      total: 100
    }

    const result = validateOrder(validOrder)

    expect(result.isValid()).toBe(true)
    expect(result.errors).toHaveLength(0)
  })
})
```

---

## 🎭 Testing Custom Error Classes

```typescript
class DomainError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message)
    this.name = 'DomainError'
  }
}

class NotFoundError extends DomainError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
  }
}

class UnauthorizedError extends DomainError {
  constructor(action: string) {
    super(`Unauthorized to ${action}`, 'UNAUTHORIZED', 401)
    this.name = 'UnauthorizedError'
  }
}

describe('Custom errors', () => {
  it('throws NotFoundError with correct properties', () => {
    function getUser(id: string) {
      throw new NotFoundError('User', id)
    }

    try {
      getUser('123')
      expect.fail('Should have thrown')
    } catch (error) {
      expect(error).toBeInstanceOf(NotFoundError)
      expect(error).toBeInstanceOf(DomainError)
      expect(error.message).toBe('User not found: 123')
      expect(error.code).toBe('NOT_FOUND')
      expect(error.statusCode).toBe(404)
    }
  })

  it('throws UnauthorizedError', () => {
    function deleteUser() {
      throw new UnauthorizedError('delete users')
    }

    expect(() => deleteUser()).toThrow(UnauthorizedError)
    expect(() => deleteUser()).toThrow('Unauthorized to delete users')
  })
})
```

---

## 🔄 Testing Error Recovery

```typescript
describe('Error recovery', () => {
  it('recovers from transient errors', async () => {
    const mockApi = vi.fn()
      .mockRejectedValueOnce(new Error('Timeout'))
      .mockResolvedValueOnce({ data: 'success' })

    async function fetchWithRetry() {
      try {
        return await mockApi()
      } catch (error) {
        // Retry once
        return await mockApi()
      }
    }

    const result = await fetchWithRetry()

    expect(result.data).toBe('success')
    expect(mockApi).toHaveBeenCalledTimes(2)
  })

  it('maintains state consistency after errors', () => {
    class BankAccount {
      constructor(public balance: number) {}

      withdraw(amount: number): void {
        if (amount > this.balance) {
          throw new Error('Insufficient funds')
        }
        this.balance -= amount
      }
    }

    const account = new BankAccount(50)

    expect(() => account.withdraw(100)).toThrow('Insufficient funds')

    // State unchanged after error
    expect(account.balance).toBe(50)
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Test all error scenarios** - invalid input, edge cases, failures
- **Verify error messages** - clear and actionable
- **Test error types** - custom error classes
- **Check state consistency** - unchanged after errors
- **Test error propagation** - errors bubble up correctly
- **Test error recovery** - retry logic, fallbacks

### ❌ Don't

- **Only test happy paths** - errors are equally important
- **Ignore error messages** - they guide debugging
- **Swallow errors silently** - always handle explicitly
- **Use generic errors** - create specific error types
- **Forget state cleanup** - ensure consistency
- **Skip edge cases** - they often cause errors

---

## 🔗 Related Patterns

- **[Async Testing](async-testing.md)** - Async error handling
- **[Black Box Testing](../strategies/black-box-testing.md)** - Test error behavior
- **[AAA Pattern](../principles/aaa-pattern.md)** - Structure error tests

---

**Next Steps:**
- Create [Custom Error Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html#extends-clauses)
- Review [Error Handling Best Practices](https://nodejs.org/en/docs/guides/error-handling/)
- Explore [API Error Testing](api-testing.md)
