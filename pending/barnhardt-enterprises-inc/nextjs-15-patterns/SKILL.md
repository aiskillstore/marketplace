---
name: nextjs-15-patterns
description: Next.js 15 App Router patterns and best practices.
---

# Next.js 15 Patterns

## Server vs Client Components

### Default: Server Components
```typescript
// app/users/page.tsx - Server Component (default)
export default async function UsersPage() {
  const users = await getUsers(); // Direct DB access
  return <UserList users={users} />;
}
```

### Client Components (when needed)
```typescript
// components/counter.tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

## Server Actions

```typescript
// actions/user-actions.ts
'use server';

import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

export async function createUser(formData: FormData) {
  const validated = CreateUserSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
  });

  if (!validated.success) {
    return { error: validated.error.flatten() };
  }

  const user = await db.insert(users).values(validated.data).returning();
  revalidatePath('/users');
  return { data: user };
}
```

## Data Fetching

### In Server Components
```typescript
// Direct async/await - no useEffect needed
async function UserProfile({ id }: { id: string }) {
  const user = await getUser(id);
  if (!user) notFound();
  return <Profile user={user} />;
}
```

### With Loading States
```typescript
// app/users/loading.tsx
export default function Loading() {
  return <UserListSkeleton />;
}
```

### With Error Handling
```typescript
// app/users/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

## Route Handlers (API)

```typescript
// app/api/users/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const users = await getUsers();
  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const body = await request.json();
  const user = await createUser(body);
  return NextResponse.json(user, { status: 201 });
}
```

## Metadata

```typescript
// app/users/[id]/page.tsx
import { Metadata } from 'next';

export async function generateMetadata({
  params,
}: {
  params: { id: string };
}): Promise<Metadata> {
  const user = await getUser(params.id);
  return {
    title: user?.name ?? 'User',
    description: `Profile for ${user?.name}`,
  };
}
```

## Parallel Routes

```
app/
├── @modal/
│   └── (.)photo/[id]/page.tsx  # Intercepted modal
├── layout.tsx
└── page.tsx
```

## Best Practices

1. **Prefer Server Components** - Only use 'use client' when needed
2. **Colocate data fetching** - Fetch where data is used
3. **Use Server Actions** - For mutations, not API routes
4. **Streaming with Suspense** - For progressive loading
5. **Validate all inputs** - Use Zod for server actions
