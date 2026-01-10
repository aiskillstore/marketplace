# Next.js 15 Server Actions - Complete Guide

Complete reference for Server Actions in Next.js 15 - server-side mutations and data handling.

**Official Docs:** https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

---

## Table of Contents

- [Basic Server Actions](#basic-server-actions)
- [Form Actions](#form-actions)
- [Button Actions](#button-actions)
- [useFormStatus Hook](#useformstatus-hook)
- [useActionState Hook](#useactionstate-hook)
- [useOptimistic Hook](#useoptimistic-hook)
- [Error Handling](#error-handling)
- [Validation](#validation)
- [Return Values](#return-values)
- [Progressive Enhancement](#progressive-enhancement)
- [Security](#security)
- [Rate Limiting](#rate-limiting)
- [Transactions](#transactions)

---

## Basic Server Actions

Server Actions are asynchronous functions that run on the server.

### Example 1: Inline Server Action

```typescript
// app/projects/page.tsx

export default function ProjectsPage() {
  async function createProject(formData: FormData) {
    'use server'

    const name = formData.get('name') as string
    const description = formData.get('description') as string

    await db.project.create({
      data: { name, description },
    })
  }

  return (
    <form action={createProject}>
      <input name="name" required />
      <textarea name="description" />
      <button type="submit">Create</button>
    </form>
  )
}
```

### Example 2: File-Level Server Action

```typescript
// app/actions.ts
'use server'

import { db } from '@/lib/db'

export async function createProject(formData: FormData) {
  const name = formData.get('name') as string
  const description = formData.get('description') as string

  const project = await db.project.create({
    data: { name, description },
  })

  return { success: true, project }
}

// app/projects/new/page.tsx
import { createProject } from '@/app/actions'

export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" required />
      <textarea name="description" />
      <button type="submit">Create Project</button>
    </form>
  )
}
```

### Example 3: Server Action with Arguments

```typescript
// app/actions.ts
'use server'

export async function updateProject(id: string, formData: FormData) {
  const name = formData.get('name') as string

  const project = await db.project.update({
    where: { id },
    data: { name },
  })

  return project
}

// components/EditProjectForm.tsx
'use client'

import { updateProject } from '@/app/actions'

export function EditProjectForm({ projectId }: { projectId: string }) {
  return (
    <form action={updateProject.bind(null, projectId)}>
      <input name="name" required />
      <button type="submit">Update</button>
    </form>
  )
}
```

---

## Form Actions

Server Actions work seamlessly with HTML forms.

### Example 4: Basic Form Action

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.post.create({
    data: { title, content },
  })

  revalidatePath('/blog')
}

// app/blog/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Publish</button>
    </form>
  )
}
```

### Example 5: Form with Multiple Actions

```typescript
// app/actions.ts
'use server'

export async function savePost(formData: FormData) {
  const title = formData.get('title') as string
  await db.post.create({ data: { title, published: false } })
}

export async function publishPost(formData: FormData) {
  const title = formData.get('title') as string
  await db.post.create({ data: { title, published: true } })
}

// app/blog/new/page.tsx
'use client'

import { savePost, publishPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    <form>
      <input name="title" required />
      <textarea name="content" required />

      <button formAction={savePost}>Save Draft</button>
      <button formAction={publishPost}>Publish</button>
    </form>
  )
}
```

### Example 6: Form with File Upload

```typescript
// app/actions.ts
'use server'

export async function uploadFile(formData: FormData) {
  const file = formData.get('file') as File

  if (!file) {
    throw new Error('No file provided')
  }

  const bytes = await file.arrayBuffer()
  const buffer = Buffer.from(bytes)

  // Save to storage
  await saveToStorage(file.name, buffer)

  return { success: true, fileName: file.name }
}

// app/upload/page.tsx
import { uploadFile } from '@/app/actions'

export default function UploadPage() {
  return (
    <form action={uploadFile}>
      <input type="file" name="file" required />
      <button type="submit">Upload</button>
    </form>
  )
}
```

---

## Button Actions

Call Server Actions from button clicks.

### Example 7: Button with Server Action

```typescript
// app/actions.ts
'use server'

export async function deleteProject(id: string) {
  await db.project.delete({ where: { id } })
  revalidatePath('/projects')
}

// components/DeleteButton.tsx
'use client'

import { deleteProject } from '@/app/actions'

export function DeleteButton({ projectId }: { projectId: string }) {
  return (
    <button
      onClick={async () => {
        await deleteProject(projectId)
      }}
    >
      Delete
    </button>
  )
}
```

### Example 8: Button with Confirmation

```typescript
// components/DeleteButton.tsx
'use client'

import { deleteProject } from '@/app/actions'
import { useState } from 'react'

export function DeleteButton({ projectId }: { projectId: string }) {
  const [loading, setLoading] = useState(false)

  const handleDelete = async () => {
    if (!confirm('Are you sure?')) return

    setLoading(true)
    try {
      await deleteProject(projectId)
    } finally {
      setLoading(false)
    }
  }

  return (
    <button onClick={handleDelete} disabled={loading}>
      {loading ? 'Deleting...' : 'Delete'}
    </button>
  )
}
```

---

## useFormStatus Hook

Track form submission status.

### Example 9: Submit Button with Status

```typescript
// components/SubmitButton.tsx
'use client'

import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

// app/projects/new/page.tsx
import { createProject } from '@/app/actions'
import { SubmitButton } from '@/components/SubmitButton'

export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <input name="name" required />
      <SubmitButton />
    </form>
  )
}
```

### Example 10: Form-Wide Status

```typescript
// components/FormStatus.tsx
'use client'

import { useFormStatus } from 'react-dom'

export function FormStatus() {
  const { pending, data, method, action } = useFormStatus()

  return (
    <div className="form-status">
      {pending && (
        <div className="loading-overlay">
          <Spinner />
          <p>Submitting form...</p>
        </div>
      )}
    </div>
  )
}

// app/projects/new/page.tsx
export default function NewProjectPage() {
  return (
    <form action={createProject}>
      <FormStatus />
      <input name="name" />
      <button type="submit">Create</button>
    </form>
  )
}
```

### Example 11: Conditional UI Based on Status

```typescript
// components/CreateProjectForm.tsx
'use client'

import { useFormStatus } from 'react-dom'

function FormFields() {
  const { pending } = useFormStatus()

  return (
    <div>
      <input name="name" disabled={pending} required />
      <textarea name="description" disabled={pending} />

      {pending && (
        <p className="text-gray-500">Creating project...</p>
      )}

      <button type="submit" disabled={pending}>
        {pending ? 'Creating...' : 'Create Project'}
      </button>
    </div>
  )
}

export function CreateProjectForm({ action }: { action: any }) {
  return (
    <form action={action}>
      <FormFields />
    </form>
  )
}
```

---

## useActionState Hook

Manage Server Action state and errors.

### Example 12: Basic useActionState

```typescript
// app/actions.ts
'use server'

interface ActionState {
  error?: string
  success?: boolean
}

export async function createProject(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  const name = formData.get('name') as string

  if (!name) {
    return { error: 'Name is required' }
  }

  await db.project.create({ data: { name } })

  return { success: true }
}

// components/CreateProjectForm.tsx
'use client'

import { useActionState } from 'react'
import { createProject } from '@/app/actions'

export function CreateProjectForm() {
  const [state, formAction] = useActionState(createProject, {})

  return (
    <form action={formAction}>
      <input name="name" required />

      {state.error && (
        <div className="error">{state.error}</div>
      )}

      {state.success && (
        <div className="success">Project created!</div>
      )}

      <button type="submit">Create</button>
    </form>
  )
}
```

### Example 13: useActionState with Validation

```typescript
// app/actions.ts
'use server'

import { z } from 'zod'

const schema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
})

interface ActionState {
  errors?: Record<string, string[]>
  success?: boolean
}

export async function createProject(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  const result = schema.safeParse({
    name: formData.get('name'),
    description: formData.get('description'),
  })

  if (!result.success) {
    return {
      errors: result.error.flatten().fieldErrors,
    }
  }

  await db.project.create({ data: result.data })

  return { success: true }
}

// components/CreateProjectForm.tsx
'use client'

import { useActionState } from 'react'
import { createProject } from '@/app/actions'

export function CreateProjectForm() {
  const [state, formAction] = useActionState(createProject, {})

  return (
    <form action={formAction}>
      <div>
        <input name="name" />
        {state.errors?.name && (
          <p className="error">{state.errors.name[0]}</p>
        )}
      </div>

      <div>
        <textarea name="description" />
        {state.errors?.description && (
          <p className="error">{state.errors.description[0]}</p>
        )}
      </div>

      {state.success && (
        <p className="success">Project created!</p>
      )}

      <button type="submit">Create</button>
    </form>
  )
}
```

### Example 14: Reset Form After Success

```typescript
// components/CreateProjectForm.tsx
'use client'

import { useActionState } from 'react'
import { useEffect, useRef } from 'react'

export function CreateProjectForm() {
  const [state, formAction] = useActionState(createProject, {})
  const formRef = useRef<HTMLFormElement>(null)

  useEffect(() => {
    if (state.success) {
      formRef.current?.reset()
    }
  }, [state.success])

  return (
    <form ref={formRef} action={formAction}>
      <input name="name" required />
      {state.success && <p>Project created!</p>}
      <button type="submit">Create</button>
    </form>
  )
}
```

---

## useOptimistic Hook

Update UI optimistically before server confirmation.

### Example 15: Basic useOptimistic

```typescript
// app/actions.ts
'use server'

export async function toggleStar(projectId: string, starred: boolean) {
  await db.project.update({
    where: { id: projectId },
    data: { starred },
  })

  revalidatePath('/projects')
}

// components/StarButton.tsx
'use client'

import { useOptimistic } from 'react'
import { toggleStar } from '@/app/actions'

export function StarButton({
  projectId,
  initialStarred,
}: {
  projectId: string
  initialStarred: boolean
}) {
  const [optimisticStarred, setOptimisticStarred] = useOptimistic(initialStarred)

  const handleToggle = async () => {
    setOptimisticStarred(!optimisticStarred)
    await toggleStar(projectId, !optimisticStarred)
  }

  return (
    <button onClick={handleToggle}>
      {optimisticStarred ? '⭐' : '☆'}
    </button>
  )
}
```

### Example 16: Optimistic List Updates

```typescript
// components/TodoList.tsx
'use client'

import { useOptimistic } from 'react'
import { addTodo, deleteTodo } from '@/app/actions'

interface Todo {
  id: string
  text: string
  completed: boolean
}

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, updateOptimisticTodos] = useOptimistic(
    todos,
    (state, action: { type: 'add' | 'delete'; todo?: Todo; id?: string }) => {
      if (action.type === 'add' && action.todo) {
        return [...state, action.todo]
      }
      if (action.type === 'delete' && action.id) {
        return state.filter(t => t.id !== action.id)
      }
      return state
    }
  )

  const handleAdd = async (text: string) => {
    const tempId = `temp-${Date.now()}`
    updateOptimisticTodos({
      type: 'add',
      todo: { id: tempId, text, completed: false },
    })
    await addTodo(text)
  }

  const handleDelete = async (id: string) => {
    updateOptimisticTodos({ type: 'delete', id })
    await deleteTodo(id)
  }

  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id}>
          {todo.text}
          <button onClick={() => handleDelete(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  )
}
```

---

## Error Handling

Handle errors gracefully in Server Actions.

### Example 17: Try-Catch Error Handling

```typescript
// app/actions.ts
'use server'

export async function createProject(formData: FormData) {
  try {
    const name = formData.get('name') as string

    const project = await db.project.create({
      data: { name },
    })

    revalidatePath('/projects')
    return { success: true, project }
  } catch (error) {
    console.error('Failed to create project:', error)
    return {
      success: false,
      error: 'Failed to create project. Please try again.',
    }
  }
}
```

### Example 18: Validation Errors

```typescript
// app/actions.ts
'use server'

import { z } from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  email: z.string().email('Invalid email'),
})

export async function createUser(formData: FormData) {
  const result = schema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  })

  if (!result.success) {
    return {
      success: false,
      errors: result.error.flatten().fieldErrors,
    }
  }

  const user = await db.user.create({ data: result.data })

  return { success: true, user }
}
```

### Example 19: Error Boundary for Server Actions

```typescript
// app/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="error-container">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

