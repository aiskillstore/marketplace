---
enact: "2.0.0"
name: enact/json-formatter
version: 1.0.1
description: Formats and prettifies JSON with configurable indentation
from: "node:20-alpine"
command: "node /workspace/format.js ${json} ${indent}"
timeout: "30s"

inputSchema:
  type: object
  properties:
    json:
      type: string
      description: "JSON string to format"
    indent:
      type: integer
      default: 2
      description: "Number of spaces for indentation"
  required:
    - json

outputSchema:
  type: object
  properties:
    formatted:
      type: string
      description: "Prettified JSON string"
    valid:
      type: boolean
      description: "Whether the input was valid JSON"
    error:
      type: string
      description: "Error message if JSON was invalid"

annotations:
  readOnlyHint: true
  idempotentHint: true

tags:
  - json
  - formatting
  - utility
---

# JSON Formatter

A simple tool that formats and prettifies JSON strings.

## Usage

```bash
enact run enact/json-formatter --args '{"json": "{\"name\":\"test\",\"value\":123}", "indent": 2}'
```

## Features

- Validates JSON input
- Configurable indentation (default: 2 spaces)
- Returns structured output with validation status
- Handles errors gracefully

## Example Output

```json
{
  "formatted": "{\n  \"name\": \"test\",\n  \"value\": 123\n}",
  "valid": true
}
```
