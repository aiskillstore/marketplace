# Common Authentication Patterns

## Protecting Routes

### Server Component Page
```typescript
import { requireAuthRedirect } from '@/lib/auth/server-auth';

export default async function ProtectedPage() {
  await requireAuthRedirect(); // Redirects to /login if not authenticated

  // User guaranteed authenticated here
  return <div>Protected Content</div>;
}
```

### Dashboard Layout (All Child Routes)
```typescript
import { requireAuthRedirect } from '@/lib/auth/server-auth';

export default async function DashboardLayout({ children }) {
  await requireAuthRedirect();

  // All dashboard routes now protected
  return <>{children}</>;
}
```

### Auth Layout (Redirect Authenticated Users)
```typescript
import { getCurrentUser } from '@/lib/auth/server-auth';
import { redirect } from 'next/navigation';

export default async function AuthLayout({ children }) {
  const user = await getCurrentUser();

  if (user) {
    redirect('/dashboard'); // Already logged in
  }

  return <>{children}</>;
}
```

## Server Actions

### Basic Auth Check
```typescript
'use server';
import { requireAuth } from '@/lib/auth/server-auth';

export async function updateProfile(data: FormData) {
  const user = await requireAuth(); // Throws if not authenticated

  // Proceed with update
  const name = data.get('name');
  // ...
}
```

### With Error Handling
```typescript
'use server';
import { requireAuth, UnauthorizedError } from '@/lib/auth/server-auth';

export async function myAction() {
  try {
    const user = await requireAuth();
    // Do work
    return { success: true };
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      return { success: false, error: 'Please log in' };
    }
    throw error;
  }
}
```

## Getting User Data

### Current User (Auth Only)
```typescript
import { getCurrentUser } from '@/lib/auth/server-auth';

export default async function Page() {
  const user = await getCurrentUser(); // Returns auth.users data or null

  if (!user) {
    return <LoginPrompt />;
  }

  return <Dashboard email={user.email} />;
}
```

### Extended User Profile
```typescript
import { getUserData } from '@/lib/auth/server-auth';

export default async function ProfilePage() {
  const userData = await getUserData(); // Returns users table data or null

  if (!userData) {
    redirect('/login');
  }

  // userData includes: role, familyId, firstName, lastName, etc.
  return <Profile {...userData} />;
}
```

### Family ID
```typescript
import { getCurrentFamilyId } from '@/lib/auth/server-auth';

export default async function FamilyPage() {
  const familyId = await getCurrentFamilyId();

  if (!familyId) redirect('/login');

  const data = await fetchFamilyData(familyId);
  return <FamilyDashboard data={data} />;
}
```

## Admin Access Control

### Admin-Only Page
```typescript
import { requireAdminRedirect } from '@/lib/auth/server-auth';

export default async function AdminSettingsPage() {
  await requireAdminRedirect(); // Redirects if not admin or not logged in

  // User guaranteed to be admin here
  return <AdminSettings />;
}
```

### Admin-Only Server Action
```typescript
'use server';
import { requireAdmin } from '@/lib/auth/server-auth';

export async function deleteAllData() {
  await requireAdmin(); // Throws if not admin

  // Proceed with admin action
  await dangerousOperation();
}
```

### Conditional Admin UI
```typescript
import { isAdmin } from '@/lib/auth/server-auth';

export default async function DashboardPage() {
  const userIsAdmin = await isAdmin();

  return (
    <div>
      <Dashboard />
      {userIsAdmin && <AdminPanel />}
    </div>
  );
}
```

## Multi-Tenant Data Access

### Validate Family Access
```typescript
'use server';
import { requireFamilyAccess } from '@/lib/auth/server-auth';

export async function updateFamilySettings(familyId: string, settings: any) {
  await requireFamilyAccess(familyId); // Throws if user not in this family

  // User guaranteed to belong to this family
  await updateSettings(familyId, settings);
}
```

### Get Current User's Family Data
```typescript
import { getCurrentFamilyId } from '@/lib/auth/server-auth';

export async function getFamilyData() {
  const familyId = await getCurrentFamilyId();

  if (!familyId) throw new Error('User has no family');

  // No need for requireFamilyAccess - already user's own family
  return await fetchFamilyData(familyId);
}
```

## Active User Validation

### Require Active Account
```typescript
'use server';
import { requireActiveUser } from '@/lib/auth/server-auth';

export async function createTransaction(data: any) {
  const userData = await requireActiveUser(); // Throws if account inactive

  // Proceed with transaction
  await insertTransaction(data);
}
```

## Root Page Redirect

### Conditional Redirect Based on Auth
```typescript
import { getCurrentUser } from '@/lib/auth/server-auth';
import { redirect } from 'next/navigation';

export default async function RootPage() {
  const user = await getCurrentUser();

  if (user) {
    redirect('/dashboard'); // Authenticated
  } else {
    redirect('/login');     // Not authenticated
  }
}
```

## Server Action Patterns

### Login Action
```typescript
'use server';
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export async function loginAction(formData: FormData) {
  const email = String(formData.get('email'));
  const password = String(formData.get('password'));

  const supabase = await createClient();

  const { error } = await supabase.auth.signInWithPassword({
    email,
    password
  });

  if (error) {
    return { success: false, error: error.message };
  }

  redirect('/dashboard');
}
```

### Logout Action
```typescript
'use server';
import { createClient } from '@/lib/supabase/server';

export async function logoutAction() {
  const supabase = await createClient();

  const { error } = await supabase.auth.signOut();

  if (error) {
    return { success: false, error: error.message };
  }

  return { success: true };
}
```

## Performance Optimization

### Request-Level Caching
All auth helper functions use React `cache()` automatically:

```typescript
import { getCurrentUser } from '@/lib/auth/server-auth';

export default async function Layout({ children }) {
  const user1 = await getCurrentUser(); // Fetches from Supabase
  const user2 = await getCurrentUser(); // Returns cached value (same request)

  // user1 === user2, only one Supabase call made
}
```

No need to manually cache - it's built into the helpers.
