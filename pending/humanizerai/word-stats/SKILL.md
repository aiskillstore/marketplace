---
name: word-stats
description: Get word count, character count, reading time, and text statistics. Quick analysis without questions.
user-invocable: true
argument-hint: "[text to analyze]"
---

# Word Statistics

Provide quick, accurate statistics about the provided text.

## Input

The user provides text in $ARGUMENTS.

**Important:** If text is provided, immediately output stats. Don't ask clarifying questions - they want the numbers.

## Output Format

```
## Word Statistics

### Counts
| Metric | Value |
|--------|-------|
| Words | [X] |
| Characters (with spaces) | [X] |
| Characters (no spaces) | [X] |
| Sentences | [X] |
| Paragraphs | [X] |

### Time
| Metric | Value |
|--------|-------|
| Reading time | [X] min |
| Speaking time | [X] min |

### Words
| Metric | Value |
|--------|-------|
| Unique words | [X] ([Y]%) |
| Avg word length | [X] chars |
| Longest word | [word] ([X] chars) |

### Sentences
| Metric | Value |
|--------|-------|
| Avg length | [X] words |
| Longest | [X] words |
| Shortest | [X] words |
```

## Calculations

- **Reading time**: words ÷ 238 (average adult reading speed)
- **Speaking time**: words ÷ 150 (average speaking pace)
- **Unique words**: distinct words ÷ total words × 100

## Keep It Simple

- Tables for metrics
- No unnecessary prose
- No recommendations unless asked
- Just the numbers
