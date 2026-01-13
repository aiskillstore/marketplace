# React Hooks - Complete Reference (React 19)

## Table of Contents

- [Rules of Hooks](#rules-of-hooks)
- [State Hooks](#state-hooks)
- [Effect Hooks](#effect-hooks)
- [Ref Hooks](#ref-hooks)
- [Context Hooks](#context-hooks)
- [Performance Hooks](#performance-hooks)
- [Transition Hooks](#transition-hooks)
- [New React 19 Hooks](#new-react-19-hooks)
- [Custom Hooks](#custom-hooks)

## Rules of Hooks

These rules are **MANDATORY** and enforced by ESLint:

### Rule 1: Only Call Hooks at the Top Level

❌ **DON'T** call hooks inside conditions, loops, or nested functions:

```typescript
// ❌ BAD: Hook in condition
function BadComponent() {
  if (condition) {
    const [state, setState] = useState(0) // ERROR!
  }
}

// ❌ BAD: Hook in loop
function BadComponent() {
  for (let i = 0; i < 10; i++) {
    const [state, setState] = useState(0) // ERROR!
  }
}

// ❌ BAD: Hook in nested function
function BadComponent() {
  function nested() {
    const [state, setState] = useState(0) // ERROR!
  }
}
```

✅ **DO** call hooks at the top level:

```typescript
// ✅ GOOD: Hooks at top level
function GoodComponent() {
  const [state, setState] = useState(0) // ✅
  const [other, setOther] = useState('') // ✅

  if (condition) {
    // Use the hook results here
    setState(1)
  }

  return <div>{state}</div>
}
```

### Rule 2: Only Call Hooks in React Functions

❌ **DON'T** call hooks in regular JavaScript functions:

```typescript
// ❌ BAD: Hook in regular function
function regularFunction() {
  const [state, setState] = useState(0) // ERROR!
}
```

✅ **DO** call hooks in React components or custom hooks:

```typescript
// ✅ GOOD: Hook in component
function MyComponent() {
  const [state, setState] = useState(0) // ✅
  return <div>{state}</div>
}

// ✅ GOOD: Hook in custom hook
function useCustomHook() {
  const [state, setState] = useState(0) // ✅
  return [state, setState] as const
}
```

## State Hooks

### useState

The fundamental hook for managing component state.

#### Basic Usage

```typescript
import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(count - 1)}>Decrement</button>
    </div>
  )
}
```

#### With TypeScript

```typescript
// Primitive type (inferred)
const [count, setCount] = useState(0) // number

// Explicit type
const [name, setName] = useState<string>('')

// Union type
const [status, setStatus] = useState<'idle' | 'loading' | 'error'>('idle')

// Object type
interface User {
  id: string
  name: string
  email: string
}

const [user, setUser] = useState<User | null>(null)

// Array type
const [items, setItems] = useState<string[]>([])
```

#### Functional Updates

Use functional updates when new state depends on previous state:

```typescript
function Counter() {
  const [count, setCount] = useState(0)

  // ❌ BAD: May be stale
  const increment = () => {
    setCount(count + 1)
    setCount(count + 1) // Will only increment by 1!
  }

  // ✅ GOOD: Functional update
  const increment = () => {
    setCount((prev) => prev + 1)
    setCount((prev) => prev + 1) // Will increment by 2!
  }

  return <button onClick={increment}>Count: {count}</button>
}
```

#### Lazy Initialization

Use lazy initialization for expensive computations:

```typescript
// ❌ BAD: Runs on every render
function Component() {
  const [state, setState] = useState(expensiveComputation())
}

// ✅ GOOD: Runs only once
function Component() {
  const [state, setState] = useState(() => expensiveComputation())
}

// Example: localStorage
function Component() {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
}
```

#### Complex State Objects

```typescript
interface FormState {
  name: string
  email: string
  age: number
}

function Form() {
  const [form, setForm] = useState<FormState>({
    name: '',
    email: '',
    age: 0,
  })

  // Update single field
  const updateName = (name: string) => {
    setForm((prev) => ({ ...prev, name }))
  }

  // Generic field updater
  const updateField = (field: keyof FormState, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <form>
      <input
        value={form.name}
        onChange={(e) => updateName(e.target.value)}
      />
      <input
        value={form.email}
        onChange={(e) => updateField('email', e.target.value)}
      />
    </form>
  )
}
```

### useReducer

Alternative to useState for complex state logic.

#### Basic Usage

```typescript
import { useReducer } from 'react'

type State = { count: number }
type Action = { type: 'increment' } | { type: 'decrement' } | { type: 'reset' }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { count: state.count + 1 }
    case 'decrement':
      return { count: state.count - 1 }
    case 'reset':
      return { count: 0 }
    default:
      return state
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0 })

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  )
}
```

#### Complex Example: Todo List

```typescript
interface Todo {
  id: string
  text: string
  completed: boolean
}

type State = {
  todos: Todo[]
  filter: 'all' | 'active' | 'completed'
}

type Action =
  | { type: 'add'; text: string }
  | { type: 'toggle'; id: string }
  | { type: 'delete'; id: string }
  | { type: 'setFilter'; filter: State['filter'] }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'add':
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: crypto.randomUUID(), text: action.text, completed: false },
        ],
      }
    case 'toggle':
      return {
        ...state,
        todos: state.todos.map((todo) =>
          todo.id === action.id
            ? { ...todo, completed: !todo.completed }
            : todo
        ),
      }
    case 'delete':
      return {
        ...state,
        todos: state.todos.filter((todo) => todo.id !== action.id),
      }
    case 'setFilter':
      return {
        ...state,
        filter: action.filter,
      }
    default:
      return state
  }
}

function TodoApp() {
  const [state, dispatch] = useReducer(reducer, {
    todos: [],
    filter: 'all',
  })

  const filteredTodos = state.todos.filter((todo) => {
    if (state.filter === 'active') return !todo.completed
    if (state.filter === 'completed') return todo.completed
    return true
  })

  return (
    <div>
      <input
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            dispatch({ type: 'add', text: e.currentTarget.value })
            e.currentTarget.value = ''
          }
        }}
      />
      <ul>
        {filteredTodos.map((todo) => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => dispatch({ type: 'toggle', id: todo.id })}
            />
            {todo.text}
            <button onClick={() => dispatch({ type: 'delete', id: todo.id })}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

#### When to Use useReducer vs useState

✅ **Use useReducer when:**
- Multiple state values that change together
- Complex state updates
- State logic is complex (multiple actions)
- Want to extract state logic (testable)

✅ **Use useState when:**
- Simple, independent state
- Single value
- Simple updates

## Effect Hooks

### useEffect

Runs side effects after render.

#### Basic Usage

```typescript
import { useEffect } from 'react'

function Component() {
  useEffect(() => {
    // Effect code runs after render
    console.log('Component mounted or updated')

    // Cleanup function (optional)
    return () => {
      console.log('Component unmounted or before next effect')
    }
  })

  return <div>Component</div>
}
```

#### Dependency Array

```typescript
// ❌ NO dependency array: Runs after EVERY render
useEffect(() => {
  console.log('Every render')
})

// ✅ Empty array: Runs ONCE (mount only)
useEffect(() => {
  console.log('Mount only')
}, [])

// ✅ With dependencies: Runs when dependencies change
useEffect(() => {
  console.log('Count changed:', count)
}, [count])

// ✅ Multiple dependencies
useEffect(() => {
  console.log('Count or name changed')
}, [count, name])
```

#### Cleanup Function

```typescript
// Event listener cleanup
useEffect(() => {
  const handleResize = () => {
    console.log('Window resized')
  }

  window.addEventListener('resize', handleResize)

  return () => {
    window.removeEventListener('resize', handleResize)
  }
}, [])

// Timer cleanup
useEffect(() => {
  const timer = setInterval(() => {
    console.log('Tick')
  }, 1000)

  return () => clearInterval(timer)
}, [])

// Subscription cleanup
useEffect(() => {
  const subscription = dataSource.subscribe(() => {
    // Handle data
  })

  return () => subscription.unsubscribe()
}, [])
```

#### Common Patterns

**Data Fetching:**

```typescript
function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchUser() {
      try {
        setLoading(true)
        const response = await fetch(`/api/users/${userId}`)
        const data = await response.json()

        if (!cancelled) {
          setUser(data)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Unknown error'))
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchUser()

    return () => {
      cancelled = true
    }
  }, [userId])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!user) return null

  return <div>{user.name}</div>
}
```

**Local Storage Sync:**

```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const saved = localStorage.getItem(key)
    return saved ? JSON.parse(saved) : initialValue
  })

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value))
  }, [key, value])

  return [value, setValue] as const
}

// Usage
function Component() {
  const [theme, setTheme] = useLocalStorage('theme', 'light')
  return <div>Theme: {theme}</div>
}
```

**Document Title:**

```typescript
function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = title
  }, [title])
}

