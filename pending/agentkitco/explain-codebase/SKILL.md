---
name: explain-codebase
description: Build an onboarding map of an unfamiliar repository covering purpose, entry points, how to run it, main modules, data flow and risky areas, with file references. Use when asked to explain, map or onboard onto a codebase.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Explain an unfamiliar codebase

Goal: give a newcomer a map they can trust, with file references, in a few pages. Every claim must point to a file you read.

## Explore in this order

1. **Purpose and users**: README, package description, docs index. What problem does this solve and for whom?
2. **Run it**: install, run, test commands from manifests, Makefile and CI config. Run the cheap ones (tests, lint) to confirm they work; say which you did not run.
3. **Shape**: directory tree two levels deep (ignore `node_modules`, build output, `.git`). Note language(s), framework(s), monorepo layout.
4. **Entry points**: `main`, server start file, CLI entry, route definitions, scheduled jobs, event handlers, `bin` and `scripts` entries.
5. **Trace one real flow end to end**: pick the most central request, command or event and follow it from entry to storage or output, listing each file and function in order.
6. **Data**: schemas, models, migrations, config files, environment variables the code reads (names only, never values).
7. **External touchpoints**: databases, queues, third-party APIs, auth providers.
8. **Quality signals**: where tests live and what they cover, CI checks, lint rules, areas with TODOs, very large files, recent churn (`git log --since="3 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head`).

## Output

```
# <repo> in one page
Purpose: ...
How to run: <commands, verified or not>
Map: <directory -> responsibility, one line each>
One flow, step by step: <file:function ...>
Data and config: ...
External services: ...
Where to start reading: <3 files in order, with why>
Risky or confusing areas: <file, reason>
Open questions: <what you could not determine>
```

## Rules

- Cite `path:line` or at least `path` for each claim. If you inferred something, label it "inferred".
- Do not describe code you did not open. Do not guess at business context; put it under open questions.
- Never print secret values from `.env` files or config; list variable names only.
- Keep it short: a map, not a tour of every file.
