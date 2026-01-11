# TOON Format Rules

Complete reference for TOON syntax and constraints.

## Core Syntax

### Key-Value (YAML-like)

```toon
name: John
age: 30
active: true
```

### Arrays with Explicit Length

```toon
tags[3]: red, green, blue
```

### Tabular Data (Primary Use Case)

```toon
# Syntax: name[count]{col1,col2,col3}:
# Followed by 2-space indented CSV-like rows

users[3]{id,name,email}:
  1,John,john@example.com
  2,Jane,jane@example.com
  3,Bob,bob@example.com

```

**CRITICAL**:
- Rows MUST be indented with 2 spaces
- Always add a blank line after the last row

### Nested Arrays in Cells

Use semicolons (NOT commas) for arrays within cells:

```toon
pages[2]{path,keywords,priority}:
  /intro,"overview;basics;start",core
  /api,"reference;methods;types",core

```

### Multi-line Strings

Use quoted strings with `\n` for line breaks:

```toon
description: "This is a multi-line\nstring value that preserves\nline breaks."
```

### Nested Objects

```toon
config:
  database:
    host: localhost
    port: 5432
  cache:
    enabled: true
```

## Format Constraints

**Enforced by official `@toon-format/cli --decode`:**

| Rule | Incorrect | Correct |
|------|-----------|---------|
| No comments | `# comment` | Remove comments entirely |
| No YAML-style lists | `- item` | `key[N]{col}:` + indented rows |
| Rows must be indented | `row,data` | `  row,data` (2 spaces) |
| Arrays need count+cols | `items{a,b}:` | `items[3]{a,b}:` |
| No multiline strings | `key: \|` | `key: "line1\nline2"` |
| No pipe delimiters | `val\|val` | `val,val` or `"val;val"` |
| No commas in cells | `"a,b"` in row | `"a;b"` in row |
| Blank line after arrays | Missing terminator | Blank line after last row |

## Common Patterns

### Index Files

```toon
meta:
  category: libraries
  generated: 2025-01-15T10:30:00Z
  count: 5

items[5]{id,name,description,path,keywords}:
  baml,BAML,Structured LLM outputs,ai-docs/libraries/baml/_index.toon,"llm;types;structured"
  mcp,MCP,Tool integration protocol,ai-docs/libraries/mcp/_index.toon,"tools;context;servers"
  prisma,Prisma,Type-safe database ORM,ai-docs/libraries/prisma/_index.toon,"database;orm;sql"

```

### Page Summaries

```toon
meta:
  library: baml
  page: error-handling
  source_url: https://docs.boundaryml.com/guide/error-handling
  content_hash: a3f2c1d4e5

summary:
  purpose: "Configure retry policies and fallback strategies for resilient LLM calls."

  key_concepts[4]: RetryPolicy,FallbackClient,timeout,exponential backoff

  gotchas[2]: Default timeout 60s may be too short,Retries count against rate limits

code_patterns[1]:
  - lang: baml
    desc: Retry policy configuration
    code: "retry_policy Resilient {\n  max_retries 3\n  strategy exponential\n}"
```

## Token Savings

**JSON** (~280 tokens):
```json
{"pages":[{"path":"/intro","section":"guide","title":"Introduction","priority":"core"},{"path":"/setup","section":"guide","title":"Setup","priority":"core"}]}
```

**TOON** (~100 tokens):
```toon
pages[2]{path,section,title,priority}:
  /intro,guide,Introduction,core
  /setup,guide,Setup,core

```

**Savings: ~64%**

## When to Use TOON

**Good candidates:**
- Uniform tabular data (lists of similar objects)
- Documentation indexes and manifests
- Repeated key-value structures
- Any structured data being fed to LLMs

**Use JSON instead for:**
- Deeply nested structures
- Non-uniform data (mixed schemas)
- Data requiring frequent programmatic manipulation
- Configuration files read by tools
