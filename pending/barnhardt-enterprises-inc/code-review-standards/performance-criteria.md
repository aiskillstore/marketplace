# Performance Criteria

## Performance Review Checklist

### Database Queries

#### N+1 Query Problem
```typescript
// 🔴 BAD: N+1 queries (1 + N)
const users = await db.select().from(usersTable)
for (const user of users) {
  const projects = await db
    .select()
    .from(projectsTable)
    .where(eq(projectsTable.userId, user.id)) // N queries!
}

// ✅ GOOD: Single query with join
const usersWithProjects = await db
  .select()
  .from(usersTable)
  .leftJoin(projectsTable, eq(usersTable.id, projectsTable.userId))
```

#### Missing Indexes
```typescript
// Check for slow queries on:
- WHERE clauses without index
- Foreign keys without index
- Sorting columns without index
```

#### Unnecessary Data Fetching
```typescript
// 🔴 BAD: Fetching all columns
const users = await db.select().from(usersTable)

// ✅ GOOD: Select only needed columns
const users = await db
  .select({ id: usersTable.id, name: usersTable.name })
  .from(usersTable)
```

---

### Async Operations

#### Sequential vs Parallel
```typescript
// 🔴 BAD: Sequential (slow)
const projects = await fetchProjects()
const users = await fetchUsers()
const tasks = await fetchTasks()

// ✅ GOOD: Parallel (fast)
const [projects, users, tasks] = await Promise.all([
  fetchProjects(),
  fetchUsers(),
  fetchTasks(),
])
```

#### Unnecessary Awaits
```typescript
// 🔴 BAD: Unnecessary await
async function process() {
  await doSomething()
  await doSomethingElse()
  return 'done'
}

// ✅ GOOD: Only await when needed
async function process() {
  doSomething() // Fire and forget
  await doSomethingElse() // Must wait
  return 'done'
}
```

---

### React Performance

#### Unnecessary Re-renders
```typescript
// 🔴 BAD: Object created on every render
function Component() {
  const style = { color: 'red' } // New object each render!
  return <div style={style}>Text</div>
}

// ✅ GOOD: Memoize or move outside
const style = { color: 'red' }

function Component() {
  return <div style={style}>Text</div>
}
```

#### Expensive Calculations
```typescript
// 🔴 BAD: Expensive calculation on every render
function Component({ items }) {
  const sorted = items.sort((a, b) => a.value - b.value) // Sorts every render!
  return <List items={sorted} />
}

// ✅ GOOD: Memoize expensive calculation
import { useMemo } from 'react'

function Component({ items }) {
  const sorted = useMemo(
    () => items.sort((a, b) => a.value - b.value),
    [items]
  )
  return <List items={sorted} />
}
```

#### Large Lists Without Virtualization
```typescript
// 🔴 BAD: Rendering 10,000 items
function Component({ items }) {
  return (
    <div>
      {items.map(item => <ItemCard key={item.id} item={item} />)}
    </div>
  )
}

// ✅ GOOD: Use virtualization for large lists
import { Virtualizer } from '@tanstack/react-virtual'

function Component({ items }) {
  // Only render visible items
}
```

---

### Images and Assets

#### Unoptimized Images
```typescript
// 🔴 BAD: Large unoptimized image
<img src="/large-image.png" width={100} height={100} />

// ✅ GOOD: Next.js Image component
import Image from 'next/image'

<Image
  src="/large-image.png"
  width={100}
  height={100}
  alt="Description"
/>
```

#### Missing Lazy Loading
```typescript
// 🔴 BAD: All images load immediately
<img src="/image.png" alt="..." />

// ✅ GOOD: Lazy load below-fold images
<img src="/image.png" alt="..." loading="lazy" />
```

---

### Pagination

#### Loading All Data
```typescript
// 🔴 BAD: Loading 100,000 records
const projects = await db.select().from(projectsTable)

// ✅ GOOD: Paginate
const projects = await db
  .select()
  .from(projectsTable)
  .limit(20)
  .offset((page - 1) * 20)
```

---

### Caching

#### No Caching Strategy
```typescript
// 🔴 BAD: Fetching same data repeatedly
async function getUser(id: string) {
  return db.select().from(usersTable).where(eq(usersTable.id, id))
}

// ✅ GOOD: Cache with React Query
const { data: user } = useQuery({
  queryKey: ['user', id],
  queryFn: () => getUser(id),
  staleTime: 5 * 60 * 1000, // 5 minutes
})
```

---

## Performance Metrics

### Target Metrics
- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.8s
- **Total Blocking Time (TBT)**: < 200ms
- **Cumulative Layout Shift (CLS)**: < 0.1

### Database Query Times
- Simple SELECT: < 10ms
- JOIN queries: < 50ms
- Complex queries: < 100ms

### API Response Times
- GET endpoint: < 200ms
- POST endpoint: < 500ms
- Complex operations: < 1s

---

## Review Template

```markdown
### 🟡 [Performance] [Issue Type]

**Location**: `src/path/file.ts:line`

**Issue**: [Description of performance problem]

**Impact**:
- Current: [O(n²), 500ms, etc.]
- Expected: [O(n), 50ms, etc.]

**Fix**:
```typescript
// Optimized implementation
```

**Metrics**:
- Before: [measurement]
- After: [measurement]
```

---

## See Also

- [Next.js Performance](https://nextjs.org/docs/app/building-your-application/optimizing)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Database Indexing](../architecture-patterns/database-patterns.md)
