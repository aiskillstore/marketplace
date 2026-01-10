# Node.js Import Mapping Cookbook

Map JavaScript/TypeScript imports to correct npm package names.

## Built-in Module Exclusions

These are Node.js built-in modules and should NOT be installed:

```
fs, path, os, crypto, http, https, net, tls, dns, dgram, cluster,
child_process, worker_threads, stream, buffer, url, querystring,
util, events, assert, console, process, timers, v8, vm, zlib,
readline, repl, tty, string_decoder, module, perf_hooks, async_hooks,
trace_events, inspector, wasi
```

Note: With `node:` prefix (e.g., `node:fs`), these are always built-ins.

## Import-to-Package Mappings

Most npm packages use their package name directly as the import. Exceptions:

| Import Pattern | Package Name | Notes |
|----------------|--------------|-------|
| `@types/*` | `@types/*` | TypeScript definitions (dev) |
| `lodash/*` | `lodash` | Lodash submodules |
| `lodash-es/*` | `lodash-es` | Lodash ES modules |
| `rxjs/*` | `rxjs` | RxJS submodules |
| `date-fns/*` | `date-fns` | Date-fns submodules |
| `@tanstack/*` | `@tanstack/*` | Direct match (scoped) |
| `@radix-ui/*` | `@radix-ui/*` | Direct match (scoped) |
| `@headlessui/*` | `@headlessui/*` | Direct match (scoped) |

## Framework-Specific Mappings

### React Ecosystem

| Import | Package | Type |
|--------|---------|------|
| `react` | `react` | prod |
| `react-dom` | `react-dom` | prod |
| `react-dom/client` | `react-dom` | prod |
| `next` | `next` | prod |
| `next/*` | `next` | prod |
| `gatsby` | `gatsby` | prod |
| `@remix-run/*` | `@remix-run/*` | prod |

### Vue Ecosystem

| Import | Package | Type |
|--------|---------|------|
| `vue` | `vue` | prod |
| `vue-router` | `vue-router` | prod |
| `pinia` | `pinia` | prod |
| `nuxt` | `nuxt` | prod |

### Testing

| Import | Package | Type |
|--------|---------|------|
| `vitest` | `vitest` | dev |
| `jest` | `jest` | dev |
| `@jest/*` | `@jest/*` | dev |
| `@testing-library/*` | `@testing-library/*` | dev |
| `playwright` | `playwright` | dev |
| `@playwright/*` | `@playwright/*` | dev |
| `cypress` | `cypress` | dev |
| `msw` | `msw` | dev |
| `supertest` | `supertest` | dev |
| `nock` | `nock` | dev |

### Database & ORM

| Import | Package | Type |
|--------|---------|------|
| `prisma` | `prisma` | dev (CLI) |
| `@prisma/client` | `@prisma/client` | prod |
| `drizzle-orm` | `drizzle-orm` | prod |
| `drizzle-kit` | `drizzle-kit` | dev |
| `typeorm` | `typeorm` | prod |
| `sequelize` | `sequelize` | prod |
| `mongoose` | `mongoose` | prod |
| `pg` | `pg` | prod |
| `mysql2` | `mysql2` | prod |
| `better-sqlite3` | `better-sqlite3` | prod |
| `ioredis` | `ioredis` | prod |

### Utilities

| Import | Package | Type |
|--------|---------|------|
| `zod` | `zod` | prod |
| `yup` | `yup` | prod |
| `joi` | `joi` | prod |
| `axios` | `axios` | prod |
| `ky` | `ky` | prod |
| `got` | `got` | prod |
| `dayjs` | `dayjs` | prod |
| `moment` | `moment` | prod |
| `uuid` | `uuid` | prod |
| `nanoid` | `nanoid` | prod |
| `lodash` | `lodash` | prod |
| `ramda` | `ramda` | prod |

### Build & Development

| Import | Package | Type |
|--------|---------|------|
| `typescript` | `typescript` | dev |
| `@types/node` | `@types/node` | dev |
| `tsx` | `tsx` | dev |
| `ts-node` | `ts-node` | dev |
| `esbuild` | `esbuild` | dev |
| `vite` | `vite` | dev |
| `webpack` | `webpack` | dev |
| `rollup` | `rollup` | dev |

### Linting & Formatting

| Import | Package | Type |
|--------|---------|------|
| `eslint` | `eslint` | dev |
| `prettier` | `prettier` | dev |
| `@eslint/*` | `@eslint/*` | dev |
| `eslint-*` | `eslint-*` | dev |

## Detection Algorithm

```typescript
function mapImportToPackage(importPath: string): string | null {
  // Skip node built-ins
  if (importPath.startsWith('node:')) {
    return null;
  }
  if (NODE_BUILTINS.has(importPath)) {
    return null;
  }

  // Handle scoped packages (@org/package)
  if (importPath.startsWith('@')) {
    // @org/package/subpath -> @org/package
    const parts = importPath.split('/');
    return parts.length >= 2 ? `${parts[0]}/${parts[1]}` : importPath;
  }

  // Handle regular packages
  // package/subpath -> package
  const packageName = importPath.split('/')[0];

  // Check known mappings
  if (MAPPINGS.has(packageName)) {
    return MAPPINGS.get(packageName);
  }

  return packageName;
}
```

## Package Manager Commands

### npm

```bash
# Add production dependency
npm install <package>

# Add development dependency
npm install --save-dev <package>

# Add multiple packages
npm install package1 package2 package3
```

### yarn

```bash
# Add production dependency
yarn add <package>

# Add development dependency
yarn add --dev <package>
```

### pnpm

```bash
# Add production dependency
pnpm add <package>

# Add development dependency
pnpm add -D <package>
```

### bun

```bash
# Add production dependency
bun add <package>

# Add development dependency
bun add -d <package>
```

## Dev Dependency Detection

A package should be added as devDependency if:

1. It matches test framework patterns (`vitest`, `jest`, `@testing-library/*`)
2. It's a type definition (`@types/*`)
3. It's a linter/formatter (`eslint`, `prettier`)
4. It's a build tool (`vite`, `webpack`, `esbuild`)
5. It's only imported in test files (`*.test.ts`, `*.spec.ts`, `__tests__/*`)

```typescript
function isDevDependency(packageName: string, importedIn: string[]): boolean {
  // Pattern-based detection
  const devPatterns = [
    /^@types\//,
    /^vitest/,
    /^jest/,
    /^@testing-library\//,
    /^eslint/,
    /^prettier/,
    /^typescript$/,
    /^@playwright\//,
    /^cypress$/,
  ];

  if (devPatterns.some(p => p.test(packageName))) {
    return true;
  }

  // File-based detection
  const testFilePatterns = [
    /\.test\.[jt]sx?$/,
    /\.spec\.[jt]sx?$/,
    /__tests__\//,
    /tests?\//,
  ];

  const onlyInTestFiles = importedIn.every(file =>
    testFilePatterns.some(p => p.test(file))
  );

  return onlyInTestFiles;
}
```
