# TypeScript + Vitest Template

Template for generating Vitest test scaffolds from TypeScript source files.

## Variables

| Variable | Description |
|----------|-------------|
| `{module_name}` | Source module name (e.g., `login`) |
| `{import_path}` | Relative import path (e.g., `../auth/login`) |
| `{symbols}` | Comma-separated list of imported symbols |
| `{class_name}` | Name of class being tested |
| `{function_name}` | Name of function being tested |

## File Template

```typescript
/**
 * Tests for {module_name}.
 *
 * Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
 * Fill in test implementations and remove TODO comments.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

import { {symbols} } from '{import_path}';

{class_tests}

{function_tests}
```

## Class Test Template

```typescript
describe('{class_name}', () => {
  let instance: {class_name};

  beforeEach(() => {
    // TODO: Configure instance with appropriate test data
    instance = new {class_name}();
  });

{method_tests}
});
```

## Method Test Template

```typescript
  describe('{method_name}', () => {
    it('should handle the happy path', () => {
      // TODO: Implement this test
      // - Call instance.{method_name}()
      // - Assert expected behavior
      expect.fail('Test not yet implemented');
    });

    it.todo('should handle edge cases');

    it.todo('should handle error conditions');
  });
```

## Function Test Template

```typescript
describe('{function_name}', () => {
  it('should handle the happy path', () => {
    // TODO: Implement this test
    // - Call {function_name}()
    // - Assert expected behavior
    expect.fail('Test not yet implemented');
  });

  it.todo('should handle edge cases');

  it.todo('should handle error conditions');
});
```

## Async Function Template

```typescript
describe('{function_name}', () => {
  it('should handle the happy path', async () => {
    // TODO: Implement this test
    // - Call await {function_name}()
    // - Assert expected behavior
    expect.fail('Test not yet implemented');
  });

  it.todo('should handle edge cases');

  it.todo('should reject on error conditions');
});
```

## Mock Template

```typescript
// Mock dependencies
vi.mock('{dependency_path}', () => ({
  {dependency_name}: vi.fn(),
}));

// In test:
const mock{Dependency} = vi.mocked({dependency_name});
mock{Dependency}.mockResolvedValue(/* TODO: mock return value */);
```

## Example Output

Given source file `src/auth/login.ts`:
```typescript
export class UserSession {
  constructor(public userId: string) {}

  async refresh(): Promise<boolean> { ... }

  invalidate(): void { ... }
}

export async function authenticate(
  username: string,
  password: string
): Promise<UserSession> { ... }

export function logout(session: UserSession): boolean { ... }
```

Generated scaffold `src/auth/login.test.ts`:
```typescript
/**
 * Tests for login.
 *
 * Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
 * Fill in test implementations and remove TODO comments.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

import { UserSession, authenticate, logout } from './login';

describe('UserSession', () => {
  let instance: UserSession;

  beforeEach(() => {
    // TODO: Configure instance with appropriate test data
    instance = new UserSession('test-user-id');
  });

  describe('refresh', () => {
    it('should handle the happy path', async () => {
      // TODO: Implement this test
      // - Call await instance.refresh()
      // - Assert expected behavior
      expect.fail('Test not yet implemented');
    });

    it.todo('should handle edge cases');

    it.todo('should reject on error conditions');
  });

  describe('invalidate', () => {
    it('should handle the happy path', () => {
      // TODO: Implement this test
      // - Call instance.invalidate()
      // - Assert expected behavior
      expect.fail('Test not yet implemented');
    });

    it.todo('should handle edge cases');

    it.todo('should handle error conditions');
  });
});

describe('authenticate', () => {
  it('should handle the happy path', async () => {
    // TODO: Implement this test
    // - Call await authenticate()
    // - Assert expected behavior
    expect.fail('Test not yet implemented');
  });

  it.todo('should handle edge cases');

  it.todo('should reject on error conditions');
});

describe('logout', () => {
  it('should handle the happy path', () => {
    // TODO: Implement this test
    // - Call logout()
    // - Assert expected behavior
    expect.fail('Test not yet implemented');
  });

  it.todo('should handle edge cases');

  it.todo('should handle error conditions');
});
```

## Naming Rules

| Source | Test File |
|--------|-----------|
| `src/auth/login.ts` | `src/auth/login.test.ts` |
| `src/utils.ts` | `src/utils.test.ts` |
| `lib/core.ts` | `lib/core.test.ts` |

## Import Resolution

1. Use relative imports from test file location
2. For `src/auth/login.ts` → `./login` in `login.test.ts`
3. Detect TypeScript path aliases from `tsconfig.json`
