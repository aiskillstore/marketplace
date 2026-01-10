# Naming Conventions

DevPrep AI follows strict naming conventions for consistency and quality.

---

## TypeScript Interfaces

### Rule: Interfaces MUST use `I` prefix

```typescript
// ✅ Correct
interface IUserProfile {
  name: string;
  email: string;
}

interface IButtonProps {
  onClick: () => void;
  label: string;
}

// ❌ Incorrect
interface UserProfile {  // Missing I prefix
  name: string;
}

interface ButtonProps {  // Missing I prefix
  onClick: () => void;
}
```

### Why?
- Clear distinction between types and interfaces
- Follows DevPrep AI code standards
- Enforced by ESLint and quality-reviewer skill

---

## Type Aliases

### Rule: Types use `T` prefix (optional but recommended)

```typescript
// ✅ Correct
type TQuestionType = "coding" | "system-design" | "behavioral";
type TDifficulty = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

// ✅ Also acceptable (no prefix for simple types)
type QuestionType = "coding" | "system-design" | "behavioral";
```

---

## Components

### Rule: PascalCase for component names

```typescript
// ✅ Correct
export function AnalyticsChart() { }
export function UserProfileCard() { }
export function QuestionList() { }

// ❌ Incorrect
export function analyticsChart() { }  // camelCase
export function analytics_chart() { } // snake_case
export function ANALYTICS_CHART() { } // SCREAMING_SNAKE_CASE
```

### File Names
Component files match component names:
- `AnalyticsChart.tsx` (PascalCase)
- `UserProfileCard.tsx`
- `QuestionList.tsx`

---

## Functions

### Rule: camelCase for function names

```typescript
// ✅ Correct
function formatDate(date: Date): string { }
function calculateScore(answers: IAnswer[]): number { }
export function getUserProfile(id: string): IUserProfile { }

// ❌ Incorrect
function FormatDate(date: Date): string { }  // PascalCase
function format_date(date: Date): string { } // snake_case
```

---

## Hooks

### Rule: `use` prefix + camelCase

```typescript
// ✅ Correct
export function useAnalytics() { }
export function useUserProfile() { }
export function useQuestionGenerator() { }

// ❌ Incorrect
export function analytics() { }      // Missing 'use' prefix
export function UseAnalytics() { }   // PascalCase (should be camelCase after 'use')
```

### File Names
Hook files match hook names:
- `useAnalytics.ts` (use + camelCase)
- `useUserProfile.ts`
- `useQuestionGenerator.ts`

---

## Variables

### Rule: camelCase for variables

```typescript
// ✅ Correct
const userName = "John";
const questionCount = 5;
const isLoading = false;

// ❌ Incorrect
const UserName = "John";      // PascalCase
const question_count = 5;     // snake_case
const QUESTION_COUNT = 5;     // SCREAMING (use for constants)
```

### Constants
Use SCREAMING_SNAKE_CASE for true constants:

```typescript
// ✅ Correct
const MAX_QUESTIONS = 50;
const DEFAULT_DIFFICULTY = 5;
const API_BASE_URL = "https://api.example.com";

// For thresholds in components (not exported)
const DIFFICULTY_THRESHOLD_MEDIUM = 3;
const DIFFICULTY_THRESHOLD_HARD = 6;
```

---

## Modules

### Rule: lowercase with hyphens (kebab-case)

```bash
# ✅ Correct
modules/analytics/
modules/user-profile/
modules/question-generator/

# ❌ Incorrect
modules/Analytics/          # PascalCase
modules/user_profile/       # snake_case
modules/userProfile/        # camelCase
```

---

## Files

### Component Files
```
ComponentName.tsx  (PascalCase, matches component)
```

### Hook Files
```
useHookName.ts  (use + camelCase)
```

### Utility Files
```
helpers.ts     (camelCase)
formatters.ts  (camelCase)
validators.ts  (camelCase)
```

