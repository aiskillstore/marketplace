# Documentation Templates

Use these templates when creating or consolidating project documentation.

## AGENTS.md Template

```markdown
# Project Name - Agent Guide

Brief description of the project and what it does.

## Quick Reference

| Task | Agent | Example Prompt |
|------|-------|----------------|
| Code review | `javascript-expert` | "Review this PR for issues" |
| Database work | `sql-expert` | "Optimize this query" |
| Deployment | `bash-expert` | "Deploy to staging" |

## Primary Agents

### agent-name

**When to use:** Describe scenarios where this agent excels.

**Example prompts:**
- "Example task description 1"
- "Example task description 2"

**Capabilities:**
- Capability 1
- Capability 2

### another-agent

**When to use:** Different scenarios for this agent.

**Example prompts:**
- "Another example prompt"

## Secondary Agents

### situational-agent

**When to use:** Specific situations only.

## Project Structure

```
project/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
└── scripts/       # Utility scripts
```

## Common Workflows

### Development

1. Step one of workflow
2. Step two of workflow
3. Step three of workflow

### Testing

```bash
# Run all tests
npm test

# Run specific test
npm test -- --grep "pattern"
```

### Deployment

```bash
# Build for production
npm run build

# Deploy to staging
npm run deploy:staging
```

## Conventions

- **Naming:** camelCase for functions, PascalCase for classes
- **Files:** kebab-case for file names
- **Commits:** Conventional commits format

## Environment Setup

1. Clone repository
2. Install dependencies: `npm install`
3. Copy `.env.example` to `.env`
4. Start development: `npm run dev`
```

## CLAUDE.md Template

```markdown
# Project Name - Claude Code Workflow

## Project Overview

Brief description of project purpose and architecture.

## Directory Structure

- `src/` - Main source code
- `tests/` - Test suites
- `scripts/` - Automation scripts

## Development Commands

```bash
# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## Code Style

- Use TypeScript strict mode
- Prefer functional patterns
- Document public APIs

## Testing Strategy

- Unit tests in `__tests__/` directories
- Integration tests in `tests/integration/`
- Run `npm test` before committing

## Common Tasks

### Adding a New Feature

1. Create feature branch
2. Implement with tests
3. Update documentation
4. Create PR

### Debugging

- Use `DEBUG=*` environment variable
- Check logs in `logs/` directory

## Architecture Notes

Key architectural decisions and patterns used in this project.
```

## Consolidation Format

When merging multiple docs, use this structure:

```markdown
# Project Name - Agent Guide

<!-- Consolidated from: CLAUDE.md, CURSOR.md, WARP.md -->
<!-- Generated: YYYY-MM-DD -->

## Quick Reference

[Merged quick reference from all sources]

## Primary Agents

[Combined agent recommendations]

## Workflows

### General Workflows

[Platform-agnostic workflows]

### Platform-Specific Notes

<!-- Source: CURSOR.md -->
**Cursor:** Specific keybindings or features

<!-- Source: WARP.md -->
**Warp:** Terminal-specific commands

## Conventions

[Merged conventions - note any conflicts]

## Commands

[Consolidated commands with platform annotations where needed]
```
