# RLS Policies Cookbook

Row Level Security (RLS) policies for Supabase PostgreSQL.

## Basic Patterns

### Enable RLS

```sql
-- Always enable RLS first
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Force RLS for table owner too (recommended)
ALTER TABLE posts FORCE ROW LEVEL SECURITY;
```

### User Owns Row

```sql
-- Users can only see their own rows
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- Users can only update their own rows
CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can only delete their own rows
CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = user_id);
```

### Insert with Ownership

```sql
-- Users can insert rows owned by themselves
CREATE POLICY "Users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

### Public Read, Owner Write

```sql
-- Anyone can read public posts
CREATE POLICY "Public read"
  ON posts FOR SELECT
  USING (is_public = true);

-- Owners can read all their posts (including private)
CREATE POLICY "Owner read all"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

-- Only owners can update
CREATE POLICY "Owner update"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id);
```

## Advanced Patterns

### Role-Based Access

```sql
-- Check user role from profiles table
CREATE POLICY "Admins can view all"
  ON posts FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM profiles
      WHERE profiles.id = auth.uid()
      AND profiles.role = 'admin'
    )
  );

-- Or using JWT claims
CREATE POLICY "Admin access via JWT"
  ON posts FOR ALL
  USING (auth.jwt() ->> 'role' = 'admin');
```

### Team/Organization Access

```sql
-- Members of the same team can see each other's posts
CREATE POLICY "Team members can view"
  ON posts FOR SELECT
  USING (
    team_id IN (
      SELECT team_id FROM team_members
      WHERE user_id = auth.uid()
    )
  );

-- Team admins can update any team post
CREATE POLICY "Team admins can update"
  ON posts FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.team_id = posts.team_id
      AND team_members.user_id = auth.uid()
      AND team_members.role = 'admin'
    )
  );
```

### Soft Delete Protection

```sql
-- Users can only see non-deleted posts
CREATE POLICY "Exclude deleted"
  ON posts FOR SELECT
  USING (
    auth.uid() = user_id
    AND deleted_at IS NULL
  );

-- Soft delete (update deleted_at) instead of hard delete
CREATE POLICY "Soft delete only"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (
    -- Only allow setting deleted_at
    auth.uid() = user_id
  );
```

### Time-Based Access

```sql
-- Posts only visible after publish date
CREATE POLICY "Published posts"
  ON posts FOR SELECT
  USING (
    published_at <= now()
    OR auth.uid() = user_id
  );
```

## Security Functions

### Create Helper Functions

```sql
-- Check if current user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid()
    AND role = 'admin'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Use in policy
CREATE POLICY "Admin access"
  ON sensitive_data FOR ALL
  USING (is_admin());
```

### Get Current User's Team

```sql
CREATE OR REPLACE FUNCTION get_user_team_ids()
RETURNS uuid[] AS $$
BEGIN
  RETURN ARRAY(
    SELECT team_id FROM team_members
    WHERE user_id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Use in policy
CREATE POLICY "Team access"
  ON team_posts FOR SELECT
  USING (team_id = ANY(get_user_team_ids()));
```

## Testing Policies

### Test as Different Users

```sql
-- Test as anonymous
SET request.jwt.claims = '{}';
SELECT * FROM posts;  -- Should see only public

-- Test as specific user
SET request.jwt.claims = '{"sub": "user-uuid-here"}';
SELECT * FROM posts;  -- Should see user's posts

-- Reset
RESET request.jwt.claims;
```

### Debug Policies

```sql
-- See which policies exist
SELECT * FROM pg_policies WHERE tablename = 'posts';

-- Check if RLS is enabled
SELECT relname, relrowsecurity, relforcerowsecurity
FROM pg_class
WHERE relname = 'posts';
```

## Common Mistakes

### Mistake 1: Forgetting WITH CHECK

```sql
-- BAD: Missing WITH CHECK allows inserting with any user_id
CREATE POLICY "Insert"
  ON posts FOR INSERT
  USING (auth.uid() = user_id);  -- USING doesn't apply to INSERT!

-- GOOD: Use WITH CHECK for INSERT
CREATE POLICY "Insert"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

### Mistake 2: Overly Permissive

```sql
-- BAD: Allows any authenticated user
CREATE POLICY "Authenticated access"
  ON sensitive_data FOR ALL
  USING (auth.uid() IS NOT NULL);

-- GOOD: Check specific permissions
CREATE POLICY "Authorized access"
  ON sensitive_data FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM permissions
      WHERE user_id = auth.uid()
      AND resource = 'sensitive_data'
      AND can_access = true
    )
  );
```

### Mistake 3: Not Enabling RLS

```sql
-- Table without RLS is open to all!
-- Always enable immediately after CREATE TABLE
CREATE TABLE posts (...);
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

## Migration Pattern

```sql
-- migrations/20231201000000_add_posts_rls.sql

-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Drop any existing policies (for idempotency)
DROP POLICY IF EXISTS "Users can view own posts" ON posts;
DROP POLICY IF EXISTS "Users can create posts" ON posts;
DROP POLICY IF EXISTS "Users can update own posts" ON posts;
DROP POLICY IF EXISTS "Users can delete own posts" ON posts;

-- Create policies
CREATE POLICY "Users can view own posts"
  ON posts FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create posts"
  ON posts FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own posts"
  ON posts FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own posts"
  ON posts FOR DELETE
  USING (auth.uid() = user_id);
```
