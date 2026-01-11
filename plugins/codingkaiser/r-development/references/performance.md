# Performance Optimization

## Performance Tool Selection Guide

### Profiling Tools Decision Matrix

| Tool | Use When | Don't Use When | What It Shows |
|------|----------|----------------|---------------|
| **`profvis`** | Complex code, unknown bottlenecks | Simple functions, known issues | Time per line, call stack |
| **`bench::mark()`** | Comparing alternatives | Single approach | Relative performance, memory |
| **`system.time()`** | Quick checks | Detailed analysis | Total runtime only |
| **`Rprof()`** | Base R only environments | When profvis available | Raw profiling data |

### Step-by-Step Performance Workflow

```r
# 1. Profile first - find the actual bottlenecks
library(profvis)
profvis({
  # Your slow code here
})

# 2. Focus on the slowest parts (80/20 rule)
# Don't optimize until you know where time is spent

# 3. Benchmark alternatives for hot spots
library(bench)
bench::mark(
  current = current_approach(data),
  vectorized = vectorized_approach(data),
  parallel = map(data, in_parallel(func))
)

# 4. Consider tool trade-offs based on bottleneck type
```

## When Each Tool Helps vs Hurts

### Parallel Processing (`in_parallel()`)

```r
# Helps when:
✓ CPU-intensive computations
✓ Embarrassingly parallel problems  
✓ Large datasets with independent operations
✓ I/O bound operations (file reading, API calls)

# Hurts when:
✗ Simple, fast operations (overhead > benefit)
✗ Memory-intensive operations (may cause thrashing)
✗ Operations requiring shared state
✗ Small datasets

# Example decision point:
expensive_func <- function(x) Sys.sleep(0.1) # 100ms per call
fast_func <- function(x) x^2                 # microseconds per call

# Good for parallel
map(1:100, in_parallel(expensive_func))  # ~10s -> ~2.5s on 4 cores

# Bad for parallel (overhead > benefit)  
map(1:100, in_parallel(fast_func))       # 100μs -> 50ms (500x slower!)
```

### vctrs Backend Tools

```r
# Use vctrs when:
✓ Type safety matters more than raw speed
✓ Building reusable package functions
✓ Complex coercion/combination logic
✓ Consistent behavior across edge cases

# Avoid vctrs when:
✗ One-off scripts where speed matters most
✗ Simple operations where base R is sufficient  
✗ Memory is extremely constrained

# Decision point:
simple_combine <- function(x, y) c(x, y)           # Fast, simple
robust_combine <- function(x, y) vec_c(x, y)      # Safer, slight overhead

# Use simple for hot loops, robust for package APIs
```

### Data Backend Selection

```r
# Use data.table when:
✓ Very large datasets (>1GB)
✓ Complex grouping operations
✓ Reference semantics desired
✓ Maximum performance critical

# Use dplyr when:
✓ Readability and maintainability priority
✓ Complex joins and window functions
✓ Team familiarity with tidyverse
✓ Moderate sized data (<100MB)

# Use dtplyr (dplyr with data.table backend) when:
✓ Want dplyr syntax with data.table performance
✓ Large data but team prefers tidyverse
✓ Lazy evaluation desired

# Use base R when:
✓ No dependencies allowed
✓ Simple operations
✓ Teaching/learning contexts
```

## Profiling Best Practices

```r
# 1. Profile realistic data sizes
profvis({
  # Use actual data size, not toy examples
  real_data |> your_analysis()
})

# 2. Profile multiple runs for stability
bench::mark(
  your_function(data),
  min_iterations = 10,  # Multiple runs
  max_iterations = 100
)

# 3. Check memory usage too
bench::mark(
  approach1 = method1(data), 
  approach2 = method2(data),
  check = FALSE,  # If outputs differ slightly
  filter_gc = FALSE  # Include GC time
)

# 4. Profile with realistic usage patterns
# Not just isolated function calls
```

## Performance Anti-Patterns to Avoid

```r
# Don't optimize without measuring
# ✗ "This looks slow" -> immediately rewrite
# ✓ Profile first, optimize bottlenecks

# Don't over-engineer for performance  
# ✗ Complex optimizations for 1% gains
# ✓ Focus on algorithmic improvements

# Don't assume - measure
# ✗ "for loops are always slow in R"
# ✓ Benchmark your specific use case

# Don't ignore readability costs
# ✗ Unreadable code for minor speedups
# ✓ Readable code with targeted optimizations

# Don't grow objects in loops
# ✗ result <- c(); for(i in 1:n) result <- c(result, x[i])
# ✓ result <- vector("list", n); for(i in 1:n) result[[i]] <- x[i]
```

