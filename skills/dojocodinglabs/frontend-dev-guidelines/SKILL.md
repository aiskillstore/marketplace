---
name: frontend-dev-guidelines
description: Frontend development guidelines for Next.js + React 19 + shadcn/ui applications. Modern patterns including App Router, Server Components, Client Components, Server Actions, shadcn/ui with Tailwind CSS, React Hook Form, lazy loading, Suspense boundaries, Supabase client integration, performance optimization, and TypeScript best practices. Use when creating pages, components, forms, styling, data fetching, or working with Next.js/React code.
---

> **📋 OPINIONATED SCAFFOLD**: Modern Next.js + React 19 + shadcn/ui stack
>
> **Default Stack**:
> - **Framework**: Next.js 14+ (App Router)
> - **UI Library**: React 19
> - **Components**: shadcn/ui (Radix primitives)
> - **Styling**: Tailwind CSS
> - **Forms**: React Hook Form + Zod validation
> - **State**: React Context + TanStack Query for server state
> - **Data Fetching**: Server Components, Server Actions, TanStack Query
> - **Language**: TypeScript
> - **Deployment**: Vercel
>
> **To customize**: Run `/customize-scaffold frontend` or use the scaffold-customizer agent
> to adapt for Vue, Angular, Svelte, vanilla React, or other frameworks/UI libraries.

# Frontend Development Guidelines

## Purpose

Modern frontend development with Next.js 14+ App Router, React 19, Server Components, and shadcn/ui. Focus on performance, type safety, and excellent UX with Supabase integration.

## When to Use This Skill

- Creating pages with App Router
- Building Server/Client Components
- Implementing Server Actions
- Adding shadcn/ui components
- Styling with Tailwind CSS
- Data fetching with Supabase
- Forms with React Hook Form + Zod
- Performance optimization
- TypeScript patterns

---

## Quick Start

### New Page Checklist

- [ ] Create `app/[route]/page.tsx`
- [ ] Use Server Component by default (no 'use client')
- [ ] Fetch data directly in component
- [ ] Add `loading.tsx` for loading state
- [ ] Add `error.tsx` for error handling
- [ ] Export metadata for SEO
- [ ] Use Tailwind for styling

### New Component Checklist

- [ ] Server Component or Client Component?
- [ ] Add `'use client'` ONLY if using hooks/events
- [ ] Use shadcn/ui components
- [ ] Style with Tailwind classes
- [ ] TypeScript types for props
- [ ] Use `cn()` for conditional classes

---

## Core Principles

### 1. Server Components by Default

```typescript
// ✅ Server Component (default)
export default async function Page() {
  const data = await getData()  // Direct fetch, no hooks
  return <div>{data.title}</div>
}

// ❌ Don't add 'use client' unless needed
'use client'  // Only add if using hooks/events!
```

### 2. Client Components When Needed

```typescript
// ✅ Client Component (interactivity)
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Counter() {
  const [count, setCount] = useState(0)
  return <Button onClick={() => setCount(count + 1)}>{count}</Button>
}
```

### 3. Server Actions for Mutations

```typescript
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { createServerClient } from '@/lib/supabase/server'

export async function createPost(formData: FormData) {
  const supabase = createServerClient()

  const { data, error } = await supabase
    .from('posts')
    .insert({ title: formData.get('title') })

  if (error) throw error

  revalidatePath('/posts')
  return { success: true, data }
}

// In component:
<form action={createPost}>
  <input name="title" />
  <button type="submit">Create</button>
</form>
```

### 4. Use shadcn/ui Components

```typescript
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

export function Example() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Title</CardTitle>
      </CardHeader>
      <CardContent>
        <Input placeholder="Type..." />
        <Button>Submit</Button>
      </CardContent>
    </Card>
  )
}
```

### 5. Tailwind CSS for Styling

```typescript
import { cn } from '@/lib/utils'

export function Component({ className, variant }: Props) {
  return (
    <div className={cn(
      'rounded-lg bg-white p-4 shadow',
      variant === 'primary' && 'border-2 border-blue-500',
      className
    )}>
      Content
    </div>
  )
}
```

### 6. Forms with React Hook Form

```typescript
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema)
  })

  async function onSubmit(values: z.infer<typeof schema>) {
    // Handle submission
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register('email')} />
      <input {...form.register('password')} type="password" />
      <button type="submit">Login</button>
    </form>
  )
}
```

### 7. Supabase Integration

