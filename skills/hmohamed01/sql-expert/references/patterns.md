# T-SQL Patterns Reference

Detailed query patterns and templates for common scenarios.

## Pagination

```sql
-- Offset-fetch (SQL Server 2012+)
SELECT columns
FROM table
ORDER BY sort_column
OFFSET @PageSize * (@PageNumber - 1) ROWS
FETCH NEXT @PageSize ROWS ONLY;

-- Keyset pagination (better for large datasets)
SELECT TOP (@PageSize) columns
FROM table
WHERE sort_column > @LastValue
ORDER BY sort_column;
```

## Running Totals

```sql
SELECT
    column,
    amount,
    SUM(amount) OVER (ORDER BY date_column ROWS UNBOUNDED PRECEDING) AS running_total
FROM table;
```

## Gap Detection

```sql
WITH numbered AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
    FROM table
)
SELECT
    curr.id + 1 AS gap_start,
    next.id - 1 AS gap_end
FROM numbered curr
JOIN numbered next ON next.rn = curr.rn + 1
WHERE next.id - curr.id > 1;
```

## Hierarchy Traversal (Recursive CTE)

```sql
WITH hierarchy AS (
    -- Anchor
    SELECT id, parent_id, name, 0 AS level
    FROM table
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive
    SELECT t.id, t.parent_id, t.name, h.level + 1
    FROM table t
    JOIN hierarchy h ON t.parent_id = h.id
)
SELECT * FROM hierarchy
OPTION (MAXRECURSION 100);
```

## Deduplication

```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY duplicate_key_columns
            ORDER BY preference_column DESC
        ) AS rn
    FROM table
)
DELETE FROM ranked WHERE rn > 1;
```

## Dynamic Pivot

```sql
DECLARE @columns NVARCHAR(MAX), @sql NVARCHAR(MAX);

SELECT @columns = STRING_AGG(QUOTENAME(pivot_value), ', ')
FROM (SELECT DISTINCT pivot_column AS pivot_value FROM source_table) AS vals;

SET @sql = N'
SELECT *
FROM (SELECT row_id, pivot_column, value_column FROM source_table) AS src
PIVOT (SUM(value_column) FOR pivot_column IN (' + @columns + N')) AS pvt';

EXEC sp_executesql @sql;
```

## Indexing Strategies

### Covering Index
```sql
CREATE NONCLUSTERED INDEX IX_table_column
ON table(filter_column, sort_column)
INCLUDE (selected_column1, selected_column2);
```

### Filtered Index
```sql
CREATE NONCLUSTERED INDEX IX_table_active
ON table(date_column)
WHERE status = 'Active';
```

### Columnstore Guidelines
- Clustered columnstore: analytical workloads with large scans
- Nonclustered columnstore: hybrid OLTP/analytical
- Avoid on tables with frequent single-row updates

## MERGE Statement

```sql
MERGE target_table AS t
USING source_table AS s
ON t.key = s.key
WHEN MATCHED THEN
    UPDATE SET t.column = s.column
WHEN NOT MATCHED BY TARGET THEN
    INSERT (key, column) VALUES (s.key, s.column)
WHEN NOT MATCHED BY SOURCE THEN
    DELETE
OUTPUT $action, inserted.*, deleted.*;
```

## APPLY Operators

```sql
-- CROSS APPLY (inner join behavior)
SELECT o.order_id, top_items.*
FROM orders o
CROSS APPLY (
    SELECT TOP 3 * FROM order_items oi
    WHERE oi.order_id = o.order_id
    ORDER BY oi.amount DESC
) AS top_items;

-- OUTER APPLY (left join behavior)
SELECT c.customer_id, latest_order.*
FROM customers c
OUTER APPLY (
    SELECT TOP 1 * FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY o.order_date DESC
) AS latest_order;
```

## JSON Processing

```sql
-- Parse JSON
SELECT *
FROM OPENJSON(@json)
WITH (
    id INT '$.id',
    name NVARCHAR(100) '$.name',
    tags NVARCHAR(MAX) '$.tags' AS JSON
);

-- Generate JSON
SELECT id, name
FROM table
FOR JSON PATH, ROOT('items');
```

## Window Function Examples

```sql
-- Ranking
SELECT *,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) AS rank_in_category,
    RANK() OVER (ORDER BY sales DESC) AS overall_rank
FROM products;

-- LAG/LEAD for comparisons
SELECT
    date,
    value,
    LAG(value) OVER (ORDER BY date) AS prev_value,
    value - LAG(value) OVER (ORDER BY date) AS change
FROM metrics;

-- Running calculations
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS cumulative,
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM daily_sales;
```
