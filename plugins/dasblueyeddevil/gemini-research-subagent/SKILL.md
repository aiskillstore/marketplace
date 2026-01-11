---
name: Gemini Research Subagent
description: Delegates large-context code analysis to Gemini CLI. Use when analyzing codebases, tracing bugs across files, reviewing architecture, or performing security audits. Gemini reads, Claude implements.
dependencies:
  - gemini-cli
---

# Gemini Research Subagent

You have access to Gemini CLI as a large-context research assistant. **Use Gemini for reading large codebases, use yourself for implementation.**

## When to Invoke Gemini

**ALWAYS use Gemini BEFORE:**
- Reading files >100 lines
- Understanding unfamiliar code areas
- Tracing bugs across multiple files
- Making changes that affect multiple components
- Performing security or architecture reviews

**DO NOT use Gemini for:**
- Simple single-file edits you can handle
- Writing code (that's your job)
- Files you've already analyzed this session

## How to Invoke

```bash
./skills/gemini.agent.wrapper.sh -d "@src/" "Your research question"
```

## Available Roles (loaded from `.gemini/roles/`)
| Role | Command | Use Case |
|------|---------|----------|
| `reviewer` | `-r reviewer` | Code quality, bugs, security |
| `debugger` | `-r debugger` | Bug tracing, root cause analysis |
| `planner` | `-r planner` | Architecture, implementation planning |
| `security` | `-r security` | Security vulnerabilities audit |
| `auditor` | `-r auditor` | Codebase-wide analysis |
| `explainer` | `-r explainer` | Code explanation |
| `migrator` | `-r migrator` | Migration planning |
| `documenter` | `-r documenter` | Documentation generation |
| `dependency-mapper` | `-r dependency-mapper` | Dependency analysis |
| `onboarder` | `-r onboarder` | Onboarding guide |

### Custom Roles
Add custom roles in `.gemini/roles/<name>.md`. Examples:
| Role | Focus |
|------|-------|
| `kotlin-expert` | Kotlin/Android, coroutines |
| `typescript-expert` | TypeScript type safety |
| `python-expert` | Python async, type hints |
| `api-designer` | REST API design |
| `database-expert` | Query optimization |

## Templates

```bash
# Implementation-ready output
./skills/gemini.agent.wrapper.sh -t implement-ready -d "@src/" "Add user profiles"

# Fix-ready output for bugs
./skills/gemini.agent.wrapper.sh -t fix-ready "Login fails with 401"

# Post-implementation verification
./skills/gemini.agent.wrapper.sh -t verify --diff "Added password reset"
```

## Response Format

Gemini returns structured output you can parse:

```
## SUMMARY
[1-2 sentence overview]

## FILES
[file:line references]

## ANALYSIS
[detailed findings]

## RECOMMENDATIONS
[actionable items]
```

## Workflow Pattern

1. **Research**: Invoke Gemini to understand context
2. **Implement**: You write code based on Gemini's analysis
3. **Verify**: Invoke Gemini to verify your changes

## Example Usage

```bash
# Pre-implementation research
./skills/gemini.agent.wrapper.sh -r planner -d "@src/" "How should I add caching?"

# Post-implementation verification
./skills/gemini.agent.wrapper.sh -t verify --diff "Added caching layer"
```
