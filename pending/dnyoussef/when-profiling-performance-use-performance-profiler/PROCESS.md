# Performance Profiler - Detailed Process Flow

## Overview

This document describes the complete step-by-step process for comprehensive performance profiling, bottleneck detection, optimization, and validation.

## Process Architecture

### High-Level Flow
```
Input (Application + Workload)
  → Baseline Phase
    → Detection Phase (Parallel: CPU, Memory, I/O, Network)
      → Analysis Phase
        → Optimization Phase
          → Implementation Phase
            → Validation Phase
              → Output (Report + Optimizations + Benchmarks)
```

## Phase 1: Baseline & Initialization

### Step 1.1: Environment Setup
**Objective**: Prepare profiling environment

**Actions**:
1. Detect runtime environment (Node.js, Python, Java, etc.)
2. Verify profiling tools available
3. Check system resources
4. Configure profiling parameters
5. Set up monitoring infrastructure

**Output**: Environment configuration
```json
{
  "runtime": "node",
  "version": "v18.16.0",
  "platform": "linux",
  "profilers": {
    "cpu": "v8-profiler",
    "memory": "heapdump",
    "io": "strace",
    "network": "tcpdump"
  },
  "system": {
    "cpu_cores": 8,
    "memory_gb": 16,
    "disk_type": "ssd"
  }
}
```

### Step 1.2: Baseline Measurement
**Objective**: Establish current performance metrics

**Metrics to Capture**:
- Throughput (requests/second)
- Latency (p50, p95, p99, p99.9)
- Error rate
- CPU utilization
- Memory usage
- I/O operations
- Network bandwidth
- Concurrent connections

**Actions**:
1. Start application in profiling mode
2. Generate realistic workload
3. Capture metrics for statistical significance
4. Record system resource usage
5. Store baseline snapshot

**Output**: Baseline metrics snapshot

### Step 1.3: Performance Budget Definition
**Objective**: Define acceptable performance thresholds

**Actions**:
1. Review performance requirements
2. Set target metrics based on SLA
3. Define regression thresholds
4. Document performance budgets

**Output**: Performance budget configuration

## Phase 2: Bottleneck Detection

### Step 2.1: CPU Profiling
**Objective**: Identify CPU-intensive code paths

**Profiling Methods**:

#### Sampling Profiler (Low Overhead):
```javascript
// Start sampling profiler
const profiler = require('v8-profiler-next');
profiler.startProfiling('CPU_PROFILE', true);

// Run workload
await runWorkload();

// Stop and save profile
const profile = profiler.stopProfiling('CPU_PROFILE');
profile.export((error, result) => {
  fs.writeFileSync('cpu-profile.cpuprofile', result);
});
```

#### Instrumentation Profiler (Accurate):
```javascript
// Instrument all functions
const instrumented = instrumentCode(sourceCode);

// Track execution time
function instrumentFunction(fn, name) {
  return function(...args) {
    const start = performance.now();
    const result = fn.apply(this, args);
    const duration = performance.now() - start;
    recordTiming(name, duration);
    return result;
  };
}
```

**Analysis**:
1. Load CPU profile data
2. Build call tree
3. Calculate self-time and total-time
4. Identify hot paths (>10% CPU time)
5. Generate flame graph
6. Detect excessive function calls
7. Analyze algorithm complexity

**Output**: CPU bottleneck report
```json
{
  "hot_paths": [
    {
      "function": "processData",
      "file": "lib/processor.js:45",
      "self_time_percent": 34.5,
      "total_time_percent": 42.1,
      "calls": 123456,
      "avg_duration_ms": 2.3,
      "complexity": "O(n²)",
      "recommendation": "Use hash map for O(n) lookup"
    }
  ],
  "flame_graph": "cpu-flame-graph.svg"
}
```

### Step 2.2: Memory Profiling
**Objective**: Analyze memory usage and detect leaks

**Profiling Methods**:

#### Heap Snapshot:
```javascript
const heapdump = require('heapdump');

// Capture initial snapshot
heapdump.writeSnapshot('heap-before.heapsnapshot');

// Run workload
await runWorkload();

// Capture after snapshot
heapdump.writeSnapshot('heap-after.heapsnapshot');

// Compare snapshots
const comparison = compareSnapshots('heap-before', 'heap-after');
```

