# Authentication Patterns

Complete reference for secure authentication implementation in Next.js 15 with App Router.

---

## Table of Contents

1. [JWT Token Authentication](#jwt-token-authentication)
2. [Session-Based Authentication](#session-based-authentication)
3. [Password Management](#password-management)
4. [Multi-Factor Authentication](#multi-factor-authentication)
5. [OAuth 2.0 Integration](#oauth-20-integration)
6. [Passwordless Authentication](#passwordless-authentication)
7. [Security Best Practices](#security-best-practices)

---

## JWT Token Authentication

### Basic JWT Implementation

```typescript
// src/lib/auth/jwt.ts
import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'

const SECRET_KEY = new TextEncoder().encode(
  process.env.JWT_SECRET || throwError('JWT_SECRET not set')
)

function throwError(message: string): never {
  throw new Error(message)
}

export interface JWTPayload {
  userId: string
  email: string
  role: string
  iat?: number
  exp?: number
}

// ✅ Generate JWT token
export async function createToken(payload: Omit<JWTPayload, 'iat' | 'exp'>): Promise<string> {
  const token = await new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('24h')  // Token expires in 24 hours
    .sign(SECRET_KEY)

  return token
}

// ✅ Verify JWT token
export async function verifyToken(token: string): Promise<JWTPayload> {
  try {
    const { payload } = await jwtVerify(token, SECRET_KEY, {
      algorithms: ['HS256'],
    })

    return payload as JWTPayload
  } catch (error) {
    throw new Error('Invalid or expired token')
  }
}

// ✅ Get current user from token
export async function getCurrentUser(): Promise<JWTPayload | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get('auth-token')?.value

  if (!token) {
    return null
  }

  try {
    return await verifyToken(token)
  } catch {
    return null
  }
}

// ✅ Set auth cookie
export async function setAuthCookie(token: string) {
  const cookieStore = await cookies()

  cookieStore.set('auth-token', token, {
    httpOnly: true,  // Not accessible via JavaScript
    secure: process.env.NODE_ENV === 'production',  // HTTPS only in production
    sameSite: 'strict',  // CSRF protection
    maxAge: 60 * 60 * 24,  // 24 hours
    path: '/',
  })
}

// ✅ Clear auth cookie
export async function clearAuthCookie() {
  const cookieStore = await cookies()
  cookieStore.delete('auth-token')
}
```

### Login Route

```typescript
// src/app/api/auth/login/route.ts
import { z } from 'zod'
import bcrypt from 'bcrypt'
import { db } from '@/lib/db'
import { createToken, setAuthCookie } from '@/lib/auth/jwt'

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(128),
})

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { email, password } = loginSchema.parse(body)

    // Find user
    const user = await db.user.findUnique({
      where: { email },
    })

    if (!user) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password)

    if (!isValid) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Create token
    const token = await createToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    })

    // Set cookie
    await setAuthCookie(token)

    return Response.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return Response.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Login error:', error)
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

### Refresh Token Pattern

```typescript
// src/lib/auth/refresh-token.ts
import { db } from '@/lib/db'
import { createToken } from './jwt'
import crypto from 'crypto'

// ✅ Generate refresh token
export async function createRefreshToken(userId: string): Promise<string> {
  const token = crypto.randomBytes(32).toString('hex')

  await db.refreshToken.create({
    data: {
      token,
      userId,
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),  // 30 days
    },
  })

  return token
}

// ✅ Use refresh token to get new access token
export async function refreshAccessToken(refreshToken: string): Promise<string | null> {
  const token = await db.refreshToken.findUnique({
    where: { token: refreshToken },
    include: { user: true },
  })

  if (!token) {
    return null
  }

  // Check expiration
  if (token.expiresAt < new Date()) {
    await db.refreshToken.delete({ where: { id: token.id } })
    return null
  }

  // Create new access token
  const accessToken = await createToken({
    userId: token.user.id,
    email: token.user.email,
    role: token.user.role,
  })

  return accessToken
}

// ✅ Revoke refresh token
export async function revokeRefreshToken(token: string): Promise<void> {
  await db.refreshToken.delete({ where: { token } })
}

// ✅ Revoke all user's refresh tokens
export async function revokeAllRefreshTokens(userId: string): Promise<void> {
  await db.refreshToken.deleteMany({ where: { userId } })
}
```

---

## Session-Based Authentication

### Session Management

```typescript
// src/lib/auth/session.ts
import { db } from '@/lib/db'
import { cookies } from 'next/headers'
import crypto from 'crypto'

export interface Session {
  id: string
  userId: string
  expiresAt: Date
  user?: {
    id: string
    email: string
    name: string
    role: string
  }
}

// ✅ Create session
export async function createSession(userId: string): Promise<string> {
  const sessionId = crypto.randomBytes(32).toString('hex')

  await db.session.create({
    data: {
      id: sessionId,
      userId,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),  // 24 hours
    },
  })

  return sessionId
}

// ✅ Get session
export async function getSession(sessionId: string): Promise<Session | null> {
  const session = await db.session.findUnique({
    where: { id: sessionId },
    include: {
      user: {
        select: {
          id: true,
          email: true,
          name: true,
          role: true,
        },
      },
    },
  })

  if (!session) {
    return null
  }

  // Check expiration
  if (session.expiresAt < new Date()) {
    await db.session.delete({ where: { id: sessionId } })
    return null
  }

  return session
}

// ✅ Get current session from cookies
export async function getCurrentSession(): Promise<Session | null> {
  const cookieStore = await cookies()
  const sessionId = cookieStore.get('session-id')?.value

  if (!sessionId) {
    return null
  }

  return getSession(sessionId)
}

// ✅ Delete session
export async function deleteSession(sessionId: string): Promise<void> {
  await db.session.delete({ where: { id: sessionId } })
}

// ✅ Delete all user sessions
export async function deleteUserSessions(userId: string): Promise<void> {
  await db.session.deleteMany({ where: { userId } })
}

// ✅ Set session cookie
export async function setSessionCookie(sessionId: string) {
  const cookieStore = await cookies()

  cookieStore.set('session-id', sessionId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 60 * 60 * 24,  // 24 hours
    path: '/',
  })
}

// ✅ Clear session cookie
export async function clearSessionCookie() {
  const cookieStore = await cookies()
  cookieStore.delete('session-id')
}

// ✅ Cleanup expired sessions (run as cron job)
export async function cleanupExpiredSessions(): Promise<number> {
  const result = await db.session.deleteMany({
    where: {
      expiresAt: {
        lt: new Date(),
      },
    },
  })

  return result.count
}
```

### Session Login

```typescript
// src/app/api/auth/session/login/route.ts
import { z } from 'zod'
import bcrypt from 'bcrypt'
import { db } from '@/lib/db'
import { createSession, setSessionCookie } from '@/lib/auth/session'

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(128),
  rememberMe: z.boolean().optional(),
})

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { email, password, rememberMe } = loginSchema.parse(body)

    // Find user
    const user = await db.user.findUnique({
      where: { email },
    })

    if (!user) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password)

    if (!isValid) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Create session
    const sessionId = await createSession(user.id)

    // Set cookie (longer expiration if "Remember Me" is checked)
    await setSessionCookie(sessionId)

    if (rememberMe) {
      const cookieStore = await cookies()
      cookieStore.set('session-id', sessionId, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 30 * 24 * 60 * 60,  // 30 days
        path: '/',
      })
    }

    return Response.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return Response.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Login error:', error)
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## Password Management

