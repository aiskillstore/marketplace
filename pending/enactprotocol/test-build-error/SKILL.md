---
name: test/build-error
version: 1.0.0
description: Tests error visibility for build step failures
from: node:20-alpine
build:
  - npm install nonexistent-package-that-does-not-exist-12345
command: echo "Build succeeded"
inputSchema:
  type: object
  properties: {}
  required: []
---

# Build Error Test

This tests that build step errors are properly visible.
