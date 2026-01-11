# Docker Workflow

Comprehensive Docker containerization workflow covering multi-stage builds, docker-compose orchestration, image optimization, debugging, and production best practices.

## Overview

Docker containerization streamlines development, testing, and deployment by packaging applications with their dependencies into portable, reproducible containers. This skill guides you through professional Docker workflows from development to production.

Use this skill when containerizing applications, setting up development environments, or deploying with Docker.

## Installation

Ensure Docker is installed:

```bash
# macOS
brew install docker

# Ubuntu/Debian
sudo apt-get install docker.io docker-compose

# Verify installation
docker --version
docker-compose --version
```

## What's Included

### SKILL.md
Comprehensive guide covering Docker workflow phases from initial setup through production deployment, including multi-stage builds, docker-compose orchestration, optimization strategies, debugging tools, and deployment best practices.

### scripts/
- `docker_helper.sh` - Utility script for common Docker operations:
  - Container health checks
  - Inspection and debugging
  - Log viewing
  - Shell access
  - Image size analysis
  - Resource cleanup

### examples/
- `Dockerfile.multi-stage` - Templates for Node.js, Python, Go, Java, Rust
- `docker-compose.yml` - Full-featured multi-service setup
- `.dockerignore` - Comprehensive ignore patterns

## Quick Start

### Create a Multi-Stage Dockerfile

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
    networks:
      - app-network

volumes:
  postgres-data:

networks:
  app-network:
```

### Build and Run

```bash
# Build image
docker build -t myapp:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

## Core Capabilities

- **Multi-stage builds**: Separate build and runtime dependencies for optimal image size (50-90% reduction)
- **Docker Compose orchestration**: Manage multi-container applications with networking and dependencies
- **Image optimization**: Reduce image size through layer caching and best practices
- **Development workflows**: Hot-reload, volume mounting, and environment-specific configs
- **Debugging tools**: Container inspection, health checks, and troubleshooting utilities
- **Production readiness**: Security hardening, health checks, and deployment strategies

## Workflow Phases

### Phase 1: Initial Setup

**Create .dockerignore:**
```dockerignore
node_modules/
__pycache__/
*.pyc
.git/
.env
*.log
dist/
build/
coverage/
```

**Key principles:**
- Exclude build artifacts and dependencies
- Exclude sensitive files (.env, credentials)
- Exclude version control (.git)
- Smaller context = faster builds

### Phase 2: Multi-Stage Dockerfile

**Optimize Layer Caching:**
```dockerfile
# ✅ GOOD: Dependencies cached separately
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# ❌ BAD: Any file change invalidates cache
COPY . .
RUN npm ci
```

**Apply Security Best Practices:**
```dockerfile
# Use specific versions
FROM node:18.17.1-alpine

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Copy with ownership
COPY --chown=nodejs:nodejs . .
```

### Phase 3: Docker Compose Setup

Use override files for different environments:

**Development (docker-compose.override.yml)**:
```yaml
services:
  app:
    build:
      target: development
    volumes:
      - ./src:/app/src
    environment:
      - NODE_ENV=development
    command: npm run dev
```

**Production (docker-compose.prod.yml)**:
```yaml
services:
  app:
    build:
      target: production
    restart: always
    environment:
      - NODE_ENV=production
```

### Phase 4: Debugging

Use the helper script:

```bash
# Check container health
./scripts/docker_helper.sh health myapp

# Inspect details
./scripts/docker_helper.sh inspect myapp

# View logs
./scripts/docker_helper.sh logs myapp 200

# Open shell
./scripts/docker_helper.sh shell myapp

# Analyze image size
./scripts/docker_helper.sh size myapp:latest

# Cleanup resources
./scripts/docker_helper.sh cleanup
```

### Phase 5: Optimization

**Reduce Image Size:**
1. Use smaller base images (alpine > slim > debian)
2. Multi-stage builds to exclude build tools
3. Combine RUN commands for fewer layers
4. Clean up in same layer
5. Use .dockerignore

**Example:**
```dockerfile
# ✅ GOOD: Combined, cleaned up
RUN apt-get update && \
    apt-get install -y --no-install-recommends package1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Phase 6: Production Deployment

**Production Dockerfile:**
```dockerfile
FROM node:18-alpine AS production

# Security: non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Deployment Commands:**
```bash
# Tag for registry
docker tag myapp:latest registry.example.com/myapp:v1.0.0

# Push to registry
docker push registry.example.com/myapp:v1.0.0

# Deploy
docker-compose pull && docker-compose up -d

# Rolling update
docker-compose up -d --no-deps --build app
```

## Essential Commands

```bash
# Build
docker build -t myapp .
docker-compose build

# Run
docker run -d -p 3000:3000 myapp
docker-compose up -d

# Logs
docker logs -f myapp
docker-compose logs -f

# Execute
docker exec -it myapp sh
docker-compose exec app sh

# Stop
docker-compose down

# Clean
docker system prune -a
```

## Best Practices Summary

### Security
✅ Use specific image versions, not `latest`
✅ Run as non-root user
✅ Use secrets management for sensitive data
✅ Scan images for vulnerabilities
✅ Use minimal base images

### Performance
✅ Use multi-stage builds
✅ Optimize layer caching
✅ Use .dockerignore
✅ Combine RUN commands
✅ Use BuildKit

### Development
✅ Use docker-compose for multi-container apps
✅ Use volumes for hot-reload
✅ Implement health checks
✅ Use proper dependency ordering

### Production
✅ Set restart policies
✅ Use orchestration (Swarm, Kubernetes)
✅ Monitor with health checks
✅ Use reverse proxy
✅ Implement rolling updates

## Common Use Cases

### Full-Stack Application
Frontend + Backend + Database + Redis with docker-compose orchestration.

### Microservices
API Gateway + Multiple Services + Message Queue with network isolation.

### Development with Hot Reload
Volume mounting for source code with dev-specific configuration.

## Troubleshooting

**Container exits immediately:**
```bash
docker logs myapp
docker run -it --entrypoint sh myapp:latest
```

**Network connectivity:**
```bash
docker network inspect myapp_default
docker exec myapp ping db
```

**Volume permissions:**
```bash
# Fix in Dockerfile
RUN chown -R nodejs:nodejs /app/data
```

## Documentation

See `SKILL.md` for comprehensive documentation, detailed workflows, and advanced techniques.

See `examples/` directory for complete Dockerfile templates and docker-compose configurations.

## Requirements

- Docker 20.10+
- docker-compose 1.29+ (or Docker Compose V2)
- Basic understanding of containerization concepts
