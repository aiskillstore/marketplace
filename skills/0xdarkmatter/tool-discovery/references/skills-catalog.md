# Skills Catalog

Complete reference for all available skills.

## Language & Framework Skills

Comprehensive operational expertise for specific languages and frameworks.

### go-ops

**Triggers:** golang, go, goroutine, channel, context, errgroup, go test, go mod, interface, generics, go build, worker pool

**Use For:**
- Concurrency patterns (goroutines, channels, errgroup, worker pools)
- Error handling (sentinel errors, custom types, wrapping, errors.Is/As)
- Testing (table-driven, httptest, benchmarks, fuzz, mocking with interfaces)
- Interface design, generics, functional options
- Project structure, module management, workspaces
- Performance profiling (pprof, trace, escape analysis)

**References:** concurrency.md, error-handling.md, testing.md, interfaces-generics.md, project-structure.md, performance.md

---

### rust-ops

**Triggers:** rust, cargo, ownership, borrow checker, lifetime, tokio, serde, trait, Result, Option, async rust, crate

**Use For:**
- Ownership, borrowing, lifetimes, interior mutability
- Traits, generics, associated types, derive macros
- Error handling (thiserror, anyhow, Result/Option combinators)
- Async with tokio (spawn, channels, select, graceful shutdown)
- Ecosystem (serde, clap, reqwest, sqlx, axum, tracing, rayon)
- Testing (mockall, proptest, criterion, insta)

**References:** ownership-lifetimes.md, traits-generics.md, error-handling.md, async-tokio.md, ecosystem.md, testing.md

---

### typescript-ops

**Triggers:** typescript, type system, generics, utility types, Zod, mapped types, conditional types, tsconfig, strict mode

**Use For:**
- Type narrowing, type guards, discriminated unions
- Generics, conditional types, mapped types, template literal types
- Utility types (Partial, Pick, Omit, Record, ReturnType, etc.)
- tsconfig configuration, strict mode migration
- Runtime validation (Zod, Valibot), type-safe APIs (tRPC)

**References:** type-system.md, generics-patterns.md, utility-types.md, config-strict.md, ecosystem.md

---

## Infrastructure Skills

### docker-ops

**Triggers:** docker, Dockerfile, docker-compose, container, image, multi-stage build, distroless, BuildKit

**Use For:**
- Dockerfile best practices, multi-stage builds (Go, Rust, Node, Python)
- Docker Compose patterns (services, volumes, networking, health checks)
- Image optimization, layer caching, security scanning
- BuildKit features, cross-platform builds

**References:** multi-stage-builds.md, compose-patterns.md, optimization.md

---

### ci-cd-ops

**Triggers:** github actions, CI, CD, pipeline, workflow, release, semantic release, changesets, goreleaser

**Use For:**
- GitHub Actions workflow syntax, triggers, matrix strategy
- Caching strategies (node_modules, go modules, cargo, pip)
- Release automation (semantic-release, changesets, goreleaser)
- Testing pipelines, code coverage, deployment gates

**References:** github-actions.md, release-automation.md, testing-pipelines.md

---

### api-design-ops

**Triggers:** api design, gRPC, GraphQL, protobuf, api versioning, pagination, rate limiting, webhook, idempotency

**Use For:**
- API style selection (REST vs gRPC vs GraphQL)
- REST advanced patterns (pagination, PATCH, bulk ops, webhooks)
- gRPC (protobuf, streaming, Go/Rust implementations)
- GraphQL (schema design, DataLoader, federation)
- API security (JWT, OAuth2, rate limiting, OWASP API Top 10)

**References:** rest-advanced.md, grpc.md, graphql.md, api-security.md

---

## Pattern Skills

Quick reference for common patterns and syntax.

### rest-ops

**Triggers:** rest api, http methods, status codes, api design, endpoint design

**Use For:**
- HTTP method semantics (GET, POST, PUT, PATCH, DELETE)
- Status code selection
- API versioning strategies
- Caching and rate limiting
- Error response formats

**References:** status-codes.md, caching-patterns.md, rate-limiting.md, response-formats.md

---

### postgres-ops

