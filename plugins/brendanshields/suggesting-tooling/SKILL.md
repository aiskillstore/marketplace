---
name: suggesting-tooling
description: |
  Analyzes a codebase and suggests custom Claude Code skills and subagents to improve
  development workflow. Use when user wants tooling suggestions, automation ideas, or
  asks "what skills would help this project".
---

# Suggesting Tooling

Analyzes codebases to suggest custom skills and agents for workflow automation.

## Quick Start

1. Scan codebase for patterns (languages, frameworks, workflows)
2. Match patterns to skill/agent templates
3. Present suggestions with rationale
4. Generate approved tooling using creating-skills/creating-agents

## Workflow

```
Progress:
- [ ] Analyze codebase patterns
- [ ] Match to tooling templates
- [ ] Present suggestions
- [ ] Generate approved items
```

### Step 1: Analyze Codebase

Run lightweight analysis:

```bash
# Language detection
find . -type f -name "*.ts" -o -name "*.js" -o -name "*.py" | head -100

# Framework detection
ls package.json pyproject.toml Cargo.toml go.mod 2>/dev/null

# Workflow detection
ls .github/workflows/ .gitlab-ci.yml Dockerfile 2>/dev/null

# Existing tooling
ls .claude/skills/ .claude/agents/ 2>/dev/null
```

Collect:
- Primary language(s)
- Framework(s) in use
- Build/test tooling
- CI/CD setup
- Existing .claude/ configuration

### Step 2: Pattern Matching

Match detected patterns to suggestions:

| Signal | Skill Suggestion | Agent Suggestion |
|--------|------------------|------------------|
| Jest/Pytest/Mocha | testing-code | - |
| REST routes | - | api-testing |
| Prisma/migrations | db-migrations | - |
| Dockerfile | deploying-code | - |
| ESLint/Prettier | linting-code | - |
| Auth patterns | - | security-review |
| Many .md files | documenting-code | - |
| PR workflow | - | code-reviewer |

See [patterns/skills.md](patterns/skills.md) and [patterns/agents.md](patterns/agents.md) for complete mappings.

### Step 3: Present Suggestions

Format suggestions for user review:

```markdown
## Tooling Suggestions for {project}

Based on analysis of your codebase:
- Language: {detected}
- Framework: {detected}
- Existing tooling: {count} skills, {count} agents

### Recommended Skills

| # | Skill | Why | Priority |
|---|-------|-----|----------|
| 1 | {name} | {rationale} | P1 |
| 2 | {name} | {rationale} | P2 |

### Recommended Agents

| # | Agent | Why | Priority |
|---|-------|-----|----------|
| 1 | {name} | {rationale} | P1 |
```

Then ask user which to generate.

### Step 4: Generate Tooling

For each approved item:

**Skills** - Invoke creating-skills:
```
Use the creating-skills skill to create a {name} skill.

Purpose: {rationale}
Detected context:
- Framework: {framework}
- Test runner: {runner}
- Patterns: {patterns}

Generate a focused skill for this project.
```

**Agents** - Invoke creating-agents:
```
Use the creating-agents skill to create a {name} agent.

Purpose: {rationale}
Suggested tools: {tools}
Detected context:
- Project type: {type}
- Workflows: {workflows}

Generate a focused agent for this project.
```

## Pattern Categories

### Testing
- **Signals**: jest.config, pytest.ini, mocha, test/ directory
- **Suggest**: testing-code skill
- **Priority**: P1 if tests exist but no skill

### API Development
- **Signals**: Express routes, FastAPI, REST patterns
- **Suggest**: api-testing agent
- **Priority**: P1 if API-heavy project

### Database
- **Signals**: Prisma, TypeORM, migrations/
- **Suggest**: db-migrations skill
- **Priority**: P2

### DevOps
- **Signals**: Dockerfile, docker-compose, CI configs
- **Suggest**: deploying-code skill
- **Priority**: P2 if no deployment automation

### Code Quality
- **Signals**: ESLint, Prettier, pre-commit
- **Suggest**: linting-code skill
- **Priority**: P3

### Security
- **Signals**: Auth middleware, JWT, OAuth
- **Suggest**: security-review agent
- **Priority**: P1 for auth-heavy projects

See [reference.md](reference.md) for detailed pattern definitions.

## Gap Analysis

Compare detected needs against existing .claude/ configuration:

```
Detected workflows:     Existing tooling:
- Testing (Jest)        - (none)
- API (Express)         - (none)
- CI (GitHub Actions)   - (none)

Gaps: testing, api-testing, deployment
```

Only suggest tooling that fills gaps.

## Output Format

After generation, report:

```markdown
## Tooling Created

| Type | Name | Location |
|------|------|----------|
| Skill | testing-code | .claude/skills/testing-code/ |
| Agent | code-reviewer | .claude/agents/code-reviewer.md |

### Restart Required

New skills and agents require a Claude restart to be available.

To continue where you left off:
\`\`\`bash
claude --continue
\`\`\`

### Next Steps

1. Restart Claude to load new tooling
2. Run `claude --continue` to resume
3. Review generated tooling in .claude/
4. Test skills with sample workflows
```

## Limits

- Maximum 5 suggestions per category
- Require explicit approval before generating
- Skip suggestions for existing tooling
- Prioritize by impact (P1 first)
