# Quality Checklist

DevPrep AI enforces strict quality standards for all code. This checklist ensures consistency, maintainability, and performance.

---

## File Size Limits

### ≤180 Lines Per File (Code Only)

**Why:** Long files are hard to maintain and test.

**How to Check:**
```bash
wc -l <file>
```

**Validation:**
```bash
./scripts/validate-module.sh <module-name>
```

**If Exceeded:**
1. Split component into smaller sub-components
2. Extract hooks into separate files
3. Move utilities to `utils/` directory
4. Extract types to `types.ts`

**Example Split:**
```typescript
// Before: LongComponent.tsx (250 lines) ❌

// After: Split into 3 files ✅
// LongComponent.tsx (80 lines)
// SubComponentA.tsx (70 lines)
// SubComponentB.tsx (65 lines)
```

---

## Function Limits

### ≤15 Complexity Per Function

**Why:** High complexity = hard to test, understand, and maintain.

**How to Check:**
ESLint automatically checks complexity (configured in `.eslintrc.json`).

**Validation:**
```bash
npm run lint
```

**If Exceeded:**
1. Extract conditional logic into helper functions
2. Use early returns to reduce nesting
3. Split into smaller functions

**Example:**
```typescript
// ❌ Before: High complexity (20)
function processData(data: IData[]) {
  if (data.length > 0) {
    if (data[0].isValid) {
      for (const item of data) {
        if (item.status === "active") {
          if (item.score > 70) {
            // Nested logic...
          }
        }
      }
    }
  }
}

// ✅ After: Reduced complexity (5)
function processData(data: IData[]) {
  if (data.length === 0) return;
  if (!data[0].isValid) return;

  const activeItems = data.filter(isActive);
  const highScoreItems = activeItems.filter(hasHighScore);

  return processItems(highScoreItems);
}
```

### ≤50 Lines Per Function

**Why:** Long functions are hard to understand and test.

**If Exceeded:** Split into smaller, focused functions.

### ≤4 Parameters Per Function

**Why:** Too many parameters make functions hard to use and test.

**If Exceeded:**
1. Group related parameters into an object
2. Use options object pattern

**Example:**
```typescript
// ❌ Before: Too many parameters
function createQuestion(
  title: string,
  type: string,
  difficulty: number,
  tags: string[],
  duration: number,
  points: number
) { }

// ✅ After: Options object
interface ICreateQuestionOptions {
  title: string;
  type: string;
  difficulty: number;
  tags: string[];
  duration: number;
  points: number;
}

function createQuestion(options: ICreateQuestionOptions) { }
```

---

## TypeScript Standards

### Strict Mode Enabled

**Required:**
- `"strict": true` in `tsconfig.json`
- No compiler errors
- No type warnings

**Validation:**
```bash
npm run type-check
```

### No `any` Types

**Rule:** Never use `any` type.

**Alternatives:**
```typescript
// ❌ Bad
function process(data: any) { }

// ✅ Good
function process(data: unknown) { }
function process<T>(data: T) { }
function process(data: ISpecificType) { }
```

**Exception:** Only acceptable in:
- Third-party library type patches
- Type guards with proper narrowing

### Interfaces Use `I` Prefix

```typescript
// ✅ Correct
interface IUserProfile { }
interface IButtonProps { }

// ❌ Incorrect
interface UserProfile { }  // Missing I prefix
interface ButtonProps { }  // Missing I prefix
```

**Validation:**
The `validate-module.sh` script checks for this automatically.

### Type Imports

```typescript
// ✅ Correct
import type { IQuestion } from "@/types/ai";

// ❌ Incorrect
import { IQuestion } from "@/types/ai";
```

---

## Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Interface | I + PascalCase | `IUserProfile` |
| Component | PascalCase | `AnalyticsChart` |
| Function | camelCase | `formatDate` |
| Hook | use + camelCase | `useAnalytics` |
| Variable | camelCase | `userName` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_QUESTIONS` |
| Module | kebab-case | `user-profile` |
| File | Match contents | `AnalyticsChart.tsx` |

See `naming-conventions.md` for complete reference.

---

## Import Patterns

### Use Path Aliases

```typescript
// ✅ Correct
import { Button } from "@shared/ui/button";
import type { IQuestion } from "@/types/ai";
import { trpc } from "@lib/trpc/client";

