---
name: tool-discovery
description: "Recommend the right agents and skills for any task. Covers both heavyweight agents (Task tool) and lightweight skills (Skill tool). Triggers on: which agent, which skill, what tool should I use, help me choose, recommend agent, find the right tool."
license: MIT
allowed-tools: "Read Glob"
metadata:
  author: claude-mods
  related-skills: claude-code-ops
---

# Tool Discovery

Recommend the right agents and skills for any task.

## Decision Flowchart

```
Is this a reference/lookup task?
├── YES → Use a SKILL (lightweight, auto-injects)
└── NO → Does it require reasoning/decisions?
         ├── YES → Use an AGENT (heavyweight, spawns subagent)
         └── MAYBE → Check catalogs below
```

**Rule:** Skills = patterns/reference. Agents = decisions/expertise.

## Quick Skill Reference

| Skill | Triggers |
|-------|----------|
| **file-search** | fd, rg, fzf, find files |
| **find-replace** | sd, batch replace |
| **code-stats** | tokei, difft, line counts |
| **data-processing** | jq, yq, json, yaml |
| **structural-search** | ast-grep, sg, ast pattern |
| **git-ops** | git, gh, lazygit, delta, commit, PR, release, rebase |
| **python-env** | uv, venv, pyproject |
| **go-ops** | golang, go, goroutine, channel, context, errgroup, go test |
| **rust-ops** | rust, cargo, ownership, tokio, serde, trait, Result, Option |
| **typescript-ops** | typescript, type system, generics, utility types, Zod |
| **docker-ops** | docker, Dockerfile, docker-compose, multi-stage build |
| **ci-cd-ops** | github actions, CI, CD, pipeline, release, workflow |
| **api-design-ops** | api design, gRPC, GraphQL, REST advanced, protobuf |
| **rest-ops** | http methods, status codes |
| **sql-ops** | cte, window functions |
| **postgres-ops** | postgresql, postgres, EXPLAIN ANALYZE, vacuum, pgbouncer, JSONB, RLS, replication |
| **sqlite-ops** | sqlite, aiosqlite |
| **tailwind-ops** | tailwind, tw classes, dark mode, responsive |
| **mcp-ops** | mcp server, fastmcp, tool handler, transport |
| **react-ops** | react, hooks, useState, next.js, RSC, zustand |
| **vue-ops** | vue, composition api, pinia, nuxt, script setup |
| **javascript-ops** | javascript, node, esm, async/await, event loop |
| **astro-ops** | astro, islands, content collections, partial hydration |
| **laravel-ops** | laravel, eloquent, artisan, sanctum, pest |
| **payloadcms-ops** | payload, payload cms, headless cms, collections |
| **craftcms-ops** | craft, craftcms, twig, matrix fields |
| **asus-router-ops** | asus router, asuswrt, merlin, network hardening |
| **nginx-ops** | nginx, reverse proxy, ssl, load balancer, proxy_pass |
| **cloudflare-ops** | cloudflare, workers, KV, D1, R2, pages, wrangler, edge |
| **cypress-ops** | cypress, e2e, component testing, custom commands, stubbing |
| **bash-ops** | bash, shell scripting, traps, CI scripts, defensive scripting |
| **claude-code-ops** | claude code extensions, skills, agents, hooks, MCP, plugins |
| **auth-ops** | jwt, oauth2, session, rbac, passkey, mfa, login |
| **monitoring-ops** | prometheus, grafana, opentelemetry, SLO, alerting |
| **debug-ops** | debug, crash, memory leak, race condition, bisect |
| **perf-ops** | performance, profiling, flamegraph, bundle size, load test, benchmark |
| **migrate-ops** | migrate, upgrade, breaking changes, codemod, version upgrade |
| **refactor-ops** | refactor, extract, code smell, dead code, rename, restructure |
| **scaffold** | scaffold, boilerplate, project template, init project, new project |
| **log-ops** | JSONL, log analysis, parse logs, lnav, log search, timeline |

## Quick Agent Reference

| Agent | Triggers |
|-------|----------|
| **firecrawl-expert** | web scraping, crawling, anti-bot |
| **project-organizer** | restructure, organize, cleanup |
| **git-agent** | commit, push, PR (dispatched by git-ops) |
| **Explore** | "where is", "find" |
| **Plan** | design, architect |

For Cloudflare/Workers, Cypress/E2E, shell scripting, Claude Code extension work, and CMS/device domains (Payload, Craft, Asus routers), use the matching `-ops` skill (`cloudflare-ops`, `cypress-ops`, `bash-ops`, `claude-code-ops`, `payloadcms-ops`, `craftcms-ops`, `asus-router-ops`). For language/framework work (Python, TypeScript, React, Postgres, etc.), use the matching `-ops` skill — or dispatch `general-purpose` with an instruction to read that skill's SKILL.md first.

## How to Launch

**Skills:**
```
Skill tool → skill: "file-search"
```

**Agents:**
```
Task tool → subagent_type: "firecrawl-expert"
         → prompt: "Your task"
```

## Match by Task Type

| Task | Skill First | Agent If Needed |
|------|-------------|-----------------|
| "How to write a CTE?" | sql-ops | — |
| "Optimize this query" | postgres-ops | — |
| "Find files named X" | file-search | Explore |
| "Set up Python project" | python-env | — |
| "What HTTP status for X?" | rest-ops | — |
| "React Server Components?" | react-ops | — |
| "Vue 3 composable pattern" | vue-ops | — |
| "Configure nginx SSL" | nginx-ops | — |
| "JWT vs session auth" | auth-ops | — |
| "Set up Prometheus" | monitoring-ops | — |
| "Debug memory leak" | debug-ops | — |
| "Scrape a blocked site" | jina-ops | firecrawl-expert |

## Tips

- **Skills are cheaper** - Use for lookups, patterns
- **Agents are powerful** - Use for decisions, optimization
- **Don't over-recommend** - Max 2-3 tools per task

## Additional Resources

For complete catalogs, load:
- `./references/agents-catalog.md` - All agents with capabilities
- `./references/skills-catalog.md` - All skills with details