#### Allocation Tracking:
```javascript
// Track all allocations
const profiler = require('v8-profiler-next');
profiler.startTrackingHeapObjects();

// Run workload
await runWorkload();

// Stop tracking and analyze
const snapshot = profiler.takeHeapSnapshot();
profiler.stopTrackingHeapObjects();
```

#### Garbage Collection Profiling:
```bash
# Run with GC logging
node --trace-gc --trace-gc-verbose app.js
```

**Analysis**:
1. Load heap snapshots
2. Compare before/after memory state
3. Identify retained objects
4. Trace retention paths
5. Detect memory growth patterns
6. Analyze GC frequency and duration
7. Calculate allocation rate
8. Identify memory leaks

**Output**: Memory analysis report
```json
{
  "heap_size_mb": 512,
  "used_mb": 387,
  "allocations_per_sec": 12345,
  "gc_pauses": {
    "count": 23,
    "avg_duration_ms": 45,
    "max_duration_ms": 123
  },
  "leaks_detected": [
    {
      "type": "EventEmitter",
      "count": 45678,
      "retained_size_mb": 23.4,
      "growth_rate_mb_per_hour": 2.3,
      "retention_path": "SessionManager -> EventEmitter -> listeners[]",
      "recommendation": "Remove event listeners in cleanup"
    }
  ]
}
```

### Step 2.3: I/O Profiling
**Objective**: Analyze file system and database performance

**File System Profiling**:
```bash
# Linux: Use strace to trace system calls
strace -c -p <pid> -e trace=open,read,write,close,stat

# Summary of syscalls
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 45.67    0.123456         234      5678        12 read
 34.21    0.098765         123      8901        23 write
 12.34    0.045678          89      5123         0 open
```

**Database Query Profiling**:
```javascript
// Enable query logging
const { Pool } = require('pg');
const pool = new Pool({
  log: (msg) => {
    if (msg.duration > 100) { // Log slow queries
      console.log(`Slow query: ${msg.query} (${msg.duration}ms)`);
    }
  }
});

// Analyze query execution plans
const explainQuery = async (query) => {
  const plan = await pool.query(`EXPLAIN ANALYZE ${query}`);
  return analyzeQueryPlan(plan.rows);
};
```

**Analysis**:
1. Track I/O operations (reads, writes, seeks)
2. Measure I/O latency distribution
3. Identify slow queries (>100ms)
4. Analyze query execution plans
5. Detect N+1 query patterns
6. Check index usage
7. Identify missing indexes
8. Analyze connection pool utilization

**Output**: I/O analysis report
```json
{
  "file_system": {
    "ops_per_sec": 234,
    "avg_latency_ms": 12,
    "read_throughput_mb": 45.6,
    "write_throughput_mb": 23.4
  },
  "database": {
    "queries_per_sec": 567,
    "avg_query_time_ms": 23,
    "slow_queries": [
      {
        "query": "SELECT * FROM users WHERE email = $1",
        "avg_duration_ms": 456,
        "calls": 12345,
        "issue": "Missing index on email column",
        "recommendation": "CREATE INDEX idx_users_email ON users(email)"
      }
    ],
    "n_plus_1_patterns": [
      {
        "parent_query": "SELECT * FROM orders",
        "child_queries": "SELECT * FROM order_items WHERE order_id = $1",
        "redundant_queries": 1234,
        "recommendation": "Use JOIN or eager loading"
      }
    ]
  }
}
```

### Step 2.4: Network Profiling
**Objective**: Analyze network requests and bandwidth

**Request Timing**:
```javascript
const http = require('http');
const { performance } = require('perf_hooks');

// Instrument HTTP requests
const originalRequest = http.request;
http.request = function(...args) {
  const start = performance.now();
  const req = originalRequest.apply(this, args);

  req.on('response', (res) => {
    const duration = performance.now() - start;
    recordRequestTiming(req.path, duration);
  });

  return req;
};
```

**Network Packet Analysis**:
```bash
# Capture network packets
tcpdump -i any -w network-capture.pcap

# Analyze with tshark
tshark -r network-capture.pcap -q -z io,stat,1
```

