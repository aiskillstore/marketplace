# Anthropic Models

Fetch Claude model names from the Anthropic API.

## API Endpoint

```
GET https://api.anthropic.com/v1/models
```

## Required Headers

| Header | Value |
|--------|-------|
| `x-api-key` | `$ANTHROPIC_API_KEY` |
| `anthropic-version` | `2023-06-01` |

## Fetch Command

```bash
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Parse with jq

```bash
# All models with key fields
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" | \
  jq '.data[] | {id, display_name, created_at}'

# Just model IDs
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" | \
  jq -r '.data[].id'
```

## Response Schema

```json
{
  "data": [
    {
      "id": "claude-sonnet-4-5",
      "type": "model",
      "display_name": "Claude Sonnet 4.5",
      "created_at": "2025-05-14T00:00:00Z"
    }
  ],
  "has_more": false,
  "first_id": "...",
  "last_id": "..."
}
```

## Response Fields

| Field | Description |
|-------|-------------|
| `id` | Model identifier for API calls (e.g., `claude-sonnet-4-5`) |
| `display_name` | Human-readable name (e.g., `Claude Sonnet 4.5`) |
| `created_at` | Release timestamp |
| `type` | Always `"model"` |

## Model Categories

| Category | Characteristics | Use Cases |
|----------|-----------------|-----------|
| **Opus** | Most capable, highest cost | Complex reasoning, analysis, code generation |
| **Sonnet** | Balanced performance/cost | General tasks, production workloads |
| **Haiku** | Fast, economical | Simple tasks, high volume, low latency |

## Model Naming Convention

- **Specific version**: `claude-sonnet-4-5-20251124` (recommended for production)
- **Alias**: `claude-sonnet-4-5-latest` (auto-updates, use for testing)

## Notes

- Aliases automatically point to the most recent snapshot
- Use specific versions in production for consistent behavior
- Models are returned sorted by `created_at` descending (newest first)
- Pagination available via `has_more` and `first_id`/`last_id`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check `ANTHROPIC_API_KEY` is set and valid |
| Empty response | API key may lack model list permissions |
| Connection refused | Check network access to api.anthropic.com |
