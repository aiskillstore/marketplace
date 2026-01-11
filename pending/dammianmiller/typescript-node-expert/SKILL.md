---
name: typescript-node-expert
description: Expert TypeScript/Node.js developer for building high-quality, performant, and maintainable CLI tools and libraries. Enforces best practices, strict typing, and modern patterns.
---

# TypeScript/Node.js Expert

## Overview

This skill provides expert guidance for TypeScript and Node.js development with a focus on:

- **Type Safety**: Strict TypeScript with full type coverage
- **Performance**: Async patterns, streaming, memory efficiency
- **Maintainability**: Clean architecture, SOLID principles
- **Modern Standards**: ES2022+, ESM modules, latest Node.js features

## PROACTIVE USAGE

**Invoke this skill before ANY TypeScript/Node.js work:**
- New features or modules
- Refactoring existing code
- Performance optimization
- Code review
- Bug fixes in TypeScript files

---

## Critical Rules - Zero Tolerance

### 1. Strict TypeScript Configuration

**Required `tsconfig.json` settings:**

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "moduleResolution": "NodeNext",
    "module": "NodeNext",
    "target": "ES2022",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### 2. No `any` - Ever

```typescript
// ❌ FORBIDDEN
function process(data: any) { ... }
const result: any = await fetch();

// ✅ REQUIRED
function process(data: unknown) { ... }
function process<T extends Record<string, unknown>>(data: T) { ... }

// Use type guards
function isValidResponse(data: unknown): data is ApiResponse {
  return typeof data === 'object' && data !== null && 'status' in data;
}
```

### 3. Explicit Return Types

```typescript
// ❌ FORBIDDEN
async function getData() {
  return await db.query();
}

// ✅ REQUIRED
async function getData(): Promise<User[]> {
  return await db.query();
}
```

### 4. Null Safety

```typescript
// ❌ FORBIDDEN
const name = user.profile.name; // Could be undefined

// ✅ REQUIRED - Optional chaining + nullish coalescing
const name = user?.profile?.name ?? 'Unknown';

// ✅ REQUIRED - Early return pattern
if (!user?.profile?.name) {
  throw new Error('User profile name is required');
}
const name = user.profile.name;
```

---

## Performance Patterns

### 1. Async/Await Best Practices

```typescript
// ❌ SLOW - Sequential
const user = await getUser(id);
const posts = await getPosts(id);
const comments = await getComments(id);

// ✅ FAST - Parallel
const [user, posts, comments] = await Promise.all([
  getUser(id),
  getPosts(id),
  getComments(id),
]);

// ✅ CONTROLLED - Promise.allSettled for fault tolerance
const results = await Promise.allSettled([
  fetchFromService1(),
  fetchFromService2(),
  fetchFromService3(),
]);

const successful = results
  .filter((r): r is PromiseFulfilledResult<Data> => r.status === 'fulfilled')
  .map(r => r.value);
```

### 2. Streaming for Large Data

```typescript
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import { Transform } from 'stream';

// ❌ BAD - Loads entire file into memory
const content = await fs.readFile('large-file.json', 'utf-8');
const data = JSON.parse(content);

// ✅ GOOD - Stream processing
async function processLargeFile(inputPath: string, outputPath: string): Promise<void> {
  const transform = new Transform({
    objectMode: true,
    transform(chunk, encoding, callback) {
      const processed = processChunk(chunk);
      callback(null, processed);
    },
  });

  await pipeline(
    createReadStream(inputPath),
    transform,
    createWriteStream(outputPath)
  );
}
```

### 3. Memory-Efficient Collections

```typescript
// ❌ BAD - Creates intermediate arrays
const result = data
  .filter(x => x.active)
  .map(x => x.id)
  .slice(0, 10);

// ✅ GOOD - Generator for lazy evaluation
function* filterAndMap<T, U>(
  items: Iterable<T>,
  predicate: (item: T) => boolean,
  mapper: (item: T) => U,
  limit = Infinity
): Generator<U> {
  let count = 0;
  for (const item of items) {
    if (count >= limit) return;
    if (predicate(item)) {
      yield mapper(item);
      count++;
    }
  }
}

const result = [...filterAndMap(data, x => x.active, x => x.id, 10)];
```

---

## Error Handling

### 1. Custom Error Classes

```typescript
// Define error hierarchy
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly isOperational: boolean = true
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public readonly field?: string) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`, 'NOT_FOUND', 404);
  }
}
```

### 2. Result Pattern (No Throw for Expected Failures)

```typescript
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E };

async function parseConfig(path: string): Promise<Result<Config, string>> {
  try {
    const content = await fs.readFile(path, 'utf-8');
    const config = JSON.parse(content);
    
    if (!isValidConfig(config)) {
      return { success: false, error: 'Invalid configuration format' };
    }
    
    return { success: true, data: config };
  } catch (e) {
    return { success: false, error: `Failed to read config: ${e}` };
  }
}

