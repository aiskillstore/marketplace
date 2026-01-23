---
name: enact/playwright
version: 1.0.0
description: Browser automation tool using Playwright - captures screenshots and extracts content from web pages
from: mcr.microsoft.com/playwright:v1.50.0-noble
build:
  - cd /workspace && npm init -y && npm install playwright-core
command: node /workspace/run.js '${url}' '${action}' '${selector}'
timeout: 600s
inputSchema:
  type: object
  properties:
    url:
      type: string
      description: The URL to navigate to
    action:
      type: string
      description: Action to perform (screenshot, text, html)
      default: text
      enum:
        - screenshot
        - text
        - html
    selector:
      type: string
      description: Optional CSS selector to target specific element
      default: body
  required:
    - url
---

# Playwright Browser Automation

A browser automation tool that uses Playwright to interact with web pages.

## Features

- Navigate to any URL
- Take screenshots
- Extract text content
- Extract HTML content
- Target specific elements with CSS selectors

## Usage

```bash
# Get text content from a page
enact run enact/playwright --args '{"url": "https://example.com"}'

# Take a screenshot
enact run enact/playwright --args '{"url": "https://example.com", "action": "screenshot"}'

# Extract text from a specific element
enact run enact/playwright --args '{"url": "https://example.com", "selector": "h1"}'
```
