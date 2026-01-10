# Validation Rules

Comprehensive quality criteria for code validation.

## TypeScript Validation

### Rule: No `any` Type

**Violation:**
```typescript
function processData(data: any) {
  return data.value
}
```

**Fix:**
```typescript
interface Data {
  value: string
}

function processData(data: Data): string {
  return data.value
}

// OR use unknown with type guard
function processData(data: unknown): string {
  if (isValidData(data)) {
    return data.value
  }
  throw new Error('Invalid data')
}
```

**Detection:**
```bash
grep -r ": any" src/
grep -r "<any>" src/
grep -r "as any" src/
```

---

### Rule: No `@ts-ignore`

**Violation:**
```typescript
// @ts-ignore
const value = getData().property
```

**Fix:**
```typescript
const data = getData()
if ('property' in data) {
  const value = data.property
}

// OR use type guard
function hasProperty(obj: unknown): obj is { property: string } {
  return typeof obj === 'object' && obj !== null && 'property' in obj
}

const data = getData()
if (hasProperty(data)) {
  const value = data.property
}
```

**Detection:**
```bash
grep -r "@ts-ignore" src/
grep -r "@ts-expect-error" src/
```

---

### Rule: No Non-Null Assertions Without Comment

**Violation:**
```typescript
const user = users.find(u => u.id === id)!
const name = user.name
```

**Fix:**
```typescript
const user = users.find(u => u.id === id)
if (!user) {
  throw new Error(`User ${id} not found`)
}
const name = user.name

// OR if you KNOW it exists, document why
const user = users.find(u => u.id === id)!
// SAFE: user is guaranteed to exist because we just created it above
```

**Detection:**
```bash
grep -r "!" src/ | grep -v "!=" | grep -v "!==" | grep -v "// SAFE:"
```

---

### Rule: Explicit Function Types

**Violation:**
```typescript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0)
}

async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}
```

**Fix:**
```typescript
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}
```

**Detection:**
```bash
npx tsc --noEmit
# Look for: Parameter 'x' implicitly has an 'any' type
```

---

## Security Validation

### Rule: No Hardcoded Secrets

**Violation:**
```typescript
const apiKey = 'sk_live_abc123'
const dbPassword = 'mypassword123'
const jwtSecret = 'secret123'
```

**Fix:**
```typescript
const apiKey = process.env.STRIPE_API_KEY
if (!apiKey) {
  throw new Error('STRIPE_API_KEY environment variable not set')
}

const dbPassword = process.env.DATABASE_PASSWORD
if (!dbPassword) {
  throw new Error('DATABASE_PASSWORD environment variable not set')
}

const jwtSecret = process.env.JWT_SECRET
if (!jwtSecret) {
  throw new Error('JWT_SECRET environment variable not set')
}
```

**Detection:**
```bash
grep -ri "api_key\s*=\s*['\"]" src/
grep -ri "apikey\s*=\s*['\"]" src/
grep -ri "secret\s*=\s*['\"]" src/
grep -ri "password\s*=\s*['\"]" src/
grep -ri "token\s*=\s*['\"]" src/
```

---

### Rule: Input Validation with Zod

**Violation:**
```typescript
export async function POST(request: Request) {
  const body = await request.json()
  const user = await createUser(body) // Unsafe!
  return Response.json(user)
}
```

**Fix:**
```typescript
import { z } from 'zod'

const createUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128),
  name: z.string().min(1).max(100).optional(),
})

export async function POST(request: Request) {
  const body = await request.json()
  const validated = createUserSchema.parse(body)
  const user = await createUser(validated)
  return Response.json(user)
}
```

**Detection:**
```bash
# Find API routes without Zod validation
grep -r "export async function POST" src/app/api/ | while read line; do
  file=$(echo "$line" | cut -d: -f1)
  if ! grep -q "z.object\|z.string\|z.number" "$file"; then
    echo "Missing Zod validation: $file"
  fi
done
```

---

### Rule: Authorization Checks

