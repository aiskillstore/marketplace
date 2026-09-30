# AI Mode API Reference

Google AI Mode search via `udm=50` parameter. Returns AI-generated answers with references.

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
| url | Yes | string | Google search URL with `udm=50` |
| parserName | Yes | string | Must be `"googleAISearch"` |
| screenshot | No | boolean | Capture page screenshot |
| param | No | string[] | Follow-up questions for multi-turn dialogue |

### URL Format

```
https://www.google.com/search?num=10&udm=50&q=<encoded_query>
```

- `udm=50` enables Google AI Mode results
- `num` controls the number of results
- `q` is the URL-encoded search query

### Single Query Example

```json
{
  "url": "https://www.google.com/search?num=10&udm=50&q=javascript",
  "parserName": "googleAISearch",
  "screenshot": true
}
```

### Multi-Turn Example

```json
{
  "url": "https://www.google.com/search?num=10&udm=50&q=javascript",
  "parserName": "googleAISearch",
  "param": ["how to setup", "best frameworks"]
}
```

The `param` array contains follow-up questions. Each element is processed as a subsequent turn in the conversation. When the array length exceeds 5, response efficiency decreases -- keep it at 5 or fewer for optimal performance.

## Response

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "results_num": 1,
    "ai_overview": 1,
    "json": {
      "type": "organic",
      "items": [
        {
          "type": "ai_overview",
          "items": [
            {
              "type": "ai_overview_elem",
              "content": [
                "JavaScript is a high-level programming language..."
              ]
            }
          ],
          "references": [
            {
              "type": "ai_overview_reference",
              "title": "JavaScript - Wikipedia",
              "url": "https://en.wikipedia.org/wiki/JavaScript",
              "domain": "Wikipedia"
            }
          ]
        }
      ]
    },
    "screenshot": "https://image.datasea.network/screenshots/...",
    "taskId": "1768988520324-766a695d93b57aad",
    "url": "https://www.google.com/search?num=10&udm=50&q=javascript"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| code | int | `0` = success, see error-codes.md for others |
| data.results_num | int | Number of result items |
| data.ai_overview | int | Number of AI overview blocks |
| data.json.items[] | array | Result items (ai_overview, organic) |
| data.screenshot | string | Screenshot URL (if requested) |
| data.taskId | string | Unique task identifier |

### AI Overview Item Structure

| Field | Type | Description |
|-------|------|-------------|
| type | string | `"ai_overview"` |
| items[].type | string | `"ai_overview_elem"` |
| items[].content | string[] | AI-generated text paragraphs |
| references[].type | string | `"ai_overview_reference"` |
| references[].title | string | Source page title |
| references[].url | string | Source page URL |
| references[].domain | string | Source domain name |

## Cost

**2 credits per request** for complete AI Overview information retrieval.
