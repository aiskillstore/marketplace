-- ============================================================================
-- DATABASE SCHEMA DESIGN EXAMPLES
-- ============================================================================
-- This file demonstrates proper database schema design including:
-- - Normalization (1NF, 2NF, 3NF, BCNF)
-- - One-to-many relationships
-- - Many-to-many relationships
-- - Self-referencing tables
-- - Indexes for performance
-- - Constraints for data integrity
-- ============================================================================


-- ============================================================================
-- SECTION 1: NORMALIZATION EXAMPLES
-- ============================================================================

-- Example 1.1: FIRST NORMAL FORM (1NF)
-- ============================================================================
-- 1NF Rules:
-- - Each column contains atomic (indivisible) values
-- - Each column contains values of a single type
-- - Each column has a unique name
-- - Order of rows and columns doesn't matter

-- BAD: Violates 1NF (multiple values in one column)
/*
CREATE TABLE customers_bad (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone_numbers VARCHAR(500),  -- "555-1234, 555-5678, 555-9999"
    addresses TEXT               -- Multiple addresses in one field
);
*/

-- GOOD: Follows 1NF (atomic values, separate related data)
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_phones (
    phone_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    phone_type VARCHAR(20) CHECK (phone_type IN ('mobile', 'home', 'work')),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (customer_id, phone_number)
);

CREATE TABLE customer_addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    address_type VARCHAR(20) CHECK (address_type IN ('billing', 'shipping', 'home')),
    street_address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) NOT NULL DEFAULT 'USA',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Example 1.2: SECOND NORMAL FORM (2NF)
-- ============================================================================
-- 2NF Rules:
-- - Must be in 1NF
-- - All non-key attributes must depend on the ENTIRE primary key
-- - Eliminate partial dependencies

-- BAD: Violates 2NF (product_name depends only on product_id, not the composite key)
/*
CREATE TABLE order_items_bad (
    order_id INTEGER,
    product_id INTEGER,
    product_name VARCHAR(100),    -- Partial dependency
    product_category VARCHAR(50),  -- Partial dependency
    quantity INTEGER,
    unit_price DECIMAL(10, 2),
    PRIMARY KEY (order_id, product_id)
);
*/

-- GOOD: Follows 2NF (separate product information)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
    ),
    total_amount DECIMAL(12, 2) CHECK (total_amount >= 0),
    shipping_address_id INTEGER REFERENCES customer_addresses(address_id),
    billing_address_id INTEGER REFERENCES customer_addresses(address_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    discount_percent DECIMAL(5, 2) DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 100),
    subtotal DECIMAL(12, 2) GENERATED ALWAYS AS (
        quantity * unit_price * (1 - discount_percent / 100)
    ) STORED,
    UNIQUE (order_id, product_id)
);


-- Example 1.3: THIRD NORMAL FORM (3NF)
-- ============================================================================
-- 3NF Rules:
-- - Must be in 2NF
-- - No transitive dependencies (non-key attributes depend only on primary key)

-- BAD: Violates 3NF (city_population depends on city, not employee_id)
/*
CREATE TABLE employees_bad (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(50),
    city_population INTEGER,  -- Transitive dependency via city
    city_timezone VARCHAR(50)  -- Transitive dependency via city
);
*/

-- GOOD: Follows 3NF (separate city information)
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    country VARCHAR(50) NOT NULL,
    population INTEGER,
    timezone VARCHAR(50),
    UNIQUE (name, state, country)
);

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    budget DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    department_id INTEGER REFERENCES departments(department_id),
    manager_id INTEGER REFERENCES employees(employee_id),
    city_id INTEGER REFERENCES cities(city_id),
    salary DECIMAL(10, 2) CHECK (salary >= 0),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- SECTION 2: RELATIONSHIP EXAMPLES
-- ============================================================================

-- Example 2.1: ONE-TO-MANY RELATIONSHIP
-- ============================================================================
-- One customer can have many orders
-- Already demonstrated above with customers -> orders
-- Key points:
-- - Foreign key in the "many" table (orders.customer_id)
-- - Index on foreign key for join performance

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);