### Type Files
```
types.ts       (lowercase)
```

### Index Files
```
index.ts       (lowercase, barrel exports)
```

---

## Props Interfaces

### Rule: Component name + `Props` suffix + `I` prefix

```typescript
// ✅ Correct
interface IAnalyticsChartProps {
  data: IChartData[];
  title: string;
}

export function AnalyticsChart({ data, title }: IAnalyticsChartProps) { }

// ❌ Incorrect
interface AnalyticsChartProps { }  // Missing I prefix
interface IProps { }                // Too generic
interface IChartProps { }          // Doesn't match component name
```

---

## Return Type Interfaces (Hooks)

### Rule: Hook name + `Return` suffix + `I` prefix

```typescript
// ✅ Correct
interface IUseAnalyticsReturn {
  data: IAnalyticsData[];
  isLoading: boolean;
  error: Error | null;
}

export function useAnalytics(): IUseAnalyticsReturn {
  // ...
  return { data, isLoading, error };
}

// ❌ Incorrect
interface UseAnalyticsReturn { }  // Missing I prefix
interface IReturn { }              // Too generic
```

---

## Boolean Variables

### Rule: Use `is`, `has`, `should`, `can` prefix

```typescript
// ✅ Correct
const isLoading = true;
const hasError = false;
const shouldValidate = true;
const canSubmit = false;

// ❌ Incorrect
const loading = true;      // Not a question
const error = false;       // Not a question
const validate = true;     // Verb, not boolean
```

---

## Event Handlers

### Rule: `handle` prefix + PascalCase event

```typescript
// ✅ Correct
function handleClick() { }
function handleSubmit() { }
function handleInputChange(value: string) { }

// ❌ Incorrect
function onClick() { }          // Missing 'handle'
function submitHandler() { }    // Wrong order
function click_handler() { }    // snake_case
```

### Props
```typescript
interface IButtonProps {
  onClick: () => void;     // Prop: 'on' prefix
  onSubmit: () => void;
}

export function Button({ onClick }: IButtonProps) {
  const handleClick = () => {  // Handler: 'handle' prefix
    onClick();
  };

  return <button onClick={handleClick}>Click</button>;
}
```

---

## Enums

### Rule: PascalCase for enum names, SCREAMING_SNAKE_CASE for values

```typescript
// ✅ Correct
enum QuestionType {
  CODING = "coding",
  SYSTEM_DESIGN = "system-design",
  BEHAVIORAL = "behavioral",
}

// ❌ Incorrect
enum questionType { }       // camelCase
enum QUESTION_TYPE { }      // SCREAMING_SNAKE_CASE
```

---

## Summary Table

| Type | Convention | Example |
|------|-----------|---------|
| Interface | I + PascalCase | `IUserProfile` |
| Type Alias | T + PascalCase (optional) | `TQuestionType` |
| Component | PascalCase | `AnalyticsChart` |
| Function | camelCase | `formatDate` |
| Hook | use + camelCase | `useAnalytics` |
| Variable | camelCase | `userName` |
| Constant | SCREAMING_SNAKE_CASE | `MAX_QUESTIONS` |
| Module | kebab-case | `user-profile` |
| Component File | PascalCase.tsx | `AnalyticsChart.tsx` |
| Hook File | useCamelCase.ts | `useAnalytics.ts` |
| Props Interface | IComponent + Props | `IAnalyticsChartProps` |
| Return Interface | IHook + Return | `IUseAnalyticsReturn` |
| Boolean | is/has/should/can + camelCase | `isLoading` |
| Event Handler | handle + PascalCase | `handleClick` |
| Event Prop | on + PascalCase | `onClick` |

---

## Validation

The `validate-module.sh` script checks for:
- ✅ Interfaces with `I` prefix
- ✅ PascalCase components
- ✅ camelCase functions/variables
- ✅ Proper file naming

Run validation:
```bash
./scripts/validate-module.sh <module-name>
```
