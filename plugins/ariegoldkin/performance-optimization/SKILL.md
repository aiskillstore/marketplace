---
name: performance-optimization
description: Full-stack performance analysis, optimization patterns, and monitoring strategies
version: 1.0.0
category: Quality & Optimization
agents: [backend-system-architect, frontend-ui-developer, code-quality-reviewer]
keywords: [performance, optimization, speed, latency, throughput, caching, profiling, bundle, Core Web Vitals]
---

# Performance Optimization Skill

Comprehensive frameworks for analyzing and optimizing application performance across the entire stack.

## When to Use

- Application feels slow or unresponsive
- Database queries taking too long
- Frontend bundle size too large
- API response times exceed targets
- Core Web Vitals need improvement
- Preparing for scale or high traffic

## Performance Targets

### Core Web Vitals (Frontend)

| Metric | Good | Needs Work |
|--------|------|------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | < 4s |
| **INP** (Interaction to Next Paint) | < 200ms | < 500ms |
| **CLS** (Cumulative Layout Shift) | < 0.1 | < 0.25 |
| **TTFB** (Time to First Byte) | < 200ms | < 600ms |

### Backend Targets

| Operation | Target |
|-----------|--------|
| Simple reads | < 100ms |
| Complex queries | < 500ms |
| Write operations | < 200ms |
| Index lookups | < 10ms |

## Bottleneck Categories

| Category | Symptoms | Tools |
|----------|----------|-------|
| **Network** | High TTFB, slow loading | Network tab, WebPageTest |
| **Database** | Slow queries, pool exhaustion | EXPLAIN ANALYZE, pg_stat_statements |
| **CPU** | High usage, slow compute | Profiler, flame graphs |
| **Memory** | Leaks, GC pauses | Heap snapshots |
| **Rendering** | Layout thrashing | React DevTools, Performance tab |

## Database Optimization

### Key Patterns

1. **Add Missing Indexes** - Turn `Seq Scan` into `Index Scan`
2. **Fix N+1 Queries** - Use JOINs or `include` instead of loops
3. **Cursor Pagination** - Never load all records
4. **Connection Pooling** - Manage connection lifecycle

### Quick Diagnostics

```sql
-- Find slow queries (PostgreSQL)
SELECT query, calls, mean_time / 1000 as mean_seconds
FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Verify index usage
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
```

> See `templates/database-optimization.ts` for N+1 fixes and pagination patterns

## Caching Strategy

### Cache Hierarchy

```
L1: In-Memory (LRU, memoization) - fastest
L2: Distributed (Redis/Memcached) - shared
L3: CDN (edge, static assets) - global
L4: Database (materialized views) - fallback
```

### Cache-Aside Pattern

```typescript
const cached = await redis.get(key);
if (cached) return JSON.parse(cached);
const data = await db.query(...);
await redis.setex(key, 3600, JSON.stringify(data));
return data;
```

> See `templates/caching-patterns.ts` for full implementation

## Frontend Optimization

### Bundle Optimization

1. **Code Splitting** - `lazy()` for route-based splitting
2. **Tree Shaking** - Import only what you need
3. **Image Optimization** - WebP/AVIF, lazy loading, proper sizing

### Rendering Optimization

1. **Memoization** - `memo()`, `useCallback()`, `useMemo()`
2. **Virtualization** - Render only visible items in long lists
3. **Batch DOM Operations** - Read all, then write all

> See `templates/frontend-optimization.tsx` for patterns

### Analysis Commands

```bash
# Lighthouse audit
lighthouse http://localhost:3000 --output=json

# Bundle analysis
npx @next/bundle-analyzer  # Next.js
npx vite-bundle-visualizer # Vite
```

## API Optimization

### Response Optimization

1. **Field Selection** - Return only requested fields
2. **Compression** - Enable gzip/brotli (threshold: 1KB)
3. **ETags** - Enable 304 responses for unchanged data
4. **Pagination** - Cursor-based for large datasets

> See `templates/api-optimization.ts` for middleware examples

## Monitoring Checklist

### Before Launch

- [ ] Lighthouse score > 90
- [ ] Core Web Vitals pass
- [ ] Bundle size within budget
- [ ] Database queries profiled
- [ ] Compression enabled
- [ ] CDN configured

### Ongoing

- [ ] Performance monitoring active
- [ ] Alerting for degradation
- [ ] Lighthouse CI in pipeline
- [ ] Weekly query analysis
- [ ] Real User Monitoring (RUM)

> See `templates/performance-metrics.ts` for Prometheus metrics setup

## Extended Thinking Triggers

Use Opus 4.5 extended thinking for:
- **Complex debugging** - Multiple potential causes
- **Architecture decisions** - Caching strategy selection
- **Trade-off analysis** - Memory vs CPU vs latency
- **Root cause analysis** - Performance regression investigation

## Templates Reference

| Template | Purpose |
|----------|---------|
| `database-optimization.ts` | N+1 fixes, pagination, pooling |
| `caching-patterns.ts` | Redis cache-aside, memoization |
| `frontend-optimization.tsx` | React memo, virtualization, code splitting |
| `api-optimization.ts` | Compression, ETags, field selection |
| `performance-metrics.ts` | Prometheus metrics, performance budget |
