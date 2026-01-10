# Performance Analysis - Quick Start

Comprehensive performance analysis and optimization for Claude Flow swarms.

## Quick Start

```bash
# 1. Establish baseline
npx claude-flow@alpha performance baseline --duration 300 --output baseline.json

# 2. Profile system
npx claude-flow@alpha performance profile-swarm --duration 300 --output profile.json

# 3. Analyze issues
npx claude-flow@alpha performance analyze --detect-bottlenecks --output analysis.json

# 4. Optimize
npx claude-flow@alpha performance optimize --recommendations recommendations.json

# 5. Validate
npx claude-flow@alpha performance compare --baseline baseline.json --current optimized.json
```

## Agents
- **performance-analyzer:** Performance analysis
- **performance-benchmarker:** Benchmarking
- **perf-analyzer:** Deep profiling

## Success Metrics
- Throughput improvement: ≥15%
- Latency reduction: ≥20%
- Error rate: <1%
