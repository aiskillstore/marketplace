# Skill Pattern Mappings

Patterns that suggest specific skills.

## Testing Skills

### testing-code

**Signals:**
- jest.config.js/ts present
- vitest.config.js/ts present
- pytest.ini or conftest.py present
- test/ or __tests__/ directory exists
- *.test.* or *.spec.* files present

**Rationale:** Test framework detected but no testing skill exists. A skill would help run tests, analyze failures, and suggest fixes.

**Template context:**
```yaml
skill: testing-code
purpose: Run tests and analyze results
triggers:
  - "run tests"
  - "test this"
  - "check tests"
detected:
  framework: {jest|pytest|vitest|mocha}
  test_dir: {path}
  config_file: {path}
```

**Priority:** P1 if test files exist, P2 if only config exists

---

### linting-code

**Signals:**
- .eslintrc.* present
- .prettierrc.* present
- pylint/flake8 in requirements
- .pre-commit-config.yaml present

**Rationale:** Code quality tools detected. A skill would help run linters and fix issues automatically.

**Template context:**
```yaml
skill: linting-code
purpose: Run linters and fix code style
triggers:
  - "lint this"
  - "fix style"
  - "format code"
detected:
  linter: {eslint|prettier|pylint|flake8}
  config_file: {path}
```

**Priority:** P3 (usually covered by pre-commit)

---

### documenting-code

**Signals:**
- docs/ directory with .md files
- README.md over 500 lines
- JSDoc/docstring patterns in code
- typedoc.json or sphinx conf.py

**Rationale:** Documentation exists but may need maintenance. A skill would help generate and update docs.

**Template context:**
```yaml
skill: documenting-code
purpose: Generate and update documentation
triggers:
  - "update docs"
  - "document this"
  - "add jsdoc"
detected:
  doc_tool: {typedoc|sphinx|mkdocs}
  doc_dir: {path}
```

**Priority:** P2 if docs exist, P3 otherwise

---

### deploying-code

**Signals:**
- Dockerfile present
- docker-compose.yml present
- .github/workflows with deploy steps
- kubernetes/ or k8s/ directory

**Rationale:** Deployment infrastructure exists. A skill would help with build and deploy workflows.

**Template context:**
```yaml
skill: deploying-code
purpose: Build and deploy application
triggers:
  - "deploy"
  - "build for production"
  - "release"
detected:
  container: {docker|podman}
  orchestration: {compose|kubernetes|none}
  ci: {github-actions|gitlab-ci|none}
```

**Priority:** P2

---

### db-migrations

**Signals:**
- schema.prisma present
- migrations/ directory
- alembic.ini present
- typeorm migration files

**Rationale:** Database with migrations detected. A skill would help create and run migrations safely.

**Template context:**
```yaml
skill: db-migrations
purpose: Create and run database migrations
triggers:
  - "create migration"
  - "run migrations"
  - "update schema"
detected:
  orm: {prisma|typeorm|alembic|knex}
  migrations_dir: {path}
```

**Priority:** P2

---

### building-components

**Signals:**
- src/components/ directory
- React/Vue/Angular detected
- Storybook config present
- Component file patterns

**Rationale:** Component-based frontend detected. A skill would help scaffold new components consistently.

**Template context:**
```yaml
skill: building-components
purpose: Generate UI components from templates
triggers:
  - "create component"
  - "new component"
  - "scaffold"
detected:
  framework: {react|vue|angular}
  component_dir: {path}
  style: {css|scss|tailwind|styled-components}
```

**Priority:** P2 if many components, P3 otherwise

---

## Gap Check

Before suggesting any skill:

1. Check `.claude/skills/` for existing coverage
2. Verify no built-in Claude capability handles this
3. Confirm at least 2 signals present
4. Ensure task is repetitive (not one-time)