**Analysis**:
1. Measure request/response timing
2. Analyze DNS lookup time
3. Measure TCP connection time
4. Track TLS handshake duration
5. Analyze bandwidth usage
6. Identify slow external APIs
7. Check connection pooling
8. Detect request batching opportunities

**Output**: Network analysis report
```json
{
  "requests_per_sec": 1247,
  "avg_latency_ms": 23,
  "latency_breakdown": {
    "dns_lookup_ms": 2,
    "tcp_connection_ms": 5,
    "tls_handshake_ms": 12,
    "ttfb_ms": 18,
    "content_download_ms": 8
  },
  "external_apis": [
    {
      "endpoint": "https://api.external.com/v1/data",
      "calls_per_sec": 89,
      "avg_duration_ms": 145,
      "p95_duration_ms": 234,
      "recommendation": "Add caching layer"
    }
  ],
  "connection_pool": {
    "size": 100,
    "active": 78,
    "idle": 22,
    "utilization_percent": 78,
    "recommendation": "Pool size adequate"
  }
}
```

## Phase 3: Root Cause Analysis

### Step 3.1: Correlation Analysis
**Objective**: Find relationships between metrics

**Actions**:
1. Correlate CPU spikes with specific code paths
2. Link memory growth to allocation sources
3. Associate I/O latency with query patterns
4. Connect network delays to external dependencies

**Output**: Correlation matrix

### Step 3.2: Impact Assessment
**Objective**: Quantify performance impact of each bottleneck

**Calculation**:
```javascript
function calculateImpact(bottleneck) {
  const currentTime = bottleneck.total_time_ms;
  const estimatedOptimizedTime = bottleneck.total_time_ms * 0.1; // 90% reduction
  const timeSavings = currentTime - estimatedOptimizedTime;

  const currentThroughput = baseline.requests_per_second;
  const bottleneckPercent = bottleneck.time_percent / 100;
  const estimatedThroughputIncrease =
    currentThroughput / (1 - bottleneckPercent * 0.9);

  return {
    time_savings_ms: timeSavings,
    throughput_improvement: estimatedThroughputIncrease / currentThroughput,
    latency_reduction_percent: bottleneckPercent * 0.9 * 100
  };
}
```

### Step 3.3: Prioritization
**Objective**: Rank bottlenecks by impact and effort

**Scoring Algorithm**:
```javascript
function prioritizeBottlenecks(bottlenecks) {
  return bottlenecks.map(b => ({
    ...b,
    impact_score: calculateImpactScore(b),
    effort_score: estimateEffortScore(b),
    priority_score: calculateImpactScore(b) / estimateEffortScore(b)
  })).sort((a, b) => b.priority_score - a.priority_score);
}
```

**Output**: Prioritized bottleneck list

## Phase 4: Optimization Generation

### Step 4.1: Algorithmic Optimizations
**Objective**: Generate algorithm improvements

**Pattern Detection**:
```javascript
function detectAlgorithmicPatterns(code, profile) {
  const patterns = [];

  // Detect nested loops
  if (hasNestedLoops(code)) {
    patterns.push({
      type: 'nested_loops',
      current_complexity: 'O(n²)',
      recommendation: 'Use hash map for O(n) lookup',
      estimated_improvement: '10-100x'
    });
  }

  // Detect linear search
  if (hasLinearSearch(code)) {
    patterns.push({
      type: 'linear_search',
      current_complexity: 'O(n)',
      recommendation: 'Use binary search or hash map for O(log n) or O(1)',
      estimated_improvement: '10-1000x'
    });
  }

  // Detect redundant computation
  if (hasRedundantComputation(code)) {
    patterns.push({
      type: 'redundant_computation',
      recommendation: 'Use memoization or caching',
      estimated_improvement: '2-10x'
    });
  }

  return patterns;
}
```

**Code Generation**:
```javascript
function generateOptimizedCode(originalCode, pattern) {
  switch (pattern.type) {
    case 'nested_loops':
      return optimizeNestedLoops(originalCode);
    case 'linear_search':
      return optimizeLinearSearch(originalCode);
    case 'redundant_computation':
      return addMemoization(originalCode);
  }
}
```

### Step 4.2: Caching Strategies
**Objective**: Identify caching opportunities

