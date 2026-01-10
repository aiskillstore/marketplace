# Context7 MCP Tools

*2 tools available*

## `resolve-library-id`

Resolves a package/product name to a Context7-compatible library ID and returns a list of matching libraries.

You MUST call this function before 'get-library-docs' to obtain a valid Context7-compatible library ID UNLESS the user explicitly provides a library ID in the format '/org/project' or '/org/project/version' in their query.

### Selection Process

1. Analyze the query to understand what library/package the user is looking for
2. Return the most relevant match based on:
   - Name similarity to the query (exact matches prioritized)
   - Description relevance to the query's intent
   - Documentation coverage (prioritize libraries with higher Code Snippet counts)
   - Source reputation (consider libraries with High or Medium reputation more authoritative)
   - Benchmark Score: Quality indicator (100 is the highest score)

### Parameters

- **`libraryName`** (`string`) *(required)*: Library name to search for and retrieve a Context7-compatible library ID

### Response Format

Returns a list of matching libraries with:
- Title
- Context7-compatible library ID (e.g., `/reactjs/react.dev`)
- Code Snippets count
- Source Reputation (High/Medium/Low)
- Benchmark Score
- Description

### Examples

```bash
# Find React library
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t resolve-library-id \
  -p '{"libraryName": "react"}'

# Find Next.js library
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t resolve-library-id \
  -p '{"libraryName": "next.js"}'

# Find MongoDB library
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t resolve-library-id \
  -p '{"libraryName": "mongodb"}'
```

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "libraryName": {
      "type": "string",
      "description": "Library name to search for and retrieve a Context7-compatible library ID."
    }
  },
  "required": ["libraryName"]
}
```
</details>

## `get-library-docs`

Fetches up-to-date documentation for a library. You must call 'resolve-library-id' first to obtain the exact Context7-compatible library ID required to use this tool, UNLESS the user explicitly provides a library ID in the format '/org/project' or '/org/project/version' in their query.

Use mode='code' (default) for API references and code examples, or mode='info' for conceptual guides, narrative information, and architectural questions.

### Parameters

- **`context7CompatibleLibraryID`** (`string`) *(required)*: Exact Context7-compatible library ID (e.g., '/mongodb/docs', '/vercel/next.js', '/supabase/supabase', '/vercel/next.js/v14.3.0-canary.87') retrieved from 'resolve-library-id' or directly from user query in the format '/org/project' or '/org/project/version'

- **`topic`** (`string`) *(optional)*: Topic to focus documentation on (e.g., 'hooks', 'routing')

- **`mode`** (`string`) *(optional, default: "code")*: Documentation mode
  - `code`: API references and code examples (default)
  - `info`: Conceptual guides, narrative information, and architectural questions

- **`page`** (`integer`) *(optional, default: 1)*: Page number for pagination (start: 1, default: 1). If the context is not sufficient, try page=2, page=3, page=4, etc. with the same topic. Range: 1-10

### Examples

```bash
# Get React hooks documentation (code mode)
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/reactjs/react.dev", "topic": "hooks", "mode": "code", "page": 1}'

# Get conceptual information about Next.js routing
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/vercel/nextjs.org", "topic": "routing", "mode": "info"}'

# Get MongoDB aggregation examples
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/mongodb/docs", "topic": "aggregation", "mode": "code"}'

# Get additional pages for more details
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/reactjs/react.dev", "topic": "hooks", "mode": "code", "page": 2}'
```

<details>
<summary>Full Schema</summary>

```json
{
  "type": "object",
  "properties": {
    "context7CompatibleLibraryID": {
      "type": "string",
      "description": "Exact Context7-compatible library ID (e.g., '/mongodb/docs', '/vercel/next.js', '/supabase/supabase', '/vercel/next.js/v14.3.0-canary.87') retrieved from 'resolve-library-id' or directly from user query in the format '/org/project' or '/org/project/version'."
    },
    "topic": {
      "type": "string",
      "description": "Topic to focus documentation on (e.g., 'hooks', 'routing')."
    },
    "mode": {
      "type": "string",
      "enum": ["code", "info"],
      "default": "code",
      "description": "Documentation mode: 'code' for API references and code examples (default), 'info' for conceptual guides, narrative information, and architectural questions."
    },
    "page": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "default": 1,
      "description": "Page number for pagination (start: 1, default: 1). If the context is not sufficient, try page=2, page=3, page=4, etc. with the same topic."
    }
  },
  "required": ["context7CompatibleLibraryID"]
}
```
</details>

## Usage Patterns

### Pattern 1: Unknown Library

When you don't know the exact library ID:

```bash
# Step 1: Resolve library name
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t resolve-library-id -p '{"libraryName": "express"}'

# Step 2: Use returned ID to fetch docs
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/expressjs/expressjs.com", "topic": "middleware"}'
```

### Pattern 2: Known Library ID

When you know the library ID:

```bash
# Direct fetch (skip resolve step)
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/reactjs/react.dev", "topic": "useState"}'
```

### Pattern 3: Exploring Multiple Topics

```bash
# Get overview first
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/prisma/docs", "topic": "getting started", "mode": "info"}'

# Then drill into specifics
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/prisma/docs", "topic": "queries", "mode": "code"}'
```

### Pattern 4: Pagination for Deep Research

```bash
# Get first page
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/reactjs/react.dev", "topic": "hooks", "page": 1}'

# Get additional pages as needed
python3 scripts/mcp-client.py call -s "npx -y @upstash/context7-mcp" \
  -t get-library-docs \
  -p '{"context7CompatibleLibraryID": "/reactjs/react.dev", "topic": "hooks", "page": 2}'
```

## Common Library IDs

Quick reference for popular libraries:

| Library | Context7 ID |
|---------|-------------|
| React | `/reactjs/react.dev` |
| Next.js | `/vercel/nextjs.org` |
| Express | `/expressjs/expressjs.com` |
| MongoDB | `/mongodb/docs` |
| Prisma | `/prisma/docs` |
| Vue | `/vuejs/docs` |
| Svelte | `/sveltejs/svelte.dev` |
| FastAPI | `/tiangolo/fastapi` |
| Django | `/django/docs` |

## Tips

1. **Library Resolution**: Always use `resolve-library-id` first unless you have the exact ID
2. **Mode Selection**: Use `code` mode for examples, `info` mode for concepts
3. **Topic Specificity**: More specific topics yield better results
4. **Pagination**: If results are insufficient, try `page: 2` or refine the topic
5. **Fallback**: If no results, try broader topics or switch modes
