---
name: semantic-code-hunter
description: Use when you need to find code by concept (not just text). Uses Serena MCP for semantic code search across the codebase with minimal token usage. Ideal for understanding architecture, finding authentication flows, or multi-file refactoring.
---

# Semantic Code Hunter (Powered by Serena MCP)

## When to Use
- "Where do we handle X?" questions
- Finding authentication flows
- Locating validation logic
- Multi-file refactoring
- Understanding component relationships
- Finding all usages of a symbol
- Tracing dependencies

## When NOT to Use
- Small projects (< 10 files) - use Grep instead
- Simple text searches - use Grep instead
- Single-file edits - use Read instead
- You already know the exact file

## How It Works
Uses Serena MCP tools for semantic understanding:
- `find_symbol` - Find symbols by concept, not just name
- `find_referencing_symbols` - Trace code relationships
- `find_referencing_code_snippets` - Find where code is used
- `get_symbols_overview` - Understand file structure first
- Token-efficient (70% savings vs traditional search)

## Serena Tools Available

### find_symbol
Find symbols globally or locally with/containing a given name/substring.
```
Example: find_symbol("authenticate")
Finds: authenticateUser, isAuthenticated, AuthenticationService
```

### find_referencing_symbols
Find symbols that reference another symbol.
```
Example: find_referencing_symbols("User", type="function")
Finds: All functions that use the User model
```

### get_symbols_overview
Get high-level overview of symbols in a file.
```
Example: get_symbols_overview("src/services/auth.ts")
Returns: List of classes, functions, exports in file
```

### search_for_pattern
Pattern search across project (when semantic search not sufficient).

## Usage Pattern

### Step 1: Start with Overview
```
If you know the file:
1. get_symbols_overview("path/to/file.ts")
2. Identify relevant symbols
3. Use find_symbol to get details
```

### Step 2: Semantic Search
```
If you don't know the file:
1. find_symbol("concept")
2. Review results
3. Use find_referencing_symbols to trace usage
```

### Step 3: Targeted Retrieval
```
Once you know what you need:
1. Use find_symbol to get specific code
2. Only loads relevant sections (not entire files)
3. Minimal token consumption
```

## Examples

### Example 1: Find Authentication Flow
```
Task: "Where do we handle user authentication?"

Process:
1. find_symbol("auth") - Find auth-related symbols
2. Identify: authenticateUser, validateToken, etc.
3. find_referencing_symbols("authenticateUser") - Where is it called?
4. Trace the flow: Login route → Auth service → JWT generation

Result: Complete authentication flow mapped without reading full files
```

### Example 2: Multi-file Refactoring
```
Task: "Rename User model to Account"

Process:
1. find_symbol("User") - Find User model
2. find_referencing_symbols("User") - Find all usages
3. List all files that need updating
4. Use rename_symbol (Serena tool) for safe refactoring

Result: All references found and renamed consistently
```

### Example 3: Understanding Component Relationships
```
Task: "How does ProjectCard component get data?"

Process:
1. find_symbol("ProjectCard")
2. find_referencing_symbols("ProjectCard") - Where is it used?
3. Trace backwards to data source
4. Understand the data flow

Result: Complete data flow from API → Page → Component
```

## Best Practices

1. **Start broad, narrow down**
   - Use find_symbol with general terms first
   - Filter results by type (function, class, interface)
   - Then get specific symbol details

2. **Use type filters**
   - type="function" - Only functions
   - type="class" - Only classes
   - type="interface" - Only interfaces

3. **Leverage symbol relationships**
   - find_referencing_symbols shows dependencies
   - Helps understand impact of changes
   - Reveals architectural patterns

4. **Combine with traditional tools**
   - Serena for semantic understanding
   - Grep for simple text matches
   - Read for config files, documentation

## Token Efficiency

Traditional approach (without Serena):
1. Read entire files → 10,000+ tokens
2. Multiple grep iterations → 5,000+ tokens
3. Manual analysis → High cognitive load

Serena approach:
1. find_symbol → 200 tokens
2. Targeted retrieval → 500 tokens
3. Total: ~700 tokens (93% savings)

## Troubleshooting

**If Serena returns too many results:**
- Add type filter: type="function"
- Use more specific search term
- Check specific file with get_symbols_overview first

**If Serena returns no results:**
- Check spelling (case-sensitive)
- Try broader search term
- Fall back to Grep for text search
- Ensure Serena is indexed (run: serena project index)

**If symbols missing:**
- Re-index project: serena project index
- Check if file is in .gitignore
- Verify language server supports file type