**Patterns**:
1. **Function Memoization**: Cache expensive function results
2. **Query Result Caching**: Cache database query results
3. **Template Caching**: Cache compiled templates
4. **API Response Caching**: Cache external API responses
5. **CDN Caching**: Cache static assets

**Implementation**:
```javascript
// Example: Add memoization
function memoize(fn) {
  const cache = new Map();
  return function(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

// Example: Add Redis caching
async function getCachedData(key, fetchFn, ttl = 3600) {
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);
  }

  const data = await fetchFn();
  await redis.setex(key, ttl, JSON.stringify(data));
  return data;
}
```

### Step 4.3: Parallelization
**Objective**: Identify parallel execution opportunities

**Patterns**:
```javascript
// Sequential → Parallel
// Before:
for (const item of items) {
  await processItem(item);
}

// After:
await Promise.all(items.map(item => processItem(item)));

// Worker threads for CPU-intensive tasks
const { Worker } = require('worker_threads');

function runInWorker(data) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker.js', { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}

// Process in parallel across workers
const results = await Promise.all(
  chunks.map(chunk => runInWorker(chunk))
);
```

### Step 4.4: Database Optimizations
**Objective**: Generate database improvements

**Optimization Types**:

1. **Add Indexes**:
```sql
-- Analysis identifies missing index
-- Query: SELECT * FROM users WHERE email = 'user@example.com'
-- Execution plan shows Seq Scan on users (cost=0.00..12345.67)

-- Generated optimization:
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

2. **Fix N+1 Queries**:
```javascript
// Before: N+1 queries
const orders = await Order.findAll();
for (const order of orders) {
  order.items = await OrderItem.findAll({ where: { orderId: order.id } });
}

// After: Single query with JOIN
const orders = await Order.findAll({
  include: [{ model: OrderItem }]
});
```

3. **Query Optimization**:
```sql
-- Before: Inefficient query
SELECT * FROM orders WHERE customer_id IN (
  SELECT id FROM customers WHERE country = 'USA'
);

-- After: Optimized with JOIN
SELECT o.* FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
WHERE c.country = 'USA';
```

### Step 4.5: Memory Optimizations
**Objective**: Reduce memory usage

**Techniques**:
1. **Object Pooling**: Reuse objects instead of creating new ones
2. **Streaming**: Process data in chunks instead of loading all at once
3. **Compression**: Compress data in memory
4. **Weak References**: Use WeakMap for caches
5. **Cleanup**: Remove event listeners and clear intervals

**Implementation Examples**:
```javascript
// Object pooling
class ObjectPool {
  constructor(factory, size = 100) {
    this.factory = factory;
    this.pool = Array.from({ length: size }, factory);
    this.available = [...this.pool];
  }

  acquire() {
    return this.available.pop() || this.factory();
  }

  release(obj) {
    this.available.push(obj);
  }
}

// Streaming instead of buffering
const fs = require('fs');
const stream = require('stream');

// Before: Load entire file into memory
const data = fs.readFileSync('large-file.txt', 'utf8');
processData(data);

// After: Stream processing
fs.createReadStream('large-file.txt')
  .pipe(new stream.Transform({
    transform(chunk, encoding, callback) {
      processChunk(chunk);
      callback();
    }
  }));
```

## Phase 5: Implementation

### Step 5.1: Code Generation
**Objective**: Generate optimized code with coder agent

**Agent Instructions**:
```javascript
Task("Coder Agent", `
  Implement the following optimizations for ./app:

  1. Optimize processData() function:
     - Current: O(n²) nested loops
     - Target: O(n) using hash map
     - Expected improvement: 3.2x

  2. Add memoization to renderTemplate():
     - Use LRU cache with max 1000 entries
     - Expected improvement: 12% CPU reduction

  3. Fix memory leak in SessionManager:
     - Remove event listeners in cleanup method
     - Expected improvement: Prevent OOM crashes

  Requirements:
  - Maintain existing API interfaces
  - Add comprehensive tests
  - Update documentation
  - Run benchmark to verify improvements

  Use coordination hooks to share progress.
`, "coder");
```

### Step 5.2: Database Migration Generation
**Objective**: Create database optimization scripts

**Generated Migration**:
```sql
-- Migration: Add missing indexes
-- Generated: 2025-10-30 14:23:45

