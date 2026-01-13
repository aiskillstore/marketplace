# Swarm Orchestration - Detailed Workflow

## Complete Execution Script

```bash
#!/bin/bash
# swarm-orchestration-workflow.sh

set -e

echo "=== Phase 1: Plan Orchestration ==="
# Decompose complex task
npx claude-flow@alpha task decompose \
  --task "Build full-stack application" \
  --max-depth 3 \
  --output decomposition.json

# Generate execution plan
npx claude-flow@alpha task plan \
  --decomposition decomposition.json \
  --available-agents 12 \
  --output execution-plan.json

echo "=== Phase 2: Initialize Swarm ==="
# Initialize with optimal topology
npx claude-flow@alpha swarm init --topology hierarchical --max-agents 15

# Spawn coordinators
npx claude-flow@alpha agent spawn --type coordinator --role "task-orchestrator"
npx claude-flow@alpha agent spawn --type coordinator --role "hierarchical-coordinator"
npx claude-flow@alpha agent spawn --type coordinator --role "adaptive-coordinator"

echo "=== Phase 3: Orchestrate Execution ==="
# Spawn specialized agents
npx claude-flow@alpha agent spawn --type researcher --count 2
npx claude-flow@alpha agent spawn --type coder --count 5
npx claude-flow@alpha agent spawn --type reviewer --count 2
npx claude-flow@alpha agent spawn --type tester --count 2

# Execute orchestration
npx claude-flow@alpha task orchestrate \
  --plan execution-plan.json \
  --strategy adaptive \
  --max-agents 12

echo "=== Phase 4: Monitor Progress ==="
# Monitor execution
npx claude-flow@alpha swarm monitor --interval 10 --duration 3600 &
MONITOR_PID=$!

# Wait for completion
while true; do
  COMPLETED=$(npx claude-flow@alpha task list --filter "completed" | wc -l)
  TOTAL=$(npx claude-flow@alpha task list | wc -l)
  if [ "$COMPLETED" -eq "$TOTAL" ]; then
    break
  fi
  sleep 30
done

kill $MONITOR_PID

echo "=== Phase 5: Synthesize Results ==="
# Collect and synthesize results
npx claude-flow@alpha task results --all --format json > all-results.json
npx claude-flow@alpha task synthesize \
  --input all-results.json \
  --output synthesized-results.json

# Generate final report
npx claude-flow@alpha orchestration report \
  --type final \
  --output final-report.md

echo "=== Orchestration Complete ==="
cat final-report.md
```

## Phase Details

### Phase 1: Plan Orchestration (15-20 min)
- Analyze task complexity
- Create decomposition tree
- Map dependencies
- Plan agent assignments

### Phase 2: Initialize Swarm (10-15 min)
- Select optimal topology
- Initialize swarm infrastructure
- Spawn coordinator agents
- Establish memory coordination

### Phase 3: Orchestrate Execution (30-60 min)
- Spawn specialized agents
- Assign tasks based on dependencies
- Execute distributed workload
- Handle errors and retries

### Phase 4: Monitor Progress (Continuous)
- Track task completion
- Identify blockers
- Monitor agent health
- Generate progress reports

### Phase 5: Synthesize Results (10-15 min)
- Collect all task results
- Aggregate by category
- Validate outputs
- Generate final report

## Success Criteria

- [ ] All tasks decomposed correctly
- [ ] ≥95% task completion rate
- [ ] Agent utilization 70-90%
- [ ] Results synthesized successfully
- [ ] Final report generated
