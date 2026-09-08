# Authentication SDK Integration

User authentication, registration, and session management via `insforge.auth`.

> **Package choice**: Use `@insforge/sdk` directly for authentication flows. Build auth UI components with the SDK methods documented below.

> **Auth email delivery is built in.** Signup verification, password reset, magic links, and invites ship on **every plan** (free included) through the InsForge platform. For custom transactional email, see [email/sdk-integration.md](../email/sdk-integration.md).

## Setup

First, ensure your `.env` file is configured with your InsForge URL and anon key. Get the anon key with `npx -y @insforge/cli secrets get ANON_KEY`. See the main [SKILL.md](../SKILL.md) for framework-specific variable names and full setup steps.

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,       // adjust prefix for your framework
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY   // adjust prefix for your framework
})
```

## SSR / Server-Rendered Apps

For Next.js, Remix, SvelteKit, Nuxt server routes, or any other SSR setup, use `@insforge/sdk/ssr` helpers. See [ssr-integration.md](ssr-integration.md) for the full pattern and minimal examples.

## Sign Up (Complete Flow)

Registration may require email verification. Implement the flow based on backend config.

1. **Sign up** — Create the user account
2. **If verification is required** — Branch on `verifyEmailMethod`
3. **Complete the verification flow**
   - `code`: user enters the 6-digit code and your app calls `verifyEmail()`
   - `link`: backend verifies the emailed link first, then redirects to your app via `redirectTo`

> **Important**: For link-based verification, pass `redirectTo` to `signUp()`. Recommended: use your sign-in page as `redirectTo`, then show a success message and ask the user to sign in with their email and password.

```javascript
try {
  // Step 1: Register the user
  const { data, error } = await insforge.auth.signUp({
    email: 'user@example.com',
    password: 'securepassword123',
    name: 'John Doe',
    redirectTo: 'http://localhost:3000/sign-in'
  })

  if (error) throw error

  if (data?.requireEmailVerification) {
    // Code method:
    // - Show a 6-digit code input on the same page
    // - Call verifyEmail({ email, otp })
    //
    // Link method:
    // - Show "Check your email"
    // - Recommended redirectTo: your sign-in page
    // - On redirect success, show a confirmation message and ask the user to sign in

  } else if (data?.accessToken) {
    // No verification required — user is already signed in
    console.log('Signed in:', data.user)
  }

} catch (error) {
  console.error('Registration flow failed:', error.message)
}
```

### Resend Verification Email

```javascript
try {
  await insforge.auth.resendVerificationEmail({
    email: 'user@example.com',
    redirectTo: 'http://localhost:3000/sign-in'
  })
  console.log('Verification email resent.')
} catch (error) {
  console.error('Failed to resend:', error.message)
}
```

## Sign In

```javascript
const { data, error } = await insforge.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securepassword123'
})

if (error) {
  console.error('Sign in failed:', error.message)
  if (error.statusCode === 403) {
    console.error('Email not verified. Redirect to verification page.')
  }
} else {
  console.log('Signed in:', data.user.email)
}
```

## Passwordless Sign In (Email OTP)

> Requires `@insforge/sdk` 1.5.1+.

Two steps: request a code, then verify it. `verifyOtp()` returns `{ data: { user, accessToken }, error }` and **automatically saves the session** — the user is signed in on success. When signups are enabled a brand-new email becomes a verified, passwordless user (with `disableSignup` on, `verifyOtp()` rejects unknown emails with a 403); `name` sets the display name only when the account is first created.

```javascript
// 1. Request the 6-digit code. The response is generic whether or not an
//    account exists (prevents account enumeration) — always show the same
//    "check your email" state.
const { error: sendError } = await insforge.auth.signInWithOtp({
  email: 'user@example.com'
})
if (sendError) console.error('Could not send code:', sendError.message)

// 2. Verify the code the user typed in.
const { data, error } = await insforge.auth.verifyOtp({
  email: 'user@example.com',
  otp: '123456',
  name: 'Ada Lovelace' // optional; applied only when the account is first created
})

if (error) {
  console.error('Invalid or expired code:', error.message)
} else {
  console.log('Signed in:', data.user.email)
}
```

> The code expires in 5 minutes, is single-use, and is invalidated after 3 failed attempts. A wrong entry can be retried with the same code; once it expires or the three attempts are used up, have the user request a fresh one with `signInWithOtp()`.

## OAuth Sign In

OAuth uses PKCE. The SDK handles code generation, redirect, and token exchange automatically in the browser.

### Two redirect URLs

| URL | Points to | Where to configure |
|-----|-----------|-------------------|
| OAuth provider callback | InsForge backend (`https://<project>.insforge.app/api/auth/oauth/<provider>/callback`) | Google Console, GitHub OAuth app, etc. |
| `redirectTo` | **Your app** (`https://yourapp.com/auth/callback`) | Passed in `signInWithOAuth()` |

