# Server Actions Reference

## Basic Server Actions

```tsx
// app/actions.ts
'use server'

import { db } from '@/lib/database'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  const post = await db.post.create({
    data: { title, content }
  })

  revalidatePath('/posts')
  redirect(`/posts/${post.id}`)
}
```

---

## Progressive Enhancement

Forms work without JavaScript:

```tsx
// app/posts/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

---

## Client-Side Enhancement

Add loading states and error handling:

```tsx
// components/PostForm.tsx
'use client'

import { createPost } from '@/app/actions'
import { useFormStatus, useFormState } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  )
}

export function PostForm() {
  const [state, formAction] = useFormState(createPost, { error: null })

  return (
    <form action={formAction}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      {state?.error && <p className="error">{state.error}</p>}
      <SubmitButton />
    </form>
  )
}
```

---

## Optimistic UI

Update UI immediately, before server responds:

```tsx
// components/TodoList.tsx
'use client'

import { useOptimistic } from 'react'
import { toggleTodo } from '@/app/actions'

export function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, newTodo]
  )

  const handleToggle = async (id: string) => {
    addOptimisticTodo({ ...todos.find(t => t.id === id)!, completed: true })
    await toggleTodo(id)
  }

  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => handleToggle(todo.id)}
          />
          {todo.title}
        </li>
      ))}
    </ul>
  )
}
```

---

## Inline Server Actions

Define actions directly in components:

```tsx
export default function Page() {
  async function handleSubmit(formData: FormData) {
    'use server'

    const email = formData.get('email')
    await subscribeToNewsletter(email)
  }

  return (
    <form action={handleSubmit}>
      <input type="email" name="email" />
      <button>Subscribe</button>
    </form>
  )
}
```

---

## Validation with Zod

```tsx
// app/actions.ts
'use server'

import { z } from 'zod'

const CreatePostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(10),
  categoryId: z.string().uuid()
})

export async function createPost(formData: FormData) {
  const rawData = {
    title: formData.get('title'),
    content: formData.get('content'),
    categoryId: formData.get('categoryId')
  }

  const result = CreatePostSchema.safeParse(rawData)

  if (!result.success) {
    return { error: result.error.flatten().fieldErrors }
  }

  const post = await db.post.create({ data: result.data })
  revalidatePath('/posts')
  return { success: true, post }
}
```

---

## Calling from Client Components

```tsx
'use client'

import { updateProfile } from '@/app/actions'

export function ProfileForm({ user }: { user: User }) {
  const handleUpdate = async () => {
    const result = await updateProfile({
      name: 'New Name',
      email: 'new@email.com'
    })

    if (result.success) {
      toast.success('Profile updated')
    }
  }

  return <button onClick={handleUpdate}>Update Profile</button>
}
```
