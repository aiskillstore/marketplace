---
name: Performance Gate
description: Verify performance implications were considered and no obvious anti-patterns exist. Issues result in WARNINGS.
---

# Gate 4: Performance Review

> "Code that works is step one. Code that scales is step two."

## Purpose

This gate catches performance anti-patterns before they cause problems. The focus is on obvious issues, not micro-optimizations.

## Gate Status

- **PASS** — No obvious performance issues
- **WARNING** — Issues found that could cause problems at scale

---

## Gate Questions

### Question 1: Scalability
> "What happens when there are 10,000 items? 1,000,000?"

**Looking for:**
- Awareness of data growth
- Pagination for large datasets
- Efficient data structures
- No unnecessary loops

### Question 2: Query Efficiency
> "How many database queries does this operation make?"

**Looking for:**
- No N+1 queries
- Bulk operations where appropriate
- Indexes on queried columns
- Awareness of query cost

### Question 3: Re-render Awareness (Frontend)
> "When this state changes, what components re-render?"

**Looking for:**
- Awareness of render triggers
- Appropriate memoization
- State placement optimization
- No expensive computations in render

---

## Performance Checklist

### Database Operations
- [ ] No N+1 queries (queries inside loops)
- [ ] Pagination for list endpoints
- [ ] Indexes on frequently queried columns
- [ ] SELECT only needed columns (not SELECT *)

### Frontend Rendering
- [ ] Expensive computations use useMemo
- [ ] Event handlers use useCallback where needed
- [ ] Large lists use virtualization
- [ ] Heavy components are lazy loaded

### API & Network
- [ ] Response payloads are minimal
- [ ] Large data is paginated
- [ ] Caching headers where appropriate
- [ ] No redundant API calls

### General
- [ ] No nested loops (O(n²)) without justification
- [ ] No blocking operations
- [ ] Cleanup of intervals/timeouts
- [ ] Reasonable memory usage

---

## Response Templates

### If PASS

```
✅ PERFORMANCE GATE: PASSED

Performance considerations look good:
- Data fetching is efficient
- No obvious N+1 patterns
- Appropriate pagination in place

Moving to the next gate...
```

### If WARNING

```
⚠️ PERFORMANCE GATE: WARNING

Found [X] performance concerns:

**Issue 1: [N+1 Query / Inefficient Loop]**
Location: `file.ts:42`
Question: "This makes [N] queries. Can we batch into 1?"

**Issue 2: [Missing Pagination]**
Location: `file.ts:88`
Question: "What happens with 100,000 records?"

**Issue 3: [Expensive Render]**
Location: `Component.tsx:15`
Question: "Does this need to recalculate on every render?"

These may not matter now, but will become problems as the app grows.
```

---

## Common Issues to Check

### 1. The N+1 Query Problem
```
❌ const users = await User.findAll();
   for (const user of users) {
     user.posts = await Post.findByUserId(user.id);
   }
   // 1 + N queries!

✅ const users = await User.findAll({
     include: [{ model: Post }]
   });
   // 1 query with JOIN
```

### 2. Fetching Everything
```
❌ // Returns 10,000 users with 50 fields each
   GET /api/users

✅ // Paginated with only needed fields
   GET /api/users?page=1&limit=20&fields=id,name,email
```

### 3. Expensive Render Calculations
```
❌ function UserList({ users }) {
     // Runs on every render
     const sorted = users.sort((a, b) => a.name.localeCompare(b.name));
     return <ul>{sorted.map(...)}</ul>;
   }

✅ function UserList({ users }) {
     const sorted = useMemo(
       () => [...users].sort((a, b) => a.name.localeCompare(b.name)),
       [users]
     );
     return <ul>{sorted.map(...)}</ul>;
   }
```

### 4. Inline Functions Causing Re-renders
```
❌ function Parent() {
     return <Child onClick={() => doSomething()} />;
     // New function every render → Child re-renders
   }

✅ function Parent() {
     const handleClick = useCallback(() => doSomething(), []);
     return <Child onClick={handleClick} />;
   }
```

### 5. Missing Cleanup
```
❌ useEffect(() => {
     const interval = setInterval(fetchData, 5000);
     // Memory leak! Runs forever
   }, []);

✅ useEffect(() => {
     const interval = setInterval(fetchData, 5000);
     return () => clearInterval(interval);
   }, []);
```

---

## Socratic Performance Questions

Instead of pointing out the fix, ask:

1. "How many queries does this endpoint execute for 100 users?"
2. "If I add 10,000 more items, what breaks?"
3. "Does this array get re-sorted on every render?"
4. "What clears this interval when the component unmounts?"
5. "Do we need all 50 columns from this table?"

---

## Big O Quick Reference

| Pattern | Complexity | 10,000 items | Concern Level |
|---------|------------|--------------|---------------|
| Map lookup | O(1) | 1 op | Fine |
| Single loop | O(n) | 10,000 ops | Usually fine |
| Nested loop | O(n²) | 100M ops | Warning |
| Triple loop | O(n³) | 1T ops | Critical |

---

## Performance Red Flags

| Flag | Question | Why |
|------|----------|-----|
| Query in a loop | "Can we batch?" | N+1 problem |
| No pagination | "What at scale?" | Memory/time explosion |
| SELECT * | "Need all fields?" | Wasted bandwidth |
| setInterval no cleanup | "What clears this?" | Memory leak |
| Inline object/function in JSX | "New reference?" | Unnecessary re-renders |
| Array.sort() in render | "Cached?" | Runs every render |

---

## When to NOT Worry

Not everything needs optimization:

- **Small datasets**: Don't paginate 20 items
- **Rare operations**: One-time admin scripts can be slow
- **Prototype phase**: Get it working first
- **Micro-optimizations**: Focus on algorithms, not `for` vs `forEach`

The gate is about catching **obvious** issues, not micro-optimization.
