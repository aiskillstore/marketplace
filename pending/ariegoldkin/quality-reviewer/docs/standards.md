# DevPrep AI Quality Standards - Detailed Reference

**Purpose**: Deep-dive explanations for fixing complex violations.

---

## Violation Details

### File Too Large (>180 lines)

**Strategy: The 4-File Split Pattern**

When a component exceeds 180 lines, split using these boundaries:

**1. Component.tsx** - UI only
```typescript
export function Form() {
  const { formData, handleChange, handleSubmit } = useFormLogic();

  return (
    <form onSubmit={handleSubmit}>
      <Input name="email" value={formData.email} onChange={handleChange} />
      <Button type="submit">Submit</Button>
    </form>
  );
}
```

**2. hooks.ts** - Logic
```typescript
export function useFormLogic() {
  const [formData, setFormData] = useState(INITIAL_STATE);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // validation, API calls, error handling
  };

  return { formData, handleChange, handleSubmit };
}
```

**3. types.ts** - Type definitions
```typescript
export interface IFormData {
  email: string;
  name: string;
}

export interface IFormErrors {
  email?: string;
  name?: string;
}
```

**4. utils.ts** (optional) - Pure helper functions
```typescript
export const validateEmail = (email: string): boolean => {
  return EMAIL_REGEX.test(email);
};

export const formatDate = (date: Date): string => {
  return date.toISOString().split('T')[0];
};
```

**See working example:** `examples/refactor-after/`

---

### Complexity Too High (>15)

**Root Causes:**
1. Nested conditionals (if inside if inside if)
2. Long switch statements
3. Multiple responsibilities in one function
4. No early returns

**Fix 1: Extract Conditional Logic**
```typescript
// Before: Complexity 18
function processUser(user) {
  if (user.role === 'admin') {
    if (user.isActive) {
      if (user.permissions.includes('write')) {
        if (user.lastLogin > cutoffDate) {
          // do something
        }
      }
    }
  }
}

// After: Complexity 3
function processUser(user) {
  if (!isEligibleAdmin(user)) return;
  processAdminUser(user);
}

function isEligibleAdmin(user) {
  return user.role === 'admin'
    && user.isActive
    && user.permissions.includes('write')
    && user.lastLogin > cutoffDate;
}
```

**Fix 2: Replace Switch with Lookup Object**
```typescript
// Before: Switch adds complexity
function getStatusColor(status) {
  switch (status) {
    case 'pending': return 'yellow';
    case 'approved': return 'green';
    case 'rejected': return 'red';
    case 'draft': return 'gray';
    default: return 'blue';
  }
}

// After: Zero complexity
const STATUS_COLORS = {
  pending: 'yellow',
  approved: 'green',
  rejected: 'red',
  draft: 'gray',
} as const;

function getStatusColor(status) {
  return STATUS_COLORS[status] ?? 'blue';
}
```

**Fix 3: Use Early Returns**
```typescript
// Before: Nested conditions
function validate(data) {
  if (data) {
    if (data.email) {
      if (isValidEmail(data.email)) {
        if (data.name.length > 2) {
          return true;
        }
      }
    }
  }
  return false;
}

// After: Early returns
function validate(data) {
  if (!data) return false;
  if (!data.email) return false;
  if (!isValidEmail(data.email)) return false;
  if (data.name.length <= 2) return false;
  return true;
}
```

---

## Path Aliases Deep Dive

### Why Aliases Matter

**Problem with relative imports:**
```typescript
// Deep nesting becomes brittle
import { Button } from '../../../shared/ui/button';
import { useAuth } from '../../../../lib/auth/hooks';

// Move the file? All imports break
// Refactor structure? Mass find-replace needed
```

**Solution with aliases:**
```typescript
// Location-independent
import { Button } from '@shared/ui/button';
import { useAuth } from '@lib/auth/hooks';

// Move the file? Imports still work
// Refactor structure? Aliases update in tsconfig.json
```

### Configured Aliases

Located in `frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "paths": {
      "@shared/*": ["./src/shared/*"],
      "@modules/*": ["./src/modules/*"],
      "@lib/*": ["./src/lib/*"],
      "@store": ["./src/store"],
      "@store/*": ["./src/store/*"],
      "@styles/*": ["./src/styles/*"]
    }
  }
}
```

