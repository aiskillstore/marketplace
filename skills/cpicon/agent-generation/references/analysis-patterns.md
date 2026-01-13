# Codebase Analysis Patterns

Patterns for thoroughly analyzing a codebase to generate effective agents.

## Phase 1: Project Identification

### Detect Project Type

```bash
# Check for package managers and languages
ls -la package.json requirements.txt Cargo.toml go.mod pom.xml build.gradle composer.json Gemfile
```

| File Present | Project Type | Primary Language |
|-------------|--------------|------------------|
| package.json | Node.js/JavaScript | TypeScript/JavaScript |
| requirements.txt / pyproject.toml | Python | Python |
| Cargo.toml | Rust | Rust |
| go.mod | Go | Go |
| pom.xml / build.gradle | Java | Java/Kotlin |
| composer.json | PHP | PHP |
| Gemfile | Ruby | Ruby |

### Extract Project Metadata

From package.json:
```bash
grep -E '"name"|"description"|"version"' package.json
```

From pyproject.toml:
```bash
grep -E 'name|description|version' pyproject.toml
```

## Phase 2: Tech Stack Analysis

### Frontend Frameworks

Check package.json dependencies for:
- `react`, `next`, `gatsby` → React ecosystem
- `vue`, `nuxt` → Vue ecosystem
- `angular` → Angular
- `svelte`, `sveltekit` → Svelte ecosystem
- `solid-js` → SolidJS

### Backend Frameworks

Check for:
- Node: `express`, `fastify`, `nestjs`, `koa`
- Python: `fastapi`, `django`, `flask`, `starlette`
- Go: Check for `gin`, `echo`, `fiber` in go.mod
- Rust: Check for `actix-web`, `axum`, `rocket` in Cargo.toml

### State Management

- React: `redux`, `zustand`, `jotai`, `recoil`, `mobx`
- Vue: `pinia`, `vuex`

### Database/ORM

- `prisma`, `typeorm`, `sequelize`, `mongoose` (Node)
- `sqlalchemy`, `django`, `tortoise-orm` (Python)
- `gorm`, `ent` (Go)

### Testing

- `jest`, `vitest`, `mocha`, `cypress`, `playwright` (JS)
- `pytest`, `unittest` (Python)
- `testing` package (Go)

## Phase 3: Architecture Analysis

### Directory Structure Patterns

**Flat Structure** (simple projects):
```
src/
├── components/
├── utils/
└── index.ts
```

**Feature-Based** (domain-driven):
```
src/
├── features/
│   ├── auth/
│   ├── users/
│   └── orders/
└── shared/
```

**Layer-Based** (clean architecture):
```
src/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

**Monorepo**:
```
packages/
├── frontend/
├── backend/
└── shared/
```

### Detect Architecture Pattern

```bash
# Check for common patterns
ls -d */ 2>/dev/null | head -20

# Check for feature folders
ls -d src/features/*/ 2>/dev/null

# Check for layer folders
ls -d src/domain src/application src/infrastructure 2>/dev/null

# Check for monorepo
ls -d packages/*/ apps/*/ 2>/dev/null
```

## Phase 4: Convention Detection

### Naming Conventions

Analyze file names:
```bash
# Check component naming
ls src/components/*.{tsx,jsx} 2>/dev/null | head -10

# Check for kebab-case vs camelCase vs PascalCase
find src -name "*.ts" -o -name "*.tsx" | head -20
```

### Import Patterns

```bash
# Check for path aliases
grep -r "from '@/" src/ | head -5
grep -r 'from "~/' src/ | head -5

# Check for barrel exports
find src -name "index.ts" | head -10
```

### Code Style

Check for config files:
- `.eslintrc.*` → ESLint rules
- `.prettierrc.*` → Prettier config
- `tsconfig.json` → TypeScript settings
- `.editorconfig` → Editor settings

## Phase 5: Domain Analysis

### Find Data Models

```bash
# TypeScript/JavaScript
find src -name "*.model.ts" -o -name "*.entity.ts" -o -name "*.type.ts"
grep -r "interface.*{" src/types/ src/models/ 2>/dev/null | head -20

# Python
find . -name "models.py" -o -name "*_model.py"
grep -r "class.*Model" --include="*.py" | head -20

# Prisma schema
cat prisma/schema.prisma 2>/dev/null
```

### Find API Routes

```bash
# Next.js App Router
ls -la app/api/**/route.ts 2>/dev/null

