# OpenAI Models

Fetch GPT-5.2 model names from the OpenAI API.

## API Endpoint

```
GET https://api.openai.com/v1/models
```

## Required Headers

| Header | Value |
|--------|-------|
| `Authorization` | `Bearer $OPENAI_API_KEY` |

## Fetch Command

```bash
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Parse with jq

```bash
# GPT-5.2 models only (excludes embeddings, whisper, dall-e, etc.)
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | \
  jq '.data[] | select(.id | startswith("gpt-5.2")) | {id, owned_by, created}'

# Just GPT-5.2 model IDs
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | \
  jq -r '.data[] | select(.id | startswith("gpt-5.2")) | .id'

# All model types
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | \
  jq -r '.data[].id' | sort
```

## Response Schema

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-5.2",
      "object": "model",
      "created": 1723075200,
      "owned_by": "system"
    }
  ]
}
```

## Response Fields

| Field | Description |
|-------|-------------|
| `id` | Model identifier for API calls |
| `object` | Always `"model"` |
| `created` | Unix timestamp of model creation |
| `owned_by` | Owner organization (`system` for OpenAI models) |

## Model Categories

| Prefix | Type | Examples |
|--------|------|----------|
| `gpt-5.2` | GPT-5.2 family | `gpt-5.2`, `gpt-5.2-mini`, `gpt-5.2-pro` |
| `text-embedding` | Embeddings | `text-embedding-3-large` |
| `whisper` | Speech-to-text | `whisper-1` |
| `dall-e` | Image generation | `dall-e-3` |
| `tts` | Text-to-speech | `tts-1`, `tts-1-hd` |

## Filtering Tips

```bash
# GPT-5.2 models only
jq '.data[] | select(.id | test("^gpt-5\\.2"))'

# Exclude fine-tuned models
jq '.data[] | select(.owned_by == "system")'

# Latest versions only (exclude dated versions)
jq '.data[] | select(.id | test("-[0-9]{4}-[0-9]{2}-[0-9]{2}$") | not)'
```

## Notes

- Returns ALL models including embeddings, whisper, dall-e, etc.
- Filter by prefix for specific model types
- `owned_by: "system"` indicates OpenAI's own models
- Fine-tuned models show different `owned_by` values
- No pagination - returns all models in single response

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check `OPENAI_API_KEY` is set and valid |
| 429 Rate limited | Wait and retry, or check API quota |
| Empty GPT list | API key may be restricted to specific models |
