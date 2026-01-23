---
name: test/failing-test
version: 1.0.0
description: A test tool that fails with visible output
from: node:20-alpine
command: node /workspace/script.js '${message}'
inputSchema:
  type: object
  properties:
    message:
      type: string
      description: Message to print before failing
      default: Hello from failing test
  required: []
---

# Failing Test Tool

This tool prints output and then fails, to test error visibility.
