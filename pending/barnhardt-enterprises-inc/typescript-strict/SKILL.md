---
name: typescript-strict
description: Strict TypeScript rules. Use when writing ANY TypeScript.
---

# Strict TypeScript Standards

## Rules

### 1. NO `any`
```typescript
// NEVER
function process(data: any) {}

// CORRECT
function process(data: unknown) {
  if (isValidData(data)) { /* use data */ }
}
```

### 2. Explicit Returns
```typescript
// NEVER
function getUser(id: string) { return db.find(id); }

// CORRECT
function getUser(id: string): Promise<User | null> { return db.find(id); }
```

### 3. Typed Errors
```typescript
// NEVER
catch (e) { console.log(e.message); }

// CORRECT
catch (error: unknown) {
  if (error instanceof AppError) { logger.error(error.message); }
  else if (error instanceof Error) { logger.error(error.message); }
  else { logger.error('Unknown error', { error }); }
}
```

### 4. No Unexplained Assertions
```typescript
// NEVER
const user = users.find(u => u.id === id)!;

// CORRECT
const user = users.find(u => u.id === id);
if (!user) throw new NotFoundError(`User ${id} not found`);
```

### 5. Prefer Type Inference Where Obvious
```typescript
// Unnecessary - type is inferred
const count: number = 5;

// Good - type is inferred
const count = 5;

// Good - explicit for function signatures
function add(a: number, b: number): number {
  return a + b;
}
```

### 6. Use Discriminated Unions
```typescript
// CORRECT
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

function handle(result: Result<User>) {
  if (result.success) {
    // TypeScript knows result.data exists
    console.log(result.data.name);
  } else {
    // TypeScript knows result.error exists
    console.log(result.error);
  }
}
```

## Quick Reference

| Pattern | Status |
|---------|--------|
| `any` | NEVER |
| Implicit return | NEVER |
| `!` without comment | NEVER |
| `// @ts-ignore` | NEVER |
| `as` casting | MINIMIZE |
| `unknown` + guards | PREFERRED |
