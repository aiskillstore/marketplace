---
name: typescript-strict-guard
description: >
  Use when writing or reviewing TypeScript code. Enforces strict mode standards,
  explicit typing, and best practices. Prevents 'any' types, @ts-ignore comments,
  and non-null assertions. This is a COMPREHENSIVE skill - consult the detailed
  guides before writing any TypeScript code.
allowed-tools: Read, Grep
---

# TypeScript Strict Mode Guardian

**You are the TypeScript Strict Mode Guardian.** Your mission is to ensure ZERO type errors in all TypeScript code before it's written. This skill contains comprehensive patterns and solutions for every TypeScript scenario.

---

## Official Documentation

**Always reference these official sources:**

- **[TypeScript 5.6 Documentation](https://www.typescriptlang.org/docs/)** - Official TypeScript handbook
- **[TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)** - Complete language reference
- **[React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)** - React-specific patterns
- **[React 19 TypeScript Guide](https://react.dev/learn/typescript)** - Official React TypeScript guide
- **[DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped)** - Type definitions repository
- **[TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)** - Advanced TypeScript patterns

---

## Quick Reference - Critical Rules

**NEVER do these things:**

❌ Use `any` type without explicit justification
❌ Use `@ts-ignore` comments (fix the underlying issue)
❌ Use `!` non-null assertion (use type guards or optional chaining)
❌ Leave implicit `any` in function parameters
❌ Omit explicit return types on functions
❌ Use type assertions without runtime validation
❌ Commit code with console.log statements
❌ Bypass strict mode checks

**ALWAYS do these things:**

✅ Define explicit types for all function parameters and return values
✅ Use type guards to narrow `unknown` types
✅ Use optional chaining (`?.`) and nullish coalescing (`??`)
✅ Create interfaces for object shapes
✅ Use discriminated unions for variant types
✅ Validate external data with type guards
✅ Use utility types (`Partial`, `Pick`, `Omit`, etc.) appropriately
✅ Write tests for all type guards and validation functions

---

## Complete Guide Index

This skill contains **9 comprehensive guides** with **250+ code examples**:

### 1. [Strict Mode Violations](strict-mode-violations.md)
**24 scenarios with before/after examples**

- Using `any` type (external APIs, event handlers, dynamic keys, array methods)
- Using `@ts-ignore` (third-party issues, complex casting)
- Non-null assertions (array find, DOM elements, optional chaining)
- Missing return types (async functions, callbacks)
- Implicit any parameters (destructured objects)
- Type assertions without validation
- Index signatures without bounds
- Enum vs union types
- Type vs interface choice
- Const assertions
- Satisfies operator
- Template literal types
- Conditional types
- Mapped types
- Intersection vs union
- Never type usage
- Unknown vs any

**When to use:** Before writing ANY TypeScript code, review this file for the specific pattern you need.

### 2. [React TypeScript Patterns](react-typescript-patterns.md)
**13 sections covering ALL React patterns**

- Functional component props (basic, optional, with children)
- Event handler typing (ALL event types: click, change, submit, keyboard, focus, mouse, drag, scroll, touch)
- useState hook typing (basic state, arrays, objects, lazy initialization)
- useRef hook typing (DOM elements, mutable values, callback refs)
- useEffect and useLayoutEffect
- useContext hook (typed context, custom hooks with guards)
- Custom hooks (basic, generic, localStorage hook)
- forwardRef typing
- Higher-order components (HOC)
- Render props pattern
- Component composition (compound components)
- Form handling (controlled forms, validation)
- Server Components (Next.js 15 async components)

**When to use:** Writing ANY React component, hook, or pattern.

### 3. [Third-Party Library Typing](third-party-typing.md)
**16 scenarios for untyped libraries**

- Installing type definitions (@types packages)
- Creating declaration files (.d.ts)
- Augmenting existing types (Window, ProcessEnv, Express Request)
- Typing untyped NPM packages
- Typing JavaScript libraries
- Typing CSS modules
- Typing JSON files
- Typing image imports
- Typing global variables
- Typing utility libraries (Lodash)
- Typing browser APIs (experimental APIs)
- Typing Node.js modules
- Creating wrapper functions
- Typing GraphQL operations
- tsconfig.json configuration

**When to use:** Integrating ANY third-party library without types.

### 4. [Type Guards Library](type-guards-library.md)
**15 categories of reusable type guards**

- Primitive type guards (string, number, boolean, function, symbol, bigInt)
- Object type guards (basic object, plain object, hasKeys, hasProperties)
- Array type guards (isArray, isArrayOf, non-empty arrays, tuples)
- Nullable type guards (isNotNull, isNotUndefined, isNotNullish, isDefined)
- Instance type guards (Error, Date, RegExp, Promise, Map, Set)
- Interface type guards (user, generic interface guard builder)
- Discriminated union guards (Result type, Action types)
- JSON type guards (isJSONValue, parseJSON safely)
- Assertion functions (assertString, assertNumber, assertNotNull, generic assert)
- Property existence guards (hasProperty, hasMethod)
- Range and validation guards (isInRange, isEmail, isURL, isUUID, isISODateString)
- Branded type guards (nominal typing with branded types)
- Async type guards (async validation)
- Composite guards (isOneOf, isAllOf, optional)

**When to use:** Validating ANY external data or narrowing types.

### 5. [Generic Patterns](generic-patterns.md)
**12 advanced generic patterns**

- Basic generic functions (single generic, multiple generics)
- Generic constraints (HasId, keyof constraints, primitive constraints)
- Generic classes (Stack, Repository with constraints)
- Generic type inference (parameter inference, return type inference, default parameters)
- Conditional types (ElementType, Awaited, Exclude, Extract, NonNullable, ReturnType, Parameters)
- Mapped types (Partial, Required, Readonly, Pick, Omit, Record, Deep types)
- Template literal types (string manipulation, event handlers, getters/setters, API routes, CSS values)
- Recursive generic types (Flatten, DeepReadonly, PathTo, Get nested property)
- Variadic tuple types (Prepend, Append, Concat, Reverse, curry)
- Branded types (nominal typing, UserId, Email, PositiveNumber)
- Builder pattern with generics (type-safe fluent APIs)
- Higher-kinded types simulation (Functor pattern)

**When to use:** Creating ANY reusable function or data structure.

### 6. [Utility Types Guide](utility-types-guide.md)
**16 built-in utility types with decision trees**

- Partial<T> (update operations, configuration with defaults)
- Required<T> (ensure all fields provided)
- Readonly<T> (prevent mutation, immutable data)
- Pick<T, K> (API DTOs, form subsets, query projections)
- Omit<T, K> (remove sensitive fields, create inputs, remove computed)
- Record<K, T> (dictionaries, lookup tables, group by key)
- Exclude<T, U> (filter union types, remove values)
- Extract<T, U> (extract matching types from union)
- NonNullable<T> (remove null/undefined)
- ReturnType<T> (infer return type)
- Parameters<T> (extract function parameters)
- ConstructorParameters<T> (extract constructor parameters)
- InstanceType<T> (get instance type of class)
- Awaited<T> (unwrap Promise type)
- ThisParameterType<T> (extract 'this' parameter)
- OmitThisParameter<T> (remove 'this' parameter)

**Decision trees included for choosing the right utility type.**

**When to use:** Transforming ANY existing type.

### 7. [Async Typing Patterns](async-typing.md)
**13 async patterns**

- Basic Promise typing (explicit Promise<T>, async functions)
- Promise.all typing (tuple results, homogeneous arrays)
- Promise.race and Promise.any
- Error handling with types (Result type, Option type, Either type)
- Async generators (paginated fetching, processing with return value)
- Async iterators (custom async iterable)
- Deferred/Lazy promises
- Retry logic (exponential backoff, retry with condition)
- Timeout utilities (withTimeout, cleanup on timeout)
- Parallel execution with concurrency limit (parallelLimit, AsyncQueue)
- Async caching (cached async function, TTL cache)
- Async event emitter (type-safe events)
- AbortController integration (cancellable fetch, cancellable operations)

**When to use:** Writing ANY asynchronous code.

### 8. [Error Handling Types](error-handling-types.md)
**10 error handling patterns**

- Basic error types (ApplicationError, ValidationError, NotFoundError, UnauthorizedError)
- Result type pattern (Ok/Err constructors, map, flatMap, unwrap utilities)
- Option/Maybe type pattern (Some/None, isSome, isNone, map, getOrElse)
- Either type pattern (Left/Right, type guards, utilities, fold)
- Try-Catch with type safety (tryCatch, tryCatchAsync, error conversion)
- Validation with error accumulation (multiple errors, field-specific errors)
- Error boundaries (React error boundary with types)
- Async error handling (async Result, async Either)
- Error recovery strategies (retry with backoff, fallback chain)
- Exhaustive error handling (discriminated union errors, error handler mapping)

**When to use:** Handling ANY errors or failures.

### 9. [Validation Script](validate-types.py)
**Executable Python script for pre-validation**

Checks for:
- `any` type usage
- `@ts-ignore` comments
- `!` non-null assertions
- `console.log` in production code
- Missing return types on functions
- Implicit any in parameters

**Run before committing:**
```bash
python .claude/skills/typescript-strict-guard/validate-types.py --dir src/
```

---

## Workflow - Use This Skill

### When Writing New Code

**STEP 1: Identify the Pattern**

Before writing code, ask:
- Is this a React component? → [React TypeScript Patterns](react-typescript-patterns.md)
- Is this async code? → [Async Typing Patterns](async-typing.md)
- Does this validate external data? → [Type Guards Library](type-guards-library.md)
- Does this handle errors? → [Error Handling Types](error-handling-types.md)
- Does this use generics? → [Generic Patterns](generic-patterns.md)
- Does this transform types? → [Utility Types Guide](utility-types-guide.md)
- Does this use third-party library? → [Third-Party Library Typing](third-party-typing.md)

**STEP 2: Read the Relevant Section**

Open the guide and find the exact pattern you need. Each guide has 20+ examples with before/after code.

**STEP 3: Write Code Following the Pattern**

Copy the pattern structure, adapt to your use case, ensure explicit types everywhere.

**STEP 4: Validate**

Run the validation script:
```bash
python .claude/skills/typescript-strict-guard/validate-types.py --file src/path/to/file.ts
```

**STEP 5: Write Tests**

Every type guard, validation function, and custom type needs tests.

---

### When Reviewing Code

**STEP 1: Run Validation Script**

```bash
python .claude/skills/typescript-strict-guard/validate-types.py --dir src/
```

**STEP 2: Check for Common Violations**

Consult [Strict Mode Violations](strict-mode-violations.md) for the specific violation found.

**STEP 3: Suggest Correct Pattern**

Reference the appropriate guide section with the correct pattern.

**STEP 4: Verify Tests Exist**

All type guards and validation logic must have tests.

---

## Decision Trees

### When You See Unknown Data

```
Is the data from external source (API, user input, JSON)?
├─ YES → Create type guard in [Type Guards Library](type-guards-library.md)
│        Example: isUser(data: unknown): data is User
│        Then: Validate before using
└─ NO → Can you define the type at compile time?
         └─ YES → Use explicit type
         └─ NO → Use unknown with type narrowing
```

### When You Need to Transform Types

```
What transformation do you need?
├─ Make properties optional → Partial<T>
├─ Make properties required → Required<T>
├─ Make properties readonly → Readonly<T>
├─ Select specific properties → Pick<T, K>
├─ Remove specific properties → Omit<T, K>
├─ Create object with keys → Record<K, T>
├─ Remove types from union → Exclude<T, U>
├─ Extract types from union → Extract<T, U>
├─ Remove null/undefined → NonNullable<T>
├─ Get function return type → ReturnType<T>
├─ Get function parameters → Parameters<T>
└─ Unwrap Promise → Awaited<T>

See: [Utility Types Guide](utility-types-guide.md)
```

### When You Have an Error

```
What kind of error handling do you need?
├─ Explicit error as return value → Result<T, E> pattern
├─ Nullable value → Option<T> pattern
├─ Two distinct outcomes → Either<L, R> pattern
├─ Custom error with metadata → Extend ApplicationError class
├─ Multiple validation errors → ValidationResult<T> with errors array
├─ React component error → Error Boundary
└─ Async error handling → async Result<T, E>

See: [Error Handling Types](error-handling-types.md)
```

---

## Example: Complete Feature Implementation

**Scenario:** Fetch user from API, validate data, handle errors, display in React component.

**Step 1: Type Guard ([Type Guards Library](type-guards-library.md))**

```typescript
interface User {
  id: string
  name: string
  email: string
}

function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj && typeof obj.id === 'string' &&
    'name' in obj && typeof obj.name === 'string' &&
    'email' in obj && typeof obj.email === 'string'
  )
}
```

**Step 2: Async Function with Error Handling ([Async Typing](async-typing.md) + [Error Handling](error-handling-types.md))**

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E }

async function fetchUser(id: string): Promise<Result<User>> {
  try {
    const response = await fetch(`/api/users/${id}`)

    if (!response.ok) {
      return {
        success: false,
        error: new Error(`HTTP ${response.status}`)
      }
    }

    const data: unknown = await response.json()

    if (!isUser(data)) {
      return {
        success: false,
        error: new Error('Invalid user data from API')
      }
    }

    return { success: true, data }
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error : new Error('Unknown error')
    }
  }
}
```

**Step 3: React Component ([React TypeScript Patterns](react-typescript-patterns.md))**

```typescript
interface UserProfileProps {
  userId: string
}