`redirectTo` is where the user lands after auth. The backend appends `?insforge_code=<code>` to it. Set it to a page where your app initializes the SDK or handles the server callback.

### SPA (browser) — fully automatic

```javascript
await insforge.auth.signInWithOAuth('google', {
  redirectTo: 'http://localhost:3000/dashboard', // any page where SDK is initialized
  additionalParams: { prompt: 'select_account' } // optional provider-specific params
})
```

Use `additionalParams` only for provider-specific optional hints. Do not pass server-owned OAuth fields such as `client_id`, `scope`, `redirect_uri`, `code_challenge`, `state`, or `response_type`; InsForge sets those server-side and ignores colliding client-provided keys.

The SDK constructor auto-detects `insforge_code` in the URL, exchanges it for a session, and cleans the URL. Initialize the SDK on the `redirectTo` page.

### SSR (Next.js) — manual exchange required

The browser auto-detection is for SPA flows. In SSR apps, use `skipBrowserRedirect: true` and exchange the OAuth code in a Route Handler so the refresh token can be written as an httpOnly cookie. See [ssr-integration.md](ssr-integration.md) for the full implementation.

```javascript
const { data } = await insforge.auth.signInWithOAuth('google', {
  redirectTo: 'https://yourapp.com/api/auth/callback',
  skipBrowserRedirect: true
})
// data.codeVerifier — store in httpOnly cookie before redirect
// data.url — redirect user to this
```

### SDK methods reference

| Method | When to use |
|--------|-------------|
| `signInWithOAuth(provider, { redirectTo, additionalParams? })` | SPA: auto-redirects and handles everything |
| `signInWithOAuth(provider, { redirectTo, additionalParams?, skipBrowserRedirect: true })` | SSR: returns `{ url, codeVerifier }` for manual handling |
| `exchangeOAuthCode(code, codeVerifier?)` | Exchange `insforge_code` for session. Auto-called in SPA; call manually in SSR |

## Sign Out

```javascript
const { error } = await insforge.auth.signOut()
```

## Get Current User

```javascript
const { data, error } = await insforge.auth.getCurrentUser()

if (data.user) {
  console.log('User:', data.user.email)
}
```

For browser apps, call `getCurrentUser()` during startup. The SDK will use the httpOnly refresh cookie automatically when it can refresh the session.

For SSR apps, use `createRefreshAuthRouter()` / `refreshAuth()` from `@insforge/sdk/ssr` to refresh through your app route.

### Cold loads & external redirects

In SPA browser apps using the root `@insforge/sdk` client, the access token is stored in memory only. On a cold page load, `getCurrentUser()` starts with no in-memory access token, so the SDK rehydrates the session by calling the backend refresh endpoint with the httpOnly refresh cookie and the JS-readable `insforge_csrf_token` cookie/header flow. During that network round-trip, `user` is temporarily `null`.

In SSR browser clients created with `createBrowserClient()` from `@insforge/sdk/ssr`, the access token is read from the `insforge_access_token` cookie and refreshed through your app's `/api/auth/refresh` route.

Any auth wrapper or hook should expose both `user` and `loading`:

```tsx
import { createContext, useContext, useEffect, useState } from 'react'

const AuthContext = createContext({ user: null, loading: true })

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function hydrateAuth() {
      const { data, error } = await insforge.auth.getCurrentUser()
      if (cancelled) return
      setUser(error ? null : (data?.user ?? null))
      setLoading(false)
    }

    void hydrateAuth()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
```

When auth state controls visible UI, gate the logged-in vs logged-out branch on `loading`:

```tsx
function Layout() {
  const { user, loading } = useAuth()

  return (
    <header>
      {loading ? <div className="auth-skeleton" /> : user ? <AccountMenu /> : <SignInButton />}
    </header>
  )
}
```

This matters most when the user lands back in your app after an external redirect:

- Post-OAuth callback
- Stripe Checkout success or cancel URL
- Stripe Customer Portal return URL
- Password-reset link landing
- Email-verification link landing

### Gate user-dependent side effects during auth loading

If a mount-time effect branches on the current user, guard the user-dependent work until `loading === false`. This is especially important for code paths that do one thing for signed-in users and another for guests.

