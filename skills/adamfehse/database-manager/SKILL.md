---
name: Database Manager
description: Manages Supabase database schema, migrations, and queries for CookMode V2. Use this when the user needs to create/modify tables, write migrations, update RLS policies, or troubleshoot database issues.
---

# Database Manager Skill

## Your Role

You specialize in Supabase PostgreSQL database operations for CookMode V2. You help users manage schema, write migrations, configure Row Level Security (RLS), and troubleshoot database issues.

## When to Use This Skill

Invoke this skill when the user wants to:
- Create or modify database tables
- Write SQL migrations
- Add/update RLS policies
- Debug database errors
- Optimize queries
- Add new database features

## Current Database Schema

### Tables Overview

1. **ingredient_checks**
   - Tracks ingredient completion status
   - Real-time synced across clients

2. **step_checks**
   - Tracks instruction step completion
   - Real-time synced across clients

3. **recipe_status**
   - Workflow status: gathered, complete, plated, packed
   - One status per recipe

4. **recipe_order_counts**
   - Number of orders for each recipe (1-50)
   - Used for ingredient scaling

5. **recipe_chef_names**
   - Chef assignment with color badge
   - Includes `name` and `color` fields

### Schema Files
- **Primary**: `/supabase-schema.sql`
- **Migrations**: `/supabase-migration-*.sql`

## Table Schemas

### ingredient_checks
```sql
CREATE TABLE ingredient_checks (
    recipe_slug TEXT NOT NULL,
    ingredient_index INTEGER NOT NULL,
    component_name TEXT NOT NULL,
    ingredient_text TEXT,
    is_checked BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (recipe_slug, ingredient_index, component_name)
);
```

### step_checks
```sql
CREATE TABLE step_checks (
    recipe_slug TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    step_text TEXT,
    is_checked BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (recipe_slug, step_index)
);
```

### recipe_status
```sql
CREATE TABLE recipe_status (
    recipe_slug TEXT PRIMARY KEY,
    status TEXT CHECK (status IN ('gathered', 'complete', 'plated', 'packed')),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### recipe_order_counts
```sql
CREATE TABLE recipe_order_counts (
    recipe_slug TEXT PRIMARY KEY,
    order_count INTEGER DEFAULT 1 CHECK (order_count >= 1 AND order_count <= 50),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### recipe_chef_names
```sql
CREATE TABLE recipe_chef_names (
    recipe_slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#9333ea',
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Row Level Security (RLS)

CookMode V2 currently uses **permissive RLS** - all users can read/write all data.

```sql
-- Enable RLS
ALTER TABLE ingredient_checks ENABLE ROW LEVEL SECURITY;

-- Allow all operations (current policy)
CREATE POLICY "Enable all access" ON ingredient_checks
    FOR ALL USING (true);
```

**Note**: This is suitable for trusted kitchen environments. For multi-tenant setups, implement user-specific policies.

## Real-Time Subscriptions

Tables with real-time sync enabled:
- `ingredient_checks`
- `step_checks`
- `recipe_status`
- `recipe_order_counts`
- `recipe_chef_names`

Configured in `/js/hooks/useRealtime.js:15-80`

## Migration Best Practices

### Creating a Migration

1. **Name convention**: `supabase-migration-{feature-name}.sql`
2. **Include rollback**: Add comments for manual rollback steps
3. **Test locally**: Verify migration before applying

### Migration Template

```sql
-- Migration: Add new feature
-- Date: 2025-01-XX
-- Description: Brief description of changes

-- ============================================
-- NEW TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    recipe_slug TEXT NOT NULL,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_new_table_recipe ON new_table(recipe_slug);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access" ON new_table
    FOR ALL USING (true);

-- ============================================
-- ROLLBACK (Manual)
-- ============================================
-- DROP TABLE IF EXISTS new_table CASCADE;
```

## Common Database Operations

### Adding a New Table

1. Define schema with constraints
2. Add indexes for performance
3. Enable RLS and create policies
4. Document in this skill
5. Update hooks if real-time needed

### Modifying Existing Table

```sql
-- Add new column
ALTER TABLE recipe_status
ADD COLUMN priority INTEGER DEFAULT 0;

-- Modify column
ALTER TABLE recipe_chef_names
ALTER COLUMN color SET DEFAULT '#10b981';

-- Add constraint
ALTER TABLE recipe_order_counts
ADD CONSTRAINT valid_count CHECK (order_count > 0);
```

### Querying Data

Use Supabase client in hooks:

```javascript
// Select
const { data, error } = await supabase
    .from('recipe_status')
    .select('*')
    .eq('recipe_slug', 'truffle-mashed-potatoes');

// Upsert
const { error } = await supabase
    .from('recipe_order_counts')
    .upsert({
        recipe_slug: 'chocolate-cake',
        order_count: 5
    }, {
        onConflict: 'recipe_slug'
    });

// Delete
const { error } = await supabase
    .from('step_checks')
    .delete()
    .eq('recipe_slug', 'old-recipe');
```

## Database Connection

### Configuration
Supabase connection configured in `/js/hooks/useSupabase.js`:
- **URL**: From environment or config
- **Anon Key**: Public key for client-side access
- **Real-time**: WebSocket connection for live updates

### Initialization Flow
1. `useSupabase()` creates client
2. Returns `{supabase, isSupabaseConnected}`
3. App checks connection before operations

## Troubleshooting

### Common Issues

**Issue**: Changes not syncing
- Check real-time subscription in useRealtime.js
- Verify table has RLS policy
- Check browser console for Supabase errors

**Issue**: Constraint violation
- Review table constraints (CHECK, UNIQUE, FK)
- Validate data before insert/update

**Issue**: RLS blocking queries
- Verify policies allow operation
- Check user authentication status

### Debug Queries

```sql
-- Check table structure
\d+ ingredient_checks

-- View all policies
SELECT * FROM pg_policies WHERE tablename = 'recipe_status';

-- Check real-time configuration
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

## Performance Considerations

### Indexes
Current indexes target:
- Primary keys (automatic)
- Foreign key columns
- Frequently filtered columns (recipe_slug)

### Optimistic Updates
UI updates immediately, syncs to DB asynchronously:
```javascript
// Optimistic update
setCompletedIngredients(prev => ({ ...prev, [key]: true }));

// Then sync to Supabase
await supabase.from('ingredient_checks').upsert(...);
```

## Schema Evolution

When modifying schema:
1. **Never drop data without backup**
2. **Use migrations for all changes**
3. **Test with realistic data volumes**
4. **Update hooks if data access changes**
5. **Document changes in CLAUDE.md**

## Example: Adding Recipe Notes Table

```sql
-- Migration: Add recipe notes feature
CREATE TABLE recipe_notes (
    id SERIAL PRIMARY KEY,
    recipe_slug TEXT NOT NULL,
    note_text TEXT NOT NULL,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recipe_notes_slug ON recipe_notes(recipe_slug);

ALTER TABLE recipe_notes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable all access" ON recipe_notes FOR ALL USING (true);
```

Then update `/js/hooks/useRecipeData.js` to fetch and manage notes.

Remember: Keep the database simple and cook-friendly, just like the UI!
