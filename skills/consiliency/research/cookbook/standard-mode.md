# Standard Mode Research

Balanced research for most queries.

## Configuration

| Setting | Value |
|---------|-------|
| Agents | 4 (2 web, 1 docs, 1 code) |
| Timeout | 3 minutes |
| Model | haiku |

## When to Use

- Technical questions
- Implementation guidance
- Best practices lookup
- API/library research

## Execution Pattern

```
Launch in parallel (ONE message):
├─ Task: Web researcher 1 (haiku)
│    └─ Primary WebSearch query
│
├─ Task: Web researcher 2 (haiku)
│    └─ Alternative angle/sources
│
├─ Task: Docs researcher (haiku)
│    └─ Search ai-docs/ + specs/
│
└─ Task: Code researcher (haiku)
     └─ Find implementation examples
```

## Agent Queries

Given query: "How to implement WebSocket authentication?"

| Agent | Query/Search |
|-------|--------------|
| Web 1 | "WebSocket authentication best practices 2025" |
| Web 2 | "WebSocket JWT token validation" |
| Docs | Grep ai-docs for "websocket auth" |
| Code | Grep codebase for WebSocket patterns |

## Output Format

```markdown
## Research Report: [query]

**Mode**: standard
**Duration**: [time]
**Agents**: [N]/4

### Summary
[3-4 sentence overview]

### Key Findings

#### [Finding 1] (HIGH confidence)
[Details from multiple sources]

#### [Finding 2] (MEDIUM confidence)
[Details from 2 sources]

### Implementation Notes
[Code examples found]

### Sources
- [URLs and file paths]

### Metadata
[Agent response stats]
```

## Cross-Validation

Standard mode cross-validates:
- Web sources against each other
- Web against local docs
- Theory against code examples

## Timeout Behavior

At 3-minute mark:
1. Collect available results
2. Note pending agents
3. Proceed with synthesis
4. Indicate incomplete sources
