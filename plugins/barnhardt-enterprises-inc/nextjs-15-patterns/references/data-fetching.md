# Data Fetching Reference

## Server Component Fetching

```typescript
// Direct database access in Server Components
async function UserList() {
  const users = await db.query.users.findMany();
  return (
    <ul>
      {users.map(user => <li key={user.id}>{user.name}</li>)}
    </ul>
  );
}
```

## Parallel Data Fetching

```typescript
async function Dashboard() {
  // Fetch in parallel
  const [users, posts, stats] = await Promise.all([
    getUsers(),
    getPosts(),
    getStats(),
  ]);

  return (
    <>
      <UserList users={users} />
      <PostList posts={posts} />
      <Stats data={stats} />
    </>
  );
}
```

## Sequential Data Fetching (When Needed)

```typescript
async function UserPosts({ userId }: { userId: string }) {
  // Must fetch user first to get preferences
  const user = await getUser(userId);

  // Then fetch posts based on user preferences
  const posts = await getPostsForUser(user.id, user.preferences);

  return <PostList posts={posts} />;
}
```

## Streaming with Suspense

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>

      <Suspense fallback={<UsersSkeleton />}>
        <Users />
      </Suspense>

      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
    </div>
  );
}
```

## Caching

```typescript
// Default: cached
const data = await fetch('https://api.example.com/data');

// No cache
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store',
});

// Revalidate every 60 seconds
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 },
});

// Tag-based revalidation
const data = await fetch('https://api.example.com/data', {
  next: { tags: ['users'] },
});

// Revalidate by tag
import { revalidateTag } from 'next/cache';
revalidateTag('users');
```

## Client-Side with TanStack Query

```typescript
'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserInput) =>
      fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }).then(r => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```
