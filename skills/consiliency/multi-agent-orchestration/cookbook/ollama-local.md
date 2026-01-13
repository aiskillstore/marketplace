# Ollama Local Delegation

Delegate tasks to locally running Ollama for privacy, offline operation, or cost-free inference.

## When to Use

- Processing sensitive/private data
- Offline or air-gapped environments
- Cost-free experimentation
- When cloud providers are unavailable
- Testing prompts before using paid APIs

## Prerequisites

### Start Ollama

```bash
ollama serve
```

### Check Status

```bash
curl -s http://localhost:11434/api/version
```

### Pull Models

```bash
# List available models
ollama list

# Pull a model
ollama pull llama3.2
ollama pull codellama
ollama pull qwen2.5-coder
```

## Delegation Commands

### Basic Query

```bash
ollama run llama3.2 "your prompt here"
```

### With Specific Model

```bash
# Get current local models
python .claude/ai-dev-kit/skills/model-discovery/scripts/fetch_models.py --provider ollama

# Use specific model
ollama run qwen2.5-coder:14b "your coding task"
```

### API-Based (for scripting)

```bash
curl -s http://localhost:11434/api/generate \
  -d '{
    "model": "llama3.2",
    "prompt": "your prompt here",
    "stream": false
  }' | jq -r '.response'
```

### Chat Mode (multi-turn)

```bash
curl -s http://localhost:11434/api/chat \
  -d '{
    "model": "llama3.2",
    "messages": [
      {"role": "user", "content": "your message"}
    ],
    "stream": false
  }' | jq -r '.message.content'
```

## Recommended Models by Task

| Task | Model | Parameters |
|------|-------|------------|
| General chat | `llama3.2` | 3B |
| Coding | `codellama` | 7B-34B |
| Coding (latest) | `qwen2.5-coder` | 7B-32B |
| Fast responses | `phi3` | 3.8B |
| Multilingual | `qwen2.5` | 7B-72B |
| Long context | `llama3.1` | 8B-405B |

## Example Delegations

### Code Review (Private)

```bash
ollama run codellama "Review this code for security issues:

\`\`\`python
$(cat sensitive-code.py)
\`\`\`
"
```

### Generate Boilerplate

```bash
ollama run qwen2.5-coder "Create a Python class for a REST API client with retry logic"
```

### Explain Code

```bash
ollama run llama3.2 "Explain what this function does:

$(cat mystery-function.ts)
"
```

### Batch Processing (API)

```bash
for file in *.py; do
  echo "Processing $file..."
  curl -s http://localhost:11434/api/generate \
    -d "{
      \"model\": \"codellama\",
      \"prompt\": \"Add docstrings to this code:\n$(cat $file)\",
      \"stream\": false
    }" | jq -r '.response' > "${file%.py}_documented.py"
done
```

## Response Handling

Parse Ollama output and summarize:

```markdown
## Delegation Result

**Provider**: Ollama (local)
**Model**: [model name]
**Task**: [task description]
**Status**: Success

### Output
[Model response]

### Notes
- Processed locally (data stayed on device)
- No API costs incurred
```

## Performance Tips

| Tip | Benefit |
|-----|---------|
| Use smaller models for simple tasks | Faster response |
| Keep model loaded (`ollama run` then Ctrl+D) | Avoid reload time |
| Use quantized models (Q4, Q8) | Less memory, faster |
| Use GPU acceleration | Much faster inference |

## Error Handling

| Error | Solution |
|-------|----------|
| "Connection refused" | Start with `ollama serve` |
| "Model not found" | Pull with `ollama pull <model>` |
| "Out of memory" | Use smaller model or quantization |
| "Slow responses" | Check if GPU is being used |

## Check GPU Usage

```bash
# NVIDIA
nvidia-smi

# Ollama should show GPU memory usage
ollama ps
```

## Limitations

- Quality varies by model size
- Slower than cloud APIs (unless good GPU)
- Limited context window on smaller models
- No web search or grounding
- Single machine only
