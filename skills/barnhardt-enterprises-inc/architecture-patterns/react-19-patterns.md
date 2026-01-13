# React 19 Patterns

For complete React 19 patterns, see: [react-19-patterns skill](../react-19-patterns/SKILL.md)

## Quick Reference

### 1. use() Hook

Read resources (Promises, Context) in components:

```typescript
import { use } from 'react'

// Use with Promises
async function fetchData() {
  const res = await fetch('/api/data')
  return res.json()
}

export function Component() {
  const dataPromise = fetchData()
  const data = use(dataPromise)

  return <div>{data.value}</div>
}

// Use with Context
const ThemeContext = createContext('light')

export function ThemedButton() {
  const theme = use(ThemeContext)
  return <button className={theme}>Click me</button>
}
```

---

### 2. useOptimistic

Optimistic UI updates for better UX:

```typescript
'use client'

import { useOptimistic } from 'react'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, newTodo]
  )

  const handleAdd = async (formData: FormData) => {
    const newTodo = {
      id: crypto.randomUUID(),
      text: formData.get('text') as string,
      done: false,
    }

    // Immediately show in UI
    addOptimisticTodo(newTodo)

    // Send to server
    await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify(newTodo),
    })
  }

  return (
    <ul>
      {optimisticTodos.map((todo) => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  )
}
```

---

### 3. useFormStatus

Access form submission state:

```typescript
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending, data, method, action } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

// Use in form
export function MyForm() {
  return (
    <form action={handleSubmit}>
      <input name="email" />
      <SubmitButton />
    </form>
  )
}
```

---

### 4. useActionState

Manage server action state:

```typescript
'use client'

import { useActionState } from 'react'

async function createUser(prevState: any, formData: FormData) {
  const name = formData.get('name')
  // ... validation and creation
  return { success: true, message: 'User created' }
}

export function UserForm() {
  const [state, formAction, isPending] = useActionState(
    createUser,
    { success: false, message: '' }
  )

  return (
    <form action={formAction}>
      <input name="name" />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create User'}
      </button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

---

### 5. Server Actions

Functions that run on the server:

```typescript
'use server'

import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
})

export async function createProject(formData: FormData) {
  const validated = createProjectSchema.parse({
    name: formData.get('name'),
  })

  const project = await db
    .insert(projectsTable)
    .values(validated)
    .returning()

  revalidatePath('/projects')
  return project[0]
}
```

**Usage:**
```typescript
// In Server Component
export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  )
}

// In Client Component
'use client'

export function CreateProjectForm() {
  const handleSubmit = async (formData: FormData) => {
    await createProject(formData)
  }

  return (
    <form action={handleSubmit}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

---

### 6. Client Actions

Client-side actions:

```typescript
'use client'

export function SearchForm() {
  const handleSearch = async (formData: FormData) => {
    const query = formData.get('query')
    const results = await fetch(`/api/search?q=${query}`)
      .then(r => r.json())

    // Update UI with results
    setResults(results)
  }

  return (
    <form action={handleSearch}>
      <input name="query" />
      <button type="submit">Search</button>
    </form>
  )
}
```

---

## Pattern Comparison

| Feature | Use Case |
|---------|----------|
| use() | Read Promises/Context in render |
| useOptimistic | Optimistic UI updates |
| useFormStatus | Form submission state |
| useActionState | Server action state management |
| Server Actions | Form submissions, mutations |
| Client Actions | Client-side form handling |

---

## See Also

- [react-19-patterns/SKILL.md](../react-19-patterns/SKILL.md) - Complete patterns
- [nextjs-patterns.md](./nextjs-patterns.md) - Next.js integration
- [state-management-patterns.md](./state-management-patterns.md) - State decisions
