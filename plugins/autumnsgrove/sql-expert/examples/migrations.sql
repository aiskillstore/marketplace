-- ============================================================================
-- DATABASE MIGRATION EXAMPLES
-- ============================================================================
-- This file demonstrates safe database migration patterns including:
-- - Adding columns safely
-- - Renaming columns and tables
-- - Creating indexes online
-- - Modifying constraints
-- - Zero-downtime migration strategies
-- - Rollback patterns
-- ============================================================================

-- Migration Best Practices:
-- 1. Always make migrations reversible
-- 2. Test migrations on a copy of production data
-- 3. Use transactions where possible
-- 4. For large tables, use CONCURRENTLY for indexes
-- 5. Backfill data in separate transactions
-- 6. Validate data after migration
-- 7. Keep the application compatible during migration


-- ============================================================================
-- SECTION 1: ADDING COLUMNS SAFELY
-- ============================================================================

-- Migration 1.1: Add a nullable column (safe, instant)
-- ============================================================================
-- UP
ALTER TABLE customers
ADD COLUMN phone_verified BOOLEAN;

-- Add default value in separate statement (safer for large tables)
ALTER TABLE customers
ALTER COLUMN phone_verified SET DEFAULT false;

-- Backfill existing rows (do this in batches for large tables)
UPDATE customers
SET phone_verified = false
WHERE phone_verified IS NULL;

-- Make NOT NULL after backfill
ALTER TABLE customers
ALTER COLUMN phone_verified SET NOT NULL;

-- DOWN (rollback)
ALTER TABLE customers
DROP COLUMN phone_verified;


-- Migration 1.2: Add column with default value (PostgreSQL 11+)
-- ============================================================================
-- Modern PostgreSQL can add columns with defaults without rewriting table
-- UP
ALTER TABLE products
ADD COLUMN featured BOOLEAN NOT NULL DEFAULT false;

-- DOWN
ALTER TABLE products
DROP COLUMN featured;


-- Migration 1.3: Add column with complex default
-- ============================================================================
-- For computed defaults, add nullable first, then backfill
-- UP
ALTER TABLE orders
ADD COLUMN order_number VARCHAR(50);

-- Generate order numbers for existing records
UPDATE orders
SET order_number = 'ORD-' || TO_CHAR(order_date, 'YYYYMMDD') || '-' || LPAD(order_id::TEXT, 6, '0')
WHERE order_number IS NULL;

-- Add unique constraint
ALTER TABLE orders
ADD CONSTRAINT uq_orders_order_number UNIQUE (order_number);

-- Make NOT NULL
ALTER TABLE orders
ALTER COLUMN order_number SET NOT NULL;

-- DOWN
ALTER TABLE orders
DROP CONSTRAINT uq_orders_order_number;

ALTER TABLE orders
DROP COLUMN order_number;


-- ============================================================================
-- SECTION 2: RENAMING COLUMNS AND TABLES
-- ============================================================================

-- Migration 2.1: Rename a column (safe in PostgreSQL, requires app changes)
-- ============================================================================
-- UP
ALTER TABLE customers
RENAME COLUMN name TO full_name;

-- Update views or functions that reference the old column name
-- CREATE OR REPLACE VIEW customer_summary AS ...

-- DOWN
ALTER TABLE customers
RENAME COLUMN full_name TO name;


-- Migration 2.2: Rename column with zero-downtime (dual-write pattern)
-- ============================================================================
-- Step 1: Add new column
-- UP
ALTER TABLE employees
ADD COLUMN employment_status VARCHAR(20);

-- Copy data from old column
UPDATE employees
SET employment_status = status
WHERE employment_status IS NULL;

-- Add constraints to new column
ALTER TABLE employees
ADD CONSTRAINT chk_employment_status
CHECK (employment_status IN ('active', 'inactive', 'terminated', 'on_leave'));

-- Step 2: (After app is updated to write to both columns)
-- Make new column NOT NULL
ALTER TABLE employees
ALTER COLUMN employment_status SET NOT NULL;

-- Step 3: (After app is updated to read from new column)
-- Remove old column
ALTER TABLE employees
DROP COLUMN status;

-- DOWN (reverse the steps)
ALTER TABLE employees
ADD COLUMN status VARCHAR(20);

