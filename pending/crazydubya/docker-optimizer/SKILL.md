---
name: docker-optimizer
description: Reviews Dockerfiles for best practices, security issues, and image size optimizations including multi-stage builds and layer caching. Use when working with Docker, containers, or deployment.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Docker Optimizer

Analyzes and optimizes Dockerfiles for performance, security, and best practices.

## When to Use
- User working with Docker or containers
- Dockerfile optimization needed
- Container image too large
- User mentions "Docker", "container", "image size", or "deployment"

## Instructions

### 1. Find Dockerfiles

Search for: `Dockerfile`, `Dockerfile.*`, `*.dockerfile`

### 2. Check Best Practices

**Use specific base image versions:**
```dockerfile
# Bad
FROM node:latest

# Good
FROM node:18-alpine
```

**Minimize layers:**
```dockerfile
# Bad
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

# Good
RUN apt-get update && \
    apt-get install -y curl git && \
    rm -rf /var/lib/apt/lists/*
```

**Order instructions by change frequency:**
```dockerfile
# Dependencies change less than code
COPY package*.json ./
RUN npm install
COPY . .
```

**Use .dockerignore:**
```
node_modules
.git
.env
*.md
```

### 3. Multi-Stage Builds

Reduce final image size:

```dockerfile
# Build stage
FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### 4. Security Issues

**Don't run as root:**
```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

**No secrets in image:**
```dockerfile
# Bad: Hardcoded secret
ENV API_KEY=secret123

# Good: Use build args or runtime env
ARG BUILD_ENV
ENV NODE_ENV=${BUILD_ENV}
```

**Scan for vulnerabilities:**
```bash
docker scan image:tag
trivy image image:tag
```

### 5. Size Optimization

**Use Alpine images:**
- `node:18-alpine` vs `node:18` (900MB → 170MB)
- `python:3.11-alpine` vs `python:3.11` (900MB → 50MB)

**Remove unnecessary files:**
```dockerfile
RUN npm install --production && \
    npm cache clean --force
```

**Use specific COPY:**
```dockerfile
# Bad: Copies everything
COPY . .

# Good: Copy only what's needed
COPY package*.json ./
COPY src ./src
```

### 6. Caching Strategy

Layer caching optimization:

```dockerfile
# Install dependencies first (cached if package.json unchanged)
COPY package*.json ./
RUN npm install

# Copy source (changes more frequently)
COPY . .
RUN npm run build
```

### 7. Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js
```

### 8. Generate Optimized Dockerfile

Provide improved version with:
- Multi-stage build
- Appropriate base image
- Security improvements
- Layer optimization
- Build caching
- .dockerignore file

### 9. Build Commands

**Efficient build:**
```bash
# Use BuildKit
DOCKER_BUILDKIT=1 docker build -t app:latest .

# Build with cache from registry
docker build --cache-from myregistry/app:latest -t app:latest .
```

### 10. Dockerfile Checklist

- [ ] Specific base image tag (not `latest`)
- [ ] Multi-stage build if applicable
- [ ] Non-root user
- [ ] Minimal layers (combined RUN commands)
- [ ] .dockerignore present
- [ ] No secrets in image
- [ ] Proper layer ordering for caching
- [ ] Alpine or slim variant used
- [ ] Cleanup in same RUN layer
- [ ] HEALTHCHECK defined

## Security Best Practices

- Scan images regularly
- Use official base images
- Keep base images updated
- Minimize attack surface (fewer packages)
- Run as non-root user
- Use read-only filesystem where possible

## Supporting Files
- `templates/Dockerfile.optimized`: Optimized multi-stage Dockerfile example
- `templates/.dockerignore`: Common .dockerignore patterns
