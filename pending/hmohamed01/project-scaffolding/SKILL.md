---
name: project-scaffolding
description: >
  IDE-grade project scaffolding wizard for creating new projects with comprehensive configuration.
  Supports 70+ project types: HTML/CSS websites, React, Next.js, Vue, Astro, Remix, React Native,
  Flutter, Expo, FastAPI, Django, Express, NestJS, Go/Gin, Rust/Axum, Spring Boot, Hono, Elysia,
  Chrome Extensions, VS Code Extensions, Tauri desktop apps, serverless functions, and more.
  Provides WebStorm/PyCharm-level project creation with interactive SDK selection, framework
  configuration, database setup, and DevOps tooling. Use when: creating a new project, setting up
  a framework application, initializing a codebase, scaffolding boilerplate, building extensions,
  creating mobile/desktop/web apps, setting up monorepos, or making static websites/landing pages.
---

# Project Scaffolding Wizard

Professional-grade project scaffolding comparable to WebStorm/PyCharm project wizards. Creates fully configured projects with SDK setup, framework options, database configuration, linting, and CI/CD.

## Wizard Workflow

When a user requests a new project, follow this interactive workflow:

### Step 1: Project Type Selection

Present the project type menu. Ask the user to select a category and type:

| Category | Types |
|----------|-------|
| **Static Websites** | HTML/CSS, HTML+Sass, HTML+Tailwind, Landing Page, Multi-page Site |
| **Frontend Web** | React, Next.js, Vue, Nuxt, Svelte, Angular, Astro, Remix, Solid, Qwik, Preact |
| **Mobile/Desktop** | React Native, Expo, Flutter, Tauri, Electron, Ionic |
| **Backend (JS/TS)** | Express, NestJS, Fastify, Hono, Elysia, tRPC, Koa |
| **Backend (Python)** | FastAPI, Django, Django REST, Flask, Litestar |
| **Backend (Go)** | Gin, Fiber, Echo, Chi |
| **Backend (Rust)** | Axum, Actix, Rocket |
| **Backend (Java)** | Spring Boot, Quarkus, Ktor, Micronaut |
| **Backend (Other)** | Laravel, Rails, .NET Web API |
| **Libraries** | TypeScript NPM, Python PyPI, Go Module, Rust Crate |
| **CLI Tools** | Node CLI, Python CLI (Typer/Click), Go CLI (Cobra), Rust CLI (Clap) |
| **Extensions** | Chrome Extension, Firefox Extension, VS Code Extension, Figma Plugin, Obsidian Plugin |
| **Serverless** | AWS Lambda, Cloudflare Workers, Vercel Functions, Supabase Functions |
| **Full-Stack** | T3 Stack, MERN, PERN, MEAN |
| **Monorepos** | Turborepo, Nx Workspace, pnpm Workspace |

### Step 2: Basic Configuration

Gather for ALL projects:
- **Project name** (required)
- **Location/directory**
- **Description**
- **Author name**
- **License** (MIT, Apache-2.0, GPL-3.0, ISC, Unlicense)

### Step 3: Framework-Specific Options

Load `references/wizard-options.md` for detailed configuration options based on the selected project type. Key decisions include:

- **Language/SDK version** - Node.js, Python, Go, Rust, Java versions
- **Package manager** - npm, pnpm, yarn, bun, poetry, uv
- **CSS framework** - Tailwind, CSS Modules, Styled Components
- **State management** - Zustand, Redux, Jotai, TanStack Query
- **Database/ORM** - PostgreSQL, SQLite, Prisma, SQLAlchemy, sqlc
- **Authentication** - NextAuth, JWT, OAuth2
- **Testing** - Vitest, Jest, pytest, Playwright

### Step 4: Code Quality & DevOps

- **Linting** - ESLint, Ruff, golangci-lint, clippy
- **Formatting** - Prettier, Ruff, gofmt, rustfmt
- **Pre-commit hooks** - husky + lint-staged, pre-commit framework
- **CI/CD** - GitHub Actions, GitLab CI
- **Docker** - Dockerfile (multi-stage), docker-compose
- **Deployment** - Vercel, Railway, Fly.io, AWS, self-hosted

### Step 5: Generate Project

Use `scripts/scaffold.py` or native CLI tools to create the project structure.

## CLI Integration

Prefer native CLI tools when available:

