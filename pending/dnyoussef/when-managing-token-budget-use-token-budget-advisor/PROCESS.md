# Token Budget Advisor - Process Flow

## Overview

Step-by-step process for analyzing token budgets, estimating task complexity, generating chunking strategies, and creating execution plans.

## Process Phases

### Phase 1: Budget Assessment (5 min)

**Input:** Current context (token usage, limits)

**Actions:**
1. Retrieve current token usage
2. Calculate remaining budget
3. Apply safety buffer (15%)
4. Determine available tokens
5. Assess status (healthy/caution/warning/critical)
6. Load historical usage patterns

**Output:**
```json
{
  "limit": 200000,
  "used": 36000,
  "remaining": 164000,
  "buffer": 30000,
  "available": 134000,
  "status": "healthy",
  "usagePercent": "18.0%"
}
```

**Formula:**
```
remaining = limit - used
buffer = limit * 0.15
available = remaining - buffer

status:
  if used/limit > 0.90 → critical
  if used/limit > 0.75 → warning
  if used/limit > 0.50 → caution
  else → healthy
```

**Hook Integration:**
```bash
npx claude-flow@alpha hooks pre-task --description "Assessing token budget"
npx claude-flow@alpha memory retrieve --key "token-usage/current"
npx claude-flow@alpha memory store --key "budget/assessment" --value "{...}"
```

---

### Phase 2: Task Complexity Analysis (10 min)

**Input:** Task description

**Actions:**
1. Infer task type (feature, refactoring, debugging, etc.)
2. Assign base token estimate
3. Identify complexity multipliers
4. Calculate total estimate
5. Assess confidence level
6. Document factors

**Task Type Base Estimates:**
```javascript
{
  "simple-edit": 2000,
  "feature-implementation": 15000,
  "refactoring": 8000,
  "architecture-design": 12000,
  "full-stack-development": 40000,
  "debugging": 5000,
  "testing": 6000,
  "documentation": 4000,
  "integration": 10000,
  "migration": 20000
}
```

**Complexity Multipliers:**
```javascript
{
  "multiple-agents": 1.3,        // >3 agents
  "external-integration": 1.4,   // APIs, databases
  "testing-required": 1.25,      // TDD, coverage
  "documentation": 1.15,         // Docs needed
  "high-complexity": 1.5         // Complex/comprehensive
}
```

**Calculation:**
```
baseTokens = taskTypeEstimate
totalMultiplier = multiplier1 * multiplier2 * ...
totalEstimate = baseTokens * totalMultiplier

confidence:
  if multipliers >= 3 → high
  if multipliers >= 1 → medium
  else → low
```

**Output:**
```json
{
  "baseTokens": 15000,
  "multipliers": {
    "integration": 1.4,
    "testing": 1.25,
    "documentation": 1.15
  },
  "totalEstimate": 30188,
  "confidence": "high",
  "factors": [
    {"type": "base", "value": 15000, "reason": "Feature implementation"},
    {"type": "multiplier", "value": 1.4, "reason": "External integrations"},
    {"type": "multiplier", "value": 1.25, "reason": "Testing requirements"},
    {"type": "multiplier", "value": 1.15, "reason": "Documentation needed"}
  ]
}
```

---

### Phase 3: Chunking Strategy (15 min)

**Agent Task:** Planner
**Instructions:**
1. Check if task fits in budget (estimate <= 85% of available)
2. If yes: single chunk execution
3. If no: decompose into logical phases
4. Calculate chunk sizes
5. Define dependencies
6. Plan inter-chunk communication
7. Store strategy

**Chunking Decision:**
```javascript
if (totalEstimate <= available * 0.85) {
  // Single chunk - no chunking needed
  return singleChunkStrategy();
} else {
  // Multi-chunk - decompose
  return multiChunkStrategy();
}
```

