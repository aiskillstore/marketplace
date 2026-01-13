---
name: baml-integration
description: "Generic BAML patterns for type-safe LLM prompting. Covers schema design, DTO generation, client wrappers, and cross-language codegen. Framework-agnostic."
---

# BAML Integration Skill

Universal patterns for working with BAML (Boundary ML) in any project. BAML provides type-safe LLM prompting with automatic code generation for Python and TypeScript.

## Design Principle

This skill is **framework-generic**. It provides universal BAML patterns that work in any codebase:
- NOT tailored to CodeGraph-DE, Book-Vetting, or any specific project
- Covers common patterns applicable across all BAML projects
- Specific domain types should go in project-specific skills

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| BAML_SRC | baml_src | Directory containing BAML files |
| AUTO_GENERATE | true | Auto-run baml-cli generate on changes |
| STRICT_TYPES | true | Enforce strict type matching |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order.

1. Understand BAML's role in the project
2. Check existing BAML schema and types
3. Follow type-safe patterns when working with LLMs
4. Keep generated code in sync

## Red Flags - STOP and Reconsider

If you're about to:
- Define LLM prompts without BAML types
- Manually parse LLM output instead of using BAML
- Skip running `baml-cli generate` after schema changes
- Ignore type errors in generated clients

**STOP** -> Define BAML types -> Generate client -> Then proceed

## Workflow

### 1. Understand Project BAML Setup

Check the BAML configuration:

```bash
# Find BAML source directory
find . -name "*.baml" -type f | head -5

# Check BAML client
ls -la baml_client/ || ls -la baml_src/baml_client/

# Check for generator config
cat baml_src/generators.baml 2>/dev/null
```

### 2. Review Existing Types

Before adding new types, review what exists:

```baml
// Common patterns in baml_src/types/

// Enums
enum TaskStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  FAILED
}

// Classes (DTOs)
class UserRequest {
  query string
  context string?
  preferences map<string, string>?
}

class UserResponse {
  answer string
  confidence float
  sources string[]
}
```

### 3. Define New Types

When adding LLM-powered features:

```baml
// 1. Define input type
class MyInput {
  field1 string @description("Clear description")
  field2 int @description("What this number represents")
}

// 2. Define output type
class MyOutput {
  result string
  metadata MyMetadata?
}

class MyMetadata {
  confidence float
  reasoning string
}

// 3. Define the function
function MyFunction(input: MyInput) -> MyOutput {
  client GPT4
  prompt #"
    Given: {{ input.field1 }}
    Count: {{ input.field2 }}

    Provide your analysis.

    {{ ctx.output_format }}
  "#
}
```

### 4. Generate Client

After schema changes:

```bash
# Generate Python and TypeScript clients
baml-cli generate

# Or with specific config
baml-cli generate --config baml_src/generators.baml
```

### 5. Use Generated Client

```python
# Python usage
from baml_client import b

async def process_request(input_data: dict):
    result = await b.MyFunction(
        input=MyInput(
            field1=input_data["query"],
            field2=input_data["count"]
        )
    )
    return result.result
```

```typescript
// TypeScript usage
import { b } from './baml_client';

async function processRequest(inputData: Record<string, unknown>) {
  const result = await b.MyFunction({
    field1: inputData.query as string,
    field2: inputData.count as number
  });
  return result.result;
}
```

## Cookbook

### Schema Synchronization
- IF: Adding or modifying BAML types
- THEN: Read and execute `./cookbook/schema-sync.md`

### DTO Generation
- IF: Creating data transfer objects
- THEN: Read and execute `./cookbook/dto-generation.md`

### Client Wrapper Patterns
- IF: Wrapping BAML client for your service
- THEN: Read and execute `./cookbook/client-wrapper.md`

## Quick Reference

### BAML Type Syntax

