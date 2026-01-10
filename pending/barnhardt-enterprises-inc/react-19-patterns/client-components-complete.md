# Client Components - Complete Guide

## Table of Contents

- [Client Components Overview](#client-components-overview)
- ['use client' Directive](#use-client-directive)
- [State Management](#state-management)
- [Event Handlers](#event-handlers)
- [Form Handling](#form-handling)
- [Browser APIs](#browser-apis)
- [Third-Party Libraries](#third-party-libraries)
- [Optimization Techniques](#optimization-techniques)
- [Code Splitting](#code-splitting)
- [Dynamic Imports](#dynamic-imports)
- [Bundle Size Optimization](#bundle-size-optimization)

## Client Components Overview

Client Components run **in the browser**. They:
- Hydrate after initial HTML load
- Enable interactivity (onClick, onChange, etc.)
- Support all React hooks
- Can use browser APIs
- Add to JavaScript bundle

### When to Use

✅ **Use Client Components for:**
- Interactive UI (buttons, forms, modals)
- React hooks (useState, useEffect, useContext)
- Event handlers (onClick, onChange, onSubmit)
- Browser APIs (localStorage, window, geolocation)
- Client-side libraries (animation, charts)

❌ **Don't Use for:**
- Static content (use Server Components)
- Data fetching (prefer Server Components)
- SEO-critical content (use Server Components)

## 'use client' Directive

### Placement Rules

```typescript
// ✅ CORRECT: Top of file, before imports
'use client'

import { useState } from 'react'

export function Component() {
  const [state, setState] = useState(0)
  return <div>{state}</div>
}
```

```typescript
// ❌ WRONG: After imports
import { useState } from 'react'

'use client' // ERROR: Must be at top

export function Component() {}
```

### File-Level Directive

```typescript
// components/Button.tsx
'use client'

// All exports are Client Components
export function Button() {
  return <button onClick={() => alert('Hi')}>Click</button>
}

export function IconButton() {
  return <button onClick={() => alert('Icon')}>🎉</button>
}
```

### Boundary Marking

```typescript
// ✅ Only mark the boundary
// components/InteractiveSection.tsx
'use client'

import { PureComponent } from './PureComponent' // Also becomes client!

export function InteractiveSection() {
  const [open, setOpen] = useState(false)

  return (
    <div>
      <button onClick={() => setOpen(!open)}>Toggle</button>
      {open && <PureComponent />}
    </div>
  )
}
```

## State Management

### useState Patterns

```typescript
'use client'

import { useState } from 'react'

// Simple state
export function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(count - 1)}>Decrement</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  )
}

// Object state
interface FormState {
  name: string
  email: string
  age: number
}

export function Form() {
  const [form, setForm] = useState<FormState>({
    name: '',
    email: '',
    age: 0,
  })

  const updateField = <K extends keyof FormState>(
    field: K,
    value: FormState[K]
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <form>
      <input
        value={form.name}
        onChange={(e) => updateField('name', e.target.value)}
      />
      <input
        value={form.email}
        onChange={(e) => updateField('email', e.target.value)}
      />
      <input
        type="number"
        value={form.age}
        onChange={(e) => updateField('age', parseInt(e.target.value))}
      />
    </form>
  )
}

// Array state
export function TodoList() {
  const [todos, setTodos] = useState<string[]>([])
  const [input, setInput] = useState('')

  const addTodo = () => {
    setTodos((prev) => [...prev, input])
    setInput('')
  }

  const removeTodo = (index: number) => {
    setTodos((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={addTodo}>Add</button>
      <ul>
        {todos.map((todo, i) => (
          <li key={i}>
            {todo}
            <button onClick={() => removeTodo(i)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### useReducer for Complex State

```typescript
'use client'

import { useReducer } from 'react'

interface State {
  count: number
  step: number
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset' }
  | { type: 'setStep'; step: number }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + state.step }
    case 'decrement':
      return { ...state, count: state.count - state.step }
    case 'reset':
      return { ...state, count: 0 }
    case 'setStep':
      return { ...state, step: action.step }
    default:
      return state
  }
}

export function AdvancedCounter() {
  const [state, dispatch] = useReducer(reducer, { count: 0, step: 1 })

  return (
    <div>
      <p>Count: {state.count}</p>
      <p>Step: {state.step}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
      <input
        type="number"
        value={state.step}
        onChange={(e) =>
          dispatch({ type: 'setStep', step: parseInt(e.target.value) })
        }
      />
    </div>
  )
}
```

### Context for Global State

```typescript
'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface User {
  id: string
  name: string
  email: string
}

interface AuthContextType {
  user: User | null
  login: (user: User) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  const login = (user: User) => setUser(user)
  const logout = () => setUser(null)

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// Usage
export function LoginButton() {
  const { user, login, logout } = useAuth()

  if (user) {
    return (
      <div>
        <span>Welcome, {user.name}</span>
        <button onClick={logout}>Logout</button>
      </div>
    )
  }

  return (
    <button
      onClick={() =>
        login({ id: '1', name: 'Alice', email: 'alice@example.com' })
      }
    >
      Login
    </button>
  )
}
```

## Event Handlers

### Basic Event Handlers

```typescript
'use client'

export function InteractiveComponent() {
  // Click events
  const handleClick = () => {
    console.log('Clicked!')
  }

  // Mouse events
  const handleMouseEnter = () => {
    console.log('Mouse entered')
  }

  // Keyboard events
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      console.log('Enter pressed')
    }
  }

  // Focus events
  const handleFocus = () => {
    console.log('Focused')
  }

  return (
    <div>
      <button onClick={handleClick}>Click Me</button>
      <div onMouseEnter={handleMouseEnter}>Hover Me</div>
      <input onKeyDown={handleKeyDown} onFocus={handleFocus} />
    </div>
  )
}
```

### Event Delegation

```typescript
'use client'

export function List({ items }: { items: string[] }) {
  const handleItemClick = (e: React.MouseEvent) => {
    const target = e.target as HTMLElement
    const index = target.dataset.index

    console.log('Clicked item:', index)
  }

  return (
    <ul onClick={handleItemClick}>
      {items.map((item, i) => (
        <li key={i} data-index={i}>
          {item}
        </li>
      ))}
    </ul>
  )
}
```

### Synthetic Events

```typescript
'use client'

export function FormWithEvents() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault() // Prevent default form submission

    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData)

    console.log('Form data:', data)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Input changed:', e.target.value)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="username" onChange={handleChange} />
      <button type="submit">Submit</button>
    </form>
  )
}
```

## Form Handling

### Controlled Components

```typescript
'use client'

import { useState } from 'react'

export function ControlledForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const response = await fetch('/api/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    if (response.ok) {
      alert('Form submitted!')
      setFormData({ name: '', email: '', message: '' })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
        required
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
        required
      />
      <button type="submit">Submit</button>
    </form>
  )
}
```

### With Validation

```typescript
'use client'

import { useState } from 'react'

interface Errors {
  name?: string
  email?: string
}

export function ValidatedForm() {
  const [formData, setFormData] = useState({ name: '', email: '' })
  const [errors, setErrors] = useState<Errors>({})

  const validate = (): boolean => {
    const newErrors: Errors = {}

    if (!formData.name) {
      newErrors.name = 'Name is required'
    }

    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (validate()) {
      console.log('Form is valid:', formData)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        {errors.name && <span className="error">{errors.name}</span>}
      </div>

      <div>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>

      <button type="submit">Submit</button>
    </form>
  )
}
```

### React 19 useFormStatus

```typescript
'use client'

import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

export function ModernForm() {
  async function handleSubmit(formData: FormData) {
    // Server Action
    await new Promise((r) => setTimeout(r, 2000))
    console.log('Submitted:', formData.get('name'))
  }

  return (
    <form action={handleSubmit}>
      <input name="name" required />
      <SubmitButton />
    </form>
  )
}
```

## Browser APIs

### LocalStorage

```typescript
'use client'

import { useState, useEffect } from 'react'

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue

    const saved = localStorage.getItem(key)
    return saved ? JSON.parse(saved) : initialValue
  })

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value))
  }, [key, value])

  return [value, setValue] as const
}