| Framework | CLI Command |
|-----------|-------------|
| Next.js | `npx create-next-app@latest` |
| React (Vite) | `npm create vite@latest -- --template react-ts` |
| Vue | `npm create vue@latest` |
| Nuxt | `npx nuxi@latest init` |
| Astro | `npm create astro@latest` |
| Remix | `npx create-remix@latest` |
| SvelteKit | `npm create svelte@latest` |
| Solid | `npm create solid@latest` |
| Expo | `npx create-expo-app@latest` |
| React Native | `npx @react-native-community/cli init` |
| Flutter | `flutter create` |
| Tauri | `npm create tauri-app@latest` |
| NestJS | `npx @nestjs/cli new` |
| Spring Boot | `spring init` or start.spring.io |
| Go | `go mod init` |
| Rust | `cargo new` |
| Chrome Ext | `npm create plasmo@latest` |
| T3 Stack | `npx create-t3-app@latest` |

## Quick Start Examples

### HTML/CSS Website
```bash
mkdir my-website && cd my-website
touch index.html style.css
# Or use boilerplate:
npx degit h5bp/html5-boilerplate my-website
```

### HTML + Tailwind (CDN)
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Website</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
  <h1 class="text-3xl font-bold">Hello World</h1>
</body>
</html>
```

### T3 Stack (Next.js + tRPC + Prisma)
```bash
npx create-t3-app@latest my-app
```

### Expo (React Native)
```bash
npx create-expo-app@latest my-app --template tabs
```

### Tauri Desktop App
```bash
npm create tauri-app@latest my-app -- --template react-ts
```

### Chrome Extension
```bash
npm create plasmo@latest my-extension
```

## Example Conversations

### Simple HTML/CSS Website
```
User: Create a simple website with HTML and CSS

Claude: I'll create a static HTML/CSS website:

- Multi-page (Home, About, Contact)
- Mobile-first responsive CSS
- BEM naming convention
- Live Server for development

Structure:
my-website/
├── index.html
├── about.html
├── contact.html
├── css/style.css
├── js/main.js
└── images/

Shall I create this?
```

### Mobile App
```
User: Create a mobile app for iOS and Android

Claude: I recommend Expo for the easiest setup:

- TypeScript
- Expo Router (file-based navigation)
- NativeWind (Tailwind for RN)
- Tab navigation template

Ready to scaffold?
```

### Full-Stack with Type Safety
```
User: Create a full-stack app with type-safe API

Claude: I recommend the T3 Stack:

- Next.js 14 (App Router)
- tRPC (type-safe API)
- Prisma (type-safe ORM)
- Tailwind CSS
- NextAuth.js
- PostgreSQL with docker-compose

This gives you full type safety from database to frontend!
```

### Chrome Extension
```
User: Build a Chrome extension

Claude: What features do you need?

- Popup UI
- Content script (modifies pages)
- Background service worker
- Side panel

Tech stack: React + Vite + TypeScript + Manifest V3

I recommend using Plasmo framework for easier development.
```

## Available Resources

Load reference files based on what you need:

| Resource | When to Load | Purpose |
|----------|--------------|---------|
| `references/wizard-options.md` | During Step 3 (gathering user preferences) | Configuration choices and defaults for each framework |
| `references/frameworks.md` | When generating code | Project structures, code examples, configuration files |
| `references/best-practices.md` | For architecture decisions | Directory organization, naming conventions, patterns |
| `scripts/scaffold.py` | For custom scaffolding | Python engine when CLI tools aren't suitable |

**Workflow:**
1. Present options from `wizard-options.md` to gather user preferences
2. Use `frameworks.md` for code patterns and project structure when generating
3. Consult `best-practices.md` for architecture decisions

## Default Recommendations

| Category | Recommendation |
|----------|----------------|
| JS Runtime | Node.js 22 LTS |
| Package Manager | pnpm |
| Python Version | 3.12 |
| Go Version | 1.23 |
| Rust Edition | 2021 |
| Java Version | 21 LTS |
| CSS Framework | Tailwind CSS |
| State (React) | Zustand + TanStack Query |
| ORM (Node) | Prisma |
| ORM (Python) | SQLAlchemy 2.0 |
| ORM (Go) | sqlc |
| Testing (JS) | Vitest |
| Testing (Python) | pytest |
| E2E Testing | Playwright |
| Linting (JS) | ESLint + Prettier |
| Linting (Python) | Ruff |
| CI/CD | GitHub Actions |
| Containerization | Multi-stage Dockerfile |
