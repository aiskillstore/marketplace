# Suggesting Tooling Reference

Detailed pattern definitions and matching rules.

## Analysis Heuristics

### Language Detection

| Extension | Language | Weight |
|-----------|----------|--------|
| .ts, .tsx | TypeScript | High |
| .js, .jsx | JavaScript | High |
| .py | Python | High |
| .go | Go | High |
| .rs | Rust | High |
| .java | Java | High |
| .cs | C# | High |
| .rb | Ruby | Medium |
| .php | PHP | Medium |

Count files, determine primary language by majority.

### Framework Detection

| File/Pattern | Framework |
|--------------|-----------|
| package.json + react | React |
| package.json + vue | Vue |
| package.json + angular | Angular |
| package.json + express | Express |
| package.json + fastify | Fastify |
| package.json + nest | NestJS |
| requirements.txt + django | Django |
| requirements.txt + flask | Flask |
| requirements.txt + fastapi | FastAPI |
| go.mod + gin | Gin |
| Cargo.toml + actix | Actix |
| *.csproj + AspNetCore | ASP.NET Core |

### Workflow Detection

| Signal | Workflow Type |
|--------|---------------|
| .github/workflows/ | GitHub Actions CI |
| .gitlab-ci.yml | GitLab CI |
| Jenkinsfile | Jenkins CI |
| .circleci/ | CircleCI |
| Dockerfile | Containerization |
| docker-compose.yml | Multi-container |
| kubernetes/, k8s/ | Kubernetes |
| terraform/ | Infrastructure as Code |
| .pre-commit-config.yaml | Pre-commit hooks |

### Test Detection

| Signal | Test Framework |
|--------|----------------|
| jest.config.* | Jest |
| vitest.config.* | Vitest |
| pytest.ini, conftest.py | Pytest |
| .mocharc.* | Mocha |
| karma.conf.* | Karma |
| __tests__/, test/, tests/ | Test directory |
| *.test.*, *.spec.* | Test files |

## Suggestion Rules

### When to Suggest Skills

Skills are best for:
- Repetitive, well-defined tasks
- Single-step or simple workflows
- Tasks user triggers frequently
- Automation with predictable output

**Suggest skill when:**
- Pattern detected but no existing skill covers it
- Task is triggered manually today
- Low complexity (< 5 steps)

### When to Suggest Agents

Agents are best for:
- Multi-step, autonomous tasks
- Tasks requiring judgment
- Complex analysis or review
- Read-heavy operations

**Suggest agent when:**
- Task requires multiple tool types
- Output depends on analysis
- Human would delegate this task
- Task benefits from specialized prompt

### Skill vs Agent Decision Tree

```
Is task repetitive and predictable?
├─ Yes → Skill
└─ No
   ├─ Does it require analysis/judgment?
   │  ├─ Yes → Agent
   │  └─ No → Skill with options
   └─ Is it multi-step with branches?
      ├─ Yes → Agent
      └─ No → Skill
```

## Priority Assignment

### P1 - High Impact

Suggest as P1 when:
- Core workflow has no automation
- Task is performed daily
- Significant time savings
- Reduces error risk

Examples:
- Testing skill when tests exist but no helper
- Code reviewer when PRs are manual

### P2 - Medium Impact

Suggest as P2 when:
- Workflow exists but could improve
- Task is performed weekly
- Moderate time savings

Examples:
- Deployment skill when manual deploys work
- Documentation skill when docs are sparse

### P3 - Nice to Have

Suggest as P3 when:
- Edge case or optional workflow
- Task is infrequent
- Small improvement

Examples:
- Linting skill when pre-commit exists
- Migration skill when schema rarely changes

## Gap Analysis

### Existing Tooling Check

Before suggesting, verify no overlap:

```bash
# List existing skills
ls .claude/skills/

# List existing agents
ls .claude/agents/

# Check for similar functionality
grep -r "description:" .claude/skills/*/SKILL.md
grep -r "description:" .claude/agents/*.md
```

### Overlap Detection

If existing tooling covers similar ground:
- Skip suggestion entirely
- Or suggest enhancement instead of new tooling

## Generation Context

### Passing Context to creating-skills

Include detected information:

```
Context for skill generation:
- Project: {name}
- Language: {primary language}
- Framework: {detected framework}
- Test runner: {detected}
- Build tool: {detected}
- Related files: {list}
```

### Passing Context to creating-agents

Include detected information:

```
Context for agent generation:
- Project: {name}
- Architecture: {detected pattern}
- API style: {REST/GraphQL/etc}
- Auth pattern: {detected}
- CI/CD: {detected}
- Focus area: {specific concern}
```

## Anti-Patterns

### Avoid These Suggestions

| Bad Suggestion | Why |
|----------------|-----|
| Generic "coding" skill | Too broad, not actionable |
| Agent for simple tasks | Overkill, use skill |
| Duplicate existing tool | Check first |
| Suggest without evidence | Base on detected patterns |
| Too many suggestions | Limit to 5 per category |

### Red Flags

Skip suggestion if:
- No clear signal in codebase
- Existing tooling adequate
- Would duplicate Claude's built-in capabilities
- Low confidence in pattern match
