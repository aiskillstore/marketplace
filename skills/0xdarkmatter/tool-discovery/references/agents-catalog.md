# Agents Catalog

Complete reference for all available agents in the Task tool.

## Language Experts

### python-expert

**Triggers:** python, py, pythonic, PEP, async, pytest, django, flask

**Capabilities:**
- Advanced Python features (decorators, metaclasses, descriptors)
- Async programming (asyncio, aiohttp, async generators)
- Testing strategies (pytest, mocking, fixtures)
- Performance optimization and profiling
- Clean, idiomatic Python code

**Best For:**
- Complex Python architecture decisions
- Performance optimization
- Testing strategy design
- Debugging difficult Python issues

---

### javascript-expert

**Triggers:** javascript, js, node, es6, esm, commonjs, npm

**Capabilities:**
- Modern JavaScript (ES2015+)
- Async patterns (Promises, async/await)
- Module systems (ESM, CommonJS)
- Event loop and concurrency
- V8 optimization patterns

**Best For:**
- JavaScript modernization
- Async code architecture
- Performance optimization
- Node.js development

---

### typescript-expert

**Triggers:** typescript, ts, types, generics, interface, type guard

**Capabilities:**
- Advanced type system (generics, conditional types)
- Utility types and type manipulation
- Declaration files (.d.ts)
- Strict mode and type safety
- Type-level programming

**Best For:**
- Complex type definitions
- Type-safe API design
- Generic library development
- Migration from JavaScript

---

### bash-expert

**Triggers:** bash, shell, script, zsh, cli

**Capabilities:**
- Defensive bash scripting
- Error handling and traps
- CI/CD pipeline scripts
- System utilities
- Cross-platform considerations

**Best For:**
- Production automation scripts
- CI/CD pipelines
- System administration
- Build scripts

---

## Framework Experts

### react-expert

**Triggers:** react, hooks, useState, useEffect, jsx, tsx

**Capabilities:**
- React hooks (built-in and custom)
- State management patterns
- Server Components and RSC
- Performance optimization
- Component architecture

**Best For:**
- React application architecture
- Performance bottlenecks
- State management design
- Migration to modern React

---

### vue-expert

**Triggers:** vue, vuejs, composition api, pinia, vue router

**Capabilities:**
- Vue 3 Composition API
- Pinia state management
- Vue Router patterns
- Reactivity system internals
- Component design

**Best For:**
- Vue 3 migration
- State management setup
- Complex component patterns
- SSR with Nuxt

---

### laravel-expert

**Triggers:** laravel, eloquent, php, artisan

**Capabilities:**
- Laravel framework patterns
- Eloquent ORM
- Testing with PHPUnit
- Queue and job handling
- API development

**Best For:**
- Laravel application design
- Database optimization
- Testing strategy
- API architecture

---

### astro-expert

**Triggers:** astro, islands, content collections, cloudflare workers

**Capabilities:**
- Astro architecture (SSR/SSG/hybrid)
- Islands architecture
- Content Collections
- Cloudflare Workers deployment
- Performance optimization

**Best For:**
- Astro project setup
- Deployment to Cloudflare
- Content management
- Performance tuning

---

## Infrastructure Experts

### postgres-expert

**Triggers:** postgres, postgresql, pg, sql optimization

**Capabilities:**
- Query optimization
- Index strategies
- Execution plan analysis
- Connection pooling
- Replication setup

**Best For:**
- Slow query optimization
- Index design
- Database architecture
- Performance tuning

---

### sql-expert

**Triggers:** sql, query, database, join, subquery

**Capabilities:**
- Complex query writing
- Query optimization
- Index strategies
- Data modeling
- Cross-database patterns

**Best For:**
- Complex query construction
- Query debugging
- Data modeling
- Performance analysis

---

### cloudflare-expert

**Triggers:** cloudflare, workers, pages, kv, d1, r2

**Capabilities:**
- Workers development
- KV/D1/R2 storage
- Edge computing patterns
- Security configuration
- DNS and CDN setup

**Best For:**
- Cloudflare Workers apps
- Edge optimization
- Storage architecture
- Security hardening

---

### wrangler-expert

**Triggers:** wrangler, deploy, cloudflare cli