| Type | Syntax | Example |
|------|--------|---------|
| String | `string` | `name string` |
| Int | `int` | `count int` |
| Float | `float` | `score float` |
| Boolean | `bool` | `active bool` |
| Optional | `type?` | `nickname string?` |
| Array | `type[]` | `tags string[]` |
| Map | `map<K, V>` | `metadata map<string, string>` |
| Enum | `enum Name` | `status TaskStatus` |
| Class | `class Name` | Custom types |
| Union | `type1 \| type2` | `result string \| Error` |

### Function Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `@description` | Field documentation | `@description("User's email")` |
| `@alias` | JSON key mapping | `@alias("user_id")` |
| `@skip` | Exclude from output | `@skip` |

### Client Selection

```baml
// Define clients in clients.baml
client GPT4 {
  provider openai
  options {
    model "gpt-4-turbo"
    temperature 0.7
  }
}

client Claude {
  provider anthropic
  options {
    model "claude-3-opus"
    max_tokens 4096
  }
}

// Use in functions
function MyFunc(input: Input) -> Output {
  client GPT4  // or Claude
  prompt #"..."#
}
```

### Retry and Fallback

```baml
// Configure retries
client GPT4WithRetry {
  provider openai
  retry_policy {
    max_retries 3
    strategy exponential_backoff
  }
}

// Fallback chain
client_fallback MainClient {
  primary GPT4
  fallback [Claude, GPT35Turbo]
}
```

## Best Practices

### 1. Type Safety First

Always define explicit types:

```baml
// Good: Explicit types
class BookAnalysis {
  title string
  author string
  summary string @description("2-3 sentence summary")
  rating float @description("Rating from 0-5")
  tags string[]
}

// Bad: Using generic types
function AnalyzeBook(text: string) -> string  // Loses type safety
```

### 2. Use Descriptions

Add descriptions for LLM guidance:

```baml
class SearchQuery {
  query string @description("The user's search query in natural language")
  filters SearchFilters? @description("Optional filters to narrow results")
  limit int @description("Maximum number of results to return, default 10")
}
```

### 3. Handle Errors

Define error types:

```baml
class Error {
  code string
  message string
}

function SafeAnalysis(input: Input) -> Output | Error {
  // LLM can return either success or error
}
```

### 4. Version Your Schema

Keep schema versions aligned:

```baml
// baml_src/version.baml
// Schema version: 1.2.0
// Last updated: 2025-12-24

// Document breaking changes in CHANGELOG
```

## Integration Points

### With Schema Alignment

BAML types should align with database models:

```baml
// BAML type
class User {
  id int
  email string
  name string?
}

// Should match SQLAlchemy model
class User(Base):
    id: Mapped[int]
    email: Mapped[str]
    name: Mapped[str | None]
```

### With API Schemas

BAML types can generate API response types:

```baml
// BAML response type
class APIResponse {
  success bool
  data ResponseData
  error string?
}

// Use generated types in FastAPI
@app.post("/analyze")
async def analyze(request: Request) -> APIResponse:
    result = await b.Analyze(request.data)
    return APIResponse(success=True, data=result)
```

### With Frontend Types

Generated TypeScript types work with frontend:

```typescript
// Generated by BAML
import type { BookAnalysis } from './baml_client/types';

// Use in React component
function BookCard({ analysis }: { analysis: BookAnalysis }) {
  return (
    <div>
      <h2>{analysis.title}</h2>
      <p>{analysis.summary}</p>
      <Rating value={analysis.rating} />
    </div>
  );
}
```

## Troubleshooting

### Generation Errors

```bash
# Check BAML syntax
baml-cli check

# Verbose generation
baml-cli generate --verbose
```

### Type Mismatches

If LLM output doesn't match expected type:
1. Check prompt for clarity
2. Add more explicit `@description` hints
3. Consider using union types with Error
4. Enable strict mode in client

### Client Import Issues

```python
# Ensure client is generated
try:
    from baml_client import b
except ImportError:
    # Run: baml-cli generate
    raise RuntimeError("BAML client not generated. Run: baml-cli generate")
```