# Express
grep -r "router\." --include="*.ts" src/routes/ | head -20

# FastAPI
grep -r "@app\." --include="*.py" | head -20
grep -r "@router\." --include="*.py" | head -20
```

### Find Business Logic

```bash
# Services layer
find src -name "*.service.ts" -o -name "*Service.ts"
find . -name "*_service.py" -o -name "services.py"

# Use cases
find src -name "*.usecase.ts" -o -name "*.use-case.ts"
```

## Phase 6: Determine Team Composition

### Complexity Scoring

| Factor | Points |
|--------|--------|
| Single language | +1 |
| Multiple languages | +2 per additional |
| Single framework | +1 |
| Multiple frameworks | +2 per additional |
| <50 source files | +1 |
| 50-200 source files | +2 |
| >200 source files | +3 |
| Has tests | +1 |
| Has CI/CD | +1 |
| Has Docker | +1 |
| Monorepo | +3 |

### Team Size Mapping

| Complexity Score | Recommended Agents |
|-----------------|-------------------|
| 1-4 | 2-3 (Tech + Architecture) |
| 5-7 | 4-5 (+ Domain) |
| 8-10 | 5-6 (+ Testing or DevOps) |
| 11+ | 6-8 (Full coverage) |

### Agent Selection Matrix

| Project Has | Generate Agent |
|-------------|---------------|
| React/Vue/Angular | Frontend Expert |
| Express/FastAPI/Django | Backend Expert |
| Prisma/SQLAlchemy | Database Expert |
| Jest/Pytest | Testing Specialist |
| Docker/K8s | DevOps Expert |
| Auth implementation | Security Expert |
| Complex business logic | Domain Expert |
| Clear architecture | Architecture Expert |

## Phase 7: Extract Project-Specific Details

### For Each Agent, Gather

1. **Relevant file paths** - Where does this agent's domain live?
2. **Key patterns** - What patterns are used in this domain?
3. **Conventions** - What naming/style conventions apply?
4. **Dependencies** - What libraries are used?
5. **Example implementations** - What are good reference files?

### Information Sources

| Info Needed | Where to Look |
|------------|---------------|
| Project name | package.json, README, directory name |
| Tech versions | package.json, requirements.txt |
| Architecture | Directory structure, README |
| Conventions | Config files, existing code patterns |
| Domain terms | README, model names, route names |
| Business logic | Services, use cases, handlers |

## Output Format

After analysis, compile findings into structured data:

```json
{
  "project": {
    "name": "Project Name",
    "slug": "project-name",
    "type": "fullstack",
    "languages": ["TypeScript"],
    "complexity": 7
  },
  "techStack": {
    "frontend": ["React", "Next.js", "Tailwind"],
    "backend": ["Node.js", "tRPC"],
    "database": ["PostgreSQL", "Prisma"],
    "testing": ["Jest", "Playwright"]
  },
  "architecture": {
    "pattern": "feature-based",
    "keyDirectories": ["src/features", "src/shared"],
    "conventions": {
      "fileNaming": "kebab-case",
      "componentNaming": "PascalCase"
    }
  },
  "domain": {
    "entities": ["User", "Order", "Product"],
    "keyFlows": ["authentication", "checkout"]
  },
  "recommendedAgents": [
    "react-expert",
    "architecture-expert",
    "domain-expert",
    "testing-specialist"
  ]
}
```
