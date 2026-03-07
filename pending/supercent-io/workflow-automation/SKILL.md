---
name: workflow-automation
description: Automate repetitive development tasks and workflows. Use when creating build scripts, automating deployments, or setting up development workflows. Handles npm scripts, Makefile, GitHub Actions workflows, and task automation.
metadata:
  tags: automation, scripts, workflow, npm-scripts, Makefile, task-runner
  platforms: Claude, ChatGPT, Gemini
---


# Workflow Automation


## When to use this skill

- **Repetitive tasks**: running the same commands every time
- **Complex builds**: multi-step build processes
- **Team onboarding**: a consistent development environment

## Instructions

### Step 1: npm scripts

**package.json**:
```json
{
  "scripts": {
    "dev": "nodemon src/index.ts",
    "build": "tsc && vite build",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,json}\"",
    "type-check": "tsc --noEmit",
    "pre-commit": "lint-staged",
    "prepare": "husky install",
    "clean": "rm -rf dist node_modules",
    "reset": "npm run clean && npm install",
    "docker:build": "docker build -t myapp .",
    "docker:run": "docker run -p 3000:3000 myapp"
  }
}
```

### Step 2: Makefile

**Makefile**:
```makefile
.PHONY: help install dev build test clean docker

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	npm install

dev: ## Start development server
	npm run dev

build: ## Build for production
	npm run build

test: ## Run all tests
	npm test

lint: ## Run linter
	npm run lint

lint-fix: ## Fix linting issues
	npm run lint:fix

clean: ## Clean build artifacts
	rm -rf dist coverage

docker-build: ## Build Docker image
	docker build -t myapp:latest .

docker-run: ## Run Docker container
	docker run -d -p 3000:3000 --name myapp myapp:latest

deploy: build ## Deploy to production
	@echo "Deploying to production..."
	./scripts/deploy.sh production

ci: lint test build ## Run CI pipeline locally
	@echo "✅ CI pipeline passed!"
```

**Usage**:
```bash
make help        # Show all commands
make dev         # Start development
make ci          # Run full CI locally
```

### Step 3: Husky + lint-staged (Git Hooks)

**package.json**:
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": [
      "prettier --write"
    ]
  }
}
```

**.husky/pre-commit**:
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "Running pre-commit checks..."

# Lint staged files
npx lint-staged

# Type check
npm run type-check

# Run tests related to changed files
npm test -- --onlyChanged

echo "✅ Pre-commit checks passed!"
```

### Step 4: Task Runner scripts

**scripts/dev-setup.sh**:
```bash
#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Check prerequisites
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "⚠️ Please update .env with your configuration"
fi

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for database
echo "⏳ Waiting for database..."
./scripts/wait-for-it.sh localhost:5432 --timeout=30

# Run migrations
echo "🗄️ Running database migrations..."
npm run migrate

# Seed data (optional)
read -p "Seed database with sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm run seed
fi

echo "✅ Development environment ready!"
echo "Run 'make dev' to start the development server"
```

**scripts/deploy.sh**:
```bash
#!/bin/bash
set -e

ENV=$1

if [ -z "$ENV" ]; then
    echo "Usage: ./deploy.sh [staging|production]"
    exit 1
fi

echo "🚀 Deploying to $ENV..."

# Build
echo "📦 Building application..."
npm run build

# Run tests
echo "🧪 Running tests..."
npm test

# Deploy based on environment
if [ "$ENV" == "production" ]; then
    echo "🌍 Deploying to production..."
    # Production deployment logic
    ssh production "cd /app && git pull && npm install && npm run build && pm2 restart all"
elif [ "$ENV" == "staging" ]; then
    echo "🧪 Deploying to staging..."
    # Staging deployment logic
    ssh staging "cd /app && git pull && npm install && npm run build && pm2 restart all"
fi

echo "✅ Deployment to $ENV completed!"
```

### Step 5: GitHub Actions workflow automation

**.github/workflows/ci.yml**:
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Output format

```
project/
├── scripts/
│   ├── dev-setup.sh
│   ├── deploy.sh
│   ├── test.sh
│   └── cleanup.sh
├── Makefile
├── package.json
└── .husky/
    ├── pre-commit
    └── pre-push
```

## Constraints

### Required rules (MUST)

1. **Idempotency**: safe to run scripts multiple times
2. **Error handling**: clear messages on failure
3. **Documentation**: comments on how to use the scripts

### Prohibited items (MUST NOT)

1. **Hardcoded secrets**: do not include passwords or API keys in scripts
2. **Destructive commands**: do not run rm -rf without confirmation

## Best practices

1. **Use Make**: platform-agnostic interface
2. **Git Hooks**: automated quality checks
3. **CI/CD**: automated with GitHub Actions

## References

- [npm scripts](https://docs.npmjs.com/cli/v9/using-npm/scripts)
- [Make Tutorial](https://makefiletutorial.com/)
- [Husky](https://typicode.github.io/husky/)

## Metadata

### Version
-- **Current version**: 1.0.0
-- **Last updated**: 2025-01-01
-- **Compatible platforms**: Claude, ChatGPT, Gemini

### Tags
`#automation` `#scripts` `#workflow` `#npm-scripts` `#Makefile` `#utilities`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
