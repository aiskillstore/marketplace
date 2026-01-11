---
name: r-development
description: Modern R development practices emphasizing tidyverse patterns (dplyr 1.1 and later, native pipe, join_by, .by grouping), rlang metaprogramming, performance optimization, and package development. Use when Claude needs to write R code, create R packages, optimize R performance, or provide R programming guidance.
---

# R Development

This skill provides comprehensive guidance for modern R development, emphasizing current best practices with tidyverse, performance optimization, and professional package development.

## Core Principles

1. **Use modern tidyverse patterns** - Prioritize dplyr 1.1+ features, native pipe, and current APIs
2. **Profile before optimizing** - Use profvis and bench to identify real bottlenecks
3. **Write readable code first** - Optimize only when necessary and after profiling
4. **Follow tidyverse style guide** - Consistent naming, spacing, and structure

## Modern Tidyverse Essentials

### Native Pipe (`|>` not `%>%`)

Always use native pipe `|>` instead of magrittr `%>%` (R 4.1+):

```r
# Modern
data |> 
  filter(year >= 2020) |>
  summarise(mean_value = mean(value))

# Avoid legacy pipe
data %>% filter(year >= 2020)
```

### Join Syntax (dplyr 1.1+)

Use `join_by()` for all joins:

```r
# Modern join syntax with equality
transactions |> 
  inner_join(companies, by = join_by(company == id))

# Inequality joins
transactions |>
  inner_join(companies, join_by(company == id, year >= since))

# Rolling joins (closest match)
transactions |>
  inner_join(companies, join_by(company == id, closest(year >= since)))
```

Control match behavior:

```r
# Expect 1:1 matches
inner_join(x, y, by = join_by(id), multiple = "error")

# Ensure all rows match
inner_join(x, y, by = join_by(id), unmatched = "error")
```

### Per-Operation Grouping with `.by`

Use `.by` instead of `group_by() |> ... |> ungroup()`:

```r
# Modern approach (always returns ungrouped)
data |>
  summarise(mean_value = mean(value), .by = category)

# Multiple grouping variables
data |>
  summarise(total = sum(revenue), .by = c(company, year))
```

### Column Operations

Use modern column selection and transformation functions:

```r
# pick() for column selection in data-masking contexts
data |>
  summarise(
    n_x_cols = ncol(pick(starts_with("x"))),
    n_y_cols = ncol(pick(starts_with("y")))
  )

# across() for applying functions to multiple columns
data |>
  summarise(across(where(is.numeric), mean, .names = "mean_{.col}"), .by = group)

# reframe() for multi-row results per group
data |>
  reframe(quantiles = quantile(x, c(0.25, 0.5, 0.75)), .by = group)
```

## rlang Metaprogramming

For comprehensive rlang patterns, see [references/rlang-patterns.md](references/rlang-patterns.md).

### Quick Reference

- **`{{}}`** - Forward function arguments to data-masking functions
- **`!!`** - Inject single expressions or values
- **`!!!`** - Inject multiple arguments from a list
- **`.data[[]]`** - Access columns by name (character vectors)
- **`pick()`** - Select columns inside data-masking functions

Example function with embracing:

```r
my_summary <- function(data, group_var, summary_var) {
  data |>
    summarise(mean_val = mean({{ summary_var }}), .by = {{ group_var }})
}
```

## Performance Optimization

For detailed performance guidance, see [references/performance.md](references/performance.md).

### Key Strategies

1. **Profile first**: Use `profvis::profvis()` and `bench::mark()`
2. **Vectorize operations**: Avoid loops when vectorized alternatives exist
3. **Use dtplyr**: For large data operations (lazy evaluation with data.table backend)
4. **Parallel processing**: Use `furrr::future_map()` for parallelizable work
5. **Memory efficiency**: Pre-allocate, use appropriate data types

Quick example:

```r
# Profile code
profvis::profvis({
  result <- data |> 
    complex_operation() |>
    another_operation()
})

# Benchmark alternatives
bench::mark(
  approach_1 = method1(data),
  approach_2 = method2(data),
  check = FALSE
)
```

## Package Development

For complete package development guidance, see [references/package-development.md](references/package-development.md).

### Quick Guidelines

**API Design:**
- Use `.by` parameter for per-operation grouping
- Use `{{}}` for column arguments
- Return tibbles consistently
- Validate user-facing function inputs thoroughly

**Dependencies:**
- Add dependencies for significant functionality gains
- Core tidyverse packages usually worth including: dplyr, purrr, stringr, tidyr
- Minimize dependencies for widely-used packages

**Testing:**
- Unit tests for individual functions
- Integration tests for workflows
- Test edge cases and error conditions

**Documentation:**
- Document all exported functions
- Provide usage examples
- Explain non-obvious parameter interactions

## Common Migration Patterns

### Base R → Tidyverse

```r
# Data manipulation
subset(data, condition)         → filter(data, condition)
data[order(data$x), ]          → arrange(data, x)
aggregate(x ~ y, data, mean)   → summarise(data, mean(x), .by = y)

# Functional programming
sapply(x, f)                   → map(x, f)  # type-stable
lapply(x, f)                   → map(x, f)

# Strings
grepl("pattern", text)         → str_detect(text, "pattern")
gsub("old", "new", text)       → str_replace_all(text, "old", "new")
```

### Old → New Tidyverse

```r
# Pipes
%>%                            → |>

# Grouping
group_by() |> ... |> ungroup() → summarise(..., .by = x)

# Joins
by = c("a" = "b")             → by = join_by(a == b)

# Reshaping
gather()/spread()              → pivot_longer()/pivot_wider()
```

## Additional Resources

- **rlang patterns**: See [references/rlang-patterns.md](references/rlang-patterns.md) for comprehensive data-masking and metaprogramming guidance
- **Performance optimization**: See [references/performance.md](references/performance.md) for profiling, benchmarking, and optimization strategies
- **Package development**: See [references/package-development.md](references/package-development.md) for complete package creation guidance
- **Object systems**: See [references/object-systems.md](references/object-systems.md) for S3, S4, S7, R6, and vctrs guidance