// Usage
const result = await parseConfig('.config.json');
if (!result.success) {
  console.error(result.error);
  process.exit(1);
}
console.log(result.data);
```

---

## CLI Development Patterns

### 1. Commander.js Structure

```typescript
import { Command, Option } from 'commander';

const program = new Command()
  .name('my-cli')
  .description('CLI description')
  .version('1.0.0', '-v, --version');

// Subcommand with options
program
  .command('generate')
  .description('Generate output files')
  .argument('<input>', 'Input file path')
  .option('-o, --output <path>', 'Output path', './output')
  .option('-f, --format <type>', 'Output format', 'json')
  .option('--dry-run', 'Preview without writing', false)
  .addOption(
    new Option('-l, --log-level <level>', 'Log level')
      .choices(['debug', 'info', 'warn', 'error'])
      .default('info')
  )
  .action(async (input: string, options: GenerateOptions) => {
    try {
      await runGenerate(input, options);
    } catch (error) {
      console.error(chalk.red(`Error: ${error instanceof Error ? error.message : error}`));
      process.exit(1);
    }
  });

program.parseAsync();
```

### 2. User Feedback

```typescript
import ora from 'ora';
import chalk from 'chalk';

async function runWithSpinner<T>(
  message: string,
  task: () => Promise<T>
): Promise<T> {
  const spinner = ora(message).start();
  try {
    const result = await task();
    spinner.succeed();
    return result;
  } catch (error) {
    spinner.fail();
    throw error;
  }
}

// Progress for multi-step operations
async function processFiles(files: string[]): Promise<void> {
  const total = files.length;
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i]!;
    process.stdout.write(`\r${chalk.cyan('Processing')} [${i + 1}/${total}] ${file}`);
    await processFile(file);
  }
  
  console.log(chalk.green('\n✔ All files processed'));
}
```

---

## Module Organization

### 1. Barrel Exports

```typescript
// types/index.ts - Export all types
export type { Config, Options, Result } from './config.js';
export type { User, UserProfile } from './user.js';

// Use in imports
import type { Config, User } from './types/index.js';
```

### 2. Dependency Injection

```typescript
// Define interfaces
interface Logger {
  info(message: string): void;
  error(message: string, error?: Error): void;
}

interface Database {
  query<T>(sql: string, params?: unknown[]): Promise<T[]>;
}

// Service with injected dependencies
class UserService {
  constructor(
    private readonly db: Database,
    private readonly logger: Logger
  ) {}

  async getUser(id: string): Promise<User | null> {
    this.logger.info(`Fetching user ${id}`);
    const [user] = await this.db.query<User>('SELECT * FROM users WHERE id = ?', [id]);
    return user ?? null;
  }
}
```

---

## Testing Standards

### 1. Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
    include: ['src/**/*.test.ts'],
    typecheck: {
      enabled: true,
      include: ['src/**/*.test.ts'],
    },
  },
});
```

### 2. Test Patterns

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('UserService', () => {
  let service: UserService;
  let mockDb: Database;
  let mockLogger: Logger;

  beforeEach(() => {
    mockDb = {
      query: vi.fn(),
    };
    mockLogger = {
      info: vi.fn(),
      error: vi.fn(),
    };
    service = new UserService(mockDb, mockLogger);
  });

  it('should return user when found', async () => {
    const expectedUser: User = { id: '1', name: 'Test' };
    vi.mocked(mockDb.query).mockResolvedValue([expectedUser]);

    const result = await service.getUser('1');

    expect(result).toEqual(expectedUser);
    expect(mockLogger.info).toHaveBeenCalledWith('Fetching user 1');
  });

  it('should return null when user not found', async () => {
    vi.mocked(mockDb.query).mockResolvedValue([]);

    const result = await service.getUser('999');

    expect(result).toBeNull();
  });
});
```

---

## Code Review Checklist

Before completing ANY TypeScript work:

- [ ] `strict: true` in tsconfig.json
- [ ] No `any` types (use `unknown` + type guards)
- [ ] All functions have explicit return types
- [ ] Errors use custom error classes or Result pattern
- [ ] Async operations use Promise.all where possible
- [ ] Large data uses streaming
- [ ] All exports have JSDoc comments
- [ ] Tests cover happy path, edge cases, and error cases
- [ ] `npm run lint` passes
- [ ] `npm run test` passes
- [ ] No console.log (use proper logger)

---

## Quick Reference

```typescript
// Type assertions (prefer type guards)
const data = value as Data;          // ❌ Avoid
if (isData(value)) { ... }           // ✅ Prefer

// Object destructuring with defaults
const { name = 'default', age } = user;

// Array methods with type narrowing
const numbers = mixed.filter((x): x is number => typeof x === 'number');

// Readonly for immutability
function process(items: readonly Item[]): void { ... }

// Template literal types
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Endpoint = `/${string}`;
type Route = `${HttpMethod} ${Endpoint}`;
```
