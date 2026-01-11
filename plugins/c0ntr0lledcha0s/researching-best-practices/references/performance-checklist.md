# Performance Best Practices Checklist

Comprehensive checklist for optimizing application performance across frontend, backend, and database layers.

## General Performance Principles

### Measurement & Monitoring
- [ ] Performance metrics defined (TTFB, FCP, LCP, TTI, CLS)
- [ ] Real User Monitoring (RUM) in place
- [ ] Synthetic monitoring for critical paths
- [ ] Performance budgets established
- [ ] Regular performance profiling
- [ ] Lighthouse/WebPageTest audits
- [ ] APM (Application Performance Monitoring) tools integrated

### Optimization Strategy
- [ ] Profile before optimizing (don't guess)
- [ ] Focus on user-perceived performance
- [ ] Optimize critical rendering path first
- [ ] Use performance budgets as gates
- [ ] Document performance requirements
- [ ] Test on real devices and networks

---

## Frontend Performance

### Loading Performance

#### Resource Optimization
- [ ] Images optimized (format, size, compression)
  - Use WebP/AVIF for modern browsers
  - Provide fallbacks for older browsers
  - Properly sized images (srcset, picture element)
  - Lazy load off-screen images
- [ ] Minify CSS, JavaScript, HTML
- [ ] Remove unused CSS/JS (tree-shaking)
- [ ] Compress assets (gzip, brotli)
- [ ] Use CDN for static assets
- [ ] Implement resource hints (preconnect, prefetch, preload)

#### Code Splitting
- [ ] Route-based code splitting
- [ ] Component-based code splitting
- [ ] Vendor bundle separation
- [ ] Dynamic imports for heavy modules
- [ ] Lazy load below-the-fold content

#### Caching Strategy
- [ ] Static assets have long cache times (1 year+)
- [ ] Content-addressable filenames (hashing)
- [ ] Service Worker for offline support
- [ ] Cache-Control headers configured
- [ ] ETag/Last-Modified headers
- [ ] Cache invalidation strategy

#### Network Optimization
- [ ] HTTP/2 or HTTP/3 enabled
- [ ] Minimize HTTP requests
- [ ] Combine critical CSS inline
- [ ] Defer non-critical JavaScript
- [ ] Reduce DNS lookups
- [ ] Connection pooling

### Runtime Performance

#### JavaScript Optimization
- [ ] Avoid long tasks (>50ms)
- [ ] Use Web Workers for heavy computation
- [ ] Debounce/throttle expensive operations
- [ ] RequestAnimationFrame for animations
- [ ] Avoid memory leaks (cleanup listeners)
- [ ] Optimize loops and iterations
- [ ] Use efficient data structures

#### React/Vue/Angular Specific
- [ ] **React**:
  - Use React.memo for expensive components
  - useMemo/useCallback for expensive computations
  - Virtual scrolling for long lists
  - Code splitting with React.lazy
  - Avoid inline functions in render
  - Key props on lists
- [ ] **Vue**:
  - Use v-once for static content
  - v-memo for expensive renders
  - Computed properties vs methods
  - Keep components small
  - Virtual scrolling (vue-virtual-scroller)
- [ ] **Angular**:
  - OnPush change detection
  - TrackBy functions for *ngFor
  - Lazy load modules
  - Pure pipes
  - Detach change detector when needed

#### Rendering Performance
- [ ] Minimize DOM manipulations
- [ ] Batch DOM updates
- [ ] Use CSS transforms for animations (GPU-accelerated)
- [ ] Avoid layout thrashing
- [ ] Virtual scrolling for long lists
- [ ] Pagination for large datasets
- [ ] Skeleton screens for perceived performance

### Third-Party Scripts
- [ ] Audit third-party scripts
- [ ] Load third-party scripts async/defer
- [ ] Use facade pattern for heavy embeds (YouTube, Maps)
- [ ] Monitor third-party performance impact
- [ ] Consider self-hosting critical scripts

---

## Backend Performance

### Application Layer

#### Code Optimization
- [ ] Profile hot paths
- [ ] Optimize database queries (N+1 prevention)
- [ ] Use connection pooling
- [ ] Implement pagination
- [ ] Avoid synchronous I/O
- [ ] Use streams for large data
- [ ] Optimize regular expressions
- [ ] Memoize expensive functions

#### Concurrency & Async
- [ ] Use async/await properly
- [ ] Non-blocking I/O
- [ ] Worker threads for CPU-intensive tasks
- [ ] Queue heavy jobs (background processing)
- [ ] Rate limiting
- [ ] Circuit breakers for external services
- [ ] Timeouts on all external calls

#### Caching
- [ ] Cache database queries
- [ ] Cache API responses
- [ ] Use Redis/Memcached for distributed cache
- [ ] Cache-aside pattern
- [ ] Cache invalidation strategy
- [ ] CDN for static content
- [ ] HTTP caching headers

#### API Design
- [ ] Pagination for lists
- [ ] Field filtering (sparse fieldsets)
- [ ] Batch endpoints
- [ ] GraphQL for flexible queries
- [ ] Compression (gzip, brotli)
- [ ] ETags for conditional requests
- [ ] API rate limiting

### Server Configuration

#### Web Server
- [ ] Enable compression
- [ ] HTTP/2 or HTTP/3
- [ ] Connection keep-alive
- [ ] Proper worker process count
- [ ] Static file serving optimized
- [ ] Reverse proxy (Nginx, Caddy)
- [ ] Load balancing

#### Application Server
- [ ] Cluster mode enabled
- [ ] Auto-scaling configured
- [ ] Health checks
- [ ] Graceful shutdown
- [ ] Process manager (PM2, systemd)
- [ ] Resource limits

---

## Database Performance

### Query Optimization
- [ ] Add indexes on frequently queried columns
- [ ] Composite indexes for multi-column queries
- [ ] Avoid SELECT * (specify columns)
- [ ] Use EXPLAIN to analyze queries
- [ ] Prevent N+1 queries (eager loading)
- [ ] Batch inserts/updates
- [ ] Use database views for complex queries
- [ ] Optimize JOIN operations
- [ ] Limit result sets (pagination)

### Indexing Strategy
- [ ] Index foreign keys
- [ ] Index WHERE clause columns
- [ ] Index ORDER BY columns
- [ ] Index columns in JOIN conditions
- [ ] Avoid over-indexing (write performance impact)
- [ ] Use covering indexes when possible
- [ ] Monitor index usage
- [ ] Remove unused indexes

### Connection Management
- [ ] Use connection pooling
- [ ] Proper pool size configuration
- [ ] Connection timeout settings
- [ ] Close connections properly
- [ ] Monitor active connections
- [ ] Prepared statements for repeated queries

### Data Design
- [ ] Normalize to reduce redundancy
- [ ] Denormalize for read-heavy workloads
- [ ] Partition large tables
- [ ] Archive old data
- [ ] Use appropriate data types
- [ ] Avoid BLOBs in frequently accessed tables
- [ ] Consider read replicas for scaling

### Caching
- [ ] Query result caching
- [ ] Use database query cache (MySQL)
- [ ] Application-level caching
- [ ] Materialized views
- [ ] Cache invalidation on writes

---

## Network & Infrastructure

### CDN & Edge
- [ ] Use CDN for static assets
- [ ] Edge caching for dynamic content
- [ ] Geographic distribution
- [ ] DDoS protection
- [ ] SSL/TLS offloading at edge

### Load Balancing
- [ ] Distribute traffic across servers
- [ ] Health checks
- [ ] Session affinity if needed
- [ ] Auto-scaling groups
- [ ] Geographic load balancing

### Infrastructure
- [ ] Use appropriate instance types
- [ ] Vertical scaling when needed
- [ ] Horizontal scaling for stateless services
- [ ] Container orchestration (Kubernetes)
- [ ] Serverless for variable workloads
- [ ] Monitor resource utilization

---

## Mobile Performance

### Mobile-Specific
- [ ] Optimize for 3G networks
- [ ] Reduce payload sizes
- [ ] Minimize battery usage
- [ ] Adaptive loading based on connection
- [ ] Touch-optimized interactions (no 300ms delay)
- [ ] Optimize for low-end devices
- [ ] Test on real devices

### Progressive Web Apps
- [ ] Service Worker for offline
- [ ] App shell architecture
- [ ] Background sync
- [ ] Push notifications
- [ ] Add to home screen

---

## Monitoring & Debugging

### Metrics to Track
- [ ] Response time (p50, p95, p99)
- [ ] Throughput (requests/second)
- [ ] Error rate
- [ ] Apdex score
- [ ] Time to First Byte (TTFB)
- [ ] First Contentful Paint (FCP)
- [ ] Largest Contentful Paint (LCP)
- [ ] Cumulative Layout Shift (CLS)
- [ ] Time to Interactive (TTI)
- [ ] Database query time
- [ ] Cache hit ratio
- [ ] Memory usage
- [ ] CPU usage

### Tools
- [ ] Chrome DevTools Performance tab
- [ ] Lighthouse
- [ ] WebPageTest
- [ ] New Relic / Datadog / AppDynamics
- [ ] Database profiling tools
- [ ] Load testing (k6, JMeter, Artillery)

---

## Quick Wins

### Easiest Performance Improvements
1. **Enable compression** (gzip/brotli) - 2 minutes
2. **Optimize images** - 30 minutes
3. **Add caching headers** - 15 minutes
4. **Enable HTTP/2** - 10 minutes
5. **Lazy load images** - 30 minutes
6. **Minify assets** - 5 minutes
7. **Use CDN** - 1 hour
8. **Add database indexes** - 1 hour
9. **Enable query caching** - 30 minutes
10. **Defer non-critical JS** - 30 minutes

---

## Common Performance Pitfalls

### What to Avoid
- ❌ No performance monitoring
- ❌ Optimizing without profiling
- ❌ Ignoring mobile/slow networks
- ❌ Large bundle sizes
- ❌ Synchronous loading
- ❌ N+1 database queries
- ❌ No caching strategy
- ❌ Uncompressed assets
- ❌ No code splitting
- ❌ Premature optimization
- ❌ Memory leaks
- ❌ Long-running tasks on main thread
- ❌ Large images
- ❌ Too many HTTP requests
- ❌ Blocking the critical rendering path

---

## Performance Budget Template

```
Target Metrics:
- Lighthouse Performance Score: ≥ 90
- Time to Interactive: < 3s (3G)
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Total Blocking Time: < 300ms

Resource Budgets:
- JavaScript: < 170KB (gzipped)
- CSS: < 50KB (gzipped)
- Images: < 500KB total
- Fonts: < 100KB
- Total page weight: < 1MB
- HTTP requests: < 50
```

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
