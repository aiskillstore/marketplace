---
name: performance-optimization
description: Optimize application performance for speed, efficiency, and scalability. Use when improving page load times, reducing bundle size, optimizing database queries, or fixing performance bottlenecks. Handles React optimization, lazy loading, caching, code splitting, and profiling.
metadata:
  tags: performance, optimization, React, lazy-loading, caching, profiling, web-vitals
  platforms: Claude, ChatGPT, Gemini
---


# Performance Optimization


## When to use this skill

- **Slow page loads**: low Lighthouse score
- **Slow rendering**: delayed user interactions
- **Large bundle size**: increased download time
- **Slow queries**: database bottlenecks

## Instructions

### Step 1: Measure performance

**Lighthouse (Chrome DevTools)**:
```bash
# CLI
npm install -g lighthouse
lighthouse https://example.com --view

# Automate in CI
lighthouse https://example.com --output=json --output-path=./report.json
```

**Measure Web Vitals** (React):
```typescript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric: any) {
  // Send to Google Analytics, Datadog, etc.
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Step 2: Optimize React

**React.memo (prevent unnecessary re-renders)**:
```tsx
// ❌ Bad: child re-renders whenever the parent re-renders
function ExpensiveComponent({ data }: { data: Data }) {
  return <div>{/* complex rendering */}</div>;
}

// ✅ Good: re-render only when props change
const ExpensiveComponent = React.memo(({ data }: { data: Data }) => {
  return <div>{/* complex rendering */}</div>;
});
```

**useMemo & useCallback**:
```tsx
function ProductList({ products, category }: Props) {
  // ✅ Memoize filtered results
  const filteredProducts = useMemo(() => {
    return products.filter(p => p.category === category);
  }, [products, category]);

  // ✅ Memoize callback
  const handleAddToCart = useCallback((id: string) => {
    addToCart(id);
  }, []);

  return (
    <div>
      {filteredProducts.map(product => (
        <ProductCard key={product.id} product={product} onAdd={handleAddToCart} />
      ))}
    </div>
  );
}
```

**Lazy Loading & Code Splitting**:
```tsx
import { lazy, Suspense } from 'react';

// ✅ Route-based code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}

// ✅ Component-based lazy loading
const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<Skeleton />}>
        <HeavyChart data={data} />
      </Suspense>
    </div>
  );
}
```

### Step 3: Optimize bundle size

**Webpack Bundle Analyzer**:
```bash
npm install --save-dev webpack-bundle-analyzer

# package.json
{
  "scripts": {
    "analyze": "webpack-bundle-analyzer build/stats.json"
  }
}
```

**Tree Shaking (remove unused code)**:
```typescript
// ❌ Bad: import entire library
import _ from 'lodash';

// ✅ Good: import only what you need
import debounce from 'lodash/debounce';
```

**Dynamic Imports**:
```typescript
// ✅ Load only when needed
button.addEventListener('click', async () => {
  const { default: Chart } = await import('chart.js');
  new Chart(ctx, config);
});
```

### Step 4: Optimize images

**Next.js Image component**:
```tsx
import Image from 'next/image';

function ProductImage() {
  return (
    <Image
      src="/product.jpg"
      alt="Product"
      width={500}
      height={500}
      priority  // for the LCP image
      placeholder="blur"  // blur placeholder
      sizes="(max-width: 768px) 100vw, 50vw"
    />
  );
}
```

**Use WebP format**:
```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.jpg" type="image/jpeg">
  <img src="image.jpg" alt="Fallback">
</picture>
```

### Step 5: Optimize database queries

**Fix the N+1 query problem**:
```typescript
// ❌ Bad: N+1 queries
const posts = await db.post.findMany();
for (const post of posts) {
  const author = await db.user.findUnique({ where: { id: post.authorId } });
  // 101 queries (1 + 100)
}

// ✅ Good: JOIN or include
const posts = await db.post.findMany({
  include: {
    author: true
  }
});
// 1 query
```

**Add indexes**:
```sql
-- Identify slow queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Add index
CREATE INDEX idx_users_email ON users(email);

-- Composite index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);
```

**Caching (Redis)**:
```typescript
async function getUserProfile(userId: string) {
  // 1. Check cache
  const cached = await redis.get(`user:${userId}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // 2. Query DB
  const user = await db.user.findUnique({ where: { id: userId } });

  // 3. Store in cache (1 hour)
  await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}
```

## Output format

### Performance optimization checklist

```markdown
## Frontend
- [ ] Prevent unnecessary re-renders with React.memo
- [ ] Use useMemo/useCallback appropriately
- [ ] Lazy loading & Code splitting
- [ ] Optimize images (WebP, lazy loading)
- [ ] Analyze and reduce bundle size

## Backend
- [ ] Remove N+1 queries
- [ ] Add database indexes
- [ ] Redis caching
- [ ] Compress API responses (gzip)
- [ ] Use a CDN

## Measurement
- [ ] Lighthouse score 90+
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1
```

## Constraints

### Required rules (MUST)

1. **Measure first**: profile, don't guess
2. **Incremental improvements**: optimize one thing at a time
3. **Performance monitoring**: track continuously

### Prohibited items (MUST NOT)

1. **Premature optimization**: don't optimize when there is no bottleneck
2. **Sacrificing readability**: don't make code complex for performance

## Best practices

1. **80/20 rule**: 80% improvement with 20% effort
2. **User-centered**: focus on improving real user experience
3. **Automation**: performance regression tests in CI

## References

- [web.dev/vitals](https://web.dev/vitals/)
- [React Optimization](https://react.dev/learn/render-and-commit#optimizing-performance)
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2025-01-01
- **Compatible platforms**: Claude, ChatGPT, Gemini

### Related skills
- [database-schema-design](../database-schema-design/SKILL.md)
- [ui-components](../ui-component-patterns/SKILL.md)

### Tags
`#performance` `#optimization` `#React` `#caching` `#lazy-loading` `#web-vitals` `#code-quality`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