### Password Hashing

```typescript
// src/lib/auth/password.ts
import bcrypt from 'bcrypt'
import { z } from 'zod'

const SALT_ROUNDS = 12  // Minimum recommended: 10-12

// ✅ Strong password validation
export const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must not exceed 128 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character')

// ✅ Hash password
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS)
}

// ✅ Verify password
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

// ✅ Check if password needs rehash (if SALT_ROUNDS increased)
export function needsRehash(hash: string): boolean {
  const rounds = bcrypt.getRounds(hash)
  return rounds < SALT_ROUNDS
}

// ✅ Generate random password
export function generateRandomPassword(length: number = 16): string {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const lowercase = 'abcdefghijklmnopqrstuvwxyz'
  const numbers = '0123456789'
  const special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
  const all = uppercase + lowercase + numbers + special

  let password = ''
  password += uppercase[Math.floor(Math.random() * uppercase.length)]
  password += lowercase[Math.floor(Math.random() * lowercase.length)]
  password += numbers[Math.floor(Math.random() * numbers.length)]
  password += special[Math.floor(Math.random() * special.length)]

  for (let i = 4; i < length; i++) {
    password += all[Math.floor(Math.random() * all.length)]
  }

  // Shuffle
  return password.split('').sort(() => Math.random() - 0.5).join('')
}
```

