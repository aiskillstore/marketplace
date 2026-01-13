# Multi-Library Gathering Pattern

Use when a task involves multiple libraries that need context consolidation.

## When to Use

- Implementing a feature that spans multiple technologies
- Need to understand how libraries work together
- Spawning sub-agents that need pre-loaded context

## Steps

```
1. List all libraries involved in task

2. For each library:
   -> Load _index.toon
   -> Identify relevant pages
   -> Load page summaries

3. Consolidate into single context block

4. OR: Spawn docs-context-gatherer agent
```

## Consolidation Format

When gathering context from multiple pages, consolidate as:

```markdown
## Documentation Context

### {Library}: {Topic}
**Purpose**: {1-2 sentence purpose}
**Key Points**:
- {concept 1}
- {concept 2}
**Gotchas**:
- {warning 1}
- {warning 2}
**Pattern**:
```{language}
{minimal code example}
```

### {Library}: {Another Topic}
...

---
Sources: {list of page paths loaded}
Tokens: ~{estimate}
```

## Example: BAML + MCP Integration

Task: Create an MCP tool that uses BAML for structured outputs

```
Libraries needed:
1. BAML - for type definitions and LLM calls
2. MCP - for tool server implementation

Load:
@ai-docs/libraries/baml/guide/pages/types.toon
@ai-docs/libraries/baml/guide/pages/functions.toon
@ai-docs/libraries/mcp/guide/pages/tool-servers.toon
@ai-docs/libraries/mcp/reference/pages/tool-schema.toon

Consolidate into context block for implementation.
```

## Token Budget

- Multiple library indexes: ~400-600 tokens
- Selected page summaries: ~400 tokens each
- **Typical total: 2000-4000 tokens**

## Tips

- Pre-load context before spawning sub-agents
- Include gotchas from all relevant libraries
- Code patterns from different libraries may need adaptation
