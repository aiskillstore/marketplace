# React 18 → React 19 Migration Guide

## Overview

React 19 includes breaking changes and new features. This guide helps you migrate from React 18.x to React 19.x.

## Breaking Changes

### 1. Removed Legacy APIs

#### ReactDOM.render (Removed)

```typescript
// ❌ React 18 (deprecated)
import ReactDOM from 'react-dom'

ReactDOM.render(<App />, document.getElementById('root'))

// ✅ React 19 (must use createRoot)
import { createRoot } from 'react-dom/client'

const root = createRoot(document.getElementById('root')!)
root.render(<App />)
```

#### ReactDOM.hydrate (Removed)

```typescript
// ❌ React 18 (deprecated)
import ReactDOM from 'react-dom'

ReactDOM.hydrate(<App />, document.getElementById('root'))

// ✅ React 19 (must use hydrateRoot)
import { hydrateRoot } from 'react-dom/client'

hydrateRoot(document.getElementById('root')!, <App />)
```

### 2. String Refs (Removed)

```typescript
// ❌ React 18 (deprecated)
class Component extends React.Component {
  componentDidMount() {
    this.refs.input.focus() // String ref
  }

  render() {
    return <input ref="input" />
  }
}

// ✅ React 19 (use callback or createRef)
class Component extends React.Component {
  inputRef = React.createRef<HTMLInputElement>()

  componentDidMount() {
    this.inputRef.current?.focus()
  }

  render() {
    return <input ref={this.inputRef} />
  }
}

// ✅ React 19 (function components)
function Component() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return <input ref={inputRef} />
}
```

### 3. defaultProps (Removed for Function Components)

```typescript
// ❌ React 18
function Button({ color = 'blue', size = 'medium' }) {
  return <button>{/* ... */}</button>
}

Button.defaultProps = {
  color: 'blue',
  size: 'medium',
}

// ✅ React 19 (use default parameters)
function Button({ color = 'blue', size = 'medium' }) {
  return <button>{/* ... */}</button>
}

// ✅ React 19 (with TypeScript)
interface ButtonProps {
  color?: string
  size?: 'small' | 'medium' | 'large'
}

function Button({ color = 'blue', size = 'medium' }: ButtonProps) {
  return <button>{/* ... */}</button>
}
```

### 4. Context.Provider Pattern Change

```typescript
// ❌ React 18
const ThemeContext = React.createContext('light')

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Component />
    </ThemeContext.Provider>
  )
}

// ✅ React 19 (simplified - just Context works)
const ThemeContext = React.createContext('light')

function App() {
  return (
    <ThemeContext value="dark">
      <Component />
    </ThemeContext>
  )
}

// Both patterns work in React 19, but simplified is preferred
```

### 5. Automatic Batching (Now Default)

```typescript
// React 18: Manual batching needed outside React events
import { unstable_batchedUpdates } from 'react-dom'

function handleClick() {
  fetch('/api/data').then(() => {
    unstable_batchedUpdates(() => {
      setCount((c) => c + 1)
      setFlag((f) => !f)
    })
  })
}

// ✅ React 19: Automatic batching everywhere
function handleClick() {
  fetch('/api/data').then(() => {
    // Automatically batched!
    setCount((c) => c + 1)
    setFlag((f) => !f)
  })
}
```

## New Features in React 19

### 1. use() Hook

```typescript
// ❌ React 18: Manual promise handling
function Component() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchData().then(setData)
  }, [])

  if (!data) return <Loading />
  return <div>{data}</div>
}

// ✅ React 19: use() hook
import { use } from 'react'

function Component({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise)
  return <div>{data}</div>
}

// Wrap with Suspense
function Page() {
  const dataPromise = fetchData()

  return (
    <Suspense fallback={<Loading />}>
      <Component dataPromise={dataPromise} />
    </Suspense>
  )
}
```

### 2. useOptimistic() Hook

