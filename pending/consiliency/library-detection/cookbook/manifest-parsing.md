# Manifest Parsing Cookbook

Parse package manifests to extract dependency information and detect technology stack.

## Instructions

Follow these steps for each manifest type discovered.

## JavaScript/TypeScript (package.json)

### Read the file

```bash
cat package.json | jq '.'
```

### Extract dependencies

```bash
# Production dependencies
cat package.json | jq -r '.dependencies // {} | keys[]'

# Development dependencies
cat package.json | jq -r '.devDependencies // {} | keys[]'

# Peer dependencies
cat package.json | jq -r '.peerDependencies // {} | keys[]'
```

### Framework detection patterns

| Dependency | Framework | Category |
|------------|-----------|----------|
| `react` | React | frontend |
| `react-dom` | React | frontend |
| `next` | Next.js | fullstack |
| `vue` | Vue | frontend |
| `nuxt` | Nuxt | fullstack |
| `svelte` | Svelte | frontend |
| `@sveltejs/kit` | SvelteKit | fullstack |
| `angular` | Angular | frontend |
| `express` | Express | backend |
| `fastify` | Fastify | backend |
| `hono` | Hono | backend |
| `@nestjs/core` | NestJS | backend |

### Test framework detection

| Dependency | Test Framework |
|------------|----------------|
| `vitest` | Vitest |
| `jest` | Jest |
| `mocha` | Mocha |
| `playwright` | Playwright |
| `@playwright/test` | Playwright |
| `cypress` | Cypress |
| `@testing-library/react` | React Testing Library |

### Build tool detection

| Dependency/File | Build Tool |
|-----------------|------------|
| `vite` | Vite |
| `webpack` | Webpack |
| `esbuild` | esbuild |
| `rollup` | Rollup |
| `turbo` | Turborepo |
| `tsconfig.json` exists | TypeScript |

## Python (pyproject.toml)

### Read the file

```bash
# Using Python to parse TOML
python3 -c "import tomllib; import json; print(json.dumps(tomllib.load(open('pyproject.toml', 'rb'))))"
```

### Extract dependencies

Look in these sections:
- `project.dependencies` (PEP 621)
- `tool.poetry.dependencies` (Poetry)
- `tool.pdm.dependencies` (PDM)

### Framework detection patterns

| Dependency | Framework | Category |
|------------|-----------|----------|
| `fastapi` | FastAPI | backend |
| `django` | Django | fullstack |
| `flask` | Flask | backend |
| `starlette` | Starlette | backend |
| `litestar` | Litestar | backend |
| `aiohttp` | aiohttp | backend |
| `streamlit` | Streamlit | frontend |
| `gradio` | Gradio | frontend |

### Test framework detection

| Dependency | Test Framework |
|------------|----------------|
| `pytest` | pytest |
| `pytest-asyncio` | pytest (async) |
| `hypothesis` | Hypothesis |
| `unittest` | unittest (stdlib) |

### Build tool detection

| File/Dependency | Build Tool |
|-----------------|------------|
| `uv` in deps | uv |
| `poetry` section | Poetry |
| `pdm` section | PDM |
| `hatch` section | Hatch |
| `setuptools` | setuptools |

## Python (requirements.txt)

### Read the file

```bash
# Extract package names (strip versions)
grep -v '^#' requirements.txt | grep -v '^$' | sed 's/[<>=!].*//' | sed 's/\[.*//'
```

### Note

requirements.txt lacks structure. Cross-reference with pyproject.toml if both exist.

## Go (go.mod)

### Read the file

```bash
cat go.mod
```

### Extract dependencies

```bash
# Direct dependencies (require block)
grep -A 100 '^require' go.mod | grep -E '^\t' | awk '{print $1}'
```

### Framework detection patterns

| Module Path | Framework | Category |
|-------------|-----------|----------|
| `github.com/gin-gonic/gin` | Gin | backend |
| `github.com/labstack/echo` | Echo | backend |
| `github.com/gofiber/fiber` | Fiber | backend |
| `github.com/go-chi/chi` | Chi | backend |
| `github.com/gorilla/mux` | Gorilla Mux | backend |

### Test framework detection

| Module | Test Framework |
|--------|----------------|
| `github.com/stretchr/testify` | Testify |
| `github.com/onsi/ginkgo` | Ginkgo |
| `github.com/onsi/gomega` | Gomega |

