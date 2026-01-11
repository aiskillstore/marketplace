# Provider Routing Cookbook

Route tasks to the most appropriate AI provider based on task characteristics.

## Quick Decision Tree

```
What is the task type?
├── Complex reasoning/architecture
│   └── Use: Claude (Opus 4.5)
├── Sandboxed code execution
│   └── Use: Codex (gpt-5.2-codex)
├── Large context (>100k tokens)
│   └── Use: Gemini (3 Pro)
├── Quick code generation
│   └── Use: Claude (Haiku 4.5) or Gemini (Flash)
├── Web search/grounding
│   └── Use: Gemini (3 Pro)
├── Multi-file IDE edits
│   └── Use: Cursor Agent
└── Default/General
    └── Use: Claude (Sonnet 4.5)
```

## Priority Matrix

| Task Type | Priority 1 | Priority 2 | Priority 3 |
|-----------|------------|------------|------------|
| Complex reasoning | Claude Opus 4.5 | OpenAI GPT-5.2 | Gemini 3 Pro |
| Sandboxed execution | Codex gpt-5.2-codex | Cursor Composer | Claude Opus 4.5 |
| Large context | Gemini 3 Pro | Claude Opus 4.5 | OpenAI GPT-5.2 |
| Quick codegen | Claude Haiku 4.5 | Gemini 3 Flash | Codex gpt-5.2-codex-mini |
| Web search | Gemini 3 Pro | OpenAI GPT-5.2 | Claude Opus 4.5 |
| Extended reasoning | OpenAI GPT-5.2 | Gemini 3 Deep Think | Claude Opus 4.5 |

## Routing Logic

### Step 1: Assess Task Characteristics

```python
task_characteristics = {
    "complexity": "low|medium|high",    # Reasoning complexity
    "context_size": "small|medium|large",  # Token count
    "sandbox_needed": True|False,        # Needs isolation
    "web_search": True|False,            # Needs grounding
    "speed_priority": True|False,        # Speed over quality
    "multimodal": True|False,            # Images/files
}
```

### Step 2: Apply Routing Rules

```python
def route_task(characteristics):
    # Highest priority checks first
    if characteristics["sandbox_needed"]:
        return "codex"

    if characteristics["context_size"] == "large":
        return "gemini"

    if characteristics["web_search"]:
        return "gemini"

    if characteristics["speed_priority"]:
        return "haiku"  # or gemini-flash

    if characteristics["complexity"] == "high":
        return "claude-opus"

    # Default
    return "claude-sonnet"
```

## Fallback Chains

When primary provider fails, try alternatives:

### Chain: Complex Analysis
```
claude-opus → openai-gpt5.2 → gemini-3-pro
```

### Chain: Code Execution
```
codex → cursor → claude-opus
```

### Chain: Quick Tasks
```
haiku → gemini-flash → codex-mini
```

### Chain: Web Research
```
gemini-3-pro → openai-gpt5.2 → claude-opus
```

## Native Invocation Examples

### Route to Codex (Sandboxed)
```bash
codex exec --sandbox workspace-write --full-auto --model gpt-5.2-codex "Implement feature X"
```

### Route to Gemini (Large Context)
```bash
gemini --model gemini-3-pro --yolo "Analyze this 150k token codebase"
```

### Route to Cursor (IDE Edits)
```bash
cursor-agent --model claude-sonnet-4.5 --force -p "Refactor these 5 files"
```

## Parallel Routing

For comprehensive analysis, route to multiple providers:

```python
# Launch parallel analysis
Task(subagent_type="general-purpose",
     description="Codex security scan [codex-1]",
     run_in_background=True,
     prompt="codex exec --sandbox read-only --full-auto 'Security audit'")

Task(subagent_type="general-purpose",
     description="Gemini architecture review [gemini-1]",
     run_in_background=True,
     prompt="gemini --sandbox --yolo 'Architecture review'")

# Collect and synthesize
results = [
    TaskOutput(task_id="codex-1", block=True),
    TaskOutput(task_id="gemini-1", block=True),
]
```

## Cost Optimization

| Provider | Cost Tier | Best For |
|----------|-----------|----------|
| Claude Haiku | $ | Quick lookups, simple tasks |
| Gemini Flash | $ | Fast responses, moderate context |
| Claude Sonnet | $$ | General coding, balanced tasks |
| Codex | $$ | Sandboxed execution |
| Claude Opus | $$$ | Complex reasoning |
| Gemini Pro | $$$ | Large context, web search |
| GPT-5.2 | $$$ | Extended reasoning |

### Cost-Aware Routing

```python
def route_with_budget(task, budget="medium"):
    if budget == "low":
        return ["haiku", "gemini-flash"]
    elif budget == "medium":
        return ["sonnet", "codex"]
    else:  # high
        return ["opus", "gemini-pro", "gpt-5.2"]
```

## Provider-Specific Strengths

### Claude (Opus 4.5)
- Best: Complex reasoning, architecture decisions
- Context: 200k tokens
- Flags: (no special flags - use Claude Code directly)

### Codex (gpt-5.2-codex)
- Best: Sandboxed execution, code generation
- Context: 32k tokens
- Flags: `--sandbox workspace-write --full-auto`

### Gemini (3 Pro)
- Best: Large context, web search, multimodal
- Context: 2M tokens
- Flags: `--model gemini-3-pro --yolo`

### Cursor Agent
- Best: IDE-integrated edits, multi-file changes
- Context: Inherited from IDE
- Flags: `--model claude-sonnet-4.5 --force -p`

## Error Handling

### Auth Failures
```
Provider returned auth error → Fork terminal for login → Retry
```

### Rate Limits
```
Provider rate limited → Try next in fallback chain → Exponential backoff
```

### Timeouts
```
Provider timeout → Try next in fallback chain → Report partial results
```

## Integration with /ai-dev-kit:route

The `/ai-dev-kit:route` command uses these patterns:

```bash
# Let the routing logic decide
/ai-dev-kit:route "Analyze this large codebase for security issues"
# → Routes to gemini-3-pro (large context + analysis)

# Override with explicit provider
/ai-dev-kit:delegate codex "Execute this code in sandbox"
```
