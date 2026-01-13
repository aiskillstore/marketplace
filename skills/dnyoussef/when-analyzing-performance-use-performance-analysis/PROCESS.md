# Performance Analysis - Workflow

## Complete Script

```bash
#!/bin/bash

# Phase 1: Establish Baseline
npx claude-flow@alpha performance baseline --duration 300 --output baseline.json
npx claude-flow@alpha benchmark run --type swarm --iterations 10 --output benchmark.json

# Phase 2: Profile System
npx claude-flow@alpha performance profile-swarm --duration 300 --output profile.json
npx claude-flow@alpha memory profile --show-hotspots --output memory-profile.json
npx claude-flow@alpha performance flamegraph --input profile.json --output flamegraph.svg

# Phase 3: Analyze Issues
npx claude-flow@alpha performance analyze --detect-bottlenecks --output analysis.json
npx claude-flow@alpha performance bottlenecks --categorize --output bottlenecks.json
npx claude-flow@alpha performance root-cause --issue "high-latency" --output root-cause.json

# Phase 4: Optimize Performance
npx claude-flow@alpha performance recommend --based-on analysis.json --output recommendations.json
npx claude-flow@alpha performance optimize --recommendations recommendations.json --auto-apply
npx claude-flow@alpha swarm optimize-topology --based-on analysis.json
npx claude-flow@alpha agent rebalance --strategy performance-optimized

# Phase 5: Validate Results
npx claude-flow@alpha performance baseline --duration 300 --output optimized.json
npx claude-flow@alpha performance compare --baseline baseline.json --current optimized.json --output improvements.json
npx claude-flow@alpha performance report --type comprehensive --output final-report.md

# Display results
cat improvements.json | jq '.improvements'
```

## Success Criteria
- [ ] Baseline established
- [ ] System profiled
- [ ] Bottlenecks identified
- [ ] Optimizations applied
- [ ] ≥15% throughput improvement
- [ ] ≥20% latency reduction
