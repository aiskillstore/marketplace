---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: code-context-finder
---

# Search Patterns Reference

Common patterns for finding code relationships and context.

## Python Projects

### Import Analysis

```bash
# Find all files importing a module
grep -r "from module_name import" --include="*.py"
grep -r "import module_name" --include="*.py"

# Find relative imports
grep -r "from \. import" --include="*.py"
grep -r "from \.module import" --include="*.py"

# Find wildcard imports (code smell)
grep -r "from .* import \*" --include="*.py"
```

### Function/Class Usage

```bash
# Find function calls
grep -rn "function_name(" --include="*.py"

# Find class instantiations
grep -rn "ClassName(" --include="*.py"

# Find class inheritance
grep -rn "class.*\(.*ClassName" --include="*.py"

# Find decorator usage
grep -rn "@decorator_name" --include="*.py"
```

### Test Discovery

```bash
# Find test files for a module
find . -name "test_*.py" -o -name "*_test.py" | xargs grep -l "module_name"

# Find pytest markers
grep -rn "@pytest.mark" --include="*.py"

# Find test classes
grep -rn "class Test" --include="*.py"
```

## TypeScript/JavaScript Projects

### Import Analysis

```bash
# ES6 imports
grep -r "import.*from ['\"].*module" --include="*.ts" --include="*.tsx"

# Require statements
grep -r "require(['\"].*module" --include="*.js" --include="*.ts"

# Dynamic imports
grep -r "import(['\"]" --include="*.ts" --include="*.tsx"
```

### Component Usage (React)

```bash
# Find component usage
grep -rn "<ComponentName" --include="*.tsx" --include="*.jsx"

# Find hook usage
grep -rn "use[A-Z][a-zA-Z]*(" --include="*.ts" --include="*.tsx"

# Find context usage
grep -rn "useContext(" --include="*.tsx"
```

### Test Discovery

```bash
# Find test files
find . -name "*.test.ts" -o -name "*.spec.ts"

# Find test blocks
grep -rn "describe\|it\|test(" --include="*.test.ts"
```

## Cross-Language Patterns

### Configuration References

```bash
# Find env var usage
grep -rn "process\.env\|os\.environ\|getenv"

# Find config file reads
grep -rn "\.json\|\.yaml\|\.toml\|\.env" --include="*.py" --include="*.ts"
```

### API Endpoints

```bash
# Find route definitions
grep -rn "@app\.route\|@router\.\|app\.get\|app\.post"

# Find API calls
grep -rn "fetch(\|axios\.\|requests\."
```

### Database Queries

```bash
# Find SQL queries
grep -rn "SELECT\|INSERT\|UPDATE\|DELETE" --include="*.py" --include="*.ts"

# Find ORM usage
grep -rn "\.query\|\.filter\|\.find\|\.create"
```

## Knowledge Graph Search Patterns

### By Entity Type

```
# Find all projects
search_nodes("project")

# Find all decisions
search_nodes("decision")

# Find all concepts
search_nodes("concept")

# Find all tools
search_nodes("tool")
```

### By Context

```
# Find by feature name
search_nodes("authentication")
search_nodes("payment")

# Find by technology
search_nodes("postgres")
search_nodes("redis")

# Find by person
search_nodes("joe")
search_nodes("team")
```

### Relationship Queries

```
# View full graph structure
read_graph()

# Open specific related entities
open_nodes(["entity1", "entity2"])
```

## Output Formatting

### Dependency Report

```markdown
## Dependencies for `module_name`

**Imports (what this module uses):**
- `dependency1` - used for X
- `dependency2` - used for Y

**Imported by (what uses this module):**
- `consumer1.py:15` - function call
- `consumer2.py:42` - class instantiation

**Tests:**
- `test_module.py` - 12 tests
- `integration/test_flow.py` - 3 tests
```

### Impact Analysis Report

```markdown
## Impact Analysis: Changing `function_name`

**Direct callers (will break if signature changes):**
- `file1.py:23`
- `file2.py:45`

**Indirect impact (uses callers):**
- `file3.py` imports `file1`
- `file4.py` imports `file2`

**Test coverage:**
- Direct: `test_function.py` (5 tests)
- Integration: `test_flow.py` (2 tests)

**Knowledge graph context:**
- Related decision: "Use X pattern for Y"
- Prior issue: "Fixed similar bug in Z"
```
