# Dependency Classification Cookbook

Determine whether a dependency should be added as production or development.

## Classification Rules

### 1. Production Dependencies

Add to `dependencies` (npm) or main dependencies (uv/poetry) if:

- Used at runtime by the application
- Required for the application to function
- Imported in source code (not just tests)
- Part of the public API

Examples:
- Web frameworks: `fastapi`, `express`, `react`
- Database clients: `asyncpg`, `pg`, `prisma`
- Utilities used at runtime: `lodash`, `zod`, `pydantic`
- API clients: `boto3`, `openai`, `anthropic`

### 2. Development Dependencies

Add to `devDependencies` (npm) or `[tool.uv.dev-dependencies]` / `[project.optional-dependencies.dev]` if:

- Only used during development
- Only used for testing
- Only used for building/bundling
- Only used for linting/formatting
- Type definitions only

Examples:
- Test frameworks: `pytest`, `vitest`, `jest`
- Type checkers: `mypy`, `typescript`
- Linters: `ruff`, `eslint`, `prettier`
- Build tools: `vite`, `esbuild`, `webpack`
- Type definitions: `@types/*`

## Language-Specific Classification

### Python (uv/poetry)

```toml
# pyproject.toml with uv

[project]
dependencies = [
    "fastapi>=0.100.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

### Node.js (npm/yarn/pnpm)

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "next": "^14.0.0",
    "zod": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "vitest": "^1.0.0",
    "typescript": "^5.0.0"
  }
}
```

### Rust (cargo)

```toml
# Cargo.toml

[dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[dev-dependencies]
mockall = "0.12"
rstest = "0.18"
```

### Go (go.mod)

Go doesn't distinguish dev dependencies at the module level.
All dependencies go in `go.mod`. Use build tags for test-only code.

```go
// go.mod
require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.0  // Test framework
)
```

## File-Based Classification

If a package is only imported in test files, classify as dev:

| File Pattern | Classification |
|--------------|----------------|
| `*_test.py` | dev |
| `test_*.py` | dev |
| `tests/*.py` | dev |
| `*.test.ts` | dev |
| `*.spec.ts` | dev |
| `__tests__/*.ts` | dev |
| `conftest.py` | dev |
| `setup.py` | dev |
| `vitest.config.ts` | dev |
| `jest.config.js` | dev |

## Pattern-Based Classification

### Always Dev

| Pattern | Reason |
|---------|--------|
| `@types/*` | TypeScript type definitions |
| `*-types` | Type packages |
| `eslint*` | Linting |
| `prettier*` | Formatting |
| `stylelint*` | Style linting |
| `*-loader` | Webpack loaders |
| `*-plugin` (bundler) | Bundler plugins |

### Always Prod (if imported in src)

| Pattern | Reason |
|---------|--------|
| `react*` | Runtime UI |
| `vue*` | Runtime UI |
| `express*` | Runtime server |
| `fastapi*` | Runtime server |
| `*-sdk` | API clients |
| `*-client` | API clients |

## Decision Flow

```
Is the package imported?
├── Only in test files?
│   └── YES → devDependency
├── In source code?
│   └── Is it a type definition (@types/*)?
│       ├── YES → devDependency
│       └── NO → Is it a linter/formatter?
│           ├── YES → devDependency
│           └── NO → Is it a build tool?
│               ├── YES → devDependency
│               └── NO → dependency (production)
└── Not imported but in config?
    └── devDependency (build/lint config)
```

## Edge Cases

### 1. Test Utilities Used in Source

If a "test" package like `faker` is used in source code (e.g., for seeding data):

```python
# In src/seed.py (not test)
from faker import Faker
```

→ Add as **production** dependency

### 2. Type-Only Imports

TypeScript imports that are type-only:

```typescript
import type { SomeType } from 'some-package';
```

→ Still add as **production** if the package is used at runtime elsewhere
→ Add as **dev** if truly type-only

### 3. CLI Tools

Tools run via CLI but not imported:

```bash
# In scripts
npx prisma generate
```

→ Add as **dev** unless it's a runtime CLI (like `next`)

### 4. Conditional Imports

```python
try:
    import uvloop
except ImportError:
    uvloop = None
```

→ Add as **optional** dependency if supported, otherwise **production**
