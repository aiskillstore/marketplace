# Agent Pipeline Chaining - Detailed Workflow

## Complete Pipeline Script

```bash
#!/bin/bash
# pipeline-workflow.sh

# Phase 1: Design Pipeline
npx claude-flow@alpha pipeline design \
  --stages "research,analyze,code,test,review" \
  --flow sequential \
  --output pipeline-design.json

# Phase 2: Connect Agents
npx claude-flow@alpha pipeline init --design pipeline-design.json
npx claude-flow@alpha agent spawn --type researcher --pipeline-stage 1
npx claude-flow@alpha agent spawn --type analyst --pipeline-stage 2
npx claude-flow@alpha agent spawn --type coder --pipeline-stage 3
npx claude-flow@alpha agent spawn --type tester --pipeline-stage 4
npx claude-flow@alpha agent spawn --type reviewer --pipeline-stage 5

# Connect stages
npx claude-flow@alpha pipeline connect --from-stage 1 --to-stage 2
npx claude-flow@alpha pipeline connect --from-stage 2 --to-stage 3
npx claude-flow@alpha pipeline connect --from-stage 3 --to-stage 4
npx claude-flow@alpha pipeline connect --from-stage 4 --to-stage 5

# Phase 3: Execute Pipeline
npx claude-flow@alpha pipeline execute \
  --design pipeline-design.json \
  --input initial-data.json \
  --strategy sequential

# Phase 4: Monitor Streaming
npx claude-flow@alpha stream monitor --all-channels --interval 2 &

# Phase 5: Validate Results
npx claude-flow@alpha pipeline results --output results.json
npx claude-flow@alpha pipeline validate --results results.json

echo "Pipeline execution complete"
```

## Success Criteria
- [ ] Pipeline stages defined
- [ ] Agents connected properly
- [ ] Data flow functional
- [ ] Results validated
