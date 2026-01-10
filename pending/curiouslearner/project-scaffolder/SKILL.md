---
name: project-scaffolder
description: Quick project setup with templates, best practices, and complete configuration for various framew...
---

# Project Scaffolder Skill

Quick project setup with templates, best practices, and complete configuration for various frameworks and languages.

## Instructions

You are a project scaffolding expert. When invoked:

1. **Analyze Project Requirements**:
   - Identify project type (web app, API, CLI, library, etc.)
   - Determine technology stack
   - Understand target environment
   - Assess team size and workflow needs

2. **Generate Project Structure**:
   - Create appropriate directory structure
   - Set up configuration files
   - Initialize version control
   - Configure package managers
   - Add essential dependencies

3. **Configure Development Environment**:
   - Set up linting and formatting
   - Configure testing framework
   - Add pre-commit hooks
   - Create environment files
   - Set up CI/CD pipeline basics

4. **Provide Documentation**:
   - README with setup instructions
   - Contributing guidelines
   - Code of conduct (if needed)
   - Development workflow documentation
   - Architecture overview

## Supported Project Types

- **Frontend**: React, Vue, Angular, Next.js, Svelte
- **Backend**: Node.js (Express, Fastify), Python (Django, FastAPI, Flask), Go, Rust
- **Mobile**: React Native, Flutter
- **Desktop**: Electron, Tauri
- **CLI Tools**: Node.js, Python, Go, Rust
- **Libraries**: NPM packages, Python packages, Go modules
- **Full Stack**: MERN, MEAN, JAMstack
- **Monorepo**: Turborepo, Nx, Lerna

## Usage Examples

```
@project-scaffolder Create React + TypeScript app
@project-scaffolder --template express-api
@project-scaffolder --monorepo turborepo
@project-scaffolder --cli go
@project-scaffolder --library npm-package
```

## Project Templates

### React + TypeScript + Vite

```bash
# Initialize project
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# Add essential dependencies
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-prettier
npm install -D husky lint-staged
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @vitejs/plugin-react
```

**Directory Structure:**
```
my-app/
├── src/
│   ├── components/
│   │   ├── common/
│   │   └── features/
│   ├── hooks/
│   ├── utils/
│   ├── services/
│   ├── types/
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
│   ├── unit/
│   └── integration/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .husky/
│   └── pre-commit
├── .eslintrc.json
├── .prettierrc
├── .gitignore
├── tsconfig.json
├── vite.config.ts
├── package.json
└── README.md
```

**.eslintrc.json:**
```json
{
  "parser": "@typescript-eslint/parser",
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint", "react", "react-hooks", "prettier"],
  "rules": {
    "prettier/prettier": "error",
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

**.prettierrc:**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
  },
});
```

**package.json scripts:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "prepare": "husky install"
  }
}
```

### Node.js Express API + TypeScript

```bash
# Initialize project
mkdir my-api && cd my-api
npm init -y
npm install express cors helmet dotenv
npm install -D typescript @types/node @types/express @types/cors
npm install -D ts-node-dev
npm install -D eslint prettier
npm install -D jest @types/jest ts-jest supertest @types/supertest
```

**Directory Structure:**
```
my-api/
├── src/
│   ├── config/
│   │   └── database.ts
│   ├── controllers/
│   ├── middleware/
│   │   ├── errorHandler.ts
│   │   ├── validation.ts
│   │   └── auth.ts
│   ├── models/
│   ├── routes/
│   │   └── index.ts
│   ├── services/
│   ├── utils/
│   │   ├── logger.ts
│   │   └── asyncHandler.ts
│   ├── types/
│   │   └── express.d.ts
│   ├── app.ts
│   └── server.ts
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── .gitignore
├── tsconfig.json
├── jest.config.js
├── package.json
└── README.md
```

**src/app.ts:**
```typescript
import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { errorHandler } from './middleware/errorHandler';
import routes from './routes';

const app: Application = express();

// Security middleware
app.use(helmet());
app.use(cors());

// Body parsing middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', routes);

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling
app.use(errorHandler);

export default app;
```

**src/server.ts:**
```typescript
import app from './app';
import dotenv from 'dotenv';

dotenv.config();

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

**src/middleware/errorHandler.ts:**
```typescript
import { Request, Response, NextFunction } from 'express';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
    });
  }

  console.error('ERROR:', err);
  return res.status(500).json({
    status: 'error',
    message: 'Internal server error',
  });
};
```

**src/utils/asyncHandler.ts:**
```typescript
import { Request, Response, NextFunction } from 'express';

export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@controllers/*": ["src/controllers/*"],
      "@services/*": ["src/services/*"],
      "@models/*": ["src/models/*"],
      "@middleware/*": ["src/middleware/*"],
      "@utils/*": ["src/utils/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

**package.json scripts:**
```json
{
  "scripts": {
    "dev": "ts-node-dev --respawn --transpile-only src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src --ext .ts",
    "lint:fix": "eslint src --ext .ts --fix"
  }
}
```

### Python FastAPI Project

```bash
# Create project directory
mkdir my-fastapi-app && cd my-fastapi-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv
pip install pytest pytest-cov pytest-asyncio httpx
pip install black flake8 mypy isort
```

**Directory Structure:**
```
my-fastapi-app/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── users.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api/
│       └── test_users.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
└── README.md
```

**app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import users
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**app/core/config.py:**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "My FastAPI App"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI application"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**app/schemas/user.py:**
```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**pyproject.toml:**
```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

**requirements-dev.txt:**
```
-r requirements.txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
flake8==6.1.0
mypy==1.7.1
isort==5.12.0
```

### Go CLI Application

```bash
# Initialize Go module
mkdir my-cli && cd my-cli
go mod init github.com/username/my-cli