// Usage
function Page() {
  useDocumentTitle('My Page Title')
  return <div>Content</div>
}
```

### useLayoutEffect

Same as useEffect but fires synchronously after DOM mutations.

#### When to Use

✅ **Use useLayoutEffect when:**
- Measuring DOM elements
- Synchronous DOM mutations before paint
- Preventing visual flicker

⚠️ **WARNING**: Blocks visual updates, use sparingly!

#### Example: Measuring DOM

```typescript
import { useLayoutEffect, useRef, useState } from 'react'

function MeasuredComponent() {
  const ref = useRef<HTMLDivElement>(null)
  const [height, setHeight] = useState(0)

  useLayoutEffect(() => {
    if (ref.current) {
      setHeight(ref.current.getBoundingClientRect().height)
    }
  }, [])

  return (
    <div>
      <div ref={ref}>Content to measure</div>
      <p>Height: {height}px</p>
    </div>
  )
}
```

#### Example: Preventing Flicker

```typescript
function TooltipPosition({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect()

      // Reposition if off-screen
      if (rect.right > window.innerWidth) {
        ref.current.style.right = '0'
        ref.current.style.left = 'auto'
      }
    }
  })

  return <div ref={ref} className="tooltip">{children}</div>
}
```

## Ref Hooks

### useRef

Creates a mutable ref object.

#### DOM References

```typescript
import { useRef, useEffect } from 'react'