-- Example 2.2: MANY-TO-MANY RELATIONSHIP
-- ============================================================================
-- Students can enroll in many courses, courses have many students
-- Requires a junction/bridge table

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    gpa DECIMAL(3, 2) CHECK (gpa BETWEEN 0.00 AND 4.00),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    credits INTEGER CHECK (credits > 0),
    department VARCHAR(50),
    max_students INTEGER CHECK (max_students > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for many-to-many relationship
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    grade VARCHAR(2) CHECK (grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W', 'I')),
    status VARCHAR(20) DEFAULT 'active' CHECK (
        status IN ('active', 'completed', 'withdrawn', 'failed')
    ),
    final_score DECIMAL(5, 2) CHECK (final_score BETWEEN 0 AND 100),
    UNIQUE (student_id, course_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);


-- Example 2.3: MANY-TO-MANY WITH ATTRIBUTES
-- ============================================================================
-- Products can have many tags, tags can belong to many products
-- Junction table stores additional metadata

CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7),  -- Hex color code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product_tags (
    product_tag_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,  -- For ordering tags
    added_by INTEGER REFERENCES employees(employee_id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, tag_id)
);

CREATE INDEX idx_product_tags_product_id ON product_tags(product_id);
CREATE INDEX idx_product_tags_tag_id ON product_tags(tag_id);


-- Example 2.4: SELF-REFERENCING RELATIONSHIP
-- ============================================================================
-- Employees table with manager hierarchy (already shown above)
-- Categories with parent-child relationships

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Prevent circular references
    CHECK (category_id != parent_category_id)
);

CREATE INDEX idx_categories_parent_id ON categories(parent_category_id);
CREATE INDEX idx_categories_slug ON categories(slug);


-- ============================================================================
-- SECTION 3: ADVANCED CONSTRAINTS
-- ============================================================================

-- Example 3.1: CHECK constraints with complex logic
CREATE TABLE promotions (
    promotion_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value DECIMAL(10, 2) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    min_purchase_amount DECIMAL(10, 2) DEFAULT 0,
    max_discount_amount DECIMAL(10, 2),
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Ensure end_date is after start_date
    CHECK (end_date > start_date),
    -- Percentage discounts should be between 0 and 100
    CHECK (
        (discount_type = 'percentage' AND discount_value BETWEEN 0 AND 100)
        OR discount_type = 'fixed_amount'
    ),
    -- Usage count cannot exceed limit
    CHECK (usage_limit IS NULL OR usage_count <= usage_limit)
);


-- Example 3.2: UNIQUE constraints on multiple columns
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    warehouse_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reserved_quantity INTEGER DEFAULT 0 CHECK (reserved_quantity >= 0),
    reorder_point INTEGER CHECK (reorder_point >= 0),
    last_stock_check TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- One inventory record per product per warehouse
    UNIQUE (product_id, warehouse_id),
    -- Reserved quantity cannot exceed total quantity
    CHECK (reserved_quantity <= quantity)
);


-- Example 3.3: EXCLUSION constraints (PostgreSQL specific)
-- Prevent overlapping date ranges
CREATE TABLE employee_shifts (
    shift_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
    shift_start TIMESTAMP NOT NULL,
    shift_end TIMESTAMP NOT NULL,
    shift_type VARCHAR(20) CHECK (shift_type IN ('morning', 'afternoon', 'night')),
    CHECK (shift_end > shift_start)
);

-- Create an exclusion constraint to prevent overlapping shifts
-- Requires btree_gist extension
-- CREATE EXTENSION IF NOT EXISTS btree_gist;
-- ALTER TABLE employee_shifts
-- ADD CONSTRAINT no_overlapping_shifts
-- EXCLUDE USING gist (
--     employee_id WITH =,
--     tsrange(shift_start, shift_end) WITH &&
-- );


-- ============================================================================
-- SECTION 4: INDEXES FOR PERFORMANCE
-- ============================================================================

-- Example 4.1: B-tree indexes (default) for equality and range queries
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_last_name ON customers(last_name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(base_price);

-- Composite indexes for multi-column queries
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);
CREATE INDEX idx_order_items_product_order ON order_items(product_id, order_id);

-- Example 4.2: Partial indexes for filtered queries
-- Index only active products
CREATE INDEX idx_products_active ON products(product_id) WHERE is_active = true;

-- Index only recent orders
CREATE INDEX idx_orders_recent ON orders(order_date DESC)
WHERE order_date >= CURRENT_DATE - INTERVAL '1 year';

