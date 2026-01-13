# Parallel Planning Cookbook

> Fan-out planning tasks to multiple providers, consolidate into optimal roadmap

## Overview

This cookbook shows how to get multiple planning perspectives on the same
feature/project, then synthesize the best elements into a single roadmap.

## When to Use

- Complex features with multiple valid approaches
- Strategic decisions with trade-offs
- High-stakes implementations (auth, payments, core infrastructure)
- When you want diverse perspectives

## Basic Pattern

### Step 1: Define Planning Variants

Create different strategic biases for each planner:

```markdown
## Planner Variants

| Planner | Strategy | Bias |
|---------|----------|------|
| conservative | Low risk, proven patterns | Stability, testing |
| aggressive | Fast-track, modern patterns | Speed, innovation |
| security | Security-first design | Defense, compliance |
| scalability | Future-proof architecture | Growth, performance |
```

### Step 2: Spawn Planners (MAP)

In a SINGLE message, launch all planners:

```markdown
Task(subagent_type="Plan", prompt="""
  Create implementation plan for: ${FEATURE}

  Strategic bias: CONSERVATIVE
  - Prefer proven patterns over novel approaches
  - Include extensive testing at each phase
  - Minimize breaking changes
  - Use incremental rollout

  Write to: specs/plans/planner-conservative.md

  Include:
  - Executive summary
  - Phases with tasks and dependencies
  - Risk assessment
  - Timeline estimates
  - Exit criteria per phase
""", run_in_background=true)

Task(subagent_type="Plan", prompt="""
  Create implementation plan for: ${FEATURE}

  Strategic bias: AGGRESSIVE
  - Optimize for delivery speed
  - Use modern patterns and tools
  - Accept calculated risks
  - Parallelize aggressively

  Write to: specs/plans/planner-aggressive.md

  Include:
  - Executive summary
  - Phases with tasks and dependencies
  - Risk assessment (with acceptable risks noted)
  - Timeline estimates
  - Exit criteria per phase
""", run_in_background=true)
```

### Step 3: Include External Providers (Optional)

For truly diverse perspectives, include non-Claude providers:

```bash
# Codex (OpenAI)
codex -m gpt-5.1-codex -a full-auto "$(cat <<'EOF'
Create implementation plan for: ${FEATURE}

Strategic bias: ENGINEERING EXCELLENCE
- Focus on code quality and maintainability
- Prioritize type safety and testing
- Design for extensibility

Write comprehensive markdown plan.
EOF
)" > specs/plans/planner-codex.md

# Gemini (Google)
gemini -m gemini-3-pro "$(cat <<'EOF'
Create implementation plan for: ${FEATURE}

Strategic bias: SCALABILITY
- Design for 10x growth
- Consider distributed systems patterns
- Plan for observability

Write comprehensive markdown plan.
EOF
)" > specs/plans/planner-gemini.md
```

### Step 4: Collect Results (COLLECT)

Wait for all planners with timeout:

```markdown
# Wait for Claude subagents
TaskOutput(task_id=conservative-id, block=true, timeout=180000)
TaskOutput(task_id=aggressive-id, block=true, timeout=180000)

# Verify CLI outputs exist
Read("specs/plans/planner-codex.md")
Read("specs/plans/planner-gemini.md")

# Check for any missing outputs
Glob("specs/plans/planner-*.md")
```

### Step 5: Consolidate (REDUCE)

Launch the plan reducer:

```markdown
Task(subagent_type="ai-dev-kit:orchestration:plan-reducer", prompt="""
  Consolidate these planning proposals:

  Input directory: specs/plans/
  Pattern: planner-*.md

  Output: specs/ROADMAP.md

  Consolidation preferences:
  - For core functionality: Favor conservative approach
  - For non-critical features: Allow aggressive optimizations
  - For security-related: Always use security-first approach
  - Timeline: Use weighted average (conservative weight: 1.5)

  Required sections in output:
  - Executive Summary
  - Attribution Table (which planner contributed what)
  - Conflict Resolution Notes
  - Consolidated Phases
  - Risk Matrix
  - Timeline

  Read the scoring rubric at:
  plugins/ai-dev-kit/skills/mapreduce/reference/scoring-rubrics.md
""")
```

## Advanced Patterns

### Pattern A: Domain-Specific Planners

For complex domains, use specialized expertise:

```markdown
# Backend planner
Task(prompt="Plan backend: API, database, caching...")

# Frontend planner
Task(prompt="Plan frontend: components, state, UX...")

# DevOps planner
Task(prompt="Plan infrastructure: CI/CD, monitoring, deployment...")

# Security planner
Task(prompt="Plan security: auth, encryption, compliance...")
```

Then reduce with domain-aware synthesis.

### Pattern B: Iterative Refinement

First round: High-level plans
Second round: Detailed plans on chosen approach

```markdown
# Round 1: Strategic options
Spawn planners with different strategies
Reduce to strategic direction

# Round 2: Detailed planning
Spawn planners to detail the chosen strategy
Different planners focus on different phases
Reduce to final ROADMAP.md
```

### Pattern C: Stakeholder Perspectives

Plan from different stakeholder viewpoints:

```markdown
# Engineering perspective
Task(prompt="Plan optimizing for: engineering velocity, code quality")

# Product perspective
Task(prompt="Plan optimizing for: user experience, feature completeness")

# Business perspective
Task(prompt="Plan optimizing for: time-to-market, ROI")
```

## Output Example

```markdown
# Consolidated Implementation Plan: User Authentication

## Executive Summary

This plan synthesizes 4 planning perspectives (conservative, aggressive,
security-focused, and scalability-focused) into an optimal implementation
roadmap for user authentication.

Key decisions:
- OAuth2/OIDC foundation (security + scalability)
- Incremental rollout (conservative)
- Modern session handling (aggressive)
- Comprehensive audit logging (security)

## Attribution

| Section | Primary | Contributing | Confidence |
|---------|---------|--------------|------------|
| Auth Protocol | security | scalability | HIGH |
| Session Mgmt | aggressive | conservative | MEDIUM |
| Migration | conservative | - | HIGH |
| Testing | conservative | security | HIGH |

## Conflicts Resolved

### Session Storage: JWT vs Server-Side

| Approach | Advocate | Pros | Cons |
|----------|----------|------|------|
| JWT | aggressive | Stateless, scalable | Token size, revocation |
| Server-side | conservative | Simple revocation | State management |
| Hybrid | security | Best of both | Complexity |

**Resolution**: Hybrid approach
**Rationale**: Security requirements mandate revocation capability;
scale requirements need efficient validation.

## Phase 1: Foundation (Weeks 1-2)

### Tasks
1. Set up OAuth2 provider (from security plan)
2. Implement token service (from aggressive plan)
3. Database migration for auth tables (from conservative plan)

...
```

## Error Handling

### Planner Timeout

```markdown
If planner times out:
  - Proceed with available plans
  - Note missing perspective in attribution
  - Reduce confidence for sections that would have benefited
  - Consider re-running just that planner later
```

### Conflicting Plans

```markdown
If plans fundamentally disagree:
  - Document both approaches
  - Use priority criteria: Feasibility > Risk > Completeness
  - Note the conflict and resolution in output
  - Consider asking user for preference before reducing
```

## Tips

1. **More planners != better**: 3-4 diverse perspectives is optimal
2. **Bias clearly**: Explicit strategic bias produces more diverse outputs
3. **Timeout generously**: Planning is complex, allow 2-3 minutes
4. **Preserve artifacts**: Keep intermediate plans for auditing
5. **Iterate**: First round can be rough; refine with focused second round
