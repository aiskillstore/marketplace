# Go and Rust Patterns

Complete pattern library for ast-grep in Go and Rust.

## Go Patterns

### Function Declarations

```bash
# Find function declarations
sg -p 'func $NAME($$$) $_ { $$$ }' --lang go

# Find functions without return type
sg -p 'func $NAME($$$) { $$$ }' --lang go

# Find method declarations
sg -p 'func ($_ $_) $NAME($$$) $_ { $$$ }' --lang go

# Find pointer receiver methods
sg -p 'func ($_ *$_) $NAME($$$) $_ { $$$ }' --lang go
```

### Type Definitions

```bash
# Find interface definitions
sg -p 'type $NAME interface { $$$ }' --lang go

# Find struct definitions
sg -p 'type $NAME struct { $$$ }' --lang go

# Find type aliases
sg -p 'type $NAME = $_' --lang go
```

### Error Handling

```bash
# Find error checks
sg -p 'if err != nil { $$$ }' --lang go

# Find error returns
sg -p 'return $_, err' --lang go

# Find error wrapping
sg -p 'fmt.Errorf($$$)' --lang go
```

### Concurrency

```bash
# Find goroutines
sg -p 'go $_' --lang go

# Find defer statements
sg -p 'defer $_' --lang go

# Find channel operations
sg -p '$_ <- $_' --lang go

# Find select statements
sg -p 'select { $$$ }' --lang go

# Find mutex locks
sg -p '$_.Lock()' --lang go
sg -p '$_.Unlock()' --lang go
```

### Common Patterns

```bash
# Find make calls
sg -p 'make($_)' --lang go

# Find new calls
sg -p 'new($_)' --lang go

# Find range loops
sg -p 'for $_, $_ := range $_ { $$$ }' --lang go

# Find init functions
sg -p 'func init() { $$$ }' --lang go
```

---

## Rust Patterns

### Function Definitions

```bash
# Find function definitions with return type
sg -p 'fn $NAME($$$) -> $_ { $$$ }' --lang rust

# Find function definitions without return
sg -p 'fn $NAME($$$) { $$$ }' --lang rust

# Find async functions
sg -p 'async fn $NAME($$$) -> $_ { $$$ }' --lang rust

# Find public functions
sg -p 'pub fn $NAME($$$) -> $_ { $$$ }' --lang rust
```

### Impl Blocks

```bash
# Find impl blocks
sg -p 'impl $_ { $$$ }' --lang rust

# Find trait implementations
sg -p 'impl $_ for $_ { $$$ }' --lang rust

# Find generic impl
sg -p 'impl<$_> $_ { $$$ }' --lang rust
```

### Error Handling

```bash
# Find unwrap calls (potential panics)
sg -p '$_.unwrap()' --lang rust

# Find expect calls
sg -p '$_.expect($_)' --lang rust

# Find ? operator
sg -p '$_?' --lang rust

# Find Result types
sg -p 'Result<$_, $_>' --lang rust

# Find Option types
sg -p 'Option<$_>' --lang rust
```

### Match Expressions

```bash
# Find match expressions
sg -p 'match $_ { $$$ }' --lang rust

# Find if let patterns
sg -p 'if let $_ = $_ { $$$ }' --lang rust

# Find while let patterns
sg -p 'while let $_ = $_ { $$$ }' --lang rust
```

### Macros and Attributes

```bash
# Find derive attributes
sg -p '#[derive($$$)]' --lang rust

# Find macro invocations
sg -p '$_!($$$)' --lang rust

# Find specific macros
sg -p 'println!($$$)' --lang rust
sg -p 'vec![$$$]' --lang rust
```

### Async/Await

```bash
# Find .await calls
sg -p '$_.await' --lang rust

# Find tokio::spawn
sg -p 'tokio::spawn($_)' --lang rust

# Find async blocks
sg -p 'async { $$$ }' --lang rust
```

### Smart Pointers

```bash
# Find Box usage
sg -p 'Box::new($_)' --lang rust

# Find Rc usage
sg -p 'Rc::new($_)' --lang rust

# Find Arc usage
sg -p 'Arc::new($_)' --lang rust

# Find RefCell
sg -p 'RefCell::new($_)' --lang rust
```
