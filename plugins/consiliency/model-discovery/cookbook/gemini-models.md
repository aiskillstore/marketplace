# Google Gemini Models

Fetch Gemini model names from the Google Generative AI API.

## API Endpoint

```
GET https://generativelanguage.googleapis.com/v1beta/models
```

## Authentication

API key as query parameter: `?key=$GEMINI_API_KEY`

## Fetch Command

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```

### Parse with jq

```bash
# All models with key fields
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  jq '.models[] | {name, displayName, inputTokenLimit, outputTokenLimit}'

# Just model names
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  jq -r '.models[].name'

# Models that support generateContent (chat/completion)
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | \
  jq '.models[] | select(.supportedGenerationMethods | index("generateContent")) | .name'
```

## Response Schema

```json
{
  "models": [
    {
      "name": "models/gemini-3-flash-lite",
      "displayName": "Gemini 3 Flash-Lite",
      "description": "Fast and versatile multimodal model",
      "inputTokenLimit": 1048576,
      "outputTokenLimit": 8192,
      "supportedGenerationMethods": ["generateContent", "countTokens"],
      "temperature": 1.0,
      "maxTemperature": 2.0,
      "topP": 0.95,
      "topK": 40
    }
  ],
  "nextPageToken": "..."
}
```

## Response Fields

| Field | Description |
|-------|-------------|
| `name` | Model path for API calls (e.g., `models/gemini-3-flash-lite`) |
| `displayName` | Human-readable name |
| `description` | Model description |
| `inputTokenLimit` | Maximum input context length |
| `outputTokenLimit` | Maximum output length |
| `supportedGenerationMethods` | Available API methods |
| `temperature` | Default temperature |
| `topP`, `topK` | Sampling parameters |

## Model Categories

| Model | Characteristics |
|-------|-----------------|
| `gemini-3-flash-lite` | Fast, multimodal |
| `gemini-3-pro` | Balanced, flagship |
| `gemini-3-deep-think` | Extended reasoning |

## Pagination

| Parameter | Default | Description |
|-----------|---------|-------------|
| `pageSize` | 50 | Models per page (max 1000) |
| `pageToken` | - | Token from previous response |

```bash
# First page
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY&pageSize=100"

# Next page
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY&pageToken=NEXT_TOKEN"
```

## Generation Methods

| Method | Purpose |
|--------|---------|
| `generateContent` | Text/chat generation |
| `countTokens` | Token counting |
| `embedContent` | Embeddings |
| `generateAnswer` | Grounded answers |

## Notes

- Model names include `models/` prefix (e.g., `models/gemini-3-pro`)
- Check `supportedGenerationMethods` for capabilities
- Large context models available; verify limits in the API response
- `thinking` field indicates reasoning capability support

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 400 Bad Request | Check API key format in URL |
| 403 Forbidden | API key invalid or Gemini API not enabled |
| Empty models | Enable Generative Language API in Google Cloud Console |
