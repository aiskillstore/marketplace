---
name: "enact/hello-js"
version: "1.0.2"
description: "A simple JavaScript greeting tool"
from: "node:22-alpine"
command: "node ./hello.js ${name}"
---

# Hello JS Tool

A simple example tool that demonstrates using JavaScript with Enact.

## Usage

This tool takes an optional `name` parameter and returns a friendly greeting.

## Examples

```bash
# Default greeting
enact run examples/hello-js
# Output: Hello, World! 👋

# Custom name
enact run examples/hello-js --input name=Alice
# Output: Hello, Alice! 👋
```