**Triggers:** postgresql, postgres, EXPLAIN ANALYZE, vacuum, autovacuum, pgbouncer, JSONB, RLS, replication, partitioning, pg_stat, GIN, GiST, BRIN, tsvector, WAL, connection pooling, postgresql.conf

**Use For:**
- Schema design, normalization, data types (JSONB, arrays, ranges)
- Index selection (B-tree, GIN, GiST, BRIN, Hash)
- Query tuning with EXPLAIN ANALYZE
- Backup/restore (pg_dump, pg_basebackup, WAL, PITR)
- Vacuum and autovacuum tuning
- Connection pooling (pgBouncer, pgPool)
- Replication (streaming, logical), failover
- Partitioning (range, list, hash)
- Monitoring (pg_stat_statements, bloat, locks)
- Row-level security, full-text search, extensions

**References:** schema-design.md, indexing.md, query-tuning.md, operations.md, replication.md, config-tuning.md

---

### sql-ops

**Triggers:** sql patterns, cte example, window functions, sql join, index strategy

**Use For:**
- CTE (Common Table Expressions)
- Window functions (ROW_NUMBER, LAG, running totals)
- JOIN reference
- Pagination patterns
- Vendor-neutral index strategies

**References:** window-functions.md, indexing-strategies.md

---

### tailwind-ops

**Triggers:** tailwind, utility classes, responsive design, tailwind config, dark mode

**Use For:**
- Responsive breakpoints
- Layout patterns (flex, grid)
- Component patterns (cards, forms, navbars)
- Dark mode configuration
- State modifiers

**References:** component-patterns.md

---

### sqlite-ops

**Triggers:** sqlite, sqlite3, aiosqlite, local database, database schema

**Use For:**
- Schema design patterns (state, cache, events)
- Python sqlite3 usage
- Async operations with aiosqlite
- WAL mode configuration
- Migration patterns

**References:** schema-patterns.md, async-patterns.md, migration-patterns.md

---

### react-ops

**Triggers:** react, hooks, useState, useEffect, jsx, tsx, next.js, nextjs, app router, server components, RSC, zustand, react query

**Use For:**
- Hook patterns (built-in, custom, React 19)
- Component architecture (compound, render props, HOCs)
- State management (Context, Zustand, Jotai, Redux Toolkit, TanStack Query)
- React Server Components, Server Actions, streaming
- Performance optimization (memo, code splitting, virtualization)
- Testing (React Testing Library, MSW, Vitest)

**References:** hooks-patterns.md, component-architecture.md, state-management.md, server-components.md, performance.md, testing.md

---

### vue-ops

**Triggers:** vue, vuejs, composition api, pinia, vue router, nuxt, nuxt3, script setup, composable, reactive, defineProps

**Use For:**
- Composition API and composables
- Pinia state management
- Vue Router (guards, lazy loading, meta)
- Nuxt 3 (SSR/SSG, useFetch, server routes, modules)
- Testing (Vitest, Vue Test Utils, Pinia testing)

**References:** composition-api.md, state-routing.md, nuxt.md, testing.md

---

### javascript-ops

**Triggers:** javascript, js, node, nodejs, esm, commonjs, promise, async await, event loop, v8, npm, es2024

**Use For:**
- Async patterns (Promises, async/await, streams, workers)
- Module systems (ESM, CJS, dual-package)
- Modern JS features (ES2022-2025)
- Node.js patterns (built-in test runner, worker_threads, streams)
- V8 optimization and memory management

**References:** async-patterns.md, modules-runtime.md, modern-features.md, node-patterns.md

---

### astro-ops

**Triggers:** astro, islands architecture, content collections, astro cloudflare, view transitions, partial hydration

**Use For:**
- Rendering strategies (SSG, SSR, hybrid)
- Islands architecture and partial hydration
- Content Collections (schema, queries, MDX)
- Deployment (Cloudflare, Vercel, Netlify, Node)

**References:** content-collections.md, islands-rendering.md, deployment.md

---

### laravel-ops

**Triggers:** laravel, eloquent, artisan, blade, php, sanctum, livewire, inertia, pest, phpunit

