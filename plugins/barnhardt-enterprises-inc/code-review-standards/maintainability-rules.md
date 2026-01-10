# Maintainability Rules

## Code Quality Checklist

### Function Complexity

#### Single Responsibility Principle
```typescript
// 🔴 BAD: Function does too much
function processUser(userData) {
  // Validate input
  if (!userData.email) throw new Error('Invalid')

  // Hash password
  const hashed = bcrypt.hash(userData.password)

  // Save to database
  await db.insert(usersTable).values({ ...userData, password: hashed })

  // Send welcome email
  await sendEmail(userData.email, 'Welcome!')

  // Log analytics
  analytics.track('user_created')
}

// ✅ GOOD: Each function has one responsibility
async function validateUser(userData: UserInput): UserData {
  return userSchema.parse(userData)
}

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12)
}

async function createUser(data: UserData): Promise<User> {
  return db.insert(usersTable).values(data).returning()
}

async function sendWelcomeEmail(email: string): Promise<void> {
  await sendEmail(email, 'Welcome!')
}

function trackUserCreation(userId: string): void {
  analytics.track('user_created', { userId })
}
```

#### Function Length
- ✅ **Target**: < 20 lines
- ⚠️ **Warning**: 20-50 lines
- 🔴 **Error**: > 50 lines

---

### Naming Conventions

#### Variables
```typescript
// 🔴 BAD: Unclear names
const d = new Date()
const arr = getData()
const x = calculateThing()

// ✅ GOOD: Descriptive names
const createdAt = new Date()
const activeProjects = getActiveProjects()
const totalRevenue = calculateMonthlyRevenue()
```

#### Functions
```typescript
// 🔴 BAD: Unclear what function does
function process() { }
function handle() { }
function doIt() { }

// ✅ GOOD: Verb + noun, describes action
function validateUserInput() { }
function calculateTotalPrice() { }
function fetchActiveProjects() { }
```

#### Booleans
```typescript
// 🔴 BAD: Unclear boolean meaning
const flag = true
const status = false

// ✅ GOOD: is/has/can prefix
const isAuthenticated = true
const hasPermission = false
const canEdit = true
```

---

### Comments

#### When to Comment
```typescript
// ✅ GOOD: Complex business logic
// Calculate compound interest using formula: A = P(1 + r/n)^(nt)
// where P = principal, r = rate, n = compounds per year, t = years
function calculateCompoundInterest(principal, rate, years) {
  const n = 12 // Monthly compounding
  return principal * Math.pow(1 + rate / n, n * years)
}

// ✅ GOOD: Explaining "why" not "what"
// Using SHA-256 instead of MD5 because MD5 is cryptographically broken
const hash = crypto.createHash('sha256')

// 🔴 BAD: Stating the obvious
// Increment counter by 1
counter++

// 🔴 BAD: Commented-out code
// const oldWay = processData(input)
// return oldWay.filter(x => x > 0)
```

---

### Error Handling

#### Informative Error Messages
```typescript
// 🔴 BAD: Generic error
throw new Error('Error')
throw new Error('Invalid input')

// ✅ GOOD: Specific, actionable error
throw new Error('Email must be a valid email address')
throw new Error(`Project ${projectId} not found`)
throw new Error('Password must be at least 8 characters and contain uppercase, lowercase, number, and special character')
```

#### Error Context
```typescript
// 🔴 BAD: No context
catch (error) {
  throw error
}

// ✅ GOOD: Add context
catch (error) {
  console.error('Failed to create project:', {
    userId,
    projectName,
    error: error.message,
  })
  throw new Error(`Failed to create project: ${error.message}`)
}
```

---

### Code Duplication

#### DRY Principle (Don't Repeat Yourself)
```typescript
// 🔴 BAD: Duplicated validation
function createProject(data) {
  if (!data.name) throw new Error('Name required')
  if (data.name.length > 100) throw new Error('Name too long')
  // ...
}

function updateProject(data) {
  if (!data.name) throw new Error('Name required')
  if (data.name.length > 100) throw new Error('Name too long')
  // ...
}

// ✅ GOOD: Extract common validation
const projectSchema = z.object({
  name: z.string().min(1).max(100),
})

function createProject(data) {
  const validated = projectSchema.parse(data)
  // ...
}

function updateProject(data) {
  const validated = projectSchema.parse(data)
  // ...
}
```

---

### Magic Values

#### Constants for Magic Numbers/Strings
```typescript
// 🔴 BAD: Magic numbers
if (user.age < 18) { }
setTimeout(callback, 86400000)
if (status === 'pending_approval') { }

// ✅ GOOD: Named constants
const MINIMUM_AGE = 18
const ONE_DAY_MS = 24 * 60 * 60 * 1000
const ProjectStatus = {
  PENDING_APPROVAL: 'pending_approval',
  APPROVED: 'approved',
  REJECTED: 'rejected',
} as const

if (user.age < MINIMUM_AGE) { }
setTimeout(callback, ONE_DAY_MS)
if (status === ProjectStatus.PENDING_APPROVAL) { }
```

---

### Dead Code

#### Remove Unused Code
```typescript
// 🔴 BAD: Unused imports, variables, functions
import { unusedFunction } from './utils'

const unusedVariable = 'test'

function neverCalled() {
  return 'unused'
}

// ✅ GOOD: Only keep what's used
import { actuallyUsedFunction } from './utils'

function actuallyUsed() {
  return actuallyUsedFunction()
}
```

---

### File Organization

#### File Length
- ✅ **Target**: < 200 lines
- ⚠️ **Warning**: 200-400 lines
- 🔴 **Error**: > 400 lines

#### Module Cohesion
```typescript
// 🔴 BAD: Everything in one file
// utils.ts (1000 lines)
function dateUtils() { }
function stringUtils() { }
function arrayUtils() { }
function objectUtils() { }

// ✅ GOOD: Separate by concern
// utils/date.ts
export function formatDate() { }
export function parseDate() { }

// utils/string.ts
export function capitalize() { }
export function slugify() { }

// utils/array.ts
export function unique() { }
export function groupBy() { }
```

---

### TODOs and FIXMEs

#### Link to Issues
```typescript
// 🔴 BAD: TODO without context
// TODO: Optimize this

// ✅ GOOD: TODO with issue reference
// TODO(#123): Optimize with caching - see issue for benchmarks
```

---

## Review Template

```markdown
### 🟡 [Code Quality] [Issue Type]

**Location**: `src/path/file.ts:line`

**Issue**: [Description of quality issue]

**Impact**:
- Readability: [How it affects understanding]
- Maintainability: [How it affects future changes]

**Suggestion**:
```typescript
// Improved implementation
```

**Priority**: LOW | MEDIUM | HIGH
```

---

## Maintainability Metrics

### Cyclomatic Complexity
- ✅ **Simple**: 1-5
- ⚠️ **Moderate**: 6-10
- 🔴 **Complex**: > 10

### Function Parameters
- ✅ **Good**: 0-3 parameters
- ⚠️ **Warning**: 4-5 parameters
- 🔴 **Too many**: > 5 parameters (use object)

### Nesting Depth
- ✅ **Good**: 1-2 levels
- ⚠️ **Warning**: 3 levels
- 🔴 **Too deep**: > 3 levels (refactor)

---

## See Also

- [Clean Code](https://www.goodreads.com/book/show/3735293-clean-code)
- [Refactoring](https://refactoring.com/)
- [../typescript-strict-guard/SKILL.md](../typescript-strict-guard/SKILL.md)
