# SQL Window Functions

Complete reference for window functions and analytical queries.

## Core Window Functions

### ROW_NUMBER

Assigns unique sequential numbers within partition:

```sql
-- Rank employees by salary within department
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;

-- Get top N per group
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
)
SELECT * FROM ranked WHERE rn <= 3;
```

### RANK and DENSE_RANK

Handle ties differently:

```sql
-- RANK: 1, 2, 2, 4 (skips after ties)
-- DENSE_RANK: 1, 2, 2, 3 (no skip)
SELECT
    name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank
FROM contestants;

-- Result for scores [100, 95, 95, 90]:
-- name    score   rank   dense_rank
-- Alice   100     1      1
-- Bob     95      2      2
-- Carol   95      2      2
-- Dave    90      4      3
```

### NTILE

Divide into N equal groups:

```sql
-- Divide into quartiles
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) as quartile
FROM employees;

-- Percentile buckets
SELECT
    name,
    score,
    NTILE(100) OVER (ORDER BY score) as percentile
FROM students;
```

## Navigation Functions

### LAG and LEAD

Access previous/next rows:

```sql
-- Previous and next day revenue
SELECT
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) as prev_day,
    LEAD(revenue, 1) OVER (ORDER BY date) as next_day,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) as day_change
FROM daily_sales;

-- With default value for first/last
SELECT
    date,
    revenue,
    LAG(revenue, 1, 0) OVER (ORDER BY date) as prev_or_zero
FROM daily_sales;

-- Multiple periods back
SELECT
    date,
    revenue,
    LAG(revenue, 7) OVER (ORDER BY date) as same_day_last_week
FROM daily_sales;
```

### FIRST_VALUE and LAST_VALUE

Get first/last value in window:

```sql
-- Compare to first sale of month
SELECT
    date,
    revenue,
    FIRST_VALUE(revenue) OVER (
        PARTITION BY DATE_TRUNC('month', date)
        ORDER BY date
    ) as first_day_revenue,
    revenue - FIRST_VALUE(revenue) OVER (
        PARTITION BY DATE_TRUNC('month', date)
        ORDER BY date
    ) as diff_from_first
FROM daily_sales;

-- Note: LAST_VALUE needs explicit frame
SELECT
    date,
    revenue,
    LAST_VALUE(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_revenue
FROM daily_sales;
```

### NTH_VALUE

Get Nth value in window:

```sql
-- Get 2nd highest salary per department
SELECT
    department,
    name,
    salary,
    NTH_VALUE(salary, 2) OVER (
        PARTITION BY department
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as second_highest
FROM employees;
```

## Aggregate Window Functions

### Running Totals

```sql
-- Running total
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;

-- Running total by category
SELECT
    date,
    category,
    amount,
    SUM(amount) OVER (
        PARTITION BY category
        ORDER BY date
    ) as category_running_total
FROM transactions;
```

### Moving Averages

```sql
-- 7-day moving average
SELECT
    date,
    value,
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM metrics;

-- Centered moving average
SELECT
    date,
    value,
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) as centered_avg
FROM metrics;
```

### Cumulative Statistics

```sql
-- Running count, sum, avg, min, max
SELECT
    date,
    revenue,
    COUNT(*) OVER (ORDER BY date) as cumulative_count,
    SUM(revenue) OVER (ORDER BY date) as cumulative_sum,
    AVG(revenue) OVER (ORDER BY date) as cumulative_avg,
    MIN(revenue) OVER (ORDER BY date) as cumulative_min,
    MAX(revenue) OVER (ORDER BY date) as cumulative_max
FROM daily_sales;
```

## Window Frame Specification

### ROWS vs RANGE

```sql
-- ROWS: Physical row count
SELECT
    date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as sum_3_rows
FROM sales;

-- RANGE: Logical value range (careful with duplicates)
SELECT
    date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY date
        RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
    ) as sum_7_days
FROM sales;
```

### Frame Boundaries

```sql
-- All frames available
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING  -- Entire partition
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW          -- From start to here
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING          -- From here to end
ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING                  -- 7 rows centered
ROWS BETWEEN 6 PRECEDING AND CURRENT ROW                  -- 7 rows trailing
```

## Practical Examples

### Year-over-Year Comparison

```sql
SELECT
    date,
    revenue,
    LAG(revenue, 365) OVER (ORDER BY date) as revenue_year_ago,
    revenue - LAG(revenue, 365) OVER (ORDER BY date) as yoy_change,
    ROUND(100.0 * (revenue - LAG(revenue, 365) OVER (ORDER BY date))
        / NULLIF(LAG(revenue, 365) OVER (ORDER BY date), 0), 2) as yoy_pct
FROM daily_sales;
```

### Running Percentage of Total

```sql
SELECT
    category,
    sales,
    SUM(sales) OVER () as total,
    ROUND(100.0 * sales / SUM(sales) OVER (), 2) as pct_of_total,
    ROUND(100.0 * SUM(sales) OVER (ORDER BY sales DESC)
        / SUM(sales) OVER (), 2) as cumulative_pct
FROM category_sales;
```

### Session/Gap Detection

```sql
-- Find sessions (gaps > 30 minutes = new session)
WITH events_with_gaps AS (
    SELECT
        *,
        EXTRACT(EPOCH FROM (timestamp - LAG(timestamp) OVER (
            PARTITION BY user_id ORDER BY timestamp
        ))) / 60 as minutes_since_last
    FROM user_events
)
SELECT
    *,
    SUM(CASE WHEN minutes_since_last > 30 OR minutes_since_last IS NULL
        THEN 1 ELSE 0 END) OVER (
        PARTITION BY user_id ORDER BY timestamp
    ) as session_id
FROM events_with_gaps;
```

### Deduplication with Row Number

```sql
-- Keep only the latest record per user
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY updated_at DESC
        ) as rn
    FROM users
)
SELECT * FROM ranked WHERE rn = 1;
```

## Performance Tips

1. **Index the ORDER BY column** - Window functions sort data
2. **Limit partitions** - Large partitions = more memory
3. **Named windows** - Reuse window definitions
4. **Avoid nested windows** - Use CTEs instead

### Named Windows

```sql
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER dept_salary as rank,
    AVG(salary) OVER dept_salary as dept_avg,
    salary - AVG(salary) OVER dept_salary as diff_from_avg
FROM employees
WINDOW dept_salary AS (PARTITION BY department ORDER BY salary DESC);
```
