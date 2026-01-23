---
enact: "2.0.0"
name: enact/text-summarizer
version: 1.0.1
description: Analyzes text and provides word count, character count, and sentence statistics
from: "node:20-alpine"
command: "node /workspace/summarize.js ${text}"
timeout: "30s"

inputSchema:
  type: object
  properties:
    text:
      type: string
      description: "The text to analyze"
  required:
    - text

outputSchema:
  type: object
  properties:
    wordCount:
      type: integer
      description: "Total number of words"
    characterCount:
      type: integer
      description: "Total number of characters (excluding spaces)"
    sentenceCount:
      type: integer
      description: "Estimated number of sentences"
    averageWordLength:
      type: number
      description: "Average word length"
    readingTimeMinutes:
      type: number
      description: "Estimated reading time in minutes"

annotations:
  readOnlyHint: true
  idempotentHint: true

tags:
  - text
  - analysis
  - utility
---

# Text Summarizer

A tool that analyzes text and provides useful statistics including word count, character count, sentence count, and estimated reading time.

## Usage

```bash
enact run keithgroves/text-summarizer --args '{"text": "Hello world. This is a test."}'
```

## Features

- Word count
- Character count (excluding spaces)
- Sentence count estimation
- Average word length calculation
- Reading time estimation (based on 200 words/minute)

## Example Output

```json
{
  "wordCount": 6,
  "characterCount": 22,
  "sentenceCount": 2,
  "averageWordLength": 3.67,
  "readingTimeMinutes": 0.03
}
```
