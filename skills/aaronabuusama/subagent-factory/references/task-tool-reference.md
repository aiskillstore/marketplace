# Task Tool Reference - Agent Invocation and Execution

Complete reference for using the Task tool to invoke agents, including parameters, execution patterns, and best practices.

## Overview

The Task tool is Claude Code's primary delegation mechanism. It spawns specialized sub-agents with:
- Independent context windows
- Configurable tool access
- Specialized system prompts
- Separate execution threads

**Key insight**: A "subagent" is a lightweight Claude Code instance running within a Task.

## Built-in Agent Types

Claude Code provides three built-in agent types:

### 1. general-purpose

**Model**: Sonnet
**Tools**: All tools (inherits from main agent)
**Purpose**: Complex multi-step tasks requiring exploration and modification

**Use when**:
- Searching without specific target
- Tasks require both reading AND modifying files
- Multi-step research with code changes

**Example invocation**:
```
Use a general-purpose agent to refactor the authentication module.
```

### 2. explore

**Model**: Haiku (fast, low-latency)
**Tools**: Read, Glob, Grep, Bash (read-only)
**Purpose**: Fast codebase searching and analysis
**Mode**: Strictly read-only

**Use when**:
- Quick file searches
- Pattern matching across large codebases
- Speed matters more than modification capability

**Example invocation**:
```
Use explore agents to search for all API endpoint definitions across the codebase.
```

### 3. plan

**Model**: Sonnet
**Tools**: Read, Glob, Grep, Bash
**Purpose**: Research and analysis during planning phase
**Behavior**: Auto-invoked when Claude enters plan mode

**Use case**: Gathering information before execution phase

## Custom Agents

Custom agents are defined in `.claude/agents/*.md` files and invoked by name.

**Example invocation**:
```
Use the security-auditor agent to scan the authentication module for vulnerabilities.
```

**Agent discovery**: Claude automatically discovers agents from:
1. Project agents: `.claude/agents/`
2. User agents: `~/.claude/agents/`

## Task Tool Parameters

### Core Parameters

#### subagent_type (Required)

**Type**: String
**Purpose**: Specifies which agent type to invoke

**Values**:
- `"general-purpose"` - Full-featured agent
- `"explore"` - Fast read-only search agent
- Custom agent name (e.g., `"code-reviewer"`, `"test-runner"`)

**Example**:
```javascript
Task({
  subagent_type: "general-purpose",
  prompt: "Analyze the database schema"
})
```

#### prompt (Required)

**Type**: String
**Purpose**: Instruction/task description for the subagent

**Guidelines**:
- Be specific and action-oriented
- Include context the subagent needs
- Define success criteria
- Specify output format if relevant

**Example**:
```javascript
Task({
  subagent_type: "code-reviewer",
  prompt: "Review the authentication changes in PR #123. Focus on security vulnerabilities, particularly around JWT handling and session management. Provide a markdown report with findings categorized by severity."
})
```

**Good prompt structure**:
1. **Context**: "We just merged PR #456 which refactored payment processing"
2. **Goal**: "Review changes for race conditions and concurrency bugs"
3. **Constraints**: "Focus on PaymentProcessor and TransactionManager classes"
4. **Output**: "Provide markdown report with severity levels and code snippets"

#### description (Optional)

**Type**: String
**Purpose**: Natural language description of when agent should be used (enables automatic delegation)

**Best practices**:
- Use action-oriented phrases
- Include trigger conditions
- Explain expected outcomes

**Example**:
```yaml
description: "Expert security reviewer. Use PROACTIVELY after any authentication or authorization code changes. Analyzes for vulnerabilities and compliance."
```

#### model (Optional)

**Type**: String
**Purpose**: Specify which Claude model to use

**Values**:
- `"sonnet"` - Default, balanced performance
- `"opus"` - Most capable, higher cost
- `"haiku"` - Fast, lower cost
- `"inherit"` - Use same model as parent agent

**Default**: Inherits from main agent if not specified

