# Package Development

## Dependency Strategy

### When to Add Dependencies vs Base R

```r
# Add dependency when:
✓ Significant functionality gain
✓ Maintenance burden reduction
✓ User experience improvement
✓ Complex implementation (regex, dates, web)

# Use base R when:
✓ Simple utility functions
✓ Package will be widely used (minimize deps)
✓ Dependency is large for small benefit
✓ Base R solution is straightforward

# Example decisions:
str_detect(x, "pattern")    # Worth stringr dependency
length(x) > 0              # Don't need purrr for this
parse_dates(x)             # Worth lubridate dependency  
x + 1                      # Don't need dplyr for this
```

### Tidyverse Dependency Guidelines

```r
# Core tidyverse (usually worth it):
dplyr     # Complex data manipulation
purrr     # Functional programming, parallel
stringr   # String manipulation
tidyr     # Data reshaping

# Specialized tidyverse (evaluate carefully):
lubridate # If heavy date manipulation
forcats   # If many categorical operations  
readr     # If specific file reading needs
ggplot2   # If package creates visualizations

# Heavy dependencies (use sparingly):
tidyverse # Meta-package, very heavy
shiny     # Only for interactive apps
```

## API Design Patterns

### Function Design Strategy

```r
# Modern tidyverse API patterns

# 1. Use .by for per-operation grouping
my_summarise <- function(.data, ..., .by = NULL) {
  # Support modern grouped operations
}

# 2. Use {{ }} for user-provided columns  
my_select <- function(.data, cols) {
  .data |> select({{ cols }})
}

# 3. Use ... for flexible arguments
my_mutate <- function(.data, ..., .by = NULL) {
  .data |> mutate(..., .by = {{ .by }})
}

# 4. Return consistent types (tibbles, not data.frames)
my_function <- function(.data) {
  result |> tibble::as_tibble()
}
```

### Input Validation Strategy

```r
# Validation level by function type:

# User-facing functions - comprehensive validation
user_function <- function(x, threshold = 0.5) {
  # Check all inputs thoroughly
  if (!is.numeric(x)) stop("x must be numeric")
  if (!is.numeric(threshold) || length(threshold) != 1) {
    stop("threshold must be a single number")
  }
  # ... function body
}

# Internal functions - minimal validation  
.internal_function <- function(x, threshold) {
  # Assume inputs are valid (document assumptions)
  # Only check critical invariants
  # ... function body
}

# Package functions with vctrs - type-stable validation
safe_function <- function(x, y) {
  x <- vec_cast(x, double())
  y <- vec_cast(y, double())
  # Automatic type checking and coercion
}
```

## Error Handling Patterns

```r
# Good error messages - specific and actionable
if (length(x) == 0) {
  cli::cli_abort(
    "Input {.arg x} cannot be empty.",
    "i" = "Provide a non-empty vector."
  )
}

# Include function name in errors
validate_input <- function(x, call = caller_env()) {
  if (!is.numeric(x)) {
    cli::cli_abort("Input must be numeric", call = call)
  }
}

# Use consistent error styling
# cli package for user-friendly messages
# rlang for developer tools
```

## When to Create Internal vs Exported Functions

### Export Function When:

```r
✓ Users will call it directly
✓ Other packages might want to extend it
✓ Part of the core package functionality
✓ Stable API that won't change often

# Example: main data processing functions
export_these <- function(.data, ...) {
  # Comprehensive input validation
  # Full documentation required
  # Stable API contract
}
```

### Keep Function Internal When:

```r
✓ Implementation detail that may change
✓ Only used within package
✓ Complex implementation helpers
✓ Would clutter user-facing API

# Example: helper functions
.internal_helper <- function(x, y) {
  # Minimal documentation
  # Can change without breaking users
  # Assume inputs are pre-validated
}
```

## Testing and Documentation Strategy

### Testing Levels

```r
# Unit tests - individual functions
test_that("function handles edge cases", {
  expect_equal(my_func(c()), expected_empty_result)
  expect_error(my_func(NULL), class = "my_error_class")
})

# Integration tests - workflow combinations  
test_that("pipeline works end-to-end", {
  result <- data |> 
    step1() |> 
    step2() |>
    step3()
  expect_s3_class(result, "expected_class")
})

# Property-based tests for package functions
test_that("function properties hold", {
  # Test invariants across many inputs
})
```

### Testing rlang Functions

