---
enact: "2.0.0"
name: "enact/hello-ruby"
version: "1.0.1"
description: "A simple Ruby greeting tool"
license: "MIT"
from: "ruby:3.3-alpine"

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

command: "ruby /workspace/hello.rb ${name}"
---

# Hello Ruby

A simple Ruby tool that greets you by name.

## Usage

```bash
enact run ./examples/hello-ruby --input "name=Alice"
```
