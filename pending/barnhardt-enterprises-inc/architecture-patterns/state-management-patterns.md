# State Management Patterns

## Decision Tree

```
What kind of state do you have?

├─ Server data (from API/database)
│  └─ Use React Query (useQuery, useMutation)
│
├─ Local UI state (toggle, input value)
│  └─ Use useState
│
├─ Shared UI state (theme, sidebar open)
│  └─ Use Context API
│
├─ URL parameters (filters, pagination)
│  └─ Use Next.js useSearchParams
│
└─ Form data (complex forms)
   └─ Use React Hook Form + Zod
```

---

## 1. Server State → React Query

**Use for:** API data, database queries, remote state

```typescript
'use client'

import { useQuery, useMutation } from '@tanstack/react-query'

export function ProjectsList() {
  // Fetch data
  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => fetch('/api/projects').then(r => r.json()),
  })

  // Mutate data
  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/projects/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  if (isLoading) return <Skeleton />
  if (error) return <Error error={error} />

  return (
    <ul>
      {data.map((project) => (
        <li key={project.id}>
          {project.name}
          <button onClick={() => deleteMutation.mutate(project.id)}>
            Delete
          </button>
        </li>
      ))}
    </ul>
  )
}
```

---

## 2. Local UI State → useState

**Use for:** Component-specific state, toggles, input values

```typescript
'use client'

import { useState } from 'react'

export function Accordion() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Collapse' : 'Expand'}
      </button>
      {isOpen && <div>Content here</div>}
    </div>
  )
}
```

---

## 3. Shared UI State → Context

**Use for:** Theme, auth state, sidebar state (across multiple components)

```typescript
'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
```

**Usage:**
```typescript
export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  return (
    <button onClick={toggleTheme}>
      Current: {theme}
    </button>
  )
}
```

---

## 4. URL State → useSearchParams

**Use for:** Filters, pagination, search queries (shareable via URL)

```typescript
'use client'

import { useSearchParams, useRouter } from 'next/navigation'

export function ProjectFilters() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const status = searchParams.get('status') || 'all'

  const setStatus = (newStatus: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('status', newStatus)
    router.push(`/projects?${params.toString()}`)
  }

  return (
    <div>
      <button onClick={() => setStatus('active')}>Active</button>
      <button onClick={() => setStatus('completed')}>Completed</button>
      <button onClick={() => setStatus('all')}>All</button>
    </div>
  )
}
```

---

## 5. Form State → React Hook Form + Zod

**Use for:** Complex forms with validation

```typescript
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const formSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().min(0).max(150),
})

type FormData = z.infer<typeof formSchema>

export function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  })

  const onSubmit = async (data: FormData) => {
    await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      {errors.name && <span>{errors.name.message}</span>}

      <input {...register('email')} type="email" />
      {errors.email && <span>{errors.email.message}</span>}

      <input {...register('age', { valueAsNumber: true })} type="number" />
      {errors.age && <span>{errors.age.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        Submit
      </button>
    </form>
  )
}
```

---

## Pattern Comparison

| Pattern | Use Case | Persistence | Shareable |
|---------|----------|-------------|-----------|
| React Query | Server data | Cache only | No |
| useState | Local UI | Component only | No |
| Context | Shared UI | App lifetime | No |
| useSearchParams | Filters | URL | Yes (via URL) |
| React Hook Form | Complex forms | Form lifetime | No |

---

## Anti-Patterns

### ❌ Using useState for server data
```typescript
// DON'T: Manual fetching with useState
const [data, setData] = useState(null)
useEffect(() => {
  fetch('/api/data').then(r => r.json()).then(setData)
}, [])
```

**Fix:** Use React Query or Server Component

---

### ❌ Using Context for server data
```typescript
// DON'T: Context for API data
const ProjectsContext = createContext()
// ... fetching projects in context provider
```

**Fix:** Use React Query (caching, refetching, error handling built-in)

---

### ❌ Prop drilling instead of Context
```typescript
// DON'T: Passing theme through 5 levels
<App theme={theme}>
  <Layout theme={theme}>
    <Sidebar theme={theme}>
      <Menu theme={theme}>
        <MenuItem theme={theme} />
```

**Fix:** Use Context for shared UI state

---

## See Also

- [nextjs-patterns.md](./nextjs-patterns.md) - Server vs Client Components
- [../react-19-patterns/SKILL.md](../react-19-patterns/SKILL.md) - React 19 state features
- [../zod-validation-patterns/SKILL.md](../zod-validation-patterns/SKILL.md) - Form validation