### Password Reset Flow

```typescript
// src/lib/auth/password-reset.ts
import { db } from '@/lib/db'
import { sendEmail } from '@/lib/email'
import crypto from 'crypto'

// ✅ Generate password reset token
export async function createPasswordResetToken(email: string): Promise<string | null> {
  const user = await db.user.findUnique({ where: { email } })

  if (!user) {
    // Don't reveal if email exists
    return null
  }

  // Generate secure token
  const token = crypto.randomBytes(32).toString('hex')
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  // Delete old tokens
  await db.passwordResetToken.deleteMany({
    where: { userId: user.id },
  })

  // Create new token
  await db.passwordResetToken.create({
    data: {
      userId: user.id,
      token: hashedToken,
      expiresAt: new Date(Date.now() + 60 * 60 * 1000),  // 1 hour
    },
  })

  // Send email
  const resetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/auth/reset-password?token=${token}`

  await sendEmail({
    to: user.email,
    subject: 'Password Reset Request',
    html: `
      <p>You requested a password reset.</p>
      <p>Click the link below to reset your password:</p>
      <a href="${resetUrl}">${resetUrl}</a>
      <p>This link expires in 1 hour.</p>
      <p>If you didn't request this, please ignore this email.</p>
    `,
  })

  return token
}

// ✅ Verify password reset token
export async function verifyPasswordResetToken(token: string): Promise<string | null> {
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  const resetToken = await db.passwordResetToken.findUnique({
    where: { token: hashedToken },
  })

  if (!resetToken) {
    return null
  }

  // Check expiration
  if (resetToken.expiresAt < new Date()) {
    await db.passwordResetToken.delete({ where: { id: resetToken.id } })
    return null
  }

  return resetToken.userId
}

// ✅ Reset password
export async function resetPassword(token: string, newPassword: string): Promise<boolean> {
  const userId = await verifyPasswordResetToken(token)

  if (!userId) {
    return false
  }

  // Hash new password
  const hashedPassword = await hashPassword(newPassword)

  // Update user password
  await db.user.update({
    where: { id: userId },
    data: { password: hashedPassword },
  })

  // Delete reset token
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')
  await db.passwordResetToken.delete({ where: { token: hashedToken } })

  // Revoke all sessions (force re-login)
  await db.session.deleteMany({ where: { userId } })

  return true
}
```

### Email Verification

```typescript
// src/lib/auth/email-verification.ts
import { db } from '@/lib/db'
import { sendEmail } from '@/lib/email'
import crypto from 'crypto'

// ✅ Send verification email
export async function sendVerificationEmail(userId: string): Promise<void> {
  const user = await db.user.findUnique({ where: { id: userId } })

  if (!user) {
    throw new Error('User not found')
  }

  if (user.emailVerified) {
    throw new Error('Email already verified')
  }

  // Generate token
  const token = crypto.randomBytes(32).toString('hex')
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  // Delete old tokens
  await db.emailVerificationToken.deleteMany({
    where: { userId },
  })

  // Create new token
  await db.emailVerificationToken.create({
    data: {
      userId,
      token: hashedToken,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),  // 24 hours
    },
  })

  // Send email
  const verifyUrl = `${process.env.NEXT_PUBLIC_APP_URL}/auth/verify-email?token=${token}`

  await sendEmail({
    to: user.email,
    subject: 'Verify Your Email',
    html: `
      <p>Welcome to Quetrex!</p>
      <p>Please verify your email address by clicking the link below:</p>
      <a href="${verifyUrl}">${verifyUrl}</a>
      <p>This link expires in 24 hours.</p>
    `,
  })
}