---

## Validation

Validate input before processing.

### Example 20: Zod Validation

```typescript
// app/actions.ts
'use server'

import { z } from 'zod'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  visibility: z.enum(['public', 'private']),
})

export async function createProject(formData: FormData) {
  const validated = createProjectSchema.parse({
    name: formData.get('name'),
    description: formData.get('description'),
    visibility: formData.get('visibility'),
  })

  const project = await db.project.create({ data: validated })

  return { success: true, project }
}
```

### Example 21: Custom Validation

```typescript
// app/actions.ts
'use server'

export async function createProject(formData: FormData) {
  const name = formData.get('name') as string

  // Custom validation
  if (!name || name.trim().length === 0) {
    return { error: 'Name is required' }
  }

  if (name.length > 100) {
    return { error: 'Name must be less than 100 characters' }
  }

  // Check if name already exists
  const existing = await db.project.findFirst({ where: { name } })
  if (existing) {
    return { error: 'Project name already exists' }
  }

  const project = await db.project.create({ data: { name } })

  return { success: true, project }
}
```

---

## Return Values

Return data from Server Actions.

### Example 22: Return JSON

```typescript
// app/actions.ts
'use server'

export async function createProject(formData: FormData) {
  const project = await db.project.create({
    data: { name: formData.get('name') as string },
  })

  return {
    success: true,
    project: {
      id: project.id,
      name: project.name,
      createdAt: project.createdAt.toISOString(),
    },
  }
}
```

