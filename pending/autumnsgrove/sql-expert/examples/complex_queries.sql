-- ============================================================================
-- COMPLEX SQL QUERIES EXAMPLES
-- ============================================================================
-- This file demonstrates advanced SQL patterns including:
-- - Complex JOINs (INNER, LEFT, RIGHT, FULL OUTER, CROSS)
-- - Window Functions (ROW_NUMBER, RANK, LAG, LEAD, etc.)
-- - CTEs (Common Table Expressions)
-- - Subqueries (correlated and non-correlated)
-- - UPSERT operations
-- - JSON operations (PostgreSQL)
-- ============================================================================


-- ============================================================================
-- SECTION 1: COMPLEX JOINS
-- ============================================================================

-- Example 1.1: Multi-table JOIN with aggregation
-- Get customer order summary with product details
SELECT
    c.customer_id,
    c.name AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items,
    SUM(oi.quantity * oi.unit_price) AS total_spent,
    AVG(oi.quantity * oi.unit_price) AS avg_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE c.active = true
GROUP BY c.customer_id, c.name, c.email
HAVING COUNT(DISTINCT o.order_id) > 0
ORDER BY total_spent DESC;


-- Example 1.2: Self-JOIN to find related records
-- Find employees and their managers
SELECT
    e.employee_id,
    e.name AS employee_name,
    e.title AS employee_title,
    m.name AS manager_name,
    m.title AS manager_title
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
WHERE e.active = true
ORDER BY m.name, e.name;


-- Example 1.3: Complex JOIN with filtering on joined tables
-- Get products that have been ordered but never reviewed
SELECT
    p.product_id,
    p.name,
    p.category,
    COUNT(DISTINCT oi.order_id) AS times_ordered,
    SUM(oi.quantity) AS total_quantity_sold
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN reviews r ON p.product_id = r.product_id
WHERE r.review_id IS NULL  -- No reviews exist
GROUP BY p.product_id, p.name, p.category
HAVING COUNT(DISTINCT oi.order_id) >= 5
ORDER BY total_quantity_sold DESC;


-- Example 1.4: FULL OUTER JOIN to find mismatches
-- Find customers with orders but no profile, or profiles with no orders
SELECT
    COALESCE(c.customer_id, o.customer_id) AS customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS order_count,
    CASE
        WHEN c.customer_id IS NULL THEN 'Order without customer'
        WHEN o.customer_id IS NULL THEN 'Customer without orders'
        ELSE 'Complete'
    END AS status
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY COALESCE(c.customer_id, o.customer_id), c.name, c.email,
         CASE
             WHEN c.customer_id IS NULL THEN 'Order without customer'
             WHEN o.customer_id IS NULL THEN 'Customer without orders'
             ELSE 'Complete'
         END;


-- ============================================================================
-- SECTION 2: WINDOW FUNCTIONS
-- ============================================================================

-- Example 2.1: ROW_NUMBER for ranking within groups
-- Rank products by revenue within each category
SELECT
    category,
    product_name,
    total_revenue,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS dense_rank_in_category
FROM (
    SELECT
        p.category,
        p.name AS product_name,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.name
) product_revenue
ORDER BY category, rank_in_category;


-- Example 2.2: LAG and LEAD for time-series analysis
-- Compare each month's revenue to previous and next month
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month,
        SUM(total_amount) AS revenue
    FROM orders
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY month) AS previous_month_revenue,
    LEAD(revenue, 1) OVER (ORDER BY month) AS next_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS month_over_month_change,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY month)) * 100.0 /
        NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0),
        2
    ) AS percent_change
FROM monthly_revenue
ORDER BY month;


