# TypeScript Utility Types Guide

**Official Documentation:**
- [TypeScript Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [TypeScript 5.6 Standard Library](https://www.typescriptlang.org/docs/handbook/utility-types.html)

Complete guide to when and how to use each utility type.

---

## 1. Partial<T>

**When to use:** Make all properties optional

```typescript
// ✅ USE: For update operations
interface User {
  id: string
  name: string
  email: string
  age: number
}

function updateUser(id: string, updates: Partial<User>): User {
  const user = getUserById(id)
  return { ...user, ...updates }
}

// Usage
updateUser('1', { name: 'Alice' })           // OK
updateUser('1', { email: 'alice@example.com' })  // OK
updateUser('1', { name: 'Alice', age: 30 })  // OK

// ✅ USE: For configuration with defaults
interface Config {
  host: string
  port: number
  timeout: number
  retries: number
}

function createConfig(overrides: Partial<Config> = {}): Config {
  const defaults: Config = {
    host: 'localhost',
    port: 3000,
    timeout: 5000,
    retries: 3
  }
  return { ...defaults, ...overrides }
}

const config = createConfig({ port: 8080 })
```

**Test Required:**
```typescript
describe('Partial<T>', () => {
  it('should accept partial updates', () => {
    const updated = updateUser('1', { name: 'Alice' })
    expect(updated.name).toBe('Alice')
  })
})
```

---

## 2. Required<T>

**When to use:** Make all properties required

```typescript
// ✅ USE: Ensure all fields are provided
interface FormData {
  name?: string
  email?: string
  phone?: string
}

function submitForm(data: Required<FormData>): void {
  // All fields are guaranteed to exist
  console.log(data.name.toUpperCase())
  console.log(data.email.toLowerCase())
  console.log(data.phone)
}

// Usage
submitForm({
  name: 'Alice',
  email: 'alice@example.com',
  phone: '123-456-7890'
})  // OK

// submitForm({ name: 'Alice' })  // Error: missing email and phone

// ✅ USE: Convert optional to required
interface PartialUser {
  id?: string
  name?: string
}

type CompleteUser = Required<PartialUser>
// { id: string; name: string }
```

---

## 3. Readonly<T>

**When to use:** Prevent mutation

```typescript
// ✅ USE: Immutable data structures
interface User {
  id: string
  name: string
  email: string
}

function createUser(data: User): Readonly<User> {
  return Object.freeze({ ...data })
}

const user = createUser({ id: '1', name: 'Alice', email: 'alice@example.com' })
// user.name = 'Bob'  // Error: Cannot assign to 'name'

// ✅ USE: Protect function parameters
function processUsers(users: readonly User[]): void {
  // users.push({ id: '2', name: 'Bob', email: 'bob@example.com' })  // Error
  users.forEach(user => console.log(user.name))  // OK
}

// ✅ USE: Configuration objects
const CONFIG: Readonly<Config> = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
}

// CONFIG.timeout = 10000  // Error
```

---

## 4. Pick<T, K>

**When to use:** Select specific properties

```typescript
// ✅ USE: API response DTOs
interface User {
  id: string
  name: string
  email: string
  password: string
  createdAt: Date
  updatedAt: Date
}

type UserPublic = Pick<User, 'id' | 'name' | 'email'>

function getUserPublic(id: string): UserPublic {
  const user = getUserById(id)
  return {
    id: user.id,
    name: user.name,
    email: user.email
  }
}

// ✅ USE: Form data subsets
type LoginForm = Pick<User, 'email' | 'password'>

function login(credentials: LoginForm): Promise<string> {
  // Only email and password available
  return authenticate(credentials.email, credentials.password)
}

// ✅ USE: Projection in queries
type UserPreview = Pick<User, 'id' | 'name'>

function getUserPreviews(): UserPreview[] {
  return db.users.findAll({
    select: ['id', 'name']
  })
}
```

**Decision Tree:**
- Need subset of properties? → Pick
- Need to exclude properties? → Omit
- Need all properties? → Use original type

---

## 5. Omit<T, K>

**When to use:** Exclude specific properties

```typescript
// ✅ USE: Remove sensitive fields
interface User {
  id: string
  name: string
  email: string
  password: string
}

type UserWithoutPassword = Omit<User, 'password'>

function getUserProfile(id: string): UserWithoutPassword {
  const user = getUserById(id)
  const { password, ...profile } = user
  return profile
}

// ✅ USE: Create from existing (without ID for creation)
type CreateUserInput = Omit<User, 'id'>

function createUser(input: CreateUserInput): User {
  return {
    id: generateId(),
    ...input
  }
}

// ✅ USE: Remove computed properties
interface Product {
  id: string
  name: string
  price: number
  tax: number
  total: number  // Computed: price + tax
}

type ProductInput = Omit<Product, 'id' | 'total'>

function createProduct(input: ProductInput): Product {
  return {
    id: generateId(),
    total: input.price + input.tax,
    ...input
  }
}
```

---

## 6. Record<K, T>

**When to use:** Object with known keys

```typescript
// ✅ USE: Dictionary/Map types
type UserRoles = Record<string, 'admin' | 'user' | 'guest'>

const roles: UserRoles = {
  'user1': 'admin',
  'user2': 'user',
  'user3': 'guest'
}

// ✅ USE: Lookup tables
type StatusCode = 200 | 400 | 404 | 500

type StatusMessages = Record<StatusCode, string>

const messages: StatusMessages = {
  200: 'OK',
  400: 'Bad Request',
  404: 'Not Found',
  500: 'Internal Server Error'
}

// ✅ USE: Group by key
type ProductsByCategory = Record<string, Product[]>

function groupByCategory(products: Product[]): ProductsByCategory {
  return products.reduce((acc, product) => {
    const category = product.category
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(product)
    return acc
  }, {} as ProductsByCategory)
}

// ✅ USE: Configuration objects
type FeatureFlags = Record<string, boolean>

const features: FeatureFlags = {
  darkMode: true,
  analytics: false,
  betaFeatures: true
}
```

---

## 7. Exclude<T, U>

**When to use:** Remove types from union

```typescript
// ✅ USE: Filter union types
type AllTypes = string | number | boolean | null | undefined

type PrimitiveTypes = Exclude<AllTypes, null | undefined>
// string | number | boolean

// ✅ USE: Remove specific values
type Action = 'create' | 'read' | 'update' | 'delete'

type ReadOnlyAction = Exclude<Action, 'create' | 'update' | 'delete'>
// 'read'

// ✅ USE: Filter function types
type MixedTypes = string | number | (() => void) | Promise<string>

type NonFunctionTypes = Exclude<MixedTypes, Function>
// string | number | Promise<string>

// ✅ USE: Create restricted types
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

type SafeHTTPMethod = Exclude<HTTPMethod, 'DELETE'>
// 'GET' | 'POST' | 'PUT' | 'PATCH'
```

---

## 8. Extract<T, U>

**When to use:** Extract matching types from union

```typescript
// ✅ USE: Filter to specific types
type MixedTypes = string | number | boolean | Date

type OnlyPrimitives = Extract<MixedTypes, string | number | boolean>
// string | number | boolean

// ✅ USE: Extract function types
type Values = string | number | (() => void) | (() => number)

type FunctionTypes = Extract<Values, Function>
// (() => void) | (() => number)

// ✅ USE: Extract by pattern
type Events =
  | { type: 'click'; x: number; y: number }
  | { type: 'keypress'; key: string }
  | { type: 'scroll'; position: number }

type MouseEvent = Extract<Events, { type: 'click' }>
// { type: 'click'; x: number; y: number }
```

---

## 9. NonNullable<T>

**When to use:** Remove null and undefined

```typescript
// ✅ USE: Ensure defined value
type MaybeString = string | null | undefined

type DefiniteString = NonNullable<MaybeString>
// string

// ✅ USE: Filter nullable values
const values: (string | null | undefined)[] = ['a', null, 'b', undefined, 'c']
const defined: string[] = values.filter((v): v is NonNullable<typeof v> => v !== null && v !== undefined)

// ✅ USE: Function return types
function getValue(): string | null {
  return Math.random() > 0.5 ? 'value' : null
}

type ValueType = NonNullable<ReturnType<typeof getValue>>
// string

// ✅ USE: API responses
interface ApiResponse<T> {
  data: T | null
  error: string | null
}

function getData<T>(response: ApiResponse<T>): NonNullable<T> {
  if (response.data === null) {
    throw new Error(response.error ?? 'Unknown error')
  }
  return response.data
}
```

---

## 10. ReturnType<T>

**When to use:** Extract function return type

```typescript
// ✅ USE: Infer return type
function createUser(name: string, email: string) {
  return {
    id: generateId(),
    name,
    email,
    createdAt: new Date()
  }
}

type User = ReturnType<typeof createUser>
// { id: string; name: string; email: string; createdAt: Date }

// ✅ USE: Generic function return
function wrapInArray<T>(value: T): T[] {
  return [value]
}

type ArrayOf<T> = ReturnType<typeof wrapInArray<T>>

// ✅ USE: Async function return
async function fetchUser(id: string) {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}

type FetchUserReturn = ReturnType<typeof fetchUser>
// Promise<any>

type UserData = Awaited<FetchUserReturn>
// any (needs type assertion or type guard)
```

---

## 11. Parameters<T>

**When to use:** Extract function parameter types

```typescript
// ✅ USE: Reuse parameter types
function createUser(name: string, email: string, age: number) {
  return { name, email, age }
}

type CreateUserParams = Parameters<typeof createUser>
// [name: string, email: string, age: number]

// ✅ USE: Wrap function with same parameters
function loggedCreateUser(...args: Parameters<typeof createUser>) {
  console.log('Creating user with:', args)
  return createUser(...args)
}

// ✅ USE: Type-safe function decorators
function memoize<T extends (...args: any[]) => any>(fn: T) {
  const cache = new Map<string, ReturnType<T>>()

  return (...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args)
    if (cache.has(key)) {
      return cache.get(key)!
    }
    const result = fn(...args)
    cache.set(key, result)
    return result
  }
}
```

---

## 12. ConstructorParameters<T>

**When to use:** Extract constructor parameter types

```typescript
// ✅ USE: Factory functions
class User {
  constructor(
    public name: string,
    public email: string,
    public age: number
  ) {}
}

type UserConstructorParams = ConstructorParameters<typeof User>
// [name: string, email: string, age: number]

function createUser(...args: UserConstructorParams): User {
  return new User(...args)
}

// ✅ USE: Dependency injection
class Service {
  constructor(private api: ApiClient, private cache: Cache) {}
}

type ServiceDeps = ConstructorParameters<typeof Service>

const deps: ServiceDeps = [new ApiClient(), new Cache()]
const service = new Service(...deps)
```

---

## 13. InstanceType<T>

**When to use:** Get instance type of class

```typescript
// ✅ USE: Factory pattern
class User {
  constructor(public name: string) {}
}

type UserInstance = InstanceType<typeof User>
// User

function createUserInstance(name: string): UserInstance {
  return new User(name)
}

// ✅ USE: Generic factories
class Repository<T> {
  constructor(private model: new () => T) {}

  create(): InstanceType<typeof this.model> {
    return new this.model()
  }
}
```

---

## 14. Awaited<T>

**When to use:** Unwrap Promise type

```typescript
// ✅ USE: Get resolved type
type AsyncString = Promise<string>
type ResolvedString = Awaited<AsyncString>
// string

// ✅ USE: Nested promises
type NestedPromise = Promise<Promise<Promise<number>>>
type Unwrapped = Awaited<NestedPromise>
// number

// ✅ USE: Function return type
async function fetchUser(): Promise<User> {
  const response = await fetch('/api/user')
  return response.json()
}

type FetchedUser = Awaited<ReturnType<typeof fetchUser>>
// User

// ✅ USE: Utility for async values
async function getValue<T>(promise: Promise<T>): Promise<Awaited<T>> {
  return await promise
}
```

---

## 15. ThisParameterType<T>

**When to use:** Extract 'this' parameter type

```typescript
// ✅ USE: Method binding
interface User {
  name: string
  greet(this: User): void
}

type UserThis = ThisParameterType<User['greet']>
// User

// ✅ USE: Ensure correct context
function bindMethod<T, F extends (this: T, ...args: any[]) => any>(
  context: ThisParameterType<F>,
  fn: F
): (...args: Parameters<F>) => ReturnType<F> {
  return fn.bind(context) as any
}
```

---

## 16. OmitThisParameter<T>

**When to use:** Remove 'this' parameter

```typescript
// ✅ USE: Standalone function from method
interface User {
  name: string
  greet(this: User, message: string): string
}

type GreetFn = OmitThisParameter<User['greet']>
// (message: string) => string

const greet: GreetFn = function(message: string) {
  return `${message}`
}
```

---

## Utility Type Decision Tree

```
Need to modify properties?
├─ Make optional → Partial<T>
├─ Make required → Required<T>
├─ Make readonly → Readonly<T>
├─ Select some → Pick<T, K>
└─ Remove some → Omit<T, K>

Need to create object type?
├─ With specific keys → Record<K, T>
└─ From union → Extract/Exclude

Need to modify union?
├─ Remove types → Exclude<T, U>
├─ Keep types → Extract<T, U>
└─ Remove null/undefined → NonNullable<T>

Need function type info?
├─ Return type → ReturnType<T>
├─ Parameters → Parameters<T>
├─ Constructor params → ConstructorParameters<T>
└─ Instance type → InstanceType<T>

Need async type?
└─ Unwrap Promise → Awaited<T>

Need method info?
├─ Get 'this' type → ThisParameterType<T>
└─ Remove 'this' → OmitThisParameter<T>
```

---

## Combining Utility Types

```typescript
// ✅ Partial update without ID
type UpdateUserInput = Partial<Omit<User, 'id'>>

// ✅ Required fields from partial type
type RequiredConfig = Required<Partial<Config>>

// ✅ Readonly array of picked properties
type ReadonlyUserPreview = Readonly<Pick<User, 'id' | 'name'>>

// ✅ Record with non-nullable values
type DefiniteRecord = Record<string, NonNullable<string | null>>

// ✅ Extract then pick
type MouseEventProps = Pick<Extract<Events, { type: 'click' }>, 'x' | 'y'>
```

---

## Test Requirements

```typescript
describe('Utility Types', () => {
  describe('Partial<T>', () => {
    it('should allow partial updates', () => {
      const update: Partial<User> = { name: 'Alice' }
      expect(update.name).toBe('Alice')
      expect(update.email).toBeUndefined()
    })
  })

  describe('Pick<T, K>', () => {
    it('should only include picked properties', () => {
      const preview: Pick<User, 'id' | 'name'> = {
        id: '1',
        name: 'Alice'
      }
      expect(preview).toHaveProperty('id')
      expect(preview).toHaveProperty('name')
      expect(preview).not.toHaveProperty('email')
    })
  })
})
```

---

## Quick Reference

| Utility Type | Purpose | Example |
|--------------|---------|---------|
| `Partial<T>` | Make optional | Update operations |
| `Required<T>` | Make required | Form validation |
| `Readonly<T>` | Prevent mutation | Immutable data |
| `Pick<T, K>` | Select properties | API DTOs |
| `Omit<T, K>` | Remove properties | Hide sensitive data |
| `Record<K, T>` | Object type | Dictionaries |
| `Exclude<T, U>` | Remove from union | Filter types |
| `Extract<T, U>` | Keep from union | Select types |
| `NonNullable<T>` | Remove null/undefined | Ensure defined |
| `ReturnType<T>` | Function return | Infer types |
| `Parameters<T>` | Function params | Wrapper functions |
| `Awaited<T>` | Unwrap Promise | Async types |
