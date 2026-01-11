---
name: docs-retrieval
description: "Retrieve documentation context from local ai-docs. Check here first when implementing features, debugging errors, or needing library information. Fall back to web search if topic not found locally."
protocols:
  - .claude/ai-dev-kit/protocols/docs-management.md
---

# Documentation Retrieval Skill

This skill enables efficient retrieval of documentation context from the hierarchical documentation system.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| MAX_TOKENS | 2000 | Target token budget for context loading |
| LOAD_FULL_CONTEXT | false | Use full-context.md instead of targeted pages |
| LOCAL_FIRST | true | Check ai-docs before web search |

## Instructions

**MANDATORY** - Always check local documentation before web searches.

- Start with `_index.toon` files for navigation
- Load targeted page summaries, not full contexts
- Consolidate multi-library context using the format below
- Pass pre-loaded context to sub-agents

## Red Flags - STOP and Reconsider

If you're about to:
- Load `full-context.md` for a simple question
- Web search without checking local docs first
- Let sub-agents navigate from scratch instead of passing context
- Load all libraries "just in case"

**STOP** -> Use targeted retrieval patterns below -> Then proceed

## Workflow

1. [ ] **CHECKPOINT**: Have you identified what libraries you need?
2. [ ] Check `ai-docs/libraries/_index.toon` for available docs
3. [ ] Navigate to specific library `_index.toon`
4. [ ] Identify relevant pages from index
5. [ ] Load only the page summaries you need
6. [ ] **CHECKPOINT**: Are you within token budget?

## Cookbook

### Direct Navigation
- IF: You know the library and topic
- THEN: Read `cookbook/direct-navigation.md`
- RESULT: Fastest path to specific information

### Keyword Search
- IF: Uncertain which library has what you need
- THEN: Read `cookbook/keyword-search.md`
- RESULT: Find relevant docs by matching keywords

### Multi-Library Gathering
- IF: Task involves multiple libraries
- THEN: Read `cookbook/multi-library.md`
- RESULT: Consolidated context from multiple sources

### Full Context Loading
- IF: Need comprehensive understanding (migrations, tutorials)
- THEN: Read `cookbook/full-context.md`
- WARNING: High token cost (5,000-15,000 tokens)

## When to Use This Skill

- Before implementing features involving external libraries
- When debugging errors from external dependencies
- When spawning sub-agents that need library context
- When uncertain about API syntax or behavior

## Retrieval Patterns

### Pattern 1: Direct Navigation (Know What You Need)

When you know the library and topic:

```
1. @ai-docs/libraries/{library}/_index.toon
   -> Read overview and common_tasks

2. Find matching task or section
   -> Note the page path

3. @ai-docs/libraries/{library}/{section}/pages/{page}.toon
   -> Get detailed summary with gotchas and patterns
```

**Example: Need BAML retry configuration**
```
1. @ai-docs/libraries/baml/_index.toon
   -> common_tasks: "Handle errors gracefully" -> guide/error-handling

2. @ai-docs/libraries/baml/guide/pages/error-handling.toon
   -> RetryPolicy syntax, gotchas about timeouts
```

### Pattern 2: Keyword Search (Uncertain What Exists)

When you're not sure which library or page:

```
1. @ai-docs/libraries/_index.toon
   -> Scan library descriptions and keywords

2. Match your need against keywords
   -> Identify candidate libraries

3. For each candidate:
   -> @ai-docs/libraries/{lib}/_index.toon
   -> Check if relevant content exists

4. Load specific pages from best match
```

**Example: Need "structured output parsing"**
```
1. @ai-docs/libraries/_index.toon
   -> BAML: "Structured LLM outputs with type safety" [match]
   -> MCP: "Tool integration protocol" [no match]

2. @ai-docs/libraries/baml/_index.toon
   -> Confirms: type system, parsing, validation

3. Load relevant BAML pages
```

### Pattern 3: Multi-Library Gathering (Complex Tasks)

When task involves multiple libraries:

```
1. List all libraries involved in task

2. For each library:
   -> Load _index.toon
   -> Identify relevant pages
   -> Load page summaries

3. Consolidate into single context block

4. OR: Spawn docs-context-gatherer agent
```

### Pattern 4: Full Context (Deep Work)

When you need comprehensive understanding:

```
@ai-docs/libraries/{library}/full-context.md
```

