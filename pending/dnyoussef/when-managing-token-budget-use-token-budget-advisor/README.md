# Token Budget Advisor

Proactive token budget management tool for assessing usage, estimating task complexity, and creating execution plans that stay within budget limits.

## Overview

This skill helps you:
- Assess current token usage and remaining budget
- Estimate task complexity and token requirements
- Generate intelligent chunking strategies
- Prioritize work by value and cost
- Create step-by-step execution plans with checkpoints

## Quick Start

```bash
# Activate skill
Use skill: when-managing-token-budget-use-token-budget-advisor

# Analyze task and budget
"I need to build [task description]. Current token usage is [X]. Help me plan execution within budget."
```

## Key Features

### 1. Budget Assessment
- Current usage vs. limits (with 15% safety buffer)
- Historical pattern analysis
- Projected usage for pending tasks
- Status indicators (healthy/caution/warning/critical)

### 2. Task Complexity Analysis
- Token estimation by task type (2K-40K base)
- Multiplier application (agents, integrations, testing)
- Confidence scoring (low/medium/high)
- Factor breakdown

### 3. Intelligent Chunking
- Logical phase decomposition
- Dependency analysis
- Optimal chunk sizing (40% of available per chunk)
- Inter-chunk communication planning
- State management between chunks

### 4. Priority Optimization
- Critical path identification
- Value vs. cost analysis
- Quick wins detection
- Risk-based prioritization

### 5. Execution Planning
- Step-by-step task sequence
- Budget tracking per checkpoint
- Rollback strategies
- Progress monitoring
- Contingency plans

## Example Results

**Input:**
- Task: Build full-stack e-commerce app
- Budget: 200K tokens, 36K used (164K remaining)

**Analysis:**
- Estimated complexity: 68K tokens
- Status: ✅ Healthy (18% used)
- Available: 134K tokens (after buffer)

**Plan:**
- 4 sequential chunks
- Max chunk: 20K tokens (15% of available)
- Total estimate: 68K (51% of available)
- Recommendation: Execute with confidence

**Chunks:**
1. Research & Planning (12K tokens)
2. Core Implementation (20K tokens)
3. Testing & Validation (18K tokens)
4. Documentation & Polish (18K tokens)

**Safety margin:** 66K tokens remaining after completion

## When to Use

- Before starting large/complex tasks (>20K estimate)
- When approaching budget limits (>75% used)
- During multi-phase project planning
- When tasks previously failed due to token exhaustion
- For optimizing multi-agent coordination

## Output Format

```markdown
## Token Budget Execution Plan

### Budget Status
- Available: [tokens]
- Status: [healthy/caution/warning/critical]

### Task Analysis
- Estimated: [tokens]
- Confidence: [low/medium/high]

### Chunking Strategy
- Chunks: [count]
- Fits in budget: [yes/no]

### Execution Sequence
[Step-by-step plan with checkpoints]

### Budget Tracking
[Table with estimated vs actual]

### Contingency Plans
[What to do if estimates are wrong]
```

## Integration

Works seamlessly with:
- `when-optimizing-prompts-use-prompt-optimization-analyzer` (reduce token waste)
- `when-analyzing-skill-gaps-use-skill-gap-analyzer` (portfolio-level planning)
- `task-orchestrator` (multi-agent execution)

## Configuration

**Token Limits:**
- Default: 200,000 tokens
- Safety buffer: 15% (30,000 tokens)
- Max chunk size: 40% of available

**Estimation Confidence:**
- High: 3+ complexity factors identified
- Medium: 1-2 factors
- Low: Generic estimate

## Success Criteria

- Budget adherence: 95%+ accuracy
- Planning precision: ±20% estimation error
- Zero overruns: No token exhaustion failures
- Optimal chunking: 40-60% utilization per chunk
- Efficient execution: <15% unused budget

## Contingency Strategies

**If chunk exceeds estimate:**
1. Stop at natural breakpoint
2. Store progress in memory
3. Re-assess remaining budget
4. Adjust subsequent chunks

**If approaching limit:**
1. Prioritize critical chunks
2. Defer low-priority work
3. Reduce scope if necessary

## Support

- Version: 1.0.0
- Complexity: MEDIUM
- Agents: planner, code-analyzer
- Hooks: Yes (pre-task, post-task, checkpoints)