```tsx
const [shouldRunAction, setShouldRunAction] = useState(false)
const handled = useRef(false)
const userId = user?.id ?? null

useEffect(() => {
  const handleStatusChanged = ({ id, status }) => {
    if (id === resourceId && status === 'ready') {
      setShouldRunAction(true)
    }
  }

  insforge.realtime.on('status_changed', handleStatusChanged)
  return () => insforge.realtime.off('status_changed', handleStatusChanged)
}, [resourceId])

useEffect(() => {
  if (loading || !shouldRunAction || handled.current) return

  async function runUserDependentAction() {
    await performUserDependentAction({ userId })
    handled.current = true
  }

  void runUserDependentAction()
}, [loading, shouldRunAction, userId])
```

Webhook-backed Realtime flows can complete before the cold-load auth refresh finishes, especially after Stripe Checkout, Customer Portal, OAuth, password-reset, or email-verification redirects. If you use a `cleared.current` or other "first event wins" guard, flip it after `loading === false` and the user-dependent work has actually succeeded.

## Profile Management

In SQL triggers and migrations, user profile metadata lives in
`auth.users.profile` JSONB. Read common values with `NEW.profile->>'name'` and
`NEW.profile->>'avatar_url'`.

```javascript
// Get any user's public profile
const { data } = await insforge.auth.getProfile('user-id')

// Update current user's profile
const { data } = await insforge.auth.setProfile({
  name: 'John',
  avatar_url: 'https://...',
  custom_field: 'value'
})
```

## Email Verification

`verifyEmail()` returns `{ data: { user, accessToken }, error }` and **automatically saves the session** — the user is signed in after successful verification.

```javascript
// Verify with code (6-digit OTP from email)
const { data, error } = await insforge.auth.verifyEmail({
  email: 'user@example.com',
  otp: '123456'
})

if (error) {
  if (error.statusCode === 400) {
    console.error('Invalid or expired code')
  }
} else {
  // User is now verified AND signed in
  console.log('Signed in:', data.user)
}

// Resend verification email
await insforge.auth.resendVerificationEmail({
  email: 'user@example.com',
  redirectTo: 'http://localhost:3000/sign-in'
})
```

### Link Verification Flow

Use `redirectTo` for link-based verification. Recommended: use your sign-in page.

Your frontend should handle these redirect query params:

- `insforge_status`: `success` or `error`
- `insforge_type`: always `verify_email`
- `insforge_error`: present only on error

When `insforge_status=success`, show a confirmation message and ask the user to sign in with their email and password.

## Password Reset

```javascript
// Step 1: Send reset email
await insforge.auth.sendResetPasswordEmail({
  email: 'user@example.com',
  redirectTo: 'http://localhost:3000/reset-password'
})

// Step 2: Code method — exchange code for token
const { data } = await insforge.auth.exchangeResetPasswordToken({
  email: 'user@example.com',
  code: '123456'
})

// Step 3: Reset password
await insforge.auth.resetPassword({
  newPassword: 'newPassword123',
  otp: data.token // or token from magic link
})
```

### Link Reset Flow

Use `redirectTo` for link-based reset. Recommended: use your app's dedicated reset-password page.

Your frontend should handle these redirect query params:

- `token`: present only when the reset form should be shown
- `insforge_status`: `ready` or `error`
- `insforge_type`: always `reset_password`
- `insforge_error`: present only on error

Only render the reset form when `insforge_status=ready` and `token` is present.

## Important Notes

- **SPA Web vs Mobile**: Root browser SDK flows use httpOnly refresh cookies + CSRF; mobile/desktop returns refreshToken in response
- **SSR apps should use SDK SSR helpers**: For Next.js and similar SSR frameworks, use `@insforge/sdk/ssr` for client creation, refresh routes, and auth cookies; use `@insforge/sdk/ssr/middleware` for Proxy/Middleware session updates. See [ssr-integration.md](ssr-integration.md)
- All methods return `{ data, error }` — always check for errors
- OAuth uses PKCE flow for security

---

## Best Practices

1. **Always check auth config first** before implementing
   - Run `npx -y @insforge/cli metadata --json` to get auth config (`requireEmailVerification`, `verifyEmailMethod`, `resetPasswordMethod`, `oAuthProviders`, `allowedRedirectUrls`)
   - This tells you what features to implement
   - To change supported project config such as redirect URLs, verification flags, password policy, or auth SMTP settings, use `npx -y @insforge/cli config apply` — see the **insforge-cli** skill's Configuration section. OAuth providers and external app setup are dashboard/provider-managed.

2. **The sign-up page must handle the full registration flow**
   - After calling `signUp()`, if `requireEmailVerification` is true, branch on `verifyEmailMethod`
   - For `"code"`, switch the UI to show a 6-digit code input on the **same page**
   - For `"link"`, pass `redirectTo` to `signUp()` and show a "check your email" state
   - Keep the user in the verification flow until verification is completed
   - Recommended verification `redirectTo`: your sign-in page
   - `verifyEmail()` automatically saves the session only for the code flow