UPDATE employees
SET status = employment_status;

ALTER TABLE employees
DROP COLUMN employment_status;


-- Migration 2.3: Rename a table (simple but requires app changes)
-- ============================================================================
-- UP
ALTER TABLE user_sessions
RENAME TO sessions;

-- Update sequences if they exist
ALTER SEQUENCE user_sessions_session_id_seq
RENAME TO sessions_session_id_seq;

-- Update indexes
ALTER INDEX idx_user_sessions_user_id
RENAME TO idx_sessions_user_id;

-- DOWN
ALTER TABLE sessions
RENAME TO user_sessions;

ALTER SEQUENCE sessions_session_id_seq
RENAME TO user_sessions_session_id_seq;

ALTER INDEX idx_sessions_user_id
RENAME TO idx_user_sessions_user_id;


-- ============================================================================
-- SECTION 3: CREATING AND REMOVING INDEXES
-- ============================================================================

-- Migration 3.1: Add index CONCURRENTLY (zero-downtime)
-- ============================================================================
-- CONCURRENTLY prevents blocking reads/writes
-- Cannot be run in a transaction block
-- UP
CREATE INDEX CONCURRENTLY idx_orders_customer_status
ON orders(customer_id, status)
WHERE status IN ('pending', 'processing');

-- Verify index was created successfully
-- SELECT * FROM pg_indexes WHERE indexname = 'idx_orders_customer_status';

-- DOWN
DROP INDEX CONCURRENTLY IF EXISTS idx_orders_customer_status;


-- Migration 3.2: Add composite index for query optimization
-- ============================================================================
-- UP
CREATE INDEX CONCURRENTLY idx_order_items_product_date
ON order_items(product_id, order_id)
INCLUDE (quantity, unit_price);  -- PostgreSQL 11+

-- DOWN
DROP INDEX CONCURRENTLY IF EXISTS idx_order_items_product_date;


-- Migration 3.3: Replace an existing index
-- ============================================================================
-- UP
-- Create new index first
CREATE INDEX CONCURRENTLY idx_products_category_active_new
ON products(category, is_active)
WHERE is_active = true;

-- Verify new index is created and valid
-- SELECT schemaname, tablename, indexname, indexdef
-- FROM pg_indexes
-- WHERE indexname = 'idx_products_category_active_new';

-- Drop old index
DROP INDEX CONCURRENTLY IF EXISTS idx_products_category;

-- Rename new index to old name
ALTER INDEX idx_products_category_active_new
RENAME TO idx_products_category;

-- DOWN
CREATE INDEX CONCURRENTLY idx_products_category_old
ON products(category);

DROP INDEX CONCURRENTLY IF EXISTS idx_products_category;

ALTER INDEX idx_products_category_old
RENAME TO idx_products_category;


-- ============================================================================
-- SECTION 4: MODIFYING CONSTRAINTS
-- ============================================================================

-- Migration 4.1: Add a NOT NULL constraint safely
-- ============================================================================
-- UP
-- First, ensure no NULL values exist
UPDATE products
SET description = 'No description'
WHERE description IS NULL;

-- Add NOT NULL constraint
ALTER TABLE products
ALTER COLUMN description SET NOT NULL;

-- DOWN
ALTER TABLE products
ALTER COLUMN description DROP NOT NULL;