## Modern purrr Patterns for Performance

Use modern purrr 1.0+ patterns:

```r
# Modern data frame row binding (purrr 1.0+)
models <- data_splits |> 
  map(\(split) train_model(split)) |>
  list_rbind()  # Replaces map_dfr()

# Column binding  
summaries <- data_list |> 
  map(\(df) get_summary_stats(df)) |>
  list_cbind()  # Replaces map_dfc()

# Side effects with walk()
plots <- walk2(data_list, plot_names, \(df, name) {
  p <- ggplot(df, aes(x, y)) + geom_point()
  ggsave(name, p)
})

# Parallel processing (purrr 1.1.0+)
library(mirai)
daemons(4)
results <- large_datasets |> 
  map(in_parallel(expensive_computation))
daemons(0)
```

## Vectorization

```r
# Good - vectorized operations
result <- x + y

# Good - Type-stable purrr functions
map_dbl(data, mean)    # always returns double
map_chr(data, class)   # always returns character

# Avoid - Type-unstable base functions
sapply(data, mean)     # might return list or vector

# Avoid - explicit loops for simple operations
result <- numeric(length(x))
for(i in seq_along(x)) {
  result[i] <- x[i] + y[i]
}
```

## Using dtplyr for Large Data

For large datasets, use dtplyr to get data.table performance with dplyr syntax:

```r
library(dtplyr)

# Convert to lazy data.table
large_data_dt <- lazy_dt(large_data)

# Use dplyr syntax as normal
result <- large_data_dt |>
  filter(year >= 2020) |>
  group_by(category) |>
  summarise(
    total = sum(value),
    avg = mean(value)
  ) |>
  as_tibble()  # Convert back to tibble

# See generated data.table code
result |> show_query()
```

## Memory Optimization

```r
# Pre-allocate vectors
result <- vector("numeric", n)

# Use appropriate data types
# integer instead of double when possible
x <- 1:1000  # integer
y <- seq(1, 1000, by = 1)  # double

# Remove large objects when done
rm(large_object)
gc()  # Force garbage collection if needed

# Use data.table for large data
library(data.table)
dt <- as.data.table(large_df)
dt[, new_col := old_col * 2]  # Modifies in place
```

## String Manipulation Performance

Use stringr over base R for consistency and performance:

```r
# Good - stringr (consistent, pipe-friendly)
text |>
  str_to_lower() |>
  str_trim() |>
  str_replace_all("pattern", "replacement") |>
  str_extract("\\d+")

# Common patterns
str_detect(text, "pattern")     # vs grepl("pattern", text)
str_extract(text, "pattern")    # vs complex regmatches()
str_replace_all(text, "a", "b") # vs gsub("a", "b", text)
str_split(text, ",")            # vs strsplit(text, ",")
str_length(text)                # vs nchar(text)
str_sub(text, 1, 5)             # vs substr(text, 1, 5)
```

## When to Use vctrs

### Core Benefits
- **Type stability** - Predictable output types regardless of input values
- **Size stability** - Predictable output sizes from input sizes
- **Consistent coercion rules** - Single set of rules applied everywhere
- **Robust class design** - Proper S3 vector infrastructure

### Use vctrs when:

```r
# Type-Stable Functions in Packages
my_function <- function(x, y) {
  # Always returns double, regardless of input values
  vec_cast(result, double())
}

# Consistent Coercion/Casting
vec_cast(x, double())  # Clear intent, predictable behavior
vec_ptype_common(x, y, z)  # Finds richest compatible type

# Size/Length Stability
vec_c(x, y)  # size = vec_size(x) + vec_size(y)
vec_rbind(df1, df2)  # size = sum of input sizes
```

### Don't Use vctrs When:
- Simple one-off analyses - Base R is sufficient
- No custom classes needed - Standard types work fine  
- Performance critical + simple operations - Base R may be faster
- External API constraints - Must return base R types

The key insight: **vctrs is most valuable in package development where type safety, consistency, and extensibility matter more than raw speed for simple operations.**
