---
name: system-environment-setup
description: Configure development and production environments for consistent and reproducible setups. Use when setting up new projects, Docker environments, or development tooling. Handles Docker Compose, .env configuration, dev containers, and infrastructure as code.
metadata:
  tags: environment-setup, Docker-Compose, dev-environment, IaC, configuration
  platforms: Claude, ChatGPT, Gemini
---


# System & Environment Setup


## When to use this skill

- **New project**: Initial environment setup
- **Team onboarding**: Standardizing new developer environments
- **Multiple services**: Local execution of microservices
- **Production replication**: Testing production environment locally

## Instructions

### Step 1: Docker Compose Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # Web Application
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - db
      - redis
    command: npm run dev

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Nginx (Reverse Proxy)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

**Usage**:
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Restart specific service only
docker-compose restart web

# Stop and remove
docker-compose down

# Remove including volumes
docker-compose down -v
```

### Step 2: Environment Variable Management

**.env.example**:
```bash
# Application
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379

# JWT
ACCESS_TOKEN_SECRET=change-me-in-production-min-32-characters
REFRESH_TOKEN_SECRET=change-me-in-production-min-32-characters
TOKEN_EXPIRY=15m

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# External APIs
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
AWS_ACCESS_KEY_ID=AKIAXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxx
AWS_REGION=us-east-1
```

**.env** (local only, add to gitignore):
```bash
# .gitignore
.env
.env.local
.env.*.local
```

**Loading environment variables** (Node.js):
```typescript
import dotenv from 'dotenv';
import path from 'path';

// Load .env file
dotenv.config();

// Type-safe environment variables
interface Env {
  NODE_ENV: 'development' | 'production' | 'test';
  PORT: number;
  DATABASE_URL: string;
  REDIS_URL: string;
  ACCESS_TOKEN_SECRET: string;
}

function loadEnv(): Env {
  const required = ['DATABASE_URL', 'ACCESS_TOKEN_SECRET', 'REDIS_URL'];

  for (const key of required) {
    if (!process.env[key]) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
  }

  return {
    NODE_ENV: (process.env.NODE_ENV as any) || 'development',
    PORT: parseInt(process.env.PORT || '3000'),
    DATABASE_URL: process.env.DATABASE_URL!,
    REDIS_URL: process.env.REDIS_URL!,
    ACCESS_TOKEN_SECRET: process.env.ACCESS_TOKEN_SECRET!
  };
}

export const env = loadEnv();
```

### Step 3: Dev Container (VS Code)

**.devcontainer/devcontainer.json**:
```json
{
  "name": "Node.js & PostgreSQL",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "web",
  "workspaceFolder": "/app",

  "customizations": {
    "vscode": {
      "extensions": [
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "ms-azuretools.vscode-docker",
        "prisma.prisma"
      ],
      "settings": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "eslint.validate": ["javascript", "typescript"]
      }
    }
  },

  "forwardPorts": [3000, 5432, 6379],

  "postCreateCommand": "npm install",

  "remoteUser": "node"
}
```

### Step 4: Makefile (Convenience Commands)

**Makefile**:
```makefile
.PHONY: help install dev build test clean docker-up docker-down migrate seed

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	npm install

dev: ## Start development server
	npm run dev

build: ## Build for production
	npm run build

test: ## Run tests
	npm test

test-watch: ## Run tests in watch mode
	npm test -- --watch

lint: ## Run linter
	npm run lint

lint-fix: ## Fix linting issues
	npm run lint -- --fix

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

migrate: ## Run database migrations
	npm run migrate

migrate-create: ## Create new migration
	@read -p "Migration name: " name; \
	npm run migrate:create -- $$name

seed: ## Seed database
	npm run seed

clean: ## Clean build artifacts
	rm -rf dist node_modules coverage

reset: clean install ## Reset project (clean + install)
```

**Usage**:
```bash
make help         # List of commands
make install      # Install dependencies
make dev          # Start dev server
make docker-up    # Start Docker services
```

### Step 5: Infrastructure as Code (Terraform)

**main.tf** (AWS example):
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "myapp-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

# RDS (PostgreSQL)
resource "aws_db_instance" "postgres" {
  identifier           = "${var.project_name}-db"
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  skip_final_snapshot     = false
  final_snapshot_identifier = "${var.project_name}-final-snapshot"

  tags = {
    Name        = "${var.project_name}-db"
    Environment = var.environment
  }
}

# ECS (Container Service)
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}
```

**variables.tf**:
```hcl
variable "project_name" {
  description = "Project name"
  type        = string
  default     = "myapp"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

## Output format

### Project Structure

```
project/
├── .devcontainer/
│   └── devcontainer.json
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── .env.example
├── .gitignore
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
└── README.md
```

## Constraints

### Mandatory Rules (MUST)

1. **Provide .env.example**: List of required environment variables
2. **.gitignore**: Never commit .env files
3. **README.md**: Document installation and running instructions

### Prohibited (MUST NOT)

1. **No committing secrets**: Never commit .env, credentials files
2. **No hardcoding**: All configuration via environment variables

## Best practices

1. **Docker Compose**: Use Docker Compose for local development
2. **Volume Mount**: Instantly reflects code changes
3. **Health Checks**: Verify service readiness

## References

- [Docker Compose](https://docs.docker.com/compose/)
- [Dev Containers](https://containers.dev/)
- [Terraform](https://www.terraform.io/)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [deployment](../deployment/SKILL.md)
- [environment-setup](../../utilities/environment-setup/SKILL.md)

### Tags
`#environment-setup` `#Docker-Compose` `#dev-environment` `#IaC` `#Terraform` `#infrastructure`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