**Violation:**
```typescript
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  await prisma.project.delete({ where: { id: params.id } })
  return new Response(null, { status: 204 })
}
```

**Fix:**
```typescript
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  const user = await getAuthUser(request)
  if (!user) {
    return new Response('Unauthorized', { status: 401 })
  }

  const project = await prisma.project.findUnique({
    where: { id: params.id },
  })

  if (!project) {
    return new Response('Not found', { status: 404 })
  }

  if (project.userId !== user.id) {
    return new Response('Forbidden', { status: 403 })
  }

  await prisma.project.delete({ where: { id: params.id } })
  return new Response(null, { status: 204 })
}
```

**Detection:**
Manual review of API routes for:
- DELETE operations without ownership check
- UPDATE operations without ownership check
- READ operations on private data without ownership check

---

### Rule: SQL Injection Prevention

**Violation:**
```typescript
const query = `SELECT * FROM users WHERE email = '${email}'`
const users = await db.query(query)
```

**Fix:**
```typescript
// Use Prisma (parameterized queries)
const user = await prisma.user.findUnique({
  where: { email },
})

// If raw SQL needed (rare), use parameterized queries
const users = await prisma.$queryRaw`
  SELECT * FROM users WHERE email = ${email}
`
```

**Detection:**
```bash
# Check for string concatenation in queries
grep -r "\`SELECT.*\${" src/
grep -r "\`INSERT.*\${" src/
grep -r "\`UPDATE.*\${" src/
grep -r "\`DELETE.*\${" src/
```

---

## Code Quality Validation

### Rule: No Debug Code

**Violation:**
```typescript
console.log('User data:', user)
console.debug('API response:', response)
debugger
```

**Fix:**
```typescript
// Use proper logger
logger.info('User logged in', { userId: user.id })

// OR remove entirely for temporary debug logs
```

**Detection:**
```bash
grep -r "console.log\|console.debug\|console.warn" src/
grep -r "debugger" src/
```

---

### Rule: No Commented-Out Code

**Violation:**
```typescript
function processData(data: Data): Result {
  // const oldWay = data.map(x => x.value)
  // return oldWay.filter(x => x > 0)
  return data.filter(x => x.value > 0).map(x => x.value)
}
```

**Fix:**
```typescript
function processData(data: Data): Result {
  return data.filter(x => x.value > 0).map(x => x.value)
}
```

**Detection:**
Manual review of commented code in Pull Requests.

---

### Rule: No TODO Without Issue

**Violation:**
```typescript
function getData(): Data {
  // TODO: Add caching
  return fetchFromAPI()
}
```

**Fix:**
```typescript
function getData(): Data {
  // TODO(#123): Add caching to improve performance
  return fetchFromAPI()
}
```

**Detection:**
```bash
grep -r "TODO\|FIXME\|HACK" src/ | grep -v "#[0-9]"
```

---

## Testing Validation

### Rule: AAA Pattern

**Violation:**
```typescript
it('should process data', () => {
  const result = processData({ value: 5 })
  expect(result).toBe(10)
  const other = processData({ value: 0 })
  expect(other).toBe(0)
})
```

**Fix:**
```typescript
it('should double positive values', () => {
  // ARRANGE: Setup test data
  const input = { value: 5 }

  // ACT: Execute behavior
  const result = processData(input)

  // ASSERT: Verify outcome
  expect(result).toBe(10)
})

it('should return zero for zero input', () => {
  // ARRANGE
  const input = { value: 0 }

  // ACT
  const result = processData(input)

  // ASSERT
  expect(result).toBe(0)
})
```

**Detection:**
Manual review - each test should have clear AAA sections.

---

### Rule: UI Tests Verify DOM State

**Violation:**
```typescript
it('should toggle visibility', () => {
  const { getByTestId } = render(<Component />)
  const button = getByTestId('toggle-button')

  fireEvent.click(button)
  expect(mockToggle).toHaveBeenCalled()
})
```

