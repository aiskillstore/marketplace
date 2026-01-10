-- Migration: YYYYMMDDHHMMSS_descriptive_migration_name.sql
-- Description: [Brief description of what this migration does]
-- Author: [Your Name]
-- Date: YYYY-MM-DD

-- ============================================================================
-- UP MIGRATION (Apply changes)
-- ============================================================================

BEGIN;

-- Step 1: Add new table
CREATE TABLE IF NOT EXISTS table_name (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  column_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Step 2: Add indexes
CREATE INDEX idx_table_column ON table_name(column_name);

-- Step 3: Add foreign key constraints
ALTER TABLE table_name
  ADD CONSTRAINT fk_table_column
  FOREIGN KEY (column_id) REFERENCES other_table(id)
  ON DELETE CASCADE;

-- Step 4: Data migration (if needed)
-- INSERT INTO table_name (column_name)
-- SELECT column FROM old_table;

-- Step 5: Add constraints after data migration
-- ALTER TABLE table_name
--   MODIFY COLUMN column_name VARCHAR(255) NOT NULL;

COMMIT;

-- ============================================================================
-- DOWN MIGRATION (Rollback changes)
-- ============================================================================

-- Uncomment to test rollback:
-- BEGIN;

-- Step 1: Drop constraints
-- ALTER TABLE table_name DROP FOREIGN KEY fk_table_column;

-- Step 2: Drop indexes
-- DROP INDEX idx_table_column ON table_name;

-- Step 3: Drop table
-- DROP TABLE IF EXISTS table_name;

-- COMMIT;

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Check table exists
-- SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
-- WHERE TABLE_SCHEMA = DATABASE()
-- AND TABLE_NAME = 'table_name';

-- Check indexes
-- SHOW INDEX FROM table_name;

-- Check foreign keys
-- SELECT CONSTRAINT_NAME, TABLE_NAME, REFERENCED_TABLE_NAME
-- FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
-- WHERE TABLE_SCHEMA = DATABASE()
-- AND TABLE_NAME = 'table_name'
-- AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ============================================================================
-- NOTES
-- ============================================================================

-- Estimated execution time: [X seconds on Y rows]
-- Requires downtime: [Yes/No]
-- Dependencies: [List migration dependencies]
-- Rollback plan: [Describe rollback steps if complex]
