# Agent Pattern Mappings

Patterns that suggest specific agents.

## Code Quality Agents

### code-reviewer

**Signals:**
- .github/PULL_REQUEST_TEMPLATE.md present
- CODEOWNERS file exists
- PR workflow in CI
- Team size > 1 (multiple contributors in git log)

**Rationale:** PR workflow detected but no automated review. An agent would provide consistent code review.

**Template context:**
```yaml
agent: code-reviewer
purpose: Review code changes for quality and consistency
tools: Read, Grep, Glob
model: sonnet
detected:
  pr_template: {present|absent}
  style_guide: {detected|none}
  test_required: {yes|no}
```

**Priority:** P1 for team projects

---

### security-review

**Signals:**
- Auth middleware or decorators
- JWT/OAuth patterns
- Password handling code
- API key management
- .env file with secrets pattern

**Rationale:** Security-sensitive code detected. An agent would help identify vulnerabilities.

**Template context:**
```yaml
agent: security-review
purpose: Analyze code for security vulnerabilities
tools: Read, Grep, Glob
model: opus
detected:
  auth_type: {jwt|oauth|session|basic}
  secrets_management: {env|vault|config}
  sensitive_areas: {list of paths}
```

**Priority:** P1 for auth-heavy projects

---

## API Agents

### api-testing

**Signals:**
- Express/Fastify/Flask routes
- OpenAPI/Swagger spec
- REST endpoint patterns
- GraphQL schema

**Rationale:** API endpoints detected. An agent would help test and validate API contracts.

**Template context:**
```yaml
agent: api-testing
purpose: Test API endpoints and validate contracts
tools: Read, Grep, Bash, WebFetch
model: sonnet
detected:
  api_style: {rest|graphql|grpc}
  framework: {express|fastify|flask|fastapi}
  openapi: {present|absent}
  endpoints_count: {number}
```

**Priority:** P1 if no OpenAPI tests exist

---

### api-documenter

**Signals:**
- Many undocumented endpoints
- OpenAPI spec outdated or missing
- GraphQL schema without descriptions

**Rationale:** API exists but documentation is sparse. An agent would generate and maintain API docs.

**Template context:**
```yaml
agent: api-documenter
purpose: Generate and maintain API documentation
tools: Read, Grep, Glob, Write
model: sonnet
detected:
  undocumented_count: {number}
  doc_format: {openapi|graphql|none}
```

**Priority:** P2

---

## Infrastructure Agents

### infra-analyzer

**Signals:**
- terraform/ directory
- CloudFormation templates
- kubernetes/ manifests
- docker-compose.yml with multiple services

**Rationale:** Infrastructure as code detected. An agent would help analyze and optimize infrastructure.

**Template context:**
```yaml
agent: infra-analyzer
purpose: Analyze and optimize infrastructure configuration
tools: Read, Grep, Glob
model: sonnet
detected:
  iac_tool: {terraform|cloudformation|pulumi}
  cloud: {aws|gcp|azure|multi}
  complexity: {simple|moderate|complex}
```

**Priority:** P2

---

## Data Agents

### data-analyzer

**Signals:**
- Prisma schema with many models
- Complex SQL queries
- Data pipeline code
- Analytics/reporting modules

**Rationale:** Data-heavy application detected. An agent would help with queries and data analysis.

**Template context:**
```yaml
agent: data-analyzer
purpose: Analyze data models and optimize queries
tools: Read, Grep, Glob, Bash
model: sonnet
detected:
  orm: {prisma|typeorm|sqlalchemy}
  models_count: {number}
  query_complexity: {simple|moderate|complex}
```

**Priority:** P2 if > 10 models

---

## Specialist Agents

### domain-expert

**Signals:**
- Domain-specific terminology in code
- Industry patterns (healthcare, finance, etc.)
- Regulatory compliance code
- Complex business logic

**Rationale:** Domain-specific codebase detected. An agent with domain knowledge would help.

**Template context:**
```yaml
agent: domain-expert
purpose: Provide domain expertise for {domain}
tools: Read, Grep, Glob
model: opus
detected:
  domain: {healthcare|finance|legal|etc}
  regulations: {hipaa|gdpr|pci|etc}
  terminology: {list}
```

**Priority:** P1 for regulated industries

---

## When to Prefer Agent Over Skill

Choose agent when task involves:
- **Analysis**: Understanding code before acting
- **Judgment**: Decisions based on context
- **Multi-step**: Complex workflows with branches
- **Delegation**: "Figure out the right approach"

Choose skill when task is:
- **Predictable**: Same steps every time
- **Trigger-based**: User explicitly requests it
- **Simple**: < 5 steps, linear flow
- **Templated**: Fill-in-the-blank generation

## Gap Check

Before suggesting any agent:

1. Check `.claude/agents/` for existing coverage
2. Verify built-in agents (explore, plan, general-purpose) don't suffice
3. Confirm task benefits from specialized prompt
4. Ensure task is complex enough to warrant agent