```typescript
// ❌ React 18: Manual optimistic updates
function TodoList({ todos }: Props) {
  const [optimisticTodos, setOptimisticTodos] = useState(todos)

  async function addTodo(text: string) {
    // Optimistically add
    const tempTodo = { id: 'temp', text, pending: true }
    setOptimisticTodos([...optimisticTodos, tempTodo])

    try {
      const newTodo = await createTodo(text)
      // Replace temp with real
      setOptimisticTodos((prev) =>
        prev.map((t) => (t.id === 'temp' ? newTodo : t))
      )
    } catch (error) {
      // Revert on error
      setOptimisticTodos(todos)
    }
  }
}

// ✅ React 19: useOptimistic hook
import { useOptimistic } from 'react'

function TodoList({ todos }: Props) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: string) => [
      ...state,
      { id: 'temp', text: newTodo, pending: true },
    ]
  )

  async function addTodo(formData: FormData) {
    const text = formData.get('text') as string
    addOptimisticTodo(text)
    await createTodo(text)
  }

  return (
    <form action={addTodo}>
      <input name="text" />
      <button type="submit">Add</button>
      <ul>
        {optimisticTodos.map((todo) => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    </form>
  )
}
```

### 3. useFormStatus() Hook

```typescript
// ❌ React 18: Manual form state tracking
function Form() {
  const [pending, setPending] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPending(true)

    try {
      await submitForm(new FormData(e.currentTarget))
    } finally {
      setPending(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" />
      <button disabled={pending}>
        {pending ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}

// ✅ React 19: useFormStatus hook
import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

function Form() {
  async function handleSubmit(formData: FormData) {
    await submitForm(formData)
  }

  return (
    <form action={handleSubmit}>
      <input name="name" />
      <SubmitButton />
    </form>
  )
}
```

### 4. useActionState() Hook

```typescript
// ❌ React 18: Manual action state
function Form() {
  const [state, setState] = useState({ message: '', errors: {} })
  const [pending, setPending] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPending(true)

    try {
      const result = await submitAction(new FormData(e.currentTarget))
      setState(result)
    } finally {
      setPending(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" />
      {state.errors.name && <p>{state.errors.name}</p>}
      <button disabled={pending}>Submit</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}

// ✅ React 19: useActionState hook
import { useActionState } from 'react'

async function submitAction(prevState: State, formData: FormData): Promise<State> {
  const name = formData.get('name') as string

  if (!name) {
    return {
      message: 'Validation failed',
      errors: { name: 'Name is required' },
    }
  }

  try {
    await saveData(name)
    return { message: 'Success!' }
  } catch (error) {
    return { message: 'Error occurred' }
  }
}

function Form() {
  const [state, formAction] = useActionState(submitAction, {
    message: '',
  })

  return (
    <form action={formAction}>
      <input name="name" />
      {state.errors?.name && <p>{state.errors.name}</p>}
      <button type="submit">Submit</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

### 5. Enhanced Transitions

```typescript
// React 18: Basic transitions
import { useTransition } from 'react'

function Component() {
  const [isPending, startTransition] = useTransition()

  const handleClick = () => {
    startTransition(() => {
      setTab('new-tab')
    })
  }
}

// ✅ React 19: Enhanced with better interruption
import { useTransition } from 'react'

function Component() {
  const [isPending, startTransition] = useTransition()

  const handleClick = () => {
    startTransition(() => {
      // Better interruption handling
      // Automatically cancels previous transition
      setTab('new-tab')
    })
  }
}
```

## Migration Steps

### Step 1: Update Dependencies

```bash
# Update to React 19
npm install react@19 react-dom@19

# Update TypeScript types (if using TypeScript)
npm install --save-dev @types/react@19 @types/react-dom@19

# Update Next.js (if using Next.js)
npm install next@15
```

### Step 2: Update Root Rendering

```typescript
// src/index.tsx (React 18)
import ReactDOM from 'react-dom'
import App from './App'

ReactDOM.render(<App />, document.getElementById('root'))

// src/index.tsx (React 19)
import { createRoot } from 'react-dom/client'
import App from './App'

const root = createRoot(document.getElementById('root')!)
root.render(<App />)
```

### Step 3: Remove String Refs

```bash
# Find all string refs
grep -r 'ref="' src/

# Replace with useRef or createRef
```

### Step 4: Remove defaultProps

```typescript
// Find components with defaultProps
// Replace with default parameters

