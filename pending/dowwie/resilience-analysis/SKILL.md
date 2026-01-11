---
name: resilience-analysis
description: Assess error handling, isolation boundaries, and recovery mechanisms in agent frameworks. Use when (1) tracing error propagation paths, (2) evaluating sandboxing for code execution, (3) understanding retry and fallback mechanisms, (4) assessing production readiness, or (5) identifying failure modes and recovery patterns.
---

# Resilience Analysis

Assesses error handling and isolation boundaries.

## Process

1. **Trace error propagation** — Map exception flow from tools to agent
2. **Identify isolation** — Sandbox mechanisms for dangerous operations
3. **Catalog recovery** — Retry logic, fallbacks, circuit breakers
4. **Assess boundaries** — What crashes propagate vs. are contained

## Error Propagation Analysis

### Questions to Answer

1. Does a tool exception terminate the agent?
2. Are LLM API errors retried automatically?
3. Is parsing failure (malformed output) recoverable?
4. What happens when state updates fail?

### Propagation Patterns

**Crash Propagation (Dangerous)**
```python
def run_tool(self, tool, args):
    return tool.execute(args)  # Exception bubbles up
```

**Exception Wrapping**
```python
def run_tool(self, tool, args):
    try:
        return tool.execute(args)
    except Exception as e:
        raise ToolExecutionError(tool.name, e) from e
```

**Error Containment**
```python
def run_tool(self, tool, args):
    try:
        return ToolResult(success=True, output=tool.execute(args))
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

### Propagation Map Template

```
User Input
    ↓
┌─────────────────────────────────────────┐
│ Agent Loop                              │
│   ↓                                     │
│ ┌─────────────────────────────────────┐ │
│ │ LLM Call                            │ │
│ │ • APIError → [Retry 3x / Propagate] │ │
│ │ • RateLimit → [Backoff / Propagate] │ │
│ │ • Timeout → [Retry / Propagate]     │ │
│ └─────────────────────────────────────┘ │
│   ↓                                     │
│ ┌─────────────────────────────────────┐ │
│ │ Output Parsing                      │ │
│ │ • ParseError → [Retry / Contained]  │ │
│ │ • ValidationError → [Contained]     │ │
│ └─────────────────────────────────────┘ │
│   ↓                                     │
│ ┌─────────────────────────────────────┐ │
│ │ Tool Execution                      │ │
│ │ • ToolError → [Feedback to LLM]     │ │
│ │ • Timeout → [Kill / Continue]       │ │
│ │ • SecurityError → [Propagate]       │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Sandboxing Mechanisms

### Code Execution Isolation

| Mechanism | Safety Level | Performance | Complexity |
|-----------|-------------|-------------|------------|
| None | ⚠️ Dangerous | Fast | None |
| RestrictedPython | Medium | Fast | Low |
| AST Validation | Low | Fast | Medium |
| Subprocess | Medium | Overhead | Low |
| Docker/Container | High | High overhead | Medium |
| gVisor/Firecracker | Very High | Medium overhead | High |

### Detection Patterns

**No Sandboxing**
```python
exec(user_code)  # Direct execution
eval(expression)  # Direct eval
subprocess.run(cmd, shell=True)  # Shell injection risk
```

**Basic Sandboxing**
```python
# RestrictedPython
from RestrictedPython import compile_restricted
code = compile_restricted(user_code, '<string>', 'exec')

# AST validation
tree = ast.parse(user_code)
if has_dangerous_nodes(tree):
    raise SecurityError()
```

**Process Isolation**
```python
# Subprocess with limits
result = subprocess.run(
    ['python', '-c', user_code],
    timeout=30,
    capture_output=True,
    user='nobody'  # Drop privileges
)
```

**Container Isolation**
```python
import docker
client = docker.from_env()
container = client.containers.run(
    'python:3.11-slim',
    command=['python', '-c', user_code],
    mem_limit='256m',
    network_disabled=True,
    remove=True
)
```

## Recovery Patterns

### Retry Logic

```python
# Simple retry
@retry(max_attempts=3, backoff=exponential)
def call_llm(self, prompt):
    return self.client.generate(prompt)

# Retry with error feedback
def call_with_retry(self, prompt, max_retries=3):
    errors = []
    for i in range(max_retries):
        try:
            return self.llm.generate(prompt)
        except ParseError as e:
            errors.append(str(e))
            prompt = f"{prompt}\n\nPrevious errors: {errors}"
    raise MaxRetriesExceeded(errors)
```

### Fallback Mechanisms

```python
def generate(self, prompt):
    try:
        return self.primary_llm.generate(prompt)
    except APIError:
        return self.fallback_llm.generate(prompt)
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failures = 0
        self.state = 'closed'
        self.last_failure = None
    
    def call(self, func, *args):
        if self.state == 'open':
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = 'half-open'
            else:
                raise CircuitOpen()
        
        try:
            result = func(*args)
            self.failures = 0
            self.state = 'closed'
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.state = 'open'
            raise
```

## Output Template

```markdown
## Resilience Analysis: [Framework Name]

### Error Propagation Map

| Error Source | Error Type | Handling | Propagates? |
|--------------|-----------|----------|-------------|
| LLM API | RateLimitError | Retry 3x with backoff | No |
| LLM API | APIError | Retry 1x | Yes |
| Parser | ParseError | Feed back to LLM | No |
| Tool | Exception | Wrap and feed to LLM | No |
| Tool | Timeout | Kill process | No |
| State | ValidationError | Propagate | Yes |

### Sandboxing Assessment
- **Code Execution**: [Mechanism or None]
- **File System**: [Isolated/Restricted/Open]
- **Network**: [Blocked/Filtered/Open]
- **Resource Limits**: [Memory/CPU/Time limits]

### Recovery Mechanisms

| Pattern | Implementation | Location |
|---------|---------------|----------|
| Retry | Exponential backoff, 3 attempts | llm.py:L45 |
| Fallback | Secondary model | agent.py:L120 |
| Circuit Breaker | None | - |

### Risk Assessment
- **Critical Gaps**: [List any missing protections]
- **Production Ready**: [Yes/No/Needs work]
```

## Integration

- **Prerequisite**: `codebase-mapping` to identify execution code
- **Feeds into**: `antipattern-catalog` for error handling issues
- **Related**: `execution-engine-analysis` for async error handling
