# Common ast-grep Patterns

## Contents
- [JavaScript/TypeScript](#javascripttypescript)
- [Python](#python)
- [Go](#go)
- [Rust](#rust)

---

## JavaScript/TypeScript

### Find function calls

```yaml
rule:
  pattern:
    context: $M($$$);
    selector: call_expression
```

### Find class methods

```yaml
rule:
  kind: method_definition
  inside:
    kind: class_body
```

### Replace console.log with logger

**Input:**
```javascript
console.log("debug message");
console.log(data, options);
```

**Rule:**
```yaml
id: replace-console-log
language: JavaScript
rule:
  pattern: console.log($$$ARGS)
fix: logger.log($$$ARGS)
```

**Output:**
```javascript
logger.log("debug message");
logger.log(data, options);
```

### Migrate var to const/let

```yaml
id: no-var
language: JavaScript
rule:
  pattern: var $A = $B
fix: const $A = $B
message: Use const instead of var
```

### Find React useEffect missing deps

```yaml
id: useeffect-missing-deps
language: TypeScript
rule:
  pattern: useEffect($FN, [])
  has:
    pattern: $VAR
    inside:
      kind: arrow_function
    not:
      inside:
        kind: array
```

---

## Python

### Replace print with logging

**Input:**
```python
print("Starting process")
print(f"Value: {value}")
```

**Rule:**
```yaml
id: replace-print
language: Python
rule:
  pattern: print($$$ARGS)
fix: logging.info($$$ARGS)
```

**Output:**
```python
logging.info("Starting process")
logging.info(f"Value: {value}")
```

### Find bare except

```yaml
id: no-bare-except
language: Python
rule:
  kind: except_clause
  not:
    has:
      kind: identifier
message: Avoid bare except, specify exception type
```

---

## Go

### Find error ignoring

```yaml
id: check-error
language: Go
rule:
  pattern: $_, _ = $FUNC($$$)
message: Don't ignore errors
```

### Replace fmt.Println with log

```yaml
id: use-log
language: Go
rule:
  pattern: fmt.Println($$$ARGS)
fix: log.Println($$$ARGS)
```

---

## Rust

### Find unwrap usage

```yaml
id: no-unwrap
language: Rust
rule:
  pattern: $EXPR.unwrap()
message: Consider using ? or expect() instead of unwrap()
severity: warning
```

### Replace println! with tracing

```yaml
id: use-tracing
language: Rust
rule:
  pattern: println!($$$ARGS)
fix: tracing::info!($$$ARGS)
```