// Before
function Button({ color, size }) {
  return <button>{/* ... */}</button>
}
Button.defaultProps = { color: 'blue', size: 'medium' }

// After
function Button({ color = 'blue', size = 'medium' }) {
  return <button>{/* ... */}</button>
}
```

### Step 5: Adopt New Features

```typescript
// 1. Use use() for async data
const data = use(dataPromise)

// 2. Use useOptimistic for optimistic UI
const [optimisticState, addOptimistic] = useOptimistic(state, updater)

// 3. Use useFormStatus for form state
const { pending } = useFormStatus()

// 4. Use useActionState for server actions
const [state, formAction] = useActionState(action, initialState)
```

## TypeScript Changes

### Type Updates

```typescript
// React 19 has improved types

// ✅ Better inference for refs
const inputRef = useRef<HTMLInputElement>(null)
// No need for null check in some cases

// ✅ Better event types
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  // e.target is properly typed
}

// ✅ Better children types
interface Props {
  children: React.ReactNode // Preferred over React.ReactElement
}
```

## Common Issues and Solutions

### Issue 1: Hydration Mismatch

```typescript
// ❌ Problem: Different content on server and client
function Component() {
  return <div>{Date.now()}</div>
}

// ✅ Solution: Use useEffect for client-only code
function Component() {
  const [time, setTime] = useState<number | null>(null)

  useEffect(() => {
    setTime(Date.now())
  }, [])

  return <div>{time ?? 'Loading...'}</div>
}
```

### Issue 2: Context Provider Warning

```typescript
// ⚠️ Warning: Using Context.Provider still works but is deprecated

// ✅ Update to new pattern (optional)
<ThemeContext value="dark">
  <App />
</ThemeContext>
```

### Issue 3: StrictMode Double Rendering

```typescript
// React 19 StrictMode intentionally double-renders in development

// ✅ Ensure effects are idempotent
useEffect(() => {
  const subscription = subscribe()

  return () => {
    subscription.unsubscribe() // Cleanup properly
  }
}, [])
```

## Performance Improvements

### 1. Automatic Batching

React 19 batches all updates automatically:

```typescript
// React 18: Only batched in React events
// React 19: Batched everywhere (including promises, setTimeout)

fetch('/api/data').then(() => {
  setCount(1)
  setFlag(true)
  // Both updates batched into single render in React 19
})
```

### 2. Better Concurrent Rendering

```typescript
// React 19 has improved concurrent rendering

// Use Suspense more aggressively
<Suspense fallback={<Skeleton />}>
  <ExpensiveComponent />
</Suspense>

// Use transitions for non-urgent updates
const [isPending, startTransition] = useTransition()
startTransition(() => {
  setResults(expensiveFilter(query))
})
```

## Testing Updates

### Update Test Setup

```typescript
// Before (React 18)
import { render } from '@testing-library/react'

test('component', () => {
  const { container } = render(<Component />)
  // Tests
})

// After (React 19) - Same API!
import { render } from '@testing-library/react'

test('component', () => {
  const { container } = render(<Component />)
  // Tests work the same
})
```

### Test Async Components

```typescript
// Test Server Components with Suspense
import { render, waitFor } from '@testing-library/react'

test('async component', async () => {
  const { getByText } = render(
    <Suspense fallback={<div>Loading...</div>}>
      <AsyncComponent />
    </Suspense>
  )

  expect(getByText('Loading...')).toBeInTheDocument()

  await waitFor(() => {
    expect(getByText('Content')).toBeInTheDocument()
  })
})
```

## Checklist

- [ ] Update react and react-dom to version 19
- [ ] Update @types/react and @types/react-dom to version 19
- [ ] Replace ReactDOM.render with createRoot
- [ ] Replace ReactDOM.hydrate with hydrateRoot
- [ ] Remove all string refs
- [ ] Remove defaultProps from function components
- [ ] Update tests if needed
- [ ] Adopt new hooks (use, useOptimistic, useFormStatus, useActionState)
- [ ] Test application thoroughly
- [ ] Update CI/CD if needed

---

**Congratulations!** You've migrated to React 19. Explore the new hooks and concurrent features to improve your app's performance and user experience.
