# Keyword Matching Guide

How to find the right documentation by matching task keywords against index keywords.

## Index Keywords Structure

Each index contains searchable fields:

```toon
items[N]{id,name,description,path,keywords,priority}:
baml,BAML,Structured LLM outputs,./baml/_index.toon,llm|types|prompts,high
```

**Searchable fields:**
- `description` - Plain text description
- `keywords` - Pipe-separated terms (llm|types|prompts)
- `purpose` - What this item is for

## Matching Strategy

### Step 1: Extract Keywords from Task

```
Task: "Handle LLM retry failures with fallback"

Keywords to find:
- Primary: retry, failure, fallback
- Secondary: error, llm, timeout
- Synonyms: recover, resilient, backup
```

### Step 2: Scan Category Index

```
@ai-docs/libraries/_index.toon

Match against library descriptions:
- BAML: "Structured LLM outputs" -> LLM match
- MCP: "Tool integration" -> no match
```

### Step 3: Drill Into Matches

```
@ai-docs/libraries/baml/_index.toon

Check common_tasks:
- "Handle errors gracefully" -> error match!
- Points to: guide/error-handling
```

### Step 4: Verify at Page Level

```
@ai-docs/libraries/baml/guide/pages/error-handling.toon

Keywords: retry|error|fallback|timeout
-> All primary keywords match!
```

## Example: Finding Streaming Documentation

```
Task: "Implement streaming responses from LLM"

Keywords: streaming, stream, response, llm, realtime

1. @ai-docs/libraries/_index.toon
   -> BAML mentions "LLM" -> check it

2. @ai-docs/libraries/baml/_index.toon
   -> common_tasks: "Stream responses" -> guide/streaming

3. @ai-docs/libraries/baml/guide/pages/streaming.toon
   -> Exact match found
```

## Tips

- Use synonyms when exact matches fail
- Check `common_tasks` in library indexes first
- The `priority` field indicates importance (core > important > supplemental)
- Multiple libraries may match - check all before deciding
