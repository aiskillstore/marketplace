---
name: search-enhancer
description: Enhanced code search with semantic understanding, pattern matching, and intelligent query interpr...
---

# Search Enhancer Skill

Enhanced code search with semantic understanding, pattern matching, and intelligent query interpretation for faster code discovery.

## Instructions

You are a code search and discovery expert. When invoked:

1. **Understand Search Intent**:
   - Parse natural language queries
   - Identify code patterns being searched
   - Infer language and framework context
   - Understand semantic meaning beyond keywords

2. **Multi-Strategy Search**:
   - Text-based grep searches
   - Pattern matching with regex
   - AST-based semantic search
   - Symbol and definition lookup
   - Cross-reference searching

3. **Search Optimization**:
   - Suggest better search terms
   - Use appropriate search tools (grep, ripgrep, ag)
   - Filter by file type and location
   - Exclude irrelevant paths (node_modules, dist)

4. **Present Results**:
   - Rank results by relevance
   - Show context around matches
   - Group related findings
   - Highlight important patterns

## Search Strategies

### 1. Text Search (Basic)
- Simple keyword matching
- Case-insensitive searches
- File name searches
- Path-based filtering

### 2. Pattern Search (Regex)
- Complex pattern matching
- Multi-line patterns
- Lookahead/lookbehind
- Capture groups

### 3. Semantic Search (AST)
- Function/class definitions
- Type references
- Import statements
- Symbol usage

### 4. Contextual Search
- Find similar code patterns
- Locate related functions
- Track dependencies
- Follow call chains

## Usage Examples

```
@search-enhancer Find all React components using useState
@search-enhancer --pattern "API.*endpoint"
@search-enhancer --semantic "function definitions with async"
@search-enhancer --references useAuth
@search-enhancer --similar-to src/utils/helper.js
```

## Search Techniques

### Basic Text Search

```bash
# Search for exact text
grep -r "TODO" src/

# Case-insensitive
grep -ri "error handler" src/

# Show line numbers and context
grep -rn -C 3 "authentication" src/

# Search in specific file types
grep -r --include="*.js" --include="*.ts" "async function" src/

# Exclude directories
grep -r --exclude-dir={node_modules,dist,build} "API_KEY" .
```

### Advanced Pattern Matching

```bash
# Find all function declarations
grep -rE "function\s+\w+\s*\(" src/

# Find all class definitions
grep -rE "class\s+\w+(\s+extends\s+\w+)?" src/

# Find environment variables
grep -rE "process\.env\.\w+" src/

# Find import statements
grep -rE "^import.*from\s+['\"]" src/

# Find API endpoints
grep -rE "(get|post|put|delete)\(['\"][^'\"]*['\"]\)" src/

# Find console logs (for cleanup)
grep -rE "console\.(log|debug|warn|error)" src/ --exclude-dir=node_modules
```

### Ripgrep (Faster Alternative)

```bash
# Install ripgrep: brew install ripgrep (macOS) or apt install ripgrep (Linux)

# Basic search (automatically excludes .gitignore patterns)
rg "useState" src/

# Search with context
rg -C 5 "authentication"

# Search by file type
rg -t js -t ts "async function"

# Search for pattern
rg "function\s+\w+\(" -t js

# Count matches
rg "TODO" --count

# Show only file names
rg "useState" --files-with-matches

# Multi-line search
rg -U "interface.*\{[^}]*\}" -t ts

# Search and replace (preview)
rg "old_name" --replace "new_name" --dry-run
```

### Language-Specific Searches

#### JavaScript/TypeScript

```bash
# Find React components
rg "export (default )?(function|const) \w+" --glob "*.tsx" --glob "*.jsx"

# Find React hooks usage
rg "use(State|Effect|Context|Ref|Memo|Callback)" -t tsx -t jsx

# Find async functions
rg "async (function|\w+\s*=>|\w+\s*\()" -t js -t ts

# Find API calls
rg "(fetch|axios)\(" -t js -t ts

# Find error handling
rg "(try|catch|throw|Error)\s*[\(\{]" -t js -t ts

# Find database queries
rg "(SELECT|INSERT|UPDATE|DELETE).*FROM" -i

# Find environment variables
rg "process\.env\.\w+" -t js -t ts

# Find commented code
rg "^\s*//" src/
```

#### Python

```bash
# Find class definitions
rg "^class \w+(\(.*\))?:" -t py

# Find function definitions
rg "^def \w+\(" -t py

# Find decorators
rg "^@\w+" -t py

# Find imports
rg "^(from|import) " -t py

# Find TODO/FIXME comments
rg "(TODO|FIXME|HACK|XXX):" -t py

# Find print statements (debugging)
rg "print\(" -t py

# Find exception handling
rg "(try|except|raise|finally):" -t py
```

#### Go

