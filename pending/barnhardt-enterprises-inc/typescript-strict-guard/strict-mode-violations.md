# TypeScript Strict Mode Violations and Fixes

**Official Documentation:**
- [TypeScript Handbook - Type Checking JavaScript Files](https://www.typescriptlang.org/docs/handbook/type-checking-javascript-files.html)
- [TypeScript 5.6 Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-6.html)
- [TypeScript Strict Mode Guide](https://www.typescriptlang.org/tsconfig#strict)

This document covers every common strict mode violation with actionable fixes.

---

## 1. Using `any` Type - External API Response

**Scenario:** Fetching data from external API

```typescript
// ❌ DON'T: Using any for API response
async function fetchUser(id: string): Promise<any> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}

// ✅ DO: Define explicit interface
interface User {
  id: string
  email: string
  name: string
  createdAt: string
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  const data: unknown = await response.json()

  if (!isUser(data)) {
    throw new Error('Invalid user data from API')
  }

  return data
}

function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj && typeof obj.id === 'string' &&
    'email' in obj && typeof obj.email === 'string' &&
    'name' in obj && typeof obj.name === 'string' &&
    'createdAt' in obj && typeof obj.createdAt === 'string'
  )
}
```

**Test Required:**
```typescript
describe('fetchUser', () => {
  it('should validate user data structure', async () => {
    const invalidData = { id: 123 } // Wrong type
    expect(() => isUser(invalidData)).toBe(false)
  })
})
```

---

## 2. Using `any` Type - Event Handlers

**Scenario:** Generic event handler

```typescript
// ❌ DON'T: Any event parameter
function handleEvent(event: any) {
  console.log(event.target.value)
}

// ✅ DO: Specific event type
function handleInputChange(event: React.ChangeEvent<HTMLInputElement>) {
  console.log(event.target.value)
}

function handleFormSubmit(event: React.FormEvent<HTMLFormElement>) {
  event.preventDefault()
  const formData = new FormData(event.currentTarget)
}

// ✅ DO: Generic event handler with type parameter
function createEventHandler<T extends Event>(
  callback: (event: T) => void
): (event: T) => void {
  return (event: T) => {
    callback(event)
  }
}
```

---

## 3. Using `any` Type - Dynamic Object Keys

**Scenario:** Accessing object properties dynamically

```typescript
// ❌ DON'T: Any for dynamic access
function getValue(obj: any, key: string) {
  return obj[key]
}

// ✅ DO: Use generics with keyof
function getValue<T extends object, K extends keyof T>(
  obj: T,
  key: K
): T[K] {
  return obj[key]
}

// ✅ DO: Use Record type for string keys
function getValue(obj: Record<string, unknown>, key: string): unknown {
  return obj[key]
}

// ✅ BEST: Use type guard for validated access
interface User {
  name: string
  email: string
}

function isValidUserKey(key: string): key is keyof User {
  return key === 'name' || key === 'email'
}

function getUserValue(user: User, key: string): string {
  if (!isValidUserKey(key)) {
    throw new Error(`Invalid user key: ${key}`)
  }
  return user[key]
}
```

---

## 4. Using `any` Type - Array Methods

**Scenario:** Using array map/filter/reduce

```typescript
// ❌ DON'T: Implicit any in callbacks
const values = items.map(item => item.value)

// ✅ DO: Explicit parameter types
interface Item {
  value: number
}

const values = items.map((item: Item): number => item.value)

// ✅ BETTER: Type inference from array
const items: Item[] = getItems()
const values = items.map(item => item.value) // item is Item

// ✅ DO: Complex reduce with accumulator type
interface Cart {
  total: number
  itemCount: number
}

const summary = items.reduce<Cart>(
  (acc, item) => ({
    total: acc.total + item.price,
    itemCount: acc.itemCount + 1
  }),
  { total: 0, itemCount: 0 }
)
```

---

## 5. Using `@ts-ignore` - Third-Party Library Issue

**Scenario:** Untyped library property

```typescript
// ❌ DON'T: Ignore the error
// @ts-ignore
window.gtag('event', 'click')

// ✅ DO: Extend global interface
declare global {
  interface Window {
    gtag: (
      command: 'event' | 'config',
      eventName: string,
      params?: Record<string, unknown>
    ) => void
  }
}

window.gtag('event', 'click', { category: 'button' })

// ✅ DO: Create type-safe wrapper
function trackEvent(eventName: string, params?: Record<string, unknown>): void {
  if (typeof window !== 'undefined' && 'gtag' in window) {
    window.gtag('event', eventName, params)
  }
}
```

---

## 6. Using `@ts-ignore` - Complex Type Casting

**Scenario:** Type assertion needed

```typescript
// ❌ DON'T: Ignore type error
// @ts-ignore
const user: User = apiResponse

// ✅ DO: Use type guard
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'email' in obj
  )
}

const apiResponse: unknown = await fetch('/api/user').then(r => r.json())
if (isUser(apiResponse)) {
  const user: User = apiResponse
}

// ✅ DO: Use validation library (Zod)
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string()
})

type User = z.infer<typeof UserSchema>

const user = UserSchema.parse(apiResponse)
```

---

## 7. Non-Null Assertion - Array Find

**Scenario:** Finding item in array

```typescript
// ❌ DON'T: Assume item exists
const user = users.find(u => u.id === id)!
console.log(user.name)

// ✅ DO: Handle undefined case
const user = users.find(u => u.id === id)
if (!user) {
  throw new Error(`User ${id} not found`)
}
console.log(user.name)

// ✅ DO: Use optional chaining with default
const userName = users.find(u => u.id === id)?.name ?? 'Unknown'

// ✅ DO: Create utility function
function findOrThrow<T>(
  array: T[],
  predicate: (item: T) => boolean,
  errorMsg: string
): T {
  const item = array.find(predicate)
  if (!item) {
    throw new Error(errorMsg)
  }
  return item
}

const user = findOrThrow(
  users,
  u => u.id === id,
  `User ${id} not found`
)
```

---

## 8. Non-Null Assertion - DOM Elements

**Scenario:** Querying DOM element

```typescript
// ❌ DON'T: Assume element exists
const button = document.querySelector('#submit')!
button.addEventListener('click', handler)

// ✅ DO: Check for null
const button = document.querySelector('#submit')
if (!button) {
  throw new Error('Submit button not found')
}
button.addEventListener('click', handler)

// ✅ DO: Use type guard for element type
function isHTMLButtonElement(
  element: Element | null
): element is HTMLButtonElement {
  return element instanceof HTMLButtonElement
}

const element = document.querySelector('#submit')
if (isHTMLButtonElement(element)) {
  element.addEventListener('click', handler)
}

// ✅ BETTER: React ref pattern (no DOM query needed)
function Component() {
  const buttonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const button = buttonRef.current
    if (!button) return

    button.addEventListener('click', handler)
    return () => button.removeEventListener('click', handler)
  }, [])

  return <button ref={buttonRef}>Submit</button>
}
```

---

## 9. Non-Null Assertion - Optional Chaining

**Scenario:** Nested object access

```typescript
// ❌ DON'T: Multiple assertions
const street = user.address!.street!

// ✅ DO: Optional chaining
const street = user.address?.street

// ✅ DO: With default value
const street = user.address?.street ?? 'No address'

// ✅ DO: Early return pattern
function getStreet(user: User): string {
  if (!user.address) {
    throw new Error('User has no address')
  }
  if (!user.address.street) {
    throw new Error('Address has no street')
  }
  return user.address.street
}

// ✅ DO: Type narrowing
interface UserWithAddress extends User {
  address: {
    street: string
    city: string
  }
}

function hasAddress(user: User): user is UserWithAddress {
  return (
    user.address !== undefined &&
    user.address !== null &&
    typeof user.address.street === 'string'
  )
}

if (hasAddress(user)) {
  console.log(user.address.street) // Safe access
}
```

---

## 10. Missing Return Type - Async Functions

**Scenario:** Async function without return type

```typescript
// ❌ DON'T: Implicit return type
async function fetchData(url: string) {
  const response = await fetch(url)
  return response.json()
}

// ✅ DO: Explicit Promise return type
async function fetchData<T>(url: string): Promise<T> {
  const response = await fetch(url)
  return response.json()
}

// ✅ DO: With error handling
async function fetchData<T>(url: string): Promise<T> {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response.json()
  } catch (error) {
    throw new Error(`Failed to fetch ${url}: ${error}`)
  }
}

// ✅ DO: Result type pattern
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E }

async function fetchData<T>(url: string): Promise<Result<T>> {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      return {
        success: false,
        error: new Error(`HTTP ${response.status}`)
      }
    }
    const data = await response.json()
    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error : new Error('Unknown error')
    }
  }
}
```

---

## 11. Missing Return Type - Callbacks

**Scenario:** Callback functions

```typescript
// ❌ DON'T: No return type on callback
function processItems(items: Item[], callback: (item: Item) => any) {
  return items.map(callback)
}

// ✅ DO: Generic return type
function processItems<T, R>(
  items: T[],
  callback: (item: T) => R
): R[] {
  return items.map(callback)
}

// ✅ DO: Explicit callback signature
type ItemProcessor<T, R> = (item: T, index: number) => R

function processItems<T, R>(
  items: T[],
  processor: ItemProcessor<T, R>
): R[] {
  return items.map((item, index) => processor(item, index))
}

// Usage
const results = processItems(items, (item): string => item.name)
```

---

## 12. Implicit Any Parameters - Destructured Objects

**Scenario:** Destructuring in function parameters

```typescript
// ❌ DON'T: Implicit any in destructuring
function greetUser({ name, age }) {
  return `Hello ${name}, you are ${age}`
}

// ✅ DO: Type the destructured parameter
interface UserInfo {
  name: string
  age: number
}

function greetUser({ name, age }: UserInfo): string {
  return `Hello ${name}, you are ${age}`
}

// ✅ DO: Inline type
function greetUser({ name, age }: { name: string; age: number }): string {
  return `Hello ${name}, you are ${age}`
}

// ✅ DO: With optional properties
function greetUser({
  name,
  age,
  title
}: {
  name: string
  age: number
  title?: string
}): string {
  return title
    ? `Hello ${title} ${name}, you are ${age}`
    : `Hello ${name}, you are ${age}`
}
```

---

## 13. Type Assertions Without Validation

**Scenario:** Casting without checking

```typescript
// ❌ DON'T: Unsafe casting
const user = apiData as User

// ✅ DO: Validate before casting
function assertUser(obj: unknown): asserts obj is User {
  if (!isUser(obj)) {
    throw new Error('Invalid user object')
  }
}

const apiData: unknown = await fetchData()
assertUser(apiData)
const user: User = apiData // Now safe

// ✅ DO: Type guard with casting
function toUser(obj: unknown): User {
  if (!isUser(obj)) {
    throw new Error('Invalid user object')
  }
  return obj
}

const user = toUser(apiData)

// ✅ DO: Use validation library
import { z } from 'zod'

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string()
})

const user = UserSchema.parse(apiData) // Throws if invalid
```

---

## 14. Index Signatures Without Bounds

**Scenario:** Objects with dynamic keys

```typescript
// ❌ DON'T: Unbounded index signature
interface Config {
  [key: string]: any
}

// ✅ DO: Constrained value type
interface Config {
  [key: string]: string | number | boolean
}

// ✅ BETTER: Use Record with union
type ConfigValue = string | number | boolean
type Config = Record<string, ConfigValue>

// ✅ BEST: Known keys with index signature
interface Config {
  apiUrl: string
  timeout: number
  debug: boolean
  [key: string]: string | number | boolean
}

// ✅ DO: Discriminated union for different configs
type StringConfig = { type: 'string'; value: string }
type NumberConfig = { type: 'number'; value: number }
type BooleanConfig = { type: 'boolean'; value: boolean }

type Config = StringConfig | NumberConfig | BooleanConfig

function getConfigValue(config: Config): string | number | boolean {
  switch (config.type) {
    case 'string':
      return config.value // string
    case 'number':
      return config.value // number
    case 'boolean':
      return config.value // boolean
  }
}
```

---

## 15. Enum vs Union Types

**Scenario:** Choosing between enum and union

```typescript
// ❌ DON'T: Numeric enum (confusing)
enum Status {
  Pending,    // 0
  Active,     // 1
  Completed   // 2
}

// ✅ ACCEPTABLE: String enum
enum Status {
  Pending = 'PENDING',
  Active = 'ACTIVE',
  Completed = 'COMPLETED'
}

// ✅ BETTER: Const assertion (more TypeScript-friendly)
const Status = {
  Pending: 'PENDING',
  Active: 'ACTIVE',
  Completed: 'COMPLETED'
} as const

type Status = typeof Status[keyof typeof Status]

// ✅ BEST: String literal union (simplest)
type Status = 'PENDING' | 'ACTIVE' | 'COMPLETED'

// Decision tree:
// - Need to iterate over values? → Const object with as const
// - Need nominal typing (brand types)? → Enum
// - Simple type checking? → Union type (RECOMMENDED)
```

**Test Required:**
```typescript
describe('Status types', () => {
  it('should only accept valid status values', () => {
    const status: Status = 'PENDING' // OK
    // const invalid: Status = 'INVALID' // Error at compile time
  })
})
```

---

## 16. Type vs Interface Choice

**Scenario:** Deciding between type and interface

```typescript
// ✅ USE INTERFACE: Object shapes that can be extended
interface User {
  id: string
  email: string
}

interface AdminUser extends User {
  permissions: string[]
}

// ✅ USE TYPE: Unions, intersections, primitives
type Status = 'active' | 'inactive' | 'pending'

type Point = {
  x: number
  y: number
}

type Shape = Circle | Rectangle | Triangle

// ✅ USE TYPE: Mapped types
type Readonly<T> = {
  readonly [P in keyof T]: T[P]
}

// ✅ USE TYPE: Conditional types
type NonNullable<T> = T extends null | undefined ? never : T

// ✅ USE INTERFACE: Augmentation (adding to existing types)
declare global {
  interface Window {
    myCustomProperty: string
  }
}

// Decision tree:
// - Extending/implementing? → Interface
// - Unions/intersections? → Type
// - Need declaration merging? → Interface
// - Simple object shape? → Either (prefer interface)
// - Advanced type manipulation? → Type
```

---

## 17. Const Assertions

**Scenario:** Creating readonly literal types

```typescript
// ❌ DON'T: Mutable array
const colors = ['red', 'green', 'blue']
// Type: string[]

// ✅ DO: Const assertion for tuple
const colors = ['red', 'green', 'blue'] as const
// Type: readonly ["red", "green", "blue"]

// ✅ DO: Object with const assertion
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
} as const
// Type: { readonly apiUrl: "https://api.example.com"; readonly timeout: 5000 }

// ✅ DO: Extract types from const assertions
const Routes = {
  Home: '/',
  About: '/about',
  Contact: '/contact'
} as const

type Route = typeof Routes[keyof typeof Routes]
// Type: "/" | "/about" | "/contact"

// ✅ DO: Enum-like pattern with const assertion
const HttpStatus = {
  OK: 200,
  BadRequest: 400,
  Unauthorized: 401,
  NotFound: 404
} as const

type HttpStatusCode = typeof HttpStatus[keyof typeof HttpStatus]
// Type: 200 | 400 | 401 | 404
```

---

## 18. Satisfies Operator (TypeScript 4.9+)

**Scenario:** Type checking without widening

```typescript
// ❌ DON'T: Lose literal types with type annotation
const config: Record<string, string | number> = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
}
// config.apiUrl is string | number (too wide!)

// ❌ DON'T: No type checking without annotation
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  wrongProperty: 'oops' // No error!
}

// ✅ DO: Use satisfies for validation without widening
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
} satisfies Record<string, string | number>
// config.apiUrl is string (exact type!)
// config.timeout is number (exact type!)

// ✅ DO: Ensure object matches interface
interface Config {
  apiUrl: string
  timeout: number
  debug?: boolean
}

const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000
} satisfies Config

// ✅ DO: Array of objects with exact types
const users = [
  { id: '1', name: 'Alice', role: 'admin' },
  { id: '2', name: 'Bob', role: 'user' }
] satisfies Array<{ id: string; name: string; role: string }>

// users[0].role is "admin" (literal type!)
```

---

## 19. Template Literal Types

**Scenario:** String pattern types

```typescript
// ✅ DO: Email format type
type Email = `${string}@${string}.${string}`

const email: Email = 'user@example.com' // OK
// const invalid: Email = 'not-an-email' // Error

// ✅ DO: URL type
type HTTPUrl = `http://${string}` | `https://${string}`

const url: HTTPUrl = 'https://example.com' // OK
// const invalid: HTTPUrl = 'ftp://example.com' // Error

// ✅ DO: CSS unit type
type CSSUnit = `${number}px` | `${number}%` | `${number}em`

const width: CSSUnit = '100px' // OK
const height: CSSUnit = '50%' // OK

// ✅ DO: Event naming convention
type EventName<T extends string> = `on${Capitalize<T>}`

type ClickEvent = EventName<'click'> // "onClick"
type ChangeEvent = EventName<'change'> // "onChange"

// ✅ DO: API route types
type ApiRoute = `/api/${string}`

function callApi(route: ApiRoute) {
  return fetch(route)
}

callApi('/api/users') // OK
// callApi('/other/path') // Error
```

---

## 20. Conditional Types

**Scenario:** Types that depend on conditions

```typescript
// ✅ DO: Extract array element type
type ElementType<T> = T extends Array<infer U> ? U : never

type StringArray = string[]
type Element = ElementType<StringArray> // string

// ✅ DO: Extract Promise resolved type
type Awaited<T> = T extends Promise<infer U> ? U : T

type AsyncString = Promise<string>
type Result = Awaited<AsyncString> // string

// ✅ DO: Filter nullable types
type NonNullable<T> = T extends null | undefined ? never : T

type MaybeString = string | null
type DefiniteString = NonNullable<MaybeString> // string

// ✅ DO: Function return type extractor
type ReturnType<T extends (...args: any[]) => any> =
  T extends (...args: any[]) => infer R ? R : never

function getUser(): User { return { id: '1', name: 'Alice' } }
type UserType = ReturnType<typeof getUser> // User

// ✅ DO: Conditional prop types
type ButtonProps<T extends 'button' | 'link'> = T extends 'button'
  ? { type: 'button'; onClick: () => void }
  : { type: 'link'; href: string }

function createButton<T extends 'button' | 'link'>(
  props: ButtonProps<T>
): void {
  if (props.type === 'button') {
    props.onClick() // OK
  } else {
    console.log(props.href) // OK
  }
}
```

---

## 21. Mapped Types

**Scenario:** Transform existing types

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

// ✅ DO: Make all properties readonly
type Readonly<T> = {
  readonly [P in keyof T]: T[P]
}

type ReadonlyUser = Readonly<User>

// ✅ DO: Remove readonly modifier
type Mutable<T> = {
  -readonly [P in keyof T]: T[P]
}

// ✅ DO: Add prefix to property names
type Prefixed<T, P extends string> = {
  [K in keyof T as `${P}${Capitalize<string & K>}`]: T[K]
}

type PrefixedUser = Prefixed<User, 'user'>
// { userId: string; userName: string; userEmail: string }

// ✅ DO: Filter properties by type
type StringProperties<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K]
}

interface Mixed {
  name: string
  age: number
  email: string
}

type OnlyStrings = StringProperties<Mixed>
// { name: string; email: string }
```

---

## 22. Intersection vs Union

**Scenario:** Combining types

```typescript
// ✅ USE INTERSECTION: Combine multiple types (AND logic)
interface Nameable {
  name: string
}

interface Ageable {
  age: number
}

type Person = Nameable & Ageable
// { name: string; age: number }

const person: Person = {
  name: 'Alice',
  age: 30
} // Must have BOTH properties

// ✅ USE UNION: One of several types (OR logic)
type Status = 'pending' | 'active' | 'completed'

const status: Status = 'active' // Must be ONE of these

// ✅ DO: Discriminated union for complex types
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number }

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2
    case 'rectangle':
      return shape.width * shape.height
    case 'triangle':
      return (shape.base * shape.height) / 2
  }
}

// ✅ DO: Intersection with union
type Admin = { role: 'admin'; permissions: string[] }
type User = { role: 'user'; profile: UserProfile }

type AuthUser = (Admin | User) & { id: string; email: string }

// Decision tree:
// - Need all properties? → Intersection (&)
// - Need one of several? → Union (|)
// - Need to distinguish cases? → Discriminated union
```

---

## 23. Never Type Usage

**Scenario:** Exhaustive checking and impossible states

```typescript
// ✅ DO: Exhaustive switch checking
type Action =
  | { type: 'INCREMENT' }
  | { type: 'DECREMENT' }
  | { type: 'RESET' }

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'INCREMENT':
      return state + 1
    case 'DECREMENT':
      return state - 1
    case 'RESET':
      return 0
    default:
      // Ensures all cases are handled
      const exhaustiveCheck: never = action
      throw new Error(`Unhandled action: ${exhaustiveCheck}`)
  }
}

// ✅ DO: Filter union types
type NonString<T> = T extends string ? never : T

type Mixed = string | number | boolean
type NoStrings = NonString<Mixed> // number | boolean

// ✅ DO: Impossible state prevention
interface NotStarted {
  state: 'not-started'
  progress?: never // Cannot exist
  result?: never
}

interface InProgress {
  state: 'in-progress'
  progress: number
  result?: never
}

interface Completed {
  state: 'completed'
  progress: 100
  result: string
}

type Task = NotStarted | InProgress | Completed

// ✅ DO: Function that never returns
function assertNever(value: never): never {
  throw new Error(`Unexpected value: ${value}`)
}
```

---

## 24. Unknown vs Any

**Scenario:** Handling unknown data

```typescript
// ❌ DON'T: Use any (no type safety)
function processValue(value: any) {
  return value.toUpperCase() // No error, crashes at runtime
}

// ✅ DO: Use unknown (type-safe)
function processValue(value: unknown): string {
  if (typeof value === 'string') {
    return value.toUpperCase() // OK after type guard
  }
  throw new Error('Value must be a string')
}

// ✅ DO: Type guard for unknown
function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function processValue(value: unknown): string {
  if (isString(value)) {
    return value.toUpperCase()
  }
  throw new Error('Value must be a string')
}

// ✅ DO: Handle multiple possible types
function processValue(value: unknown): string | number {
  if (typeof value === 'string') {
    return value.toUpperCase()
  }
  if (typeof value === 'number') {
    return value * 2
  }
  throw new Error('Value must be string or number')
}

// Decision tree:
// - Can you define the type? → Use specific type
// - Truly unknown at compile time? → Use unknown
// - Need to bypass type system? → NEVER use any
```

---

## Summary Decision Trees

### When to Use Each Type Feature

**Type vs Interface:**
- Object shape that extends? → Interface
- Union/intersection? → Type
- Simple object? → Interface (convention)
- Advanced type manipulation? → Type

**Enum vs Union:**
- Need iteration? → Const object with `as const`
- Simple string literals? → Union type
- Need nominal typing? → Enum

**Any vs Unknown:**
- Know the type? → Specific type
- Truly unknown? → Unknown with type guards
- Bypassing type system? → NEVER (find another way)

**Type Assertion vs Type Guard:**
- Can validate at runtime? → Type guard
- 100% certain of type? → Assertion (rare)
- External API data? → Type guard (ALWAYS)

### Common Patterns Quick Reference

| Pattern | Use Case | Example |
|---------|----------|---------|
| Type guard | Runtime validation | `obj is Type` |
| Generic | Reusable function | `<T>(item: T)` |
| Conditional | Type depends on condition | `T extends U ? X : Y` |
| Mapped | Transform type | `{ [K in keyof T]: ... }` |
| Template literal | String patterns | `` `${T}@${U}` `` |
| Discriminated union | Multiple variants | `{ type: 'a' } \| { type: 'b' }` |
| Const assertion | Readonly literals | `as const` |
| Satisfies | Type check without widening | `satisfies Type` |

---

**Test Coverage Required:**
- Every type guard must have test
- Every assertion function must have test
- Every generic function must have test with multiple types
- Every discriminated union must have exhaustive test