## Rust (Cargo.toml)

### Read the file

```bash
cat Cargo.toml
```

### Extract dependencies

```bash
# Using Python to parse TOML
python3 -c "import tomllib; import json; d=tomllib.load(open('Cargo.toml', 'rb')); print(json.dumps(list(d.get('dependencies', {}).keys())))"
```

### Framework detection patterns

| Crate | Framework | Category |
|-------|-----------|----------|
| `actix-web` | Actix Web | backend |
| `axum` | Axum | backend |
| `rocket` | Rocket | backend |
| `warp` | Warp | backend |
| `yew` | Yew | frontend |
| `leptos` | Leptos | fullstack |
| `dioxus` | Dioxus | frontend |

## Dart/Flutter (pubspec.yaml)

### Read the file

```bash
cat pubspec.yaml
```

### Extract dependencies

Look in these sections:
- `dependencies`
- `dev_dependencies`

### Framework detection patterns

| Dependency | Framework | Category |
|------------|-----------|----------|
| `flutter` | Flutter | mobile |

### Test framework detection

| Dependency | Test Framework |
|------------|----------------|
| `flutter_test` | Flutter Test |
| `test` | Dart Test |
| `integration_test` | Flutter Integration Test |

### Build tool detection

| File/Dependency | Build Tool |
|-----------------|------------|
| `flutter` in deps | Flutter |
| `build_runner` | Build Runner |

## C/C++ (CMakeLists.txt / meson.build / WORKSPACE)

### Read the file

```bash
ls -la CMakeLists.txt meson.build WORKSPACE 2>/dev/null
```

### Extract dependencies

Look for:
- `find_package(...)` in CMake
- `dependency(...)` in Meson
- `http_archive` / `git_repository` in Bazel WORKSPACE

### Framework detection patterns

| Pattern | Framework | Category |
|---------|-----------|----------|
| `find_package(Boost` | Boost | core |
| `find_package(GTest` | GoogleTest | testing |
| `dependency('gtest'` | GoogleTest | testing |
| `dependency('catch2'` | Catch2 | testing |

### Test framework detection

| Dependency/Pattern | Test Framework |
|--------------------|----------------|
| `gtest` | GoogleTest |
| `gmock` | GoogleMock |
| `catch2` | Catch2 |
| `doctest` | doctest |

### Build tool detection

| File/Pattern | Build Tool |
|--------------|------------|
| `CMakeLists.txt` | CMake |
| `meson.build` | Meson |
| `WORKSPACE` | Bazel |

## Database Detection

Look for these patterns in any manifest:

| Pattern | Database |
|---------|----------|
| `prisma`, `@prisma/client` | PostgreSQL/MySQL (Prisma) |
| `sqlalchemy`, `asyncpg` | PostgreSQL |
| `pymongo`, `motor` | MongoDB |
| `redis`, `ioredis` | Redis |
| `mysql2`, `pymysql` | MySQL |
| `sqlite3`, `better-sqlite3` | SQLite |
| `typeorm` | Various SQL |
| `drizzle-orm` | Various SQL |
| `mongoose` | MongoDB |

## Cloud Provider Detection

Look for SDK packages:

| Pattern | Provider |
|---------|----------|
| `@aws-sdk/*`, `boto3` | AWS |
| `@google-cloud/*`, `google-cloud-*` | GCP |
| `@azure/*`, `azure-*` | Azure |
| `@vercel/*` | Vercel |
| `@supabase/*`, `supabase` | Supabase |

## Output Template

After parsing all manifests, compile results:

```json
{
  "project_root": "/path/to/project",
  "scanned_at": "2025-12-21T12:00:00Z",
  "languages": ["typescript", "python", "go", "rust", "dart", "cpp"],
  "frameworks": [
    {"name": "react", "version": "^18.2.0", "category": "frontend"},
    {"name": "fastapi", "version": "^0.109.0", "category": "backend"}
  ],
  "test_frameworks": [
    {"name": "vitest", "version": "^1.2.0"},
    {"name": "pytest", "version": "^7.4.0"}
  ],
  "build_tools": ["vite", "uv"],
  "databases": ["postgresql"],
  "cloud_providers": ["vercel"],
  "ci_cd": ["github-actions"],
  "manifests_found": ["package.json", "pyproject.toml"]
}
```
