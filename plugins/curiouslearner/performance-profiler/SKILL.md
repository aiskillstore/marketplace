---
name: performance-profiler
description: Analyze code performance patterns and identify optimization opportunities.
---

# Performance Profiler Skill

Analyze code performance patterns and identify optimization opportunities.

## Instructions

You are a performance optimization expert. When invoked:

1. **Identify Performance Issues**:
   - Inefficient algorithms (O(n²) where O(n) possible)
   - Memory leaks and excessive allocations
   - Unnecessary re-renders (React/Vue)
   - Blocking operations on main thread
   - N+1 query problems
   - Excessive network requests
   - Large bundle sizes
   - Unoptimized loops and iterations

2. **Analyze Patterns**:
   - Function call frequency and duration
   - Memory usage patterns
   - CPU-intensive operations
   - I/O bottlenecks
   - Database query efficiency
   - Render performance (frontend)

3. **Measure Impact**:
   - Time complexity analysis
   - Space complexity analysis
   - Actual runtime measurements (if possible)
   - Memory footprint
   - Bundle size impact

4. **Provide Recommendations**:
   - Specific optimization strategies
   - Code examples showing improvements
   - Expected performance gains
   - Trade-offs and considerations

## Performance Anti-Patterns

### Inefficient Algorithms
```javascript
// ❌ O(n²) - Inefficient
function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) duplicates.push(arr[i]);
    }
  }
  return duplicates;
}

// ✓ O(n) - Efficient
function findDuplicates(arr) {
  const seen = new Set();
  const duplicates = new Set();
  for (const item of arr) {
    if (seen.has(item)) duplicates.add(item);
    seen.add(item);
  }
  return Array.from(duplicates);
}
```

### Unnecessary Re-renders
```javascript
// ❌ Re-renders on every parent update
function ExpensiveComponent({ data }) {
  const processed = expensiveCalculation(data);
  return <div>{processed}</div>;
}

// ✓ Memoized, only re-renders when data changes
const ExpensiveComponent = React.memo(({ data }) => {
  const processed = useMemo(() => expensiveCalculation(data), [data]);
  return <div>{processed}</div>;
});
```

### N+1 Query Problem
```javascript
// ❌ N+1 queries
async function getPostsWithAuthors() {
  const posts = await db.posts.findAll();
  for (const post of posts) {
    post.author = await db.users.findById(post.authorId); // N queries
  }
  return posts;
}

// ✓ Single query with join
async function getPostsWithAuthors() {
  return await db.posts.findAll({
    include: [{ model: db.users, as: 'author' }]
  });
}
```

### Memory Leaks
```javascript
// ❌ Memory leak - event listener not cleaned up
useEffect(() => {
  window.addEventListener('scroll', handleScroll);
  // Missing cleanup!
}, []);

// ✓ Proper cleanup
useEffect(() => {
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

## Usage Examples

```
@performance-profiler
@performance-profiler src/
@performance-profiler UserList.jsx
@performance-profiler --focus algorithms
@performance-profiler --include-bundle-size
```

## Report Format

```markdown
# Performance Analysis Report

## Summary
- Files analyzed: 23
- Issues found: 18
- High priority: 4
- Medium priority: 9
- Low priority: 5
- Estimated improvement: 60% faster, 30% smaller bundle

## Critical Issues (4)

### 1. Inefficient Algorithm - src/utils/search.js:34
**Issue**: O(n²) search algorithm
**Current**: Linear search within loop (complexity: O(n²))
**Impact**: ~850ms for 1000 items
**Recommendation**: Use Map for O(1) lookups
**Expected improvement**: 99% faster (~8ms for 1000 items)

```javascript
// Current (slow)
function findMatches(items, queries) {
  return queries.map(q => items.find(i => i.id === q));
}

// Optimized
function findMatches(items, queries) {
  const itemMap = new Map(items.map(i => [i.id, i]));
  return queries.map(q => itemMap.get(q));
}
```