// Usage
export function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage('theme', 'light')

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Theme: {theme}
    </button>
  )
}
```

### Geolocation

```typescript
'use client'

import { useState, useEffect } from 'react'

interface Position {
  latitude: number
  longitude: number
}

export function LocationComponent() {
  const [position, setPosition] = useState<Position | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported')
      return
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPosition({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
        })
      },
      (err) => {
        setError(err.message)
      }
    )
  }, [])

  if (error) return <div>Error: {error}</div>
  if (!position) return <div>Loading location...</div>

  return (
    <div>
      Latitude: {position.latitude}, Longitude: {position.longitude}
    </div>
  )
}
```

### IntersectionObserver

```typescript
'use client'

import { useEffect, useRef, useState } from 'react'

export function LazyImage({ src, alt }: { src: string; alt: string }) {
  const [isVisible, setIsVisible] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <img
      ref={imgRef}
      src={isVisible ? src : '/placeholder.png'}
      alt={alt}
      loading="lazy"
    />
  )
}
```

## Third-Party Libraries

### Animation Libraries

```typescript
'use client'

import { motion } from 'framer-motion'

export function AnimatedCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      Card Content
    </motion.div>
  )
}
```

### Chart Libraries

```typescript
'use client'

import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement)

export function LineChart({ data }: { data: number[] }) {
  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        label: 'Sales',
        data: data,
        borderColor: 'rgb(75, 192, 192)',
      },
    ],
  }

  return <Line data={chartData} />
}
```

## Optimization Techniques

### React.memo

```typescript
'use client'

