---
name: tanstack
description: "Uses TanStack Query, Router, Table, Form, Virtual, or Start in an existing or explicitly selected TanStack project. Use for its query keys, mutations, loaders, URL state, and library APIs; do not introduce the stack for generic React work."
---

# TanStack

Use the selected TanStack libraries for their specific data and routing contracts. Avoid maintaining an accidental second copy of shared server state in component state.

Apply the libraries already chosen by the project. This skill does not require migrating a working framework loader or adding the entire TanStack stack. Form drafts may intentionally start from server data and diverge while the user edits.

## The core mental model

- **Server state ≠ client state.** Data owned by the server (lives in a DB, can change, is shared) belongs in **TanStack Query**, not `useState`.
- Reserve `useState`/`useReducer` for true UI state (open/closed, input draft, selection).
- Prefer Query or Router for shared server data. Preserve justified effect-based integrations with appropriate race handling and cleanup.

## TanStack Query (server state)

- `useQuery` for reads; it handles caching, dedup, background refetch, loading/error states.
- Use stable, structured query keys (`['todos', { status }]`). Keys are the cache identity.
- Set `staleTime` intentionally — how long data is "fresh" before background refetch. Default 0 refetches often; raise it for stable data.
- Co-locate query options in a factory so keys/fns stay consistent and reusable across components and route loaders.

```ts
const todosQuery = (status: string) => queryOptions({
  queryKey: ['todos', { status }],
  queryFn: ({ signal }) => fetchTodos(status, signal), // pass signal for cancellation
  staleTime: 60_000,
});
useQuery(todosQuery(status));
```

Import `queryOptions` and `useQuery` from `@tanstack/react-query`; `queryOptions` preserves inference for the query function context. Include every data-changing parameter in the key. Inline arrays and query functions are supported: keys are hashed by value, not object identity.

### Mutations + optimistic updates

- `useMutation` for writes. After success, **invalidate** affected queries to refetch truth.
- Optimistic update via `onMutate`: cancel in-flight queries, snapshot, write the optimistic value; **roll back in `onError`** using the snapshot; reconcile in `onSettled` by invalidating.

```ts
const key = todosQuery(status).queryKey; // the same filtered list used by useQuery
useMutation({
  mutationFn: updateTodo,
  onMutate: async (next) => {
    await qc.cancelQueries({ queryKey: key, exact: true });
    const prev = qc.getQueryData(key);
    qc.setQueryData(key, (old) => old === undefined ? old : applyOptimistic(old, next));
    return { prev };
  },
  onError: (_e, _next, ctx) => {
    if (ctx?.prev !== undefined) qc.setQueryData(key, ctx.prev);
  },
  onSettled: () => qc.invalidateQueries({ queryKey: ['todos'] }),     // reconcile
});
```

This snapshot pattern assumes mutations to that list are serialized and the key remains fixed for the mutation's lifetime. Concurrent writes need mutation-aware reconciliation or optimistic UI derived from pending variables; restoring an old snapshot can erase a newer update. Make `applyOptimistic` respect the list's filter and leave uncached lists to refetch.

- Prefetch on intent (hover/route enter) with `queryClient.prefetchQuery` to kill waterfalls.
- React 19 note: `useOptimistic` + Actions give *transient* optimistic UI for a single form/mutation; Query's `onMutate` updates the *shared cache* so every component reading that key reflects it. Use Query's approach when the optimistic value must persist across components/navigation.

## TanStack Router (routing + data)

- File/code-based routes are fully type-safe: typed params, search params, and links.
- Treat **search params as state** — Router validates/serializes them (great for filters, pagination, tabs). Don't duplicate them in `useState`.
- Load data in route **loaders** and integrate with Query (`ensureQueryData`) so navigation prefetches and avoids component-mount waterfalls.

## TanStack Start (SSR/full-stack)

- Use Start when you need SSR/streaming, server functions, and shared Query hydration between server and client.
- Prefetch in loaders on the server, dehydrate, and hydrate on the client so the first paint has data and no refetch flash.
- For pure SPA (no SSR needs), Router + Query alone is enough.

## TanStack Table / Form / Virtual

- **Table**: headless — you own markup/styling; it manages sorting/filtering/pagination/grouping. Keep `columns` referentially stable (define outside render or `useMemo`).
- **Virtual**: use `useVirtualizer` when measured list or table rendering costs justify windowing. Preserve keyboard focus and accessible navigation.
- **Form**: type-safe, headless form state + validation (pairs with a schema lib). Avoids re-rendering the whole form on each keystroke.

## Do / Don't

- Do: server data in Query, URL state in Router search params, UI state in `useState`.
- Avoid redundant copies of shared server data; form drafts and external integrations may intentionally diverge from the cache.
- Don't omit data dependencies from query keys. Keep Table `columns` and `data` stable where required; Query `queryFn` does not need memoization solely to prevent refetches.

## Reference

- TanStack docs: [Query keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys), [Query options](https://tanstack.com/query/latest/docs/framework/react/guides/query-options), Query mutations, Router, Start, Table, Form, Virtual.
- TkDodo's blog "Practical React Query" (the canonical Query best-practices series).