-- Migration 4.2: Add CHECK constraint (validate in steps)
-- ============================================================================
-- UP
-- Add constraint as NOT VALID first (doesn't block writes)
ALTER TABLE orders
ADD CONSTRAINT chk_orders_total_positive
CHECK (total_amount >= 0) NOT VALID;

-- Validate existing data in a separate transaction
-- This can be done during low-traffic period
ALTER TABLE orders
VALIDATE CONSTRAINT chk_orders_total_positive;

-- DOWN
ALTER TABLE orders
DROP CONSTRAINT chk_orders_total_positive;


-- Migration 4.3: Add foreign key constraint safely
-- ============================================================================
-- UP
-- First verify data integrity
-- SELECT o.order_id, o.customer_id
-- FROM orders o
-- LEFT JOIN customers c ON o.customer_id = c.customer_id
-- WHERE c.customer_id IS NULL;

-- Add constraint as NOT VALID
ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
NOT VALID;

-- Validate in separate transaction
ALTER TABLE orders
VALIDATE CONSTRAINT fk_orders_customer;

-- DOWN
ALTER TABLE orders
DROP CONSTRAINT fk_orders_customer;


-- Migration 4.4: Modify CHECK constraint
-- ============================================================================
-- UP
-- Cannot modify constraint directly, must drop and recreate
ALTER TABLE products
DROP CONSTRAINT IF EXISTS chk_products_price;

ALTER TABLE products
ADD CONSTRAINT chk_products_price
CHECK (base_price > 0 AND base_price < 1000000);

-- DOWN
ALTER TABLE products
DROP CONSTRAINT IF EXISTS chk_products_price;

ALTER TABLE products
ADD CONSTRAINT chk_products_price
CHECK (base_price >= 0);


-- ============================================================================
-- SECTION 5: CHANGING COLUMN TYPES
-- ============================================================================

-- Migration 5.1: Change column type (compatible types)
-- ============================================================================
-- UP
-- Compatible change (VARCHAR to TEXT, INT to BIGINT)
ALTER TABLE customers
ALTER COLUMN email TYPE TEXT;

-- DOWN
ALTER TABLE customers
ALTER COLUMN email TYPE VARCHAR(100);


-- Migration 5.2: Change column type (incompatible, requires conversion)
-- ============================================================================
-- UP
-- Add new column with desired type
ALTER TABLE products
ADD COLUMN price_in_cents BIGINT;

-- Convert and copy data
UPDATE products
SET price_in_cents = (base_price * 100)::BIGINT;

-- Make NOT NULL after backfill
ALTER TABLE products
ALTER COLUMN price_in_cents SET NOT NULL;

-- (After app is updated to use new column)
-- Drop old column
ALTER TABLE products
DROP COLUMN base_price;

-- Rename new column
ALTER TABLE products
RENAME COLUMN price_in_cents TO base_price;

-- DOWN
ALTER TABLE products
RENAME COLUMN base_price TO price_in_cents;

ALTER TABLE products
ADD COLUMN base_price DECIMAL(10, 2);

UPDATE products
SET base_price = price_in_cents / 100.0;

ALTER TABLE products
DROP COLUMN price_in_cents;


-- Migration 5.3: Change column type with USING clause
-- ============================================================================
-- UP
-- Convert JSON column to JSONB
ALTER TABLE user_preferences
ALTER COLUMN settings TYPE JSONB USING settings::JSONB;

-- Convert VARCHAR to INTEGER
ALTER TABLE legacy_table
ALTER COLUMN old_id TYPE INTEGER USING old_id::INTEGER;

-- DOWN
ALTER TABLE user_preferences
ALTER COLUMN settings TYPE JSON USING settings::JSON;


-- ============================================================================
-- SECTION 6: ZERO-DOWNTIME MIGRATIONS
-- ============================================================================

-- Migration 6.1: Split a column into multiple columns
-- ============================================================================
-- Original: customers.name (contains "First Last")
-- Goal: customers.first_name and customers.last_name

-- UP - Step 1: Add new columns
ALTER TABLE customers
ADD COLUMN first_name VARCHAR(50),
ADD COLUMN last_name VARCHAR(50);

-- UP - Step 2: Backfill data
UPDATE customers
SET
    first_name = SPLIT_PART(name, ' ', 1),
    last_name = SPLIT_PART(name, ' ', 2)
WHERE first_name IS NULL;

-- UP - Step 3: (After app updated to write to new columns)
-- Make columns NOT NULL
ALTER TABLE customers
ALTER COLUMN first_name SET NOT NULL,
ALTER COLUMN last_name SET NOT NULL;

-- UP - Step 4: (After app updated to read from new columns)
-- Drop old column
ALTER TABLE customers
DROP COLUMN name;

-- DOWN - Reverse the process
ALTER TABLE customers
ADD COLUMN name VARCHAR(100);

UPDATE customers
SET name = first_name || ' ' || last_name;

ALTER TABLE customers
DROP COLUMN first_name,
DROP COLUMN last_name;


-- Migration 6.2: Move column to a new table (extract relationship)
-- ============================================================================
-- Original: products.supplier_name, products.supplier_contact
-- Goal: New suppliers table with one-to-many relationship

-- UP - Step 1: Create new table
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name)
);