// ✅ Verify email
export async function verifyEmail(token: string): Promise<boolean> {
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  const verificationToken = await db.emailVerificationToken.findUnique({
    where: { token: hashedToken },
  })

  if (!verificationToken) {
    return false
  }

  // Check expiration
  if (verificationToken.expiresAt < new Date()) {
    await db.emailVerificationToken.delete({ where: { id: verificationToken.id } })
    return false
  }

  // Mark email as verified
  await db.user.update({
    where: { id: verificationToken.userId },
    data: { emailVerified: true },
  })

  // Delete verification token
  await db.emailVerificationToken.delete({ where: { id: verificationToken.id } })

  return true
}
```

---

## Multi-Factor Authentication

### TOTP (Time-based One-Time Password)

```typescript
// src/lib/auth/mfa.ts
import speakeasy from 'speakeasy'
import QRCode from 'qrcode'
import { db } from '@/lib/db'

// ✅ Generate MFA secret
export async function generateMFASecret(userId: string): Promise<{
  secret: string
  qrCode: string
}> {
  const user = await db.user.findUnique({ where: { id: userId } })

  if (!user) {
    throw new Error('User not found')
  }

  // Generate secret
  const secret = speakeasy.generateSecret({
    name: `Quetrex (${user.email})`,
    issuer: 'Quetrex',
    length: 32,
  })

  // Store temporary secret (not enabled until verified)
  await db.user.update({
    where: { id: userId },
    data: {
      mfaSecret: secret.base32,
      mfaEnabled: false,
    },
  })

  // Generate QR code
  const qrCode = await QRCode.toDataURL(secret.otpauth_url!)

  return {
    secret: secret.base32,
    qrCode,
  }
}

// ✅ Enable MFA (after user scans QR code and verifies)
export async function enableMFA(userId: string, token: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { mfaSecret: true },
  })

  if (!user?.mfaSecret) {
    throw new Error('MFA secret not found')
  }

  // Verify token
  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: 'base32',
    token,
    window: 2,  // Allow 2 time steps before/after (60 seconds tolerance)
  })

  if (!verified) {
    return false
  }

  // Enable MFA
  await db.user.update({
    where: { id: userId },
    data: { mfaEnabled: true },
  })

  return true
}

// ✅ Disable MFA
export async function disableMFA(userId: string, token: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { mfaSecret: true, mfaEnabled: true },
  })

  if (!user?.mfaEnabled || !user.mfaSecret) {
    throw new Error('MFA not enabled')
  }

  // Verify token before disabling
  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: 'base32',
    token,
    window: 2,
  })

  if (!verified) {
    return false
  }

  // Disable MFA
  await db.user.update({
    where: { id: userId },
    data: {
      mfaEnabled: false,
      mfaSecret: null,
    },
  })

  return true
}

// ✅ Verify MFA token
export async function verifyMFA(userId: string, token: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { mfaSecret: true, mfaEnabled: true },
  })

  if (!user?.mfaEnabled || !user.mfaSecret) {
    return false
  }

  return speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: 'base32',
    token,
    window: 2,
  })
}

// ✅ Generate backup codes
export async function generateBackupCodes(userId: string): Promise<string[]> {
  const codes = Array.from({ length: 10 }, () =>
    crypto.randomBytes(4).toString('hex').toUpperCase()
  )

  // Hash codes before storing
  const hashedCodes = await Promise.all(
    codes.map((code) => bcrypt.hash(code, 10))
  )

  await db.user.update({
    where: { id: userId },
    data: { mfaBackupCodes: hashedCodes },
  })

  return codes
}

// ✅ Verify backup code
export async function verifyBackupCode(userId: string, code: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { mfaBackupCodes: true },
  })

  if (!user?.mfaBackupCodes || user.mfaBackupCodes.length === 0) {
    return false
  }

  // Check if code matches any backup code
  for (let i = 0; i < user.mfaBackupCodes.length; i++) {
    const match = await bcrypt.compare(code, user.mfaBackupCodes[i])

    if (match) {
      // Remove used code
      const remaining = user.mfaBackupCodes.filter((_, index) => index !== i)

      await db.user.update({
        where: { id: userId },
        data: { mfaBackupCodes: remaining },
      })

      return true
    }
  }

  return false
}
```

### MFA Login Flow

```typescript
// src/app/api/auth/mfa-login/route.ts
import { z } from 'zod'
import bcrypt from 'bcrypt'
import { db } from '@/lib/db'
import { verifyMFA, verifyBackupCode } from '@/lib/auth/mfa'
import { createToken, setAuthCookie } from '@/lib/auth/jwt'

const mfaLoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(128),
  mfaToken: z.string().optional(),
  backupCode: z.string().optional(),
})

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { email, password, mfaToken, backupCode } = mfaLoginSchema.parse(body)

    // Find user
    const user = await db.user.findUnique({
      where: { email },
    })

    if (!user) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Verify password
    const isValid = await bcrypt.compare(password, user.password)

    if (!isValid) {
      return Response.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      )
    }

    // Check if MFA is enabled
    if (user.mfaEnabled) {
      // If no MFA token provided, return requiresMFA
      if (!mfaToken && !backupCode) {
        return Response.json({
          requiresMFA: true,
          userId: user.id,
        })
      }

      // Verify MFA token or backup code
      let mfaValid = false

      if (mfaToken) {
        mfaValid = await verifyMFA(user.id, mfaToken)
      } else if (backupCode) {
        mfaValid = await verifyBackupCode(user.id, backupCode)
      }

      if (!mfaValid) {
        return Response.json(
          { error: 'Invalid MFA code' },
          { status: 401 }
        )
      }
    }

    // Create token
    const token = await createToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    })

    // Set cookie
    await setAuthCookie(token)

    return Response.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return Response.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Login error:', error)
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## OAuth 2.0 Integration

### GitHub OAuth

```typescript
// src/lib/auth/oauth/github.ts
import { db } from '@/lib/db'
import { createToken, setAuthCookie } from '@/lib/auth/jwt'

const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID!
const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET!
const GITHUB_REDIRECT_URI = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/oauth/github/callback`

// ✅ Generate OAuth URL
export function getGitHubAuthUrl(): string {
  const params = new URLSearchParams({
    client_id: GITHUB_CLIENT_ID,
    redirect_uri: GITHUB_REDIRECT_URI,
    scope: 'user:email',
    state: crypto.randomBytes(16).toString('hex'),  // CSRF protection
  })

  return `https://github.com/login/oauth/authorize?${params}`
}

// ✅ Exchange code for access token
async function getGitHubAccessToken(code: string): Promise<string> {
  const response = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: GITHUB_REDIRECT_URI,
    }),
  })

  const data = await response.json()

  if (!data.access_token) {
    throw new Error('Failed to get access token')
  }

  return data.access_token
}

// ✅ Get GitHub user
async function getGitHubUser(accessToken: string): Promise<{
  id: number
  email: string
  name: string
  avatar_url: string
}> {
  const response = await fetch('https://api.github.com/user', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json',
    },
  })

  return response.json()
}

// ✅ Handle OAuth callback
export async function handleGitHubCallback(code: string): Promise<string> {
  // Exchange code for access token
  const accessToken = await getGitHubAccessToken(code)

  // Get user data
  const githubUser = await getGitHubUser(accessToken)

  // Find or create user
  let user = await db.user.findUnique({
    where: { email: githubUser.email },
  })

  if (!user) {
    user = await db.user.create({
      data: {
        email: githubUser.email,
        name: githubUser.name,
        avatar: githubUser.avatar_url,
        emailVerified: true,  // GitHub verifies emails
        password: '',  // No password for OAuth users
      },
    })
  }

  // Store OAuth account
  await db.oauthAccount.upsert({
    where: {
      provider_providerAccountId: {
        provider: 'github',
        providerAccountId: String(githubUser.id),
      },
    },
    create: {
      userId: user.id,
      provider: 'github',
      providerAccountId: String(githubUser.id),
      accessToken,
    },
    update: {
      accessToken,
    },
  })

  // Create JWT token
  const token = await createToken({
    userId: user.id,
    email: user.email,
    role: user.role,
  })

  return token
}
```

### Google OAuth

```typescript
// src/lib/auth/oauth/google.ts
import { google } from 'googleapis'
import { db } from '@/lib/db'
import { createToken } from '@/lib/auth/jwt'

