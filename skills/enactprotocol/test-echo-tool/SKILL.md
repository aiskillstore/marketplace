---
enact: "2.0.0"
name: test/echo-tool
version: "1.0.0"
description: A tool that echoes its input for testing
from: alpine:latest
command: echo '{"output":"${text}"}'
inputSchema:
  type: object
  properties:
    text:
      type: string
      description: Text to echo
  required:
    - text
outputSchema:
  type: object
  properties:
    output:
      type: string
---

# Echo Tool

A simple tool that echoes back the input text. Used for testing.

## Usage

```bash
enact run test/echo-tool --input text="Hello"
```
