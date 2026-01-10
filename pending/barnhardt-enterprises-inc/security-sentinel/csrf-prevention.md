# CSRF Prevention (Next.js)

Complete guide to preventing Cross-Site Request Forgery (CSRF) attacks in Next.js applications.

---

## Table of Contents

1. [Understanding CSRF Attacks](#understanding-csrf-attacks)
2. [SameSite Cookies](#samesite-cookies)
3. [CSRF Tokens](#csrf-tokens)
4. [Double Submit Cookie](#double-submit-cookie)
5. [Server Actions Protection](#server-actions-protection)
6. [Origin Header Validation](#origin-header-validation)

---

## Understanding CSRF Attacks

### What is CSRF?

CSRF (Cross-Site Request Forgery) tricks victims into executing unwanted actions on a web application where they're authenticated.

**Attack Scenario:**
```html
<!-- Attacker's website: evil.com -->
<html>
<body>
  <!-- Hidden form that submits to victim's bank -->
  <form action="https://bank.com/api/transfer" method="POST" id="hack">
    <input type="hidden" name="to" value="attacker" />
    <input type="hidden" name="amount" value="10000" />
  </form>
  <script>
    // Auto-submit when victim visits page
    document.getElementById('hack').submit()
  </script>
</body>
</html>
```

**What happens:**
1. Victim is logged into bank.com
2. Victim visits evil.com
3. Evil.com submits form to bank.com
4. Browser automatically includes victim's session cookies
5. Bank processes the transfer as if victim initiated it

---

## SameSite Cookies

### SameSite Attribute

The SameSite cookie attribute is the **primary defense** against CSRF in modern browsers.

```typescript
// ✅ BEST: SameSite=Strict
cookies().set('session', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',  // Cookie never sent in cross-site requests
  maxAge: 60 * 60 * 24,  // 24 hours
  path: '/',
})

// ✅ GOOD: SameSite=Lax (allows top-level navigation)
cookies().set('session', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',  // Cookie sent only on safe cross-site requests (GET)
  maxAge: 60 * 60 * 24,
  path: '/',
})

// ❌ BAD: SameSite=None
cookies().set('session', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'none',  // Cookie sent in all cross-site requests (vulnerable!)
  maxAge: 60 * 60 * 24,
  path: '/',
})
```

### When to Use Each Value

| SameSite Value | Use Case | CSRF Protection |
|----------------|----------|-----------------|
| `strict` | Same-origin only apps | ✅ Full protection |
| `lax` | Apps needing external links to work | ✅ Good protection |
| `none` | Cross-origin APIs, third-party integrations | ❌ No protection |

**Example scenarios:**

```typescript
// ✅ Use 'strict' for internal apps
export async function setAuthCookie(sessionId: string) {
  cookies().set('auth-token', sessionId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',  // Best security
  })
}

// ✅ Use 'lax' if users share links via email
export async function setAuthCookieLax(sessionId: string) {
  cookies().set('auth-token', sessionId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',  // Allows following emailed links
  })
}

// ⚠️ Use 'none' only for embedded widgets
export async function setEmbedCookie(sessionId: string) {
  cookies().set('embed-token', sessionId, {
    httpOnly: true,
    secure: true,  // MUST be true when sameSite=none
    sameSite: 'none',  // Required for iframe embeds
  })
}
```

---

## CSRF Tokens

### Token Generation

```typescript
// src/lib/csrf.ts
import crypto from 'crypto'
import { cookies } from 'next/headers'

// ✅ Generate CSRF token
export async function generateCSRFToken(): Promise<string> {
  const token = crypto.randomBytes(32).toString('hex')

  // Store in httpOnly cookie
  cookies().set('csrf-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
  })

  return token
}

// ✅ Verify CSRF token
export async function verifyCSRFToken(token: string): Promise<boolean> {
  const cookieToken = cookies().get('csrf-token')?.value

  if (!cookieToken || !token) {
    return false
  }

  // Constant-time comparison to prevent timing attacks
  return crypto.timingSafeEqual(
    Buffer.from(cookieToken),
    Buffer.from(token)
  )
}
```

### Token Usage in Forms

```typescript
// src/app/page.tsx
export default async function HomePage() {
  const csrfToken = await generateCSRFToken()

  return (
    <form action="/api/submit" method="POST">
      {/* Hidden CSRF token field */}
      <input type="hidden" name="csrf-token" value={csrfToken} />

      <input type="text" name="message" />
      <button type="submit">Submit</button>
    </form>
  )
}

// src/app/api/submit/route.ts
export async function POST(request: Request) {
  const formData = await request.formData()
  const csrfToken = formData.get('csrf-token') as string

  // ✅ Verify CSRF token
  const isValid = await verifyCSRFToken(csrfToken)

  if (!isValid) {
    return Response.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    )
  }

  // Process form...
  return Response.json({ success: true })
}
```

### Token Usage in AJAX

```typescript
// Server: Generate and send token
export async function GET() {
  const csrfToken = await generateCSRFToken()

  return Response.json({
    csrfToken,
  })
}

// Client: Include token in requests
'use client'

import { useState, useEffect } from 'react'

export function ProtectedForm() {
  const [csrfToken, setCSRFToken] = useState('')

  useEffect(() => {
    // Fetch CSRF token on mount
    fetch('/api/csrf-token')
      .then(r => r.json())
      .then(data => setCSRFToken(data.csrfToken))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    await fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken,  // Include token in header
      },
      body: JSON.stringify({ message: 'Hello' }),
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="message" />
      <button type="submit">Submit</button>
    </form>
  )
}

// Server: Verify token from header
export async function POST(request: Request) {
  const csrfToken = request.headers.get('X-CSRF-Token')

  if (!csrfToken) {
    return Response.json({ error: 'Missing CSRF token' }, { status: 403 })
  }

  const isValid = await verifyCSRFToken(csrfToken)

  if (!isValid) {
    return Response.json({ error: 'Invalid CSRF token' }, { status: 403 })
  }

  // Process request...
  return Response.json({ success: true })
}
```

---

## Double Submit Cookie

### Implementation

```typescript
// src/lib/csrf-double-submit.ts
import crypto from 'crypto'
import { cookies } from 'next/headers'

// ✅ Set CSRF cookie (not httpOnly - client needs to read it)
export async function setCSRFCookie(): Promise<string> {
  const token = crypto.randomBytes(32).toString('hex')

  cookies().set('csrf-token', token, {
    httpOnly: false,  // Client needs to read this
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
  })

  return token
}

// ✅ Verify double submit
export async function verifyDoubleSubmit(requestToken: string): Promise<boolean> {
  const cookieToken = cookies().get('csrf-token')?.value

  if (!cookieToken || !requestToken) {
    return false
  }

  return crypto.timingSafeEqual(
    Buffer.from(cookieToken),
    Buffer.from(requestToken)
  )
}
```

### Client-Side Usage

```typescript
'use client'

export function ProtectedFormDoubleSubmit() {
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Read CSRF token from cookie
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf-token='))
      ?.split('=')[1]

    await fetch('/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken!,  // Send token in header
      },
      body: JSON.stringify({ message: 'Hello' }),
    })
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

---

## Server Actions Protection

### Automatic CSRF Protection

Next.js Server Actions have **built-in CSRF protection** in Next.js 14+.

```typescript
// src/app/actions/submit.ts
'use server'

// ✅ Automatically protected against CSRF
export async function submitForm(formData: FormData) {
  const message = formData.get('message')

  // Process form...
  return { success: true }
}

// src/app/page.tsx
import { submitForm } from './actions/submit'

export default function Page() {
  return (
    <form action={submitForm}>
      <input type="text" name="message" />
      <button type="submit">Submit</button>
    </form>
  )
}
```

### Additional Verification

```typescript
'use server'

import { headers } from 'next/headers'

export async function submitForm(formData: FormData) {
  // ✅ Additional origin check
  const headersList = headers()
  const origin = headersList.get('origin')
  const host = headersList.get('host')

  if (origin && !origin.endsWith(host || '')) {
    throw new Error('Invalid origin')
  }

  // Process form...
  return { success: true }
}
```

---

## Origin Header Validation

### Validate Origin/Referer

```typescript
// src/lib/csrf-origin.ts
import { headers } from 'next/headers'

export async function validateOrigin(): Promise<boolean> {
  const headersList = headers()

  // Get origin and referer
  const origin = headersList.get('origin')
  const referer = headersList.get('referer')
  const host = headersList.get('host')

  if (!host) {
    return false
  }

  // Check origin header
  if (origin) {
    try {
      const originURL = new URL(origin)
      if (originURL.host !== host) {
        return false  // Different origin
      }
    } catch {
      return false  // Invalid origin
    }
  }

  // Check referer header (fallback)
  if (!origin && referer) {
    try {
      const refererURL = new URL(referer)
      if (refererURL.host !== host) {
        return false  // Different referer
      }
    } catch {
      return false  // Invalid referer
    }
  }

  return true
}
```

### Middleware Implementation

```typescript
// src/middleware.ts
import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  // Only check for state-changing methods
  if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
    return NextResponse.next()
  }

  const origin = request.headers.get('origin')
  const host = request.headers.get('host')

  // Validate origin
  if (origin) {
    try {
      const originURL = new URL(origin)
      if (originURL.host !== host) {
        return NextResponse.json(
          { error: 'Invalid origin' },
          { status: 403 }
        )
      }
    } catch {
      return NextResponse.json(
        { error: 'Invalid origin' },
        { status: 403 }
      )
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}
```

---

## Complete CSRF Protection Example

### Multi-Layer Defense

```typescript
// src/lib/csrf-protection.ts
import crypto from 'crypto'
import { cookies, headers } from 'next/headers'

export async function generateCSRFToken(): Promise<string> {
  const token = crypto.randomBytes(32).toString('hex')

  cookies().set('csrf-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
  })

  return token
}

export async function verifyCSRFProtection(token?: string): Promise<boolean> {
  // Layer 1: Verify CSRF token
  if (token) {
    const cookieToken = cookies().get('csrf-token')?.value

    if (!cookieToken) {
      return false
    }

    const tokensMatch = crypto.timingSafeEqual(
      Buffer.from(cookieToken),
      Buffer.from(token)
    )

    if (!tokensMatch) {
      return false
    }
  }

  // Layer 2: Validate origin
  const headersList = headers()
  const origin = headersList.get('origin')
  const host = headersList.get('host')

  if (origin && host) {
    try {
      const originURL = new URL(origin)
      if (originURL.host !== host) {
        return false
      }
    } catch {
      return false
    }
  }

  return true
}

// API Route Usage
export async function POST(request: Request) {
  const csrfToken = request.headers.get('X-CSRF-Token')

  const isValid = await verifyCSRFProtection(csrfToken || undefined)

  if (!isValid) {
    return Response.json(
      { error: 'CSRF validation failed' },
      { status: 403 }
    )
  }

  // Process request...
  return Response.json({ success: true })
}
```

---

## Summary Checklist

**CSRF Prevention:**

- [ ] All session cookies use `sameSite=strict` or `sameSite=lax`
- [ ] All session cookies use `httpOnly=true`
- [ ] All session cookies use `secure=true` in production
- [ ] CSRF tokens implemented for state-changing operations
- [ ] CSRF tokens verified on server for POST/PUT/PATCH/DELETE
- [ ] Origin header validated for API requests
- [ ] Referer header validated as fallback
- [ ] Server Actions used (built-in CSRF protection)
- [ ] No `sameSite=none` unless absolutely necessary
- [ ] CSRF protection tested with cross-origin requests
- [ ] Custom headers required for AJAX requests (e.g., X-Requested-With)
- [ ] Rate limiting on authentication endpoints

**Defense in Depth:**

Use multiple layers:
1. **SameSite cookies** (primary defense)
2. **CSRF tokens** (secondary defense)
3. **Origin/Referer validation** (tertiary defense)
4. **Custom headers** (additional defense for AJAX)

**References:**
- OWASP CSRF: https://owasp.org/www-community/attacks/csrf
- SameSite Cookie Spec: https://tools.ietf.org/html/draft-ietf-httpbis-cookie-same-site
- Next.js Security: https://nextjs.org/docs/app/building-your-application/routing/middleware