const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/oauth/google/callback`
)

// ✅ Generate OAuth URL
export function getGoogleAuthUrl(): string {
  return oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: [
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile',
    ],
    state: crypto.randomBytes(16).toString('hex'),
  })
}

// ✅ Handle OAuth callback
export async function handleGoogleCallback(code: string): Promise<string> {
  // Exchange code for tokens
  const { tokens } = await oauth2Client.getToken(code)
  oauth2Client.setCredentials(tokens)

  // Get user info
  const oauth2 = google.oauth2({ version: 'v2', auth: oauth2Client })
  const { data: googleUser } = await oauth2.userinfo.get()

  if (!googleUser.email) {
    throw new Error('No email from Google')
  }

  // Find or create user
  let user = await db.user.findUnique({
    where: { email: googleUser.email },
  })

  if (!user) {
    user = await db.user.create({
      data: {
        email: googleUser.email,
        name: googleUser.name || '',
        avatar: googleUser.picture,
        emailVerified: true,
        password: '',
      },
    })
  }

  // Store OAuth account
  await db.oauthAccount.upsert({
    where: {
      provider_providerAccountId: {
        provider: 'google',
        providerAccountId: googleUser.id!,
      },
    },
    create: {
      userId: user.id,
      provider: 'google',
      providerAccountId: googleUser.id!,
      accessToken: tokens.access_token!,
      refreshToken: tokens.refresh_token,
    },
    update: {
      accessToken: tokens.access_token!,
      refreshToken: tokens.refresh_token,
    },
  })

  // Create JWT token
  const token = await createToken({
    userId: user.id,
    email: user.email,
    role: user.role,
  })

  return token
}
```

---

## Passwordless Authentication

### Magic Link

```typescript
// src/lib/auth/magic-link.ts
import { db } from '@/lib/db'
import { sendEmail } from '@/lib/email'
import { createToken } from '@/lib/auth/jwt'
import crypto from 'crypto'

// ✅ Send magic link
export async function sendMagicLink(email: string): Promise<void> {
  // Find or create user
  let user = await db.user.findUnique({ where: { email } })

  if (!user) {
    user = await db.user.create({
      data: {
        email,
        emailVerified: true,
        password: '',  // No password for magic link users
      },
    })
  }

  // Generate token
  const token = crypto.randomBytes(32).toString('hex')
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  // Delete old tokens
  await db.magicLinkToken.deleteMany({
    where: { userId: user.id },
  })

  // Create new token
  await db.magicLinkToken.create({
    data: {
      userId: user.id,
      token: hashedToken,
      expiresAt: new Date(Date.now() + 15 * 60 * 1000),  // 15 minutes
    },
  })

  // Send email
  const loginUrl = `${process.env.NEXT_PUBLIC_APP_URL}/auth/magic-link?token=${token}`

  await sendEmail({
    to: email,
    subject: 'Sign in to Quetrex',
    html: `
      <p>Click the link below to sign in to Quetrex:</p>
      <a href="${loginUrl}">${loginUrl}</a>
      <p>This link expires in 15 minutes.</p>
      <p>If you didn't request this, please ignore this email.</p>
    `,
  })
}

// ✅ Verify magic link token
export async function verifyMagicLink(token: string): Promise<string | null> {
  const hashedToken = crypto.createHash('sha256').update(token).digest('hex')

  const magicToken = await db.magicLinkToken.findUnique({
    where: { token: hashedToken },
    include: { user: true },
  })

  if (!magicToken) {
    return null
  }

  // Check expiration
  if (magicToken.expiresAt < new Date()) {
    await db.magicLinkToken.delete({ where: { id: magicToken.id } })
    return null
  }

  // Create JWT token
  const jwtToken = await createToken({
    userId: magicToken.user.id,
    email: magicToken.user.email,
    role: magicToken.user.role,
  })

  // Delete magic link token (one-time use)
  await db.magicLinkToken.delete({ where: { id: magicToken.id } })

  return jwtToken
}
```

---

## Security Best Practices

### Secure Cookie Configuration

```typescript
// Cookie settings for production
export const SECURE_COOKIE_OPTIONS = {
  httpOnly: true,  // ✅ Not accessible via JavaScript (prevents XSS)
  secure: process.env.NODE_ENV === 'production',  // ✅ HTTPS only in production
  sameSite: 'strict' as const,  // ✅ CSRF protection
  path: '/',
  maxAge: 60 * 60 * 24,  // 24 hours
}

// For third-party cookies (OAuth redirects)
export const LAX_COOKIE_OPTIONS = {
  ...SECURE_COOKIE_OPTIONS,
  sameSite: 'lax' as const,  // Allow cross-site GET requests
}
```

