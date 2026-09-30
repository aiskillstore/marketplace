# AI Overview SERP API Reference

Standard Google search results with AI Overview extraction. Returns both organic results and AI-generated overview when available.

## Endpoint

```
POST https://scrapeapi.pangolinfo.com/api/v2/scrape
```

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

## Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| url | Yes | string | Standard Google search URL (no `udm=50`) |
| parserName | Yes | string | Must be `"googleSearch"` |
| screenshot | No | boolean | Capture page screenshot |

### URL Format

```
https://www.google.com/search?num=10&q=<encoded_query>
```

No `udm=50` parameter -- this uses standard Google search.

### Request Example

```json
{
  "url": "https://www.google.com/search?num=10&q=how+java+work",
  "parserName": "googleSearch",
  "screenshot": true
}
```

## Response

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "results_num": 3,
    "ai_overview": 1,
    "json": {
      "type": "organic",
      "items": [
        {
          "type": "ai_overview",
          "items": [
            {
              "type": "ai_overview_elem",
              "content": ["Java works by compiling source code..."]
            }
          ],
          "references": [
            {
              "type": "ai_overview_reference",
              "title": "How Java Works - Oracle",
              "url": "https://docs.oracle.com/...",
              "domain": "Oracle"
            }
          ]
        },
        {
          "type": "organic",
          "items": [
            {
              "type": "organic",
              "url": "https://example.com/java-tutorial",
              "title": "Java Tutorial for Beginners",
              "text": "Learn how Java works from the ground up..."
            }
          ]
        }
      ]
    },
    "screenshot": "https://image.datasea.network/screenshots/...",
    "taskId": "1768988520324-abcdef123456"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| code | int | `0` = success, see error-codes.md for others |
| data.results_num | int | Total number of result items |
| data.ai_overview | int | `1` if AI overview present, `0` if not |
| data.json.items[] | array | Mixed array of ai_overview and organic items |
| data.screenshot | string | Screenshot URL (if requested) |
| data.taskId | string | Unique task identifier |

### AI Overview Detection

- Check `data.ai_overview == 1` to confirm presence
- The AI overview item appears first in the `items` array with `type: "ai_overview"`
- Not all queries trigger an AI overview -- the field will be `0` when absent

### Organic Result Structure

| Field | Type | Description |
|-------|------|-------------|
| type | string | `"organic"` |
| items[].url | string | Result page URL |
| items[].title | string | Result page title |
| items[].text | string | Result snippet text |

## Differences from AI Mode API

| Aspect | AI Overview SERP | AI Mode |
|--------|-----------------|---------|
| parserName | `googleSearch` | `googleAISearch` |
| URL param | no `udm=50` | requires `udm=50` |
| Multi-turn | Not supported | Supported via `param` |
| Results | Organic + optional AI overview | Primarily AI overview |

## Cost

**2 credits per request** for complete AI Overview information retrieval.
