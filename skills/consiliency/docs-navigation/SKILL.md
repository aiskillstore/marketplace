---
name: docs-navigation
description: "Navigate hierarchical ai-docs indexes to find documentation. Check local docs FIRST for speed and curated context before web searching. Covers Claude Code, BAML, MCP, and other tracked libraries."
---

# Documentation Navigation Skill

Navigate the hierarchical documentation system to find relevant context with minimal token usage.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| START_LEVEL | auto | `auto`, `root`, `category`, `library`, `section`, `page` |
| KEYWORD_MATCH | fuzzy | `fuzzy` (semantic) or `exact` matching for index navigation |

## Instructions

**MANDATORY** - Always start at the appropriate index level and drill down.

- Read `_index.toon` files before loading pages
- Match task keywords against index keywords
- Load specific pages, not full contexts
- Note `priority` and `when_to_use` fields in indexes

## Red Flags - STOP and Reconsider

If you're about to:
- Load `full-context.md` for a simple question
- Guess file paths instead of reading the index
- Skip the index and go straight to pages
- Load everything "just in case"

**STOP** -> Follow the Navigation Protocol below -> Then proceed

## Workflow

1. [ ] **CHECKPOINT**: Identify what you know (library? section? topic?)
2. [ ] Start at the appropriate index level
3. [ ] Read index, match keywords to your task
4. [ ] Drill down to specific pages
5. [ ] Load only the pages you need
6. [ ] **CHECKPOINT**: Is full-context.md justified? (rarely)

## Cookbook

### Level Selection
- IF: Unsure where to start in the hierarchy
- THEN: Read `cookbook/level-selection.md`
- RESULT: Start at the right level based on what you know

### Keyword Matching
- IF: Searching for documentation by topic
- THEN: Read `cookbook/keyword-matching.md`
- RESULT: Find relevant pages through index keywords

### Efficient Page Loading
- IF: Loading multiple pages or managing token budget
- THEN: Read `cookbook/page-loading.md`
- RESULT: Minimize token usage while getting needed context

## The Hierarchy

```
ai-docs/
├── _root_index.toon              # Level 0: All categories
├── libraries/
│   ├── _index.toon               # Level 1: All libraries
│   ├── {library}/
│   │   ├── _index.toon           # Level 2: Library sections
│   │   ├── {section}/
│   │   │   ├── _index.toon       # Level 3: Section pages
│   │   │   └── pages/
│   │   │       └── {page}.toon   # Level 4: Page summary
│   │   └── full-context.md       # Everything (escape hatch)
```

## Navigation Protocol

### Step 1: Start at the Right Level

| You Know | Start Here |
|----------|------------|
| Nothing | `ai-docs/_root_index.toon` |
| Category (libraries/frameworks) | `ai-docs/{category}/_index.toon` |
| Library name | `ai-docs/libraries/{lib}/_index.toon` |
| Library + section | `ai-docs/libraries/{lib}/{section}/_index.toon` |
| Exact page | `ai-docs/libraries/{lib}/{section}/pages/{page}.toon` |

### Step 2: Read Index, Match Keywords

Each index contains:
- `description` or `purpose` - What this level contains
- `keywords` - Terms for matching your task
- `when_to_use` - Guidance on when to drill deeper
- Child paths - Where to navigate next

**Match your task against keywords:**
```
Task: "Handle LLM retry failures"
Keywords to find: retry, error, failure, fallback, timeout

Navigate:
1. libraries/_index.toon -> "baml" has "llm|structured-output"
2. baml/_index.toon -> common_tasks mentions "error handling"
3. baml/guide/_index.toon -> "error-handling" page has "retry|fallback"
4. baml/guide/pages/error-handling.toon -> Exact info needed
```

### Step 3: Load Only What's Needed

**DO:**
```
@ai-docs/libraries/baml/guide/pages/error-handling.toon  # ~400 tokens
```

