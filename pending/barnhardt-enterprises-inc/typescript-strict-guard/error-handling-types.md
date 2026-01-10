# Error Handling with TypeScript

**Official Documentation:**
- [TypeScript Error Handling Best Practices](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-4.html#control-flow-analysis-of-aliased-conditions-and-discriminants)
- [Error Handling Patterns](https://kentcdodds.com/blog/get-a-catch-block-error-message-with-typescript)

Complete guide for type-safe error handling patterns.

---

## 1. Basic Error Types

```typescript
// ✅ DO: Custom error classes
class ApplicationError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message)
    this.name = 'ApplicationError'
    Object.setPrototypeOf(this, ApplicationError.prototype)
  }
}

class ValidationError extends ApplicationError {
  constructor(
    message: string,
    public field: string,
    public value: unknown
  ) {
    super(message, 'VALIDATION_ERROR', 400)
    this.name = 'ValidationError'
    Object.setPrototypeOf(this, ValidationError.prototype)
  }
}

class NotFoundError extends ApplicationError {
  constructor(
    message: string,
    public resource: string,
    public id: string
  ) {
    super(message, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
    Object.setPrototypeOf(this, NotFoundError.prototype)
  }
}

class UnauthorizedError extends ApplicationError {
  constructor(message: string = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401)
    this.name = 'UnauthorizedError'
    Object.setPrototypeOf(this, UnauthorizedError.prototype)
  }
}

// Usage
throw new ValidationError('Invalid email format', 'email', 'not-an-email')
throw new NotFoundError('User not found', 'User', '123')
throw new UnauthorizedError()
```

---

## 2. Result Type Pattern

```typescript
// ✅ DO: Result type for explicit error handling
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E }

// Helper constructors
function Ok<T>(data: T): Result<T, never> {
  return { success: true, data }
}

function Err<E>(error: E): Result<never, E> {
  return { success: false, error }
}

// Usage in functions
function parseNumber(input: string): Result<number, string> {
  const num = parseFloat(input)
  if (isNaN(num)) {
    return Err(`Invalid number: ${input}`)
  }
  return Ok(num)
}

// Consuming code
const result = parseNumber('42')

if (result.success) {
  console.log(result.data * 2)  // Type: number
} else {
  console.error(result.error)   // Type: string
}

// ✅ DO: Result utilities
function map<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U
): Result<U, E> {
  if (result.success) {
    return Ok(fn(result.data))
  }
  return result
}

function flatMap<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => Result<U, E>
): Result<U, E> {
  if (result.success) {
    return fn(result.data)
  }
  return result
}

function unwrap<T, E>(result: Result<T, E>): T {
  if (result.success) {
    return result.data
  }
  throw result.error
}

function unwrapOr<T, E>(result: Result<T, E>, defaultValue: T): T {
  return result.success ? result.data : defaultValue
}

// Usage
const doubled = map(parseNumber('42'), n => n * 2)
const value = unwrapOr(parseNumber('invalid'), 0)
```

---

## 3. Option/Maybe Type Pattern

```typescript
// ✅ DO: Option type for nullable values
type Option<T> = T | null

type Some<T> = T
type None = null

// Helper functions
function Some<T>(value: T): Some<T> {
  return value
}

function None(): None {
  return null
}

function isSome<T>(option: Option<T>): option is Some<T> {
  return option !== null
}

function isNone<T>(option: Option<T>): option is None {
  return option === null
}

// Usage
function findUser(id: string): Option<User> {
  const user = db.users.find(u => u.id === id)
  return user ?? None()
}

const maybeUser = findUser('1')

if (isSome(maybeUser)) {
  console.log(maybeUser.name)  // Type: User
}

// ✅ DO: Option utilities
function mapOption<T, U>(
  option: Option<T>,
  fn: (value: T) => U
): Option<U> {
  return isSome(option) ? fn(option) : None()
}

function flatMapOption<T, U>(
  option: Option<T>,
  fn: (value: T) => Option<U>
): Option<U> {
  return isSome(option) ? fn(option) : None()
}

function getOrElse<T>(option: Option<T>, defaultValue: T): T {
  return isSome(option) ? option : defaultValue
}

// Usage
const userName = mapOption(findUser('1'), u => u.name)
const name = getOrElse(userName, 'Unknown')
```

---

## 4. Either Type Pattern

```typescript
// ✅ DO: Either for two possible outcomes
type Either<L, R> =
  | { type: 'left'; value: L }
  | { type: 'right'; value: R }

// Helper constructors
function Left<L>(value: L): Either<L, never> {
  return { type: 'left', value }
}

function Right<R>(value: R): Either<never, R> {
  return { type: 'right', value }
}

// Type guards
function isLeft<L, R>(either: Either<L, R>): either is { type: 'left'; value: L } {
  return either.type === 'left'
}

function isRight<L, R>(either: Either<L, R>): either is { type: 'right'; value: R } {
  return either.type === 'right'
}

// Usage
function divide(a: number, b: number): Either<string, number> {
  if (b === 0) {
    return Left('Division by zero')
  }
  return Right(a / b)
}

const result = divide(10, 2)

if (isRight(result)) {
  console.log(result.value)  // Type: number
} else {
  console.error(result.value)  // Type: string
}

// ✅ DO: Either utilities
function mapEither<L, R, U>(
  either: Either<L, R>,
  fn: (value: R) => U
): Either<L, U> {
  if (isRight(either)) {
    return Right(fn(either.value))
  }
  return either
}

function mapLeft<L, R, U>(
  either: Either<L, R>,
  fn: (value: L) => U
): Either<U, R> {
  if (isLeft(either)) {
    return Left(fn(either.value))
  }
  return either
}

function fold<L, R, T>(
  either: Either<L, R>,
  onLeft: (left: L) => T,
  onRight: (right: R) => T
): T {
  if (isLeft(either)) {
    return onLeft(either.value)
  }
  return onRight(either.value)
}
```

---

## 5. Try-Catch with Type Safety

```typescript
// ✅ DO: Type-safe error catching
function tryCatch<T>(fn: () => T): Result<T, Error> {
  try {
    return Ok(fn())
  } catch (error) {
    return Err(toError(error))
  }
}

async function tryCatchAsync<T>(
  fn: () => Promise<T>
): Promise<Result<T, Error>> {
  try {
    const data = await fn()
    return Ok(data)
  } catch (error) {
    return Err(toError(error))
  }
}

// Helper to convert unknown error to Error
function toError(error: unknown): Error {
  if (error instanceof Error) {
    return error
  }
  if (typeof error === 'string') {
    return new Error(error)
  }
  return new Error('Unknown error occurred')
}

// Usage
const result = tryCatch(() => JSON.parse(invalidJson))

if (result.success) {
  console.log(result.data)
} else {
  console.error(result.error.message)
}

// ✅ DO: Typed error extraction
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'Unknown error'
}

function getErrorStack(error: unknown): string | undefined {
  if (error instanceof Error) {
    return error.stack
  }
  return undefined
}

// Usage in catch blocks
try {
  await someOperation()
} catch (error) {
  const message = getErrorMessage(error)
  const stack = getErrorStack(error)
  logger.error(message, { stack })
}
```

---

## 6. Validation with Error Accumulation

```typescript
// ✅ DO: Collect multiple errors
type ValidationResult<T> =
  | { valid: true; value: T }
  | { valid: false; errors: string[] }

interface UserInput {
  email: string
  password: string
  age: number
}

function validateUser(input: unknown): ValidationResult<UserInput> {
  const errors: string[] = []

  if (!isObject(input)) {
    return { valid: false, errors: ['Input must be an object'] }
  }

  if (!('email' in input) || typeof input.email !== 'string') {
    errors.push('Email is required and must be a string')
  } else if (!input.email.includes('@')) {
    errors.push('Email must be valid')
  }

  if (!('password' in input) || typeof input.password !== 'string') {
    errors.push('Password is required and must be a string')
  } else if (input.password.length < 8) {
    errors.push('Password must be at least 8 characters')
  }

  if (!('age' in input) || typeof input.age !== 'number') {
    errors.push('Age is required and must be a number')
  } else if (input.age < 0 || input.age > 120) {
    errors.push('Age must be between 0 and 120')
  }

  if (errors.length > 0) {
    return { valid: false, errors }
  }

  return {
    valid: true,
    value: {
      email: input.email,
      password: input.password,
      age: input.age
    }
  }
}

// Usage
const result = validateUser(inputData)

if (result.valid) {
  console.log('Valid user:', result.value)
} else {
  console.error('Validation errors:', result.errors)
}

// ✅ DO: Field-specific errors
type FieldErrors<T> = Partial<Record<keyof T, string>>

function validateUserWithFields(input: unknown): Result<UserInput, FieldErrors<UserInput>> {
  const errors: FieldErrors<UserInput> = {}

  if (!isObject(input)) {
    return Err({ email: 'Invalid input' })
  }

  if (!('email' in input) || typeof input.email !== 'string') {
    errors.email = 'Email is required'
  } else if (!input.email.includes('@')) {
    errors.email = 'Email must be valid'
  }

  if (!('password' in input) || typeof input.password !== 'string') {
    errors.password = 'Password is required'
  } else if (input.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
  }

  if (Object.keys(errors).length > 0) {
    return Err(errors)
  }

  return Ok({
    email: input.email,
    password: input.password,
    age: input.age
  })
}
```

---

## 7. Error Boundaries (React)

```typescript
// ✅ DO: Type-safe error boundary
import React, { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback: (error: Error, errorInfo: React.ErrorInfo) => ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    this.setState({ error, errorInfo })
    this.props.onError?.(error, errorInfo)
  }

  render(): ReactNode {
    if (this.state.hasError && this.state.error && this.state.errorInfo) {
      return this.props.fallback(this.state.error, this.state.errorInfo)
    }

    return this.props.children
  }
}

// Usage
<ErrorBoundary
  fallback={(error, errorInfo) => (
    <div>
      <h1>Something went wrong</h1>
      <p>{error.message}</p>
      <pre>{errorInfo.componentStack}</pre>
    </div>
  )}
  onError={(error, errorInfo) => {
    logErrorToService(error, errorInfo)
  }}
>
  <App />
</ErrorBoundary>
```

---

## 8. Async Error Handling

```typescript
// ✅ DO: Async Result pattern
async function fetchUserSafe(id: string): Promise<Result<User, Error>> {
  try {
    const response = await fetch(`/api/users/${id}`)

    if (!response.ok) {
      return Err(new Error(`HTTP ${response.status}`))
    }

    const data: unknown = await response.json()

    if (!isUser(data)) {
      return Err(new Error('Invalid user data'))
    }

    return Ok(data)
  } catch (error) {
    return Err(toError(error))
  }
}

// Usage
const result = await fetchUserSafe('1')

if (result.success) {
  console.log(result.data.name)
} else {
  console.error(result.error.message)
}

// ✅ DO: Async Either pattern
async function fetchUserEither(id: string): Promise<Either<Error, User>> {
  try {
    const response = await fetch(`/api/users/${id}`)

    if (!response.ok) {
      return Left(new Error(`HTTP ${response.status}`))
    }

    const data = await response.json()
    return Right(data)
  } catch (error) {
    return Left(toError(error))
  }
}
```

---

## 9. Error Recovery Strategies

```typescript
// ✅ DO: Retry with backoff
async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxAttempts: number
    delayMs: number
    shouldRetry?: (error: Error) => boolean
  }
): Promise<Result<T, Error>> {
  const { maxAttempts, delayMs, shouldRetry = () => true } = options

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await fn()
      return Ok(result)
    } catch (error) {
      const err = toError(error)

      if (attempt === maxAttempts || !shouldRetry(err)) {
        return Err(err)
      }

      await new Promise(resolve => setTimeout(resolve, delayMs * attempt))
    }
  }

  return Err(new Error('Max retries exceeded'))
}

// Usage
const result = await withRetry(
  () => fetchData<User>('/api/user'),
  {
    maxAttempts: 3,
    delayMs: 1000,
    shouldRetry: error => error.message.includes('timeout')
  }
)

// ✅ DO: Fallback chain
async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>
): Promise<Result<T, Error>> {
  try {
    const result = await primary()
    return Ok(result)
  } catch (primaryError) {
    try {
      const result = await fallback()
      return Ok(result)
    } catch (fallbackError) {
      return Err(toError(fallbackError))
    }
  }
}
```

---

## 10. Exhaustive Error Handling

```typescript
// ✅ DO: Discriminated union for error types
type ApiError =
  | { type: 'network'; message: string }
  | { type: 'validation'; field: string; message: string }
  | { type: 'authorization'; message: string }
  | { type: 'not_found'; resource: string; id: string }
  | { type: 'server'; statusCode: number; message: string }

function handleApiError(error: ApiError): string {
  switch (error.type) {
    case 'network':
      return `Network error: ${error.message}`

    case 'validation':
      return `Validation error on ${error.field}: ${error.message}`

    case 'authorization':
      return `Authorization error: ${error.message}`

    case 'not_found':
      return `${error.resource} with id ${error.id} not found`

    case 'server':
      return `Server error (${error.statusCode}): ${error.message}`

    default:
      // Exhaustive check - TypeScript will error if we miss a case
      const exhaustiveCheck: never = error
      throw new Error(`Unhandled error type: ${exhaustiveCheck}`)
  }
}

// ✅ DO: Error handler mapping
type ErrorHandler<E> = (error: E) => string | void

const errorHandlers: Record<ApiError['type'], ErrorHandler<any>> = {
  network: (error: Extract<ApiError, { type: 'network' }>) => {
    console.error('Network error:', error.message)
  },

  validation: (error: Extract<ApiError, { type: 'validation' }>) => {
    console.error(`Validation error on ${error.field}:`, error.message)
  },

  authorization: (error: Extract<ApiError, { type: 'authorization' }>) => {
    console.error('Authorization error:', error.message)
    // Redirect to login
  },

  not_found: (error: Extract<ApiError, { type: 'not_found' }>) => {
    console.error(`${error.resource} not found:`, error.id)
  },

  server: (error: Extract<ApiError, { type: 'server' }>) => {
    console.error(`Server error ${error.statusCode}:`, error.message)
  }
}

function handleError(error: ApiError): void {
  const handler = errorHandlers[error.type]
  handler(error)
}
```

---

## Test Requirements

```typescript
describe('Error Handling', () => {
  describe('Result type', () => {
    it('should handle success case', () => {
      const result = parseNumber('42')
      expect(result.success).toBe(true)
      if (result.success) {
        expect(result.data).toBe(42)
      }
    })

    it('should handle error case', () => {
      const result = parseNumber('invalid')
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error).toContain('Invalid number')
      }
    })
  })

  describe('Custom errors', () => {
    it('should throw ValidationError', () => {
      expect(() => {
        throw new ValidationError('Invalid email', 'email', 'bad')
      }).toThrow(ValidationError)
    })

    it('should have correct error properties', () => {
      try {
        throw new ValidationError('Invalid email', 'email', 'bad')
      } catch (error) {
        if (error instanceof ValidationError) {
          expect(error.field).toBe('email')
          expect(error.statusCode).toBe(400)
        }
      }
    })
  })
})
```

---

## Quick Reference

| Pattern | Use Case | Example |
|---------|----------|---------|
| Custom Error | Specific error types | `class ValidationError extends Error` |
| Result<T, E> | Explicit error handling | `Result<User, string>` |
| Option<T> | Nullable values | `Option<User>` |
| Either<L, R> | Two outcomes | `Either<Error, User>` |
| Try-Catch | Convert to Result | `tryCatch(() => ...)` |
| Validation | Multiple errors | `ValidationResult<T>` |
| Error Boundary | React errors | `<ErrorBoundary>` |
| Retry | Transient failures | `withRetry(fn, options)` |
| Discriminated Union | Exhaustive handling | `type ApiError = ...` |
