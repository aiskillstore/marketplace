---
name: pitfalls-tanstack-query
description: TanStack Query v5 patterns and common pitfalls. Use when implementing data fetching, cache invalidation, or debugging stale data issues. Triggers on: useQuery, useMutation, queryKey, invalidate, TanStack, React Query.
---

# TanStack Query v5 Pitfalls

Common pitfalls and correct patterns for TanStack Query v5.

## When to Use

- Implementing data fetching with useQuery
- Setting up mutations with useMutation
- Debugging stale data or cache issues
- Reviewing code that uses TanStack Query
- Migrating from v4 to v5

## Workflow

### Step 1: Check Query Keys

Verify query keys use full URL paths for proper deduplication.

### Step 2: Verify Invalidation

Ensure mutations invalidate relevant queries on success.

### Step 3: Check v5 Patterns

Verify v5-specific patterns (isPending vs isLoading).

---

## Correct Usage

```typescript
// ✅ CORRECT: Full URL path in queryKey
const { data } = useQuery({
  queryKey: ['/api/strategies', strategyId],
  queryFn: () => api.get(`/api/strategies/${strategyId}`),
});

// ✅ CORRECT: Invalidate after mutation
const mutation = useMutation({
  mutationFn: (data) => api.post('/api/strategies', data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['strategies'] });
  },
});

// ✅ CORRECT: Type responses with schema types
import type { Strategy } from '@shared/schema';
const { data } = useQuery<{ data: Strategy[] }>(...);
```

## Anti-Patterns

```typescript
// ❌ WRONG: Short queryKey
queryKey: ['strategy']  // Won't dedupe properly

// ❌ WRONG: Forgetting to invalidate
onSuccess: () => { navigate('/'); }  // Stale cache!

// ❌ WRONG: Using isLoading for mutations
mutation.isLoading  // Use isPending in v5
```

## Optimistic Updates

```typescript
// ✅ Update UI immediately, rollback on error
const mutation = useMutation({
  mutationFn: updateStrategy,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['strategy', id] });
    const previous = queryClient.getQueryData(['strategy', id]);

    // Optimistic update
    queryClient.setQueryData(['strategy', id], newData);

    return { previous };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    queryClient.setQueryData(['strategy', id], context.previous);
    toast.error('Update failed');
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['strategy', id] });
  },
});
```

## Quick Checklist

- [ ] QueryKeys use full URL paths
- [ ] Mutations invalidate relevant queries
- [ ] Using isPending (not isLoading) for mutations in v5
- [ ] Responses typed with schema types
