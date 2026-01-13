# Database Migration Reference

## Naming Conventions

### Migration File Names

**Timestamp-based (most common):**
- Format: `YYYYMMDDHHMMSS_description.ext`
- Example: `20231215120000_create_users_table.js`
- Example: `20231215120001_add_email_index_to_users.sql`

**Sequential:**
- Format: `NNN_description.ext`
- Example: `001_create_users.sql`
- Example: `002_add_indexes.sql`

**Framework-specific:**
- Rails: `20231215120000_create_users.rb`
- Django: `0001_initial.py`, `0002_add_user_email.py`
- Alembic: `abc123def456_create_users.py`

### Description Format

**Action-based naming:**
- `create_<table_name>` - Create new table
- `add_<column>_to_<table>` - Add new column
- `remove_<column>_from_<table>` - Remove column
- `add_index_to_<table>_<column>` - Add index
- `rename_<old>_to_<new>_in_<table>` - Rename column
- `change_<column>_in_<table>` - Modify column type/constraint

**Examples:**
- ✓ `create_products_table`
- ✓ `add_user_id_to_posts`
- ✓ `add_index_to_users_email`
- ✓ `remove_deprecated_status_from_orders`
- ✗ `migration_1`
- ✗ `update_database`
- ✗ `fix`

## Common Migration Patterns

### Creating Tables

**Include:**
- Primary key (usually id)
- Timestamps (created_at, updated_at) if project uses them
- NOT NULL constraints for required fields
- Default values where appropriate
- Indexes on frequently queried columns
- Foreign keys for relationships

**Example structure:**
```
Table: users
- id (PK, UUID/Integer)
- email (unique, not null)
- name (nullable)
- created_at (timestamp)
- updated_at (timestamp)

Indexes:
- Primary key on id
- Unique index on email
```

### Altering Tables

**Add Column:**
- Specify data type
- Set nullable/not null
- Provide default value if adding to existing table with data
- Consider performance impact on large tables

**Remove Column:**
- Check for dependent code first
- Consider deprecation period
- Warn about data loss

**Modify Column:**
- Change type carefully (may require data conversion)
- Changing NOT NULL → NULL is safe
- Changing NULL → NOT NULL requires data backfill

### Indexes

**When to add:**
- Foreign key columns
- Columns used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY
- Columns used for uniqueness

**Index types:**
- **B-tree** (default): General purpose, range queries
- **Hash**: Equality comparisons only, faster than B-tree
- **GIN/GiST**: Full-text search, array columns (PostgreSQL)
- **Partial**: Index subset of rows matching condition

**Naming:**
- `idx_<table>_<column(s)>` - Regular index
- `unq_<table>_<column(s)>` - Unique index
- `fk_<table>_<column>` - Foreign key

### Foreign Keys

**Cascade options:**
- `ON DELETE CASCADE` - Delete child records when parent deleted
- `ON DELETE SET NULL` - Set foreign key to NULL when parent deleted
- `ON DELETE RESTRICT` - Prevent deletion of parent if children exist
- `ON UPDATE CASCADE` - Update foreign key when parent key changes

**When to use:**
- Enforce referential integrity
- Automatic cleanup with CASCADE
- Data consistency requirements

### Data Migrations

**Best practices:**
- Separate from schema migrations when possible
- Use batch processing for large datasets
- Consider timeouts and locks
- Test with production-like data volumes
- Make idempotent (safe to run multiple times)

**Batch processing example:**
```ruby
User.find_in_batches(batch_size: 1000) do |batch|
  batch.each do |user|
    user.update(normalized_email: user.email.downcase)
  end
end
```

## Migration Order

**When creating related structures:**

1. Create parent tables first
2. Create child tables
3. Add foreign keys
4. Add indexes (can be done last for better performance)

**When dropping:**

1. Drop foreign keys first
2. Drop indexes
3. Drop child tables
4. Drop parent tables

## Rollback Considerations

**Always provide rollback:**
- Test rollback in development
- Ensure data can be recovered or migration is safe to revert
- Document irreversible migrations clearly

**Irreversible operations:**
- Data deletion without backup
- Dropping columns with data
- Type changes that lose precision
- Destructive data transformations

**Handle gracefully:**
```ruby
def up
  # Migration code
end

def down
  raise ActiveRecord::IrreversibleMigration, "Cannot undo data deletion"
end
```

## Performance Considerations

**Large table migrations:**
- Add indexes CONCURRENTLY (PostgreSQL)
- Use online DDL features when available
- Schedule during low-traffic periods
- Consider blue-green deployments

**Locking:**
- `ADD COLUMN` - Usually quick, minimal lock
- `ADD INDEX` - Can lock table, use CONCURRENT
- `CHANGE COLUMN` - May require table rewrite
- `DROP COLUMN` - Usually quick in PostgreSQL

**PostgreSQL-specific:**
```sql
-- Non-blocking index creation
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Add column with default (fast in PG 11+)
ALTER TABLE users ADD COLUMN status INTEGER DEFAULT 0 NOT NULL;
```

## Testing Checklist

Before running migrations in production:

- [ ] Migration runs successfully on development database
- [ ] Rollback works correctly
- [ ] Schema changes match requirements
- [ ] No data loss occurs
- [ ] Application code is compatible with both old and new schema
- [ ] Performance impact is acceptable
- [ ] Tested on staging with production-like data
- [ ] Backup strategy is in place

## ORM-Specific Commands

### Prisma
```bash
npx prisma migrate dev --name description
npx prisma migrate deploy  # Production
npx prisma migrate reset    # Reset database
```

### Sequelize
```bash
npx sequelize-cli migration:generate --name description
npx sequelize-cli db:migrate
npx sequelize-cli db:migrate:undo
```

### Knex
```bash
npx knex migrate:make description
npx knex migrate:latest
npx knex migrate:rollback
```

### TypeORM
```bash
npm run typeorm migration:create src/migrations/Name
npm run typeorm migration:run
npm run typeorm migration:revert
```

### Alembic
```bash
alembic revision -m "description"
alembic upgrade head
alembic downgrade -1
```

### Rails
```bash
rails generate migration Name
rails db:migrate
rails db:rollback
```

### Django
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate app_name zero  # Rollback all
```
