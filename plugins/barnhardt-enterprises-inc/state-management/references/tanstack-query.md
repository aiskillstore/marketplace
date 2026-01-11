# TanStack Query Reference

## Setup

```typescript
// providers/query-provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            gcTime: 5 * 60 * 1000, // 5 minutes (formerly cacheTime)
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

## Query Options

```typescript
useQuery({
  queryKey: ['users', id],
  queryFn: () => fetchUser(id),

  // Timing
  staleTime: 5 * 60 * 1000,      // Consider fresh for 5 min
  gcTime: 10 * 60 * 1000,        // Keep in cache for 10 min
  refetchInterval: 30 * 1000,    // Poll every 30 seconds

  // Behavior
  enabled: !!id,                  // Only fetch if id exists
  retry: 3,                       // Retry failed requests 3 times
  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),

  // Callbacks
  select: (data) => data.user,    // Transform data
  placeholderData: previousData,  // Show while fetching
});
```

## Mutations

```typescript
const mutation = useMutation({
  mutationFn: createUser,

  // Optimistic update
  onMutate: async (newUser) => {
    await queryClient.cancelQueries({ queryKey: ['users'] });
    const previous = queryClient.getQueryData(['users']);
    queryClient.setQueryData(['users'], (old) => [...old, newUser]);
    return { previous };
  },

  // Rollback on error
  onError: (err, newUser, context) => {
    queryClient.setQueryData(['users'], context?.previous);
  },

  // Always refetch
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

## Infinite Queries

```typescript
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam }) => fetchPosts(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
});

// Flatten pages
const allPosts = data?.pages.flatMap(page => page.posts) ?? [];
```

## Prefetching

```typescript
// In Server Component or loader
await queryClient.prefetchQuery({
  queryKey: ['users'],
  queryFn: getUsers,
});

// In Client Component on hover
function UserLink({ id }: { id: string }) {
  const queryClient = useQueryClient();

  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: ['user', id],
      queryFn: () => getUser(id),
    });
  };

  return (
    <Link href={`/users/${id}`} onMouseEnter={prefetch}>
      View User
    </Link>
  );
}
```
