# Scaffolding Best Practices

Comprehensive best practices for IDE-grade project scaffolding, aligned with WebStorm/PyCharm standards.

## Project Organization

### Directory Structure Principles

1. **Feature-Based Organization** (Recommended for large apps)
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── index.ts
│   └── dashboard/
├── shared/
│   ├── components/
│   ├── hooks/
│   └── utils/
└── app/                    # Entry points, routing
```

2. **Layer-Based Organization** (Traditional, good for small-medium apps)
```
src/
├── components/
├── hooks/
├── services/
├── utils/
└── types/
```

3. **Domain-Driven Design** (Enterprise apps)
```
src/
├── domain/                 # Business logic, entities
├── application/            # Use cases, services
├── infrastructure/         # External services, DB
└── presentation/           # UI, API controllers
```

### Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Hooks | camelCase, `use` prefix | `useAuth.ts` |
| Utilities | camelCase | `formatDate.ts` |
| Constants | SCREAMING_SNAKE | `API_URL` |
| Types/Interfaces | PascalCase | `User`, `ApiResponse` |
| CSS Modules | kebab-case | `user-profile.module.css` |
| Python modules | snake_case | `user_service.py` |

---

## Configuration Management

### Environment Variables

**Structure:**
```
.env.example      # Template (committed)
.env.local        # Local overrides (not committed)
.env.development  # Dev defaults (optional)
.env.production   # Prod defaults (optional)
```

**Best Practices:**
1. Never commit `.env` files with secrets
2. Always provide `.env.example` with all variables
3. Validate env vars at startup
4. Use typed configuration objects

**TypeScript Env Validation (Zod):**
```typescript
// src/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
  PORT: z.coerce.number().default(3000),
});

export const env = envSchema.parse(process.env);
```

**Python Env Validation (Pydantic):**
```python
# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## Code Quality Setup

### ESLint Configuration (2024)

**Flat Config (eslint.config.js) - Recommended:**
```javascript
import js from '@eslint/js';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        project: './tsconfig.json',
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
];
```

### Prettier Configuration

**.prettierrc:**
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "plugins": ["prettier-plugin-tailwindcss"]
}
```

### Python Linting with Ruff

**ruff.toml:**
```toml
line-length = 100
target-version = "py311"

[lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
]
ignore = ["E501"]  # Line too long (handled by formatter)

[lint.isort]
known-first-party = ["app"]
combine-as-imports = true

[format]
quote-style = "double"
indent-style = "space"
```

### Pre-commit Hooks

**JavaScript/TypeScript (.husky/pre-commit):**
```bash
#!/bin/sh
npx lint-staged
```

**lint-staged.config.js:**
```javascript
export default {
  '*.{js,jsx,ts,tsx}': ['eslint --fix', 'prettier --write'],
  '*.{json,md,yml}': ['prettier --write'],
};
```

**Python (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## TypeScript Best Practices

### Strict Mode Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Path Aliases

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"]
    }
  }
}
```

**vite.config.ts:**
```typescript
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### Type Organization

```typescript
// types/api.ts - API response types
export interface ApiResponse<T> {
  data: T;
  error?: string;
  meta?: {
    page: number;
    total: number;
  };
}

// types/user.ts - Domain types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

// types/index.ts - Re-export all
export * from './api';
export * from './user';
```

---

## Security Best Practices

### Environment Security

**Always include in .gitignore:**
```
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
service-account.json
```

**Never commit:**
- API keys
- Database credentials
- JWT secrets
- Private keys
- Service account files

### Input Validation

**Frontend (Zod):**
```typescript
import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  name: z.string().min(1).max(100),
});

export type UserInput = z.infer<typeof userSchema>;
```

**Backend (Python/Pydantic):**
```python
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=1, max_length=100)
```

### API Security Headers

**Express.js (Helmet):**
```typescript
import helmet from 'helmet';

app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
  },
}));
```

**Next.js (next.config.js):**
```javascript
const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
];

module.exports = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
};
```

---

## Testing Setup

### Test Directory Structure

```
tests/
├── unit/                   # Isolated unit tests
│   ├── components/
│   ├── hooks/
│   └── utils/
├── integration/            # Integration tests
│   ├── api/
│   └── db/
├── e2e/                    # End-to-end tests
│   └── flows/
├── fixtures/               # Test data
├── mocks/                  # Mock implementations
└── setup.ts                # Global setup
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
      ],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
]
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["app"]
omit = ["*/tests/*", "*/__init__.py"]
```

---

## CI/CD Configuration

### GitHub Actions (Node.js)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test -- --coverage
      - uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
```

### GitHub Actions (Python)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy .

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest --cov --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      - uses: codecov/codecov-action@v3
```

---

## Docker Configuration

### Node.js Multi-Stage Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS base
WORKDIR /app

# Dependencies
FROM base AS deps
COPY package*.json ./
RUN npm ci --only=production

# Build
FROM base AS builder
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production
FROM base AS runner
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 appuser

COPY --from=deps --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=builder --chown=appuser:nodejs /app/package.json ./

USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Python Multi-Stage Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim AS runner

WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    command: npm run dev

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## Documentation Standards

### README.md Template

```markdown
# Project Name

Brief description of the project.

## Features

- Feature 1
- Feature 2

## Tech Stack

- Frontend: React, TypeScript, Tailwind CSS
- Backend: Node.js, Express, Prisma
- Database: PostgreSQL

## Prerequisites

- Node.js 20+
- PostgreSQL 15+
- Docker (optional)

## Getting Started

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/user/project.git
cd project

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local

# Set up database
npm run db:push

# Start development server
npm run dev
\`\`\`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| API_KEY | External API key | Yes |
| DEBUG | Enable debug mode | No |

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run test` | Run tests |
| `npm run lint` | Run linter |

## Project Structure

\`\`\`
src/
├── components/     # React components
├── lib/           # Utilities and helpers
├── app/           # Next.js app directory
└── types/         # TypeScript types
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT
```

---

## Common Pitfalls to Avoid

### 1. Over-Engineering
- Don't add abstractions before you need them
- Start simple, refactor when patterns emerge
- YAGNI: You Aren't Gonna Need It

### 2. Configuration Sprawl
- Centralize configuration in one place
- Use typed configuration objects
- Document all configuration options

### 3. Dependency Hell
- Keep dependencies minimal
- Audit dependencies regularly
- Pin versions for reproducibility

### 4. Missing Error Handling
- Handle all error cases explicitly
- Provide meaningful error messages
- Log errors with context

### 5. Security Afterthoughts
- Build security in from the start
- Validate all inputs
- Never trust client data

### 6. No Tests
- Write tests from the beginning
- Maintain test coverage thresholds
- Test critical paths thoroughly

### 7. Poor Documentation
- Document as you build
- Keep docs up to date
- Include examples

### 8. Ignoring Performance
- Profile before optimizing
- Monitor in production
- Set performance budgets