**Phase Decomposition Template:**
```javascript
[
  {
    name: "Research & Planning",
    description: "Requirements, research, design",
    dependencies: [],
    priority: "high",
    outputs: ["requirements.md", "architecture.md"],
    estimatedTokens: baseEstimate * 0.20
  },
  {
    name: "Core Implementation",
    description: "Main functionality",
    dependencies: ["chunk-1"],
    priority: "high",
    outputs: ["src/**/*.js"],
    estimatedTokens: baseEstimate * 0.40
  },
  {
    name: "Testing & Validation",
    description: "Tests, validation, bug fixes",
    dependencies: ["chunk-2"],
    priority: "medium",
    outputs: ["tests/**/*.js", "coverage"],
    estimatedTokens: baseEstimate * 0.25
  },
  {
    name: "Documentation & Polish",
    description: "Docs, refinement, finalization",
    dependencies: ["chunk-3"],
    priority: "low",
    outputs: ["README.md", "docs/**"],
    estimatedTokens: baseEstimate * 0.15
  }
]
```

**Optimal Chunk Size:**
```
idealChunkSize = available * 0.40  // 40% of available
maxChunkSize = available * 0.60    // 60% absolute max
```

**Output:**
```json
{
  "chunks": [
    {
      "id": "chunk-1",
      "name": "Research & Planning",
      "description": "...",
      "estimatedTokens": 12000,
      "dependencies": [],
      "priority": "high",
      "outputs": ["requirements.md", "architecture.md"]
    },
    // ... more chunks
  ],
  "totalEstimate": 68000,
  "fitsInBudget": true,
  "recommendation": "Execute in 4 sequential chunks"
}
```

**Hook Integration:**
```bash
npx claude-flow@alpha memory store --key "budget/chunking-strategy" --value "{...}"
```

---

### Phase 4: Priority Optimization (10 min)

**Input:** Chunks + constraints

**Actions:**
1. Calculate priority score for each chunk
2. Sort by score (high to low)
3. Identify critical path
4. Flag quick wins
5. Mark deferrable work

**Priority Scoring:**
```javascript
score = 0

// Base priority
score += priorityWeights[chunk.priority]  // high:100, medium:50, low:25

// Dependency blocking (how many chunks depend on this one)
score += blockingCount * 20

// Critical path
if (isOnCriticalPath(chunk)) score += 30

// Quick wins (low cost, high value)
if (chunk.tokens < 5000 && chunk.value === "high") score += 25

// Risk mitigation (high-risk earlier)
if (chunk.risk === "high") score += 15
```

**Output:**
```json
{
  "prioritized": [
    {
      "id": "chunk-1",
      "name": "Research & Planning",
      "priorityScore": 150,
      "reasons": ["high-priority", "blocks 3 chunks", "critical-path"]
    },
    {
      "id": "chunk-2",
      "name": "Core Implementation",
      "priorityScore": 145,
      "reasons": ["high-priority", "blocks 2 chunks", "critical-path"]
    },
    // ... more chunks
  ]
}
```

---

### Phase 5: Execution Plan Generation (10 min)

**Input:** All analysis results

**Actions:**
1. Format comprehensive plan
2. Create budget tracking table
3. Define checkpoints
4. Document contingency strategies
5. Add rollback procedures
6. Store final plan

**Plan Structure:**
```markdown
## Token Budget Execution Plan

### Budget Status
[Current assessment]

### Task Analysis
[Complexity estimation]

### Chunking Strategy
[Chunks and dependencies]

### Execution Sequence
[Step-by-step for each chunk:]
- Estimated tokens
- Cumulative usage
- Dependencies
- Tasks
- Outputs
- Success criteria
- Checkpoint commands

### Budget Tracking
[Table: checkpoint, estimated, actual, remaining, status]

### Contingency Plans
[What to do if things go wrong]
```

**Checkpoint Template:**
```bash
# After each chunk
npx claude-flow@alpha memory store --key "project/chunk-X-complete" --value "{outputs}"
npx claude-flow@alpha hooks post-task --task-id "chunk-X" --tokens-used <actual>

# Check remaining budget
npx claude-flow@alpha memory retrieve --key "token-usage/current"

# Proceed or adjust
```