### Example 23: Return with Redirect

```typescript
// app/actions.ts
'use server'

import { redirect } from 'next/navigation'

export async function createProject(formData: FormData) {
  const project = await db.project.create({
    data: { name: formData.get('name') as string },
  })

  redirect(`/projects/${project.id}`)
}
```

### Example 24: Return with Revalidation

```typescript
// app/actions.ts
'use server'

import { revalidatePath, revalidateTag } from 'next/cache'

export async function updateProject(id: string, formData: FormData) {
  const project = await db.project.update({
    where: { id },
    data: { name: formData.get('name') as string },
  })

  // Revalidate specific paths
  revalidatePath('/projects')
  revalidatePath(`/projects/${id}`)

  // Revalidate by tag
  revalidateTag('projects')

  return { success: true, project }
}
```

---

## Progressive Enhancement

Server Actions work without JavaScript.

### Example 25: Form Without JavaScript

```typescript
// app/projects/new/page.tsx
import { createProject } from '@/app/actions'

export default function NewProjectPage() {
  // Works without JavaScript enabled
  return (
    <form action={createProject}>
      <input name="name" required />
      <button type="submit">Create Project</button>
    </form>
  )
}
```

### Example 26: Enhanced with JavaScript

```typescript
// components/CreateProjectForm.tsx
'use client'

import { useActionState } from 'react'
import { createProject } from '@/app/actions'

export function CreateProjectForm() {
  const [state, formAction, isPending] = useActionState(
    createProject,
    { success: false }
  )

  return (
    <form action={formAction}>
      <input name="name" required />

      {/* Enhanced feedback with JavaScript */}
      {isPending && <p>Creating...</p>}
      {state.success && <p>Created!</p>}

      <button type="submit" disabled={isPending}>
        Create
      </button>
    </form>
  )
}
```

