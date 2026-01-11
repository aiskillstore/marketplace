# Database Migration Skill
## Creating Idempotent Supabase Migrations

**When to Use**: Adding tables, modifying schemas, creating RLS policies, adding functions

---

## Process

### 1. Check Existing Schema
**ALWAYS** check before creating:
```bash
# Read schema reference
cat docs/guides/schema-reference.md

# Or check existing migrations
ls supabase/migrations/
```

### 2. Create Migration File

**Location**: `supabase/migrations/YYYYMMDDHHMMSS_description.sql`

**Naming**: Use timestamp + descriptive name
```
20251230120000_add_agent_registry_table.sql
```

### 3. Write Idempotent SQL

**Pattern**: Use `IF NOT EXISTS` and `CREATE OR REPLACE`

```sql
-- Tables
CREATE TABLE IF NOT EXISTS agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL,
  version TEXT NOT NULL,
  capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(workspace_id, agent_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_agent_registry_workspace
  ON agent_registry(workspace_id);

CREATE INDEX IF NOT EXISTS idx_agent_registry_agent
  ON agent_registry(agent_id, workspace_id);

-- RLS
ALTER TABLE agent_registry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their workspace agents" ON agent_registry;
CREATE POLICY "Users can view their workspace agents" ON agent_registry
  FOR SELECT USING (
    workspace_id IN (
      SELECT w.id FROM workspaces w
      INNER JOIN user_organizations uo ON uo.org_id = w.org_id
      WHERE uo.user_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "System can manage agents" ON agent_registry;
CREATE POLICY "System can manage agents" ON agent_registry
  FOR ALL USING (true) WITH CHECK (true);

-- Functions
CREATE OR REPLACE FUNCTION get_agent_count(p_workspace_id UUID)
RETURNS INTEGER AS $$
BEGIN
  RETURN (SELECT COUNT(*) FROM agent_registry WHERE workspace_id = p_workspace_id);
END;
$$ LANGUAGE plpgsql STABLE;

-- Comments
COMMENT ON TABLE agent_registry IS 'Registry of all active agents per workspace';
```

### 4. RLS Policy Pattern

**ALWAYS use**: `user_organizations` + `workspaces` join (NOT workspace_members)

```sql
-- Correct pattern
workspace_id IN (
  SELECT w.id FROM workspaces w
  INNER JOIN user_organizations uo ON uo.org_id = w.org_id
  WHERE uo.user_id = auth.uid()
)

-- For admin/owner only
workspace_id IN (
  SELECT w.id FROM workspaces w
  INNER JOIN user_organizations uo ON uo.org_id = w.org_id
  WHERE uo.user_id = auth.uid() AND uo.role IN ('admin', 'owner')
)
```

### 5. Apply Migration

**Method**: Supabase Dashboard → SQL Editor

**Steps**:
1. Copy migration SQL
2. Paste into SQL Editor
3. Click "Run"
4. Verify success

**Alternative**: Use WORKING_MIGRATIONS.sql pattern for combined migrations

---

## Examples

### Example 1: Simple Table

```sql
CREATE TABLE IF NOT EXISTS my_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_my_table_workspace ON my_table(workspace_id);

ALTER TABLE my_table ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "workspace_isolation" ON my_table;
CREATE POLICY "workspace_isolation" ON my_table
  FOR ALL USING (
    workspace_id IN (
      SELECT w.id FROM workspaces w
      INNER JOIN user_organizations uo ON uo.org_id = w.org_id
      WHERE uo.user_id = auth.uid()
    )
  );
```

### Example 2: ENUM Type

```sql
DO $$ BEGIN
  CREATE TYPE agent_status AS ENUM ('active', 'paused', 'disabled');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
```

### Example 3: Trigger

```sql
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_updated_at ON my_table;
CREATE TRIGGER trigger_update_updated_at
  BEFORE UPDATE ON my_table
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();
```

---

## Common Patterns

### Workspace Isolation (MANDATORY)

```sql
CREATE TABLE table_name (
  ...
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  ...
);

-- Always add index on workspace_id
CREATE INDEX IF NOT EXISTS idx_table_workspace ON table_name(workspace_id);

-- Always add RLS
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
```

### Constraints

```sql
-- Check constraints
CONSTRAINT valid_status CHECK (status IN ('active', 'inactive')),
CONSTRAINT valid_score CHECK (score >= 0 AND score <= 100),
CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
```

### Foreign Keys

```sql
-- With cascade delete
workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

-- With set null
created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,

-- With restrict (prevents delete if referenced)
org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT
```

---

## Checklist

Before applying migration:

- [ ] Checked schema-reference.md for conflicts
- [ ] Used `IF NOT EXISTS` on tables
- [ ] Used `CREATE OR REPLACE` on functions
- [ ] Added workspace_id column (if multi-tenant table)
- [ ] Created index on workspace_id
- [ ] Enabled RLS
- [ ] Added RLS policies (user + system)
- [ ] Used correct RLS pattern (user_organizations join)
- [ ] Added constraints where appropriate
- [ ] Added comments for documentation
- [ ] Tested SQL syntax locally

---

## Troubleshooting

**Error**: "relation workspace_members does not exist"
**Fix**: Use `user_organizations` + `workspaces` join (see RLS pattern above)

**Error**: "already exists"
**Fix**: Use `IF NOT EXISTS` or `CREATE OR REPLACE`

**Error**: "permission denied"
**Fix**: Use service role key in Supabase Dashboard, not anon key

---

**Standard**: Idempotent, workspace-isolated, RLS-secured, well-documented
