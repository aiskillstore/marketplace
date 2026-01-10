# Performance Optimization Checklist

## Database
- [ ] Indexes on foreign keys and frequently queried columns
- [ ] No N+1 query problems
- [ ] Proper use of eager loading
- [ ] Query result pagination
- [ ] Connection pooling configured
- [ ] SELECT specific columns, not *
- [ ] Caching for expensive queries

## Algorithms & Data Structures
- [ ] No O(n²) or worse in hot paths
- [ ] Appropriate data structure (hash map vs array)
- [ ] Memoization for repeated calculations
- [ ] Avoid premature optimization

## Frontend
- [ ] Code splitting and lazy loading
- [ ] Images optimized and lazy loaded
- [ ] Bundle size analyzed and minimized
- [ ] React.memo / useMemo / useCallback where needed
- [ ] Virtual scrolling for long lists
- [ ] Debounce/throttle expensive operations

## Network
- [ ] HTTP/2 or HTTP/3 enabled
- [ ] Compression enabled (gzip/brotli)
- [ ] CDN for static assets
- [ ] Proper caching headers
- [ ] Minimize number of requests

## Memory
- [ ] Event listeners cleaned up
- [ ] Timers cleared
- [ ] No circular references
- [ ] Cache size limits
- [ ] Proper garbage collection

## Monitoring
- [ ] Performance metrics tracked
- [] Error tracking in place
- [ ] Database slow query log
- [ ] Application profiling in production
