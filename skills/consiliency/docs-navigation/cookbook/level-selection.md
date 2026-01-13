# Level Selection Guide

Choose the right starting level based on what you already know.

## Decision Matrix

| You Know | Start Here | Example |
|----------|------------|---------|
| Nothing | `ai-docs/_root_index.toon` | "What documentation exists?" |
| Category | `ai-docs/{category}/_index.toon` | "What libraries are tracked?" |
| Library name | `ai-docs/libraries/{lib}/_index.toon` | "What BAML docs exist?" |
| Library + section | `ai-docs/libraries/{lib}/{section}/_index.toon` | "What BAML guide pages?" |
| Exact page | `ai-docs/libraries/{lib}/{section}/pages/{page}.toon` | "BAML error-handling" |

## Level Descriptions

### Level 0: Root Index
```
ai-docs/_root_index.toon
```
- Lists all categories (libraries, guides)
- Use when completely unfamiliar with available docs
- ~100 tokens

### Level 1: Category Index
```
ai-docs/libraries/_index.toon
ai-docs/guides/_index.toon
```
- Lists all items in a category
- Shows descriptions, keywords, priorities
- ~150 tokens

### Level 2: Library Index
```
ai-docs/libraries/{lib}/_index.toon
```
- Overview of a specific library
- Lists sections with page counts
- Shows common_tasks for quick navigation
- ~200 tokens

### Level 3: Section Index
```
ai-docs/libraries/{lib}/{section}/_index.toon
```
- Lists all pages in a section
- Shows purpose and keywords for each page
- ~150 tokens

### Level 4: Page Summary
```
ai-docs/libraries/{lib}/{section}/pages/{page}.toon
```
- Detailed summary of a documentation page
- Contains purpose, key_concepts, gotchas, code_patterns
- ~400 tokens

## Anti-Pattern: Guessing

**Wrong:**
```
# Guessing the path
@ai-docs/libraries/baml/docs/error-handling.toon  # WRONG PATH
```

**Correct:**
```
# Navigate from index
1. @ai-docs/libraries/baml/_index.toon
   -> Shows sections: guide, reference, examples

2. @ai-docs/libraries/baml/guide/_index.toon
   -> Shows pages including error-handling

3. @ai-docs/libraries/baml/guide/pages/error-handling.toon
   -> Correct path found through navigation
```