function AutoFocusInput() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus()
  }, [])

  return <input ref={inputRef} />
}
```

#### Mutable Values

```typescript
function Timer() {
  const [count, setCount] = useState(0)
  const intervalRef = useRef<number | null>(null)

  const start = () => {
    if (intervalRef.current !== null) return

    intervalRef.current = window.setInterval(() => {
      setCount((c) => c + 1)
    }, 1000)
  }

  const stop = () => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  useEffect(() => {
    return () => stop()
  }, [])

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  )
}
```

#### Previous Value

```typescript
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>()

  useEffect(() => {
    ref.current = value
  }, [value])

  return ref.current
}

// Usage
function Component({ count }: { count: number }) {
  const prevCount = usePrevious(count)

  return (
    <div>
      Current: {count}, Previous: {prevCount}
    </div>
  )
}
```

#### Imperative Handle (Advanced)

```typescript
import { useImperativeHandle, forwardRef, useRef } from 'react'

interface InputHandle {
  focus: () => void
  clear: () => void
}

const CustomInput = forwardRef<InputHandle, {}>((props, ref) => {
  const inputRef = useRef<HTMLInputElement>(null)

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
    clear: () => {
      if (inputRef.current) inputRef.current.value = ''
    },
  }))

  return <input ref={inputRef} />
})

// Usage
function Parent() {
  const inputRef = useRef<InputHandle>(null)

  return (
    <div>
      <CustomInput ref={inputRef} />
      <button onClick={() => inputRef.current?.focus()}>Focus</button>
      <button onClick={() => inputRef.current?.clear()}>Clear</button>
    </div>
  )
}
```

## Context Hooks

### useContext

Reads context value.

#### Basic Usage

```typescript
import { createContext, useContext, ReactNode } from 'react'

