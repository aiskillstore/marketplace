---
name: structural-search
description: "Search code by AST structure using ast-grep. Find semantic patterns like function calls, imports, class definitions instead of text patterns. Triggers on: find all calls to X, search for pattern, refactor usages, find where function is used, structural search, ast-grep, sg."
compatibility: "Requires ast-grep (sg) CLI tool. Install: brew install ast-grep (macOS) or cargo install ast-grep (cross-platform)."
allowed-tools: "Bash"
---

# Structural Search

Search code by its abstract syntax tree (AST) structure. Finds semantic patterns that regex cannot match reliably.

## Tools

| Tool | Command | Use For |
|------|---------|---------|
| ast-grep | `sg -p 'pattern'` | AST-aware code search |

## Pattern Syntax

| Pattern | Matches | Example |
|---------|---------|---------|
| `$NAME` | Named identifier | `function $NAME() {}` |
| `$_` | Any single node | `console.log($_)` |
| `$$$` | Zero or more nodes | `function $_($$$) {}` |

## Top 10 Essential Patterns

```bash
# 1. Find console.log calls
sg -p 'console.log($_)'

# 2. Find React hooks
sg -p 'const [$_, $_] = useState($_)'
sg -p 'useEffect($_, [$$$])'

# 3. Find function definitions
sg -p 'function $NAME($$$) { $$$ }'
sg -p 'def $NAME($$$): $$$' --lang python

# 4. Find imports
sg -p 'import $_ from "$_"'
sg -p 'from $_ import $_' --lang python

# 5. Find async patterns
sg -p 'await $_'
sg -p 'async function $NAME($$$) { $$$ }'

# 6. Find error handling
sg -p 'try { $$$ } catch ($_) { $$$ }'
sg -p 'if err != nil { $$$ }' --lang go

# 7. Find potential issues
sg -p '$_ == $_'           # == instead of ===
sg -p 'eval($_)'           # Security risk
sg -p '$_.innerHTML = $_'  # XSS vector

# 8. Preview refactoring
sg -p 'console.log($_)' -r 'logger.info($_)'

# 9. Apply refactoring
sg -p 'var $NAME = $_' -r 'const $NAME = $_' --rewrite

# 10. Search specific language
sg -p 'pattern' --lang typescript
```

## Quick Reference

| Task | Command |
|------|---------|
| Find pattern | `sg -p 'pattern'` |
| Specific language | `sg -p 'pattern' --lang python` |
| Replace (preview) | `sg -p 'old' -r 'new'` |
| Replace (apply) | `sg -p 'old' -r 'new' --rewrite` |
| Show context | `sg -p 'pattern' -A 3` |
| JSON output | `sg -p 'pattern' --json` |
| File list only | `sg -p 'pattern' -l` |
| Count matches | `sg -p 'pattern' --count` |
| Run YAML rules | `sg scan` |

## When to Use

- Finding all usages of a function/method
- Locating specific code patterns (hooks, API calls)
- Preparing for large-scale refactoring
- When regex would match false positives
- Detecting anti-patterns and security issues
- Creating custom linting rules

## Additional Resources

For complete patterns, load:
- `./references/js-ts-patterns.md` - JavaScript/TypeScript patterns
- `./references/python-patterns.md` - Python patterns
- `./references/go-rust-patterns.md` - Go and Rust patterns
- `./references/security-patterns.md` - Security vulnerability detection
- `./references/advanced-usage.md` - YAML rules and tool integration
- `./assets/rule-template.yaml` - Starter template for custom rules
