---
name: quetrex-architect
description: Use when implementing new features in Quetrex. Ensures TDD, TypeScript strict mode, Next.js App Router patterns, ShadCN UI components, and security best practices are followed. Updated for November 2025 standards.
allowed-tools: Read, Grep, Glob
---

# Quetrex Architecture Enforcer

## When to Use
- Creating new features
- Refactoring existing code
- Reviewing PRs
- Ensuring pattern compliance

## Process
1. Read CLAUDE.md for project context
2. Read .quetrex/memory/patterns.md for architectural patterns (if exists)
3. Check if feature uses correct patterns:
   - TypeScript strict (no any, no @ts-ignore)
   - Zod validation for API routes
   - Server Components vs Client Components
   - SSE pattern for streaming
4. If violations found, explain correct pattern
5. Guide implementation following TDD

## Patterns to Enforce

### TypeScript Strict Mode
```typescript
// ✅ DO: Explicit types
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// ❌ DON'T: Using 'any'
function processData(data: any) { }

// ✅ DO: Use type guards
function isCartItem(obj: unknown): obj is CartItem {
  return typeof obj === 'object' && obj !== null && 'price' in obj
}
```

### Next.js App Router Patterns
```typescript
// ✅ DO: Server Component (default)
export default async function DashboardPage() {
  const projects = await prisma.project.findMany()
  return <ProjectList projects={projects} />
}

// ✅ DO: Client Component (when needed)
'use client'
export function InteractiveButton() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}

// ❌ DON'T: Async Client Component
'use client'
export default async function BadComponent() { } // ERROR
```

### Zod Validation
```typescript
// ✅ DO: Validate all API input
import { z } from 'zod'

const createProjectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
})

export async function POST(request: Request) {
  const body = await request.json()
  const validated = createProjectSchema.parse(body) // Throws if invalid
  // ... use validated data
}

// ❌ DON'T: Unvalidated input
export async function POST(request: Request) {
  const { name, description } = await request.json() // No validation
}
```

### ShadCN UI Patterns (November 2025 Standard)
```typescript
// ✅ DO: Use ShadCN UI components
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Form, FormField, FormItem, FormLabel, FormControl } from "@/components/ui/form"

// ✅ DO: Use DialogTrigger with asChild
<DialogTrigger asChild>
  <Button>Open</Button>
</DialogTrigger>

// ❌ DON'T: Create custom buttons without ShadCN
<button className="px-4 py-2 bg-blue-500">Bad</button>

// ✅ DO: Use Form component with React Hook Form + Zod
const form = useForm<z.infer<typeof schema>>({
  resolver: zodResolver(schema),
})

<Form {...form}>
  <FormField ... />
</Form>

// ❌ DON'T: Use uncontrolled forms
<form>
  <input name="email" /> {/* No validation */}
</form>
```

**→ See:** shadcn-ui-patterns skill for complete component library

### Security Patterns
```typescript
// ❌ DON'T: Hardcoded secrets
const apiKey = 'sk_live_abc123'

// ✅ DO: Environment variables
const apiKey = process.env.OPENAI_API_KEY
if (!apiKey) throw new Error('OPENAI_API_KEY not configured')

// ❌ DON'T: SQL injection
const query = `SELECT * FROM users WHERE email = '${email}'`

// ✅ DO: Parameterized queries (Drizzle)
const user = await db.query.users.findFirst({ where: eq(users.email, email) })
```

## TDD Requirements
1. Write tests FIRST
2. Verify tests FAIL
3. Write implementation
4. Verify tests PASS
5. Refactor as needed

## Coverage Thresholds
- Overall: 75%+
- Business Logic (src/services/): 90%+
- Utilities (src/utils/): 90%+
- UI Components: 60%+

## Common Mistakes to Catch
- Using 'any' type (suggest explicit types or unknown)
- Using @ts-ignore (suggest fixing underlying issue)
- Async Client Components (suggest Server Component or remove async)
- Missing Zod validation on API routes
- Hardcoded secrets (suggest environment variables)
- console.log in production code (suggest proper logger)

## Output Format
When violations found:
1. List each violation with file and line number
2. Explain why it's a violation
3. Show correct pattern
4. Provide code example to fix it