-- Index only pending orders
CREATE INDEX idx_orders_pending ON orders(customer_id, order_date)
WHERE status = 'pending';


-- Example 4.3: Expression indexes (functional indexes)
-- Index on lowercased email for case-insensitive searches
CREATE INDEX idx_customers_email_lower ON customers(LOWER(email));

-- Index on extracted year-month for grouping
CREATE INDEX idx_orders_year_month ON orders(
    EXTRACT(YEAR FROM order_date),
    EXTRACT(MONTH FROM order_date)
);


-- Example 4.4: Full-text search indexes (PostgreSQL)
-- Add tsvector column for full-text search
ALTER TABLE products ADD COLUMN search_vector tsvector;

-- Create trigger to maintain search vector
CREATE OR REPLACE FUNCTION products_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_search_update
    BEFORE INSERT OR UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION products_search_trigger();

-- Create GIN index for full-text search
CREATE INDEX idx_products_search ON products USING GIN(search_vector);


-- Example 4.5: JSON indexes (PostgreSQL)
-- For JSONB columns
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES customers(customer_id),
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GIN index for general JSONB queries
CREATE INDEX idx_user_preferences_settings ON user_preferences USING GIN(settings);

-- Index on specific JSONB path
CREATE INDEX idx_user_preferences_notifications ON user_preferences(
    (settings->'notifications'->>'email')
);


-- ============================================================================
-- SECTION 5: AUDIT AND VERSIONING
-- ============================================================================

-- Example 5.1: Audit table with triggers
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by INTEGER REFERENCES employees(employee_id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at DESC);


-- Example 5.2: Soft delete pattern
CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    author_id INTEGER REFERENCES employees(employee_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    deleted_by INTEGER REFERENCES employees(employee_id)
);

-- Index excluding deleted records for performance
CREATE INDEX idx_documents_active ON documents(document_id)
WHERE deleted_at IS NULL;


-- Example 5.3: Versioning table
CREATE TABLE document_versions (
    version_id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_by INTEGER REFERENCES employees(employee_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_description TEXT,
    UNIQUE (document_id, version_number)
);

CREATE INDEX idx_document_versions_document ON document_versions(document_id, version_number DESC);


-- ============================================================================
-- SECTION 6: PERFORMANCE AND ANALYTICS TABLES
-- ============================================================================

-- Example 6.1: Summary/materialized table
CREATE TABLE daily_sales_summary (
    summary_date DATE PRIMARY KEY,
    total_orders INTEGER DEFAULT 0,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    total_items_sold INTEGER DEFAULT 0,
    unique_customers INTEGER DEFAULT 0,
    avg_order_value DECIMAL(10, 2),
    top_product_id INTEGER REFERENCES products(product_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Example 6.2: Partitioning large tables (PostgreSQL 10+)
-- Partition orders by year
CREATE TABLE orders_partitioned (
    order_id SERIAL,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),
    total_amount DECIMAL(12, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (order_date);

-- Create partitions for each year
CREATE TABLE orders_2023 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');


-- ============================================================================
-- SECTION 7: EXAMPLE QUERIES FOR THIS SCHEMA
-- ============================================================================

-- Query 7.1: Get customer order history with details
/*
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS lifetime_value,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY lifetime_value DESC;
*/

-- Query 7.2: Get product sales performance
/*
SELECT
    p.product_id,
    p.name,
    p.category,
    COUNT(DISTINCT oi.order_id) AS times_ordered,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.subtotal) AS total_revenue,
    AVG(oi.unit_price) AS avg_selling_price,
    p.stock_quantity AS current_stock
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name, p.category, p.stock_quantity
ORDER BY total_revenue DESC;
*/

-- Query 7.3: Get category hierarchy
/*
WITH RECURSIVE category_tree AS (
    SELECT
        category_id,
        name,
        parent_category_id,
        1 AS level,
        name::TEXT AS path
    FROM categories
    WHERE parent_category_id IS NULL

    UNION ALL

    SELECT
        c.category_id,
        c.name,
        c.parent_category_id,
        ct.level + 1,
        ct.path || ' > ' || c.name
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_category_id = ct.category_id
)
SELECT * FROM category_tree ORDER BY path;
*/
