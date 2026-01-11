# Ollama Local Models

Fetch locally installed models from the Ollama API.

## API Endpoints

### List All Available Models

```
GET http://localhost:11434/api/tags
```

### List Currently Running Models

```
GET http://localhost:11434/api/ps
```

## No Authentication Required

Ollama runs locally and does not require API keys.

## Fetch Commands

### All Installed Models

```bash
curl -s http://localhost:11434/api/tags
```

### Parse with jq

```bash
# Just model names
curl -s http://localhost:11434/api/tags | jq -r '.models[].name'

# Model names and sizes
curl -s http://localhost:11434/api/tags | \
  jq '.models[] | {name, size: (.size / 1073741824 | floor | tostring + "GB")}'

# Currently loaded/running models
curl -s http://localhost:11434/api/ps | jq -r '.models[].name'
```

## Response Schema

### /api/tags Response

```json
{
  "models": [
    {
      "name": "llama3:latest",
      "model": "llama3:latest",
      "modified_at": "2024-12-01T10:30:00Z",
      "size": 4661224676,
      "digest": "sha256:abc123...",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",
        "families": ["llama"],
        "parameter_size": "8B",
        "quantization_level": "Q4_0"
      }
    }
  ]
}
```

### /api/ps Response

```json
{
  "models": [
    {
      "name": "llama3:latest",
      "model": "llama3:latest",
      "size": 4661224676,
      "digest": "sha256:abc123...",
      "expires_at": "2024-12-01T11:30:00Z",
      "size_vram": 4661224676
    }
  ]
}
```

## Response Fields

| Field | Description |
|-------|-------------|
| `name` | Model identifier (e.g., `llama3:latest`) |
| `size` | Model size in bytes |
| `modified_at` | Last modification timestamp |
| `digest` | SHA256 hash of model |
| `details.parameter_size` | Model parameters (e.g., `8B`, `70B`) |
| `details.quantization_level` | Quantization (e.g., `Q4_0`, `Q8_0`) |

## Common Models

| Model | Parameters | Use Case |
|-------|------------|----------|
| `llama3.2` | 1B, 3B | Lightweight, fast |
| `llama3.1` | 8B, 70B, 405B | General purpose |
| `codellama` | 7B, 13B, 34B | Code generation |
| `mistral` | 7B | Fast, efficient |
| `mixtral` | 8x7B | MoE architecture |
| `phi3` | 3.8B | Microsoft, efficient |
| `qwen2.5` | 0.5B-72B | Alibaba, multilingual |
| `deepseek-coder` | 1.3B-33B | Code-focused |

## Model Naming Convention

```
<model>:<tag>

Examples:
- llama3:latest      # Latest version
- llama3:8b          # Specific size
- llama3:8b-q4_0     # Specific quantization
- codellama:13b-code # Specific variant
```

## Check Ollama Status

```bash
# Version check
curl -s http://localhost:11434/api/version

# Health check (should return empty JSON)
curl -s http://localhost:11434/
```

## Custom Host

If Ollama is running on a different host or port:

```bash
OLLAMA_HOST="http://192.168.1.100:11434"
curl -s "$OLLAMA_HOST/api/tags"
```

## Notes

- Models must be pulled before they appear (`ollama pull llama3`)
- `/api/ps` shows only models currently loaded in memory
- Models unload after inactivity (configurable timeout)
- No pagination - returns all models in single response

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ollama not running - start with `ollama serve` |
| Empty models list | No models pulled - run `ollama pull <model>` |
| Slow response | Large model being loaded into memory |
| Out of memory | Try smaller model or quantization |
