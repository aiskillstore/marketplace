---
name: database-migration-helper
description: Creates database migration files following project conventions for Prisma, Sequelize, Alembic, Knex, TypeORM, and other ORMs. Use when adding tables, modifying schemas, or when user mentions database changes.
allowed-tools: Read, Grep, Glob, Write, Bash
---

# Database Migration Helper

This skill helps you create database migration files that follow your project's ORM conventions and naming patterns.

## When to Use This Skill

- User requests to create a database migration
- Adding new tables or columns to the database
- Modifying existing database schema
- Creating indexes, constraints, or relationships
- User mentions "migration", "schema change", or "database update"

## Instructions

### 1. Detect the ORM/Migration Tool

First, identify which ORM or migration tool the project uses:

- **Prisma**: Look for `prisma/schema.prisma` or `@prisma/client` in package.json
- **Sequelize**: Look for `.sequelizerc` or `sequelize-cli` in package.json
- **Knex**: Look for `knexfile.js` or `knex` in package.json
- **TypeORM**: Look for `ormconfig.json` or `typeorm` in package.json
- **Alembic** (Python): Look for `alembic.ini` or `alembic/` directory
- **Django**: Look for `manage.py` and Django migrations in `*/migrations/`
- **Active Record** (Rails): Look for `db/migrate/` directory
- **Flyway**: Look for `flyway.conf` or `db/migration/`
- **Liquibase**: Look for `liquibase.properties` or changelog files

Use Glob to search for these indicator files.

### 2. Examine Existing Migrations

Read existing migration files to understand:

- Naming conventions (timestamp format, description format)
- Directory structure
- Migration file format (SQL, JavaScript, TypeScript, Python, etc.)
- Coding patterns (up/down functions, forwards/rollback, etc.)

Use Grep to find recent migrations: look in common directories like:
- `prisma/migrations/`
- `db/migrate/`
- `migrations/` or `database/migrations/`
- `alembic/versions/`

### 3. Generate Migration File

Based on the detected ORM, create an appropriate migration file:

#### Prisma
- Run `npx prisma migrate dev --name <description>` OR
- Manually create migration SQL in `prisma/migrations/<timestamp>_<name>/migration.sql`

#### Sequelize
- Generate: `npx sequelize-cli migration:generate --name <description>`
- Then fill in the up/down functions with the schema changes

#### Knex
- Generate: `npx knex migrate:make <description>`
- Fill in exports.up and exports.down functions

#### TypeORM
- Generate: `npm run typeorm migration:create src/migrations/<Name>`
- Implement up() and down() methods

#### Alembic
- Generate: `alembic revision -m "<description>"`
- Fill in upgrade() and downgrade() functions

#### Django
- Run: `python manage.py makemigrations`
- Or manually create migration in `<app>/migrations/`

#### Rails
- Generate: `rails generate migration <ClassName>`
- Fill in the change method (or up/down for complex migrations)

### 4. Follow Naming Conventions

Use consistent, descriptive names:

- **Good**: `add_user_email_index`, `create_products_table`, `add_payment_status_to_orders`
- **Bad**: `migration1`, `update`, `fix`

Format based on project patterns:
- Timestamp prefix: `20231215120000_add_email_to_users`
- Sequential: `001_create_users`, `002_add_indexes`

### 5. Include Both Up and Down/Rollback

Always provide both directions when supported:

- **Up/Upgrade/Forward**: Apply the schema change
- **Down/Downgrade/Rollback**: Revert the schema change

For ORMs that use reversible operations (Rails, some Sequelize), a single `change` method may be sufficient.

### 6. Migration Content Guidelines

**Creating Tables:**
- Define all columns with appropriate types
- Set NOT NULL constraints where appropriate
- Add primary keys
- Include timestamps (created_at, updated_at) if project uses them
- Add foreign keys and indexes in the same migration or separate if project prefers

**Altering Tables:**
- Be specific: `ADD COLUMN`, `DROP COLUMN`, `MODIFY COLUMN`
- Handle existing data appropriately (defaults, backfills)
- Consider backwards compatibility

**Adding Indexes:**
- Name indexes clearly: `idx_users_email`, `idx_orders_user_id_created_at`
- Use appropriate index types (B-tree, Hash, GIN, etc.)
- Consider partial indexes for large tables

**Data Migrations:**
- Separate schema migrations from data migrations if possible
- Be cautious with large datasets (batch operations)
- Test rollback with realistic data volumes

### 7. Validate Migration Safety

Before finalizing, check:

- **Reversibility**: Can the migration be rolled back?
- **Data loss**: Will any data be lost? Warn the user!
- **Downtime**: Will this lock tables? Consider online migrations for large tables
- **Dependencies**: Are there dependent migrations that must run first?

### 8. Testing Recommendations

Suggest to the user:
- Run migration on a development database first
- Test rollback functionality
- For production: test on a staging environment
- Review generated SQL (for ORMs that auto-generate)

## ORM-Specific Templates

Reference the templates in `templates/` directory:

- `prisma-migration.sql` - Prisma migration example
- `sequelize-migration.js` - Sequelize migration example
- `knex-migration.js` - Knex migration example
- `typeorm-migration.ts` - TypeORM migration example
- `alembic-migration.py` - Alembic migration example
- `rails-migration.rb` - Rails migration example

## Best Practices

1. **One purpose per migration**: Don't mix unrelated changes
2. **Descriptive names**: Names should explain what the migration does
3. **Timestamps**: Use the ORM's timestamp format for ordering
4. **Idempotent when possible**: Safe to run multiple times
5. **Test rollbacks**: Ensure down/rollback works correctly
6. **Document complex logic**: Add comments for non-obvious operations
7. **Batch large operations**: For data migrations affecting many rows
8. **Use transactions**: Wrap operations in transactions when supported

## Supporting Files

- `templates/`: Migration templates for various ORMs
- `reference.md`: Naming conventions and migration patterns
