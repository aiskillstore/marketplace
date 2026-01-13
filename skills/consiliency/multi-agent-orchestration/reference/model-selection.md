# Model Tier Selection Guide

Guidance on selecting the right model tier for different task types across providers.

## Model Tiers by Provider

### Claude (Anthropic)

| Tier | Model | Token Speed | Best For |
|------|-------|-------------|----------|
| Fast | Haiku 4.5 | ~200 tok/s | Lookups, verification, simple transforms |
| Default | Sonnet 4.5 | ~100 tok/s | Implementation, code review, most coding |
| Heavy | Opus 4.5 | ~50 tok/s | Architecture, complex reasoning, planning |

### OpenAI

| Tier | Model | Token Speed | Best For |
|------|-------|-------------|----------|
| Fast | GPT-5.2-Codex-Mini | ~180 tok/s | Quick code generation, simple tasks |
| Default | GPT-5.2 | ~90 tok/s | General coding, reasoning |
| Heavy | GPT-5.2-Pro | ~40 tok/s | Extended reasoning, complex problems |

### Gemini (Google)

| Tier | Model | Token Speed | Best For |
|------|-------|-------------|----------|
| Fast | Gemini 3 Flash | ~250 tok/s | Quick queries, high volume |
| Default | Gemini 3 Pro | ~120 tok/s | General use, multimodal |
| Heavy | Gemini 3 Deep Think | ~60 tok/s | Complex analysis, large context |

## Task-to-Tier Mapping

### Use FAST Tier (Haiku/Flash/Mini)

Speed matters, intelligence sufficient:

| Task Type | Example |
|-----------|---------|
| Simple lookups | "What's the syntax for X?" |
| Format conversion | JSON to YAML, snake_case to camelCase |
| Validation | Check if file exists, verify format |
| Simple extraction | Get function name from code |
| Grunt work | Repetitive transformations |
| URL fetching | Basic content retrieval |
| Verification steps | Confirm action completed |

**Cost/Speed**: 10-20x faster and cheaper than Heavy tier.

### Use DEFAULT Tier (Sonnet/GPT-5.2/Pro)

Balance of speed and capability:

| Task Type | Example |
|-----------|---------|
| Code implementation | Write a new function or component |
| Bug fixes | Diagnose and fix issues |
| Refactoring | Restructure existing code |
| Documentation | Generate docs from code |
| Code review | Analyze PR changes |
| Test writing | Create unit/integration tests |
| API integration | Connect to external services |
| Summarization | Create documentation summaries |

**This is your workhorse** - use for 70-80% of tasks.

### Use HEAVY Tier (Opus/GPT-5.2-Pro/Deep Think)

Maximum intelligence required:

| Task Type | Example |
|-----------|---------|
| Architecture design | System design, component relationships |
| Complex debugging | Multi-file, subtle bugs |
| Security analysis | Vulnerability assessment |
| Algorithm design | Novel problem solving |
| Large refactors | Cross-cutting architectural changes |
| Strategic planning | Roadmap creation, phase planning |
| Deep code review | Security-focused, architectural review |
| Research synthesis | Combining multiple sources into insights |

**Cost/Speed**: 5-10x slower and more expensive than Default tier.

## Quick Decision Tree

```
Is the task...
│
├─ Simple lookup/transform? ────────────► FAST (Haiku/Flash)
│
├─ Repetitive/grunt work? ──────────────► FAST (Haiku/Flash)
│
├─ Standard coding task? ───────────────► DEFAULT (Sonnet/Pro)
│
├─ Needs deep reasoning? ───────────────► HEAVY (Opus/Deep Think)
│
├─ Architecture/design? ────────────────► HEAVY (Opus/Deep Think)
│
├─ User-facing quality matters? ────────► DEFAULT or HEAVY
│
└─ Uncertain? ──────────────────────────► DEFAULT (safe choice)
```

## Agent Model Recommendations

Recommended model tiers for ai-dev-kit agents:

| Agent | Recommended Tier | Rationale |
|-------|------------------|-----------|
| docs-fetch-url | Fast | Simple retrieval, no complex reasoning |
| docs-summarize-page | Default | Needs good summarization quality |
| docs-discover-* | Fast | URL discovery is mechanical |
| architecture-explorer | Heavy | Deep codebase understanding needed |
| lane-executor | Default | Standard implementation work |
| roadmap-planner | Heavy | Strategic planning requires depth |
| parallel-researcher | Default | Synthesis needs good reasoning |
| test-engineer | Default | Test quality matters |

## Parallel Execution Pattern

When launching multiple agents in parallel, tier selection amplifies:

```markdown
## Good: Mix tiers appropriately

- 5x Fast agents for URL fetching → completes in ~10s total
- 3x Default agents for summarization → completes in ~30s total
- 1x Heavy agent for synthesis → completes in ~60s total

## Bad: All Heavy for grunt work

- 5x Heavy agents for URL fetching → wastes 10x cost/time
```

## Cost Optimization Strategies

### 1. Tier Down for Intermediate Steps

```
DON'T: Use Opus for every step of multi-step task
DO: Use Haiku for data gathering, Opus for final synthesis
```

### 2. Batch Similar Tasks at Same Tier

```
DON'T: Switch tiers frequently within a workflow
DO: Group Fast tasks together, then Default, then Heavy
```

### 3. Fail Fast with Fast Tier

```
DON'T: Use Opus to check if a URL is accessible
DO: Use Haiku for quick validation, escalate if needed
```

### 4. Reserve Heavy for Final Output

```
DON'T: Use Opus for drafts and iterations
DO: Use Sonnet for drafts, Opus for final polish (if needed)
```

## Model Selection in Agent Definitions

Specify model tier in agent frontmatter:

```yaml
---
name: my-agent
description: "Agent description"
model: haiku  # Options: haiku, sonnet, opus (or provider equivalents)
---
```

Or in Task tool calls:

```typescript
Task({
  subagent_type: "docs-fetch-url",
  model: "haiku",  // Explicit tier selection
  prompt: "Fetch https://docs.viperjuice.dev",
  description: "Fetch URL"
})
```

## Provider-Specific Notes

### Claude
- Haiku is remarkably capable for its speed
- Sonnet handles most coding tasks excellently
- Opus shines for architecture and complex reasoning

### OpenAI
- Codex models optimized for code generation
- GPT-5.2-Pro excels at extended chain-of-thought
- Sandbox execution available at all tiers

### Gemini
- Flash has industry-leading speed
- Pro handles massive context (2M tokens)
- Ultra best for multimodal analysis

### Ollama (Local)
- Model selection depends on local hardware
- Smaller models (7B) for Fast tier
- Larger models (70B+) for Default/Heavy
- No cost, but compute-limited