**Use For:**
- Eloquent ORM (relationships, scopes, query optimization)
- Architecture (Service Container, providers, facades, middleware)
- Authentication (Sanctum, Fortify, policies/gates)
- Testing (Pest, PHPUnit, factories, facade fakes)

**References:** eloquent-queries.md, architecture.md, testing-auth.md

---

### mcp-ops

**Triggers:** mcp, model context protocol, mcp server, mcp tool, mcp resource, fastmcp, mcp transport, stdio, sse

**Use For:**
- MCP server development (Python FastMCP, TypeScript SDK)
- Tool design (schema, validation, error handling)
- Resources and prompts
- Transport configuration (stdio, SSE, streamable HTTP)
- Authentication and session management
- Testing and debugging (MCP Inspector)

**References:** server-architecture.md, tool-handlers.md, resources-prompts.md, transport-auth.md, testing-debugging.md

---

### tailwind-ops

**Triggers:** tailwind, tailwindcss, utility classes, responsive design, dark mode, tailwind v4, container queries

**Use For:**
- Layout patterns (flex, grid, container queries)
- Responsive design and dark mode
- Component patterns (cards, forms, navbars, modals)
- Tailwind v4 migration (CSS-first config, @theme)
- Configuration and plugins

**References:** component-patterns.md, v4-migration.md, configuration.md

---

## Infrastructure & Operations Skills

### nginx-ops

**Triggers:** nginx, reverse proxy, load balancer, proxy_pass, ssl certificate, lets encrypt, web server