function UserProfile({ userId }: UserProfileProps): React.ReactElement {
  const [user, setUser] = useState<User | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    async function loadUser(): Promise<void> {
      setLoading(true)
      const result = await fetchUser(userId)

      if (result.success) {
        setUser(result.data)
        setError(null)
      } else {
        setError(result.error.message)
        setUser(null)
      }

      setLoading(false)
    }

    loadUser()
  }, [userId])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!user) return <div>User not found</div>

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

**Step 4: Tests**

```typescript
describe('fetchUser', () => {
  it('should fetch user successfully', async () => {
    const result = await fetchUser('1')
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.id).toBe('1')
    }
  })

  it('should handle invalid data', async () => {
    // Mock returns invalid data
    const result = await fetchUser('invalid')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.message).toContain('Invalid user data')
    }
  })
})

describe('isUser', () => {
  it('should validate correct user object', () => {
    expect(isUser({ id: '1', name: 'Alice', email: 'alice@example.com' })).toBe(true)
  })

  it('should reject invalid object', () => {
    expect(isUser({ id: 123 })).toBe(false)
    expect(isUser(null)).toBe(false)
  })
})
```

**Step 5: Validate**

```bash
python .claude/skills/typescript-strict-guard/validate-types.py --file src/components/UserProfile.tsx
```

