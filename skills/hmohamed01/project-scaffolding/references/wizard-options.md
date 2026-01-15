# Wizard Configuration Options

Detailed configuration options for each project type. Load this reference when gathering user preferences for a specific framework.

## Table of Contents

1. [Language & SDK Options](#language--sdk-options)
2. [HTML/CSS Projects](#htmlcss-projects)
3. [React Projects](#react-projects)
4. [Next.js Projects](#nextjs-projects)
5. [Vue Projects](#vue-projects)
6. [Nuxt Projects](#nuxt-projects)
7. [Svelte Projects](#svelte-projects)
8. [Angular Projects](#angular-projects)
9. [Astro Projects](#astro-projects)
10. [Mobile Projects](#mobile-projects)
11. [JavaScript/TypeScript Backend](#javascripttypescript-backend)
12. [Python Backend](#python-backend)
13. [Go Backend](#go-backend)
14. [Rust Backend](#rust-backend)
15. [Java/Kotlin Backend](#javakotlin-backend)
16. [Other Backends](#other-backends)
17. [Libraries & Packages](#libraries--packages)
18. [CLI Tools](#cli-tools)
19. [Browser Extensions](#browser-extensions)
20. [Desktop Apps](#desktop-apps)
21. [Serverless & Edge](#serverless--edge)
22. [Full-Stack Templates](#full-stack-templates)
23. [Monorepos](#monorepos)
24. [Code Quality & Tooling](#code-quality--tooling)
25. [Testing Configuration](#testing-configuration)
26. [DevOps & Deployment](#devops--deployment)

---

## Language & SDK Options

### JavaScript/TypeScript
| Option | Choices | Default |
|--------|---------|---------|
| Language | TypeScript, JavaScript | TypeScript |
| Strict mode | Yes, No | Yes |
| Path aliases (@/*) | Yes, No | Yes |
| Runtime | Node.js 20/22, Bun, Deno | Node.js 22 |
| Package Manager | npm, yarn, pnpm, bun | pnpm |

### Python
| Option | Choices | Default |
|--------|---------|---------|
| Version | 3.11, 3.12, 3.13 | 3.12 |
| Environment | venv, uv, poetry, pipenv, conda | uv |
| Type Hints | Full, Minimal, None | Full |

### Go
| Option | Choices | Default |
|--------|---------|---------|
| Version | 1.22, 1.23 | 1.23 |
| Module Path | github.com/username/project | - |

### Rust
| Option | Choices | Default |
|--------|---------|---------|
| Edition | 2021, 2024 | 2021 |
| Crate Type | Binary, Library, Both | Library |

### Java/Kotlin
| Option | Choices | Default |
|--------|---------|---------|
| Java Version | 17 LTS, 21 LTS, 23 | 21 LTS |
| Build Tool | Gradle (Kotlin DSL), Gradle (Groovy), Maven | Gradle (Kotlin DSL) |

---

## HTML/CSS Projects

### Structure Options
- Single page (index.html only)
- Multi-page (index, about, contact, etc.) *recommended*
- Landing page template

### CSS Approach
- Plain CSS
- Sass/SCSS *recommended*
- Tailwind CLI
- CSS Variables + Custom Properties

### Features
- Responsive design (mobile-first) *recommended*
- SEO meta tags *recommended*
- Open Graph tags
- Favicon set
- Sitemap.xml
- Robots.txt

### JavaScript Enhancement
- None (pure HTML/CSS)
- Vanilla JS (minimal interactivity)
- Alpine.js (reactive)
- HTMX (server interactions)

### CSS Methodology
- BEM naming convention *recommended*
- SMACSS
- Utility-first
- None (custom)

### Development Tools
- Live Server / Browser Sync *recommended*
- Sass watch mode
- Image optimization script

---

## React Projects

### Build Tool
- Vite *recommended*
- Create React App (legacy)

### CSS Framework
- Tailwind CSS *recommended*
- CSS Modules
- Styled Components
- Emotion
- Vanilla Extract
- UnoCSS
- None

### UI Component Library
- None
- shadcn/ui *recommended*
- Radix UI
- Headless UI
- Chakra UI
- Material UI
- Ant Design

### State Management
- None (React Context only)
- Zustand *recommended*
- Jotai (atomic)
- Redux Toolkit
- TanStack Query (server state)

### Data Fetching
- TanStack Query *recommended*
- SWR
- Apollo Client (GraphQL)
- None

### Routing
- React Router v6 *recommended*
- TanStack Router
- None

### Forms
- React Hook Form + Zod *recommended*
- Formik + Yup
- None

### Testing
- Vitest + Testing Library *recommended*
- Jest + Testing Library
- None

---

## Next.js Projects

### Version & Router
- Next.js 14+ App Router *recommended*
- Next.js Pages Router

### Features
- TypeScript *default*
- ESLint *default*
- Tailwind CSS *default*
- src/ directory *default*
- Turbopack

### Database/ORM
- None
- Prisma *recommended*
- Drizzle
- Supabase

### Authentication
- None
- NextAuth.js / Auth.js *recommended*
- Clerk
- Lucia
- Custom JWT

### API Style
- REST (Route Handlers)
- tRPC *recommended for full-stack*
- GraphQL (Apollo/Yoga)

---

## Vue Projects

### Build Tool
- Vite *recommended*
- Vue CLI (legacy)

### API Style
- Composition API *recommended*
- Options API

### CSS Framework
- Tailwind CSS *recommended*
- UnoCSS
- CSS Modules
- None

### UI Component Library
- None
- Vuetify
- PrimeVue
- Naive UI
- Element Plus
- Headless UI

### State Management
- Pinia *recommended*
- Vuex (legacy)
- None

### Routing
- Vue Router *default*

### Forms
- VeeValidate + Zod *recommended*
- FormKit
- None

### Testing
- Vitest + Vue Test Utils *recommended*
- Jest
- None

---

## Nuxt Projects

### Version
- Nuxt 3 *recommended*

### Features
- TypeScript *default*
- Auto-imports *default*
- ESLint *default*
- Tailwind CSS (@nuxtjs/tailwindcss)

### Rendering Mode
- Universal (SSR) *recommended*
- SPA (client-only)
- Static (SSG)
- Hybrid

### Modules
- @pinia/nuxt (state) *recommended*
- @nuxt/image
- @nuxt/content (for content sites)
- @sidebase/nuxt-auth

### API
- Nitro server routes *default*
- tRPC (@trpc-nuxt/client)

---

## Svelte Projects

### Framework
- SvelteKit *recommended*
- Svelte (standalone)

### Features
- TypeScript *default*
- ESLint *default*

### CSS Framework
- Tailwind CSS *recommended*
- UnoCSS
- None

### State Management
- Svelte stores *default*
- None (props only)

### Rendering Mode (SvelteKit)
- SSR *default*
- SPA
- Static (prerender)

### Testing
- Vitest + Testing Library *recommended*
- Playwright (E2E)

---

## Angular Projects

### Version
- Angular 17+ *recommended*

### Features
- TypeScript *default*
- Standalone components *recommended*
- Signals *recommended*
- SSR (Angular Universal)

### CSS Framework
- Tailwind CSS
- Angular Material *recommended*
- PrimeNG
- None (SCSS)

### State Management
- Signals *recommended*
- NgRx
- Akita
- None (services)

### HTTP Client
- HttpClient *default*
- Apollo Client (GraphQL)

### Forms
- Reactive Forms *recommended*
- Template-driven Forms

### Testing
- Jest *recommended*
- Karma (default)
- Playwright (E2E)

---

## Astro Projects

### Template
- Minimal *default*
- Blog
- Documentation (Starlight)
- Portfolio

### Integrations
- React
- Vue
- Svelte
- Solid
- Tailwind CSS *recommended*
- MDX

### Rendering Mode
- Static (SSG)
- Hybrid (SSG + SSR) *recommended*
- Server (SSR)

---

## Mobile Projects

### React Native / Expo

#### Template
- Expo (managed workflow) *recommended*
- Expo (bare workflow)
- React Native CLI

#### Navigation
- Expo Router (file-based) *recommended*
- React Navigation

#### Features
- TypeScript *default*
- NativeWind (Tailwind)
- Tamagui
- Expo Router typed routes

### Flutter

#### Platforms
- Android *default*
- iOS *default*
- Web
- Desktop (Windows/macOS/Linux)

#### State Management
- Riverpod *recommended*
- BLoC
- Provider
- GetX

#### Integrations
- Firebase
- Supabase
- Local storage (Hive/Isar)

---

## JavaScript/TypeScript Backend

### Express

#### Features
- TypeScript *recommended*
- ESLint + Prettier

#### Project Structure
- Simple (single file)
- Standard (routes/, controllers/, services/) *recommended*
- Domain-driven

#### Database/ORM
- None
- Prisma *recommended*
- Drizzle
- TypeORM
- Sequelize

#### Authentication
- None
- Passport.js *recommended*
- Custom JWT

#### Validation
- Zod *recommended*
- Joi
- express-validator

### NestJS

#### Features
- TypeScript *default*
- Strict mode *default*

#### Database/ORM
- Prisma *recommended*
- TypeORM
- Sequelize
- Mongoose (MongoDB)

#### Authentication
- @nestjs/passport *recommended*
- Custom guards

#### API Style
- REST *default*
- GraphQL (@nestjs/graphql)
- gRPC

#### Microservices
- None (monolith)
- @nestjs/microservices

### Fastify

#### Features
- TypeScript *recommended*
- Schema validation (JSON Schema)

#### Plugins
- @fastify/cors
- @fastify/jwt
- @fastify/swagger

### Hono

#### Runtime
- Node.js
- Bun *recommended*
- Cloudflare Workers
- Deno

#### Features
- TypeScript *default*
- Zod validation
- JWT middleware

### Elysia

#### Runtime
- Bun *required*

#### Features
- TypeScript *default*
- End-to-end type safety
- Swagger/OpenAPI

### tRPC

#### Framework Integration
- Next.js *recommended*
- Express
- Fastify
- Standalone

#### Features
- Zod validation *default*
- React Query integration
- Subscriptions (WebSocket)

### Koa

#### Features
- TypeScript *recommended*
- Middleware-based

#### Common Middleware
- koa-router
- koa-bodyparser
- koa-jwt

---

## Python Backend

### FastAPI

#### Project Structure
- Simple (single main.py)
- Standard (app/ directory) *recommended*
- Large-scale (domain-driven)

#### Database
- None
- SQLite (development)
- PostgreSQL *recommended*
- MySQL
- MongoDB

#### ORM
- SQLAlchemy 2.0 *recommended*
- SQLModel
- Tortoise ORM
- Beanie (MongoDB)

#### Authentication
- None
- JWT with python-jose *recommended*
- OAuth2 with authlib
- Session-based

#### Additional Features
- Background tasks (Celery/ARQ)
- WebSocket support
- GraphQL (Strawberry)
- Redis caching

### Django

#### API Framework
- Django REST Framework *recommended*
- Django Ninja

#### Features
- Custom User model *recommended*
- Celery for background tasks
- Channels (WebSocket)

#### Database
- PostgreSQL *recommended*
- MySQL
- SQLite (dev)

#### Authentication
- Django Allauth *recommended*
- Simple JWT
- Session-based

### Flask

#### Extensions
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Flask-CORS

### Litestar

#### Features
- Async-first
- Msgspec/Pydantic validation
- SQLAlchemy integration

---

## Go Backend

### Framework
- Gin *recommended*
- Fiber
- Echo
- Chi
- Standard library (net/http)

### Project Structure
- Simple (single main.go)
- Standard (internal/, cmd/, pkg/) *recommended*
- Domain-driven

### Database
- None
- PostgreSQL *recommended*
- MySQL
- MongoDB
- SQLite

### ORM/Query Builder
- sqlc (type-safe SQL) *recommended*
- GORM
- sqlx
- Ent

### Features
- JWT authentication
- Rate limiting
- Swagger/OpenAPI (swaggo)
- Graceful shutdown

---

## Rust Backend

### Framework
- Axum *recommended*
- Actix Web
- Rocket

### Axum Features
- Async runtime (Tokio) *default*
- Database (SQLx + PostgreSQL)
- Tracing/logging
- Error handling (thiserror/anyhow)
- Configuration (config-rs)

### Actix Features
- Actor model
- WebSocket support
- High performance

### Rocket Features
- Request guards
- Fairings (middleware)
- Type-safe routing

---

## Java/Kotlin Backend

### Spring Boot

#### Language
- Java *default*
- Kotlin

#### Dependencies
- Spring Web *default*
- Spring Data JPA *default*
- Spring Security
- Spring Cloud
- Spring Actuator

#### Database
- H2 (dev)
- PostgreSQL *recommended*
- MySQL
- MongoDB

### Quarkus

#### Features
- Native compilation (GraalVM)
- Fast startup
- Low memory footprint

### Ktor

#### Features
- Kotlin-first
- Coroutines
- Lightweight

### Micronaut

#### Features
- Compile-time DI
- GraalVM native
- Cloud-native

---

## Other Backends

### Laravel (PHP)

#### Features
- Eloquent ORM
- Blade templates
- Sanctum (API auth)
- Horizon (queues)

### Ruby on Rails

#### Features
- Active Record
- Action Cable (WebSocket)
- Hotwire/Turbo

### .NET Web API

#### Features
- C# *default*
- Entity Framework Core
- Identity (auth)
- Minimal APIs or Controllers

---

## Libraries & Packages

### TypeScript NPM Package

#### Build Tool
- tsup *recommended*
- Rollup
- esbuild
- tsc only

#### Features
- ESM + CJS dual publish *recommended*
- TypeScript declarations
- Changesets (versioning)

#### Testing
- Vitest *recommended*
- Jest

### Python PyPI Package

#### Build Tool
- Hatch *recommended*
- Poetry
- Setuptools
- Flit

#### Features
- Type hints (py.typed)
- Multiple Python versions
- Documentation (mkdocs/sphinx)

#### Testing
- pytest *recommended*
- tox/nox (multi-version)

### Go Module

#### Features
- Semantic versioning
- Example tests
- Benchmarks

#### Documentation
- pkg.go.dev *default*
- GoDoc comments

### Rust Crate

#### Crate Type
- Library *default*
- Binary
- Proc-macro

#### Features
- Documentation (rustdoc)
- Feature flags
- no_std support

---

## CLI Tools

### Node.js CLI

#### Framework
- Commander.js *recommended*
- Yargs
- Oclif
- CAC

#### Features
- TypeScript *recommended*
- Interactive prompts (inquirer/prompts)
- Progress bars (ora/cli-progress)
- Colors (chalk/picocolors)

### Python CLI

#### Framework
- Typer *recommended*
- Click
- argparse (stdlib)

#### Features
- Rich (formatting)
- Type hints
- Auto-completion

### Go CLI

#### Framework
- Cobra *recommended*
- urfave/cli
- Kong

#### Features
- Viper (config)
- Cross-compilation
- Single binary

### Rust CLI

#### Framework
- Clap *recommended*
- argh
- structopt (legacy)

#### Features
- Colored output (colored/termcolor)
- Progress bars (indicatif)
- Cross-compilation

---

## Browser Extensions

### Chrome Extension

#### Manifest Version
- Manifest V3 *required*

#### Features
- Popup UI
- Options page
- Background service worker
- Content scripts
- Side panel

#### UI Framework
- React + Vite *recommended*
- Vue + Vite
- Svelte
- Vanilla JS
- Plasmo framework

### Firefox Extension

#### Features
- WebExtension API
- Cross-browser compatibility
- Manifest V2/V3

### VS Code Extension

#### Extension Type
- Language support
- Themes/colors
- Snippets
- Commands/tools *default*
- Webview

#### Features
- TypeScript *default*
- Webview UI
- Language Server Protocol
- Testing setup

### Figma Plugin

#### Features
- TypeScript *recommended*
- UI (HTML/CSS or React)
- Figma API

### Obsidian Plugin

#### Features
- TypeScript *recommended*
- Obsidian API
- Settings tab

---

## Desktop Apps

### Tauri

#### Frontend
- React + Vite *recommended*
- Vue + Vite
- Svelte + Vite
- Solid + Vite
- Vanilla

#### Features
- System tray
- Auto-updater
- Custom titlebar
- File system access

### Electron

#### Frontend
- React *recommended*
- Vue
- Svelte
- Vanilla

#### Build Tool
- Electron Forge *recommended*
- electron-builder

#### Features
- Auto-updater
- Native menus
- System tray
- IPC communication

---

## Serverless & Edge

### AWS Lambda

#### Runtime
- Node.js 20 *recommended*
- Python 3.12
- Go
- Rust (custom runtime)

#### Framework
- SST *recommended*
- Serverless Framework
- SAM
- CDK

#### Features
- API Gateway
- DynamoDB
- S3 triggers
- EventBridge

### Cloudflare Workers

#### Framework
- Hono *recommended*
- Itty Router
- None (Fetch API)

#### Features
- KV storage
- D1 (SQLite)
- R2 (object storage)
- Durable Objects

### Vercel Functions

#### Runtime
- Node.js *default*
- Edge Runtime

#### Features
- Next.js API routes
- Edge middleware
- Cron jobs

### Supabase Functions

#### Runtime
- Deno *default*

#### Features
- Database access
- Auth integration
- Edge deployment

---

## Full-Stack Templates

### T3 Stack
- Next.js 14+ (App Router)
- tRPC
- Prisma
- Tailwind CSS
- NextAuth.js

### MERN Stack
- MongoDB
- Express
- React
- Node.js

### PERN Stack
- PostgreSQL
- Express
- React
- Node.js

### MEAN Stack
- MongoDB
- Express
- Angular
- Node.js

---

## Monorepos

### Turborepo

#### Package Manager
- pnpm *recommended*
- npm
- yarn

#### Features
- Remote caching
- Parallel execution
- Incremental builds

#### Structure
- apps/ (applications)
- packages/ (shared libraries)

### Nx Workspace

#### Features
- Generators
- Executors
- Affected commands
- Module federation

#### Plugins
- @nx/react
- @nx/next
- @nx/node
- @nx/nest

### pnpm Workspace

#### Features
- Simple setup
- Workspace protocol
- Catalog (shared deps)

---

## Code Quality & Tooling

### JavaScript/TypeScript
| Tool | Options | Default |
|------|---------|---------|
| Linting | ESLint (flat config), Biome | ESLint |
| Formatting | Prettier, Biome | Prettier |
| Pre-commit | lint-staged + husky | Yes |

### Python
| Tool | Options | Default |
|------|---------|---------|
| Linting | Ruff, Flake8, Pylint | Ruff |
| Formatting | Ruff, Black | Ruff |
| Pre-commit | pre-commit framework | Yes |

### Go
| Tool | Options | Default |
|------|---------|---------|
| Linting | golangci-lint | Yes |
| Formatting | gofmt/goimports | Yes |

### Rust
| Tool | Options | Default |
|------|---------|---------|
| Linting | clippy | Yes |
| Formatting | rustfmt | Yes |

### CSS
| Tool | Options | Default |
|------|---------|---------|
| Linting | Stylelint | Yes (for CSS/SCSS) |

---

## Testing Configuration

### Unit Testing
| Language | Options | Default |
|----------|---------|---------|
| JS/TS | Vitest, Jest | Vitest |
| Python | pytest, unittest | pytest |
| Go | Built-in, Testify | Built-in |
| Rust | Built-in | Built-in |

### E2E Testing
| Tool | Best For |
|------|----------|
| Playwright *recommended* | Cross-browser, modern |
| Cypress | Component + E2E |

### Coverage
- With threshold (80%) *recommended*
- Reporting only
- None

---

## DevOps & Deployment

### Version Control
- Initialize Git repository *default*
- Add .gitignore *default*
- Create initial commit *default*

### CI/CD
- GitHub Actions *recommended*
- GitLab CI
- None

### Containerization
- Dockerfile (multi-stage) *recommended*
- docker-compose.yml *recommended*
- None

### Deployment Targets

| Target | Best For |
|--------|----------|
| GitHub Pages | Static HTML/CSS |
| Netlify | Static/JAMstack |
| Vercel | Next.js, frontend |
| Railway | Full-stack, databases |
| Fly.io | Containers, edge |
| AWS (ECS/Lambda) | Enterprise |
| Google Cloud Run | Containers |
| Self-hosted | Full control |

### Environment Management
- .env.example template *default*
- Config validation (Zod/Pydantic) *recommended*

### Monitoring
- Structured logging
- Error tracking (Sentry)
- None
