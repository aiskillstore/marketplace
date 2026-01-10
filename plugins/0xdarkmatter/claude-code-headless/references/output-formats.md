# Output Formats Reference

Detailed documentation for Claude Code output formats.

## Text Format (Default)

Human-readable output for terminal use.

```bash
claude -p "Hello"
# Output: Hello! How can I help you today?
```

Characteristics:
- Plain text response
- May include ANSI colors (disable with `NO_COLOR=1`)
- No metadata (session ID, cost, etc.)
- Best for interactive scripts

## JSON Format

Structured output for programmatic parsing.

```bash
claude -p "Hello" --output-format json
```

### Success Response

```json
{
  "type": "result",
  "subtype": "success",
  "result": "Hello! How can I help you today?",
  "session_id": "session_abc123xyz",
  "total_cost_usd": 0.00123,
  "duration_ms": 1542,
  "num_turns": 1,
  "is_error": false
}
```

### Error Response

```json
{
  "type": "result",
  "subtype": "error",
  "result": "Error message here",
  "session_id": "session_abc123xyz",
  "total_cost_usd": 0.0005,
  "duration_ms": 234,
  "num_turns": 0,
  "is_error": true
}
```

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always "result" |
| `subtype` | string | "success" or "error" |
| `result` | string | Response text or error message |
| `session_id` | string | Session identifier for resumption |
| `total_cost_usd` | number | Total API cost in USD |
| `duration_ms` | number | Total execution time in milliseconds |
| `num_turns` | number | Number of conversation turns |
| `is_error` | boolean | Whether result is an error |

### Parsing Examples

```bash
# Extract session ID
session=$(claude -p "Start" --output-format json | jq -r '.session_id')

# Check for errors
result=$(claude -p "Task" --output-format json)
if [[ $(echo "$result" | jq -r '.is_error') == "true" ]]; then
    echo "Error: $(echo "$result" | jq -r '.result')"
    exit 1
fi

# Get cost
cost=$(echo "$result" | jq -r '.total_cost_usd')
echo "Cost: \$${cost}"
```

## Stream-JSON Format

Real-time JSONL (JSON Lines) output for streaming applications.

```bash
claude -p "Count to 5" --output-format stream-json
```

### Message Types

#### Assistant Message

```json
{"type": "assistant", "content": "1", "timestamp": "2024-01-15T10:30:00Z"}
{"type": "assistant", "content": "2", "timestamp": "2024-01-15T10:30:01Z"}
```

#### Tool Use

```json
{"type": "tool_use", "tool": "Read", "input": {"file_path": "/path/to/file"}, "timestamp": "..."}
{"type": "tool_result", "tool": "Read", "output": "file contents...", "timestamp": "..."}
```

#### Final Result

```json
{"type": "result", "session_id": "...", "total_cost_usd": 0.01, "duration_ms": 5000}
```

### Stream Processing

```bash
# Process each line as it arrives
claude -p "Long task" --output-format stream-json | while IFS= read -r line; do
    type=$(echo "$line" | jq -r '.type')
    case "$type" in
        assistant)
            echo "Claude: $(echo "$line" | jq -r '.content')"
            ;;
        tool_use)
            echo "Using: $(echo "$line" | jq -r '.tool')"
            ;;
        result)
            echo "Done! Cost: \$$(echo "$line" | jq -r '.total_cost_usd')"
            ;;
    esac
done
```

### Node.js Stream Processing

```javascript
const { spawn } = require('child_process');
const readline = require('readline');

const claude = spawn('claude', ['-p', 'Task', '--output-format', 'stream-json']);

const rl = readline.createInterface({ input: claude.stdout });

rl.on('line', (line) => {
    const event = JSON.parse(line);
    switch (event.type) {
        case 'assistant':
            process.stdout.write(event.content);
            break;
        case 'result':
            console.log(`\nCost: $${event.total_cost_usd}`);
            break;
    }
});
```

### Python Stream Processing

```python
import subprocess
import json

proc = subprocess.Popen(
    ['claude', '-p', 'Task', '--output-format', 'stream-json'],
    stdout=subprocess.PIPE,
    text=True
)

for line in proc.stdout:
    event = json.loads(line)
    if event['type'] == 'assistant':
        print(event['content'], end='', flush=True)
    elif event['type'] == 'result':
        print(f"\nCost: ${event['total_cost_usd']}")
```

## Format Comparison

| Feature | text | json | stream-json |
|---------|------|------|-------------|
| Real-time output | Yes | No | Yes |
| Structured data | No | Yes | Yes |
| Session ID | No | Yes | Yes |
| Cost tracking | No | Yes | Yes |
| Easy parsing | No | Yes | Yes |
| Best for | Humans | Scripts | Real-time apps |

## Format Selection Guide

| Use Case | Format |
|----------|--------|
| Interactive terminal | text |
| CI/CD pipelines | json |
| Web applications | stream-json |
| Cost tracking | json |
| Session management | json |
| Live progress display | stream-json |