// Define context type
interface ThemeContextType {
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

// Create context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

// Provider component
function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

// Custom hook for consuming context
function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

// Consumer component
function ThemedButton() {
  const { theme, setTheme } = useTheme()

  return (
    <button
      className={theme}
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      Toggle Theme
    </button>
  )
}
```

#### Multiple Contexts

```typescript
interface User {
  id: string
  name: string
}

const UserContext = createContext<User | null>(null)
const ThemeContext = createContext<'light' | 'dark'>('light')

function App() {
  return (
    <UserContext.Provider value={{ id: '1', name: 'Alice' }}>
      <ThemeContext.Provider value="dark">
        <Dashboard />
      </ThemeContext.Provider>
    </UserContext.Provider>
  )
}

function Dashboard() {
  const user = useContext(UserContext)
  const theme = useContext(ThemeContext)

  return (
    <div className={theme}>
      {user ? `Welcome, ${user.name}` : 'Not logged in'}
    </div>
  )
}
```

## Performance Hooks

### useMemo

Memoizes expensive computations.

#### When to Use

✅ **Use when:**
- Expensive computations
- Referential equality matters
- Preventing child re-renders

❌ **Don't use when:**
- Simple computations
- Premature optimization

#### Basic Usage

```typescript
import { useMemo } from 'react'

function ExpensiveComponent({ items }: { items: string[] }) {
  // ❌ BAD: Computes on every render
  const sorted = items.slice().sort()

  // ✅ GOOD: Only recomputes when items change
  const sorted = useMemo(() => {
    return items.slice().sort()
  }, [items])

  return (
    <ul>
      {sorted.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  )
}
```

#### Complex Example

```typescript
interface Product {
  id: string
  name: string
  price: number
  category: string
}

function ProductList({ products, filter }: Props) {
  const filteredAndSorted = useMemo(() => {
    console.log('Computing filtered and sorted products')

    return products
      .filter((p) => p.category === filter)
      .sort((a, b) => a.price - b.price)
  }, [products, filter])

  return (
    <ul>
      {filteredAndSorted.map((product) => (
        <ProductItem key={product.id} product={product} />
      ))}
    </ul>
  )
}
```

### useCallback

Memoizes function references.

#### When to Use

✅ **Use when:**
- Passing callbacks to memoized children
- Dependencies in useEffect
- Referential equality matters

❌ **Don't use when:**
- Function not passed to children
- Premature optimization

#### Basic Usage

```typescript
import { useCallback } from 'react'

function Parent() {
  const [count, setCount] = useState(0)

  // ❌ BAD: New function on every render
  const increment = () => setCount(count + 1)

  // ✅ GOOD: Stable function reference
  const increment = useCallback(() => {
    setCount((c) => c + 1)
  }, [])

  return <Child onIncrement={increment} />
}

const Child = React.memo(({ onIncrement }: Props) => {
  console.log('Child rendered')
  return <button onClick={onIncrement}>Increment</button>
})
```

#### With Dependencies

```typescript
function SearchComponent({ onSearch }: { onSearch: (query: string) => void }) {
  const [query, setQuery] = useState('')

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query)
    }
  }, [query, onSearch])

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleSearch}>Search</button>
    </div>
  )
}
```

## Transition Hooks

### useTransition

Marks state updates as non-urgent (See [transitions.md](./transitions.md) for complete guide).

```typescript
import { useTransition } from 'react'

function SearchResults() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value: string) => {
    // Urgent: Update input immediately
    setQuery(value)

    // Non-urgent: Update results in background
    startTransition(() => {
      const filtered = searchData(value)
      setResults(filtered)
    })
  }

  return (
    <div>
      <input value={query} onChange={(e) => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
      <ResultsList results={results} />
    </div>
  )
}
```

### useDeferredValue

Defers updating a value.

```typescript
import { useDeferredValue } from 'react'

function SearchResults({ query }: { query: string }) {
  const deferredQuery = useDeferredValue(query)

  // deferredQuery lags behind query
  const results = useMemo(() => {
    return searchData(deferredQuery)
  }, [deferredQuery])

  return (
    <div>
      <p>Searching for: {query}</p>
      {query !== deferredQuery && <Spinner />}
      <ResultsList results={results} />
    </div>
  )
}
```

### useId

Generates unique IDs for accessibility.

```typescript
import { useId } from 'react'

function FormField({ label }: { label: string }) {
  const id = useId()

  return (
    <div>
      <label htmlFor={id}>{label}</label>
      <input id={id} />
    </div>
  )
}
```

## New React 19 Hooks

### use (React 19)

Reads promises and context in render.

```typescript
import { use } from 'react'

// With promises
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  // use() unwraps the promise
  const user = use(userPromise)

  return <div>{user.name}</div>
}