```r
# Test data-masking behavior
test_that("function supports data masking", {
  result <- my_function(mtcars, cyl)
  expect_equal(names(result), "mean_cyl")
  
  # Test with expressions
  result2 <- my_function(mtcars, cyl * 2)
  expect_true("mean_cyl * 2" %in% names(result2))
})

# Test injection behavior
test_that("function supports injection", {
  var <- "cyl"
  result <- my_function(mtcars, !!sym(var))
  expect_true(nrow(result) > 0)
})
```

### Documentation Priorities

```r
# Must document:
✓ All exported functions
✓ Complex algorithms or formulas
✓ Non-obvious parameter interactions
✓ Examples of typical usage

# Can skip documentation:
✗ Simple internal helpers
✗ Obvious parameter meanings
✗ Functions that just call other functions
```

### Documentation Tags for rlang

```r
#' @param var <[`data-masked`][dplyr::dplyr_data_masking]> Column to summarize
#' @param ... <[`dynamic-dots`][rlang::dyn-dots]> Additional grouping variables  
#' @param cols <[`tidy-select`][dplyr::dplyr_tidy_select]> Columns to select
```

## Package Structure

### DESCRIPTION File

```r
Package: mypackage
Title: What the Package Does (One Line, Title Case)
Version: 0.1.0
Authors@R: person("First", "Last", email = "email@example.com", role = c("aut", "cre"))
Description: What the package does (one paragraph).
License: MIT + file LICENSE
Encoding: UTF-8
Roxygen: list(markdown = TRUE)
RoxygenNote: 7.2.3
Imports:
    dplyr (>= 1.1.0),
    rlang (>= 1.1.0),
    cli
Suggests:
    testthat (>= 3.0.0)
Config/testthat/edition: 3
```

### NAMESPACE Management

Use roxygen2 for NAMESPACE management:

```r
# Import specific functions
#' @importFrom rlang := enquo enquos
#' @importFrom dplyr mutate filter

# Or import entire packages (use sparingly)
#' @import dplyr
```

### rlang Import Strategy

```r
# In DESCRIPTION:
Imports: rlang

# In NAMESPACE, import specific functions:
importFrom(rlang, enquo, enquos, expr, !!!, :=)

# Or import key functions:
#' @importFrom rlang := enquo enquos
```

## Naming Conventions

```r
# Good naming: snake_case for variables/functions
calculate_mean_score <- function(data, score_col) {
  # Function body
}

# Prefix non-standard arguments with .
my_function <- function(.data, ...) {
  # Reduces argument conflicts
}

# Internal functions start with .
.internal_helper <- function(x, y) {
  # Not exported
}
```

## Style Guide Essentials

### Object Names

- Use snake_case for all names
- Variable names = nouns, function names = verbs
- Avoid dots except for S3 methods

```r
# Good
day_one
calculate_mean  
user_data

# Avoid
DayOne
calculate.mean
userData
```

### Spacing and Layout

```r
# Good spacing
x[, 1]
mean(x, na.rm = TRUE)
if (condition) {
  action()
}

# Pipe formatting
data |>
  filter(year >= 2020) |>
  group_by(category) |>
  summarise(
    mean_value = mean(value),
    count = n()
  )
```

## Package Development Workflow

1. **Setup**: Use `usethis::create_package()`
2. **Add functions**: Place in `R/` directory
3. **Document**: Use roxygen2 comments
4. **Test**: Write tests in `tests/testthat/`
5. **Check**: Run `devtools::check()`
6. **Build**: Use `devtools::build()`
7. **Install**: Use `devtools::install()`

### Key usethis Functions

```r
# Initial setup
usethis::create_package("mypackage")
usethis::use_git()
usethis::use_mit_license()

# Add dependencies
usethis::use_package("dplyr")
usethis::use_package("testthat", "Suggests")

# Add infrastructure
usethis::use_readme_md()
usethis::use_news_md()
usethis::use_testthat()

# Add files
usethis::use_r("my_function")
usethis::use_test("my_function")
usethis::use_vignette("introduction")
```

## Common Pitfalls

### What to Avoid

```r
# Don't use library() in packages
# Use Imports in DESCRIPTION instead

# Don't use source()
# Use proper function dependencies

# Don't use attach()
# Always use explicit :: notation

# Don't modify global options without restoring
old <- options(stringsAsFactors = FALSE)
on.exit(options(old), add = TRUE)

# Don't use setwd()
# Use here::here() or relative paths
```
