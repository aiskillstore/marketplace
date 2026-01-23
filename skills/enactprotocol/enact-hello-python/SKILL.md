---
enact: "2.0.0"
name: "enact/hello-python"
version: "1.0.3"
description: "A simple Python greeting tool"
license: "MIT"
from: "python:3.12-slim"

inputSchema:
  type: object
  properties:
    name:
      type: string
      description: "Name to greet"
      default: "World"

outputSchema:
  type: object
  properties:
    greeting:
      type: string

command: "python /workspace/hello.py ${name}"
---

# Hello Python

A simple Python tool that greets you by name.

## Usage

```bash
enact run examples/hello-python --input "name=Alice"
```