// ❌ Incorrect
import { Button } from "../../../shared/ui/button";
import type { IQuestion } from "../../../../types/ai";
```

### Import Order

1. React and external libraries
2. Global types (`@/types/*`)
3. Shared imports (`@shared/*`)
4. Lib imports (`@lib/*`)
5. Store imports (`@store/*`)
6. Module-internal imports (relative)

---

## Architecture Compliance

### Module Structure

Required structure:
```
modules/<module-name>/
├── components/        # Required
│   ├── Component.tsx
│   └── index.ts       # Required
├── hooks/            # Optional
│   └── index.ts
├── utils/            # Optional
│   └── index.ts
└── types.ts          # Optional
```

### No Cross-Module Imports

```typescript
// ❌ Bad
import { QuestionCard } from "@modules/questions/components";

// ✅ Good
import { Card } from "@shared/ui/card";  // Use shared instead
```

### Barrel Exports

Each directory with exports needs `index.ts`:

```typescript
// components/index.ts
export * from "./AnalyticsChart";
export * from "./AnalyticsSummary";
```

---

## Code Quality

### No Duplicate Code

**Rule:** DRY (Don't Repeat Yourself)

**If you copy-paste code:**
1. Extract to utility function
2. Move to `@shared/utils/` if used across modules
3. Keep in module's `utils/` if module-specific

### Proper Error Handling

```typescript
// ✅ Good
try {
  const data = await fetchData();
  return data;
} catch (error) {
  console.error("Error fetching data:", error);
  throw error;  // Re-throw or handle appropriately
}

// ❌ Bad
try {
  const data = await fetchData();
  return data;
} catch (error) {
  // Silent failure - no logging or handling
}
```

### Comments for Complex Logic

```typescript
// ✅ Good: Comment explains WHY, not WHAT
// Calculate score using weighted average to prioritize recent attempts
const score = calculateWeightedScore(attempts);

// ❌ Bad: Comment states the obvious
// This calculates the score
const score = calculateWeightedScore(attempts);
```

---

## Testing (Future)

When tests are added:
- Each component has test file: `ComponentName.test.tsx`
- Test coverage > 80%
- All hooks tested
- Edge cases covered

---

## Validation Commands

### Run All Checks

```bash
# TypeScript check
npm run type-check

# ESLint
npm run lint

# File size check
npm run test

# Module validation
./scripts/validate-module.sh <module-name>
```

### Before Commit

The pre-commit hook automatically runs:
- TypeScript type checking
- ESLint
- File size validation

**Fix issues before committing.**

---

## Quality-Reviewer Skill Integration

After creating a module, use the `quality-reviewer` skill:

```bash
# Run full quality review
./.claude/skills/quality-reviewer/scripts/full-review.sh

# Check specific aspects
./.claude/skills/quality-reviewer/scripts/check-file-size.sh
./.claude/skills/quality-reviewer/scripts/check-complexity.sh
./.claude/skills/quality-reviewer/scripts/check-naming.sh
./.claude/skills/quality-reviewer/scripts/check-imports.sh
```

---

## Summary Checklist

Before considering a module complete:

- [ ] All files ≤180 lines
- [ ] All functions ≤15 complexity
- [ ] All functions ≤50 lines
- [ ] All functions ≤4 parameters
- [ ] No `any` types
- [ ] All interfaces have `I` prefix
- [ ] Using path aliases (`@shared`, `@lib`, etc.)
- [ ] Proper directory structure (components/, hooks/, utils/)
- [ ] Barrel exports (index.ts files)
- [ ] No cross-module imports
- [ ] TypeScript strict mode passes
- [ ] ESLint passes with no warnings
- [ ] Proper error handling
- [ ] Comments for complex logic
- [ ] Follows naming conventions

**Validation:**
```bash
npm run type-check && npm run lint && ./scripts/validate-module.sh <module-name>
```

---

## Common Violations

### 1. File Too Long
**Error:** `File exceeds 180 lines`
**Fix:** Split into smaller files

### 2. Interface Without I Prefix
**Error:** `interface UserProfile` detected
**Fix:** Rename to `IUserProfile`

### 3. Using `any` Type
**Error:** TypeScript warning
**Fix:** Use `unknown`, `T` generic, or specific type

### 4. Too Many Relative Imports
**Warning:** `Found 10 relative imports`
**Fix:** Use path aliases (`@shared`, `@lib`, etc.)

### 5. High Complexity
**Error:** `Function complexity is 20 (max 15)`
**Fix:** Extract nested logic into helper functions

---

## Resources

- See `quality-reviewer` skill for automated checks
- See `naming-conventions.md` for naming rules
- See `6-folder-architecture.md` for structure rules
- See `path-aliases.md` for import patterns
