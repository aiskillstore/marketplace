# Source Analysis Heuristics

How to extract testable units from source files for scaffold generation.

## General Principles

1. **Public API only**: Only scaffold tests for public/exported symbols
2. **Skip internals**: Ignore private functions, internal helpers
3. **Preserve hierarchy**: Test file structure mirrors source structure
4. **Detect signatures**: Extract parameter names for fixture hints

## Language-Specific Patterns

### Python

**Functions**:
```regex
^def\s+([a-z][a-z0-9_]*)\s*\(
```
- Match function definitions starting with lowercase
- Skip names starting with `_` (private)
- Skip dunder methods (`__init__`, `__str__`)

**Classes**:
```regex
^class\s+([A-Z][A-Za-z0-9]*)\s*[:\(]
```
- Match class definitions starting with uppercase
- Extract methods within class scope

**Methods**:
```regex
^\s{4}def\s+([a-z][a-z0-9_]*)\s*\(self
```
- Match method definitions (4-space indent)
- Must have `self` as first parameter
- Skip `_` prefixed methods

### TypeScript/JavaScript

**Exports**:
```regex
^export\s+(async\s+)?function\s+(\w+)
^export\s+const\s+(\w+)\s*=\s*(async\s+)?\(
^export\s+class\s+(\w+)
^export\s+default\s+function\s+(\w+)?
^export\s+default\s+class\s+(\w+)?
```

**Class Methods**:
```regex
^\s{2}(async\s+)?(\w+)\s*\([^)]*\)\s*[:{]
```
- Detect methods at 2-space indent
- Skip constructor, private (#) methods

### Go

**Functions**:
```regex
^func\s+([A-Z][A-Za-z0-9]*)\s*\(
```
- Only exported functions (capital letter)

**Methods**:
```regex
^func\s+\([^)]+\)\s+([A-Z][A-Za-z0-9]*)\s*\(
```
- Exported methods on receivers

**Types**:
```regex
^type\s+([A-Z][A-Za-z0-9]*)\s+(struct|interface)
```

### Rust

**Functions**:
```regex
^pub\s+(async\s+)?fn\s+(\w+)
```

**Structs/Enums**:
```regex
^pub\s+(struct|enum)\s+(\w+)
```

**Impl Methods**:
```regex
^\s+pub\s+(async\s+)?fn\s+(\w+)
```
- Within `impl` blocks

### Dart

**Functions**:
```regex
^(?!_)\w+\s+(\w+)\s*\(
```
- Skip underscore-prefixed (private)

**Classes**:
```regex
^class\s+(\w+)
```
- All classes are public unless underscore-prefixed

## Extraction Algorithm

```
1. Read source file
2. Detect language from extension
3. Apply language regex patterns
4. Build symbol table:
   - name: string
   - type: function | class | method
   - line: number
   - signature: string (parameters)
   - parent: string | null (for methods)
5. Filter out private symbols
6. Return sorted by line number
```

## Output Format

```json
{
  "file": "src/auth/login.py",
  "language": "python",
  "symbols": [
    {
      "name": "authenticate",
      "type": "function",
      "line": 15,
      "signature": "(username: str, password: str) -> User",
      "parent": null
    },
    {
      "name": "UserSession",
      "type": "class",
      "line": 42,
      "signature": "",
      "parent": null
    },
    {
      "name": "refresh",
      "type": "method",
      "line": 55,
      "signature": "(self) -> bool",
      "parent": "UserSession"
    }
  ]
}
```

## Edge Cases

| Case | Handling |
|------|----------|
| Empty file | Skip, log warning |
| Binary file | Skip |
| No public symbols | Skip, log warning |
| Parse error | Skip file, continue others |
| Very large file (>10k lines) | Process but log performance warning |
