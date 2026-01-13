# Object-Oriented Programming in R

## S7: Modern OOP for New Projects

S7 combines S3 simplicity with S4 structure:
- Formal class definitions with automatic validation
- Compatible with existing S3 code
- Better error messages and discoverability

```r
# S7 class definition
Range <- new_class("Range",
  properties = list(
    start = class_double,
    end = class_double
  ),
  validator = function(self) {
    if (self@end < self@start) {
      "@end must be >= @start"
    }
  }
)

# Usage - constructor and property access
x <- Range(start = 1, end = 10)
x@start  # 1
x@end <- 20  # automatic validation

# Methods
inside <- new_generic("inside", "x")
method(inside, Range) <- function(x, y) {
  y >= x@start & y <= x@end
}
```

## OOP System Decision Matrix

### Decision Tree: What Are You Building?

#### 1. Vector-like Objects

**Use vctrs when:**
- ✓ Need data frame integration (columns/rows)
- ✓ Want type-stable vector operations  
- ✓ Building factor-like, date-like, or numeric-like classes
- ✓ Need consistent coercion/casting behavior
- ✓ Working with existing tidyverse infrastructure

**Examples:** custom date classes, units, categorical data

```r
# Vector-like behavior in data frames
percent <- new_vctr(0.5, class = "percentage") 
data.frame(x = 1:3, pct = percent(c(0.1, 0.2, 0.3)))  # works seamlessly

# Type-stable operations
vec_c(percent(0.1), percent(0.2))  # predictable behavior
vec_cast(0.5, percent())          # explicit, safe casting
```

#### 2. General Objects (Complex Data Structures)

**Use S7 when:**
- ✓ NEW projects that need formal classes
- ✓ Want property validation and safe property access (@)
- ✓ Need multiple dispatch (beyond S3's double dispatch)
- ✓ Converting from S3 and want better structure
- ✓ Building class hierarchies with inheritance
- ✓ Want better error messages and discoverability

```r
# Complex validation needs
Range <- new_class("Range",
  properties = list(start = class_double, end = class_double),
  validator = function(self) {
    if (self@end < self@start) "@end must be >= @start"
  }
)

# Multiple dispatch needs  
method(generic, list(ClassA, ClassB)) <- function(x, y) ...

# Class hierarchies with clear inheritance
Child <- new_class("Child", parent = Parent)
```

**Use S3 when:**
- ✓ Simple classes with minimal structure needs
- ✓ Maximum compatibility and minimal dependencies  
- ✓ Quick prototyping or internal classes
- ✓ Contributing to existing S3-based ecosystems
- ✓ Performance is absolutely critical (minimal overhead)

```r
# Simple classes without complex needs
new_simple <- function(x) structure(x, class = "simple")
print.simple <- function(x, ...) cat("Simple:", x)
```

**Use S4 when:**
- ✓ Working in Bioconductor ecosystem
- ✓ Need complex multiple inheritance (S7 doesn't support this)
- ✓ Existing S4 codebase that works well

**Use R6 when:**
- ✓ Need reference semantics (mutable objects)
- ✓ Building stateful objects
- ✓ Coming from OOP languages like Python/Java
- ✓ Need encapsulation and private methods

## Detailed S7 vs S3 Comparison

| Feature | S3 | S7 | When S7 wins |
|---------|----|----|---------------|
| **Class definition** | Informal (convention) | Formal (`new_class()`) | Need guaranteed structure |
| **Property access** | `$` or `attr()` (unsafe) | `@` (safe, validated) | Property validation matters |
| **Validation** | Manual, inconsistent | Built-in validators | Data integrity important |
| **Method discovery** | Hard to find methods | Clear method printing | Developer experience matters |
| **Multiple dispatch** | Limited (base generics) | Full multiple dispatch | Complex method dispatch needed |
| **Inheritance** | Informal, `NextMethod()` | Explicit `super()` | Predictable inheritance needed |
| **Migration cost** | - | Low (1-2 hours) | Want better structure |
| **Performance** | Fastest | ~Same as S3 | Performance difference negligible |
| **Compatibility** | Full S3 | Full S3 + S7 | Need both old and new patterns |

## vctrs for Vector Classes

### Basic Vector Class

```r
# Constructor (low-level)
new_percent <- function(x = double()) {
  vec_assert(x, double())
  new_vctr(x, class = "pkg_percent")
}

# Helper (user-facing)
percent <- function(x = double()) {
  x <- vec_cast(x, double())
  new_percent(x)
}

# Format method
format.pkg_percent <- function(x, ...) {
  paste0(vec_data(x) * 100, "%")
}
```

### Coercion Methods

```r
# Self-coercion
vec_ptype2.pkg_percent.pkg_percent <- function(x, y, ...) {
  new_percent()
}

# With double
vec_ptype2.pkg_percent.double <- function(x, y, ...) double()
vec_ptype2.double.pkg_percent <- function(x, y, ...) double()

# Casting
vec_cast.pkg_percent.double <- function(x, to, ...) {
  new_percent(x)
}
vec_cast.double.pkg_percent <- function(x, to, ...) {
  vec_data(x)
}
```

## S3 Basics

### Creating S3 Classes

```r
# Constructor
new_myclass <- function(x, y) {
  structure(
    list(x = x, y = y),
    class = "myclass"
  )
}

# Methods
print.myclass <- function(x, ...) {
  cat("myclass object\n")
  cat("x:", x$x, "\n")
  cat("y:", x$y, "\n")
}

summary.myclass <- function(object, ...) {
  list(x = object$x, y = object$y)
}
```

### Generic Functions

```r
# Create generic
my_generic <- function(x, ...) {
  UseMethod("my_generic")
}

# Default method
my_generic.default <- function(x, ...) {
  stop("No method for class ", class(x))
}

# Specific method
my_generic.myclass <- function(x, ...) {
  # Implementation
}
```

## R6 Classes

### Basic R6 Class

```r
library(R6)

MyClass <- R6Class("MyClass",
  public = list(
    x = NULL,
    y = NULL,
    
    initialize = function(x, y) {
      self$x <- x
      self$y <- y
    },
    
    add = function() {
      self$x + self$y
    }
  ),
  
  private = list(
    internal_value = NULL
  )
)

# Usage
obj <- MyClass$new(1, 2)
obj$add()  # 3
```

## Migration Strategy

### S3 → S7

Usually 1-2 hours work, keeps full compatibility:

```r
# S3 version
new_range <- function(start, end) {
  structure(
    list(start = start, end = end),
    class = "range"
  )
}

# S7 version
Range <- new_class("Range",
  properties = list(
    start = class_double,
    end = class_double
  )
)
```

### S4 → S7

More complex, evaluate if S4 features are actually needed.

### Base R → vctrs

For vector-like classes, significant benefits in type stability and data frame integration.

### Combining Approaches

S7 classes can use vctrs principles internally for vector-like properties.

## When to Use Each System

### Use S7 for:
- New projects needing formal OOP
- Class validation and type safety
- Multiple dispatch
- Better developer experience

### Use vctrs for:
- Vector-like classes
- Data frame columns
- Type-stable operations
- Tidyverse integration

### Use S3 for:
- Simple classes
- Maximum compatibility
- Existing S3 ecosystems
- Quick prototypes

### Use S4 for:
- Bioconductor packages
- Complex multiple inheritance
- Existing S4 codebases

### Use R6 for:
- Mutable state
- Reference semantics
- Encapsulation needs
- Coming from OOP languages
