# Transitions - Complete Guide

## Table of Contents

- [What are Transitions?](#what-are-transitions)
- [useTransition Hook](#usetransition-hook)
- [startTransition Function](#starttransition-function)
- [isPending State](#ispending-state)
- [useDeferredValue](#usedeferredvalue)
- [Concurrent Features](#concurrent-features)
- [Best Practices](#best-practices)

## What are Transitions?

Transitions let you mark state updates as **non-urgent**, allowing React to:
- Keep UI responsive during expensive updates
- Interrupt non-urgent updates for urgent ones
- Show pending states during transitions
- Improve perceived performance

### Urgent vs Non-Urgent Updates

**Urgent Updates** (immediate):
- Typing in input
- Clicking buttons
- Toggling switches
- Direct user interactions

**Non-Urgent Updates** (can be delayed):
- Search results filtering
- Complex calculations
- Large list rendering
- Data transformations

## useTransition Hook

### Basic Usage

```typescript
'use client'

import { useState, useTransition } from 'react'

export function SearchComponent() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<string[]>([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value: string) => {
    // Urgent: Update input immediately
    setQuery(value)

    // Non-urgent: Filter results in background
    startTransition(() => {
      const filtered = expensiveFilter(value)
      setResults(filtered)
    })
  }

  return (
    <div>
      <input
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search..."
      />
      {isPending && <Spinner />}
      <ResultsList results={results} />
    </div>
  )
}

function expensiveFilter(query: string): string[] {
  // Simulate expensive operation
  const items = Array.from({ length: 10000 }, (_, i) => `Item ${i}`)
  return items.filter((item) => item.toLowerCase().includes(query.toLowerCase()))
}
```

### With TypeScript

```typescript
'use client'

import { useState, useTransition } from 'react'

interface Product {
  id: string
  name: string
  price: number
  category: string
}

export function ProductSearch({ products }: { products: Product[] }) {
  const [query, setQuery] = useState('')
  const [filtered, setFiltered] = useState(products)
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value: string) => {
    setQuery(value)

    startTransition(() => {
      const result = products.filter((p) =>
        p.name.toLowerCase().includes(value.toLowerCase())
      )
      setFiltered(result)
    })
  }

  return (
    <div>
      <input value={query} onChange={(e) => handleSearch(e.target.value)} />
      {isPending ? <Skeleton /> : <ProductList products={filtered} />}
    </div>
  )
}
```

### Multiple Transitions

```typescript
'use client'

import { useState, useTransition } from 'react'

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('projects')
  const [isPending, startTransition] = useTransition()

  const handleTabChange = (tab: string) => {
    startTransition(() => {
      setActiveTab(tab)
    })
  }

  return (
    <div>
      <div className="tabs">
        <button onClick={() => handleTabChange('projects')}>Projects</button>
        <button onClick={() => handleTabChange('users')}>Users</button>
        <button onClick={() => handleTabChange('settings')}>Settings</button>
      </div>

      {isPending && <LoadingBar />}

      <div className={isPending ? 'opacity-50' : ''}>
        {activeTab === 'projects' && <ProjectsTab />}
        {activeTab === 'users' && <UsersTab />}
        {activeTab === 'settings' && <SettingsTab />}
      </div>
    </div>
  )
}
```

## startTransition Function

### Standalone Usage

```typescript
'use client'

import { startTransition } from 'react'

export function FilteredList({ items }: { items: string[] }) {
  const [filter, setFilter] = useState('')
  const [filtered, setFiltered] = useState(items)

  const handleFilter = (value: string) => {
    // Urgent
    setFilter(value)

    // Non-urgent
    startTransition(() => {
      setFiltered(items.filter((item) => item.includes(value)))
    })
  }

  return (
    <div>
      <input value={filter} onChange={(e) => handleFilter(e.target.value)} />
      <ul>
        {filtered.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  )
}
```

### With Router Navigation

```typescript
'use client'

import { startTransition } from 'react'
import { useRouter } from 'next/navigation'

export function NavigationMenu() {
  const router = useRouter()

  const navigate = (path: string) => {
    startTransition(() => {
      router.push(path)
    })
  }

  return (
    <nav>
      <button onClick={() => navigate('/projects')}>Projects</button>
      <button onClick={() => navigate('/users')}>Users</button>
      <button onClick={() => navigate('/settings')}>Settings</button>
    </nav>
  )
}
```

## isPending State

### Loading Indicators

```typescript
'use client'

import { useState, useTransition } from 'react'

export function DataTable({ data }: { data: any[] }) {
  const [sortedData, setSortedData] = useState(data)
  const [isPending, startTransition] = useTransition()

  const handleSort = (key: string) => {
    startTransition(() => {
      const sorted = [...data].sort((a, b) =>
        a[key] > b[key] ? 1 : -1
      )
      setSortedData(sorted)
    })
  }

  return (
    <div>
      <button onClick={() => handleSort('name')}>Sort by Name</button>
      <button onClick={() => handleSort('date')}>Sort by Date</button>

      {isPending && (
        <div className="loading-overlay">
          <Spinner />
        </div>
      )}

      <table className={isPending ? 'opacity-50' : ''}>
        {/* ... */}
      </table>
    </div>
  )
}
```

### Optimistic UI

```typescript
'use client'

import { useState, useTransition } from 'react'

interface Todo {
  id: string
  text: string
  completed: boolean
}

export function TodoList({ initialTodos }: { initialTodos: Todo[] }) {
  const [todos, setTodos] = useState(initialTodos)
  const [isPending, startTransition] = useTransition()

  const toggleTodo = async (id: string) => {
    // Optimistically update UI
    setTodos((prev) =>
      prev.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    )

    // Update server in background
    startTransition(async () => {
      try {
        await fetch(`/api/todos/${id}`, { method: 'PATCH' })
      } catch (error) {
        // Revert on error
        setTodos(initialTodos)
      }
    })
  }

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => toggleTodo(todo.id)}
          />
          {todo.text}
        </li>
      ))}
    </ul>
  )
}
```

## useDeferredValue

### Basic Usage

```typescript
'use client'

import { useState, useDeferredValue, useMemo } from 'react'

export function SearchResults() {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)

  // deferredQuery lags behind query
  const results = useMemo(() => {
    return expensiveSearch(deferredQuery)
  }, [deferredQuery])

  return (
    <div>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />

      {/* Show loading state while deferred */}
      {query !== deferredQuery && <Spinner />}

      <ResultsList results={results} />
    </div>
  )
}
```

### Compared to useTransition

```typescript
// useTransition: Control when state updates happen
function WithTransition() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value: string) => {
    setQuery(value) // Immediate

    startTransition(() => {
      setResults(search(value)) // Deferred
    })
  }

  return <div>{/* ... */}</div>
}

// useDeferredValue: Defer a value
function WithDeferredValue() {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)

  const results = useMemo(() => {
    return search(deferredQuery)
  }, [deferredQuery])

  return <div>{/* ... */}</div>
}
```

### List Filtering

```typescript
'use client'

import { useState, useDeferredValue, useMemo } from 'react'

interface Item {
  id: string
  title: string
  description: string
}

export function FilterableList({ items }: { items: Item[] }) {
  const [filter, setFilter] = useState('')
  const deferredFilter = useDeferredValue(filter)

  const filtered = useMemo(() => {
    return items.filter(
      (item) =>
        item.title.toLowerCase().includes(deferredFilter.toLowerCase()) ||
        item.description.toLowerCase().includes(deferredFilter.toLowerCase())
    )
  }, [items, deferredFilter])

  const isStale = filter !== deferredFilter

  return (
    <div>
      <input
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter items..."
      />

      <div className={isStale ? 'opacity-50' : ''}>
        {filtered.map((item) => (
          <div key={item.id}>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Concurrent Features

### Interrupting Transitions

```typescript
'use client'

import { useState, useTransition } from 'react'

export function InterruptibleSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<string[]>([])
  const [isPending, startTransition] = useTransition()

  const handleSearch = (value: string) => {
    setQuery(value)

    // This will interrupt previous transition if still running
    startTransition(() => {
      const filtered = hugeList.filter((item) =>
        item.toLowerCase().includes(value.toLowerCase())
      )
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

### Progressive Enhancement

```typescript
'use client'

import { useState, useTransition, useDeferredValue } from 'react'

export function ProgressiveList({ items }: { items: string[] }) {
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const [isPending, startTransition] = useTransition()

  const filtered = items.filter((item) =>
    item.toLowerCase().includes(deferredQuery.toLowerCase())
  )

  return (
    <div>
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          startTransition(() => {
            // Trigger re-render
          })
        }}
      />

      {isPending && <ProgressBar />}

      <ul className={isPending ? 'opacity-60' : ''}>
        {filtered.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  )
}
```

## Best Practices

### 1. Use for Expensive Operations

```typescript
// ✅ GOOD: Expensive filtering
startTransition(() => {
  setResults(items.filter(expensiveFilter))
})

// ❌ NOT NEEDED: Simple state update
startTransition(() => {
  setCount(count + 1)
})
```

### 2. Keep Input Responsive

```typescript
// ✅ GOOD: Input updates immediately
const handleChange = (value: string) => {
  setQuery(value) // Urgent

  startTransition(() => {
    setResults(search(value)) // Non-urgent
  })
}
```

### 3. Show Loading States

```typescript
// ✅ GOOD: Indicate pending state
const [isPending, startTransition] = useTransition()

return (
  <div>
    {isPending && <LoadingSpinner />}
    <div className={isPending ? 'opacity-50' : ''}>{content}</div>
  </div>
)
```

### 4. Don't Overuse

```typescript
// ❌ BAD: Every state update
onClick={() => {
  startTransition(() => {
    setSimpleState(true)
  })
}}

// ✅ GOOD: Only expensive operations
onClick={() => {
  setSimpleState(true) // Simple update

  startTransition(() => {
    setExpensiveState(computeExpensive()) // Expensive
  })
}}
```

### 5. Combine with Suspense

```typescript
export function Page() {
  const [tab, setTab] = useState('projects')
  const [isPending, startTransition] = useTransition()

  return (
    <div>
      <button onClick={() => startTransition(() => setTab('projects'))}>
        Projects
      </button>

      <Suspense fallback={<Skeleton />}>
        {tab === 'projects' && <ProjectsTab />}
      </Suspense>

      {isPending && <ProgressBar />}
    </div>
  )
}
```

---

**Next**: Read [streaming-patterns.md](./streaming-patterns.md) for progressive rendering.
