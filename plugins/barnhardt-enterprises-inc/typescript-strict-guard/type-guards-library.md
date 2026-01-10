# Type Guards Library

**Official Documentation:**
- [TypeScript Type Guards and Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [User-Defined Type Guards](https://www.typescriptlang.org/docs/handbook/advanced-types.html#user-defined-type-guards)
- [TypeScript 5.6 Type Predicates](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-6.html)

Reusable type guard patterns for common scenarios.

---

## 1. Primitive Type Guards

```typescript
// ✅ String type guard
export function isString(value: unknown): value is string {
  return typeof value === 'string'
}

// ✅ Number type guard
export function isNumber(value: unknown): value is number {
  return typeof value === 'number' && !isNaN(value)
}

// ✅ Boolean type guard
export function isBoolean(value: unknown): value is boolean {
  return typeof value === 'boolean'
}

// ✅ Function type guard
export function isFunction(value: unknown): value is Function {
  return typeof value === 'function'
}

// ✅ Symbol type guard
export function isSymbol(value: unknown): value is symbol {
  return typeof value === 'symbol'
}

// ✅ BigInt type guard
export function isBigInt(value: unknown): value is bigint {
  return typeof value === 'bigint'
}

// Usage
function process(value: unknown) {
  if (isString(value)) {
    return value.toUpperCase()  // value is string
  }
  if (isNumber(value)) {
    return value.toFixed(2)  // value is number
  }
}
```

---

## 2. Object Type Guards

```typescript
// ✅ Basic object type guard
export function isObject(value: unknown): value is object {
  return typeof value === 'object' && value !== null
}

// ✅ Plain object (not array, not null, not date, etc.)
export function isPlainObject(value: unknown): value is Record<string, unknown> {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value) &&
    Object.prototype.toString.call(value) === '[object Object]'
  )
}

// ✅ Non-null object
export function isNonNullObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

// ✅ Object with specific keys
export function hasKeys<K extends string>(
  value: unknown,
  keys: readonly K[]
): value is Record<K, unknown> {
  if (!isObject(value)) return false

  return keys.every(key => key in value)
}

// Usage
if (hasKeys(obj, ['id', 'name'] as const)) {
  console.log(obj.id)    // OK
  console.log(obj.name)  // OK
}
```

---

## 3. Array Type Guards

```typescript
// ✅ Array type guard
export function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value)
}

// ✅ Array of specific type
export function isArrayOf<T>(
  value: unknown,
  guard: (item: unknown) => item is T
): value is T[] {
  return Array.isArray(value) && value.every(guard)
}

// Usage
const maybeNumbers: unknown = [1, 2, 3]

if (isArrayOf(maybeNumbers, isNumber)) {
  // maybeNumbers is number[]
  const sum = maybeNumbers.reduce((a, b) => a + b, 0)
}

// ✅ Non-empty array
export function isNonEmptyArray<T>(value: T[]): value is [T, ...T[]] {
  return value.length > 0
}

// Usage
function processArray(items: string[]) {
  if (isNonEmptyArray(items)) {
    const first = items[0]  // Type is string (not string | undefined)
    console.log(first.toUpperCase())
  }
}

// ✅ Tuple type guard
export function isTuple<T extends readonly unknown[]>(
  value: unknown,
  guards: { [K in keyof T]: (item: unknown) => item is T[K] }
): value is T {
  if (!Array.isArray(value)) return false
  if (value.length !== guards.length) return false

  return guards.every((guard, index) => guard(value[index]))
}

// Usage
const pair: unknown = ['hello', 42]

if (isTuple(pair, [isString, isNumber])) {
  // pair is [string, number]
  const [str, num] = pair
  console.log(str.toUpperCase(), num.toFixed(2))
}
```

---

## 4. Nullable Type Guards

```typescript
// ✅ Not null
export function isNotNull<T>(value: T | null): value is T {
  return value !== null
}

// ✅ Not undefined
export function isNotUndefined<T>(value: T | undefined): value is T {
  return value !== undefined
}

// ✅ Not nullish (not null and not undefined)
export function isNotNullish<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined
}

// ✅ Defined (not undefined)
export function isDefined<T>(value: T | undefined): value is T {
  return value !== undefined
}

// Usage
const users: (User | null)[] = getUsers()
const validUsers = users.filter(isNotNull)  // Type: User[]

const maybeValue: string | undefined = getValue()
if (isDefined(maybeValue)) {
  console.log(maybeValue.toUpperCase())  // Safe
}
```

---

## 5. Instance Type Guards

```typescript
// ✅ Error instance
export function isError(value: unknown): value is Error {
  return value instanceof Error
}

// ✅ Date instance
export function isDate(value: unknown): value is Date {
  return value instanceof Date && !isNaN(value.getTime())
}

// ✅ RegExp instance
export function isRegExp(value: unknown): value is RegExp {
  return value instanceof RegExp
}

// ✅ Promise instance
export function isPromise<T = unknown>(value: unknown): value is Promise<T> {
  return (
    value instanceof Promise ||
    (isObject(value) &&
      'then' in value &&
      typeof value.then === 'function')
  )
}

// ✅ Map instance
export function isMap<K = unknown, V = unknown>(
  value: unknown
): value is Map<K, V> {
  return value instanceof Map
}

// ✅ Set instance
export function isSet<T = unknown>(value: unknown): value is Set<T> {
  return value instanceof Set
}

// Usage
function handleError(error: unknown) {
  if (isError(error)) {
    console.error(error.message)  // Type-safe
    console.error(error.stack)
  }
}
```

---

## 6. Interface Type Guards

```typescript
// ✅ User interface
interface User {
  id: string
  email: string
  name: string
  age?: number
}

export function isUser(value: unknown): value is User {
  return (
    isObject(value) &&
    'id' in value &&
    isString(value.id) &&
    'email' in value &&
    isString(value.email) &&
    'name' in value &&
    isString(value.name) &&
    (!('age' in value) || isNumber(value.age))
  )
}

// ✅ Generic interface guard builder
export function createInterfaceGuard<T extends Record<string, unknown>>(
  schema: {
    [K in keyof T]: (value: unknown) => value is T[K]
  }
): (value: unknown) => value is T {
  return (value: unknown): value is T => {
    if (!isObject(value)) return false

    return Object.entries(schema).every(([key, guard]) => {
      if (!(key in value)) return false
      return guard((value as Record<string, unknown>)[key])
    })
  }
}

// Usage
const isUser = createInterfaceGuard<User>({
  id: isString,
  email: isString,
  name: isString,
  age: (v: unknown): v is number | undefined =>
    v === undefined || isNumber(v)
})

const data: unknown = { id: '1', email: 'test@example.com', name: 'Alice' }
if (isUser(data)) {
  console.log(data.email)  // Type-safe
}
```

---

## 7. Discriminated Union Guards

```typescript
// ✅ Discriminated union
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E }

export function isSuccess<T, E>(
  result: Result<T, E>
): result is { success: true; data: T } {
  return result.success === true
}

export function isFailure<T, E>(
  result: Result<T, E>
): result is { success: false; error: E } {
  return result.success === false
}

// Usage
const result: Result<User, string> = await fetchUser()

if (isSuccess(result)) {
  console.log(result.data.name)  // Type: User
}

if (isFailure(result)) {
  console.error(result.error)  // Type: string
}

// ✅ Action discriminated union
type Action =
  | { type: 'INCREMENT'; by: number }
  | { type: 'DECREMENT'; by: number }
  | { type: 'RESET' }

export function isIncrementAction(
  action: Action
): action is { type: 'INCREMENT'; by: number } {
  return action.type === 'INCREMENT'
}

export function isDecrementAction(
  action: Action
): action is { type: 'DECREMENT'; by: number } {
  return action.type === 'DECREMENT'
}

export function isResetAction(
  action: Action
): action is { type: 'RESET' } {
  return action.type === 'RESET'
}

// Usage
function reducer(state: number, action: Action): number {
  if (isIncrementAction(action)) {
    return state + action.by  // action.by is available
  }
  if (isDecrementAction(action)) {
    return state - action.by  // action.by is available
  }
  if (isResetAction(action)) {
    return 0
  }
  return state
}
```

---

## 8. JSON Type Guards

```typescript
// ✅ JSON value type
type JSONValue =
  | null
  | boolean
  | number
  | string
  | JSONValue[]
  | { [key: string]: JSONValue }

export function isJSONValue(value: unknown): value is JSONValue {
  if (value === null) return true
  if (typeof value === 'boolean') return true
  if (typeof value === 'number') return !isNaN(value) && isFinite(value)
  if (typeof value === 'string') return true

  if (Array.isArray(value)) {
    return value.every(isJSONValue)
  }

  if (isPlainObject(value)) {
    return Object.values(value).every(isJSONValue)
  }

  return false
}

// ✅ Parse JSON safely
export function parseJSON<T = unknown>(
  json: string,
  guard?: (value: unknown) => value is T
): T | null {
  try {
    const parsed: unknown = JSON.parse(json)

    if (guard && !guard(parsed)) {
      return null
    }

    return parsed as T
  } catch {
    return null
  }
}

// Usage
const userJson = '{"id":"1","name":"Alice"}'
const user = parseJSON(userJson, isUser)

if (user) {
  console.log(user.name)  // Type-safe
}
```

---

## 9. Assertion Functions

```typescript
// ✅ Assert string
export function assertString(
  value: unknown,
  message?: string
): asserts value is string {
  if (!isString(value)) {
    throw new Error(message ?? 'Value must be a string')
  }
}

// ✅ Assert number
export function assertNumber(
  value: unknown,
  message?: string
): asserts value is number {
  if (!isNumber(value)) {
    throw new Error(message ?? 'Value must be a number')
  }
}

// ✅ Assert not null
export function assertNotNull<T>(
  value: T | null,
  message?: string
): asserts value is T {
  if (value === null) {
    throw new Error(message ?? 'Value must not be null')
  }
}

// ✅ Assert not nullish
export function assertNotNullish<T>(
  value: T | null | undefined,
  message?: string
): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message ?? 'Value must not be null or undefined')
  }
}

// ✅ Generic assertion
export function assert<T>(
  value: unknown,
  guard: (value: unknown) => value is T,
  message?: string
): asserts value is T {
  if (!guard(value)) {
    throw new Error(message ?? 'Assertion failed')
  }
}

// Usage
function processUser(data: unknown) {
  assertUser(data, 'Invalid user data')
  // data is now typed as User
  console.log(data.email)
}

function assertUser(value: unknown, message?: string): asserts value is User {
  if (!isUser(value)) {
    throw new Error(message ?? 'Invalid user')
  }
}
```

---

## 10. Property Existence Guards

```typescript
// ✅ Has property
export function hasProperty<K extends PropertyKey>(
  value: unknown,
  key: K
): value is Record<K, unknown> {
  return isObject(value) && key in value
}

// ✅ Has properties (multiple)
export function hasProperties<K extends PropertyKey>(
  value: unknown,
  keys: readonly K[]
): value is Record<K, unknown> {
  return isObject(value) && keys.every(key => key in value)
}

// ✅ Has method
export function hasMethod<K extends PropertyKey>(
  value: unknown,
  method: K
): value is Record<K, Function> {
  return (
    isObject(value) &&
    method in value &&
    typeof (value as Record<K, unknown>)[method] === 'function'
  )
}

// Usage
if (hasProperty(obj, 'email')) {
  console.log(obj.email)  // obj.email exists
}

if (hasMethod(obj, 'save')) {
  obj.save()  // obj.save is a function
}
```

---

## 11. Range and Validation Guards

```typescript
// ✅ Number in range
export function isInRange(
  value: unknown,
  min: number,
  max: number
): value is number {
  return isNumber(value) && value >= min && value <= max
}

// ✅ String length validation
export function isStringWithLength(
  value: unknown,
  minLength: number,
  maxLength?: number
): value is string {
  if (!isString(value)) return false
  if (value.length < minLength) return false
  if (maxLength !== undefined && value.length > maxLength) return false
  return true
}

// ✅ Email validation
export function isEmail(value: unknown): value is string {
  return (
    isString(value) &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
  )
}

// ✅ URL validation
export function isURL(value: unknown): value is string {
  if (!isString(value)) return false

  try {
    new URL(value)
    return true
  } catch {
    return false
  }
}

// ✅ UUID validation
export function isUUID(value: unknown): value is string {
  return (
    isString(value) &&
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
  )
}

// ✅ ISO date string
export function isISODateString(value: unknown): value is string {
  if (!isString(value)) return false

  const date = new Date(value)
  return !isNaN(date.getTime()) && date.toISOString() === value
}

// Usage
function processAge(age: unknown) {
  if (isInRange(age, 0, 120)) {
    console.log(`Valid age: ${age}`)
  }
}

function sendEmail(email: unknown) {
  if (isEmail(email)) {
    // email is string and validated
    console.log(`Sending to: ${email}`)
  }
}
```

---

## 12. Branded Type Guards

```typescript
// ✅ Brand types for nominal typing
declare const brand: unique symbol

type Brand<T, B> = T & { [brand]: B }

type UserId = Brand<string, 'UserId'>
type Email = Brand<string, 'Email'>
type PositiveNumber = Brand<number, 'PositiveNumber'>

// ✅ Create branded value
export function createUserId(id: string): UserId | null {
  if (isUUID(id)) {
    return id as UserId
  }
  return null
}

export function createEmail(email: string): Email | null {
  if (isEmail(email)) {
    return email as Email
  }
  return null
}

export function createPositiveNumber(n: number): PositiveNumber | null {
  if (isNumber(n) && n > 0) {
    return n as PositiveNumber
  }
  return null
}

// ✅ Type guards for branded types
export function isUserId(value: unknown): value is UserId {
  return isString(value) && isUUID(value)
}

export function isEmailBrand(value: unknown): value is Email {
  return isString(value) && isEmail(value)
}

// Usage
function findUser(id: UserId) {
  // id is guaranteed to be a valid UUID
  return db.users.find({ id })
}

const maybeId = createUserId(input)
if (maybeId) {
  findUser(maybeId)  // Type-safe
}
```

---

## 13. Async Type Guards

```typescript
// ✅ Async type guard
export async function isValidUser(value: unknown): Promise<boolean> {
  if (!isUser(value)) return false

  // Check email exists in database
  const exists = await db.users.exists({ email: value.email })
  return exists
}

// ✅ Async assertion
export async function assertValidUser(value: unknown): Promise<asserts value is User> {
  if (!isUser(value)) {
    throw new Error('Invalid user object')
  }

  const exists = await db.users.exists({ email: value.email })
  if (!exists) {
    throw new Error('User email not found in database')
  }
}

// Usage
async function processUser(data: unknown) {
  await assertValidUser(data)
  // data is now typed as User and validated
  console.log(data.email)
}
```

---

## 14. Composite Guards

```typescript
// ✅ One of (union guard)
export function isOneOf<T extends readonly unknown[]>(
  value: unknown,
  guards: { [K in keyof T]: (value: unknown) => value is T[K] }
): value is T[number] {
  return guards.some(guard => guard(value))
}

// Usage
const isStringOrNumber = (value: unknown): value is string | number => {
  return isOneOf(value, [isString, isNumber])
}

// ✅ All of (intersection guard)
export function isAllOf<T extends readonly unknown[]>(
  value: unknown,
  guards: { [K in keyof T]: (value: unknown) => value is T[K] }
): value is T[number] {
  return guards.every(guard => guard(value))
}

// ✅ Optional field guard
export function optional<T>(
  guard: (value: unknown) => value is T
): (value: unknown) => value is T | undefined {
  return (value: unknown): value is T | undefined => {
    return value === undefined || guard(value)
  }
}

// Usage
const isOptionalString = optional(isString)

interface Config {
  apiKey: string
  timeout?: number
}

const isConfig = createInterfaceGuard<Config>({
  apiKey: isString,
  timeout: optional(isNumber)
})
```

---

## 15. Complete Example Library

```typescript
// src/lib/type-guards.ts

// Re-export all guards
export {
  // Primitives
  isString,
  isNumber,
  isBoolean,
  isFunction,
  isSymbol,
  isBigInt,

  // Objects
  isObject,
  isPlainObject,
  isNonNullObject,
  hasKeys,

  // Arrays
  isArray,
  isArrayOf,
  isNonEmptyArray,
  isTuple,

  // Nullable
  isNotNull,
  isNotUndefined,
  isNotNullish,
  isDefined,

  // Instances
  isError,
  isDate,
  isRegExp,
  isPromise,
  isMap,
  isSet,

  // Validation
  isInRange,
  isStringWithLength,
  isEmail,
  isURL,
  isUUID,
  isISODateString,

  // JSON
  isJSONValue,
  parseJSON,

  // Assertions
  assertString,
  assertNumber,
  assertNotNull,
  assertNotNullish,
  assert,

  // Property
  hasProperty,
  hasProperties,
  hasMethod,

  // Composite
  isOneOf,
  isAllOf,
  optional
}
```

---

## Test Requirements

```typescript
// Every type guard must have comprehensive tests

describe('Type Guards', () => {
  describe('isString', () => {
    it('should return true for strings', () => {
      expect(isString('hello')).toBe(true)
      expect(isString('')).toBe(true)
    })

    it('should return false for non-strings', () => {
      expect(isString(123)).toBe(false)
      expect(isString(null)).toBe(false)
      expect(isString(undefined)).toBe(false)
    })
  })

  describe('isUser', () => {
    it('should validate correct user object', () => {
      const user = { id: '1', email: 'test@example.com', name: 'Alice' }
      expect(isUser(user)).toBe(true)
    })

    it('should reject invalid user object', () => {
      expect(isUser({ id: 123 })).toBe(false)
      expect(isUser(null)).toBe(false)
    })
  })

  describe('assertNotNull', () => {
    it('should not throw for non-null values', () => {
      expect(() => assertNotNull('value')).not.toThrow()
    })

    it('should throw for null', () => {
      expect(() => assertNotNull(null)).toThrow('Value must not be null')
    })
  })
})
```

---

## Quick Reference

| Guard Type | Function | Example |
|-----------|----------|---------|
| Primitive | `isString`, `isNumber` | `if (isString(x))` |
| Object | `isObject`, `hasKeys` | `if (hasKeys(obj, ['id']))` |
| Array | `isArray`, `isArrayOf` | `if (isArrayOf(arr, isNumber))` |
| Nullable | `isNotNull`, `isDefined` | `arr.filter(isNotNull)` |
| Instance | `isError`, `isDate` | `if (isError(e))` |
| Validation | `isEmail`, `isURL` | `if (isEmail(input))` |
| Assertion | `assert`, `assertNotNull` | `assertUser(data)` |
| Composite | `isOneOf`, `optional` | `optional(isString)` |
