# OpenAI / Codex Delegation

Delegate tasks to OpenAI's Codex CLI for sandboxed execution.

## When to Use

- Sandboxed code execution (security-sensitive)
- Running untrusted or experimental code
- Tasks requiring isolated environment
- When you need deterministic execution

## Prerequisites

### Authentication

**Subscription (Interactive):**
```bash
codex login
```

**API Key (Headless):**
```bash
export OPENAI_API_KEY="sk-..."
# or
export CODEX_API_KEY="sk-..."
```

### Check Installation

```bash
which codex
codex --version
```

## Delegation Commands

### Basic Execution

```bash
codex "your task description here"
```

### With Specific Model

```bash
# Get current models first
python .claude/ai-dev-kit/skills/model-discovery/scripts/fetch_models.py --provider openai

# Then use a specific model
codex --model gpt-5.2-codex "your task"
```

### Non-Interactive Mode

```bash
codex -p "task description" --output-format text
```

### Full Auto-Approval (YOLO Mode)

```bash
codex --full-auto "task description"
```

**Warning**: Only use in sandboxed environments

## Key Flags

| Flag | Description |
|------|-------------|
| `--model` | Specify model (e.g., `gpt-5.2-codex`) |
| `-p "prompt"` | Non-interactive with prompt |
| `--full-auto` | Auto-approve all actions |
| `--output-format` | `text` or `json` |
| `--sandbox` | Force sandboxed execution |

## Example Delegations

### Run Code Safely

```bash
codex -p "Run this Python script and report the output:

\`\`\`python
import subprocess
result = subprocess.run(['ls', '-la'], capture_output=True)
print(result.stdout.decode())
\`\`\`
" --sandbox
```

### Test Implementation

```bash
codex -p "Write and run tests for this function:

\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
\`\`\`
"
```

### Security Analysis

```bash
codex -p "Analyze this code for security vulnerabilities and test each finding:

\`\`\`python
import pickle
data = pickle.loads(user_input)
\`\`\`
" --sandbox
```

## Response Handling

Parse Codex output and summarize:

```markdown
## Delegation Result

**Provider**: OpenAI Codex
**Task**: [task description]
**Status**: Success

### Execution Output
[stdout/stderr from sandboxed execution]

### Analysis
[Any additional observations]
```

## Error Handling

| Error | Solution |
|-------|----------|
| "Authentication required" | Run `codex login` or set API key |
| "Model not found" | Check available models with model-discovery |
| "Sandbox unavailable" | Codex sandbox may be in maintenance |
| "Rate limited" | Wait and retry, or switch to subscription |

## Limitations

- Sandboxed environment has limited network access
- File persistence may not survive sessions
- Some system operations restricted
- Rate limits apply based on plan
