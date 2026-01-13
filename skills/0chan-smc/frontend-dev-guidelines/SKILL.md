---
name: frontend-dev-guidelines
description: Next.js 15 애플리케이션을 위한 프론트엔드 개발 가이드라인. React 19, TypeScript, Shadcn/ui, Tailwind CSS를 사용한 모던 패턴. Server Components, Client Components, App Router, 파일 구조, Shadcn/ui 컴포넌트, 성능 최적화, TypeScript 모범 사례 포함. 컴포넌트, 페이지, 기능 생성, 데이터 페칭, 스타일링, 라우팅, 프론트엔드 코드 작업 시 사용.
---

# Frontend Development Guidelines

## Purpose

Comprehensive guide for modern Next.js 15 development with React 19, emphasizing Server Components, Client Components, App Router patterns, Shadcn/ui components, proper file organization, and performance optimization.

## When to Use This Skill

- Creating new components or pages
- Building new features
- Fetching data (Server Components, Server Actions)
- Setting up routing with Next.js App Router
- Styling components with Tailwind CSS and Shadcn/ui
- Performance optimization
- Organizing frontend code
- TypeScript best practices

---

## Quick Start

### New Component Checklist

Creating a component? Follow this checklist:

- [ ] Determine Server vs Client Component (default: Server Component)
- [ ] Add `"use client"` directive only if needed (interactivity, hooks, browser APIs)
- [ ] Use TypeScript with explicit prop types
- [ ] Import Shadcn/ui components from `@/components/ui`
- [ ] Use Tailwind CSS classes for styling
- [ ] Import aliases: `@/components`, `@/lib`, `@/hooks`
- [ ] Use `cn()` utility for conditional classes
- [ ] Default export at bottom
- [ ] Use Server Components for data fetching when possible

### New Page Checklist

Creating a page? Set up this structure:

- [ ] Create `app/{route-name}/page.tsx` for route
- [ ] Use Server Component by default
- [ ] Fetch data directly in Server Component
- [ ] Create `components/` directory for page-specific components
- [ ] Use `loading.tsx` for loading states
- [ ] Use `error.tsx` for error boundaries
- [ ] Export metadata for SEO

---

## Import Aliases Quick Reference

| Alias          | Resolves To   | Example                                           |
| -------------- | ------------- | ------------------------------------------------- |
| `@/`           | Project root  | `import { cn } from '@/lib/utils'`                |
| `@/components` | `components/` | `import { Button } from '@/components/ui/button'` |
| `@/lib`        | `lib/`        | `import { cn } from '@/lib/utils'`                |
| `@/hooks`      | `hooks/`      | `import { useMobile } from '@/hooks/use-mobile'`  |
| `@/app`        | `app/`        | `import { Metadata } from 'next'`                 |

Defined in: `tsconfig.json` paths configuration

---

## Common Imports Cheatsheet

```typescript
// Next.js
import { Metadata } from 'next'
import { Suspense } from 'react'
import { notFound, redirect } from 'next/navigation'

// React (Client Components only)
;('use client')
import { useState, useCallback, useMemo } from 'react'

// Shadcn/ui Components
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

// Utilities
import { cn } from '@/lib/utils'

// Hooks (Client Components only)
import { useMobile } from '@/hooks/use-mobile'

// Types
import type { ComponentProps } from 'react'
```

---

## Topic Guides

### 🎨 Component Patterns

**Server Components vs Client Components:**

- **Server Components** (default): No `"use client"`, can fetch data directly, smaller bundle
- **Client Components**: Add `"use client"` for interactivity, hooks, browser APIs

**Key Concepts:**

- Default to Server Components
- Only use Client Components when necessary
- Use Shadcn/ui components (already Client Components)
- Component structure: Props → Data Fetching → Render → Export

**Example Server Component:**

```typescript
// app/features/posts/components/PostList.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface PostListProps {
  posts: Post[]
}

export function PostList({ posts }: PostListProps) {
  return (
    <div className='grid gap-4'>
      {posts.map((post) => (
        <Card key={post.id}>
          <CardHeader>
            <CardTitle>{post.title}</CardTitle>
          </CardHeader>
          <CardContent>{post.content}</CardContent>
        </Card>
      ))}
    </div>
  )
}
```

**Example Client Component:**

```typescript
// app/features/posts/components/PostForm.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export function PostForm() {
  const [title, setTitle] = useState('')

  return (
    <form>
      <Input value={title} onChange={(e) => setTitle(e.target.value)} />
      <Button type='submit'>Submit</Button>
    </form>
  )
}
```

