---
name: auth-integration
description: |
  Use when implementing authentication - login/signup forms, session management, protected routes, or role-based access control.
  NOT when non-auth UI, plain data fetching, or unrelated backend logic.
  Triggers: "login page", "signup form", "auth setup", "protected route", "role-based access", "Better Auth", "NextAuth".
---

# Better Auth Integration Skill

## Overview

Expert guidance for authentication implementation using Better Auth/NextAuth v5, including login/signup forms, session management with Zustand, protected routes via middleware, and role-based access control for ERP systems.

## When This Skill Applies

This skill triggers when users request:
- **Auth Setup**: "Setup Better Auth", "Configure authentication", "Auth providers"
- **Auth Forms**: "Login page", "Signup form", "Forgot password", "Email verification"
- **Session Management**: "Auth store", "Session handling", "Zustand auth"
- **Protected Routes**: "Protected dashboard", "Auth middleware", "Route guards"
- **Role-Based Access**: "Role guard", "Permission check", "Admin only", "Teacher access"

## Core Rules

### 1. Provider Setup

```typescript
// app/auth/[...auth]/route.ts
import { auth } from '@/lib/auth';
import { toNextJsHandler } from 'better-auth/next-js';

export const { GET, POST } = toNextJsHandler(auth);

// lib/auth.ts
import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';

export const auth = betterAuth({
  database: prismaAdapter(prisma),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 24 hours
  },
});
```

**Requirements:**
- Use Better Auth v5 for Next.js App Router
- Configure providers (Google, Email/Password)
- Enable email verification for new users
- Set appropriate session expiration
- Use environment variables for secrets (never hardcode)
- Prisma adapter for database integration

### 2. Auth Forms with Validation

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { signIn } from '@/lib/auth/client';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    await signIn.email({
      email: data.email,
      password: data.password,
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Email</label>
        <input
          {...register('email')}
          type="email"
          className="w-full px-4 py-2 rounded-lg border"
        />
        {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">Password</label>
        <input
          {...register('password')}
          type="password"
          className="w-full px-4 py-2 rounded-lg border"
        />
        {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
      </div>
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
      >
        {isSubmitting ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  );
}
```

**Requirements:**
- Use React Hook Form + Zod for validation
- shadcn/ui components for form inputs
- Clear error messages with localization support
- Loading states for better UX
- Accessibility: proper labels, ARIA attributes
- Password strength indicator for signup

### 3. Session Management

```typescript
import { create } from 'zustand';
import { authClient } from '@/lib/auth/client';

interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  role: string | null;
  hydrateAuth: () => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  session: null,
  isLoading: true,
  isAuthenticated: false,
  role: null,

  hydrateAuth: async () => {
    set({ isLoading: true });
    try {
      const session = await authClient.getSession();
      set({
        user: session.user,
        session: session,
        isAuthenticated: !!session,
        role: session.user?.role || null,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, isAuthenticated: false });
    }
  },

  signIn: async (email: string, password: string) => {
    await authClient.signIn.email({ email, password });
    await get().hydrateAuth();
  },

  signOut: async () => {
    await authClient.signOut();
    set({
      user: null,
      session: null,
      isAuthenticated: false,
      role: null,
    });
  },

  refresh: async () => {
    await get().hydrateAuth();
  },
}));

export const useAuth = () => {
  const auth = useAuthStore();

  useEffect(() => {
    if (!auth.user && !auth.isLoading) {
      auth.hydrateAuth();
    }
  }, []);

  return auth;
};
```

**Requirements:**
- Use Zustand for client-side auth state
- Sync with Better Auth session
- Type-safe user and session data
- Automatic session refresh on hydration
- Secure cookie storage (httpOnly, secure, sameSite)
- Clear sessions on sign out

### 4. Protected Routes

```typescript
import { authMiddleware } from 'better-auth/next-js';
import { NextResponse } from 'next/server';