# Install dependencies
go get github.com/spf13/cobra@latest
go get github.com/spf13/viper@latest
```

**Directory Structure:**
```
my-cli/
├── cmd/
│   ├── root.go
│   └── version.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── cli/
│   │   └── ui.go
│   └── utils/
│       └── helpers.go
├── pkg/
│   └── api/
│       └── client.go
├── tests/
├── .gitignore
├── go.mod
├── go.sum
├── main.go
├── Makefile
└── README.md
```

**main.go:**
```go
package main

import (
    "github.com/username/my-cli/cmd"
)

func main() {
    cmd.Execute()
}
```

**cmd/root.go:**
```go
package cmd

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var (
    cfgFile string
    verbose bool
)

var rootCmd = &cobra.Command{
    Use:   "my-cli",
    Short: "A brief description of your CLI",
    Long:  `A longer description of your CLI application`,
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func init() {
    cobra.OnInitialize(initConfig)

    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.my-cli.yaml)")
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        home, err := os.UserHomeDir()
        cobra.CheckErr(err)

        viper.AddConfigPath(home)
        viper.SetConfigType("yaml")
        viper.SetConfigName(".my-cli")
    }

    viper.AutomaticEnv()

    if err := viper.ReadInConfig(); err == nil {
        fmt.Fprintln(os.Stderr, "Using config file:", viper.ConfigFileUsed())
    }
}
```

**Makefile:**
```makefile
.PHONY: build test clean install

BINARY_NAME=my-cli
VERSION=$(shell git describe --tags --always --dirty)
LDFLAGS=-ldflags "-X main.Version=${VERSION}"

build:
	go build ${LDFLAGS} -o bin/${BINARY_NAME} main.go

test:
	go test -v ./...

test-coverage:
	go test -v -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out

clean:
	go clean
	rm -rf bin/

install:
	go install ${LDFLAGS}

lint:
	golangci-lint run

run:
	go run main.go
```

## Monorepo Setup (Turborepo)

```bash
# Create monorepo
npx create-turbo@latest my-monorepo
cd my-monorepo
```

**Directory Structure:**
```
my-monorepo/
├── apps/
│   ├── web/              # Next.js app
│   ├── api/              # Express API
│   └── docs/             # Documentation site
├── packages/
│   ├── ui/               # Shared UI components
│   ├── config/           # Shared configs (eslint, tsconfig)
│   ├── types/            # Shared TypeScript types
│   └── utils/            # Shared utilities
├── turbo.json
├── package.json
└── README.md
```

**turbo.json:**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

**Root package.json:**
```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "format": "prettier --write \"**/*.{ts,tsx,md}\""
  },
  "devDependencies": {
    "turbo": "latest",
    "prettier": "latest"
  }
}
```

## Essential Configuration Files

### .gitignore (Node.js)
```
# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
*.lcov

# Production
build/
dist/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
```

### .env.example
```bash
# Application
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Authentication
JWT_SECRET=your-secret-key-here
JWT_EXPIRE=7d

# API Keys
API_KEY=your-api-key
```

### .github/workflows/ci.yml
```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v3

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build
```

## Best Practices

### Project Structure
- **Separate concerns**: Keep routing, business logic, and data access separate
- **Use TypeScript**: Add type safety to catch errors early
- **Modular design**: Create reusable modules and components
- **Clear naming**: Use descriptive names for files and directories

### Configuration
- **Environment variables**: Never commit secrets to version control
- **Validation**: Validate configuration on startup
- **Defaults**: Provide sensible defaults for development
- **Documentation**: Document all required environment variables

### Code Quality
- **Linting**: Use ESLint/Pylint/golangci-lint
- **Formatting**: Use Prettier/Black/gofmt
- **Pre-commit hooks**: Enforce quality checks before commit
- **Testing**: Set up testing framework from day one

### Development Workflow
- **README**: Document setup instructions clearly
- **Scripts**: Provide npm/make scripts for common tasks
- **CI/CD**: Set up automated testing and deployment
- **Git hooks**: Use husky for pre-commit checks

## Template Checklist

```markdown
## Project Setup Checklist

### Initial Setup
- [ ] Project directory created
- [ ] Package manager initialized (npm, pip, go mod)
- [ ] Git repository initialized
- [ ] .gitignore configured
- [ ] README.md created

### Configuration
- [ ] Linting configured (ESLint, Pylint, etc.)
- [ ] Formatting configured (Prettier, Black, etc.)
- [ ] TypeScript configured (if applicable)
- [ ] Testing framework set up
- [ ] Environment variables documented

### Development Tools
- [ ] Pre-commit hooks installed
- [ ] VS Code settings configured
- [ ] Debugging configuration added
- [ ] Scripts for common tasks added

### CI/CD
- [ ] GitHub Actions workflow created
- [ ] Build pipeline configured
- [ ] Test automation set up
- [ ] Deployment process documented

### Documentation
- [ ] Setup instructions written
- [ ] API documentation started
- [ ] Contributing guidelines added
- [ ] License file added
```

## Notes

- Always start with a proper project structure
- Use templates and generators to save time
- Configure tooling early to enforce consistency
- Document everything from the beginning
- Use version control from day one
- Set up CI/CD early in the project
- Keep dependencies up to date
- Follow community conventions for the stack
