---
enact: "2.0.0"
name: "enact/hello-rust"
version: "1.0.1"
description: "A simple Rust greeting tool"
license: "MIT"
from: "rust:1.83-slim"

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

build: "rustc /workspace/hello.rs -o /workspace/hello"
command: "/workspace/hello ${name}"
---

# Hello Rust

A simple Rust tool that greets you by name.

## Usage

```bash
enact run ./examples/hello-rust --input "name=Alice"
```
