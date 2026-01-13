# Advanced Generic Patterns

**Official Documentation:**
- [TypeScript Generics Handbook](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript 5.6 Generic Constraints](https://www.typescriptlang.org/docs/handbook/2/generics.html#generic-constraints)
- [Conditional Types Deep Dive](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)

Complete reference for advanced generic TypeScript patterns.

---

## 1. Basic Generic Functions

```typescript
// ❌ DON'T: Without generics
function firstString(arr: string[]): string | undefined {
  return arr[0]
}

function firstNumber(arr: number[]): number | undefined {
  return arr[0]
}

// ✅ DO: Single generic
function first<T>(arr: T[]): T | undefined {
  return arr[0]
}

// Usage
const num = first([1, 2, 3])      // Type: number | undefined
const str = first(['a', 'b', 'c']) // Type: string | undefined

// ✅ DO: Multiple generics
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b]
}

const p1 = pair('hello', 42)        // Type: [string, number]
const p2 = pair(true, { id: 1 })    // Type: [boolean, { id: number }]
```

---

## 2. Generic Constraints

```typescript
// ✅ DO: Constrain to object with specific property
interface HasId {
  id: string
}

function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id)
}

// Usage
interface User extends HasId {
  name: string
  email: string
}

interface Product extends HasId {
  title: string
  price: number
}

const users: User[] = [{ id: '1', name: 'Alice', email: 'alice@example.com' }]
const user = findById(users, '1')  // Type: User | undefined

const products: Product[] = [{ id: '1', title: 'Book', price: 10 }]
const product = findById(products, '1')  // Type: Product | undefined

// ✅ DO: Constrain to primitive types
function stringify<T extends string | number | boolean>(value: T): string {
  return String(value)
}

// ✅ DO: Constrain to array
function sum<T extends number[]>(numbers: T): number {
  return numbers.reduce((a, b) => a + b, 0)
}

// ✅ DO: Constrain with keyof
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key]
}

const user = { name: 'Alice', age: 30 }
const name = getProperty(user, 'name')  // Type: string
const age = getProperty(user, 'age')    // Type: number
// getProperty(user, 'invalid')          // Error
```

---

## 3. Generic Classes

```typescript
// ✅ DO: Generic data structure
class Stack<T> {
  private items: T[] = []

  push(item: T): void {
    this.items.push(item)
  }

  pop(): T | undefined {
    return this.items.pop()
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1]
  }

  get size(): number {
    return this.items.length
  }

  isEmpty(): boolean {
    return this.items.length === 0
  }
}

// Usage
const numberStack = new Stack<number>()
numberStack.push(1)
numberStack.push(2)
const top = numberStack.pop()  // Type: number | undefined

const stringStack = new Stack<string>()
stringStack.push('hello')

// ✅ DO: Generic with constraints
class Repository<T extends { id: string }> {
  private items: Map<string, T> = new Map()

  add(item: T): void {
    this.items.set(item.id, item)
  }

  get(id: string): T | undefined {
    return this.items.get(id)
  }

  getAll(): T[] {
    return Array.from(this.items.values())
  }

  delete(id: string): boolean {
    return this.items.delete(id)
  }

  update(item: T): void {
    if (this.items.has(item.id)) {
      this.items.set(item.id, item)
    }
  }
}

// Usage
interface User {
  id: string
  name: string
}

const userRepo = new Repository<User>()
userRepo.add({ id: '1', name: 'Alice' })
const user = userRepo.get('1')  // Type: User | undefined
```

---

## 4. Generic Type Inference

```typescript
// ✅ DO: Infer from parameters
function map<T, R>(items: T[], fn: (item: T) => R): R[] {
  return items.map(fn)
}

// Types inferred automatically
const numbers = [1, 2, 3]
const strings = map(numbers, n => String(n))  // R inferred as string

// ✅ DO: Infer from return type
function identity<T>(value: T): T {
  return value
}

const num = identity(42)        // T inferred as number
const str = identity('hello')   // T inferred as string

// ✅ DO: Infer array element type
function flatten<T>(arrays: T[][]): T[] {
  return arrays.flat()
}

const numbers2D = [[1, 2], [3, 4]]
const flat = flatten(numbers2D)  // Type: number[]

// ✅ DO: Default generic parameters
function createArray<T = string>(length: number, value: T): T[] {
  return Array(length).fill(value)
}

const strings2 = createArray(3, 'hello')  // Type: string[]
const numbers2 = createArray(3, 42)       // Type: number[]
const defaults = createArray(3)           // Error: value required
```

---

## 5. Conditional Types

```typescript
// ✅ DO: Extract array element type
type ElementType<T> = T extends Array<infer U> ? U : never

type StringArray = string[]
type Element = ElementType<StringArray>  // string

// ✅ DO: Extract Promise resolved type
type Awaited<T> = T extends Promise<infer U> ? Awaited<U> : T

type AsyncString = Promise<string>
type SyncString = Awaited<AsyncString>  // string

type NestedPromise = Promise<Promise<number>>
type Unwrapped = Awaited<NestedPromise>  // number

// ✅ DO: Exclude types from union
type Exclude<T, U> = T extends U ? never : T

type AllTypes = string | number | boolean
type NoStrings = Exclude<AllTypes, string>  // number | boolean

// ✅ DO: Extract types from union
type Extract<T, U> = T extends U ? T : never

type OnlyStrings = Extract<AllTypes, string>  // string

// ✅ DO: Non-nullable type
type NonNullable<T> = T extends null | undefined ? never : T

type MaybeString = string | null | undefined
type DefiniteString = NonNullable<MaybeString>  // string

// ✅ DO: Function return type
type ReturnType<T extends (...args: any[]) => any> =
  T extends (...args: any[]) => infer R ? R : never

function getUser(): User {
  return { id: '1', name: 'Alice' }
}

type UserType = ReturnType<typeof getUser>  // User

// ✅ DO: Function parameters type
type Parameters<T extends (...args: any[]) => any> =
  T extends (...args: infer P) => any ? P : never

function createUser(name: string, age: number): User {
  return { id: '1', name, age }
}

type CreateUserParams = Parameters<typeof createUser>  // [string, number]
```

---

## 6. Mapped Types

```typescript
// ✅ DO: Make all properties optional
type Partial<T> = {
  [P in keyof T]?: T[P]
}

interface User {
  id: string
  name: string
  email: string
}

type PartialUser = Partial<User>
// { id?: string; name?: string; email?: string }

// ✅ DO: Make all properties required
type Required<T> = {
  [P in keyof T]-?: T[P]
}

// ✅ DO: Make all properties readonly
type Readonly<T> = {
  readonly [P in keyof T]: T[P]
}

type ReadonlyUser = Readonly<User>
// { readonly id: string; readonly name: string; readonly email: string }

// ✅ DO: Pick specific properties
type Pick<T, K extends keyof T> = {
  [P in K]: T[P]
}

type UserPreview = Pick<User, 'id' | 'name'>
// { id: string; name: string }

// ✅ DO: Omit specific properties
type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>

type UserWithoutId = Omit<User, 'id'>
// { name: string; email: string }

// ✅ DO: Create record type
type Record<K extends keyof any, T> = {
  [P in K]: T
}

type UserRoles = Record<string, 'admin' | 'user' | 'guest'>
// { [key: string]: 'admin' | 'user' | 'guest' }

// ✅ DO: Nullable properties
type Nullable<T> = {
  [P in keyof T]: T[P] | null
}

type NullableUser = Nullable<User>
// { id: string | null; name: string | null; email: string | null }

// ✅ DO: Deep partial
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

interface NestedConfig {
  database: {
    host: string
    port: number
    credentials: {
      username: string
      password: string
    }
  }
}

type PartialConfig = DeepPartial<NestedConfig>
// All nested properties optional
```

---

## 7. Template Literal Types

```typescript
// ✅ DO: String manipulation
type Uppercase<S extends string> = intrinsic

type Lowercase<S extends string> = intrinsic

type Capitalize<S extends string> = intrinsic

type Uncapitalize<S extends string> = intrinsic

// Usage
type Greeting = 'hello'
type Loud = Uppercase<Greeting>          // "HELLO"
type Quiet = Lowercase<Loud>             // "hello"
type Proper = Capitalize<Greeting>       // "Hello"
type Lower = Uncapitalize<Proper>        // "hello"

// ✅ DO: Event handler naming
type EventHandlerName<T extends string> = `on${Capitalize<T>}`

type ClickHandler = EventHandlerName<'click'>      // "onClick"
type ChangeHandler = EventHandlerName<'change'>    // "onChange"

// ✅ DO: Getter/Setter naming
type GetterName<T extends string> = `get${Capitalize<T>}`
type SetterName<T extends string> = `set${Capitalize<T>}`

type GetName = GetterName<'name'>  // "getName"
type SetName = SetterName<'name'>  // "setName"

// ✅ DO: API route types
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE'
type Endpoint = 'users' | 'posts' | 'comments'

type ApiRoute = `/${Endpoint}` | `/${Endpoint}/:id`

const route1: ApiRoute = '/users'      // OK
const route2: ApiRoute = '/posts/:id'  // OK

// ✅ DO: CSS property types
type CSSUnit = 'px' | '%' | 'em' | 'rem'
type CSSValue<T extends CSSUnit> = `${number}${T}`

const width: CSSValue<'px'> = '100px'    // OK
const height: CSSValue<'%'> = '50%'      // OK

// ✅ DO: Combine template literals
type Color = 'red' | 'green' | 'blue'
type Shade = 'light' | 'dark'

type ColorWithShade = `${Shade}-${Color}`
// "light-red" | "light-green" | "light-blue" |
// "dark-red" | "dark-green" | "dark-blue"
```

---

## 8. Recursive Generic Types

```typescript
// ✅ DO: Nested array flattening
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T

type Nested = number[][][]
type Flat = Flatten<Nested>  // number

// ✅ DO: Deep readonly
type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object
    ? DeepReadonly<T[P]>
    : T[P]
}

interface NestedData {
  user: {
    profile: {
      name: string
      settings: {
        theme: string
      }
    }
  }
}

type ReadonlyData = DeepReadonly<NestedData>
// All properties at all levels are readonly

// ✅ DO: Path to property
type PathTo<T, Prefix extends string = ''> = {
  [K in keyof T & string]: T[K] extends object
    ? PathTo<T[K], `${Prefix}${K}.`> | `${Prefix}${K}`
    : `${Prefix}${K}`
}[keyof T & string]

interface Config {
  database: {
    host: string
    credentials: {
      username: string
      password: string
    }
  }
  app: {
    name: string
  }
}

type ConfigPath = PathTo<Config>
// "database" | "database.host" | "database.credentials" |
// "database.credentials.username" | "database.credentials.password" |
// "app" | "app.name"

// ✅ DO: Get nested property type
type Get<T, Path extends string> =
  Path extends `${infer Key}.${infer Rest}`
    ? Key extends keyof T
      ? Get<T[Key], Rest>
      : never
    : Path extends keyof T
      ? T[Path]
      : never

type HostType = Get<Config, 'database.host'>  // string
type UsernameType = Get<Config, 'database.credentials.username'>  // string
```

---

## 9. Variadic Tuple Types

```typescript
// ✅ DO: Prepend to tuple
type Prepend<T extends unknown[], U> = [U, ...T]

type WithId = Prepend<[string, number], number>  // [number, string, number]

// ✅ DO: Append to tuple
type Append<T extends unknown[], U> = [...T, U]

type WithTimestamp = Append<[string, number], Date>  // [string, number, Date]

// ✅ DO: Concat tuples
type Concat<T extends unknown[], U extends unknown[]> = [...T, ...U]

type Combined = Concat<[string, number], [boolean, Date]>
// [string, number, boolean, Date]

// ✅ DO: Reverse tuple
type Reverse<T extends unknown[]> =
  T extends [infer First, ...infer Rest]
    ? [...Reverse<Rest>, First]
    : []

type Original = [1, 2, 3, 4]
type Reversed = Reverse<Original>  // [4, 3, 2, 1]

// ✅ DO: Function with variable arguments
function curry<Args extends unknown[], R>(
  fn: (...args: Args) => R
): <Provided extends unknown[]>(
  ...args: Provided
) => (...rest: Tail<Args, Provided>) => R {
  return (...provided) => (...rest) => {
    return fn(...[...provided, ...rest] as Args)
  }
}

type Tail<T extends unknown[], Provided extends unknown[]> =
  T extends [...Provided, ...infer Rest] ? Rest : never
```

---

## 10. Branded Types

```typescript
// ✅ DO: Create nominal types
declare const brand: unique symbol

type Brand<T, B> = T & { [brand]: B }

type UserId = Brand<string, 'UserId'>
type Email = Brand<string, 'Email'>
type PositiveNumber = Brand<number, 'PositiveNumber'>
type NonEmptyString = Brand<string, 'NonEmptyString'>

// ✅ DO: Constructor functions
function UserId(id: string): UserId {
  // Validation logic
  if (!/^[0-9a-f]{24}$/.test(id)) {
    throw new Error('Invalid UserId format')
  }
  return id as UserId
}

function Email(email: string): Email {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email format')
  }
  return email as Email
}

function PositiveNumber(n: number): PositiveNumber {
  if (n <= 0) {
    throw new Error('Number must be positive')
  }
  return n as PositiveNumber
}

// ✅ DO: Type-safe APIs
function findUser(id: UserId): User {
  // id is guaranteed to be valid
  return db.users.findById(id)
}

function sendEmail(to: Email, subject: string): void {
  // to is guaranteed to be valid email
  emailService.send(to, subject)
}

// Usage
const userId = UserId('507f1f77bcf86cd799439011')
findUser(userId)  // OK

const rawId = 'invalid'
// findUser(rawId)  // Error: string is not assignable to UserId
```

---

## 11. Builder Pattern with Generics

```typescript
// ✅ DO: Type-safe builder
class QueryBuilder<T, Selected extends keyof T = never> {
  private query: {
    select?: (keyof T)[]
    where?: Partial<Record<keyof T, unknown>>
    orderBy?: keyof T
  } = {}

  select<K extends keyof T>(
    ...fields: K[]
  ): QueryBuilder<T, Selected | K> {
    this.query.select = fields
    return this as any
  }

  where(conditions: Partial<Record<keyof T, unknown>>): this {
    this.query.where = conditions
    return this
  }

  orderBy(field: keyof T): this {
    this.query.orderBy = field
    return this
  }

  execute(): Pick<T, Selected>[] {
    // Execute query and return results
    // Type is automatically narrowed to selected fields
    return [] as Pick<T, Selected>[]
  }
}

// Usage
interface User {
  id: string
  name: string
  email: string
  age: number
}

const users = new QueryBuilder<User>()
  .select('id', 'name')
  .where({ age: 30 })
  .orderBy('name')
  .execute()

// users is typed as Pick<User, 'id' | 'name'>[]
```

---

## 12. Higher-Kinded Types Simulation

```typescript
// ✅ DO: Simulate higher-kinded types
interface HKT {
  _URI?: unknown
  _A?: unknown
}

interface URItoKind<A> {
  Array: A[]
  Promise: Promise<A>
  Option: A | null
}

type Kind<F extends keyof URItoKind<unknown>, A> = URItoKind<A>[F]

// ✅ DO: Generic map function
interface Functor<F extends keyof URItoKind<unknown>> {
  map<A, B>(fa: Kind<F, A>, f: (a: A) => B): Kind<F, B>
}

const ArrayFunctor: Functor<'Array'> = {
  map: (fa, f) => fa.map(f)
}

const PromiseFunctor: Functor<'Promise'> = {
  map: (fa, f) => fa.then(f)
}

// Usage
const numbers = [1, 2, 3]
const doubled = ArrayFunctor.map(numbers, n => n * 2)

const asyncNumber = Promise.resolve(42)
const asyncDoubled = PromiseFunctor.map(asyncNumber, n => n * 2)
```

---

## Test Requirements

```typescript
// Test generic functions
describe('Generic Functions', () => {
  describe('findById', () => {
    it('should find item by id', () => {
      const users = [
        { id: '1', name: 'Alice' },
        { id: '2', name: 'Bob' }
      ]
      const user = findById(users, '1')
      expect(user).toEqual({ id: '1', name: 'Alice' })
    })

    it('should return undefined if not found', () => {
      const users = [{ id: '1', name: 'Alice' }]
      const user = findById(users, '999')
      expect(user).toBeUndefined()
    })
  })
})

// Test generic classes
describe('Stack', () => {
  it('should work with numbers', () => {
    const stack = new Stack<number>()
    stack.push(1)
    stack.push(2)
    expect(stack.pop()).toBe(2)
    expect(stack.pop()).toBe(1)
  })

  it('should work with strings', () => {
    const stack = new Stack<string>()
    stack.push('a')
    stack.push('b')
    expect(stack.pop()).toBe('b')
  })
})

// Test branded types
describe('Branded Types', () => {
  it('should create valid UserId', () => {
    const id = UserId('507f1f77bcf86cd799439011')
    expect(id).toBe('507f1f77bcf86cd799439011')
  })

  it('should throw for invalid UserId', () => {
    expect(() => UserId('invalid')).toThrow('Invalid UserId format')
  })
})
```

---

## Quick Reference

| Pattern | Use Case | Example |
|---------|----------|---------|
| Basic generic | Reusable function | `<T>(arr: T[])` |
| Constraint | Limit type | `<T extends HasId>` |
| Conditional | Type depends on condition | `T extends U ? X : Y` |
| Mapped | Transform type | `{ [K in keyof T]: ... }` |
| Template literal | String types | `` `${T}@${U}` `` |
| Recursive | Nested structures | `DeepReadonly<T>` |
| Variadic tuple | Variable args | `[...T, U]` |
| Branded | Nominal typing | `Brand<T, B>` |
| Builder | Fluent API | Chainable methods |