---

## Security

Secure Server Actions against attacks.

### Example 27: Authentication Check

```typescript
// app/actions.ts
'use server'

import { auth } from '@/lib/auth'

export async function deleteProject(id: string) {
  const session = await auth()

  if (!session?.user) {
    throw new Error('Unauthorized')
  }

  // Check ownership
  const project = await db.project.findUnique({
    where: { id },
    select: { ownerId: true },
  })

  if (project?.ownerId !== session.user.id) {
    throw new Error('Forbidden')
  }

  await db.project.delete({ where: { id } })

  revalidatePath('/projects')
}
```

### Example 28: CSRF Protection

```typescript
// Next.js automatically provides CSRF protection for Server Actions
// No additional configuration needed

// app/actions.ts
'use server'

export async function sensitiveAction(formData: FormData) {
  // CSRF token automatically validated
  await performSensitiveOperation()
}
```

### Example 29: Input Sanitization

```typescript
// app/actions.ts
'use server'

import { z } from 'zod'

const schema = z.object({
  name: z.string()
    .trim()
    .min(1)
    .max(100)
    .regex(/^[a-zA-Z0-9\s-]+$/, 'Invalid characters'),
})

export async function createProject(formData: FormData) {
  const validated = schema.parse({
    name: formData.get('name'),
  })

  // validated.name is sanitized and safe
  await db.project.create({ data: validated })
}
```

