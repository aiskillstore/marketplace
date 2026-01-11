# Performance Profiler - Quick Start Guide

## What is Performance Profiler?

A comprehensive multi-dimensional performance profiling system that identifies bottlenecks, generates optimizations, and validates improvements across CPU, memory, I/O, and network.

## When to Use

- Before production deployments
- When application feels slow
- For capacity planning
- When debugging performance issues
- For optimization sprints
- In CI/CD pipelines
- For continuous monitoring

## Quick Start

### 1. Basic Usage

```bash
# Quick 30-second scan
/profile .

# Standard 5-minute profiling
/profile . --mode standard

# Deep analysis with all targets
/profile . --mode deep --target all

# CPU-focused profiling
/profile . --target cpu --flame-graph

# Memory leak detection
/profile . --target memory --detect-leaks

# Database query optimization
/profile . --target io --database
```

### 2. Using the Subagent

```javascript
Task("Performance Profiler",
  "Profile ./my-app with standard CPU and memory analysis, generate optimizations",
  "performance-analyzer")
```

### 3. Using MCP Tool

```javascript
mcp__performance-profiler__analyze({
  project_path: "./my-app",
  profiling_mode: "standard",
  targets: ["cpu", "memory", "io"],
  generate_optimizations: true,
  auto_benchmark: true
})
```

## Output Examples

### Console Output
```
⚡ Performance Profiler
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project: my-app
Mode: standard (300s)
Targets: CPU, Memory, I/O
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Baseline Performance:
  ├─ Throughput: 1,247 req/s
  ├─ Avg Response Time: 123ms
  ├─ P95 Response Time: 456ms
  ├─ P99 Response Time: 789ms
  ├─ CPU Usage: 67%
  ├─ Memory Usage: 512 MB
  └─ Error Rate: 0.1%

🔥 CPU Bottlenecks (3 found):
  1. [HIGH] processData() - 34.5% CPU time
     ├─ Called: 123,456 times
     ├─ Avg Time: 2.3ms
     └─ Issue: O(n²) algorithm complexity

  2. [MEDIUM] renderTemplate() - 12.3% CPU time
     ├─ Called: 45,678 times
     ├─ Avg Time: 0.8ms
     └─ Issue: No template caching

  3. [MEDIUM] validateInput() - 8.7% CPU time
     ├─ Called: 123,456 times
     ├─ Avg Time: 0.2ms
     └─ Issue: Redundant regex compilation

💾 Memory Analysis:
  ├─ Heap Size: 512 MB
  ├─ Used: 387 MB (75.6%)
  ├─ Allocations/sec: 12,345
  ├─ GC Pauses: 23 (avg 45ms)
  └─ Potential Leaks: 1 detected ⚠️

  [WARNING] Leak detected in SessionManager
  ├─ Growth Rate: 2.3 MB/hour
  ├─ Root Cause: Event listeners not removed
  └─ Retained Objects: 45,678

💿 I/O Analysis:
  ├─ File System: 234 ops/s (avg 12ms)
  ├─ Database Queries: 567 queries/s (avg 23ms)
  └─ Slow Queries: 12 queries > 100ms ⚠️

  Top 3 Slow Queries:
  1. SELECT * FROM users WHERE ... (456ms)
     └─ Missing index on email column
  2. SELECT * FROM orders WHERE ... (234ms)
     └─ N+1 query pattern detected
  3. SELECT * FROM products WHERE ... (123ms)
     └─ Full table scan

🌐 Network Analysis:
  ├─ Requests/sec: 1,247
  ├─ Avg Latency: 23ms
  ├─ External API Calls: 89 req/s (avg 145ms)
  └─ Connection Pool: 78% utilization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Optimization Recommendations (8 total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[CRITICAL] Optimize processData() algorithm
  Impact: 🔥🔥🔥 (Est. 3.2x throughput improvement)
  Effort: Medium
  Action: Replace nested loops with hash map lookup
  Code: See optimization-1.patch

[HIGH] Fix memory leak in SessionManager
  Impact: 🔥🔥 (Prevent OOM crashes)
  Effort: Low
  Action: Remove event listeners in cleanup
  Code: See optimization-2.patch

[HIGH] Add database index on users.email
  Impact: 🔥🔥 (2.8x query speedup)
  Effort: Low
  Action: CREATE INDEX idx_users_email ON users(email)

[MEDIUM] Implement template caching
  Impact: 🔥 (12% CPU reduction)
  Effort: Low
  Action: Add LRU cache for compiled templates

[MEDIUM] Fix N+1 query pattern
  Impact: 🔥 (8x query reduction)
  Effort: Medium
  Action: Use eager loading with JOIN

... 3 more recommendations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Estimated Total Improvement
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ├─ Throughput: 1,247 → 3,991 req/s (+3.2x)
  ├─ Response Time: 123ms → 39ms (-68%)
  ├─ CPU Usage: 67% → 42% (-37%)
  └─ Memory Usage: 512MB → 282MB (-45%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Output Files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ Performance Report: ./profiling/report.json
  ✓ CPU Flame Graph: ./profiling/cpu-flame-graph.svg
  ✓ Memory Heap Snapshot: ./profiling/heap-snapshot.heapsnapshot
  ✓ Optimization Patches: ./profiling/optimizations/*.patch
  ✓ Benchmark Results: ./profiling/benchmarks.json

✅ Profiling complete! Apply optimizations with: /profile --apply
```

## Common Workflows

### Workflow 1: CPU Bottleneck Investigation
```bash
# 1. Profile CPU with flame graph
/profile . --target cpu --flame-graph

# 2. Identify hot paths from flame graph
# Open ./profiling/cpu-flame-graph.svg in browser

# 3. Generate optimizations
/profile . --target cpu --optimize

# 4. Apply recommended optimizations
# Review and apply patches in ./profiling/optimizations/

# 5. Benchmark improvements
/profile . --benchmark --compare-baseline
```