**DON'T:**
```
@ai-docs/libraries/baml/full-context.md  # ~15,000 tokens
```

### Step 4: Load Multiple Pages if Needed

For complex tasks, load several specific pages:
```
@ai-docs/libraries/baml/guide/pages/error-handling.toon
@ai-docs/libraries/baml/guide/pages/timeouts.toon
@ai-docs/libraries/baml/reference/pages/retry-policy.toon
```

Still far cheaper than full-context.md.

### Step 5: Use full-context.md Sparingly

Only for:
- Writing comprehensive tutorials
- Major migrations
- Initial deep learning of a library

## Index File Structure

### Category Index (`_index.toon`)
```toon
meta:
  level: category
  name: libraries
  count: 5

items[5]{id,name,description,path,keywords,priority}:
baml,BAML,Structured LLM outputs with type safety,./baml/_index.toon,llm|types|prompts,high
mcp,MCP,Tool integration for AI assistants,./mcp/_index.toon,tools|servers|context,high
```

### Library Index (`{lib}/_index.toon`)
```toon
meta:
  level: library
  name: BAML
  version: 0.70.0
  homepage: https://docs.boundaryml.com

overview: |
  Brief description of what this library does and when to use it.

sections[3]{id,name,path,page_count,when_to_use}:
guide,Guide,./guide/_index.toon,15,Learning concepts and tutorials
reference,Reference,./reference/_index.toon,25,Exact syntax and API details
examples,Examples,./examples/_index.toon,8,Working code samples

common_tasks[5]{task,section,page}:
Define output types,reference,types
Handle errors,guide,error-handling
Stream responses,guide,streaming
```

### Section Index (`{lib}/{section}/_index.toon`)
```toon
meta:
  level: section
  library: baml
  section: guide
  page_count: 15

pages[15]{id,title,path,priority,purpose,keywords}:
introduction,Introduction,./pages/introduction.toon,core,Overview and basic concepts,basics|overview|start
error-handling,Error Handling,./pages/error-handling.toon,important,Retry and fallback strategies,retry|error|fallback
```

### Page Summary (`{lib}/{section}/pages/{page}.toon`)
```toon
meta:
  level: page
  library: baml
  section: guide
  page: error-handling
  source_url: https://docs.boundaryml.com/guide/error-handling
  content_hash: abc123

summary:
  purpose: |
    One to two sentences on what this page teaches.

  key_concepts[5]: concept1|concept2|concept3|concept4|concept5

  gotchas[3]: warning1|warning2|warning3

code_patterns[2]:
  - lang: baml
    desc: What this pattern shows
    code: |
      // Truncated code example

related_pages[2]: ../pages/timeouts.toon|../../reference/pages/retry-policy.toon
```

## Navigation Examples

### Example 1: Specific Feature
```
Task: "Configure BAML streaming"

1. @ai-docs/libraries/baml/_index.toon
   -> common_tasks: "Stream responses" -> guide/streaming

2. @ai-docs/libraries/baml/guide/pages/streaming.toon
   -> Get streaming configuration

Tokens: ~600
```

### Example 2: Unknown Library
```
Task: "Type-safe database access in TypeScript"

1. @ai-docs/libraries/_index.toon
   -> Scan keywords: "prisma" has "database|orm|typescript"

2. @ai-docs/libraries/prisma/_index.toon
   -> Navigate to relevant section

Tokens: ~400 + next level
```

### Example 3: Comprehensive Knowledge
```
Task: "Migrate entire codebase from X to BAML"

1. @ai-docs/libraries/baml/full-context.md
   -> Load everything (correct choice here)

Tokens: ~15,000 (justified for migration)
```

## Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| Load full-context.md for simple question | Navigate to specific page | 95% token waste |
| Guess at file paths | Start at index, drill down | Indexes show what exists |
| Load everything "just in case" | Load what task requires | Wastes context window |
| Skip index, go straight to pages | Read index first | May miss better pages |