export default authMiddleware({
  pathPrefix: '/dashboard',

  callback: async (request) => {
    const { user } = request;

    // Redirect to login if not authenticated
    if (!user) {
      return NextResponse.redirect(new URL('/auth/login', request.url));
    }

    // Role-based access control
    const path = request.nextUrl.pathname;

    if (path.startsWith('/dashboard/admin') && user.role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    if (path.startsWith('/dashboard/teacher') && user.role !== 'teacher' && user.role !== 'admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    return NextResponse.next();
  },
});

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

```tsx
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  allowedRoles?: string[]
) {
  return function AuthGuard(props: P) {
    const { isAuthenticated, user, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/auth/login');
      }

      if (!isLoading && isAuthenticated && allowedRoles) {
        if (!allowedRoles.includes(user?.role || '')) {
          router.push('/unauthorized');
        }
      }
    }, [isAuthenticated, isLoading, user, router]);

    if (isLoading) {
      return <LoadingSkeleton />;
    }

    if (!isAuthenticated || (allowedRoles && !allowedRoles.includes(user?.role || ''))) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };
}
```

**Requirements:**
- Middleware for server-side route protection
- Path matchers for protected routes
- Role-based access control in middleware
- Client-side auth guard HOC for extra protection
- Redirect unauthorized users to appropriate pages
- Loading states during auth checks

### 5. Role-Based Access Control

```typescript
export const ROLES = {
  ADMIN: 'admin',
  TEACHER: 'teacher',
  STUDENT: 'student',
  PARENT: 'parent',
} as const;

export const PERMISSIONS = {
  // Admin permissions
  MANAGE_USERS: 'manage:users',
  MANAGE_COURSES: 'manage:courses',
  VIEW_ALL_DATA: 'view:all_data',

  // Teacher permissions
  VIEW_CLASS: 'view:class',
  MANAGE_STUDENTS: 'manage:students',
  CREATE_ASSIGNMENTS: 'create:assignments',

  // Student permissions
  VIEW_OWN_DATA: 'view:own_data',
  SUBMIT_ASSIGNMENTS: 'submit:assignments',
} as const;

export const hasRole = (user: User | null, role: string): boolean => {
  return user?.role === role || user?.role === ROLES.ADMIN;
};

export const hasPermission = (user: User | null, permission: string): boolean => {
  if (!user) return false;
  if (user.role === ROLES.ADMIN) return true;

  const rolePermissions = {
    [ROLES.ADMIN]: Object.values(PERMISSIONS),
    [ROLES.TEACHER]: [
      PERMISSIONS.VIEW_CLASS,
      PERMISSIONS.MANAGE_STUDENTS,
      PERMISSIONS.CREATE_ASSIGNMENTS,
    ],
    [ROLES.STUDENT]: [
      PERMISSIONS.VIEW_OWN_DATA,
      PERMISSIONS.SUBMIT_ASSIGNMENTS,
    ],
    [ROLES.PARENT]: [
      PERMISSIONS.VIEW_OWN_DATA,
    ],
  };

  return rolePermissions[user.role]?.includes(permission) ?? false;
};

export const PermissionGuard = ({
  permission,
  fallback = null,
  children,
}: {
  permission: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}) => {
  const { user } = useAuth();

  if (!hasPermission(user, permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
```

**Requirements:**
- Define roles and permissions clearly
- Admin has all permissions by default
- Type-safe permission checking
- Permission-aware components
- Server-side permission verification for sensitive actions
- Audit logs for permission checks

## Output Requirements

### Code Files

1. **Auth Configuration**:
   - `lib/auth.ts` - Better Auth setup
   - `app/auth/[...auth]/route.ts` - Auth API routes

2. **Forms**:
   - `app/auth/login/page.tsx` - Login form
   - `app/auth/signup/page.tsx` - Signup form
   - `app/auth/forgot-password/page.tsx` - Password reset

3. **Session Management**:
   - `lib/auth-store.ts` - Zustand auth store
   - `hooks/useAuth.ts` - Auth hook

4. **Protected Routes**:
   - `middleware.ts` - Route protection
   - `components/AuthGuard.tsx` - Auth guard HOC

### Integration Requirements

- **shadcn/ui**: Use shadcn form components
- **@ui-ux-designer**: Ensure responsive, accessible forms
- **@nextjs-app-router**: Follow Next.js App Router patterns
- **@react-component**: Use functional components with hooks

### Documentation

- **PHR**: Create Prompt History Record for auth decisions
- **ADR**: Document auth strategy (JWT vs DB sessions, provider choice)
- **Comments**: Document security considerations

## Workflow

1. **Analyze Auth Requirements**
   - Identify auth providers needed (Google, Email/Password)
   - Determine role-based access needs
   - Check email verification requirements

2. **Setup Auth Provider**
   - Configure Better Auth with providers
   - Setup database adapter (Prisma)
   - Configure session settings

3. **Create Auth Forms**
   - Build login form with validation
   - Create signup with email verification
   - Add password reset flow

4. **Implement Session Management**
   - Create Zustand auth store
   - Sync with Better Auth session
   - Handle session refresh

5. **Protect Routes**
   - Setup middleware for server-side protection
   - Create auth guard HOC for client-side
   - Implement role-based access control

6. **Validate Security**
   - Check OWASP compliance
   - Verify CSRF protection
   - Test session handling

## Quality Checklist

Before completing any auth implementation:

- [ ] **OWASP Secure**: CSRF tokens, XSS protection, secure headers
- [ ] **Password Hash/Verify**: bcrypt/argon2, no plain text storage
- [ ] **Role Guards**: Middleware + client-side role checks
- [ ] **Logout Clear Sessions**: Clear cookies, Zustand store, redirect
- [ ] **Responsive Mobile Login**: Mobile-friendly forms, touch targets 44px+
- [ ] **Email Verification**: Required for new accounts
- [ ] **Session Expiration**: Reasonable timeout (7-30 days)
- [ ] **Secure Cookies**: httpOnly, secure, sameSite='strict'
- [ ] **Rate Limiting**: Prevent brute force attacks
- [ ] **Audit Logging**: Log auth events for security monitoring

## Common Patterns

### Login Page with Google Auth

```tsx
'use client';

import { useState } from 'react';
import { signIn } from '@/lib/auth/client';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState('');

  const handleGoogleSignIn = async () => {
    try {
      await signIn.social({
        provider: 'google',
        callbackURL: '/dashboard',
      });
    } catch (err) {
      setError('Failed to sign in with Google');
    }
  };

  const handleEmailSignIn = async (email: string, password: string) => {
    try {
      await signIn.email({
        email,
        password,
        callbackURL: '/dashboard',
      });
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center">Sign In</h1>

        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <button
          onClick={handleGoogleSignIn}
          className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          Sign in with Google
        </button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with email</span>
          </div>
        </div>

        <LoginForm onSubmit={handleEmailSignIn} />

        <p className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <a href="/auth/signup" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
```

### Signup with Email Verification

```tsx
'use client';

import { useState } from 'react';
import { signUp } from '@/lib/auth/client';

export default function SignupPage() {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSignup = async (data: SignupFormData) => {
    try {
      await signUp.email({
        email: data.email,
        password: data.password,
        name: data.name,
      });

      setSuccess(true);
    } catch (err) {
      setError('Failed to create account');
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Check your email</h1>
          <p className="text-gray-600">
            We've sent a verification link to your email address
          </p>
        </div>
      </div>
    );
  }

  return <SignupForm onSubmit={handleSignup} />;
}
```

### Protected Dashboard with Role Guard

```tsx
import { withAuth } from '@/components/AuthGuard';
import { ROLES } from '@/lib/permissions';

function AdminDashboard() {
  const { user } = useAuth();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <p>Welcome, {user?.name}</p>
    </div>
  );
}

export default withAuth(AdminDashboard, [ROLES.ADMIN]);
```

### Password Strength Indicator

```tsx
export const PasswordStrength = ({ password }: { password: string }) => {
  const getStrength = (pwd: string) => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[a-z]/.test(pwd)) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^a-zA-Z0-9]/.test(pwd)) strength++;
    return strength;
  };

  const strength = getStrength(password);
  const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-green-600'];
  const labels = ['Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];

  return (
    <div className="mt-2">
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className={`h-2 flex-1 rounded ${i <= strength ? colors[strength - 1] : 'bg-gray-200'}`}
          />
        ))}
      </div>
      {password && (
        <p className={`text-sm mt-1 ${colors[strength - 1]?.replace('bg-', 'text-')}`}>
          Password strength: {labels[strength - 1]}
        </p>
      )}
    </div>
  );
};
```

## Security Best Practices

### OWASP Compliance

1. **CSRF Protection**: Use built-in Better Auth CSRF tokens
2. **XSS Prevention**: Sanitize user input, use React's auto-escaping
3. **SQL Injection**: Use Prisma ORM (parameterized queries)
4. **Password Security**: bcrypt/argon2 hashing, minimum 8 characters
5. **Session Security**: httpOnly, secure, sameSite cookies

### Rate Limiting

```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(5, '10 s'), // 5 requests per 10 seconds
});

export async function checkRateLimit(identifier: string) {
  const { success } = await ratelimit.limit(identifier);
  return success;
}
```

### Audit Logging

```typescript
export async function logAuthEvent(event: {
  type: 'login' | 'logout' | 'signup' | 'password_reset';
  userId?: string;
  ip?: string;
  userAgent?: string;
}) {
  await prisma.authEvent.create({
    data: {
      ...event,
      timestamp: new Date(),
    },
  });
}
```

## Environment Variables

```bash
# .env.local
AUTH_SECRET=your-super-secret-random-string
BETTER_AUTH_URL=http://localhost:3000

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Database
DATABASE_URL=your-database-url
```

## References

- Better Auth: https://www.better-auth.com
- NextAuth v5: https://authjs.dev
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- shadcn/ui Forms: https://ui.shadcn.com/docs/components/form
- React Hook Form: https://react-hook-form.com
- Zod Validation: https://zod.dev
