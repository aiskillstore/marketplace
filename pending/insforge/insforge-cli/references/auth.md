# Auth Backend Configuration

Use migrations for database-side auth lifecycle hooks. The common case is
creating an app-owned profile row whenever a new InsForge user is created.

## `auth.users` Fields Agents Commonly Need

Do not rely on a full `auth.users` schema dump in skills. For common app hooks,
these fields are safe to assume:

| Field | Use |
|-------|-----|
| `id` | User UUID; reference it with `auth.users(id)` |
| `email` | User email |
| `profile` | JSONB profile metadata from sign-up/OAuth, such as `name` and `avatar_url` |

InsForge stores profile metadata in `auth.users.profile` JSONB. In triggers,
read common values with `NEW.profile->>'name'` and
`NEW.profile->>'avatar_url'`.

## Create a Profile on Sign Up

```sql
CREATE TABLE IF NOT EXISTS public.profiles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY profiles_owner_select ON public.profiles
FOR SELECT TO authenticated
USING (user_id = (SELECT auth.uid()));

CREATE POLICY profiles_owner_update ON public.profiles
FOR UPDATE TO authenticated
USING (user_id = (SELECT auth.uid()))
WITH CHECK (user_id = (SELECT auth.uid()));

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (user_id, display_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.profile->>'name',
    NEW.profile->>'avatar_url'
  )
  ON CONFLICT (user_id) DO NOTHING;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION public.handle_new_user();
```

Create the trigger function in `public`, then attach the trigger to `auth.users`. To remove the hook later, drop the function with `CASCADE`:

```sql
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
```

Keep app data in app-owned tables such as `public.profiles`; do not add custom columns to `auth.users`.
