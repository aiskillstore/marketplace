# ast-grep Rule Syntax Reference

## Contents
- [Atomic Rules](#atomic-rules)
- [Composite Rules](#composite-rules)
- [Relational Rules](#relational-rules)
- [Pattern Syntax](#pattern-syntax)
- [Constraints](#constraints)
- [Fix & Transform](#fix--transform)
- [Utility Rules](#utility-rules)

---

## Atomic Rules

### `pattern`

Matches syntax node using pattern syntax.

```yaml
rule:
  pattern: console.log($GREETING)
```

**Pattern object** for ambiguous code:

```yaml
rule:
  pattern:
    context: 'class A { $FIELD = $INIT }'
    selector: field_definition
```

### `kind`

Matches AST node type by tree-sitter name.

```yaml
rule:
  kind: field_definition
```

ESQuery-style selector (v0.39.1+):
```yaml
rule:
  kind: call_expression > identifier
```

### `regex`

Matches node text with Rust regex. **Always combine with other rules** for performance:

```yaml
rule:
  kind: identifier
  regex: "^debug"
```

### `nthChild`

Matches nodes by position (1-based, CSS-style).

```yaml
rule:
  kind: number
  nthChild: 2
```

Advanced:
```yaml
rule:
  nthChild:
    position: 2n+1
    reverse: true
    ofRule:
      kind: function_declaration
```

### `range`

Matches by source code position.

```yaml
rule:
  range:
    start: {line: 0, column: 0}
    end: {line: 1, column: 5}
```

---

## Composite Rules

### `all`

Match nodes satisfying ALL rules.

```yaml
rule:
  all:
    - pattern: console.log('Hello World')
    - kind: expression_statement
```

### `any`

Match nodes satisfying ANY rule.

```yaml
rule:
  any:
    - pattern: var $A = $B
    - pattern: const $A = $B
    - pattern: let $A = $B
```

### `not`

Negate a rule.

```yaml
rule:
  pattern: console.log($GREETING)
  not:
    pattern: console.log('Hello World')
```

### `matches`

Reference a utility rule.

```yaml
rule:
  matches: utility-rule-name
```

---

## Relational Rules

### `has`

Node must have matching child.

```yaml
rule:
  kind: function_declaration
  has:
    kind: return_statement
```

### `inside`

Node must be inside matching ancestor.

```yaml
rule:
  pattern: this.$PROP
  inside:
    kind: class_body
```

### `follows`

Node must follow matching sibling.

```yaml
rule:
  pattern: $VAL
  follows:
    kind: property_identifier
```

### `precedes`

Node must precede matching sibling.

```yaml
rule:
  pattern: return $VAL
  precedes:
    pattern: $A = $VAL
```

### `direct`

Limit to immediate children.

```yaml
rule:
  kind: class_body
  has:
    direct: true
    kind: field_definition
```

### `stopBy`

Stop searching at matching node.

```yaml
rule:
  pattern: $EXP
  inside:
    kind: function_body
    stopBy:
      kind: return_statement
```

---

## Pattern Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `$NAME` | Match exactly one AST node | `console.log($GREETING)` |
| `$$$ARGS` | Match zero or more nodes | `console.log($$$ARGS)` |
| `$_NAME` | Non-capturing (independent match) | `$_FUNC($_FUNC)` |
| `$$VAR` | Capture unnamed nodes | `async function $$NAME() {}` |

**Variable Capturing**: Same name = same content.

```yaml
pattern: $A == $A  # matches: a == a, 1 == 1; not: a == b
```

---

## Constraints

Filter meta-variables after pattern match.

```yaml
rule:
  pattern: console.log($ARG)
constraints:
  ARG:
    kind: number
```

---

## Fix & Transform

### Simple Fix

```yaml
rule:
  pattern: console.log($$$ARGS)
fix: logger.log($$$ARGS)
```

### Transform

```yaml
transform:
  NEW_VAR:
    replace:
      source: $OLD
      replace: debug(?<TAIL>.*)
      by: release$TAIL
fix: $NEW_VAR
```

**String style** (v0.38.3+):
```yaml
transform:
  LIST: substring($GEN, startChar=1, endChar=-1)
  KEBABED: convert($OLD_FN, toCase=kebabCase)
```

### FixConfig

For list items with commas.

```yaml
fix:
  template: ''
  expandEnd: {regex: ','}
```

---

## Utility Rules

Define reusable rules locally:

```yaml
utils:
  match-function:
    any:
      - kind: function_declaration
      - kind: arrow_function

rule:
  matches: match-function
```