```bash
# Find function definitions
rg "^func (\(\w+ \*?\w+\) )?\w+\(" -t go

# Find interface definitions
rg "^type \w+ interface" -t go

# Find struct definitions
rg "^type \w+ struct" -t go

# Find error handling
rg "if err != nil" -t go

# Find goroutines
rg "go (func|\w+)\(" -t go

# Find defer statements
rg "defer " -t go
```

### Semantic Search Patterns

#### Find All Function Definitions

```javascript
// Pattern for JavaScript/TypeScript functions
// Regular functions
function myFunction() {}

// Arrow functions
const myFunction = () => {}

// Method definitions
class MyClass {
  myMethod() {}
}

// Search pattern:
rg "(function \w+\(|const \w+ = \(.*\) =>|^\s*\w+\s*\(.*\)\s*\{)" -t js -t ts
```

#### Find All Class Components (React)

```javascript
// Pattern for React class components
rg "class \w+ extends (React\.)?Component" -t jsx -t tsx
```

#### Find All Custom Hooks (React)

```javascript
// Pattern for custom hooks
rg "^(export )?(const|function) use[A-Z]\w+" -t ts -t tsx
```

#### Find Configuration Files

```bash
# Find all config files
find . -name "*config*" -type f

# Find specific config types
find . -regex ".*\.\(json\|yaml\|yml\|toml\|ini\)$" -type f
```

### Cross-Reference Search

#### Find All Usages of a Function

```bash
# 1. Find function definition
rg "function myFunction\(" -t js

# 2. Find all calls to this function
rg "myFunction\(" -t js

# 3. Find imports of this function
rg "import.*myFunction.*from" -t js
```

#### Find All Implementations of an Interface

```typescript
// Search for interface
rg "interface IUserService" -t ts

// Search for implementations
rg "implements IUserService" -t ts

// Search for usages
rg "IUserService" -t ts
```

### Smart Search Queries

#### Natural Language to Search Pattern

```bash
# Query: "Find all API endpoints"
rg "(app|router)\.(get|post|put|delete|patch)\(" -t js -t ts

# Query: "Find all database models"
rg "(Schema|model|Model)\(" -t js -t ts

# Query: "Find all authentication code"
rg "(auth|authenticate|login|logout|token|jwt)" -i -t js -t ts

# Query: "Find all error handling"
rg "(try|catch|throw|error)" -i --type-add 'src:*.{js,ts,jsx,tsx}' -t src

# Query: "Find all TODOs and FIXMEs"
rg "(TODO|FIXME|HACK|XXX|NOTE):" -i

# Query: "Find hardcoded strings that should be i18n"
rg ">\s*[A-Z][a-z]+" -t jsx -t tsx

# Query: "Find potential SQL injection vulnerabilities"
rg "query.*\+.*req\.(params|query|body)" -t js -t ts

# Query: "Find console logs to remove"
rg "console\.(log|debug|info)" --glob "!**/*.test.*" -t js -t ts
```

## Advanced Search Techniques

### Multi-Pattern Search

```bash
# Search for multiple patterns
rg -e "useState" -e "useEffect" -e "useContext" -t tsx

# Search with AND logic (using pipes)
rg "async" | rg "await"

# Search with OR logic
rg "(async|await)" -t js
```

### Context-Aware Search

```bash
# Show function that contains pattern
rg "useState" -A 20 -B 5 | rg "^(function|const)" -A 25

# Find classes with specific method
rg "class.*extends.*Component" -A 50 | rg "componentDidMount"
```

### Performance Optimization

```bash
# Search only in tracked git files
rg "pattern" $(git ls-files)

# Use parallel processing
rg "pattern" --threads 8

# Search with type filtering
rg "pattern" -t js -t ts -t jsx -t tsx

# Exclude large directories
rg "pattern" --glob "!{node_modules,dist,build,coverage}/**"
```

### Search and Replace

```bash
# Dry run (preview changes)
rg "old_function" --replace "new_function" --dry-run

# Perform replacement (use with caution)
rg "old_function" --replace "new_function" --files-with-matches | xargs sed -i '' 's/old_function/new_function/g'

# Better: Use specific files
rg "old_function" -l | xargs sed -i '' 's/old_function/new_function/g'
```

## Search Result Processing

### Format and Filter Results

```bash
# Get unique filenames
rg "pattern" --files-with-matches | sort | uniq

# Count occurrences per file
rg "pattern" --count-matches

# Show only files with more than N matches
rg "pattern" --count | awk -F: '$2 > 5'

# Create summary report
rg "TODO" --count --sort path > todo_report.txt

# Group by directory
rg "pattern" --files-with-matches | xargs dirname | sort | uniq -c
```

### Export Results

```bash
# Export to JSON
rg "pattern" --json > results.json

# Export with context to file
rg "pattern" -C 3 > search_results.txt

# Create clickable links (for IDEs)
rg "pattern" --vimgrep > quickfix.txt
```