BEGIN;

-- Add index on users.email (estimated 2.8x speedup for email lookups)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);

-- Add composite index on orders (estimated 4.1x speedup for date range queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_created
  ON orders(customer_id, created_at DESC);

-- Add partial index on orders (reduce index size by 60%)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_pending
  ON orders(status, created_at)
  WHERE status = 'pending';

COMMIT;

-- Verify index usage
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Step 5.3: Configuration Updates
**Objective**: Apply configuration optimizations

**Examples**:
```javascript
// Database connection pool
const pool = new Pool({
  max: 100, // Increased from 20 based on profiling
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Redis cache configuration
const redis = new Redis({
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  lazyConnect: true,
});

// HTTP server optimization
const server = http.createServer({
  keepAlive: true,
  keepAliveTimeout: 60000,
  maxHeaderSize: 8192,
});
```

## Phase 6: Validation

### Step 6.1: Test Execution
**Objective**: Ensure optimizations don't break functionality

**Actions**:
1. Run unit tests
2. Run integration tests
3. Run end-to-end tests
4. Verify no regressions

### Step 6.2: Benchmark Execution
**Objective**: Measure performance improvements

**Benchmark Suite**:
```javascript
const { performance } = require('perf_hooks');

async function runBenchmark(fn, iterations = 1000) {
  // Warmup
  for (let i = 0; i < 100; i++) {
    await fn();
  }

  // Measure
  const durations = [];
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    await fn();
    durations.push(performance.now() - start);
  }

  return {
    min: Math.min(...durations),
    max: Math.max(...durations),
    mean: durations.reduce((a, b) => a + b) / durations.length,
    p50: percentile(durations, 0.5),
    p95: percentile(durations, 0.95),
    p99: percentile(durations, 0.99)
  };
}
```

### Step 6.3: Comparison & Report
**Objective**: Compare baseline vs optimized performance

**Comparison**:
```javascript
function comparePerformance(baseline, optimized) {
  return {
    throughput_improvement: optimized.rps / baseline.rps,
    latency_reduction: (baseline.p95 - optimized.p95) / baseline.p95,
    cpu_reduction: (baseline.cpu - optimized.cpu) / baseline.cpu,
    memory_reduction: (baseline.memory - optimized.memory) / baseline.memory,
    improvements: {
      throughput: `${baseline.rps} → ${optimized.rps} req/s (+${((optimized.rps / baseline.rps - 1) * 100).toFixed(1)}%)`,
      latency_p95: `${baseline.p95}ms → ${optimized.p95}ms (-${(((baseline.p95 - optimized.p95) / baseline.p95) * 100).toFixed(1)}%)`,
      cpu: `${baseline.cpu}% → ${optimized.cpu}% (-${(((baseline.cpu - optimized.cpu) / baseline.cpu) * 100).toFixed(1)}%)`,
      memory: `${baseline.memory}MB → ${optimized.memory}MB (-${(((baseline.memory - optimized.memory) / baseline.memory) * 100).toFixed(1)}%)`
    }
  };
}
```

**Final Report**:
```json
{
  "optimization_summary": {
    "optimizations_applied": 8,
    "total_time_hours": 12,
    "performance_improvement": {
      "throughput": "+3.2x",
      "latency_p95": "-68%",
      "cpu_usage": "-37%",
      "memory_usage": "-45%"
    }
  },
  "before": { ... },
  "after": { ... },
  "regression_check": "passed",
  "production_ready": true
}
```

## Integration Points

### Claude-Flow Coordination:
```bash
# Throughout profiling process
npx claude-flow@alpha hooks pre-task --description "Performance profiling for my-app"
npx claude-flow@alpha hooks post-edit --file "profiling-report.json" --memory-key "swarm/profiler/report"
npx claude-flow@alpha hooks notify --message "CPU profiling complete: 3 bottlenecks found"
npx claude-flow@alpha hooks post-task --task-id "profiler-001"
```

## See Also

- SKILL.md - Complete skill documentation
- README.md - Quick start guide
- subagent-performance-profiler.md - Agent implementation
- process-diagram.gv - Visual process flow diagram
