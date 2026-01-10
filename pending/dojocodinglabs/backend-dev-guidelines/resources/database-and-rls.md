# Database and Row-Level Security Guide

PostgreSQL database design and Row-Level Security (RLS) patterns for Supabase.

## Schema Design

### Tables

```sql
-- Users profile (extends auth.users)
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  bio TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL CHECK (char_length(title) <= 200),
  content TEXT NOT NULL,
  published BOOLEAN DEFAULT false,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  content TEXT NOT NULL CHECK (char_length(content) <= 1000),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes

```sql
-- User lookups
CREATE INDEX user_profiles_username_idx ON user_profiles(username);

-- Post queries
CREATE INDEX posts_user_id_idx ON posts(user_id);
CREATE INDEX posts_published_idx ON posts(published) WHERE published = true;
CREATE INDEX posts_created_at_idx ON posts(created_at DESC);

-- Comment queries
CREATE INDEX comments_post_id_idx ON comments(post_id);
CREATE INDEX comments_user_id_idx ON comments(user_id);
```

### Timestamps with Triggers

```sql
-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_updated_at
  BEFORE UPDATE ON posts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();
```

## Row-Level Security (RLS)

### Enable RLS

```sql
-- Enable on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
```

### Basic Policies

```sql
-- User Profiles: Users can read all, update own
CREATE POLICY "profiles_select_all" ON user_profiles
  FOR SELECT USING (true);

CREATE POLICY "profiles_update_own" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);

-- Posts: Read published or own, insert/update/delete own
CREATE POLICY "posts_select_published" ON posts
  FOR SELECT USING (published = true OR auth.uid() = user_id);

CREATE POLICY "posts_insert_own" ON posts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "posts_update_own" ON posts
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "posts_delete_own" ON posts
  FOR DELETE USING (auth.uid() = user_id);

-- Comments: Read if post visible, insert/update/delete own
CREATE POLICY "comments_select_visible" ON comments
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM posts
      WHERE posts.id = comments.post_id
      AND (posts.published = true OR posts.user_id = auth.uid())
    )
  );

CREATE POLICY "comments_insert_authenticated" ON comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "comments_update_own" ON comments
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "comments_delete_own" ON comments
  FOR DELETE USING (auth.uid() = user_id);
```

### Admin Policies

```sql
-- Admin role check function
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    SELECT (auth.jwt() -> 'user_metadata' ->> 'role') = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Admin can do everything
CREATE POLICY "admins_all_posts" ON posts
  USING (is_admin());
```

## Migrations

### Create Migration

```bash
supabase migration new add_posts_table
```

### Migration Example

```sql
-- supabase/migrations/20250104_add_posts.sql

-- Create table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes
CREATE INDEX posts_user_id_idx ON posts(user_id);

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Add policies
CREATE POLICY "posts_select_own" ON posts
  FOR SELECT USING (auth.uid() = user_id);
```

### Apply Migrations

```bash
# Locally
supabase db reset  # Resets and applies all migrations

# Production
supabase db push
```

## Query Patterns

### From Edge Function

```typescript
// RLS is automatically enforced
const { data, error } = await supabase
  .from('posts')
  .select('*')
  .eq('user_id', user.id)

// Only returns posts user can see
```

### Service Role (Bypass RLS)

```typescript
// Use service role key (admin access)
const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')! // Not anon key
)

// RLS is bypassed
const { data } = await supabase.from('posts').select('*')
```

## Testing RLS

```sql
-- Test as specific user
SET request.jwt.claims TO '{"sub":"user-uuid-here"}';

-- Test queries
SELECT * FROM posts;  -- Should only return user's posts

-- Reset
RESET request.jwt.claims;
```

---

**Related:**
- [architecture-overview.md](architecture-overview.md) - Complete architecture
- [edge-functions-guide.md](edge-functions-guide.md) - Using database from functions
