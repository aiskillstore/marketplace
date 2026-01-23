---
enact: "2.0.0"
name: enact/formatter
version: 1.0.0
description: Formats and prettifies JSON with configurable indentation
from: "node:20-alpine"
command: "node /workspace/format.js ${json} ${indent}"

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