**Output:**
```markdown
[Full execution plan as shown in SKILL.md example]
```

**Hook Integration:**
```bash
npx claude-flow@alpha memory store --key "budget/execution-plan" --value "{...}"
npx claude-flow@alpha hooks post-task --task-id "budget-planning"
```

---

## Decision Tree

```
Start: Need to execute task
  |
  v
Assess current budget
  |
  v
Status?
  Critical (>90%) → Minimal scope only, warn user
  Warning (>75%)  → Conservative chunking
  Caution (>50%)  → Standard chunking
  Healthy (<50%)  → Flexible planning
  |
  v
Estimate task complexity
  |
  v
Task fits in available budget (85%)?
  Yes → Single chunk execution
  No  → Multi-chunk decomposition
  |
  v
If multi-chunk:
  Decompose into phases
  Calculate chunk sizes
  Define dependencies
  |
  v
Optimize priorities
  |
  v
Generate execution plan
  |
  v
Store plan in memory
  |
  v
Execute chunk 1
  |
  v
Checkpoint: Track actual usage
  |
  v
Actual within estimate (±20%)?
  Yes → Continue to next chunk
  No  → Adjust remaining chunks
  |
  v
Repeat until complete
  |
  v
Final checkpoint
  |
  v
End: Update historical patterns
```

## Integration Points

### Pre-Task Hook
```bash
npx claude-flow@alpha hooks pre-task \
  --description "Planning token budget for [task]" \
  --complexity "medium"
```

### Memory Storage
```bash
# Budget assessment
npx claude-flow@alpha memory store \
  --key "budget/assessment" \
  --value "{limit, used, available, status}"

# Complexity estimation
npx claude-flow@alpha memory store \
  --key "budget/complexity" \
  --value "{baseTokens, multipliers, totalEstimate}"

# Chunking strategy
npx claude-flow@alpha memory store \
  --key "budget/chunking-strategy" \
  --value "{chunks, dependencies}"

# Execution plan
npx claude-flow@alpha memory store \
  --key "budget/execution-plan" \
  --value "{full-plan-markdown}"
```

### Checkpoint Hooks
```bash
# After each chunk
npx claude-flow@alpha hooks post-task \
  --task-id "chunk-X" \
  --tokens-used <actual> \
  --tokens-estimated <estimated>
```

### Post-Task Hook
```bash
npx claude-flow@alpha hooks post-task \
  --task-id "[task-id]" \
  --success true \
  --total-tokens <actual> \
  --estimated-tokens <estimated> \
  --accuracy-percent <percentage>
```

## Success Criteria

- Budget assessment: Accurate current usage
- Complexity estimation: ±20% of actual
- Chunking: All chunks fit in budget
- Prioritization: Critical path identified
- Execution plan: Clear, actionable, checkpointed
- Tracking: Real-time budget monitoring
- Contingency: Rollback strategies defined

## Common Patterns

### Pattern 1: Large Project
- Estimate: 100K tokens
- Available: 150K tokens
- Strategy: 4-5 chunks, 20-25K each
- Result: Safe execution with buffer

### Pattern 2: Budget Tight
- Estimate: 80K tokens
- Available: 90K tokens
- Strategy: Conservative chunking, defer low-priority
- Result: Core functionality delivered

### Pattern 3: Budget Critical
- Estimate: 50K tokens
- Available: 20K tokens
- Strategy: Scope reduction, phase 1 only
- Result: Minimal viable implementation

## Accuracy Improvement

Track estimation accuracy:
```javascript
{
  "task": "feature-implementation",
  "estimated": 15000,
  "actual": 17200,
  "accuracy": 87.2,
  "factors": ["underestimated testing"],
  "adjustment": "increase testing multiplier from 1.25 to 1.35"
}
```

Store patterns for future improvement.

## Related Processes

- Prompt Optimization (reduce per-chunk cost)
- Skill Gap Analysis (identify resource-heavy operations)
- Task Orchestration (coordinate multi-agent execution)
