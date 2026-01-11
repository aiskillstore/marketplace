---
name: Performance Fundamentals
description: Auto-invoke when reviewing loops, data fetching, rendering, database queries, or resource-intensive operations. Identifies N+1 queries, unnecessary re-renders, memory leaks, and scalability issues.
---

# Performance Fundamentals Review

> "Premature optimization is the root of all evil, but mature ignorance is worse."

## When to Apply

Activate this skill when reviewing:
- Database queries (especially in loops)
- React/Vue render logic
- API response payloads
- Data transformations
- File operations
- Caching decisions

---

## Review Checklist

### Database Performance

- [ ] **No N+1 queries**: Are related records fetched in bulk, not loops?
- [ ] **Indexes**: Are frequently queried fields indexed?
- [ ] **Pagination**: Do list endpoints paginate results?
- [ ] **Select only needed fields**: Are we fetching entire records unnecessarily?

### Frontend Performance

- [ ] **Memoization**: Are expensive computations cached?
- [ ] **Re-render prevention**: Will state changes cause unnecessary re-renders?
- [ ] **Bundle size**: Are heavy libraries lazy-loaded?
- [ ] **Image optimization**: Are images properly sized and formatted?

### API Performance

- [ ] **Response size**: Is the payload minimal?
- [ ] **Compression**: Is gzip/brotli enabled?
- [ ] **Caching headers**: Are cacheable responses marked?
- [ ] **Async processing**: Are slow operations queued?

### Memory & Resources

- [ ] **Cleanup**: Are subscriptions/timers cleaned up?
- [ ] **Memory leaks**: Are event listeners removed?
- [ ] **Connection pooling**: Are DB connections reused?

---

## Common Mistakes (Anti-Patterns)

### 1. The N+1 Query Problem
```
❌ const users = await User.findAll();
   for (const user of users) {
     user.posts = await Post.findByUserId(user.id); // N queries!
   }

✅ const users = await User.findAll({
     include: [{ model: Post }] // 1 query with JOIN
   });
```

### 2. Unnecessary Re-renders
```
❌ function Parent() {
     const handleClick = () => {}; // New function every render
     return <Child onClick={handleClick} />;
   }

✅ function Parent() {
     const handleClick = useCallback(() => {}, []);
     return <Child onClick={handleClick} />;
   }
```

### 3. Computing in Render
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

### 4. Fetching Everything
```
❌ GET /api/users → returns 10,000 users with all fields

✅ GET /api/users?page=1&limit=20&fields=id,name,email
```

### 5. Missing Cleanup
```
❌ useEffect(() => {
     const interval = setInterval(fetchData, 5000);
     // No cleanup! Runs forever.
   }, []);

✅ useEffect(() => {
     const interval = setInterval(fetchData, 5000);
     return () => clearInterval(interval);
   }, []);
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Scale**: "What happens when there are 10,000 items? 1,000,000?"
2. **Queries**: "How many database queries does this operation make?"
3. **Re-renders**: "When this state changes, what components re-render?"
4. **Memory**: "Is anything holding a reference after it's no longer needed?"
5. **Payload**: "Does the client need ALL of this data?"

---

## Big O Quick Reference

| Pattern | Complexity | Example | At 10,000 items |
|---------|------------|---------|-----------------|
| Direct lookup | O(1) | `map.get(key)` | 1 op |
| Single loop | O(n) | `array.find()` | 10,000 ops |
| Nested loops | O(n²) | `for i { for j }` | 100,000,000 ops |
| Sort | O(n log n) | `array.sort()` | ~130,000 ops |

---

## Performance Targets

| Metric | Target | Measure With |
|--------|--------|--------------|
| Time to First Byte (TTFB) | < 600ms | DevTools Network |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| First Input Delay (FID) | < 100ms | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| API Response Time | < 200ms (p95) | Server metrics |

---

## Red Flags to Call Out

| Flag | Question to Ask |
|------|-----------------|
| Query inside a loop | "Can we batch this into one query?" |
| No pagination | "What if there are 100,000 records?" |
| `SELECT *` | "Do we need all these fields?" |
| Large JSON in localStorage | "Will this slow down page load?" |
| Inline function in JSX | "Does this create a new function every render?" |
| setInterval without cleanup | "What clears this when the component unmounts?" |
| Synchronous file operations | "Should this be async?" |
| No loading states | "What does the user see while waiting?" |

---

## Quick Wins

1. **Add indexes** to frequently queried DB columns
2. **Paginate** all list endpoints
3. **Lazy load** below-the-fold content
4. **Compress** API responses
5. **Cache** expensive computations with useMemo
6. **Debounce** search inputs
7. **Virtualize** long lists (react-window)
