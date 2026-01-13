# Logseq HTTP API Guide

## Overview

Logseq's HTTP API server exposes the full Plugin API over HTTP, allowing external applications to interact with Logseq.

## Setup

### Enable HTTP API

1. Open Logseq
2. Go to **Settings** → **Advanced**
3. Enable **Developer mode**
4. Enable **HTTP APIs server**
5. Optionally enable **Auto start server with app**

### Create Authorization Token

1. **Settings** → **Advanced** → **Authorization tokens**
2. Click **Create token**
3. Copy the token (shown only once!)
4. Store securely (e.g., environment variable)

## API Endpoint

**Base URL**: `http://127.0.0.1:12315`
**API Endpoint**: `http://127.0.0.1:12315/api`
**Method**: POST only

## Request Format

```http
POST /api HTTP/1.1
Host: 127.0.0.1:12315
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN_HERE

{
  "method": "namespace.methodName",
  "args": [arg1, arg2, ...]
}
```

## Available Methods

All methods from `@logseq/libs` are available. Key namespaces:

### logseq.App

```json
// Get current graph
{"method": "logseq.App.getCurrentGraph", "args": []}

// Show notification
{"method": "logseq.App.showMsg", "args": ["Hello!", "success"]}

// Get user configs
{"method": "logseq.App.getUserConfigs", "args": []}
```

### logseq.Editor

```json
// Get page by name
{"method": "logseq.Editor.getPage", "args": ["PageName"]}

// Get block by UUID
{"method": "logseq.Editor.getBlock", "args": ["block-uuid-here"]}

// Get page blocks tree
{"method": "logseq.Editor.getPageBlocksTree", "args": ["PageName"]}

// Insert block
{"method": "logseq.Editor.insertBlock", "args": ["parent-uuid", "Block content"]}

// Update block
{"method": "logseq.Editor.updateBlock", "args": ["block-uuid", "New content"]}

// Set block property
{"method": "logseq.Editor.upsertBlockProperty", "args": ["block-uuid", "propertyName", "value"]}

// Create page
{"method": "logseq.Editor.createPage", "args": ["PageName", {}, {"createFirstBlock": true}]}
```

### logseq.DB

```json
// Execute Datalog query
{
  "method": "logseq.DB.datascriptQuery",
  "args": ["[:find ?title :where [?p :block/title ?title]]"]
}

// Query with parameters
{
  "method": "logseq.DB.datascriptQuery",
  "args": [
    "[:find (pull ?b [*]) :in $ ?tag :where [?b :block/tags ?t] [?t :block/title ?tag]]",
    ["Book"]
  ]
}
```

## Response Format

### Success

```json
{
  "result": <return-value>
}
```

### Error

```json
{
  "error": "Error message"
}
```

## Examples

### Python

```python
import requests
import json

def logseq_call(method, args=None):
    response = requests.post(
        "http://127.0.0.1:12315/api",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}"
        },
        json={"method": method, "args": args or []}
    )
    return response.json()

# Get current graph
graph = logseq_call("logseq.App.getCurrentGraph")
print(f"Current graph: {graph['result']['name']}")

# Get all pages
pages = logseq_call(
    "logseq.DB.datascriptQuery",
    ["[:find ?title :where [?p :block/title ?title] [?p :block/tags ?t] [?t :db/ident :logseq.class/Page]]"]
)
```

### JavaScript/Node.js

```javascript
async function logseqCall(method, args = []) {
  const response = await fetch('http://127.0.0.1:12315/api', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.LOGSEQ_API_TOKEN}`
    },
    body: JSON.stringify({ method, args })
  });
  return response.json();
}

// Usage
const graph = await logseqCall('logseq.App.getCurrentGraph');
console.log(`Current graph: ${graph.result.name}`);
```

### cURL

```bash
# Get current graph
curl -X POST http://127.0.0.1:12315/api \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGSEQ_API_TOKEN" \
  -d '{"method":"logseq.App.getCurrentGraph"}'

# Execute query
curl -X POST http://127.0.0.1:12315/api \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOGSEQ_API_TOKEN" \
  -d '{"method":"logseq.DB.datascriptQuery","args":["[:find ?title :where [?p :block/title ?title]]"]}'
```

## Rate Limits

- No official rate limits documented
- Recommended: Keep requests reasonable (< 10/second)
- Use batching for bulk operations when possible

## Known Issues

- **Windows EBADF errors**: May occur on some Windows systems
- **Port conflicts**: Check if port 12315 is available
- **Token expiry**: Tokens don't expire but can be revoked

## Security Considerations

- API only listens on `127.0.0.1` (localhost)
- Always use Authorization header
- Don't expose port to network
- Store tokens in environment variables
