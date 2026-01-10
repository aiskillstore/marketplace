---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# {{API_NAME}} API Documentation

**Version:** {{VERSION}}
**Base URL:** `{{BASE_URL}}`
**Last Updated:** {{DATE}}

---

## Overview

{{API_DESCRIPTION}}

### Authentication

```
Authorization: Bearer {{TOKEN}}
```

| Method | Description |
|--------|-------------|
| API Key | `X-API-Key: {{KEY}}` |
| Bearer Token | `Authorization: Bearer {{TOKEN}}` |
| OAuth 2.0 | {{OAUTH_FLOW}} |

### Rate Limiting

| Tier | Requests/min | Requests/day |
|------|--------------|--------------|
| Free | {{N}} | {{N}} |
| Pro | {{N}} | {{N}} |
| Enterprise | Unlimited | Unlimited |

**Headers:**

- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Endpoints

### {{RESOURCE_NAME}}

#### List {{RESOURCES}}

```http
GET /{{RESOURCE}}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max items (default: 20, max: 100) |
| `offset` | integer | No | Pagination offset |
| `sort` | string | No | Sort field |
| `order` | string | No | `asc` or `desc` |

**Response:**

```json
{
  "data": [
    {
      "id": "{{ID}}",
      "{{FIELD}}": "{{VALUE}}"
    }
  ],
  "meta": {
    "total": {{N}},
    "limit": {{N}},
    "offset": {{N}}
  }
}
```

#### Get {{RESOURCE}}

```http
GET /{{RESOURCE}}/{{id}}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Resource identifier |

**Response:** `200 OK`

```json
{
  "id": "{{ID}}",
  "{{FIELD}}": "{{VALUE}}",
  "created_at": "{{ISO_DATE}}",
  "updated_at": "{{ISO_DATE}}"
}
```

#### Create {{RESOURCE}}

```http
POST /{{RESOURCE}}
```

**Request Body:**

```json
{
  "{{FIELD}}": "{{VALUE}}",
  "{{FIELD}}": {{VALUE}}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `{{FIELD}}` | {{TYPE}} | {{YES/NO}} | {{DESCRIPTION}} |

**Response:** `201 Created`

#### Update {{RESOURCE}}

```http
PATCH /{{RESOURCE}}/{{id}}
```

**Request Body:**

```json
{
  "{{FIELD}}": "{{NEW_VALUE}}"
}
```

**Response:** `200 OK`

#### Delete {{RESOURCE}}

```http
DELETE /{{RESOURCE}}/{{id}}
```

**Response:** `204 No Content`

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "{{ERROR_CODE}}",
    "message": "{{ERROR_MESSAGE}}",
    "details": [
      {
        "field": "{{FIELD}}",
        "issue": "{{ISSUE}}"
      }
    ]
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Malformed request |
| `unauthorized` | 401 | Invalid credentials |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limited` | 429 | Too many requests |
| `server_error` | 500 | Internal error |

---

## Webhooks

### Event Types

| Event | Description |
|-------|-------------|
| `{{RESOURCE}}.created` | New resource created |
| `{{RESOURCE}}.updated` | Resource modified |
| `{{RESOURCE}}.deleted` | Resource removed |

### Payload Format

```json
{
  "event": "{{EVENT_TYPE}}",
  "timestamp": "{{ISO_DATE}}",
  "data": {
    "{{RESOURCE}}": { ... }
  }
}
```

### Signature Verification

```
X-Webhook-Signature: sha256={{SIGNATURE}}
```

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## SDKs

### JavaScript/TypeScript

```bash
npm install {{PACKAGE_NAME}}
```

```typescript
import { Client } from '{{PACKAGE_NAME}}';

const client = new Client({ apiKey: '{{API_KEY}}' });
const items = await client.{{resource}}.list();
```

### Python

```bash
pip install {{PACKAGE_NAME}}
```

```python
from {{package_name}} import Client

client = Client(api_key="{{API_KEY}}")
items = client.{{resource}}.list()
```

---

## Examples

### cURL

```bash
curl -X GET "{{BASE_URL}}/{{RESOURCE}}" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json"
```

### Create Resource

```bash
curl -X POST "{{BASE_URL}}/{{RESOURCE}}" \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{"{{FIELD}}": "{{VALUE}}"}'
```

---

## Changelog

### v{{VERSION}} ({{DATE}})

- Added: {{NEW_ENDPOINT}}
- Changed: {{MODIFIED_BEHAVIOR}}
- Deprecated: {{DEPRECATED_FIELD}}
- Removed: {{REMOVED_ENDPOINT}}

---

## Quality Checklist

- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Error codes comprehensive
- [ ] Authentication methods explained
- [ ] Rate limits documented
- [ ] SDK examples included
- [ ] Webhook payloads documented