### 2. Unnecessary Re-renders - src/components/DataTable.jsx:45
**Issue**: Component re-renders on every state change
**Impact**: ~500ms render time for 100 rows
**Recommendation**: Implement React.memo and useMemo
**Expected improvement**: 80% reduction in render time

### 3. Bundle Size - Entire lodash imported
**Issue**: Importing entire lodash library (71KB gzipped)
**Current**: `import _ from 'lodash'`
**Recommendation**: Import only needed functions
**Expected improvement**: -65KB (91% reduction)

```javascript
// Instead of
import _ from 'lodash';

// Use
import debounce from 'lodash/debounce';
import throttle from 'lodash/throttle';
```

### 4. N+1 Database Queries - src/api/posts.js:67
**Issue**: Sequential database queries in loop
**Impact**: ~2000ms for 50 posts
**Recommendation**: Use eager loading/joins
**Expected improvement**: 95% faster (~100ms)

## Medium Priority Issues (9)

### Memory Allocations in Loop - src/parsers/csv.js:23
- Creating new objects in tight loop
- Recommendation: Reuse objects or use object pool
- Expected improvement: 40% less memory allocation

### Blocking Main Thread - src/workers/processor.js:89
- CPU-intensive calculation on main thread
- Recommendation: Move to Web Worker
- Expected improvement: UI remains responsive

## Bundle Analysis

**Total Bundle Size**: 487KB (gzipped: 142KB)

**Largest Dependencies**:
1. lodash - 71KB (use lodash-es or cherry-pick)
2. moment - 68KB (use date-fns or day.js)
3. chart.js - 52KB (consider lighter alternative)

**Recommendations**:
- Replace moment with date-fns: -55KB
- Use lodash-es with tree shaking: -50KB
- Lazy load chart.js: -52KB (move to async chunk)
- Total potential savings: ~157KB (110% improvement)

## Performance Metrics

### Time Complexity Issues
- O(n²): 3 instances (should be O(n) or O(n log n))
- O(n³): 1 instance (should be optimized)

### Memory Issues
- Potential memory leaks: 2
- Excessive allocations: 5
- Large object creation in loops: 4

## Recommendations Priority

**High Priority (Do First)**:
1. Fix O(n²) algorithm in search.js
2. Add React.memo to DataTable
3. Fix N+1 queries in posts API
4. Remove unused lodash imports

**Medium Priority**:
1. Move heavy computations to workers
2. Implement virtualization for long lists
3. Optimize image loading (lazy load, WebP)
4. Add response caching

**Low Priority (Nice to Have)**:
1. Code splitting for routes
2. Preload critical resources
3. Service worker for offline support
```

## Optimization Techniques

### Frontend Performance
- **Memoization**: Cache expensive calculations
- **Virtualization**: Render only visible items
- **Lazy Loading**: Load code/images on demand
- **Code Splitting**: Break bundle into chunks
- **Debouncing/Throttling**: Limit function calls
- **Web Workers**: Offload CPU-intensive tasks

### Backend Performance
- **Caching**: Redis, in-memory caches
- **Query Optimization**: Indexes, joins, pagination
- **Connection Pooling**: Reuse database connections
- **Async Operations**: Non-blocking I/O
- **Batching**: Combine multiple operations

### General Optimizations
- **Algorithm Choice**: Pick right data structure
- **Early Returns**: Exit loops/functions early
- **Avoid Premature Optimization**: Profile first
- **Lazy Evaluation**: Compute only when needed

## Profiling Tools

- **JavaScript**: Chrome DevTools, React Profiler, Lighthouse
- **Node.js**: clinic.js, 0x, node --prof
- **Python**: cProfile, memory_profiler, py-spy
- **Database**: Query analyzers, EXPLAIN plans
- **Bundle**: webpack-bundle-analyzer, source-map-explorer

## Notes

- Always profile before optimizing
- Measure actual impact after changes
- Consider readability vs performance trade-offs
- Focus on bottlenecks, not micro-optimizations
- Test performance improvements with realistic data
- Document why optimizations were made
