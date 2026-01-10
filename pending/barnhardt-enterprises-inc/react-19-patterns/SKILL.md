---
name: react-19-patterns
description: Comprehensive React 19 patterns including all hooks, Server/Client Components, Suspense, streaming, and transitions. Ensures correct React 19 usage with TypeScript.
allowed-tools: Read, Grep, Glob, WebFetch, Bash
---

# React 19 Patterns - Comprehensive Guide

## When to Use This Skill

Use this skill when:
- Writing React components (Server or Client)
- Using React hooks (standard or new React 19 hooks)
- Implementing forms with Server Actions
- Working with Suspense and streaming
- Managing state and transitions
- Optimistic UI updates
- Migrating from React 18 to React 19

## What This Skill Covers

### Core Patterns
- **Server vs Client Components** - Complete decision tree
- **All React Hooks** - Complete reference with TypeScript
- **Suspense Patterns** - Boundaries, streaming, error handling
- **Server Components** - Data fetching, caching, composition
- **Client Components** - Interactivity, state, effects
- **Transitions** - useTransition, startTransition, isPending
- **Streaming** - Progressive rendering patterns
- **Migration Guide** - React 18 → React 19

### New in React 19
- `use()` - For async data in components
- `useOptimistic()` - For optimistic UI updates
- `useFormStatus()` - For form submission state
- `useActionState()` - For Server Action state
- Enhanced `useTransition()` - Better performance
- Improved error boundaries
- Better hydration

## Quick Reference

### Server Component Pattern
```typescript
// ✅ Default - async data fetching
export default async function ProjectsPage() {
  const projects = await db.project.findMany()
  return <ProjectList projects={projects} />
}
```

### Client Component Pattern
```typescript
// ✅ Use 'use client' for interactivity
'use client'

import { useState } from 'react'

export function InteractiveComponent() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

### New React 19 Hook Pattern
```typescript
'use client'

import { useOptimistic } from 'react'

export function TodoList({ todos }: Props) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: string) => [...state, { id: 'temp', text: newTodo, pending: true }]
  )

  return (
    <form action={async (formData) => {
      addOptimisticTodo(formData.get('todo'))
      await createTodo(formData)
    }}>
      <input name="todo" />
      <button type="submit">Add</button>
    </form>
  )
}
```

## File Structure

This skill is organized into detailed guides:

1. **server-vs-client.md** - Decision tree for component type
2. **hooks-complete.md** - All React hooks with TypeScript
3. **suspense-patterns.md** - Suspense boundaries and streaming
4. **server-components-complete.md** - Server Component patterns
5. **client-components-complete.md** - Client Component patterns
6. **transitions.md** - useTransition and concurrent features
7. **streaming-patterns.md** - Progressive rendering
8. **migration-guide.md** - React 18 → 19 migration
9. **validate-react.py** - Validation tool for React rules

## Decision Flow

```
START: Creating new component
│
├─ Does it need interactivity (onClick, onChange)?
│  ├─ YES → Read client-components-complete.md
│  └─ NO → Continue
│
├─ Does it need React hooks (useState, useEffect)?
│  ├─ YES → Read client-components-complete.md + hooks-complete.md
│  └─ NO → Continue
│
├─ Does it fetch data?
│  ├─ YES → Read server-components-complete.md
│  └─ NO → Continue
│
└─ Default → Server Component (read server-components-complete.md)

Need specific hook help?
└─ Read hooks-complete.md (complete reference)

Need Suspense/streaming?
└─ Read suspense-patterns.md + streaming-patterns.md

Need optimistic UI?
└─ Read hooks-complete.md (useOptimistic section)

Need form handling?
└─ Read hooks-complete.md (useFormStatus, useActionState)

Migrating from React 18?
└─ Read migration-guide.md
```

## Common Mistakes Prevented

### ❌ Async Client Component
```typescript
'use client'
export default async function Bad() {} // ERROR!
```

### ✅ Use Server Component or useEffect
```typescript
// Option 1: Server Component
export default async function Good() {} // ✅

// Option 2: Client with useEffect
'use client'
export default function Good() {
  useEffect(() => {
    fetchData()
  }, [])
}
```

### ❌ Hooks in Conditions
```typescript
if (condition) {
  useState(0) // ERROR: Rules of Hooks violation
}
```

### ✅ Hooks at Top Level
```typescript
const [value, setValue] = useState(0)
if (condition) {
  // Use the hook result here
}
```

### ❌ Browser APIs in Server Component
```typescript
export default function Bad() {
  const data = localStorage.getItem('key') // ERROR!
  return <div>{data}</div>
}
```

### ✅ Use Client Component
```typescript
'use client'
export default function Good() {
  const [data, setData] = useState(() =>
    localStorage.getItem('key')
  )
  return <div>{data}</div>
}
```

## Validation

Use `validate-react.py` to check your React code:

```bash
# Validate single file
python .claude/skills/react-19-patterns/validate-react.py src/components/Button.tsx

# Validate directory
python .claude/skills/react-19-patterns/validate-react.py src/components/

# Auto-fix (where possible)
python .claude/skills/react-19-patterns/validate-react.py --fix src/components/
```

Checks for:
- Rules of Hooks violations
- Server/Client component mistakes
- Missing 'use client' directives
- Invalid async Client Components
- Browser API usage in Server Components
- Non-serializable props to Client Components

## Best Practices

1. **Default to Server Components**
   - Better performance (no JS to client)
   - Direct data access
   - SEO friendly

2. **Use Client Components Sparingly**
   - Only when interactivity needed
   - Keep them small
   - Minimize bundle size

3. **Compose Server + Client**
   - Fetch data in Server Components
   - Pass as props to Client Components
   - Best of both worlds

4. **Use New React 19 Hooks**
   - `use()` for async data
   - `useOptimistic()` for instant feedback
   - `useFormStatus()` for form states
   - `useActionState()` for Server Actions

5. **Leverage Suspense**
   - Stream data progressively
   - Better perceived performance
   - Parallel data loading

## Resources

- React 19 Docs: https://react.dev/
- Server Components: https://react.dev/reference/rsc/server-components
- React 19 Changelog: https://react.dev/blog/2024/12/05/react-19
- Hooks API: https://react.dev/reference/react/hooks
- Server Actions: https://react.dev/reference/rsc/server-actions

## Quick Links

- [Server vs Client Decision Tree](./server-vs-client.md)
- [All Hooks Reference](./hooks-complete.md)
- [Suspense Patterns](./suspense-patterns.md)
- [Server Components Guide](./server-components-complete.md)
- [Client Components Guide](./client-components-complete.md)
- [Transitions Guide](./transitions.md)
- [Streaming Patterns](./streaming-patterns.md)
- [Migration Guide](./migration-guide.md)
- [Validation Tool](./validate-react.py)

---

**Last Updated**: 2025-11-23
**React Version**: 19.2.0
**Next.js Version**: 15.5
