---
name: developer-experience
description: Developer Experience specialist for tooling, setup, and workflow optimization.
  Use when setting up projects, reducing friction, improving development workflows,
  or automating repetitive tasks. Focuses on making development joyful and productive.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Developer Experience

This skill optimizes developer workflows, reduces friction, and automates repetitive tasks to make development more productive and enjoyable.

## When to Use This Skill

- When setting up new projects or onboarding developers
- When identifying and eliminating repetitive tasks
- When improving build and test execution times
- When optimizing development workflows
- When creating helpful aliases and shortcuts
- When setting up IDE configurations and tooling

## What This Skill Does

1. **Environment Setup**: Simplifies onboarding to under 5 minutes
2. **Workflow Optimization**: Identifies and automates repetitive tasks
3. **Tooling Enhancement**: Configures IDE settings, git hooks, and CLI commands
4. **Documentation**: Creates setup guides and troubleshooting documentation
5. **Automation**: Creates scripts and commands for common tasks
6. **Friction Reduction**: Eliminates manual steps and improves feedback loops

## How to Use

### Optimize Workflow

```
Analyze the development workflow and suggest improvements
```

```
Set up this project for optimal developer experience
```

### Specific Improvements

```
Create helpful npm scripts for common tasks
```

```
Set up git hooks for code quality checks
```

## Optimization Areas

### Environment Setup

**Goals:**

- Onboarding in under 5 minutes
- Intelligent defaults
- Automated dependency installation
- Helpful error messages
- Clear setup instructions

**Deliverables:**

- README with clear setup steps
- Setup scripts (setup.sh, setup.ps1)
- Environment validation
- Dependency checking
- Configuration templates

### Development Workflows

**Identify Repetitive Tasks:**

- Code generation
- Database migrations
- Test running
- Build processes
- Deployment steps

**Create Automation:**

- npm/yarn scripts
- Makefile commands
- Shell aliases
- Custom CLI tools
- Task runners

### Tooling Enhancement

**IDE Configuration:**

- EditorConfig
- ESLint/Prettier configs
- VS Code settings
- Debug configurations
- Snippet libraries

**Git Hooks:**

- Pre-commit hooks (linting, formatting)
- Commit message validation
- Pre-push hooks (tests)
- Post-merge hooks (dependency updates)

**CLI Commands:**

- Project-specific commands
- Development shortcuts
- Database utilities
- Testing helpers

## Examples

### Example 1: Project Setup Optimization

**Input**: Optimize the setup process for this project

**Output**:

```markdown
## Developer Experience Improvements

### Current Setup Issues
- Manual dependency installation
- No environment validation
- Unclear setup instructions
- Missing development tools

### Improvements

**1. Setup Script**
```bash
#!/bin/bash
# setup.sh
echo "Setting up development environment..."

# Check Node.js version
node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$node_version" -lt 18 ]; then
  echo "Error: Node.js 18+ required"
  exit 1
fi

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Run database migrations
npm run db:migrate

echo "Setup complete! Run 'npm run dev' to start."
```

**2. Enhanced package.json Scripts**

```json
{
  "scripts": {
    "dev": "nodemon src/index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "db:migrate": "knex migrate:latest",
    "db:seed": "knex seed:run",
    "setup": "bash setup.sh"
  }
}
```

**3. Git Hooks**

```bash
# .husky/pre-commit
#!/bin/sh
npm run lint
npm run test
```

### Example 2: Workflow Automation

**Input**: Create shortcuts for common development tasks

**Output**:

```markdown
## Development Shortcuts

### Makefile Commands
```makefile
.PHONY: dev test lint format db-setup

dev:
 npm run dev

test:
 npm test

lint:
 npm run lint

format:
 npm run format

db-setup:
 npm run db:migrate
 npm run db:seed

clean:
 rm -rf node_modules dist .next

install:
 npm install
```

### Shell Aliases

```bash
# Add to ~/.zshrc or ~/.bashrc
alias dev="npm run dev"
alias test="npm test"
alias lint="npm run lint"
alias format="npm run format"
```

### VS Code Tasks

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "npm test",
      "group": "test"
    },
    {
      "label": "Start Dev Server",
      "type": "shell",
      "command": "npm run dev",
      "group": "build",
      "isBackground": true
    }
  ]
}
```

```

## Best Practices

### DX Principles

1. **Invisible When Working**: Great DX is seamless when it works
2. **Obvious When Broken**: Clear error messages when something fails
3. **Fast Feedback**: Quick build/test cycles
4. **Clear Documentation**: Setup guides that actually work
5. **Helpful Defaults**: Sensible configurations out of the box

### Success Metrics

- **Time to First Success**: How long until a new developer runs the app?
- **Manual Steps**: Count of manual steps eliminated
- **Build/Test Time**: Execution time for common tasks
- **Developer Satisfaction**: Feedback on workflow improvements

### Common Improvements

**Fast Feedback:**
- Hot reload for development
- Fast test execution
- Quick build times
- Instant linting feedback

**Clear Errors:**
- Helpful error messages
- Stack traces with context
- Setup validation
- Dependency checking

**Automation:**
- One-command setup
- Automated testing
- Code generation
- Deployment automation

## Reference Files

- **`references/ONBOARDING_GUIDE.template.md`** - Developer onboarding guide template with environment setup, day-by-day tasks, and troubleshooting

## Related Use Cases

- Project setup optimization
- Workflow automation
- Tooling configuration
- Developer onboarding
- Reducing development friction
- Improving build/test times