**Use sparingly** - this loads everything (~5,000-15,000 tokens)

Appropriate for:
- Major migrations
- Writing tutorials
- Architectural decisions
- First-time deep learning

## Context Consolidation Format

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

## Budget Management

### Token Estimates by File Type

| File Type | Typical Size |
|-----------|--------------|
| `_index.toon` (category) | 100-150 tokens |
| `_index.toon` (library) | 150-250 tokens |
| `_index.toon` (section) | 100-200 tokens |
| `pages/*.toon` | 250-450 tokens |
| `full-context.md` | 5,000-15,000 tokens |

### Budget Guidelines

| Task Type | Target Budget | Loading Strategy |
|-----------|---------------|------------------|
| Quick fix | 300-500 | 1 page summary |
| Single feature | 800-1,200 | 2-3 page summaries |
| Integration | 1,500-2,500 | Library index + 4-6 pages |
| Multi-library | 2,000-4,000 | Multiple library indexes + key pages |
| Full context | 5,000+ | full-context.md |

### Efficiency Tips

1. **Index files are cheap navigation** - Read them freely
2. **Page summaries are high-signal** - Designed for this purpose
3. **Gotchas prevent expensive mistakes** - Always worth loading
4. **Code patterns are copy-paste ready** - High value per token
5. **full-context.md is last resort** - Use targeted loading first

## Common Retrieval Scenarios

### Scenario: Implementing a Feature

```
1. Identify: What libraries does this feature use?
2. Navigate: Find relevant pages in each library
3. Load: Page summaries for implementation guidance
4. Note: Gotchas before writing code
5. Proceed: Implement with context loaded
```

### Scenario: Debugging an Error

```
1. Identify: Which library produced the error?
2. Search: Error-related pages in that library
3. Load: Error handling and troubleshooting pages
4. Check: Known gotchas that might explain the issue
5. Proceed: Debug with context
```

### Scenario: Spawning Sub-Agent

```
1. Analyze: What docs will sub-agent need?
2. Gather: Load relevant pages NOW
3. Consolidate: Format as context block
4. Include: Add to sub-agent spawn prompt
5. Spawn: Sub-agent has pre-loaded context
```

### Scenario: Uncertain Which Library

```
1. Start: @ai-docs/libraries/_index.toon
2. Scan: Library descriptions and keywords
3. Match: Find libraries relevant to your need
4. Explore: Check promising library indexes
5. Load: Pages from best matching library
```

### Scenario: AI Tool Documentation

When you need information about AI tools (Claude Code, BAML, MCP, TOON, etc.):

```
1. Check local ai-docs FIRST:
   @ai-docs/libraries/claude-code/_index.toon
   @ai-docs/libraries/baml/_index.toon
   @ai-docs/libraries/toon/_index.toon

2. Navigate using same patterns as any library:
   -> Find section in _index.toon
   -> Load relevant page summaries
   -> Use full-context.md for comprehensive needs

3. Fall back to web search/fetch when:
   - Local docs don't cover the specific topic
   - Need time-sensitive info (release dates, latest versions)
   - Local docs are insufficient after checking
   - User explicitly requests current web information
```

**Why local first:**
- Faster (no network round-trip)
- Curated context (TOON format optimized for LLMs)
- Gotchas pre-extracted
- Token-efficient vs. full web pages

**When to web search:**
- Topic not found after checking local index
- Need current/live information
- User explicitly asks for latest from web

## Anti-Patterns

### Don't: Load full-context.md for Simple Questions

**Bad**: Load 15K tokens to answer "what's the retry syntax?"
**Good**: Navigate to specific page, load ~400 tokens

### Don't: Skip Documentation

**Bad**: "I probably remember how this works..."
**Good**: Take 30 seconds to load relevant page

### Don't: Re-Navigate in Sub-Agents

**Bad**: Each sub-agent navigates from scratch
**Good**: Parent loads context, passes to sub-agents

### Don't: Load Everything "Just in Case"

**Bad**: Load all libraries mentioned anywhere
**Good**: Load specific pages for specific needs

## Integration with Protocol

This skill implements the retrieval portions of:
`.claude/ai-dev-kit/protocols/docs-management.md`

Always follow the protocol's decision flow:
1. Task Analysis -> Identify libraries
2. Documentation Check -> Verify docs exist
3. Context Loading -> Use this skill's patterns
4. Execute with Context -> Proceed with task