### When to Use What

| Import | Use When | Example |
|--------|----------|---------|
| `@shared/ui/*` | UI components | `@shared/ui/button` |
| `@shared/components/*` | Layouts | `@shared/components/AppLayout` |
| `@shared/hooks/*` | Reusable hooks | `@shared/hooks/useLocalStorage` |
| `@modules/{feature}/*` | Feature code | `@modules/practice/hooks/usePractice` |
| `@lib/trpc/*` | tRPC client | `@lib/trpc/client` |
| `@store/*` | Zustand store | `@store/hooks` |
| `./utils` | Same directory | `./helpers` |

**Rule:** Use alias if going up 2+ directories (`../../`)

---

## Architecture Patterns

### The 6-Folder Philosophy

**Principle:** Every file has ONE clear home

**Decision Tree:**
```
Is it a route/page?
  └─ YES → app/

Is it feature-specific business logic?
  └─ YES → modules/{feature}/

Is it reusable across features?
  ├─ UI component? → shared/ui/
  ├─ Hook? → shared/hooks/
  ├─ Utility? → shared/utils/
  └─ Layout? → shared/components/

Is it an external integration?
  └─ YES → lib/{service}/

Is it global state?
  └─ YES → store/slices/{domain}/

Is it styling?
  └─ YES → styles/
```

### Anti-Patterns

**❌ Don't:** Create new top-level folders
```
src/
├── helpers/        # ❌ Use shared/utils/
├── contexts/       # ❌ Use store/ or modules/
├── services/       # ❌ Use lib/
```

**❌ Don't:** Put everything in shared
```
shared/
├── PracticeWizard.tsx   # ❌ Feature-specific → modules/practice/
├── QuestionCard.tsx     # ❌ Feature-specific → modules/questions/
```

**✅ Do:** Follow domain boundaries
```
modules/practice/
├── components/
│   └── PracticeWizard.tsx    # Practice feature UI
├── hooks/
│   └── usePractice.ts        # Practice feature logic
└── types.ts                   # Practice feature types
```

---

## Type Safety Patterns

### Avoiding 'any'

**Pattern 1: Unknown + Type Guards**
```typescript
// ❌ Bad: any defeats type safety
function parse(data: any) {
  return data.user.name;  // No type checking
}

// ✅ Good: unknown + type guard
function parse(data: unknown) {
  if (!isUserData(data)) {
    throw new Error('Invalid data');
  }
  return data.user.name;  // Type-safe
}

function isUserData(data: unknown): data is { user: { name: string } } {
  return typeof data === 'object'
    && data !== null
    && 'user' in data
    && typeof (data as any).user.name === 'string';
}
```

**Pattern 2: Zod Schemas**
```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  name: z.string(),
  email: z.string().email(),
  age: z.number().min(0),
});

// Infer type from schema
type User = z.infer<typeof UserSchema>;

// Parse with runtime validation
function getUser(data: unknown): User {
  return UserSchema.parse(data);  // Throws if invalid
}
```

**Pattern 3: Generic Constraints**
```typescript
// ❌ Bad: any in generic
function getProperty<T>(obj: T, key: any): any {
  return obj[key];
}

// ✅ Good: constrained generic
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Usage is type-safe
const user = { name: 'Alice', age: 30 };
const name = getProperty(user, 'name');    // string
const age = getProperty(user, 'age');      // number
const bad = getProperty(user, 'invalid'); // Error: Type error
```

---

## Naming Conventions Rationale

### Why 'I' Prefix for Interfaces?

**Benefits:** Instant recognition (`IUser` vs `User`), prevents naming conflicts, improves IDE autocomplete, easier code review.

**DevPrep AI Standard:** ALL interfaces use 'I' prefix including React props (`IButtonProps`, not `ButtonProps`).

**Example:**
```typescript
interface IUser { name: string; email: string; }      // ✅ Interface
class User implements IUser { /* ... */ }              // ✅ Implementation
type UserId = string;                                  // ✅ Type (no I prefix)
```

---

**Last Updated:** October 2025
**Full Standards:** `Docs/code-standards.md`
**Code Examples:** `examples/good-code.tsx`, `examples/bad-code.tsx`, `examples/refactor-after/`