### Workflow 2: Memory Leak Detection
```bash
# 1. Start continuous profiling
/profile . --mode continuous --target memory --detect-leaks

# 2. Let application run for 30-60 minutes
# Profiler tracks memory growth

# 3. Review leak report
cat ./profiling/memory-leaks.json

# 4. Fix identified leaks
# Apply suggested fixes

# 5. Verify leak fixed
/profile . --target memory --detect-leaks --duration 3600
```

### Workflow 3: Database Query Optimization
```bash
# 1. Profile database queries
/profile . --target io --database --explain-queries

# 2. Review slow query report
cat ./profiling/slow-queries.json

# 3. Add recommended indexes
# Execute suggested CREATE INDEX statements

# 4. Optimize N+1 queries
# Apply eager loading patches

# 5. Verify improvements
/profile . --target io --database --compare-baseline
```

### Workflow 4: Full Stack Optimization Sprint
```bash
# Day 1: Baseline and analysis
/profile . --mode deep --target all --baseline

# Day 2: Review recommendations with team
# Prioritize by impact and effort

# Day 3-4: Implementation
# Apply high-impact optimizations

# Day 5: Validation
/profile . --mode standard --target all --compare-baseline

# Result: 3.2x throughput, 68% latency reduction
```

## Integration Examples

### CI/CD Integration (GitHub Actions)
```yaml
name: Performance Regression Check
on: [pull_request]

jobs:
  perf-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Baseline performance
        run: |
          git checkout main
          /profile . --mode quick --baseline --output ./baseline.json

      - name: Current performance
        run: |
          git checkout ${{ github.sha }}
          /profile . --mode quick --output ./current.json

      - name: Compare performance
        run: |
          /profile --compare ./baseline.json ./current.json --fail-on-regression 10%

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-report
          path: ./profiling/
```

### Production Monitoring
```javascript
// Continuous profiling in production
const profiler = require('@performance-profiler/agent');

profiler.start({
  mode: 'continuous',
  sampling_rate: 10, // Low overhead sampling
  targets: ['cpu', 'memory'],
  upload_to: 'datadog', // or New Relic, etc.
  alert_on_regression: true
});
```

### Load Test Integration
```bash
# Run load test while profiling
/profile . --mode continuous --target all &
PROFILE_PID=$!

# Run your load test
artillery run load-test.yml

# Stop profiling
kill $PROFILE_PID

# Analyze results under load
/profile --analyze ./profiling/continuous-*.json
```

## Command Reference

| Command | Description |
|---------|-------------|
| `/profile [path]` | Quick profiling with default settings |
| `/profile [path] --mode quick` | 30-second scan |
| `/profile [path] --mode standard` | 5-minute analysis (default) |
| `/profile [path] --mode deep` | 30-minute deep dive |
| `/profile [path] --mode continuous` | Long-running monitoring |
| `/profile [path] --target cpu` | CPU profiling only |
| `/profile [path] --target memory` | Memory profiling only |
| `/profile [path] --target io` | I/O profiling only |
| `/profile [path] --target network` | Network profiling only |
| `/profile [path] --target all` | All dimensions |
| `/profile [path] --flame-graph` | Generate CPU flame graph |
| `/profile [path] --heap-snapshot` | Capture memory snapshot |
| `/profile [path] --detect-leaks` | Memory leak detection |
| `/profile [path] --database` | Database query profiling |
| `/profile [path] --optimize` | Generate optimizations |
| `/profile [path] --apply` | Apply recommended optimizations |
| `/profile [path] --benchmark` | Run benchmark suite |
| `/profile [path] --baseline` | Save as baseline for comparison |
| `/profile --compare A.json B.json` | Compare two profiling results |

## Configuration

Create `.performance-profiler.json` in project root:

```json
{
  "profiling": {
    "default_mode": "standard",
    "sampling_rate_hz": 99,
    "stack_depth": 128
  },
  "thresholds": {
    "cpu_hot_path_percent": 10,
    "memory_leak_growth_mb": 10,
    "slow_query_ms": 100,
    "slow_request_ms": 1000,
    "regression_tolerance_percent": 10
  },
  "optimization": {
    "auto_apply": false,
    "require_tests": true,
    "require_benchmark": true
  },
  "targets": {
    "cpu": {
      "enabled": true,
      "flame_graph": true
    },
    "memory": {
      "enabled": true,
      "leak_detection": true,
      "heap_snapshots": true
    },
    "io": {
      "enabled": true,
      "database_profiling": true
    },
    "network": {
      "enabled": true
    }
  },
  "output": {
    "directory": "./profiling",
    "formats": ["json", "html", "svg"]
  }
}
```

## Troubleshooting

### Problem: "Profiler cannot attach to process"
**Solution**: Run with elevated permissions or use user-space profiling

### Problem: "High profiling overhead"
**Solution**: Reduce sampling rate or use quick mode

### Problem: "No bottlenecks detected"
**Solution**: Increase profiling duration or run under load

### Problem: "Optimization breaks functionality"
**Solution**: Always run tests before and after applying optimizations

## Performance Tips

1. Profile production workloads
2. Use realistic data volumes
3. Measure under load
4. Focus on p95/p99 metrics
5. Optimize highest-impact bottlenecks first
6. Benchmark before and after
7. Monitor continuously
8. Set performance budgets
9. Automate regression detection
10. Profile regularly during development

## Support

- Full Documentation: See SKILL.md
- Process Details: See PROCESS.md
- Technical Implementation: See subagent-performance-profiler.md
- Issues: Report at project repository

## License

MIT - Part of Claude Code Skills Collection