-- UP - Step 2: Add foreign key column to products
ALTER TABLE products
ADD COLUMN supplier_id INTEGER REFERENCES suppliers(supplier_id);

-- UP - Step 3: Migrate data
INSERT INTO suppliers (name, contact)
SELECT DISTINCT
    supplier_name,
    supplier_contact
FROM products
WHERE supplier_name IS NOT NULL
ON CONFLICT (name) DO NOTHING;

-- UP - Step 4: Update foreign keys
UPDATE products p
SET supplier_id = s.supplier_id
FROM suppliers s
WHERE p.supplier_name = s.name;

-- UP - Step 5: (After app updated) Drop old columns
ALTER TABLE products
DROP COLUMN supplier_name,
DROP COLUMN supplier_contact;

-- DOWN - Reverse migration
ALTER TABLE products
ADD COLUMN supplier_name VARCHAR(100),
ADD COLUMN supplier_contact VARCHAR(100);

UPDATE products p
SET
    supplier_name = s.name,
    supplier_contact = s.contact
FROM suppliers s
WHERE p.supplier_id = s.supplier_id;

ALTER TABLE products
DROP COLUMN supplier_id;

DROP TABLE suppliers;


-- ============================================================================
-- SECTION 7: DATA MIGRATIONS
-- ============================================================================

-- Migration 7.1: Batch update for large tables
-- ============================================================================
-- Instead of updating all rows at once, process in batches

DO $$
DECLARE
    batch_size INTEGER := 1000;
    rows_updated INTEGER;
BEGIN
    LOOP
        -- Update a batch
        WITH batch AS (
            SELECT order_id
            FROM orders
            WHERE processed = false
            LIMIT batch_size
            FOR UPDATE SKIP LOCKED
        )
        UPDATE orders o
        SET
            processed = true,
            processed_at = CURRENT_TIMESTAMP
        FROM batch
        WHERE o.order_id = batch.order_id;

        GET DIAGNOSTICS rows_updated = ROW_COUNT;

        -- Exit if no more rows to update
        EXIT WHEN rows_updated = 0;

        -- Commit and pause to avoid lock contention
        COMMIT;
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;


-- Migration 7.2: Backfill with progress tracking
-- ============================================================================
CREATE TABLE migration_progress (
    migration_name VARCHAR(100) PRIMARY KEY,
    last_processed_id INTEGER,
    total_rows INTEGER,
    processed_rows INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize progress tracking
INSERT INTO migration_progress (migration_name, total_rows, processed_rows)
VALUES ('backfill_customer_tier', (SELECT COUNT(*) FROM customers), 0);

-- Backfill in batches with progress tracking
DO $$
DECLARE
    batch_size INTEGER := 1000;
    last_id INTEGER := 0;
    rows_updated INTEGER;
BEGIN
    -- Get last processed ID if migration was interrupted
    SELECT COALESCE(last_processed_id, 0)
    INTO last_id
    FROM migration_progress
    WHERE migration_name = 'backfill_customer_tier';

    LOOP
        -- Update batch
        WITH batch AS (
            SELECT customer_id
            FROM customers
            WHERE customer_id > last_id
            ORDER BY customer_id
            LIMIT batch_size
        )
        UPDATE customers c
        SET tier = CASE
            WHEN (SELECT SUM(total_amount) FROM orders WHERE customer_id = c.customer_id) > 1000 THEN 'gold'
            WHEN (SELECT SUM(total_amount) FROM orders WHERE customer_id = c.customer_id) > 500 THEN 'silver'
            ELSE 'bronze'
        END
        FROM batch
        WHERE c.customer_id = batch.customer_id;

        GET DIAGNOSTICS rows_updated = ROW_COUNT;
        EXIT WHEN rows_updated = 0;

        -- Update progress
        SELECT MAX(customer_id) INTO last_id FROM customers WHERE customer_id > last_id LIMIT batch_size;

        UPDATE migration_progress
        SET
            last_processed_id = last_id,
            processed_rows = processed_rows + rows_updated,
            updated_at = CURRENT_TIMESTAMP
        WHERE migration_name = 'backfill_customer_tier';

        COMMIT;
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;


-- Migration 7.3: Deduplication migration
-- ============================================================================
-- Remove duplicate records, keeping the most recent
WITH duplicates AS (
    SELECT
        customer_id,
        email,
        ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) AS rn
    FROM customers
)
DELETE FROM customers
WHERE customer_id IN (
    SELECT customer_id
    FROM duplicates
    WHERE rn > 1
);