-- Example 2.3: Running totals with SUM OVER
-- Calculate running total of orders per customer
SELECT
    customer_id,
    order_id,
    order_date,
    total_amount,
    SUM(total_amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    AVG(total_amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3_orders
FROM orders
ORDER BY customer_id, order_date;


-- Example 2.4: NTILE for bucketing
-- Divide customers into quartiles by lifetime value
WITH customer_ltv AS (
    SELECT
        c.customer_id,
        c.name,
        COALESCE(SUM(o.total_amount), 0) AS lifetime_value
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
)
SELECT
    customer_id,
    name,
    lifetime_value,
    NTILE(4) OVER (ORDER BY lifetime_value DESC) AS value_quartile,
    CASE NTILE(4) OVER (ORDER BY lifetime_value DESC)
        WHEN 1 THEN 'VIP'
        WHEN 2 THEN 'High Value'
        WHEN 3 THEN 'Medium Value'
        WHEN 4 THEN 'Low Value'
    END AS customer_segment
FROM customer_ltv
ORDER BY lifetime_value DESC;


-- ============================================================================
-- SECTION 3: CTEs (COMMON TABLE EXPRESSIONS)
-- ============================================================================

-- Example 3.1: Simple CTE for code clarity
-- Find high-value customers who haven't ordered recently
WITH high_value_customers AS (
    SELECT
        customer_id,
        SUM(total_amount) AS lifetime_value
    FROM orders
    GROUP BY customer_id
    HAVING SUM(total_amount) > 1000
),
recent_orders AS (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT
    c.customer_id,
    c.name,
    c.email,
    hvc.lifetime_value,
    MAX(o.order_date) AS last_order_date,
    CURRENT_DATE - MAX(o.order_date) AS days_since_last_order
FROM customers c
INNER JOIN high_value_customers hvc ON c.customer_id = hvc.customer_id
LEFT JOIN recent_orders ro ON c.customer_id = ro.customer_id
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE ro.customer_id IS NULL  -- Not in recent orders
GROUP BY c.customer_id, c.name, c.email, hvc.lifetime_value
ORDER BY lifetime_value DESC;


-- Example 3.2: Recursive CTE for hierarchical data
-- Build employee hierarchy tree
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top-level managers (no manager)
    SELECT
        employee_id,
        name,
        manager_id,
        title,
        1 AS level,
        name AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees with managers
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        e.title,
        eh.level + 1,
        eh.path || ' > ' || e.name
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT
    employee_id,
    name,
    title,
    level,
    path,
    REPEAT('  ', level - 1) || name AS indented_name
FROM employee_hierarchy
ORDER BY path;


-- Example 3.3: Multiple CTEs for complex analysis
-- Customer cohort retention analysis
WITH first_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
customer_orders AS (
    SELECT
        o.customer_id,
        o.order_date,
        DATE_TRUNC('month', o.order_date) AS order_month,
        fo.cohort_month
    FROM orders o
    INNER JOIN first_orders fo ON o.customer_id = fo.customer_id
),
cohort_data AS (
    SELECT
        cohort_month,
        order_month,
        COUNT(DISTINCT customer_id) AS active_customers,
        EXTRACT(YEAR FROM AGE(order_month, cohort_month)) * 12 +
        EXTRACT(MONTH FROM AGE(order_month, cohort_month)) AS months_since_first
    FROM customer_orders
    GROUP BY cohort_month, order_month
)
SELECT
    cohort_month,
    months_since_first,
    active_customers,
    FIRST_VALUE(active_customers) OVER (
        PARTITION BY cohort_month
        ORDER BY months_since_first
    ) AS cohort_size,
    ROUND(
        active_customers * 100.0 / FIRST_VALUE(active_customers) OVER (
            PARTITION BY cohort_month
            ORDER BY months_since_first
        ),
        2
    ) AS retention_rate
FROM cohort_data
ORDER BY cohort_month, months_since_first;


-- ============================================================================
-- SECTION 4: SUBQUERIES
-- ============================================================================

-- Example 4.1: Correlated subquery
-- Find products priced above their category average
SELECT
    p.product_id,
    p.name,
    p.category,
    p.price,
    (
        SELECT AVG(price)
        FROM products p2
        WHERE p2.category = p.category
    ) AS category_avg_price,
    p.price - (
        SELECT AVG(price)
        FROM products p2
        WHERE p2.category = p.category
    ) AS price_vs_avg
FROM products p
WHERE p.price > (
    SELECT AVG(price)
    FROM products p2
    WHERE p2.category = p.category
)
ORDER BY category, price_vs_avg DESC;


-- Example 4.2: Subquery in SELECT clause
-- Add aggregated data to each row
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount,
    (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.order_id) AS item_count,
    (SELECT AVG(total_amount) FROM orders o2 WHERE o2.customer_id = o.customer_id) AS customer_avg_order,
    (SELECT COUNT(*) FROM orders o2 WHERE o2.customer_id = o.customer_id) AS customer_total_orders
FROM orders o
ORDER BY o.order_date DESC;


-- Example 4.3: Subquery with EXISTS
-- Find customers who have ordered from multiple categories
SELECT
    c.customer_id,
    c.name,
    c.email,
    (
        SELECT COUNT(DISTINCT p.category)
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        INNER JOIN products p ON oi.product_id = p.product_id
        WHERE o.customer_id = c.customer_id
    ) AS categories_purchased
FROM customers c
WHERE EXISTS (
    SELECT 1
    FROM orders o
    WHERE o.customer_id = c.customer_id
)
AND (
    SELECT COUNT(DISTINCT p.category)
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    WHERE o.customer_id = c.customer_id
) >= 3
ORDER BY categories_purchased DESC;


-- ============================================================================
-- SECTION 5: UPSERT OPERATIONS
-- ============================================================================

-- Example 5.1: PostgreSQL UPSERT (ON CONFLICT)
-- Insert or update product inventory
INSERT INTO inventory (product_id, warehouse_id, quantity, last_updated)
VALUES
    (101, 1, 50, CURRENT_TIMESTAMP),
    (102, 1, 30, CURRENT_TIMESTAMP),
    (103, 1, 75, CURRENT_TIMESTAMP)
ON CONFLICT (product_id, warehouse_id)
DO UPDATE SET
    quantity = inventory.quantity + EXCLUDED.quantity,
    last_updated = EXCLUDED.last_updated
RETURNING *;


-- Example 5.2: PostgreSQL UPSERT with conditional update
-- Update user stats only if new data is more recent
INSERT INTO user_stats (user_id, login_count, last_login, total_purchases)
VALUES ($1, 1, CURRENT_TIMESTAMP, 0)
ON CONFLICT (user_id)
DO UPDATE SET
    login_count = user_stats.login_count + 1,
    last_login = CASE
        WHEN EXCLUDED.last_login > user_stats.last_login
        THEN EXCLUDED.last_login
        ELSE user_stats.last_login
    END
WHERE EXCLUDED.last_login > user_stats.last_login;


-- Example 5.3: MySQL UPSERT (ON DUPLICATE KEY UPDATE)
-- For MySQL compatibility
INSERT INTO product_views (product_id, view_date, view_count)
VALUES (101, CURRENT_DATE, 1)
ON DUPLICATE KEY UPDATE
    view_count = view_count + VALUES(view_count);


-- Example 5.4: MERGE statement (PostgreSQL 15+, SQL Server)
-- Comprehensive merge operation
MERGE INTO customer_summary cs
USING (
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent,
        MAX(order_date) AS last_order_date
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY customer_id
) recent_orders
ON cs.customer_id = recent_orders.customer_id
WHEN MATCHED THEN
    UPDATE SET
        order_count = recent_orders.order_count,
        total_spent = recent_orders.total_spent,
        last_order_date = recent_orders.last_order_date,
        updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (customer_id, order_count, total_spent, last_order_date, updated_at)
    VALUES (recent_orders.customer_id, recent_orders.order_count,
            recent_orders.total_spent, recent_orders.last_order_date,
            CURRENT_TIMESTAMP);


-- ============================================================================
-- SECTION 6: JSON OPERATIONS (PostgreSQL)
-- ============================================================================

-- Example 6.1: Querying JSON columns
-- Extract data from JSONB column
SELECT
    order_id,
    customer_id,
    metadata->>'source' AS order_source,
    metadata->>'device' AS device_type,
    metadata->'items'->0->>'name' AS first_item_name,
    (metadata->>'item_count')::int AS item_count
FROM orders
WHERE metadata->>'source' = 'mobile_app'
AND (metadata->>'item_count')::int > 3;


-- Example 6.2: JSON aggregation
-- Build JSON objects from query results
SELECT
    c.customer_id,
    c.name,
    json_build_object(
        'total_orders', COUNT(o.order_id),
        'total_spent', COALESCE(SUM(o.total_amount), 0),
        'recent_orders', json_agg(
            json_build_object(
                'order_id', o.order_id,
                'order_date', o.order_date,
                'amount', o.total_amount
            ) ORDER BY o.order_date DESC
        ) FILTER (WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days')
    ) AS customer_summary
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;


-- Example 6.3: JSONB array operations
-- Find orders containing specific product in JSON array
SELECT
    order_id,
    customer_id,
    order_date,
    jsonb_array_length(items) AS item_count
FROM orders
WHERE items @> '[{"product_id": 101}]'  -- Contains product 101
OR items @> '[{"category": "electronics"}]';


-- Example 6.4: Update JSON fields
-- Update nested JSON data
UPDATE user_preferences
SET settings = jsonb_set(
    settings,
    '{notifications,email}',
    'true'::jsonb,
    true  -- create if not exists
)
WHERE user_id = 123;


-- Example 6.5: Complex JSON aggregation with grouping
-- Create hierarchical JSON structure
SELECT
    category,
    json_build_object(
        'category_name', category,
        'total_products', COUNT(DISTINCT product_id),
        'total_revenue', SUM(revenue),
        'top_products', json_agg(
            json_build_object(
                'product_name', product_name,
                'revenue', revenue,
                'units_sold', units_sold
            ) ORDER BY revenue DESC
        ) FILTER (WHERE product_rank <= 5)
    ) AS category_summary
FROM (
    SELECT
        p.category,
        p.product_id,
        p.name AS product_name,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        SUM(oi.quantity) AS units_sold,
        ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS product_rank
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_id, p.name
) ranked_products
GROUP BY category
ORDER BY SUM(revenue) DESC;


-- ============================================================================
-- SECTION 7: ADVANCED PATTERNS
-- ============================================================================

-- Example 7.1: Pivot table (dynamic columns)
-- Convert rows to columns for reporting
SELECT
    product_name,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN quantity ELSE 0 END) AS jan_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN quantity ELSE 0 END) AS feb_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN quantity ELSE 0 END) AS mar_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 4 THEN quantity ELSE 0 END) AS apr_sales,
    SUM(quantity) AS total_sales
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE EXTRACT(YEAR FROM o.order_date) = 2024
GROUP BY product_name
ORDER BY total_sales DESC;