import { memo } from 'react'

interface Props {
  name: string
  count: number
}

// Only re-renders when props change
export const ExpensiveComponent = memo(function ExpensiveComponent({
  name,
  count,
}: Props) {
  console.log('ExpensiveComponent rendered')

  return (
    <div>
      {name}: {count}
    </div>
  )
})
```

### useCallback

```typescript
'use client'

import { useCallback, memo } from 'react'

const Child = memo(({ onClick }: { onClick: () => void }) => {
  console.log('Child rendered')
  return <button onClick={onClick}>Click</button>
})

export function Parent() {
  const [count, setCount] = useState(0)

  // ❌ Without useCallback: Child re-renders every time
  // const handleClick = () => setCount(count + 1)

  // ✅ With useCallback: Child doesn't re-render
  const handleClick = useCallback(() => {
    setCount((c) => c + 1)
  }, [])

  return (
    <div>
      <p>Count: {count}</p>
      <Child onClick={handleClick} />
    </div>
  )
}
```

### useMemo

```typescript
'use client'

import { useMemo } from 'react'

export function ExpensiveList({ items }: { items: number[] }) {
  // ❌ Without useMemo: Computes on every render
  // const sorted = items.slice().sort((a, b) => b - a)

  // ✅ With useMemo: Only recomputes when items change
  const sorted = useMemo(() => {
    console.log('Sorting items...')
    return items.slice().sort((a, b) => b - a)
  }, [items])

  return (
    <ul>
      {sorted.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  )
}
```

## Code Splitting

### Dynamic Imports

```typescript
'use client'

import { lazy, Suspense } from 'react'

// Lazy load heavy component
const HeavyComponent = lazy(() => import('./HeavyComponent'))

export function Page() {
  return (
    <div>
      <h1>Page</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <HeavyComponent />
      </Suspense>
    </div>
  )
}
```

### Conditional Loading

```typescript
'use client'

import { useState, lazy, Suspense } from 'react'

const Modal = lazy(() => import('./Modal'))

export function App() {
  const [showModal, setShowModal] = useState(false)

  return (
    <div>
      <button onClick={() => setShowModal(true)}>Open Modal</button>

      {showModal && (
        <Suspense fallback={<div>Loading modal...</div>}>
          <Modal onClose={() => setShowModal(false)} />
        </Suspense>
      )}
    </div>
  )
}
```

## Bundle Size Optimization

### Tree Shaking

```typescript
// ❌ BAD: Imports entire library
import _ from 'lodash'
const result = _.uniq([1, 2, 2, 3])

// ✅ GOOD: Import only what's needed
import uniq from 'lodash/uniq'
const result = uniq([1, 2, 2, 3])
```

### Dynamic Imports for Heavy Libraries

```typescript
'use client'

import { useState } from 'react'

export function ChartComponent() {
  const [data, setData] = useState([])

  const loadChart = async () => {
    // Only load when needed
    const { Chart } = await import('chart.js')
    // Use Chart
  }

  return <button onClick={loadChart}>Load Chart</button>
}
```

---

**Next**: Read [transitions.md](./transitions.md) for transition patterns.
