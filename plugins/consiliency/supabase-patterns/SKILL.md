---
name: supabase-patterns
description: "Generic Supabase best practices for Row Level Security, realtime subscriptions, storage, and edge functions. Framework-agnostic."
---

# Supabase Patterns Skill

Universal patterns for working with Supabase in any project. Covers RLS policies, realtime, storage, edge functions, and migrations.

## Design Principle

This skill is **framework-generic**. It provides universal Supabase patterns:
- NOT tailored to Book-Vetting, ocr-service, or any specific project
- Covers common patterns applicable across all Supabase projects
- Project-specific configurations go in project-specific skills

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SUPABASE_DIR | supabase | Directory for Supabase config |
| ENFORCE_RLS | true | Require RLS on all tables |
| REALTIME_ENABLED | auto | Auto-detect realtime tables |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order.

1. Check Supabase project configuration
2. Review existing RLS policies
3. Follow security-first patterns
4. Keep migrations organized

## Red Flags - STOP and Reconsider

If you're about to:
- Create a table without RLS policies
- Use service role key in client-side code
- Skip migrations for schema changes
- Expose sensitive data in realtime

**STOP** -> Add RLS policies -> Use appropriate keys -> Then proceed

## Cookbook

### RLS Policies
- IF: Creating or modifying RLS policies
- THEN: Read and execute `./cookbook/rls-policies.md`

### Realtime Subscriptions
- IF: Setting up realtime features
- THEN: Read and execute `./cookbook/realtime-subscriptions.md`

### Storage Patterns
- IF: Working with Supabase Storage
- THEN: Read and execute `./cookbook/storage-patterns.md`

## Quick Reference

### Project Structure

```
supabase/
├── config.toml           # Project config
├── migrations/           # SQL migrations
│   ├── 20231201000000_initial.sql
│   └── 20231202000000_add_users.sql
├── seed.sql             # Seed data
└── functions/           # Edge functions
    └── hello/
        └── index.ts
```

### Key Commands

```bash
# Initialize project
supabase init

# Start local development
supabase start

# Generate migration
supabase migration new my_migration

# Push to remote
supabase db push

# Generate types
supabase gen types typescript --local > types/supabase.ts
```

### RLS Policy Patterns

```sql
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- User owns row
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- User can insert own
CREATE POLICY "Users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Public read
CREATE POLICY "Public read"
  ON posts FOR SELECT
  USING (is_public = true);
```

### Client Patterns

```typescript
// Initialize client
import { createClient } from '@supabase/supabase-js';
import type { Database } from './types/supabase';

const supabase = createClient<Database>(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

// Query with types
const { data, error } = await supabase
  .from('posts')
  .select('*')
  .eq('user_id', userId);

// Insert
const { data, error } = await supabase
  .from('posts')
  .insert({ title, content, user_id: userId })
  .select()
  .single();
```

### Realtime Pattern

```typescript
// Subscribe to changes
const subscription = supabase
  .channel('posts')
  .on(
    'postgres_changes',
    { event: '*', schema: 'public', table: 'posts' },
    (payload) => {
      console.log('Change:', payload);
    }
  )
  .subscribe();

// Cleanup
subscription.unsubscribe();
```

### Storage Pattern

```typescript
// Upload file
const { data, error } = await supabase.storage
  .from('avatars')
  .upload(`${userId}/avatar.png`, file, {
    upsert: true,
    contentType: 'image/png'
  });

// Get public URL
const { data: { publicUrl } } = supabase.storage
  .from('avatars')
  .getPublicUrl(`${userId}/avatar.png`);
```

## Security Checklist

### Before Production

- [ ] RLS enabled on ALL tables
- [ ] Service role key NOT in client code
- [ ] Anon key for public operations only
- [ ] Storage buckets have policies
- [ ] Sensitive columns excluded from realtime
- [ ] API rate limiting configured
- [ ] CORS properly configured

### RLS Checklist

- [ ] Every table has RLS enabled
- [ ] SELECT policies defined
- [ ] INSERT/UPDATE/DELETE policies defined
- [ ] Policies tested with different roles
- [ ] No overly permissive policies

## Integration

### With Schema Alignment

Supabase migrations should align with ORM models:

```sql
-- supabase/migrations/20231201000000_users.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Should match:

```python
# SQLAlchemy model
class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

### Type Generation

```bash
# Generate TypeScript types from local schema
supabase gen types typescript --local > types/supabase.ts

# Use in client
import type { Database } from './types/supabase';
type Post = Database['public']['Tables']['posts']['Row'];
```

## Best Practices

1. **RLS first**: Always add RLS policies when creating tables
2. **Migrations for everything**: Never modify schema directly
3. **Type safety**: Generate and use TypeScript types
4. **Key hygiene**: Use anon key client-side, service key server-side only
5. **Test policies**: Test RLS with actual user contexts
6. **Realtime carefully**: Only enable for tables that need it