-- Example 7.2: Gap and island detection
-- Find consecutive date ranges
WITH daily_orders AS (
    SELECT DISTINCT DATE(order_date) AS order_date
    FROM orders
    WHERE order_date >= '2024-01-01'
),
date_groups AS (
    SELECT
        order_date,
        order_date - (ROW_NUMBER() OVER (ORDER BY order_date) || ' days')::INTERVAL AS group_id
    FROM daily_orders
)
SELECT
    MIN(order_date) AS period_start,
    MAX(order_date) AS period_end,
    COUNT(*) AS consecutive_days
FROM date_groups
GROUP BY group_id
ORDER BY period_start;


-- Example 7.3: Running difference calculation
-- Find products with declining sales trend
WITH monthly_sales AS (
    SELECT
        p.product_id,
        p.name,
        DATE_TRUNC('month', o.order_date) AS month,
        SUM(oi.quantity) AS units_sold
    FROM products p
    INNER JOIN order_items oi ON p.product_id = oi.product_id
    INNER JOIN orders o ON oi.order_id = o.order_id
    GROUP BY p.product_id, p.name, DATE_TRUNC('month', o.order_date)
)
SELECT
    product_id,
    name,
    month,
    units_sold,
    LAG(units_sold, 1) OVER (PARTITION BY product_id ORDER BY month) AS prev_month_sales,
    units_sold - LAG(units_sold, 1) OVER (PARTITION BY product_id ORDER BY month) AS sales_change,
    COUNT(*) FILTER (
        WHERE units_sold < LAG(units_sold, 1) OVER (PARTITION BY product_id ORDER BY month)
    ) OVER (PARTITION BY product_id ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS declining_months
FROM monthly_sales
WHERE month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY product_id, month;
