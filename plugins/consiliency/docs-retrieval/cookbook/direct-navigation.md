# Direct Navigation Pattern

Use when you know the library and topic you need.

## When to Use

- You know the library name (e.g., "BAML", "Prisma", "MCP")
- You know approximately what topic you need (e.g., "error handling", "streaming")
- You want the most efficient path to the information

## Steps

```
1. @ai-docs/libraries/{library}/_index.toon
   -> Read overview and common_tasks

2. Find matching task or section
   -> Note the page path

3. @ai-docs/libraries/{library}/{section}/pages/{page}.toon
   -> Get detailed summary with gotchas and patterns
```

## Example: BAML Retry Configuration

```
1. @ai-docs/libraries/baml/_index.toon
   -> common_tasks: "Handle errors gracefully" -> guide/error-handling

2. @ai-docs/libraries/baml/guide/pages/error-handling.toon
   -> RetryPolicy syntax, gotchas about timeouts
```

## Token Budget

- Library index: ~200 tokens
- Page summary: ~400 tokens
- **Total: ~600 tokens**

## Tips

- Always check `common_tasks` in the library index first
- The `gotchas` field often contains the most valuable information
- Code patterns are copy-paste ready