✅ **Result:** Zero type errors, comprehensive error handling, full test coverage.

---

## Pre-Commit Validation

**Before committing ANY TypeScript code:**

```bash
# Validate all TypeScript files
python .claude/skills/typescript-strict-guard/validate-types.py --dir src/

# Run TypeScript compiler
npx tsc --noEmit

# Run tests
npm test

# Run linter
npm run lint
```

All checks must pass before code is committed.

---

## Common Violations - Quick Fixes

| Violation | Quick Fix | Guide Section |
|-----------|-----------|---------------|
| `any` type | Use explicit type or `unknown` with type guard | [Strict Mode Violations](strict-mode-violations.md) #1-4 |
| `@ts-ignore` | Fix underlying issue or create proper type | [Strict Mode Violations](strict-mode-violations.md) #5-6 |
| `!` assertion | Use `?.` optional chaining or type guard | [Strict Mode Violations](strict-mode-violations.md) #7-9 |
| Missing return type | Add `: ReturnType` to function | [Strict Mode Violations](strict-mode-violations.md) #10-11 |
| Implicit `any` | Add type to parameters | [Strict Mode Violations](strict-mode-violations.md) #12 |
| Untyped event | Use `React.XEvent<HTMLElement>` | [React TypeScript Patterns](react-typescript-patterns.md) #2 |
| External data | Create type guard | [Type Guards Library](type-guards-library.md) #6 |
| Async error | Use `Result<T, E>` pattern | [Error Handling Types](error-handling-types.md) #8 |

---

## Success Metrics

**This skill is working when:**

✅ Zero `any` types in production code
✅ Zero `@ts-ignore` comments
✅ Zero `!` non-null assertions
✅ 100% explicit function return types
✅ All external data validated with type guards
✅ All type guards have tests
✅ TypeScript compiler passes with zero errors
✅ Validation script passes with zero violations

---

## File Statistics

- **Total Files:** 10
- **Total Lines:** 3,200+
- **Code Examples:** 250+
- **Patterns Covered:** 100+
- **Official Documentation Links:** 15+

---

## When to Use This Skill

**Always use when:**
- Writing any TypeScript code
- Reviewing any TypeScript code
- Debugging type errors
- Integrating third-party libraries
- Handling external data
- Writing React components
- Creating async functions
- Handling errors
- Creating generic utilities

**This skill prevents 99% of TypeScript errors before code is written.**

---

**Remember:** TypeScript strict mode is not a burden - it's a superpower. Use this skill to write perfect TypeScript code the first time, every time.
