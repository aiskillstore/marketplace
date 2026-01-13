# Extensive Mode Research

Comprehensive deep-dive research.

## Configuration

| Setting | Value |
|---------|-------|
| Agents | 8 (4 web, 2 docs, 2 code) |
| Timeout | 10 minutes |
| Model | haiku (researchers), sonnet (synthesis) |

## When to Use

- Architecture decisions
- Technology comparisons
- Comprehensive best practices
- Multi-faceted questions
- Writing documentation

## Execution Pattern

```
Launch in parallel (ONE message):
├─ Task: Web researcher 1-4 (haiku)
│    ├─ Official documentation
│    ├─ Community articles
│    ├─ Recent developments
│    └─ Alternative perspectives
│
├─ Task: Docs researcher 1-2 (haiku)
│    ├─ Deep ai-docs/ search
│    └─ Related concepts
│
└─ Task: Code researcher 1-2 (haiku)
     ├─ Implementation patterns
     └─ Test examples
```

## Agent Distribution

| Type | Count | Focus |
|------|-------|-------|
| Web | 4 | Different angles on query |
| Docs | 2 | Breadth and depth |
| Code | 2 | Patterns and tests |

## Query Variation

For query: "Compare Codex CLI and Claude Code workflows"

| Agent | Query Focus |
|-------|-------------|
| Web 1 | "Codex CLI vs Claude Code comparison" |
| Web 2 | "Codex CLI configuration best practices" |
| Web 3 | "Claude Code MCP integration guide" |
| Web 4 | "Agentic coding tools workflow comparison" |
| Docs 1 | Search ai-docs/libraries/codex-cli/ |
| Docs 2 | Search ai-docs/libraries/claude-code/ |
| Code 1 | Find state management in codebase |
| Code 2 | Find related test patterns |

## Output Format

```markdown
## Comprehensive Research Report: [query]

**Mode**: extensive
**Duration**: [time]
**Agents**: [N]/8

### Executive Summary
[Paragraph-length overview]

### Key Findings

#### [Major Finding 1] (HIGH confidence)
**Sources**: web-1, web-3, docs-1

[Detailed analysis with specifics]

[Continue for all major findings]

### Comparative Analysis
[If applicable: comparison table or analysis]

### Implementation Recommendations
[Actionable guidance based on findings]

### Code Examples
[Relevant code from codebase or web]

### Conflicting Information
[Areas where sources disagreed]

### Further Research
[Topics that warrant additional investigation]

### Sources

**Web**:
- [Source 1](url) - main documentation
- [Source 2](url) - community perspective

**Documentation**:
- `ai-docs/path/file.toon`

**Code**:
- `src/path/file.ts:42`

### Metadata
| Metric | Value |
|--------|-------|
| Mode | extensive |
| Total agents | 8 |
| Responded | [N] |
| Timed out | [N] |
| Duration | [time] |
| Synthesis model | sonnet |
```

## Synthesis Upgrade

Extensive mode uses `sonnet` for final synthesis:
- Better cross-referencing
- Improved conflict resolution
- More nuanced confidence scoring
- Better executive summary

## Timeout Strategy

Tiered timeout handling:
- 8 min: Warn approaching timeout
- 9 min: Stop waiting, begin synthesis
- 10 min: Hard cutoff, return available

## Cost Considerations

Extensive mode uses more resources:
- 8 parallel haiku calls
- 1 sonnet synthesis call
- Longer duration

Use only when depth justifies cost.
