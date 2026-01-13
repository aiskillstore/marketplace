---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: nathan-standards
---

# n8n Workflow Patterns for Nathan

Detailed patterns and templates for creating n8n workflows in the Nathan project.

## Complete Webhook Workflow Template

```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "id": "webhook",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "webhookId": "unique-webhook-id",
      "parameters": {
        "path": "webhook-path",
        "httpMethod": "POST",
        "responseMode": "responseNode"
      }
    },
    {
      "id": "validate-secret",
      "name": "Validate Secret",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [450, 300],
      "parameters": {
        "conditions": {
          "options": {
            "caseSensitive": true,
            "leftValue": "",
            "typeValidation": "strict"
          },
          "conditions": [
            {
              "id": "secret-check",
              "leftValue": "={{ $json.headers['x-n8n-secret'] }}",
              "rightValue": "={{ $env.N8N_WEBHOOK_SECRET }}",
              "operator": {
                "type": "string",
                "operation": "equals"
              }
            }
          ],
          "combinator": "and"
        }
      }
    },
    {
      "id": "unauthorized-response",
      "name": "Unauthorized Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [650, 450],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { success: false, error: \"Unauthorized\" } }}",
        "options": {
          "responseCode": 401
        }
      }
    },
    {
      "id": "operation",
      "name": "Main Operation",
      "type": "n8n-nodes-base.jira",
      "typeVersion": 1,
      "position": [650, 150],
      "parameters": {
        "resource": "issue",
        "operation": "get",
        "issueKey": "={{ $('Webhook').item.json.body.ticket_id }}"
      },
      "onError": "continueErrorOutput"
    },
    {
      "id": "success-response",
      "name": "Success Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [850, 100],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { success: true, data: $json } }}"
      }
    },
    {
      "id": "error-response",
      "name": "Error Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [850, 250],
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ { success: false, error: $json.error?.message || 'Operation failed' } }}",
        "options": {
          "responseCode": 500
        }
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Validate Secret", "type": "main", "index": 0}]]
    },
    "Validate Secret": {
      "main": [
        [{"node": "Main Operation", "type": "main", "index": 0}],
        [{"node": "Unauthorized Response", "type": "main", "index": 0}]
      ]
    },
    "Main Operation": {
      "main": [
        [{"node": "Success Response", "type": "main", "index": 0}],
        [{"node": "Error Response", "type": "main", "index": 0}]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1",
    "meta": {
      "version": "1.0.0",
      "description": "Workflow description",
      "contract": {
        "input": {
          "param_name": "type (required|optional) - description"
        },
        "output": {
          "success": "boolean",
          "data": "object (on success)",
          "error": "string (on failure)"
        }
      }
    }
  }
}
```

## Connection Patterns

### Standard Flow (Success/Error Split)

```json
"connections": {
  "Operation Node": {
    "main": [
      [{"node": "Success Handler", "type": "main", "index": 0}],
      [{"node": "Error Handler", "type": "main", "index": 0}]
    ]
  }
}
```

### If Node Branching

Output 0 = TRUE branch, Output 1 = FALSE branch:

```json
"connections": {
  "If Node": {
    "main": [
      [{"node": "True Branch", "type": "main", "index": 0}],
      [{"node": "False Branch", "type": "main", "index": 0}]
    ]
  }
}
```

### AI Language Model Connection

```json
"connections": {
  "LLM Model Node": {
    "ai_languageModel": [
      [{"node": "Chain/Agent Node", "type": "ai_languageModel", "index": 0}]
    ]
  }
}
```

## Expression Patterns

### Accessing Webhook Data

```javascript
// Request body
$('Webhook').item.json.body.field_name

// Headers
$json.headers['x-custom-header']

// Query params (for GET requests)
$('Webhook').item.json.query.param_name
```

### Referencing Other Nodes

```javascript
// By node name
$('Node Name').item.json.field

// Current node input
$json.field

// Previous node in chain
$input.item.json.field
```

### Array Operations (Properly Escaped)

```javascript
// Map with string concatenation (not template literals)
$json.items.map(item => '"' + item + '"').join(',')

// Filter and map
$json.users.filter(u => u.active).map(u => u.name).join('\\n')

// Replace newlines
$json.text.replaceAll('\\n', ' ')
```

## Code Node Pattern

For sandboxed code execution:

```json
{
  "id": "execute-code",
  "name": "Execute Code",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [650, 200],
  "parameters": {
    "jsCode": "// Code here\nconst input = $('Webhook').item.json.body;\ntry {\n  const result = /* processing */;\n  return [{ json: { success: true, result } }];\n} catch (error) {\n  return [{ json: { success: false, error: error.message } }];\n}",
    "mode": "runOnceForAllItems"
  },
  "onError": "continueErrorOutput"
}
```

## Position Guidelines

Standard grid positioning:

| Node Type | X Position | Y Position |
|-----------|------------|------------|
| Webhook | 250 | 300 |
| Validate Secret | 450 | 300 |
| Main Operation | 650 | 200 |
| Unauthorized Response | 650 | 450 |
| Success Response | 850 | 100-150 |
| Error Response | 850 | 250-350 |

Spacing: 200px horizontal, 150px vertical between branches.

## Credential References

```json
{
  "credentials": {
    "jiraSoftwareCloudApi": {
      "id": "credential-id",
      "name": "Jira SW Cloud account"
    }
  }
}
```

Common credential types:

- `jiraSoftwareCloudApi` - Jira Cloud
- `googleGeminiSdkApi` - Google Gemini
- `openAiApi` - OpenAI
- `slackApi` - Slack

## Metadata Contract

Always include a `meta` object in settings:

```json
"settings": {
  "executionOrder": "v1",
  "meta": {
    "version": "1.0.0",
    "description": "What this workflow does",
    "contract": {
      "input": {
        "ticket_id": "string (required) - Jira issue key e.g. AOP-307"
      },
      "output": {
        "success": "boolean",
        "data": "object (on success) - Response data",
        "error": "string (on failure) - Error message"
      }
    }
  }
}
```