---

## Rate Limiting

Prevent abuse with rate limiting.

### Example 30: Simple Rate Limiting

```typescript
// lib/rate-limit.ts
const rateLimits = new Map<string, number[]>()

export function rateLimit(key: string, limit: number, window: number) {
  const now = Date.now()
  const timestamps = rateLimits.get(key) || []

  // Remove old timestamps
  const recentTimestamps = timestamps.filter(t => now - t < window)

  if (recentTimestamps.length >= limit) {
    throw new Error('Rate limit exceeded')
  }

  recentTimestamps.push(now)
  rateLimits.set(key, recentTimestamps)
}

// app/actions.ts
'use server'

import { rateLimit } from '@/lib/rate-limit'
import { auth } from '@/lib/auth'

export async function createProject(formData: FormData) {
  const session = await auth()

  // Limit to 5 projects per minute
  rateLimit(`create-project:${session.user.id}`, 5, 60000)

  const project = await db.project.create({
    data: { name: formData.get('name') as string },
  })

  return { success: true, project }
}
```

---

## Transactions

Handle multi-step database operations.

### Example 31: Database Transaction

```typescript
// app/actions.ts
'use server'

export async function transferOwnership(projectId: string, newOwnerId: string) {
  const session = await auth()

  await db.$transaction(async (tx) => {
    // Update project
    await tx.project.update({
      where: { id: projectId },
      data: { ownerId: newOwnerId },
    })

    // Create activity log
    await tx.activity.create({
      data: {
        type: 'OWNERSHIP_TRANSFER',
        projectId,
        userId: session.user.id,
        metadata: { newOwnerId },
      },
    })

    // Update stats
    await tx.user.update({
      where: { id: newOwnerId },
      data: { projectCount: { increment: 1 } },
    })
  })

  revalidatePath(`/projects/${projectId}`)
}
```

---

## Summary

**Key Concepts:**
- Server Actions run on the server
- Marked with `'use server'` directive
- Can be used in forms and buttons
- Support progressive enhancement

**Hooks:**
- `useFormStatus()` - Track submission status
- `useActionState()` - Manage state and errors
- `useOptimistic()` - Optimistic UI updates

**Best Practices:**
1. Validate all input
2. Handle errors gracefully
3. Revalidate caches after mutations
4. Implement authentication checks
5. Use rate limiting
6. Sanitize user input
7. Use transactions for multi-step operations

**Security:**
- CSRF protection (automatic)
- Authentication checks
- Authorization validation
- Input sanitization
- Rate limiting

**Official Docs:**
- Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations
- Forms and Mutations: https://nextjs.org/docs/app/api-reference/functions/server-actions