---

### 📊 Data Fetching

**PRIMARY PATTERN: Server Components**

- Fetch data directly in Server Components
- Use `async/await` in Server Components
- No need for `useEffect` or data fetching libraries
- Automatic request deduplication

**Server Actions:**

- Use for mutations (forms, updates)
- Create `app/actions/` directory
- Mark with `"use server"` directive

**Example Server Component with Data Fetching:**

```typescript
// app/posts/page.tsx
import { PostList } from '@/components/PostList'

async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    cache: 'no-store', // or 'force-cache', 'revalidate'
  })
  return res.json()
}

export default async function PostsPage() {
  const posts = await getPosts()

  return <PostList posts={posts} />
}
```

**Example Server Action:**

```typescript
// app/actions/posts.ts
'use server'

export async function createPost(formData: FormData) {
  const title = formData.get('title')
  // ... validation and creation logic
  redirect('/posts')
}
```

---

### 📁 File Organization

**App Router Structure:**

```
app/
  (routes)/
    page.tsx          # Route page
    layout.tsx        # Route layout
    loading.tsx       # Loading UI
    error.tsx         # Error UI
  components/         # Shared components
    ui/               # Shadcn/ui components
  features/           # Feature-specific code
    posts/
      components/     # Feature components
      actions/        # Server Actions
      types/          # TypeScript types
lib/
  utils.ts            # Utilities (cn, etc.)
hooks/
  use-mobile.ts       # Custom hooks (Client only)
```

**Feature Organization:**

