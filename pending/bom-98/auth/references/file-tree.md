# Authentication System File Tree

Complete reference of all files in the authentication and access control system.

## Core Infrastructure

```
.env
├── NEXT_PUBLIC_SUPABASE_URL
├── NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
└── NEXT_PUBLIC_SITE_URL

src/middleware.ts
└── Token refresh on every request via updateSession()

src/lib/supabase/
├── client.ts          # Client-side Supabase (for 'use client' components)
├── server.ts          # Server-side Supabase (for Server Components/Actions)
└── middleware.ts      # Middleware-specific client with updateSession()
```

## Authentication Helpers

```
src/lib/auth/
├── server-auth.ts     # All server-side auth functions (CRITICAL)
│   ├── getCurrentUser()
│   ├── getUserData()
│   ├── requireAuth()
│   ├── requireAuthRedirect()
│   ├── isAdmin()
│   ├── requireAdmin()
│   ├── requireAdminRedirect()
│   ├── requireFamilyAccess()
│   ├── requireActiveUser()
│   └── getCurrentFamilyId()
│
└── types.ts           # Shared type definitions
    ├── AuthResult
    ├── SignupData
    └── ResendVerificationResult
```

## Form Validation

```
src/lib/authFormSchema.ts
└── authFormSchema(type)   # Zod schemas for sign-in/sign-up forms
```

## Route Protection

```
src/app/page.tsx                    # Root: redirect to /dashboard or /login
src/app/dashboard/layout.tsx        # Protects all /dashboard/* routes
src/app/(auth)/layout.tsx           # Prevents authenticated users from auth pages
```

## Authentication Pages

```
src/app/(auth)/
├── login/
│   ├── page.tsx       # Login form (Client Component)
│   └── actions.ts     # loginAction, loginWithGithubAction, logoutAction
│
├── register/
│   ├── page.tsx       # Multi-step registration form
│   └── actions.ts     # signupAction (3-step: auth user, family, user profile)
│
└── confirm-signup/
    ├── page.tsx       # Email confirmation waiting page
    └── actions.ts     # resendVerificationEmail
```

## Email Verification

```
src/app/auth/callback/
└── route.ts           # OAuth & email verification callback handler
```

## Client State (Optional)

```
src/hooks/useAuthStore.ts
└── Zustand store for client-side auth state (partially deprecated)
```

## Database Tables

```
auth.users (Supabase managed)
├── id (UUID)
├── email
├── encrypted_password
├── email_confirmed_at
└── user_metadata
    ├── first_name
    ├── last_name
    ├── phone_number
    ├── birthdate
    ├── address
    ├── city
    ├── state
    ├── postal_code
    └── ssn

public.families
├── id (UUID)
├── name
├── currency
├── locale
├── country
└── timezone

public.users
├── id (UUID, same as auth.users.id)
├── family_id (FK to families.id)
├── email
├── first_name
├── last_name
├── role ('admin' | 'member')
└── active (boolean)
```
