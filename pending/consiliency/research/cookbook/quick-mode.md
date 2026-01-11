# Quick Mode Research

Fast fact-checking with minimal latency.

## Configuration

| Setting | Value |
|---------|-------|
| Agents | 2 (1 web, 1 docs) |
| Timeout | 2 minutes |
| Model | haiku |

## When to Use

- Simple fact verification
- Quick definition lookup
- "What is X?" questions
- Time-sensitive queries

## Execution Pattern

```
Launch in parallel (ONE message):
├─ Task: Web researcher (haiku)
│    └─ Single WebSearch query
│
└─ Task: Docs researcher (haiku)
     └─ Quick Grep of ai-docs/
```

## Example

Query: "What is TOON format?"

**Agents launched**:
1. Web: Search for "TOON format specification"
2. Docs: Grep ai-docs/ for "toon"

**Expected response time**: 20-40 seconds

## Output Format

Quick mode produces a concise report:

```markdown
## Quick Research: [query]

**Answer**: [1-2 sentence answer]

**Sources**:
- [Web source](url)
- `ai-docs/path/file.toon`

**Confidence**: HIGH | MEDIUM | LOW
```

## Limitations

- May miss nuanced information
- Single query per source
- No code examples searched
- Limited cross-validation

## When to Upgrade

Upgrade to `standard` if:
- Answer seems incomplete
- Need implementation details
- Question is complex
- Multiple aspects to research
