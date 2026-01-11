---
name: ast-grep-rule-crafter
description: Write AST-based code search and rewrite rules using ast-grep YAML. Create linting rules, code modernizations, and API migrations with auto-fix. Use when the user mentions ast-grep, tree-sitter patterns, code search rules, lint rules with YAML, AST matching, or code refactoring patterns.
---

# ast-grep Rule Crafter

ast-grep uses tree-sitter to parse code into AST, enabling precise pattern matching. Rules are defined in YAML for linting, searching, and rewriting code.

## Quick Start

```yaml
id: no-console-log
language: JavaScript
rule:
  pattern: console.log($$$ARGS)
fix: logger.log($$$ARGS)
message: Replace console.log with logger
```

## Project Configuration

项目级扫描需要 `sgconfig.yml` 配置文件：

```yaml
# sgconfig.yml (项目根目录)
ruleDirs:
  - rules          # 规则目录，递归加载所有 .yml 文件
```

典型项目结构：

```
my-project/
├── sgconfig.yml
├── rules/
│   ├── no-console.yml
│   └── custom/
│       └── team-rules.yml
└── src/
```

运行项目扫描：

```bash
ast-grep scan              # 自动查找 sgconfig.yml
ast-grep scan --config path/to/sgconfig.yml  # 指定配置
```

> **注意**: `ast-grep scan` 命令必须有 `sgconfig.yml`，而 `ast-grep run -p` 可单独使用。

## Rule Workflow

### Lint Rule (常见)

只检查不修复，用于 CI/编辑器提示：

```yaml
# rules/no-console-log.yml
id: no-console-log
language: JavaScript
severity: warning
message: Avoid console.log in production code
rule:
  pattern: console.log($$$ARGS)
```

验证：

```bash
ast-grep scan -r rules/no-console-log.yml src/
```

### Rewrite Rule (可选)

需要自动修复时添加 `fix`：

```yaml
id: no-console-log
language: JavaScript
severity: warning
message: Replace console.log with logger
rule:
  pattern: console.log($$$ARGS)
fix: logger.log($$$ARGS)
```

应用修复：

```bash
ast-grep scan -r rules/no-console-log.yml --update-all src/
```

### 开发流程

```
- [ ] 1. 用 CLI 探索 pattern: ast-grep -p 'pattern' src/
- [ ] 2. 创建规则文件 (.yml)
- [ ] 3. 验证: ast-grep scan -r rule.yml src/
- [ ] 4. 如有误报 → 添加 constraints → 重新验证
```

调试 AST 结构：

```bash
ast-grep -p 'console.log($ARG)' --debug-query ast
```

## Essential Syntax

| Element | Syntax | Example |
|---------|--------|---------|
| Single node | `$VAR` | `console.log($MSG)` |
| Multiple nodes | `$$$ARGS` | `fn($$$ARGS)` |
| Same content | Use same name | `$A == $A` |
| Non-capturing | `$_VAR` | `$_FN($_FN)` |

## Core Rules Quick Reference

| Type | Purpose | Example |
|------|---------|---------|
| `pattern` | Match code structure | `pattern: if ($COND) {}` |
| `kind` | Match AST node type | `kind: function_declaration` |
| `all` | Match ALL conditions | `all: [pattern: X, kind: Y]` |
| `any` | Match ANY condition | `any: [pattern: var $A, pattern: let $A]` |
| `not` | Exclude matches | `not: {pattern: safe_call()}` |
| `has` | Must have child | `has: {kind: return_statement}` |
| `inside` | Must be in ancestor | `inside: {kind: class_body}` |

## Detailed References

**Complete syntax guide**: See [references/rule-syntax.md](references/rule-syntax.md)
- Atomic rules (pattern, kind, regex, nthChild, range)
- Composite rules (all, any, not, matches)
- Relational rules (has, inside, follows, precedes)
- Transform and fixConfig

**Language-specific patterns**: See [references/common-patterns.md](references/common-patterns.md)
- JavaScript/TypeScript examples
- Python examples
- Go and Rust examples

## Supported Languages

Bash, C, Cpp, CSharp, Css, Elixir, Go, Haskell, Hcl, Html, Java, JavaScript, Json, Kotlin, Lua, Nix, Php, Python, Ruby, Rust, Scala, Solidity, Swift, Tsx, TypeScript, Yaml
