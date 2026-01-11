# Advanced Usage

Advanced ast-grep features including YAML rules, output formatting, and tool integration.

## Context and Output Options

```bash
# Show surrounding lines (context)
sg -p 'console.log($_)' -A 3    # 3 lines after
sg -p 'console.log($_)' -B 3    # 3 lines before
sg -p 'console.log($_)' -C 3    # 3 lines both

# JSON output (for scripting)
sg -p 'console.log($_)' --json

# File names only
sg -p 'TODO' -l
sg -p 'TODO' --files-with-matches

# Count matches
sg -p 'console.log($_)' --count

# Report format
sg -p 'console.log($_)' --report
```

## Combining with Other Tools

```bash
# Find and process with jq
sg -p 'fetch($_)' --json | jq '.matches[].file'

# Find in specific files
fd -e ts | xargs sg -p 'useState($_)'

# Interactive selection with fzf
sg -p 'console.log($_)' -l | fzf | xargs code

# Parallel search in large codebases
fd -e ts -e tsx | xargs -P 4 sg -p 'useEffect($_)'

# Combine with ripgrep for pre-filtering
rg -l 'useState' | xargs sg -p 'const [$_, $_] = useState($_)'
```

## YAML Rules (Reusable Patterns)

Create `.ast-grep.yml` or `sgconfig.yml` in project root:

```yaml
# Single rule file
id: no-console-log
language: typescript
rule:
  pattern: console.log($$$)
message: Remove console.log before committing
severity: warning
```

### Multiple Rules

Create `rules/` directory with individual files:

```yaml
# rules/no-console.yml
id: no-console-log
language: typescript
rule:
  pattern: console.log($$$)
message: Remove console.log statements
severity: warning
fix: "// removed: console.log"

---
# rules/prefer-const.yml
id: prefer-const
language: typescript
rule:
  pattern: var $NAME = $_
message: Use const instead of var
severity: error
fix: const $NAME = $_
```

### Rule Configuration

```yaml
id: rule-identifier
language: typescript  # js, python, go, rust, etc.

rule:
  # Match a pattern
  pattern: console.log($$$)

  # Or use multiple conditions
  any:
    - pattern: console.log($$$)
    - pattern: console.warn($$$)

  # Negative patterns
  not:
    pattern: console.error($$$)

  # Inside specific context
  inside:
    pattern: function $_ { $$$ }

message: "Human-readable warning message"
severity: error | warning | info | hint
note: "Additional context for the developer"

# Optional auto-fix
fix: "replacement code using $METAVARS"

# Optional metadata
metadata:
  category: best-practice
  references:
    - https://example.com/rule-explanation
```

### Running Rules

```bash
# Scan with all rules
sg scan

# Scan specific directory
sg scan src/

# Scan with specific config
sg scan --config sgconfig.yml

# Test rules
sg test

# Auto-fix issues
sg scan --fix
```

## Project Configuration

Create `sgconfig.yml` in project root:

```yaml
# sgconfig.yml
ruleDirs:
  - rules/         # Directory containing rule files
  - .ast-grep/     # Alternative rules location

testConfigs:
  - testDir: rules/tests/

# Ignore patterns
ignores:
  - "**/node_modules/**"
  - "**/dist/**"
  - "**/*.min.js"

# Language-specific settings
languageGlobs:
  typescript:
    - "**/*.ts"
    - "**/*.tsx"
  python:
    - "**/*.py"
```

## Rule Testing

Create test files for rules:

```yaml
# rules/tests/no-console-test.yml
id: no-console-log
valid:
  - const x = 1;
  - logger.info("message");
invalid:
  - console.log("test");
  - console.log(variable);
```

Run tests:
```bash
sg test
```

## Integration Patterns

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ast-grep
        name: ast-grep security
        entry: sg scan --fail-on warning
        language: system
        types: [file]
```

### CI/CD Pipeline

```yaml
# GitHub Actions
- name: AST Security Scan
  run: |
    sg scan --json > ast-grep-results.json
    if [ $(jq '.diagnostics | length' ast-grep-results.json) -gt 0 ]; then
      echo "Security issues found"
      jq '.diagnostics[]' ast-grep-results.json
      exit 1
    fi
```

### VS Code Integration

Install `ast-grep.ast-grep-vscode` extension for:
- Real-time pattern matching
- Inline warnings from rules
- Quick fixes

## Performance Tips

```bash
# Limit to specific directories
sg -p 'pattern' src/ lib/

# Use file type filters
sg -p 'pattern' --lang typescript

# Combine with fd for speed
fd -e ts -x sg -p 'pattern' {}

# Parallel processing
find . -name "*.ts" -print0 | xargs -0 -P 4 sg -p 'pattern'
```