3. **Render OAuth from configured providers**
   - Check `oAuthProviders` array in config
   - The array contains enabled provider names (e.g., `["google", "github"]`)

4. **Handle the sign-up response correctly**
   ```javascript
   const { data, error } = await insforge.auth.signUp({...})

   if (error) {
     // Show error message to user
   } else if (data?.requireEmailVerification) {
     // Usually: switch UI to show 6-digit code input and keep the user in the verification flow
     // If verifyEmailMethod === "link", show a "check your email" state instead
   } else if (data?.accessToken) {
     // No verification needed — user is signed in, navigate to app
   }
   ```

5. **Use `@insforge/sdk/ssr` for SSR auth**
   - For Next.js or other SSR frameworks, perform auth mutations where cookies can be written
   - Use `createAuthActions()` for sign-in, sign-up, sign-out, OAuth initiation/exchange, ID-token sign-in, and email verification flows that create or clear sessions
   - Keep `insforge_refresh_token` httpOnly and server-owned
   - Let `insforge_access_token` be browser-readable so Storage and Realtime can authenticate from Client Components
   - Use `createServerClient()` for Server Components / Route Handlers and `createBrowserClient()` for Client Components; the SSR browser client exposes read-only auth methods only
   - Add `/api/auth/refresh` with `createRefreshAuthRouter()` and use `updateSession()` from `@insforge/sdk/ssr/middleware` in Proxy/Middleware
   - Use [ssr-integration.md](ssr-integration.md) as the reference implementation

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Navigating to dashboard/home while verification is still required | Stay in the verification flow and branch on `verifyEmailMethod` |
| Skipping the email verification step | Check `requireEmailVerification` in the sign-up response and implement the verification step |
| Missing `redirectTo` for link flows | Pass the app URL as `redirectTo` and include it in `allowedRedirectUrls` |
| Building the wrong verification UI | Build the UI from `verifyEmailMethod` |
| Treating link verification like code verification | Handle the redirect result and send the user to sign in |
| Signing in again after code-based `verifyEmail()` | Use the session returned by `verifyEmail()` |
| Hardcoding OAuth providers | Render providers from `oAuthProviders` |
| Handling SSR auth like a browser-only flow | Use `createAuthActions()` for auth mutations, `createBrowserClient()` only to consume an existing SSR session, and `@insforge/sdk/ssr/middleware` for Proxy/Middleware session updates |
| Passing `apiKey` to `createClient()` | Use `createAdminClient({ apiKey })` in trusted server-only code |

## Conditional Implementation Guide

### Email Verification Flow

```javascript
// After sign-up, check if verification is needed
if (data?.requireEmailVerification) {
  // If verifyEmailMethod === "code":
  //   Show 6-digit code input on the SAME page, then call:
  const { data: verifyData, error } = await insforge.auth.verifyEmail({ email, otp: userEnteredCode })
  //   On success, user is automatically signed in — navigate to the app

  // If verifyEmailMethod === "link":
  //   Pass redirectTo to signUp() / resendVerificationEmail()
  //   Show "Check your email and click the verification link" message
  //   Recommended redirectTo: your sign-in page
  //   On redirect success, show a confirmation message and ask the user to sign in
}
```

### OAuth Implementation

```javascript
// oAuthProviders is already an array of enabled provider names
// e.g., ["google", "github"]
const enabledProviders = authConfig.oAuthProviders

// Show OAuth buttons from enabled providers:
if (enabledProviders.includes('google')) {
  // Show Google login button
}
if (enabledProviders.includes('github')) {
  // Show GitHub login button
}
```

## Recommended Workflow

```
1. Get auth config           → npx -y @insforge/cli metadata --json
2. Check what's enabled      → Email verification? Which OAuth providers?
3. Build appropriate UI      → Code input vs magic link, OAuth buttons
4. Implement sign-up         → Handle requireEmailVerification response
5. Implement verification    → Code input or redirectTo-based link flow
6. Implement OAuth           → Use providers from oAuthProviders
7. Implement password reset  → Based on resetPasswordMethod (code vs link)
```

## Implementation Checklist

Based on auth config, implement:

- [ ] Sign up form with password (respecting `passwordMinLength`)
- [ ] Email verification step on the sign-up page (if `requireEmailVerification` is true)
  - [ ] 6-digit code input (if `verifyEmailMethod` is "code")
  - [ ] "Check your email" state plus sign-in-page `redirectTo` handling (if `verifyEmailMethod` is "link")
- [ ] Sign in form
- [ ] OAuth buttons from enabled providers
- [ ] Password reset flow
  - [ ] Code input (if `resetPasswordMethod` is "code")
  - [ ] App reset page using `redirectTo` (if `resetPasswordMethod` is "link")
- [ ] Sign out
