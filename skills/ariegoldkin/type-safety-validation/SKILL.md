---
name: type-safety-validation
description: Achieve end-to-end type safety with Zod runtime validation, tRPC type-safe APIs, Prisma ORM, and TypeScript 5.7+ features. Build fully type-safe applications from database to UI for 2025+ development.
version: 1.0.0
author: AI Agent Hub
tags: [typescript, zod, trpc, prisma, type-safety, validation, 2025]
---

# Type Safety & Validation

## Overview

End-to-end type safety ensures bugs are caught at compile time, not runtime. This skill covers Zod for runtime validation, tRPC for type-safe APIs, Prisma for type-safe database access, and modern TypeScript features.

**When to use this skill:**
- Building type-safe APIs (REST, RPC, GraphQL)
- Validating user input and external data
- Ensuring database queries are type-safe
- Creating end-to-end typed full-stack applications
- Migrating from JavaScript to TypeScript
- Implementing strict validation rules

## Core Stack

### 1. Zod - Runtime Validation

```typescript
import { z } from 'zod'

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  age: z.number().int().positive().max(120),
  role: z.enum(['admin', 'user', 'guest']),
  metadata: z.record(z.string()).optional(),
  createdAt: z.date().default(() => new Date())
})

// Infer TypeScript type from schema
type User = z.infer<typeof UserSchema>

// Validate data
const result = UserSchema.safeParse(data)
if (result.success) {
  const user: User = result.data
} else {
  console.error(result.error.issues)
}

// Transform data
const EmailSchema = z.string().email().transform(email => email.toLowerCase())
```

**Advanced Patterns**:
```typescript
// Refinements
const PasswordSchema = z.string()
  .min(8)
  .refine((pass) => /[A-Z]/.test(pass), 'Must contain uppercase')
  .refine((pass) => /[0-9]/.test(pass), 'Must contain number')

// Discriminated Unions
const EventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('click'), x: z.number(), y: z.number() }),
  z.object({ type: z.literal('scroll'), offset: z.number() })
])

// Recursive Types
const CategorySchema: z.ZodType<Category> = z.lazy(() =>
  z.object({
    name: z.string(),
    children: z.array(CategorySchema).optional()
  })
)
```

### 2. tRPC - Type-Safe APIs

```typescript
// Server: Define procedures
import { initTRPC } from '@trpc/server'
import { z } from 'zod'

const t = initTRPC.create()

export const appRouter = t.router({
  getUser: t.procedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      return await db.user.findUnique({ where: { id: input.id } })
    }),

  createUser: t.procedure
    .input(z.object({
      email: z.string().email(),
      name: z.string()
    }))
    .mutation(async ({ input }) => {
      return await db.user.create({ data: input })
    })
})

export type AppRouter = typeof appRouter

// Client: Fully typed!
import { createTRPCProxyClient, httpBatchLink } from '@trpc/client'
import type { AppRouter } from './server'

const client = createTRPCProxyClient<AppRouter>({
  links: [httpBatchLink({ url: 'http://localhost:3000/api/trpc' })]
})

// TypeScript knows the exact shape!
const user = await client.getUser.query({ id: '123' })
//    ^? User | null
```

### 3. Prisma - Type-Safe ORM

```prisma
// schema.prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  posts     Post[]
  profile   Profile?
  createdAt DateTime @default(now())
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
}
```

```typescript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// Fully typed queries
const user = await prisma.user.findUnique({
  where: { id: '123' },
  include: {
    posts: {
      where: { published: true },
      orderBy: { createdAt: 'desc' }
    }
  }
})
// user is typed as: User & { posts: Post[] }

// Type-safe creates
const newUser = await prisma.user.create({
  data: {
    email: 'user@example.com',
    posts: {
      create: [
        { title: 'First Post', content: 'Hello world' }
      ]
    }
  }
})
```

### 4. TypeScript 5.7+ Features

```typescript
// Const type parameters (TS 5.0+)
function firstElement<T extends readonly any[]>(arr: T) {
  return arr[0]
}

const result = firstElement(['a', 'b'] as const)
// result is typed as 'a'

// Satisfies operator (TS 4.9+)
const config = {
  url: 'https://api.example.com',
  timeout: 5000
} satisfies Config  // Ensures config matches Config, but keeps literal types

// Decorators (TS 5.0+)
function logged(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value
  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey}`)
    return original.apply(this, args)
  }
}

class API {
  @logged
  async fetchData() {}
}
```

## Full-Stack Example

```typescript
// ===== BACKEND (Next.js API) =====
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch'
import { appRouter } from '@/server/routers/_app'

export async function GET(req: Request) {
  return fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext: () => ({})
  })
}

export const POST = GET

// server/routers/_app.ts
import { z } from 'zod'
import { prisma } from '@/lib/prisma'
import { publicProcedure, router } from '../trpc'

export const appRouter = router({
  posts: {
    list: publicProcedure
      .input(z.object({
        limit: z.number().min(1).max(100).default(10),
        cursor: z.string().optional()
      }))
      .query(async ({ input }) => {
        const posts = await prisma.post.findMany({
          take: input.limit + 1,
          cursor: input.cursor ? { id: input.cursor } : undefined,
          orderBy: { createdAt: 'desc' },
          include: { author: true }
        })

        return {
          items: posts.slice(0, input.limit),
          nextCursor: posts[input.limit]?.id
        }
      }),

    create: publicProcedure
      .input(z.object({
        title: z.string().min(1).max(200),
        content: z.string().optional()
      }))
      .mutation(async ({ input }) => {
        return await prisma.post.create({
          data: input
        })
      })
  }
})

// ===== FRONTEND (React) =====
// lib/trpc.ts
import { createTRPCReact } from '@trpc/react-query'
import type { AppRouter } from '@/server/routers/_app'

export const trpc = createTRPCReact<AppRouter>()

// components/PostList.tsx
'use client'

import { trpc } from '@/lib/trpc'

export function PostList() {
  const { data, isLoading } = trpc.posts.list.useQuery({ limit: 10 })
  const createPost = trpc.posts.create.useMutation()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {data?.items.map(post => (
        <div key={post.id}>
          <h2>{post.title}</h2>
          <p>{post.content}</p>
          <span>By {post.author.name}</span>
        </div>
      ))}

      <button onClick={() => createPost.mutate({ title: 'New Post' })}>
        Create Post
      </button>
    </div>
  )
}
```

## Best Practices

### Validation
- ✅ Validate at boundaries (API inputs, form submissions, external data)
- ✅ Use `.safeParse()` to handle errors gracefully
- ✅ Provide clear error messages for users
- ✅ Validate environment variables at startup
- ✅ Use branded types for IDs (`z.string().brand<'UserId'>()`)

### Type Safety
- ✅ Enable `strict: true` in `tsconfig.json`
- ✅ Use `noUncheckedIndexedAccess` for safer array access
- ✅ Prefer `unknown` over `any`
- ✅ Use type guards for narrowing
- ✅ Leverage inference with `typeof` and `ReturnType`

### Performance
- ✅ Reuse schemas (don't create inline)
- ✅ Use `.parse()` for known-good data (faster than `.safeParse()`)
- ✅ Enable Prisma query optimization
- ✅ Use tRPC batching for multiple queries
- ✅ Cache validation results when appropriate

## Resources

- [Zod Documentation](https://zod.dev)
- [tRPC Documentation](https://trpc.io)
- [Prisma Documentation](https://www.prisma.io/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