// With context
function ThemedButton() {
  const theme = use(ThemeContext)
  return <button className={theme}>Click</button>
}
```

### useOptimistic (React 19)

Optimistic UI updates.

```typescript
import { useOptimistic } from 'react'

interface Todo {
  id: string
  text: string
  pending?: boolean
}

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: string) => [
      ...state,
      { id: `temp-${Date.now()}`, text: newTodo, pending: true },
    ]
  )

  async function createTodo(formData: FormData) {
    const text = formData.get('todo') as string
    addOptimisticTodo(text)

    await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ text }),
    })
  }

  return (
    <div>
      <form action={createTodo}>
        <input name="todo" />
        <button type="submit">Add</button>
      </form>
      <ul>
        {optimisticTodos.map((todo) => (
          <li key={todo.id} className={todo.pending ? 'pending' : ''}>
            {todo.text}
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### useFormStatus (React 19)

Form submission status.

```typescript
'use client'

import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending, data, method, action } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

function MyForm() {
  async function handleSubmit(formData: FormData) {
    await new Promise((resolve) => setTimeout(resolve, 2000))
    console.log('Submitted:', formData.get('name'))
  }

  return (
    <form action={handleSubmit}>
      <input name="name" />
      <SubmitButton />
    </form>
  )
}
```

### useActionState (React 19)

Manages Server Action state.

```typescript
'use client'

import { useActionState } from 'react'

interface FormState {
  message: string
  errors?: Record<string, string[]>
}

async function createProject(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  const name = formData.get('name') as string

  if (!name) {
    return {
      message: 'Validation failed',
      errors: { name: ['Name is required'] },
    }
  }

  try {
    await fetch('/api/projects', {
      method: 'POST',
      body: JSON.stringify({ name }),
    })

    return { message: 'Project created successfully' }
  } catch (error) {
    return { message: 'Failed to create project' }
  }
}

function CreateProjectForm() {
  const [state, formAction] = useActionState(createProject, {
    message: '',
  })

  return (
    <form action={formAction}>
      <input name="name" />
      {state.errors?.name && <p className="error">{state.errors.name[0]}</p>}
      <button type="submit">Create</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

## Custom Hooks

### Rules for Custom Hooks

1. Name must start with `use`
2. Can call other hooks
3. Should be reusable
4. Return values or functions

### Example: useDebounce

```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

// Usage
function SearchInput() {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 500)

  useEffect(() => {
    if (debouncedQuery) {
      // Search with debounced value
      search(debouncedQuery)
    }
  }, [debouncedQuery])

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />
}
```

### Example: useAsync

```typescript
interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

function useAsync<T>(
  asyncFunction: () => Promise<T>,
  dependencies: any[] = []
): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    setState({ data: null, loading: true, error: null })

    asyncFunction()
      .then((data) => {
        if (!cancelled) {
          setState({ data, loading: false, error: null })
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setState({ data: null, loading: false, error })
        }
      })

    return () => {
      cancelled = true
    }
  }, dependencies)

  return state
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data: user, loading, error } = useAsync(
    () => fetch(`/api/users/${userId}`).then((r) => r.json()),
    [userId]
  )

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!user) return null

  return <div>{user.name}</div>
}
```

### Example: useMediaQuery

```typescript
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

// Usage
function ResponsiveComponent() {
  const isMobile = useMediaQuery('(max-width: 768px)')
  const isDesktop = useMediaQuery('(min-width: 1024px)')

  return (
    <div>
      {isMobile && <MobileView />}
      {isDesktop && <DesktopView />}
    </div>
  )
}
```

### Example: useOnClickOutside

```typescript
function useOnClickOutside<T extends HTMLElement>(
  ref: React.RefObject<T>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return
      }
      handler(event)
    }

    document.addEventListener('mousedown', listener)
    document.addEventListener('touchstart', listener)

    return () => {
      document.removeEventListener('mousedown', listener)
      document.removeEventListener('touchstart', listener)
    }
  }, [ref, handler])
}

// Usage
function Modal({ onClose }: { onClose: () => void }) {
  const modalRef = useRef<HTMLDivElement>(null)
  useOnClickOutside(modalRef, onClose)

  return (
    <div ref={modalRef} className="modal">
      Modal content
    </div>
  )
}
```

---

**Next**: Read [suspense-patterns.md](./suspense-patterns.md) for Suspense and streaming patterns.
