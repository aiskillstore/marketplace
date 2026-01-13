# Keyword Search Pattern

Use when you're uncertain which library or page has what you need.

## When to Use

- You're not sure which library covers your topic
- You need to find relevant documentation for a concept
- You're exploring what's available

## Steps

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

## Example: Structured Output Parsing

Task: Find documentation for "structured output parsing"

```
1. @ai-docs/libraries/_index.toon
   -> BAML: "Structured LLM outputs with type safety" [match]
   -> MCP: "Tool integration protocol" [no match]

2. @ai-docs/libraries/baml/_index.toon
   -> Confirms: type system, parsing, validation

3. Load relevant BAML pages
```

## Keyword Matching Tips

- Look for synonyms (error/failure, retry/fallback)
- Check `keywords` fields in indexes
- Scan `description` and `purpose` fields
- Multiple libraries may be relevant - check all matches

## Token Budget

- Category index: ~150 tokens
- Each library index checked: ~200 tokens
- Final page summaries: ~400 tokens each
- **Typical total: 800-1500 tokens**
