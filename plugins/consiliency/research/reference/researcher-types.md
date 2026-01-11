# Researcher Types

Available researcher agents and their capabilities.

## Overview

| Type | Focus | Tools | Best For |
|------|-------|-------|----------|
| Web | Current info | WebSearch | Latest docs, news |
| Docs | Local docs | Read, Glob, Grep | Library patterns |
| Code | Examples | Read, Grep | Implementation |

## Web Researcher

**Tools**: WebSearch

**Capabilities**:
- Search current web content
- Access official documentation
- Find recent articles and discussions
- Retrieve up-to-date information

**Limitations**:
- Requires network connectivity
- May hit rate limits
- Can't access paywalled content

**Query patterns**:
```
Primary: "[query] [current_year]"
Alternative: "[query] best practices"
Comparison: "[query] vs [alternative]"
```

## Documentation Researcher

**Tools**: Read, Glob, Grep

**Capabilities**:
- Search ai-docs/ indexes
- Navigate TOON hierarchies
- Find library-specific guidance
- Extract relevant sections

**Search strategy**:
```
1. Glob ai-docs/libraries/**/_index.toon
2. Grep for query terms
3. Read relevant pages
4. Extract key sections
```

**Paths searched**:
- `ai-docs/libraries/` - Library docs
- `ai-docs/guides/` - Internal guides
- `specs/` - Project specifications

## Code Researcher

**Tools**: Read, Grep

**Capabilities**:
- Find implementation examples
- Locate test patterns
- Identify usage in codebase
- Extract configuration examples

**Search strategy**:
```
1. Grep for function/class names
2. Grep for import patterns
3. Find test files
4. Read relevant sections
```

**File patterns**:
- `**/*.ts` - TypeScript implementation
- `**/*.test.ts` - Test files
- `**/*.config.*` - Configuration
- `**/README.md` - Local documentation

## Agent Model Selection

All researcher agents use `haiku` by default:
- Fast execution (critical for parallel)
- Sufficient for search/extract tasks
- Lower cost per agent

Synthesis uses `sonnet` in extensive mode:
- Better reasoning for cross-validation
- Improved conflict resolution
- Higher quality summary

## Instance Tagging

Each agent instance is tagged for observability:

```
[researcher-web-1]    First web researcher
[researcher-web-2]    Second web researcher
[researcher-docs-1]   First docs researcher
[researcher-code-1]   First code researcher
```

Tags appear in:
- Agent prompts
- Run logs
- Observability dashboard
- Error reports

## Extending Researchers

To add new researcher type:

1. Create agent in `agents/research/`
2. Define tools and search strategy
3. Add to mode configurations
4. Update this reference
