# Technical Debt Identification

Systematically identify and categorize technical debt.

## Debt Categories

### 1. Code Debt

```bash
# Find TODOs, FIXMEs, HACKs
grep -rn "TODO\|FIXME\|HACK\|XXX\|TEMP" --include="*.ts" --include="*.js"

# Find commented-out code
grep -rn "^[[:space:]]*//.*function\|^[[:space:]]*//.*const\|^[[:space:]]*//.*class" --include="*.ts"

# Find magic numbers/strings
grep -rn "[^a-zA-Z]\"[a-zA-Z0-9_-]\{10,\}\"" --include="*.ts" | head -10
```

### 2. Test Debt

```bash
# Find files without tests
find src -name "*.ts" | while read f; do
  test_file=$(echo "$f" | sed 's/\.ts$/.test.ts/')
  [ ! -f "$test_file" ] && echo "Missing test: $f"
done

# Check test coverage (if configured)
npm run test:coverage 2>/dev/null | grep -E "Statements|Branches"
```

### 3. Dependency Debt

```bash
# Outdated packages (Node.js)
npm outdated

# Security vulnerabilities
npm audit

# Check for deprecated packages
npm ls 2>&1 | grep -i "deprecated"
```

### 4. Documentation Debt

```bash
# Find functions without comments
grep -B2 "^export function\|^export const.*=" --include="*.ts" | \
  grep -v "^\*\|^//" | head -20

# Check for README
[ ! -f README.md ] && echo "Missing README"

# Check for API docs
ls docs/ api-docs/ 2>/dev/null || echo "No docs directory"
```

### 5. Architecture Debt

```bash
# Find large files (potential god classes)
find . -name "*.ts" -exec wc -l {} \; | sort -rn | head -20

# Find circular dependencies
npx madge --circular --extensions ts src/ 2>/dev/null

# Find files with too many imports
for f in src/**/*.ts; do
  count=$(grep -c "^import" "$f" 2>/dev/null || echo 0)
  [ "$count" -gt 15 ] && echo "$f: $count imports"
done
```

## Anti-Pattern Detection

### God Class

```bash
# Files over 500 lines
find . -name "*.ts" -exec wc -l {} \; | awk '$1 > 500' | sort -rn
```

### Long Methods

```bash
# Functions over 50 lines (rough heuristic)
# Manual inspection often needed
```

### Too Many Parameters

```bash
# Functions with many parameters
grep -rn "function.*,.*,.*,.*,.*," --include="*.ts" | head -10
```

### Deep Nesting

```bash
# Files with deep indentation
grep -rn "^                " --include="*.ts" | wc -l
```

### Duplicate Code

```bash
# Similar blocks (requires jscpd)
npx jscpd src/ --min-lines 10 --min-tokens 50
```

## Severity Classification

| Severity | Criteria | Examples | Action |
|----------|----------|----------|--------|
| **Critical** | Blocks development, security risk | Vulnerability, broken build | Fix immediately |
| **High** | Significant pain, slows team | God class, circular deps | Fix in next sprint |
| **Medium** | Noticeable friction | Missing tests, outdated deps | Plan to address |
| **Low** | Minor inconvenience | TODOs, style issues | Address opportunistically |

## Output Format

```markdown
## Technical Debt Inventory

### Summary

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Code | 0 | 3 | 12 | 25 |
| Test | 0 | 5 | 8 | 0 |
| Dependencies | 2 | 4 | 10 | 15 |
| Documentation | 0 | 1 | 5 | 10 |
| Architecture | 0 | 2 | 3 | 5 |

### Critical Issues

| Issue | Location | Impact |
|-------|----------|--------|
| Security vulnerability | `package.json` | Potential data breach |

### High Priority

| Issue | Location | Impact |
|-------|----------|--------|
| God class | `src/services/UserService.ts` (800 lines) | Hard to maintain |
| Circular dependency | `auth.ts ↔ user.ts` | Import issues |
| Missing critical tests | `src/api/` (20% coverage) | Risk of regressions |

### Recommended Actions

1. **Immediate**: Update vulnerable dependencies
2. **This Sprint**: Split UserService into smaller services
3. **Next Sprint**: Add tests for API routes
4. **Backlog**: Address TODOs (25 items)
```
