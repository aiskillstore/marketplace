# Advanced SQL Patterns

## UPSERT (Insert or Update)

### PostgreSQL: ON CONFLICT

```sql
INSERT INTO users (user_id, name, email, updated_at)
VALUES (1, 'John Doe', 'john@example.com', NOW())
ON CONFLICT (user_id)
DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = NOW();
```

### MySQL: ON DUPLICATE KEY UPDATE

```sql
INSERT INTO users (user_id, name, email, updated_at)
VALUES (1, 'John Doe', 'john@example.com', NOW())
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    email = VALUES(email),
    updated_at = NOW();
```

### SQLite: ON CONFLICT

```sql
INSERT INTO users (user_id, name, email, updated_at)
VALUES (1, 'John Doe', 'john@example.com', datetime('now'))
ON CONFLICT(user_id) DO UPDATE SET
    name = excluded.name,
    email = excluded.email,
    updated_at = datetime('now');
```

## Bulk Operations

### Bulk INSERT

```sql
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');
```

### Bulk UPDATE from Another Table

```sql
UPDATE products p
SET price = new_prices.price
FROM (
    VALUES
        (1, 19.99),
        (2, 29.99),
        (3, 39.99)
) AS new_prices(product_id, price)
WHERE p.product_id = new_prices.product_id;
```

### Bulk DELETE with JOIN

```sql
DELETE FROM orders
WHERE order_id IN (
    SELECT order_id
    FROM orders o
    INNER JOIN users u ON o.user_id = u.user_id
    WHERE u.status = 'deleted'
);
```

## Pivot Tables

### Manual Pivot with CASE

```sql
-- Transform rows to columns
SELECT
    product_name,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN quantity ELSE 0 END) as jan,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN quantity ELSE 0 END) as feb,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN quantity ELSE 0 END) as mar
FROM
    order_items oi
INNER JOIN
    products p ON oi.product_id = p.product_id
GROUP BY
    product_name;
```

### PostgreSQL Crosstab

```sql
-- Requires tablefunc extension
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM crosstab(
    'SELECT product_name, month, total_quantity
     FROM monthly_sales
     ORDER BY 1, 2',
    'SELECT DISTINCT month FROM monthly_sales ORDER BY 1'
) AS ct(product_name TEXT, jan INT, feb INT, mar INT);
```

## JSON Operations (PostgreSQL)

### Query JSON Data

```sql
SELECT
    user_id,
    preferences->>'theme' as theme,
    preferences->>'language' as language
FROM
    users
WHERE
    preferences->>'notifications' = 'true';
```

### Update JSON Field

```sql
UPDATE users
SET preferences = jsonb_set(
    preferences,
    '{theme}',
    '"dark"'
)
WHERE user_id = 123;
```

### JSON Aggregation

```sql
SELECT
    department,
    jsonb_agg(jsonb_build_object(
        'name', name,
        'salary', salary
    )) as employees
FROM
    employees
GROUP BY
    department;
```

### JSON Array Operations

```sql
-- Check if JSON array contains value
SELECT * FROM users
WHERE preferences->'tags' ? 'premium';

-- Get array element
SELECT preferences->'tags'->0 as first_tag
FROM users;

-- Expand JSON array to rows
SELECT
    user_id,
    jsonb_array_elements_text(preferences->'tags') as tag
FROM
    users;
```

## Recursive Queries

### Hierarchical Data Traversal

```sql
WITH RECURSIVE employee_hierarchy AS (
    -- Anchor member: top-level employees
    SELECT
        id,
        name,
        manager_id,
        1 as level,
        name::TEXT as path
    FROM
        employees
    WHERE
        manager_id IS NULL

    UNION ALL

    -- Recursive member: employees reporting to previous level
    SELECT
        e.id,
        e.name,
        e.manager_id,
        eh.level + 1,
        eh.path || ' > ' || e.name
    FROM
        employees e
    INNER JOIN
        employee_hierarchy eh ON e.manager_id = eh.id
    WHERE
        eh.level < 10  -- Prevent infinite recursion
)
SELECT * FROM employee_hierarchy ORDER BY path;
```

### Graph Traversal

```sql
WITH RECURSIVE connected_nodes AS (
    -- Start node
    SELECT
        node_id,
        1 as depth,
        ARRAY[node_id] as path
    FROM
        nodes
    WHERE
        node_id = 1

    UNION ALL

    -- Connected nodes
    SELECT
        e.to_node_id,
        cn.depth + 1,
        cn.path || e.to_node_id
    FROM
        edges e
    INNER JOIN
        connected_nodes cn ON e.from_node_id = cn.node_id
    WHERE
        NOT e.to_node_id = ANY(cn.path)  -- Prevent cycles
        AND cn.depth < 10
)
SELECT * FROM connected_nodes;
```

## Window Function Advanced Patterns

### Percentile Rankings

```sql
SELECT
    name,
    salary,
    department,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) as percentile
FROM
    employees;
```

### Running Aggregates with Frames

```sql
SELECT
    order_date,
    total_amount,
    -- Last 7 days average
    AVG(total_amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7days,
    -- Month to date total
    SUM(total_amount) OVER (
        PARTITION BY DATE_TRUNC('month', order_date)
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as mtd_total
FROM
    daily_sales;
```

### Gap and Island Detection

```sql
-- Find consecutive sequences
WITH numbered AS (
    SELECT
        id,
        value,
        ROW_NUMBER() OVER (ORDER BY id) -
        ROW_NUMBER() OVER (PARTITION BY value ORDER BY id) as grp
    FROM
        sequences
)
SELECT
    value,
    MIN(id) as start_id,
    MAX(id) as end_id,
    COUNT(*) as sequence_length
FROM
    numbered
GROUP BY
    value, grp
ORDER BY
    start_id;
```

## Common Table Expressions (CTEs)

### Multiple CTEs

```sql
WITH
    high_value_customers AS (
        SELECT user_id, SUM(total_amount) as lifetime_value
        FROM orders
        GROUP BY user_id
        HAVING SUM(total_amount) > 1000
    ),
    recent_orders AS (
        SELECT user_id, COUNT(*) as order_count
        FROM orders
        WHERE order_date > CURRENT_DATE - INTERVAL '30 days'
        GROUP BY user_id
    )
SELECT
    u.name,
    hvc.lifetime_value,
    COALESCE(ro.order_count, 0) as recent_order_count
FROM
    users u
INNER JOIN high_value_customers hvc ON u.id = hvc.user_id
LEFT JOIN recent_orders ro ON u.id = ro.user_id;
```

### Recursive CTE with Aggregation

```sql
WITH RECURSIVE category_totals AS (
    -- Leaf categories
    SELECT
        category_id,
        parent_category_id,
        category_name,
        (SELECT SUM(price) FROM products WHERE category_id = c.category_id) as total
    FROM
        categories c
    WHERE
        category_id NOT IN (SELECT parent_category_id FROM categories WHERE parent_category_id IS NOT NULL)

    UNION ALL

    -- Parent categories
    SELECT
        c.category_id,
        c.parent_category_id,
        c.category_name,
        ct.total
    FROM
        categories c
    INNER JOIN
        category_totals ct ON c.category_id = ct.parent_category_id
)
SELECT
    category_name,
    SUM(total) as category_total
FROM
    category_totals
GROUP BY
    category_id, category_name;
```
