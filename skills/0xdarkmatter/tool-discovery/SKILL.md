---
name: tool-discovery
description: "Recommend the right agents and skills for any task. Covers both heavyweight agents (Task tool) and lightweight skills (Skill tool). Triggers on: which agent, which skill, what tool should I use, help me choose, recommend agent, find the right tool."
allowed-tools: "Read Glob"
depends-on: []
related-skills: [claude-code-templates, claude-code-debug]
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
| **git-workflow** | lazygit, gh, delta, rebase |
| **python-env** | uv, venv, pyproject |
| **rest-patterns** | http methods, status codes |
| **sql-patterns** | cte, window functions |
| **sqlite-ops** | sqlite, aiosqlite |
| **tailwind-patterns** | tailwind, tw classes |
| **mcp-patterns** | mcp server, protocol |

## Quick Agent Reference

| Agent | Triggers |
|-------|----------|
| **python-expert** | Python, async, pytest |
| **typescript-expert** | TypeScript, types, generics |
| **react-expert** | React, hooks, state |
| **postgres-expert** | PostgreSQL, query optimization |
| **cloudflare-expert** | Workers, KV, D1, R2 |
| **Explore** | "where is", "find" |
| **Plan** | design, architect |

## How to Launch

**Skills:**
```
Skill tool → skill: "file-search"
```

**Agents:**
```
Task tool → subagent_type: "python-expert"
         → prompt: "Your task"
```

## Match by Task Type

| Task | Skill First | Agent If Needed |
|------|-------------|-----------------|
| "How to write a CTE?" | sql-patterns | sql-expert |
| "Optimize this query" | — | postgres-expert |
| "Find files named X" | file-search | Explore |
| "Set up Python project" | python-env | python-expert |
| "What HTTP status for X?" | rest-patterns | — |

## Tips

- **Skills are cheaper** - Use for lookups, patterns
- **Agents are powerful** - Use for decisions, optimization
- **Don't over-recommend** - Max 2-3 tools per task

## Additional Resources

For complete catalogs, load:
- `./references/agents-catalog.md` - All agents with capabilities
- `./references/skills-catalog.md` - All skills with details