## Search Optimization Tips

### 1. Use Appropriate Scope

```bash
# Bad: Search everything
rg "pattern"

# Good: Search specific directories
rg "pattern" src/ tests/

# Better: Search specific file types
rg "pattern" -t js -t ts src/
```

### 2. Use Smart Case

```bash
# Case-insensitive by default, sensitive if uppercase present
rg "useState"  # Matches: useState, UseState, USESTATE
rg "UseState"  # Matches: UseState only (contains uppercase)
```

### 3. Leverage .gitignore

```bash
# ripgrep automatically respects .gitignore
# To include ignored files:
rg "pattern" --no-ignore

# To include hidden files:
rg "pattern" --hidden
```

### 4. Use File Type Aliases

```bash
# Define custom file type
rg "pattern" --type-add 'app:*.{js,ts,jsx,tsx}' -t app

# Or in config file (~/.ripgreprc)
--type-add=app:*.{js,ts,jsx,tsx}
```

## IDE Integration

### VS Code Search

```json
{
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true,
    "**/.git": true,
    "**/coverage": true
  },
  "search.useRipgrep": true,
  "search.followSymlinks": false
}
```

### Search Shortcuts

- Cmd/Ctrl + Shift + F: Global search
- Cmd/Ctrl + P: Quick file open
- Cmd/Ctrl + T: Go to symbol
- Cmd/Ctrl + Shift + O: Go to symbol in file

## Common Search Patterns Library

### Security Patterns

```bash
# Find hardcoded secrets
rg "password\s*=\s*['\"]" -i

# Find API keys
rg "(api[_-]?key|token|secret)\s*[:=]\s*['\"][^'\"]{10,}" -i

# Find SQL concatenation (potential injection)
rg "SELECT.*\+.*" -t js -t py

# Find eval usage (security risk)
rg "eval\(" -t js
```

### Performance Patterns

```bash
# Find synchronous file operations
rg "fs\.(readFileSync|writeFileSync)" -t js

# Find blocking operations
rg "(readFileSync|execSync|sync\(\))" -t js

# Find expensive operations in loops
rg "for.*\{" -A 10 | rg "(await|fetch|query)"

# Find N+1 query patterns
rg "\.map.*await" -t js -t ts
```

### Code Quality Patterns

```bash
# Find magic numbers
rg "\b\d{2,}\b" -t js | rg -v "(test|spec)"

# Find long functions (heuristic)
rg "function \w+\(" -A 100 | rg "^}" | rg -c "A 100"

# Find duplicate code (similar lines)
rg "^\s*const \w+ = " | sort | uniq -d

# Find commented code
rg "^\s*//.*[{}\(\);]" -t js -t ts
```

### Dependency Analysis

```bash
# Find all npm package imports
rg "from ['\"](?![\./])" -t js -t ts

# Find deprecated API usage
rg "(componentWillMount|componentWillReceiveProps)" -t jsx -t tsx

# Find specific library usage
rg "import.*from ['\"](lodash|moment|jquery)" -t js
```

## Search Result Analysis

### Generate Reports

```bash
# TODO report by file
rg "TODO:" --count | sort -t: -k2 -nr > todo_by_count.txt

# Complexity indicators
rg "if|else|switch|for|while" --count | awk -F: '$2 > 20' > complex_files.txt

# Import analysis
rg "^import" --count | sort -t: -k2 -nr > imports_by_file.txt

# Test coverage gaps (files without tests)
comm -23 <(find src -name "*.ts" | sort) <(find tests -name "*.test.ts" | sed 's/tests/src/' | sed 's/\.test//' | sort)
```

## Best Practices

### Search Strategy
- **Start broad, narrow down**: Begin with simple search, add filters
- **Use appropriate tools**: ripgrep for text, AST tools for semantic
- **Leverage file types**: Filter by extension to reduce noise
- **Exclude build artifacts**: Always exclude dist, node_modules, etc.

### Performance
- **Limit scope**: Search specific directories when possible
- **Use patterns**: Regex can be faster than multiple searches
- **Cache results**: Save frequent searches
- **Parallel execution**: Use tools that support multi-threading

### Result Quality
- **Show context**: Use -A/-B/-C flags for surrounding lines
- **Rank by relevance**: Sort by match count or recency
- **Filter noise**: Exclude test files, mocks, fixtures when needed
- **Group related**: Organize results by file or directory

## Notes

- Always exclude build directories (node_modules, dist, build)
- Use `.gitignore` patterns for automatic exclusion
- Combine text and semantic search for best results
- Regular expressions can be slow on large codebases
- Cache frequently used search patterns
- Consider using specialized tools (ag, ack) for specific needs
- IDE built-in search is often sufficient for small projects
- For large codebases, consider code indexing tools
- Document common search patterns for team
