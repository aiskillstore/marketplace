---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: performance
---

# React Performance Patterns

React-specific performance optimization patterns, memoization strategies, bundle optimization, and Core Web Vitals improvements.

## Rendering Optimization

### React.memo for Component Memoization

**When to Use:**

- Component receives props that don't change often
- Component renders frequently
- Rendering is expensive

**Example:**

```javascript
// Before: Re-renders on every parent update
function ExpensiveComponent({ data, config }) {
  const processed = processComplex(data, config);
  return <Chart data={processed} />;
}

// After: Only re-renders when props change
const ExpensiveComponent = React.memo(({ data, config }) => {
  const processed = processComplex(data, config);
  return <Chart data={processed} />;
});
```

### useMemo for Expensive Computations

**When to Use:**

- Expensive calculations
- Derived data from props/state
- Preventing recalculation on every render

**Example:**

```javascript
function Component({ items, filter }) {
  // Expensive computation - memoize result
  const filteredItems = useMemo(() => {
    return items
      .filter(item => item.category === filter)
      .map(item => processComplex(item));
  }, [items, filter]);

  return <List items={filteredItems} />;
}
```

### useCallback for Function Props

**When to Use:**

- Passing functions to memoized children
- Functions used in dependency arrays
- Preventing function recreation on every render

**Example:**

```javascript
function Parent({ items }) {
  // Memoize callback to prevent child re-renders
  const handleClick = useCallback((id) => {
    console.log('Clicked:', id);
  }, []);

  return <Child items={items} onClick={handleClick} />;
}

const Child = React.memo(({ items, onClick }) => {
  return items.map(item => (
    <button key={item.id} onClick={() => onClick(item.id)}>
      {item.name}
    </button>
  ));
});
```

### Virtualization for Long Lists

**When to Use:**

- Rendering large lists (1000+ items)
- Performance issues with scrolling
- Memory concerns with many DOM nodes

**Example:**

```javascript
import { FixedSizeList } from 'react-window';

function LongList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>
          {items[index].name}
        </div>
      )}
    </FixedSizeList>
  );
}
```

## Bundle Optimization

### Code Splitting by Route

**Example:**

```javascript
import { lazy, Suspense } from 'react';

// Lazy load routes
const Dashboard = lazy(() => import('./Dashboard'));
const Settings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

### Component Lazy Loading

**Example:**

```javascript
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

### Tree Shaking

**Best Practices:**

- Use ES modules (import/export)
- Avoid default exports when possible
- Use named exports for better tree shaking
- Check bundle analyzer for unused code

### Dynamic Imports

**Example:**

```javascript
// Dynamic import for code splitting
async function loadFeature() {
  const { FeatureComponent } = await import('./Feature');
  return FeatureComponent;
}
```

### Bundle Analysis

**Tools:**

- webpack-bundle-analyzer
- source-map-explorer
- Next.js bundle analyzer

**Example:**

```bash
# Analyze bundle
npm run build
npx webpack-bundle-analyzer build/static/js/*.js
```

## Core Web Vitals

### LCP (Largest Contentful Paint) Optimization

**Target**: < 2.5s

**Strategies:**

- Optimize hero images (WebP, proper sizing)
- Preload critical resources
- Minimize render-blocking CSS/JS
- Use CDN for assets
- Optimize font loading

**Example:**

```html
<!-- Preload critical resources -->
<link rel="preload" href="/hero-image.webp" as="image">
<link rel="preload" href="/critical.css" as="style">
```

### FID (First Input Delay) Optimization

**Target**: < 100ms

**Strategies:**

- Reduce JavaScript execution time
- Break up long tasks
- Use web workers for heavy computation
- Defer non-critical JavaScript
- Minimize third-party scripts

**Example:**

```javascript
// Break up long tasks
function processLargeDataset(data) {
  // Use requestIdleCallback or setTimeout to break up work
  const chunkSize = 100;
  let index = 0;

  function processChunk() {
    const chunk = data.slice(index, index + chunkSize);
    processChunkData(chunk);
    index += chunkSize;

    if (index < data.length) {
      setTimeout(processChunk, 0); // Yield to browser
    }
  }

  processChunk();
}
```

### CLS (Cumulative Layout Shift) Prevention

**Target**: < 0.1

**Strategies:**

- Set image dimensions (width/height)
- Reserve space for dynamic content
- Avoid inserting content above existing
- Use CSS transforms for animations
- Preload fonts with font-display

**Example:**

```jsx
// Set image dimensions to prevent layout shift
<img
  src="/hero.jpg"
  width={1200}
  height={600}
  alt="Hero image"
/>

// Reserve space for dynamic content
<div style={{ minHeight: '400px' }}>
  {loading ? <Skeleton /> : <Content />}
</div>
```

## Memory Management

### Event Listener Cleanup

**Example:**

```javascript
useEffect(() => {
  const handler = () => {
    // Handle event
  };

  window.addEventListener('resize', handler);

  // Cleanup: Remove listener
  return () => {
    window.removeEventListener('resize', handler);
  };
}, []);
```

### Preventing Memory Leaks

**Common Patterns:**

- Remove event listeners in cleanup
- Clear intervals/timeouts
- Unsubscribe from observables
- Avoid closures retaining large objects

**Example:**

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    // Do something
  }, 1000);

  // Cleanup: Clear interval
  return () => {
    clearInterval(interval);
  };
}, []);
```

## Performance Monitoring

### React Profiler

**Example:**

```javascript
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
  console.log('Component:', id);
  console.log('Phase:', phase);
  console.log('Duration:', actualDuration);
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <YourApp />
    </Profiler>
  );
}
```

### Performance Metrics

**Key Metrics:**

- Component render time
- Re-render frequency
- Bundle size
- Core Web Vitals
- Memory usage

## Best Practices

### Do's

- ✅ Measure before optimizing
- ✅ Use React DevTools Profiler
- ✅ Memoize expensive computations
- ✅ Code split by route
- ✅ Lazy load heavy components
- ✅ Optimize images
- ✅ Monitor Core Web Vitals

### Don'ts

- ❌ Over-memoize (adds overhead)
- ❌ Premature optimization
- ❌ Ignore bundle size
- ❌ Block main thread
- ❌ Forget cleanup functions
- ❌ Load everything upfront

## Common Patterns

### Context Optimization

**Problem**: Context causes unnecessary re-renders

**Solution**: Split contexts or use selectors

```javascript
// Split contexts to prevent unnecessary re-renders
const UserContext = createContext();
const ThemeContext = createContext();

// Or use context selectors
function useUserSelector(selector) {
  const user = useContext(UserContext);
  return useMemo(() => selector(user), [user, selector]);
}
```

### List Optimization

**Problem**: Rendering large lists is slow

**Solution**: Virtualization or pagination

```javascript
// Use virtualization for long lists
import { FixedSizeList } from 'react-window';

// Or paginate
function PaginatedList({ items }) {
  const [page, setPage] = useState(0);
  const pageSize = 50;
  const pageItems = items.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <>
      {pageItems.map(item => <Item key={item.id} item={item} />)}
      <Pagination page={page} onPageChange={setPage} />
    </>
  );
}
```
