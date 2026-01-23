---
enact: "2.0.0"
name: "enact/hello-go"
version: "1.0.2"
description: "A simple Go greeting tool"
license: "MIT"
from: "golang:1.23-alpine"

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

command: "go run /workspace/hello.go ${name}"
---

# Hello Go

A simple Go tool that greets you by name.

## Usage

```bash
enact run ./examples/hello-go --input "name=Alice"
```