- `app/features/{feature}/`: Feature-specific pages/routes
- `components/`: Truly reusable components
- `components/ui/`: Shadcn/ui components (don't modify directly)

---

### 🎨 Styling

**Tailwind CSS + Shadcn/ui:**

- Use Tailwind utility classes
- Use `cn()` utility for conditional classes
- Shadcn/ui components use CSS variables for theming
- Customize theme in `app/globals.css`

**Styling Patterns:**

```typescript
import { cn } from '@/lib/utils'

interface ButtonProps {
  variant?: 'primary' | 'secondary'
  className?: string
}

export function Button({ variant = 'primary', className }: ButtonProps) {
  return (
    <button
      className={cn(
        'rounded-md px-4 py-2',
        variant === 'primary' && 'bg-primary text-primary-foreground',
        variant === 'secondary' && 'bg-secondary text-secondary-foreground',
        className,
      )}
    >
      Click me
    </button>
  )
}
```

**Shadcn/ui Components:**

- Import from `@/components/ui/{component-name}`
- Components are already styled and accessible
- Customize via `className` prop or CSS variables

---

### 🛣️ Routing

**Next.js App Router - File-Based:**

- Directory: `app/{route-name}/page.tsx`
- Nested routes: `app/{parent}/{child}/page.tsx`
- Dynamic routes: `app/posts/[id]/page.tsx`
- Route groups: `app/(marketing)/about/page.tsx`

**Example Route:**

```typescript
// app/posts/page.tsx
import { Metadata } from 'next'
import { PostList } from '@/components/PostList'

export const metadata: Metadata = {
  title: 'Posts',
  description: 'List of all posts',
}

export default async function PostsPage() {
  const posts = await getPosts()

  return (
    <div className='container mx-auto py-8'>
      <h1 className='text-3xl font-bold mb-6'>Posts</h1>
      <PostList posts={posts} />
    </div>
  )
}
```

**Dynamic Route:**

```typescript
// app/posts/[id]/page.tsx
interface PostPageProps {
  params: Promise<{ id: string }>
}

export default async function PostPage({ params }: PostPageProps) {
  const { id } = await params
  const post = await getPost(id)

  if (!post) {
    notFound()
  }

  return <PostDetail post={post} />
}
```

---

### ⏳ Loading & Error States

**Loading States:**

- Create `loading.tsx` in route directory
- Automatically wraps page in Suspense
- Use for route-level loading

**Error Boundaries:**

- Create `error.tsx` in route directory
- Automatically catches errors in route
- Can reset error state

**Example Loading UI:**

```typescript
// app/posts/loading.tsx
export default function Loading() {
  return (
    <div className='flex items-center justify-center min-h-screen'>
      <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary' />
    </div>
  )
}
```

**Example Error UI:**

```typescript
// app/posts/error.tsx
'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className='flex flex-col items-center justify-center min-h-screen'>
      <h2 className='text-2xl font-bold mb-4'>Something went wrong!</h2>
      <Button onClick={reset}>Try again</Button>
    </div>
  )
}
```

---

### ⚡ Performance

**Optimization Patterns:**

- Use Server Components (smaller bundle)
- Use `next/image` for images
- Use `next/font` for fonts
- Lazy load Client Components when possible
- Use `useMemo` and `useCallback` in Client Components
- Stream data with Suspense boundaries

**Image Optimization:**

```typescript
import Image from 'next/image'

export function Avatar({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={40}
      height={40}
      className='rounded-full'
    />
  )
}
```

**Streaming with Suspense:**

```typescript
import { Suspense } from 'react'
import { PostList } from '@/components/PostList'
import { Loading } from '@/components/Loading'

export default function Page() {
  return (
    <div>
      <Suspense fallback={<Loading />}>
        <PostList />
      </Suspense>
    </div>
  )
}
```

---

### 📘 TypeScript

**Standards:**

- Strict mode enabled
- No `any` type
- Explicit return types on functions
- Type imports: `import type { Post } from '@/types/post'`
- Component prop interfaces with JSDoc

**Example:**

```typescript
import type { ComponentProps } from 'react'
import { Button } from '@/components/ui/button'

/**
 * Custom button component with loading state
 */
interface CustomButtonProps extends ComponentProps<typeof Button> {
  isLoading?: boolean
}

export function CustomButton({
  isLoading,
  children,
  ...props
}: CustomButtonProps) {
  return (
    <Button disabled={isLoading} {...props}>
      {isLoading ? 'Loading...' : children}
    </Button>
  )
}
```

---

### 🔧 Common Patterns

**Form Handling:**

- Use Server Actions for form submissions
- Use `react-hook-form` with `zod` for validation (Client Components)
- Use Shadcn/ui Form components

**Example Form with Server Action:**

```typescript
// app/actions/posts.ts
'use server'

import { z } from 'zod'

const createPostSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
})

export async function createPost(formData: FormData) {
  const rawData = {
    title: formData.get('title'),
    content: formData.get('content'),
  }

  const validated = createPostSchema.parse(rawData)
  // ... create post logic
  redirect('/posts')
}
```

**Metadata:**

```typescript
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Posts',
  description: 'List of all posts',
  openGraph: {
    title: 'Posts',
    description: 'List of all posts',
  },
}
```

---

## Core Principles

1. **Server Components First**: Default to Server Components, use Client Components only when needed
2. **App Router Structure**: Use file-based routing with `app/` directory
3. **Shadcn/ui Components**: Use pre-built accessible components
4. **Tailwind CSS**: Utility-first styling with `cn()` helper
5. **TypeScript Strict**: No `any`, explicit types
6. **Performance**: Use Server Components, optimize images, lazy load when needed
7. **File Organization**: Features in `app/features/`, shared in `components/`
8. **Import Aliases**: Use `@/` prefix for clean imports

---

## Quick Reference: File Structure

```
app/
  layout.tsx                    # Root layout
  page.tsx                      # Home page
  globals.css                   # Global styles
  (routes)/
    posts/
      page.tsx                  # Posts list page
      [id]/
        page.tsx                # Post detail page
      loading.tsx               # Loading UI
      error.tsx                 # Error UI
  features/
    posts/
      components/
        PostList.tsx            # Feature components
      actions/
        posts.ts                # Server Actions
components/
  ui/                           # Shadcn/ui components
    button.tsx
    card.tsx
lib/
  utils.ts                      # Utilities (cn, etc.)
hooks/
  use-mobile.ts                 # Custom hooks
```

---

## Modern Component Template (Quick Copy)

**Server Component:**

```typescript
// app/components/PostCard.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { Post } from '@/types/post'

interface PostCardProps {
  post: Post
}

export function PostCard({ post }: PostCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{post.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{post.content}</p>
      </CardContent>
    </Card>
  )
}
```

**Client Component:**

```typescript
// app/components/PostForm.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { createPost } from '@/app/actions/posts'
import { cn } from '@/lib/utils'

export function PostForm({ className }: { className?: string }) {
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(formData: FormData) {
    setIsLoading(true)
    await createPost(formData)
    setIsLoading(false)
  }

  return (
    <form action={handleSubmit} className={cn('space-y-4', className)}>
      <Input name='title' placeholder='Post title' required />
      <Input name='content' placeholder='Post content' required />
      <Button type='submit' disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Post'}
      </Button>
    </form>
  )
}
```

---

## Related Skills

- **backend-dev-guidelines**: Backend API patterns that frontend consumes

---

**Skill Status**: Optimized for Next.js 15 with App Router, Server Components, and Shadcn/ui
