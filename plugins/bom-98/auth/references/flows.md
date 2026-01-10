# Authentication Flow Diagrams

## User Registration Flow

```
Step 1: User fills registration form
   └─> src/app/(auth)/register/page.tsx
       ├─> Multi-step form (2 steps)
       ├─> Step 1: Personal details, address, phone, DOB, SSN
       └─> Step 2: Email, password

Step 2: Form submitted to signupAction
   └─> src/app/(auth)/register/actions.ts
       └─> signupAction(data: SignupData)

Step 3: Server creates 3 records
   ├─> a) Supabase auth user
   │   └─> supabase.auth.signUp()
   │   └─> Metadata: first_name, last_name, phone, address, etc.
   │   └─> Sends verification email with magic link
   │
   ├─> b) Family record (household)
   │   └─> Insert into public.families
   │   └─> Name: "{firstName}'s Household"
   │   └─> Defaults: USD currency, en locale, US country
   │
   └─> c) User profile record
       └─> Insert into public.users
       └─> Links: auth.users.id = users.id
       └─> Role: 'admin' (first user in family)
       └─> Links to family_id

Step 4: Redirect to confirmation page
   └─> redirect('/confirm-signup')
       └─> src/app/(auth)/confirm-signup/page.tsx
       └─> Shows: Email address and instructions
       └─> Action: Resend verification button

Step 5: User clicks link in email
   └─> Email link: /auth/callback?token_hash=xxx&type=signup
       └─> src/app/auth/callback/route.ts
       └─> Verifies: supabase.auth.verifyOtp()
       └─> Success: redirect('/dashboard')
       └─> Failure: redirect('/login?error=verification_failed')
```

## User Login Flow

```
Step 1: User enters credentials
   └─> src/app/(auth)/login/page.tsx
       └─> Form: email, password
       └─> Client Component with loading state

Step 2: Form submitted to loginAction
   └─> src/app/(auth)/login/actions.ts
       └─> loginAction(formData: FormData)
       └─> Calls: supabase.auth.signInWithPassword()

Step 3: Server validates credentials
   ├─> Success:
   │   └─> Sets httpOnly cookies
   │   └─> redirect('/dashboard')
   │   └─> Dashboard layout checks: requireAuthRedirect()
   │   └─> User sees dashboard
   │
   └─> Failure:
       └─> Return: { success: false, error: message }
       └─> Client shows error on login page
```

## Route Protection Flow

### Root Page (/)
```
User visits /
   └─> src/app/page.tsx
       └─> getCurrentUser()
           ├─> User authenticated?
           │   └─> redirect('/dashboard')
           │
           └─> Not authenticated?
               └─> redirect('/login')
```

### Dashboard Access
```
User visits /dashboard
   └─> src/app/dashboard/layout.tsx
       └─> requireAuthRedirect()
           ├─> User authenticated?
           │   └─> Render dashboard and children
           │   └─> Protection applies to ALL /dashboard/* routes
           │
           └─> Not authenticated?
               └─> redirect('/login')
```

### Auth Pages (Already Logged In)
```
Authenticated user visits /login or /register
   └─> src/app/(auth)/layout.tsx
       └─> getCurrentUser()
           ├─> User authenticated?
           │   └─> redirect('/dashboard')
           │   └─> Prevents unnecessary auth page access
           │
           └─> Not authenticated?
               └─> Render login/register page
```

## OAuth Flow (GitHub)

```
Step 1: User clicks "Sign in with GitHub"
   └─> src/app/(auth)/login/page.tsx
       └─> Calls: loginWithGithubAction()

Step 2: Server initiates OAuth
   └─> src/app/(auth)/login/actions.ts
       └─> supabase.auth.signInWithOAuth({ provider: 'github' })
       └─> Returns OAuth URL

Step 3: Redirect to GitHub
   └─> redirect(data.url)
       └─> User authenticates on GitHub
       └─> GitHub redirects back with token in URL hash

Step 4: Callback handler processes OAuth
   └─> src/app/auth/callback/route.ts
       └─> Extracts token from URL
       └─> Verifies with Supabase
       └─> redirect('/dashboard')
```

## Email Verification Resend Flow

```
Step 1: User on confirmation page
   └─> src/app/(auth)/confirm-signup/page.tsx
       └─> Clicks "Resend verification email"

Step 2: Call resend action
   └─> src/app/(auth)/confirm-signup/actions.ts
       └─> resendVerificationEmail()
       └─> Gets current user from session
       └─> supabase.auth.resend({ type: 'signup', email })

Step 3: New email sent
   └─> User receives new magic link
       └─> Clicks link
       └─> Routes to /auth/callback
       └─> Verification completes
```

## Logout Flow

```
Step 1: User clicks logout
   └─> Call logoutAction()

Step 2: Server clears session
   └─> src/app/(auth)/login/actions.ts
       └─> logoutAction()
       └─> supabase.auth.signOut()
       └─> Clears httpOnly cookies

Step 3: Return success
   └─> { success: true }
       └─> Client-side redirect to /login
```

## Middleware Token Refresh Flow

```
Every Request:
   └─> src/middleware.ts
       └─> Calls: updateSession(request)
           └─> src/lib/supabase/middleware.ts
               ├─> Creates Supabase client
               ├─> Calls: supabase.auth.getUser()
               │   └─> Validates token with Supabase server
               │   └─> Refreshes token if needed
               │
               └─> Sets cookies on both:
                   ├─> request (for Server Components)
                   └─> response (for browser)

This ensures:
   - Tokens are always fresh
   - Server Components have valid auth state
   - Expired tokens are automatically refreshed
   - No manual refresh logic needed
```

## Multi-Tenant Access Flow

```
User attempts to access family data
   └─> Server Action: getFamilyData(familyId)
       └─> requireFamilyAccess(familyId)
           ├─> Gets user's familyId from getUserData()
           │
           ├─> user.familyId === familyId?
           │   └─> YES: Allow access
           │   └─> Data fetched and returned
           │
           └─> user.familyId !== familyId?
               └─> NO: Throw ForbiddenError
               └─> "Access to this family data is not allowed"
```

## Admin Access Flow

```
User visits admin page
   └─> AdminPage component
       └─> requireAdminRedirect()
           ├─> getCurrentUser()
           │   └─> Not authenticated?
           │       └─> redirect('/login')
           │
           └─> getUserData()
               ├─> role === 'admin'?
               │   └─> Render admin page
               │
               └─> role !== 'admin'?
                   └─> redirect('/dashboard?error=unauthorized')
```