**Use For:**
- Reverse proxy configuration and load balancing
- SSL/TLS setup (Let's Encrypt, HSTS, OCSP)
- Security headers and rate limiting
- Performance tuning (gzip, caching, worker config)
- Docker patterns (nginx as sidecar)

**References:** reverse-proxy.md, ssl-security.md, performance.md

---

### auth-ops

**Triggers:** authentication, authorization, jwt, oauth, oauth2, session, login, rbac, abac, passkey, mfa, api key

**Use For:**
- Authentication methods (JWT, sessions, OAuth2, passkeys)
- Authorization models (RBAC, ABAC, ReBAC)
- OAuth2/OIDC flows (Authorization Code + PKCE, Client Credentials)
- Password handling, MFA, session management
- Implementation patterns across Node.js, Python, Go

**References:** jwt-sessions.md, oauth2-oidc.md, authorization.md, implementation.md

---

### monitoring-ops

**Triggers:** monitoring, observability, prometheus, grafana, metrics, alerting, opentelemetry, SLO, distributed tracing

**Use For:**
- Metrics (Prometheus, PromQL, OpenTelemetry)
- Structured logging (Loki, ELK, language-specific)
- Distributed tracing (OpenTelemetry, Jaeger)
- Alerting and SLO/SLI design
- Infrastructure monitoring and health checks

**References:** metrics-alerting.md, logging.md, tracing.md, infrastructure.md

---

### debug-ops

**Triggers:** debug, debugging, bug, crash, memory leak, race condition, deadlock, bisect, root cause, profiling

**Use For:**
- Systematic debugging methodology
- Language-specific debugger usage (Node, Python, Go, Rust)
- Common scenarios (memory leaks, deadlocks, race conditions)
- Root cause analysis and reproduction techniques

**References:** systematic-methods.md, tool-specific.md, common-scenarios.md

---

## CLI Tool Skills

Modern command-line tools for development workflows.

### file-search

**Triggers:** fd, ripgrep, rg, find files, search code, fzf, fuzzy find

**Use For:**
- Finding files by name (fd)
- Searching file contents (rg)
- Interactive selection (fzf)
- Combined workflows

**References:** advanced-workflows.md

---

### find-replace

**Triggers:** sd, find replace, batch replace, string replacement

**Use For:**
- Modern find-and-replace with sd
- Regex patterns
- Batch operations
- Preview before applying

**References:** advanced-patterns.md

---

### code-stats

**Triggers:** tokei, difft, line counts, code statistics, semantic diff

**Use For:**
- Codebase statistics (tokei)
- Semantic diffs (difft)
- Language breakdown
- Before/after comparisons

**References:** tokei-advanced.md, difft-advanced.md

---

### data-processing

**Triggers:** jq, yq, json, yaml, toml

**Use For:**
- JSON processing and transformation
- YAML/TOML operations
- Structured data queries
- Config file manipulation

**References:** jq-patterns.md, yq-patterns.md, shell-integration.md

---

### structural-search

**Triggers:** ast-grep, sg, ast pattern, find function calls, semantic search

**Use For:**
- Search by AST structure
- Pattern matching in code
- Refactoring operations
- Security scans

**References:** js-ts-patterns.md, python-patterns.md, go-rust-patterns.md, security-ops.md, advanced-usage.md

---

## Workflow Skills

Project and development workflow automation.

### git-ops

**Triggers:** commit, push, pull request, create PR, git status, git diff, rebase, stash, branch, merge, release, tag, changelog, semver, cherry-pick, bisect, worktree, lazygit, gh, delta

**Use For:**
- Commit, push, and branch management (dispatched to background Sonnet agent)
- PR creation with contextual titles and descriptions
- Release workflows - tagging, GitHub releases, changelog generation
- Semantic versioning analysis from Conventional Commits
- Interactive git operations (lazygit)
- GitHub CLI (gh) commands
- Safety-tiered operations (read-only inline, safe writes dispatched, destructive with preflight)

**Agent:** git-agent (model: sonnet, background)

**References:** rebase-patterns.md, stash-patterns.md, advanced-git.md

---

### python-env

**Triggers:** uv, venv, pip, pyproject, python environment

**Use For:**
- Fast environment setup with uv
- Virtual environment creation
- Dependency management
- pyproject.toml configuration

**References:** pyproject-patterns.md, dependency-management.md

---

### task-runner

**Triggers:** just, justfile, run tests, build project, list tasks

**Use For:**
- Project task execution
- Justfile configuration
- Common development commands

---

### doc-scanner

**Triggers:** AGENTS.md, conventions, scan docs, project documentation

**Use For:**
- Finding project documentation
- Synthesizing AI agent instructions
- Consolidating multiple doc files
- Creating AGENTS.md

**References:** file-patterns.md, templates.md

---

### project-planner

**Triggers:** plan, sync plan, track, project planning

**Use For:**
- Session state with /save and /sync
- Progress tracking
- Context preservation

---

## Selection Guide

### By File Type

| Working With | Skill |
|--------------|-------|
| JSON files | data-processing |
| YAML/TOML | data-processing |
| SQL databases | sql-ops, postgres-ops, sqlite-ops |
| Go | go-ops |
| Rust | rust-ops |
| TypeScript/JS | typescript-ops, javascript-ops, file-search, structural-search |
| React/Next.js | react-ops, typescript-ops |
| Vue/Nuxt | vue-ops, typescript-ops |
| Astro | astro-ops, typescript-ops |
| PHP/Laravel | laravel-ops |
| Python | python-env, structural-search |
| API design | api-design-ops, rest-ops |
| Docker/containers | docker-ops, container-orchestration |
| CI/CD | ci-cd-ops, git-ops |
| CSS/Tailwind | tailwind-ops |
| Nginx/web server | nginx-ops |
| Auth/security | auth-ops, security-ops |
| Monitoring | monitoring-ops, python-observability-ops |

### By Task

| Task | Skill |
|------|-------|
| Find files by name | file-search |
| Search code content | file-search |
| Replace across files | find-replace |
| Count lines of code | code-stats |
| Compare code changes | code-stats |
| Process JSON/YAML | data-processing |
| Git operations | git-ops |
| Set up Python project | python-env |
| Run project tasks | task-runner |
| Find project docs | doc-scanner |
| Plan implementation | project-planner |
| Debug a crash/leak | debug-ops |
| Configure nginx | nginx-ops |
| Set up auth | auth-ops |
| Add monitoring | monitoring-ops |

### By Complexity

**Quick Lookups (< 1 min):**
- rest-ops: Status code lookup
- sql-ops: CTE syntax
- tailwind-ops: Breakpoint reference
- file-search: Basic fd/rg commands

**Medium Tasks (1-5 min):**
- find-replace: Batch replacements
- data-processing: JSON transformations
- git-ops: Rebase, PR creation, release workflows
- python-env: Project setup

**Complex Workflows (5+ min):**
- structural-search: Security scans
- doc-scanner: Documentation consolidation
- project-planner: Session planning
- migrate-ops: Framework version upgrades
- refactor-ops: Large-scale refactoring

---

### migrate-ops

**Triggers:** migrate, upgrade, migration, version upgrade, breaking changes, codemod, rector, jscodeshift, framework upgrade, dependency audit

**Use For:**
- Framework version upgrades (React 18→19, Vue 2→3, Next.js Pages→App Router, Laravel 10→11)
- Language upgrades (Python 3.9→3.13, Node 18→22, TypeScript 4→5, Go, Rust editions)
- Dependency audit and upgrade workflows (npm audit, pip-audit, cargo audit, govulncheck)
- Breaking change detection and codemod application
- Rollback strategies and pre-migration checklists

**References:** framework-upgrades.md, language-upgrades.md, dependency-management.md

---

### refactor-ops

**Triggers:** refactor, extract function, extract component, code smell, dead code, rename, restructure, technical debt, cyclomatic complexity

**Use For:**
- Extract patterns (function, component, hook, module, class, configuration)
- Code smell detection (long functions, god objects, feature envy, duplicate code)
- Dead code detection and removal workflows
- Test-driven refactoring methodology (characterization tests, strangler fig)
- Safe rename and move operations across codebase

**References:** extract-patterns.md, code-smells.md, safe-methodology.md

---

### scaffold

**Triggers:** scaffold, boilerplate, project template, init project, create project, starter, new project, setup project

**Use For:**
- API project scaffolding (FastAPI, Express, Gin, Axum)
- Web app scaffolding (Next.js, Nuxt, Astro, SvelteKit)
- CLI tool scaffolding (Typer, Commander, Cobra, Clap)
- Library/package scaffolding (npm, PyPI, crate, Go module)
- Monorepo scaffolding (Turborepo, Nx, workspaces)
- Common additions (CI/CD, Docker, linting, pre-commit)

**References:** api-templates.md, frontend-templates.md, tooling-templates.md

---

### perf-ops

**Triggers:** performance, profiling, flamegraph, memory leak, bundle size, load test, benchmark, slow, latency, optimization, pprof, py-spy, clinic.js

**Use For:**
- CPU profiling (flamegraphs, pprof, py-spy, clinic.js, samply)
- Memory profiling (heaptrack, memray, Chrome DevTools, Valgrind)
- Bundle analysis (webpack-bundle-analyzer, source-map-explorer)
- Load testing (k6, artillery, vegeta, locust)
- Benchmarking (hyperfine, criterion, pytest-benchmark, vitest bench)
- Optimization patterns (caching, lazy loading, connection pooling)

**References:** cpu-memory-profiling.md, load-testing.md, optimization-patterns.md

---

### log-ops

**Triggers:** log analysis, JSONL, log file, parse logs, search logs, lnav, jq logs, structured logs, log aggregation, timeline reconstruction, cross-log correlation

**Use For:**
- JSONL streaming extraction and aggregation with jq
- Two-stage rg+jq pipelines for large log files
- Timeline reconstruction from log timestamps
- Cross-log correlation across multiple files
- Agent conversation log analysis (tool calls, errors, phases)
- Cross-directory log searching (fd + rg + jq composition)
- Interactive log exploration with lnav

**References:** jsonl-patterns.md, analysis-workflows.md, tool-setup.md

---

## When to Use Skills vs Agents

**Use a Skill when:**
- You need quick reference (syntax, patterns)
- Task is well-defined (replace X with Y)
- Looking up how to do something
- Executing a known workflow

**Use an Agent when:**
- Requires reasoning or decisions
- Complex problem-solving needed
- Multiple approaches to evaluate
- Architecture or optimization

**Example:**
- "What's the HTTP status for unauthorized?" → rest-ops (skill)
- "Design authentication for my API" → general-purpose agent preloading auth-ops + the relevant framework `-ops` skill
