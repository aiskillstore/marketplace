---
name: code-quality
description: Expert at TypeScript strict mode, linting, formatting, code review standards. Use when checking code quality, fixing type errors, or enforcing standards.
allowed-tools: Read, Bash, Grep, Glob
---

# Code Quality Specialist

You are an expert at maintaining high code quality in TypeScript/React projects.

## When To Use

Claude should automatically use this skill when:
- User asks to check or improve code quality
- Fixing TypeScript errors or warnings
- Reviewing code for best practices
- Enforcing consistent patterns

## TypeScript Standards

### Strict Mode Requirements
- `strict: true` in tsconfig.json
- No `any` types (use `unknown` instead)
- Explicit return types on exported functions
- Null checks with optional chaining

### Type Safety Patterns
```typescript
// Good - explicit types
function processData(data: UserData): ProcessedResult {
  return { ... };
}

// Bad - implicit any
function processData(data) {
  return { ... };
}

// Good - null handling
const value = obj?.property ?? defaultValue;

// Bad - unchecked access
const value = obj.property;
```

## Code Patterns

### Component Structure
```typescript
// Props interface above component
interface ComponentNameProps {
  /** Description of prop */
  propName: string;
  /** Optional prop with default */
  optional?: boolean;
}

// Explicit function component
export function ComponentName({ propName, optional = false }: ComponentNameProps) {
  // Hooks first
  const [state, setState] = useState<StateType>(initial);

  // Derived values
  const derived = useMemo(() => compute(state), [state]);

  // Callbacks
  const handleClick = useCallback(() => {
    // ...
  }, [dependencies]);

  // Render
  return <div>...</div>;
}
```

### Hook Structure
```typescript
interface UseHookNameOptions {
  /** Required option */
  required: string;
  /** Optional with default */
  optional?: number;
}

interface UseHookNameReturn {
  /** Current state */
  value: string;
  /** Update function */
  setValue: (value: string) => void;
}

export function useHookName(options: UseHookNameOptions): UseHookNameReturn {
  const { required, optional = 10 } = options;
  // ...
}
```

## Quality Checks

### Type Check
```bash
pnpm tsc --noEmit
```

### Common Issues

| Issue | Fix |
|-------|-----|
| `Type 'X' is not assignable to type 'Y'` | Check type compatibility, add type guard |
| `Object is possibly 'undefined'` | Add null check or optional chaining |
| `Parameter 'x' implicitly has an 'any' type` | Add explicit type annotation |
| `Property 'x' does not exist on type 'Y'` | Add property to interface or use type assertion |

## Anti-Patterns to Avoid

### Don't Do
```typescript
// Type assertions to escape type system
const value = data as any;

// Ignoring errors
// @ts-ignore
const broken = thing.property;

// Unused variables
const unused = 'never used';

// Console logs in production
console.log('debug');
```

### Do Instead
```typescript
// Type guards for runtime checks
function isValidData(data: unknown): data is ValidData {
  return typeof data === 'object' && data !== null && 'id' in data;
}

// Explicit error handling
if (!data) {
  throw new Error('Data is required');
}

// Remove unused code
// Delete it entirely

// Use proper logging
if (process.env.NODE_ENV === 'development') {
  console.log('debug');
}
```

## Project-Specific Rules

### Platform Abstraction
- All platform code goes through `getPlatformAdapter()`
- Never import platform-specific modules directly
- Use `isNative()`, `isTauri()`, `isCapacitor()` for checks

### Component Rules
- Every component needs a Storybook story
- Props must have TSDoc comments
- Use `useCallback` for event handlers passed to children
- Use `useMemo` for expensive computations

### Hook Rules
- Hooks must return typed objects
- Include TSDoc with @example
- Handle loading, error, and success states
- Clean up subscriptions in useEffect return

## Review Checklist

When reviewing code:
- [ ] No TypeScript errors (`pnpm tsc --noEmit`)
- [ ] No `any` types
- [ ] All exports have TSDoc
- [ ] Consistent naming (PascalCase components, camelCase functions)
- [ ] Error handling present
- [ ] No console.logs
- [ ] Tests written or updated
- [ ] Storybook stories for components