### Rate Limiting Login Attempts

```typescript
// src/lib/auth/rate-limit.ts
import { db } from '@/lib/db'

export async function checkLoginRateLimit(email: string, ip: string): Promise<boolean> {
  const now = new Date()
  const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000)

  // Count failed attempts in last hour
  const failedAttempts = await db.loginAttempt.count({
    where: {
      OR: [
        { email },
        { ip },
      ],
      success: false,
      timestamp: {
        gte: oneHourAgo,
      },
    },
  })

  // Block if more than 5 failed attempts
  return failedAttempts < 5
}

export async function recordLoginAttempt(
  email: string,
  ip: string,
  success: boolean
): Promise<void> {
  await db.loginAttempt.create({
    data: {
      email,
      ip,
      success,
      timestamp: new Date(),
    },
  })

  // Cleanup old attempts (>7 days)
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  await db.loginAttempt.deleteMany({
    where: {
      timestamp: {
        lt: sevenDaysAgo,
      },
    },
  })
}
```

### CSRF Protection

```typescript
// src/lib/auth/csrf.ts
import crypto from 'crypto'
import { cookies } from 'next/headers'

// ✅ Generate CSRF token
export async function generateCSRFToken(): Promise<string> {
  const token = crypto.randomBytes(32).toString('hex')

  const cookieStore = await cookies()
  cookieStore.set('csrf-token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    path: '/',
  })

  return token
}

// ✅ Verify CSRF token
export async function verifyCSRFToken(token: string): Promise<boolean> {
  const cookieStore = await cookies()
  const cookieToken = cookieStore.get('csrf-token')?.value

  return cookieToken === token
}

// ✅ Middleware for CSRF protection
export async function csrfMiddleware(request: Request): Promise<boolean> {
  // Only check for state-changing methods
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
    const token = request.headers.get('x-csrf-token')

    if (!token) {
      return false
    }

    return verifyCSRFToken(token)
  }

  return true
}
```

---

## Complete Registration Example

```typescript
// src/app/api/auth/register/route.ts
import { z } from 'zod'
import { db } from '@/lib/db'
import { hashPassword, passwordSchema } from '@/lib/auth/password'
import { sendVerificationEmail } from '@/lib/auth/email-verification'
import { checkLoginRateLimit, recordLoginAttempt } from '@/lib/auth/rate-limit'

const registerSchema = z.object({
  email: z.string().email(),
  password: passwordSchema,
  name: z.string().min(1).max(100),
})

export async function POST(request: Request) {
  try {
    const ip = request.headers.get('x-forwarded-for') || 'unknown'

    const body = await request.json()
    const { email, password, name } = registerSchema.parse(body)

    // Check rate limit
    const allowed = await checkLoginRateLimit(email, ip)

    if (!allowed) {
      return Response.json(
        { error: 'Too many attempts. Please try again later.' },
        { status: 429 }
      )
    }

    // Check if user exists
    const existing = await db.user.findUnique({ where: { email } })

    if (existing) {
      await recordLoginAttempt(email, ip, false)
      return Response.json(
        { error: 'Email already registered' },
        { status: 400 }
      )
    }

    // Hash password
    const hashedPassword = await hashPassword(password)

    // Create user
    const user = await db.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        emailVerified: false,
        role: 'USER',
      },
    })

    // Send verification email
    await sendVerificationEmail(user.id)

    await recordLoginAttempt(email, ip, true)

    return Response.json({
      success: true,
      message: 'Registration successful. Please check your email to verify your account.',
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    }, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return Response.json(
        { error: 'Invalid input', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Registration error:', error)
    return Response.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
```

---

## Summary

**Authentication checklist:**

- [ ] Passwords hashed with bcrypt (12+ rounds) or Argon2
- [ ] Strong password policy enforced
- [ ] Email verification required
- [ ] Password reset flow implemented
- [ ] Rate limiting on login/registration
- [ ] MFA support for sensitive accounts
- [ ] OAuth providers configured (GitHub, Google)
- [ ] CSRF protection enabled
- [ ] Secure cookie settings (httpOnly, secure, sameSite)
- [ ] Session/token expiration enforced
- [ ] Failed login attempts logged
- [ ] Account lockout after multiple failures
- [ ] Magic link as alternative auth method