**Fix:**
```typescript
it('should toggle visibility', () => {
  const { getByTestId } = render(<Component />)
  const button = getByTestId('toggle-button')
  const content = getByTestId('content')

  // Initial state
  expect(content).toBeVisible()
  expect(content).toHaveClass('opacity-100')

  // After click
  fireEvent.click(button)
  expect(content).not.toBeVisible()
  expect(content).toHaveClass('opacity-0')

  // After second click
  fireEvent.click(button)
  expect(content).toBeVisible()
  expect(content).toHaveClass('opacity-100')
})
```

**Detection:**
Manual review of UI component tests for:
- `.toHaveClass()`
- `.toHaveStyle()`
- `.toBeVisible()`
- `.toHaveAttribute()`

---

### Rule: Coverage Thresholds

**Requirements:**
- Overall: ≥ 75%
- Business logic (src/services/): ≥ 90%
- Utilities (src/utils/): ≥ 90%
- API routes (src/app/api/): ≥ 75%
- UI components: ≥ 60%

**Detection:**
```bash
npm test -- --coverage --run
```

**Coverage Report:**
```
Statements   : 75% ( 150/200 )
Branches     : 75% ( 30/40 )
Functions    : 75% ( 15/20 )
Lines        : 75% ( 145/193 )
```

---

## Next.js Pattern Validation

### Rule: Server vs Client Components

**Violation:**
```typescript
// ❌ Async Client Component (SYNTAX ERROR)
'use client'

export default async function BadComponent() {
  const data = await fetch('/api/data')
  return <div>{data}</div>
}
```

**Fix:**
```typescript
// ✅ Async Server Component
export default async function GoodComponent() {
  const data = await fetch('/api/data')
  return <DataDisplay data={data} />
}

// ✅ OR Client Component with useEffect
'use client'

export default function GoodComponent() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData)
  }, [])

  return <DataDisplay data={data} />
}
```

**Detection:**
```bash
# Find files with both 'use client' and async function
grep -l "'use client'" src/**/*.tsx | while read file; do
  if grep -q "export default async function" "$file"; then
    echo "Invalid async client component: $file"
  fi
done
```

---

## Error Handling Validation

### Rule: All Async Operations Have Try/Catch

**Violation:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}
```

**Fix:**
```typescript
async function fetchUser(id: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    logger.error('fetchUser failed', { id, error })
    throw new Error(`Failed to fetch user ${id}`)
  }
}
```

**Detection:**
Manual review of async functions for try/catch blocks.

---

## Validation Checklist

Use this checklist before finishing any work:

### TypeScript
- [ ] No `any` types
- [ ] No `@ts-ignore` comments
- [ ] No unexplained non-null assertions
- [ ] All functions have explicit types
- [ ] TypeScript compiles: `npx tsc --noEmit`

### Security
- [ ] No hardcoded secrets
- [ ] All inputs validated with Zod
- [ ] Authorization checked on protected routes
- [ ] SQL injection prevented (using Prisma)
- [ ] No XSS vulnerabilities

### Code Quality
- [ ] No console.log statements
- [ ] No commented-out code
- [ ] No TODO without GitHub issue
- [ ] Functions have single responsibility
- [ ] Variable names are descriptive

### Testing
- [ ] All tests follow AAA pattern
- [ ] Coverage meets thresholds (75%/90%)
- [ ] UI tests verify DOM state
- [ ] E2E tests for visual changes
- [ ] All tests passing

### Build
- [ ] TypeScript compiles
- [ ] Tests pass
- [ ] Linting passes
- [ ] Build succeeds
- [ ] No runtime errors in dev

---

## Automated Validation

Run all validations:
```bash
.claude/skills/quality-gates/validate.py
```

This script:
1. Calls typescript-strict-guard/validate-types.py
2. Calls security-sentinel/validate-security.py
3. Calls nextjs-15-specialist/validate-patterns.py
4. Calls drizzle-orm-patterns/validate-queries.py
5. Aggregates results
6. Exits 0 if all pass, 1 if any fail