```typescript
// Server Component
import { createServerClient } from '@/lib/supabase/server'

export default async function Page() {
  const supabase = createServerClient()
  const { data } = await supabase.from('posts').select('*')

  return <div>{/* Render data */}</div>
}

// Client Component
'use client'

import { createClient } from '@/lib/supabase/client'

export function ClientComponent() {
  const supabase = createClient()
  // Use with hooks...
}
```

---

## Directory Structure

```
app/
├── (auth)/              # Route group (auth pages)
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── dashboard/
│   ├── page.tsx         # /dashboard
│   ├── loading.tsx      # Loading UI
│   ├── error.tsx        # Error UI
│   └── posts/
│       ├── page.tsx     # /dashboard/posts
│       └── [id]/
│           └── page.tsx # /dashboard/posts/[id]
├── api/
│   └── webhook/
│       └── route.ts     # API route
├── layout.tsx           # Root layout
└── page.tsx             # Home page

components/
├── ui/                  # shadcn/ui components
│   ├── button.tsx
│   ├── card.tsx
│   └── input.tsx
└── dashboard/           # Feature components
    ├── post-list.tsx
    └── post-card.tsx

lib/
├── supabase/
│   ├── client.ts        # Client-side
│   └── server.ts        # Server-side
└── utils.ts             # cn() utility
```

---

## Example Resource Files

> **📝 Note**: This is a **scaffold skill** with instructional examples. Generate additional resources as needed for your specific project following these patterns.

### Patterns Covered

When you need guidance on a specific topic, ask Claude to generate examples:

- **Server vs Client Components** - When to use each, migration patterns
- **Data fetching** - Server Components, Server Actions, TanStack Query
- **Forms** - React Hook Form + Zod, Server Actions
- **shadcn/ui usage** - Component patterns, customization
- **Tailwind patterns** - Responsive design, dark mode, animations
- **Performance** - Code splitting, lazy loading, images
- **TypeScript** - Component props, generics, utility types
- **Testing** - Unit tests, integration tests, E2E

**How to request**: "Show me examples of [topic] with Next.js + shadcn/ui"

---

## Common Imports

```typescript
// Next.js
import { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { redirect, notFound } from 'next/navigation'
import { revalidatePath, revalidateTag } from 'next/cache'

// React (Client Components)
'use client'
import { useState, useEffect, useCallback, useMemo, useTransition } from 'react'

// shadcn/ui
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'

// Tailwind
import { cn } from '@/lib/utils'

// Supabase
import { createClient } from '@/lib/supabase/client'
import { createServerClient } from '@/lib/supabase/server'

// Forms
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
```

---

## Quick Reference

### Metadata (SEO)

```typescript
export const metadata: Metadata = {
  title: 'Page Title',
  description: 'Page description',
}

// Dynamic metadata
export async function generateMetadata({ params }): Promise<Metadata> {
  return {
    title: `Post ${params.id}`,
  }
}
```

### Loading States

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return <div>Loading...</div>
}
```

### Error Handling

```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### API Routes

```typescript
// app/api/posts/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const posts = await getPosts()
  return NextResponse.json(posts)
}

export async function POST(request: Request) {
  const body = await request.json()
  const post = await createPost(body)
  return NextResponse.json(post, { status: 201 })
}
```

---

## Anti-Patterns

❌ Using 'use client' on every component
❌ Not using Server Components for data fetching
❌ Inline styles instead of Tailwind
❌ Not using shadcn/ui components
❌ useState for server data (use Server Components)
❌ Direct database queries in Client Components
❌ Missing loading/error states
❌ Not using TypeScript properly

---

## Customization Instructions

### For Your Tech Stack

**Not using Next.js?** Adapt the patterns:

- Vue/Nuxt → Similar SSR patterns
- Vite + React → Remove Server Components, use TanStack Query
- Angular → Similar concepts, different syntax
- Svelte/SvelteKit → SvelteKit has similar features

### For Your UI Library

**Not using shadcn/ui?** Replace with:

- Material-UI → Import from @mui/material
- Chakra UI → Import from @chakra-ui/react
- Ant Design → Import from antd
- Custom components → Build your own

### For Your Patterns

Keep the principles:
- Component composition
- Type safety
- Performance optimization
- Accessibility
- SEO considerations

---

## Related Skills

- **backend-dev-guidelines** - Supabase Edge Functions patterns
- **memory-management** - Track UI/UX decisions
- **skill-developer** - Meta-skill for creating skills

---

**Skill Status**: SCAFFOLD ✅
**Line Count**: < 500 ✅
**Progressive Disclosure**: Instructional patterns + generate on-demand ✅
