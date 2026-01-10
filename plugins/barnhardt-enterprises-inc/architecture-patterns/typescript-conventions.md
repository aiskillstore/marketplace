# TypeScript Conventions

For complete TypeScript patterns, see: [typescript-strict-guard skill](../typescript-strict-guard/SKILL.md)

## Strict Mode Rules

### 1. No `any` Type
→ [Full Details](../typescript-strict-guard/SKILL.md#violation-1-using-any-type)

**Violation:**
```typescript
function processData(data: any) {
  return data.value
}
```

**Fix:**
```typescript
interface Data {
  value: string
}

function processData(data: Data): string {
  return data.value
}

// OR use unknown with type guard
function processData(data: unknown): string {
  if (isValidData(data)) {
    return data.value
  }
  throw new Error('Invalid data')
}
```

---

### 2. No `@ts-ignore`
→ [Full Details](../typescript-strict-guard/SKILL.md#violation-2-using-ts-ignore)

**Violation:**
```typescript
// @ts-ignore
const value = getData().property
```

**Fix:**
```typescript
const data = getData()
if ('property' in data) {
  const value = data.property
}
```

---

### 3. No Non-Null Assertions
→ [Full Details](../typescript-strict-guard/SKILL.md#violation-3-non-null-assertion)

**Violation:**
```typescript
const user = users.find(u => u.id === id)!
```

**Fix:**
```typescript
const user = users.find(u => u.id === id)
if (!user) {
  throw new Error(`User ${id} not found`)
}
const name = user.name
```

---

### 4. Explicit Function Types
→ [Full Details](../typescript-strict-guard/SKILL.md#violation-4-missing-return-type)

**Violation:**
```typescript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0)
}
```

**Fix:**
```typescript
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}
```

---

## Type Guards

→ [Full Details](../typescript-strict-guard/SKILL.md#type-guard-patterns)

### Basic Type Guards

```typescript
function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number'
}

function isObject(value: unknown): value is object {
  return typeof value === 'object' && value !== null
}
```

### Complex Type Guards

```typescript
interface User {
  id: string
  email: string
  name?: string
}

function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    typeof obj.id === 'string' &&
    'email' in obj &&
    typeof obj.email === 'string' &&
    (!('name' in obj) || typeof obj.name === 'string')
  )
}
```

### Usage

```typescript
const data: unknown = JSON.parse(response)
if (isUser(data)) {
  // TypeScript knows data is User here
  console.log(data.email)
}
```

---

## Utility Types

→ [Full Details](../typescript-strict-guard/SKILL.md#utility-types)

```typescript
type User = {
  id: string
  name: string
  email: string
}

// Make all properties optional
type UserUpdate = Partial<User>

// Make all properties required
type UserRequired = Required<UserUpdate>

// Pick specific properties
type UserPreview = Pick<User, 'id' | 'name'>

// Omit specific properties
type UserWithoutId = Omit<User, 'id'>

// Create object type with specific keys
type UserRoles = Record<string, 'admin' | 'user' | 'guest'>
```

---

## React-Specific Patterns

→ [Full Details](../typescript-strict-guard/SKILL.md#react-specific-patterns)

### Component Props

```typescript
interface ButtonProps {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

function Button({
  children,
  onClick,
  disabled,
  variant = 'primary'
}: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled} className={variant}>
      {children}
    </button>
  )
}
```

### Generic Components

```typescript
interface ListProps<T> {
  items: T[]
  renderItem: (item: T) => React.ReactNode
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <div>{items.map(renderItem)}</div>
}
```

### Event Handlers

```typescript
function Input() {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value)
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
  }

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} />
    </form>
  )
}
```

---

## Discriminated Unions

→ [Full Details](../typescript-strict-guard/SKILL.md#discriminated-unions)

```typescript
type Success = {
  status: 'success'
  data: string
}

type Error = {
  status: 'error'
  error: string
}

type Result = Success | Error

function handleResult(result: Result): string {
  if (result.status === 'success') {
    return result.data // TypeScript knows this is Success
  } else {
    return result.error // TypeScript knows this is Error
  }
}
```

---

## Generic Patterns

→ [Full Details](../typescript-strict-guard/SKILL.md#generic-patterns)

```typescript
// Basic generic
function first<T>(arr: T[]): T | undefined {
  return arr[0]
}

// Constrained generic
interface HasId {
  id: string
}

function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id)
}

// Generic with inference
function identity<T>(value: T): T {
  return value
}

const num = identity(42) // Type inferred as number
const str = identity('hello') // Type inferred as string
```

---

## Common Fixes Cheat Sheet

| Problem | Solution |
|---------|----------|
| `any` type | Use explicit types or `unknown` with type guards |
| `@ts-ignore` | Fix the underlying type error |
| `!` assertion | Use optional chaining or type guards |
| Missing return type | Add explicit return type annotation |
| Implicit any | Add type annotations to parameters |
| Union types | Use type guards or discriminated unions |
| Null/undefined | Use optional chaining `?.` or nullish coalescing `??` |

---

## tsconfig.json Requirements

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

---

## See Also

- [typescript-strict-guard/SKILL.md](../typescript-strict-guard/SKILL.md) - Complete patterns
- [quality-gates/validation-rules.md](../quality-gates/validation-rules.md) - Validation rules
- [api-patterns.md](./api-patterns.md) - API type patterns
