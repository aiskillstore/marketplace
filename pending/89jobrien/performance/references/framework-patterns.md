---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: performance
---

# Performance Analysis Framework Patterns

Reference guide for performance analysis patterns specific to different frameworks and technologies.

## Node.js Performance Patterns

### Event Loop Blocking

**Detection:**

- High event loop delay (> 10ms)
- Slow response times
- CPU spikes

**Common Causes:**

- Synchronous file operations
- CPU-intensive computations
- Large JSON parsing
- Synchronous crypto operations

**Solutions:**

- Use async file operations
- Move heavy computation to worker threads
- Stream large data processing
- Use async crypto operations

### Memory Leaks

**Detection:**

- Gradual memory growth
- No decrease after requests complete
- High heap usage

**Common Patterns:**

- Unclosed event listeners
- Closures retaining large objects
- Circular references
- Timers not cleared

**Solutions:**

- Remove event listeners
- Use WeakMap/WeakSet
- Clear timers/intervals
- Monitor with heap snapshots

## React Performance Patterns

### Unnecessary Re-renders

**Detection:**

- Components re-render on every parent update
- Performance issues with large lists
- Slow interactions

**Solutions:**

- Use React.memo for components
- useMemo for expensive computations
- useCallback for function props
- Optimize context usage

### Bundle Size Issues

**Detection:**

- Large initial bundle size
- Slow first load
- High Lighthouse scores

**Solutions:**

- Code splitting by route
- Lazy load components
- Tree shaking unused code
- Dynamic imports
- Analyze bundle with webpack-bundle-analyzer

## Database Performance Patterns

### Slow Queries

**Detection:**

- Queries taking > 100ms
- High database CPU usage
- Slow query logs

**Common Causes:**

- Missing indexes
- Full table scans
- Complex JOINs
- Suboptimal query plans

**Solutions:**

- Add appropriate indexes
- Optimize query structure
- Use EXPLAIN ANALYZE
- Consider denormalization
- Implement query caching

### Connection Issues

**Detection:**

- Connection pool exhaustion
- Connection timeouts
- High connection count

**Solutions:**

- Increase pool size
- Implement connection retry
- Add connection timeout
- Use connection pooling
- Monitor connection metrics

## API Performance Patterns

### Slow Endpoints

**Detection:**

- High response times
- Timeout errors
- Slow p95/p99 percentiles

**Common Causes:**

- N+1 queries
- Synchronous operations
- External API calls
- Large payloads

**Solutions:**

- Optimize database queries
- Implement caching
- Use async operations
- Batch external calls
- Compress responses

### Rate Limiting

**Detection:**

- 429 Too Many Requests errors
- API quota exceeded
- Throttling issues

**Solutions:**

- Implement client-side rate limiting
- Add request queuing
- Use exponential backoff
- Cache responses
- Batch requests

## Frontend Performance Patterns

### Core Web Vitals

**LCP (Largest Contentful Paint):**

- Optimize hero images
- Preload critical resources
- Minimize render-blocking CSS/JS
- Use CDN for assets

**FID (First Input Delay):**

- Reduce JavaScript execution time
- Break up long tasks
- Use web workers
- Defer non-critical JavaScript

**CLS (Cumulative Layout Shift):**

- Set image dimensions
- Reserve space for dynamic content
- Avoid inserting content above existing
- Use CSS transforms for animations

### Resource Loading

**Optimization Strategies:**

- Lazy load images
- Preload critical resources
- Prefetch likely next pages
- Use resource hints (preconnect, dns-prefetch)
- Implement service workers

## Monitoring Patterns

### Key Metrics

**Application Metrics:**

- Response time (p50, p95, p99)
- Throughput (requests/second)
- Error rate
- CPU usage
- Memory usage

**Database Metrics:**

- Query execution time
- Connection pool usage
- Lock contention
- Cache hit rate

**Frontend Metrics:**

- Core Web Vitals
- Bundle size
- Resource load times
- Time to interactive

### Alerting Thresholds

**Response Time:**

- Warning: p95 > 500ms
- Critical: p95 > 1000ms

**Error Rate:**

- Warning: > 1%
- Critical: > 5%

**Memory:**

- Warning: > 80% of limit
- Critical: > 90% of limit

**CPU:**

- Warning: > 70% average
- Critical: > 90% average