-- ============================================================================
-- SECTION 8: ROLLBACK AND VALIDATION
-- ============================================================================

-- Migration 8.1: Migration with validation
-- ============================================================================
-- UP
BEGIN;

-- Make the change
ALTER TABLE products
ADD COLUMN sku VARCHAR(50);

-- Validate the change
DO $$
BEGIN
    -- Check column exists
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'products'
        AND column_name = 'sku'
    ) THEN
        RAISE EXCEPTION 'Column sku was not created';
    END IF;
END $$;

COMMIT;


-- Migration 8.2: Migration with automatic rollback on error
-- ============================================================================
DO $$
BEGIN
    -- Attempt migration
    ALTER TABLE customers ADD COLUMN loyalty_points INTEGER DEFAULT 0;

    -- Validate data
    IF EXISTS (SELECT 1 FROM customers WHERE loyalty_points IS NULL) THEN
        RAISE EXCEPTION 'Found NULL loyalty_points after migration';
    END IF;

    -- If we get here, migration succeeded
    RAISE NOTICE 'Migration completed successfully';

EXCEPTION
    WHEN OTHERS THEN
        -- Rollback happens automatically
        RAISE NOTICE 'Migration failed: %', SQLERRM;
        RAISE;
END $$;


-- Migration 8.3: Create migration log table
-- ============================================================================
CREATE TABLE schema_migrations (
    migration_id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100),
    execution_time INTERVAL,
    success BOOLEAN DEFAULT true,
    error_message TEXT
);

-- Record migration
INSERT INTO schema_migrations (version, description, applied_by)
VALUES ('2024_01_15_001', 'Add customer tier column', CURRENT_USER);


-- ============================================================================
-- SECTION 9: COMPLEX MIGRATION SCENARIOS
-- ============================================================================

-- Migration 9.1: Merge two tables
-- ============================================================================
-- Merge user_profiles into users table

-- UP
-- Add columns from user_profiles to users
ALTER TABLE users
ADD COLUMN bio TEXT,
ADD COLUMN avatar_url VARCHAR(500),
ADD COLUMN date_of_birth DATE;

-- Copy data
UPDATE users u
SET
    bio = up.bio,
    avatar_url = up.avatar_url,
    date_of_birth = up.date_of_birth
FROM user_profiles up
WHERE u.user_id = up.user_id;

-- (After verification) Drop old table
-- DROP TABLE user_profiles;


-- Migration 9.2: Partition existing table
-- ============================================================================
-- Convert regular table to partitioned table

-- Create new partitioned table
CREATE TABLE orders_new (
    LIKE orders INCLUDING ALL
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2023 PARTITION OF orders_new
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_new
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Copy data
INSERT INTO orders_new SELECT * FROM orders;

-- Swap tables (requires brief downtime)
-- BEGIN;
-- ALTER TABLE orders RENAME TO orders_old;
-- ALTER TABLE orders_new RENAME TO orders;
-- COMMIT;

-- (After verification) Drop old table
-- DROP TABLE orders_old;


-- ============================================================================
-- SECTION 10: MIGRATION TEMPLATES
-- ============================================================================

-- Template 10.1: Standard migration template
-- ============================================================================
/*
-- Migration: [YYYY_MM_DD_NNN_description]
-- Description: [What this migration does]
-- Dependencies: [List any dependent migrations]

-- UP
BEGIN;

-- Your migration code here


-- Record migration
INSERT INTO schema_migrations (version, description)
VALUES ('2024_01_15_001', 'Description of migration');

COMMIT;

-- Validation queries
-- SELECT COUNT(*) FROM ...;

-- DOWN (Rollback)
BEGIN;

-- Reverse migration code here


-- Remove migration record
DELETE FROM schema_migrations WHERE version = '2024_01_15_001';

COMMIT;
*/