**Capabilities:**
- Wrangler CLI configuration
- Multi-environment deployment
- Binding configuration
- Troubleshooting deployments
- CI/CD integration

**Best For:**
- Deployment issues
- Wrangler configuration
- Environment setup
- CI/CD pipelines

---

### aws-fargate-ecs-expert

**Triggers:** ecs, fargate, aws containers, task definition

**Capabilities:**
- ECS/Fargate deployment
- Task definitions
- Service Auto Scaling
- Networking (awsvpc)
- Logging (FireLens)

**Best For:**
- Container deployment on AWS
- ECS architecture
- Scaling strategy
- Cost optimization

---

## Specialized Experts

### firecrawl-expert

**Triggers:** firecrawl, web scraping, crawl, anti-bot

**Capabilities:**
- Web scraping strategies
- Anti-bot bypass
- Dynamic content handling
- Structured data extraction
- API integration

**Best For:**
- Complex scraping tasks
- Blocked site access
- Data extraction pipelines
- Crawl architecture

---

### payloadcms-expert

**Triggers:** payload, payload cms, headless cms

**Capabilities:**
- Payload CMS architecture
- Collection configuration
- Access control design
- Media handling
- Multi-tenant setup

**Best For:**
- Payload project setup
- Access control design
- Schema planning
- Integration patterns

---

### craftcms-expert

**Triggers:** craft, craftcms, twig

**Capabilities:**
- Craft CMS development
- Twig templates
- Plugin development
- Matrix fields
- GraphQL API

**Best For:**
- Craft CMS projects
- Template development
- Custom field types
- Content modeling

---

### cypress-expert

**Triggers:** cypress, e2e, component testing, test runner

**Capabilities:**
- E2E test architecture
- Component testing
- Custom commands
- Network stubbing
- CI integration

**Best For:**
- E2E test suite setup
- Test architecture
- Flaky test debugging
- CI optimization

---

### playwright-roulette-expert

**Triggers:** playwright, browser automation, casino, roulette

**Capabilities:**
- Playwright automation
- DOM manipulation
- Coordinate-based clicking
- Browser process management
- Viewport configuration

**Best For:**
- Browser automation
- Game automation
- Complex DOM interactions
- Process management

---

### project-organizer

**Triggers:** restructure, organize, cleanup, directory

**Capabilities:**
- Project structure analysis
- Directory reorganization
- Old file cleanup
- Git-aware operations
- Best practice structure

**Best For:**
- Project restructuring
- Codebase cleanup
- Structure standardization
- Tech debt reduction

---

## Built-in Agents

### Explore

**Triggers:** where is, find, locate, codebase search

**Capabilities:**
- Fast codebase exploration
- Pattern matching
- File discovery
- Quick answers

**Best For:**
- "Where is X defined?"
- "Find files matching Y"
- Quick codebase questions

---

### Plan

**Triggers:** plan, design, architect, strategy

**Capabilities:**
- Implementation planning
- Architecture design
- File identification
- Trade-off analysis

**Best For:**
- Feature planning
- Architectural decisions
- Implementation strategy

---

### general-purpose

**Triggers:** multi-step, complex, research

**Capabilities:**
- Autonomous research
- Multi-step tasks
- Code search
- Tool coordination

**Best For:**
- Complex investigations
- Open-ended research
- Multi-step operations

---

### claude-code-guide

**Triggers:** how to use claude code, can claude code, does claude code

**Capabilities:**
- Claude Code documentation
- Feature explanations
- Hook configuration
- MCP server setup
- Agent SDK guidance

**Best For:**
- Claude Code questions
- Configuration help
- Feature discovery
- SDK usage

---

## Selection Guide

| Need | First Try | Then Try |
|------|-----------|----------|
| "How to write X in Python" | python-expert | - |
| "Optimize this query" | postgres-expert | sql-expert |
| "Find where X is defined" | Explore | general-purpose |
| "Plan feature implementation" | Plan | general-purpose |
| "Scrape this website" | firecrawl-expert | - |
| "Deploy to Cloudflare" | wrangler-expert | cloudflare-expert |
| "Fix React performance" | react-expert | - |
| "Write E2E tests" | cypress-expert | - |
| "Restructure project" | project-organizer | - |