**Example**:
```javascript
Task({
  subagent_type: "security-analyzer",
  model: "opus",  // Use highest capability for security analysis
  prompt: "Comprehensive security audit of authentication system"
})
```

#### tools (Optional)

**Type**: Array of strings
**Purpose**: Override tool access for this specific invocation

**Note**: This parameter is available in agent definitions but not directly in Task tool calls. Tool scoping is defined in the agent's YAML frontmatter.

#### run_in_background (Proposed)

**Status**: Feature request pending (Issue #9905)
**Type**: Boolean
**Purpose**: Enable async subagent execution

**Proposed API**:
```javascript
Task({
  subagent_type: "security-analyzer",
  prompt: "Comprehensive security audit",
  run_in_background: true  // Would enable non-blocking execution
})
```

**Current limitation**: Task tool executes synchronously, blocking until completion.

**Workaround**: Use parallel execution (up to 10 concurrent tasks)

#### resume (Supported)

**Purpose**: Resume a previous subagent conversation

**Usage**:
```
Resume agent abc123 and now analyze the authorization logic as well.
```

**Behavior**:
- Maintains full context from previous execution
- Agent can reference prior work
- Useful for iterative refinement

**Use cases**:
- Build upon previous analysis
- Extend scope incrementally
- Refine outputs iteratively

## Execution Patterns

### Parallel Execution (Recommended)

**Mechanism**: Automatic concurrency management with dynamic queuing

**Characteristics**:
- Maximum 10 concurrent tasks
- New tasks launch immediately when slots free up
- No batch boundaries or artificial delays
- Optimal throughput (3-5x faster than sequential)

**Example prompt**:
```
Analyze this codebase using multiple explore agents. Have each agent examine
a different module: auth, api, database, frontend, utils, tests.
```

**What happens**:
- Claude spawns multiple tasks (up to 10 concurrent)
- As each completes, next task launches automatically
- Results aggregated in main agent context

**When to use**:
- Independent subtasks (no shared state)
- Reading operations dominate
- Large-scale analysis (100+ files)
- Context isolation matters

**Token cost**: 10 agents × 20k tokens = 200k tokens overhead

### Sequential Execution (Chained)

**Mechanism**: Explicit orchestration where outputs feed into subsequent tasks

**Example prompt**:
```
First use the code-analyzer subagent to identify performance bottlenecks,
then use the optimizer subagent to fix the top 3 issues it found,
finally use the test-runner subagent to verify the optimizations.
```

**What happens**:
- Tasks execute one at a time
- Each task receives output from previous
- Main agent coordinates handoffs

**When to use**:
- Tasks have dependencies (output → input)
- Stateful operations (database migrations)
- Progressive refinement workflows
- Quality gates (analyze → fix → verify)

**Token cost**: 3 agents × 20k tokens = 60k tokens overhead

### Parallel Batches (Anti-Pattern)

**Problem**: Specifying explicit parallelism levels

**Bad example**:
```
Use 4 parallel explore agents to search the codebase
```

**What happens**:
- Launches 4 agents
- WAITS for ALL 4 to complete (even if 3 finish quickly)
- Then launches next batch of 4
- Introduces unnecessary delays

**Why inefficient**:
- Slowest task in batch blocks next batch
- Resources sit idle while waiting
- Lower overall throughput

**Alternative**: Omit parallelism specification, let Claude Code optimize

### Hybrid Pattern (Advanced)

**Mechanism**: Combine parallel and sequential for complex workflows

**Example**:
```
Phase 1 (Parallel): Spawn 5 explore agents to analyze different modules
[Wait for completion, aggregate results]

Phase 2 (Sequential): Use code-implementer to fix top 5 issues one at a time
[Each fix depends on previous completing]

Phase 3 (Parallel): Spawn 3 test-runner agents to verify fixes in parallel
```

**When to use**:
- Multi-phase projects
- Some phases parallelizable, others sequential
- Quality gates between phases

## Token Cost Management

### Base Cost
**Each Task starts with ~20k token overhead**

**Cost examples**:
- 1 subagent: 20k tokens
- 10 parallel subagents: 200k tokens
- 100 queued tasks: 2M tokens

### Cost Optimization Strategies

#### 1. Group Related Work
```
# Expensive: 3 agents, 60k tokens
Agent 1: Analyze auth/login.go
Agent 2: Analyze auth/signup.go
Agent 3: Analyze auth/session.go

# Cheaper: 1 agent, 20k tokens
Agent 1: Analyze entire auth/ directory
```

#### 2. Use Explore Agents for Searches
```
# Haiku model = lower cost
Use explore agents to find all API endpoint definitions
```

#### 3. Summary Protocol
```markdown
After analysis, provide concise summary (max 500 words) to reduce
main agent context consumption.
```

#### 4. Reuse Agents
```
# Resume instead of spawning new
Resume agent abc123 and also analyze the database module
```

#### 5. Selective Parallelization
```
# Balance token cost vs time savings
- Quick tasks (< 30s): Sequential
- Long tasks (> 2 min): Parallel
```

### Breakeven Analysis

**Parallel execution worth it when**:
- Task duration > 2 minutes (time savings offset token costs)
- Tasks are truly independent
- Need context isolation for large codebase

**Sequential better when**:
- Quick tasks (< 30 seconds)
- Small context requirements
- Dependencies between tasks

## Context Management

### Context Window Benefits

**Problem**: Large tasks exhaust single agent context

**Solution**: Each subagent has independent context window

**Capacity example**:
- Main agent: 200k tokens
- 10 parallel subagents: 10 × 200k = 2M tokens effective capacity
- Context isolation prevents cross-contamination

### Context Isolation Patterns

#### Domain Separation
```
Agent 1: Analyze frontend code
Agent 2: Analyze backend code
Agent 3: Analyze database schema
Agent 4: Analyze DevOps configs
```

**Benefit**: No frontend details pollute backend analysis

#### Phase Separation
```
Phase 1 Agent: Gather requirements
Phase 2 Agent: Design solution
Phase 3 Agent: Implement solution
Phase 4 Agent: Write tests
Phase 5 Agent: Generate documentation
```

**Benefit**: Each phase starts fresh, focuses only on its role

#### Scale-Out Analysis
```
100 files to analyze:
- Spawn 10 agents
- Each analyzes 10 files
- Each maintains full context for its subset
- Main agent aggregates findings
```

**Benefit**: Deep analysis without context exhaustion

### Summary Protocol

**Best practice**: Have subagents provide summaries to main agent

**Example prompt inclusion**:
```markdown
After completing your analysis, provide a concise summary (max 500 words) with:
1. Key findings (bullet points)
2. Critical issues requiring immediate attention
3. Recommendations prioritized by impact
4. Files examined (list)

This summary will be provided to the orchestrator agent.
```

**Why it matters**:
- Main agent doesn't need full subagent context
- Preserves main agent's context budget
- Enables coordination across many subagents

## Best Practices

### 1. Write Detailed Prompts

**Minimal prompt (not recommended)**:
```
Review this code for quality issues.
```

**Detailed prompt (recommended)**:
```
Review the authentication changes in src/auth/ for:
1. Security vulnerabilities (SQL injection, XSS, auth bypasses)
2. Performance issues (N+1 queries, missing indexes)
3. Code quality (complexity, duplication, error handling)

Focus on files modified in the last commit.

Provide findings as markdown with:
- Executive summary
- Issues categorized by severity (Critical/High/Medium/Low)
- Code snippets showing problems
- Recommended fixes with rationale
```

### 2. Leverage Built-in Types

**Use explore for fast searches**:
```
Use explore agents to find all database connection initialization code.
```

**Use general-purpose for complex work**:
```
Use a general-purpose agent to refactor the payment processing pipeline.
```

### 3. Balance Parallelization

**Don't over-parallelize**:
```
# Overkill: 50 agents for simple task
Use 50 explore agents to find all TODO comments

# Appropriate: 5-10 agents for complex analysis
Use multiple explore agents to analyze different architectural layers
```

### 4. Specify Output Format

```
Provide results as JSON with this schema:
{
  "summary": "brief overview",
  "findings": [
    {
      "file": "path/to/file",
      "line": 123,
      "severity": "high",
      "issue": "description",
      "fix": "recommended solution"
    }
  ],
  "metrics": {
    "files_analyzed": 0,
    "issues_found": 0
  }
}
```

### 5. Set Success Criteria

```
Success criteria:
- All modified files analyzed
- No critical severity issues remaining
- All recommendations include code examples
- Report completed in markdown format
```

### 6. Provide Context

```
Context:
- We're preparing for security audit
- Authentication system recently refactored
- Known issue: session handling needs review
- Compliance requirement: OWASP Top 10

Your task: [...]
```

## Invocation Examples

### Example 1: Simple Invocation

```
Use the test-runner agent to execute the test suite and diagnose any failures.
```

### Example 2: Multiple Parallel Agents

```
Analyze this codebase for performance issues using multiple explore agents.
Have each agent focus on a different area:
- Agent 1: API endpoints and route handlers
- Agent 2: Database queries and ORM usage
- Agent 3: Frontend rendering and state management
- Agent 4: Background jobs and async tasks

Look for N+1 queries, missing indexes, blocking operations, and missing caching.
```

### Example 3: Sequential Pipeline

```
Execute this security review pipeline:

1. Use security-auditor agent to scan authentication module for vulnerabilities
2. Use code-implementer agent to fix top 3 critical issues from audit
3. Use security-validator agent to verify fixes address vulnerabilities

Provide complete pipeline results with before/after comparison.
```

### Example 4: Agent with Specific Model

```
Use the tech-researcher agent with opus model to conduct comprehensive
analysis of database migration strategies. Compare Flyway, Liquibase, and
golang-migrate for our Go codebase. Provide detailed comparison matrix
with recommendations.
```

### Example 5: Resume Agent

```
Resume security-auditor agent abc123 and extend the analysis to include
the authorization logic in src/authz/. Apply the same security checklist.
```

## Limitations and Considerations

### Current Limitations

1. **No native background execution** - Tasks run synchronously (feature request pending)
2. **Parallelism capped at 10** - Hard limit on concurrent tasks
3. **~20k token overhead per agent** - Impacts cost at scale
4. **No built-in agent communication** - Main agent must orchestrate
5. **Limited resume functionality** - Only within session
6. **No result streaming** - Agent completes entirely before returning

### When NOT to Use Agents

**Use single-agent approach when**:
- Task is simple and quick (< 30 seconds)
- No context isolation needed
- Token budget is constrained
- Task requires shared state across steps

**Use code/tools directly when**:
- Deterministic operation (formatting, validation)
- Simple file operations
- Single command execution
- No analysis or reasoning needed

## Quick Reference

### Agent Type Selection

| Task | Agent Type | Model | Tools |
|------|------------|-------|-------|
| Fast file search | explore | haiku | Read, Grep, Glob |
| Code review | Custom | sonnet | Read, Grep, Glob |
| Implementation | general-purpose | sonnet | Read, Write, Edit, Bash |
| Research | Custom | sonnet | Read, WebFetch, WebSearch |
| Security analysis | Custom | opus | Read, Grep, Glob, Bash |
| Testing | Custom | sonnet | Read, Edit, Bash |

### Execution Pattern Selection

| Scenario | Pattern | Reason |
|----------|---------|--------|
| Independent analysis | Parallel | Max speed, context isolation |
| Pipeline (A→B→C) | Sequential | Dependencies between stages |
| Quick operations | Single agent | Minimize token overhead |
| Mixed dependencies | Hybrid | Optimize each phase |

### Token Budget Planning

| Agents | Token Overhead | Use Case |
|--------|---------------|----------|
| 1 | 20k | Simple task |
| 5 | 100k | Module analysis |
| 10 | 200k | Full codebase scan |
| 50 | 1M | Extensive research |

## Resources

For agent definition schema, see: `references/agent-schema.md`

For prompt engineering patterns, see: `references/prompt-patterns.md`

For advanced integration, see: `references/advanced-features.md`
