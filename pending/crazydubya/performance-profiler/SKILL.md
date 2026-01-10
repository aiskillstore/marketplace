---
name: performance-profiler
description: Identifies performance bottlenecks including N+1 queries, inefficient loops, memory leaks, and slow algorithms. Use when user mentions performance issues, slow code, optimization, or profiling.
allowed-tools: Read, Grep, Glob
---

# Performance Profiler

Identifies and suggests fixes for common performance bottlenecks in code.

## When to Use
- User reports performance issues or slow code
- Optimization requests
- Code review for performance
- User mentions "slow", "bottleneck", "optimization", "memory leak"

## Instructions

### 1. Identify Performance Anti-Patterns

**N+1 Query Problems:**
```javascript
// Bad: N+1 queries
users.forEach(user => {
  const posts = db.query('SELECT * FROM posts WHERE user_id = ?', user.id);
});

// Good: Single query with JOIN
const usersWithPosts = db.query('SELECT * FROM users LEFT JOIN posts ON users.id = posts.user_id');
```

**Inefficient Loops:**
```python
# Bad: O(n²) nested loops
for item in list1:
    for other in list2:
        if item.id == other.id:
            process(item, other)

# Good: O(n) with hash map
lookup = {other.id: other for other in list2}
for item in list1:
    if item.id in lookup:
        process(item, lookup[item.id])
```

**Unnecessary Re-renders (React):**
```javascript
// Bad: Creates new object on every render
<Component style={{ margin: 10 }} />

// Good: Define outside or useMemo
const style = { margin: 10 };
<Component style={style} />
```

**Memory Leaks:**
- Event listeners not cleaned up
- Timers not cleared
- Circular references
- Large caches without limits

**Blocking Operations:**
- Synchronous file I/O
- Long-running calculations in UI thread
- Missing pagination

### 2. Database Performance

**Check for:**
- Missing indexes on foreign keys
- SELECT * instead of specific columns
- Queries in loops (N+1)
- Missing query limits
- Inefficient JOINs

**Suggest:**
- Add indexes: `CREATE INDEX idx_user_id ON posts(user_id);`
- Use eager loading/prefetching
- Implement pagination
- Use database query analyzers (EXPLAIN)

### 3. Algorithm Complexity

**Identify:**
- O(n²) or worse algorithms
- Redundant calculations
- Unnecessary sorting
- Inefficient data structures

**Common fixes:**
- Hash maps for O(1) lookup vs O(n) array search
- Binary search O(log n) vs linear search O(n)
- Memoization for repeated calculations
- Lazy evaluation for expensive operations

### 4. Frontend Performance

**Check for:**
- Large bundle sizes
- Unoptimized images
- Missing code splitting
- Inefficient React components
- Missing memoization

**Suggest:**
- Lazy loading: `const Component = lazy(() => import('./Component'));`
- Image optimization
- Debounce/throttle expensive operations
- Virtual scrolling for long lists
- Web Workers for heavy computations

### 5. Network Performance

**Issues:**
- Too many HTTP requests
- Large payloads
- Missing caching
- Synchronous requests

**Solutions:**
- Bundle/concatenate resources
- Implement compression (gzip, brotli)
- Use HTTP/2 multiplexing
- Add caching headers
- Parallel vs sequential requests

### 6. Generate Performance Report

```
Performance Analysis
===================

Critical Issues (Fix Immediately):
1. N+1 query in UserController.index (file.js:45)
   - Impact: 100+ DB queries per request
   - Fix: Use eager loading or JOIN

2. Memory leak in EventEmitter (file.js:120)
   - Impact: Memory grows unbounded
   - Fix: Remove listeners in cleanup

High Priority:
3. O(n²) loop in processData (file.js:200)
   - Impact: Slow for large datasets
   - Fix: Use hash map for O(n)

Medium Priority:
4. Missing image optimization
   - Impact: Slow page load
   - Fix: Use next/image or optimize manually
```

### 7. Profiling Tools

**JavaScript:**
- Chrome DevTools Performance tab
- Node.js --inspect flag
- `console.time()` / `console.timeEnd()`

**Python:**
- cProfile module
- line_profiler
- memory_profiler

**Database:**
- EXPLAIN / EXPLAIN ANALYZE
- Slow query log
- pg_stat_statements (PostgreSQL)

## Best Practices
- Profile before optimizing
- Focus on hot paths (80/20 rule)
- Measure impact of changes
- Consider readability vs performance trade-offs
- Document performance-critical sections
