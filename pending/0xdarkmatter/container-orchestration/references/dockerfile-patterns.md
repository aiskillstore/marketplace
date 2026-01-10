# Advanced Dockerfile Patterns

Production-ready Dockerfile techniques.

## Multi-Stage Builds

### Python Application

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy application
COPY --chown=appuser:appuser src/ ./src/

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

### Node.js Application

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

USER nextjs
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Go Application

```dockerfile
# Stage 1: Build
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# Stage 2: Minimal runtime
FROM scratch

# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app/server /server

EXPOSE 8080
ENTRYPOINT ["/server"]
```

## Layer Optimization

### Order by Change Frequency

```dockerfile
# Least frequently changed first
FROM python:3.11-slim

# System packages (rarely change)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (changes frequently)
COPY src/ ./src/

CMD ["python", "-m", "src.main"]
```

### Combine RUN Commands

```dockerfile
# BAD - Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

# GOOD - Single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
```

## Security Best Practices

### Non-Root User

```dockerfile
# Create user with specific UID
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Switch to user
USER appuser

# Copy files with correct ownership
COPY --chown=appuser:appgroup src/ ./src/
```

### Read-Only Root Filesystem

```dockerfile
# Use with docker run --read-only
FROM python:3.11-slim

# Create writable directories
RUN mkdir -p /tmp /var/log/app \
    && chown -R appuser:appuser /tmp /var/log/app

USER appuser

# Application writes only to /tmp and /var/log/app
```

### No Secrets in Image

```dockerfile
# WRONG - Secret in build arg
ARG API_KEY
ENV API_KEY=${API_KEY}

# CORRECT - Secret at runtime
# Pass via environment variable or secret manager
ENV API_KEY=""  # Set at runtime
```

### Minimal Base Image

```dockerfile
# Full image: ~1GB
FROM python:3.11

# Slim image: ~150MB
FROM python:3.11-slim

# Alpine image: ~50MB (but musl libc issues)
FROM python:3.11-alpine

# Distroless: Minimal, no shell
FROM gcr.io/distroless/python3-debian12
```

## Health Checks

```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Without curl (for minimal images)
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# TCP health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD nc -z localhost 8000 || exit 1
```

## Build Arguments

```dockerfile
# Declare build args
ARG PYTHON_VERSION=3.11
ARG APP_ENV=production

FROM python:${PYTHON_VERSION}-slim

# Use in ENV
ARG APP_ENV
ENV APP_ENV=${APP_ENV}

# Conditional logic
RUN if [ "$APP_ENV" = "development" ]; then \
        pip install debugpy pytest; \
    fi
```

## Caching Strategies

### Mount Cache (BuildKit)

```dockerfile
# syntax=docker/dockerfile:1.4

# Cache pip downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache apt packages
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y curl
```

### Bind Mounts for Build

```dockerfile
# syntax=docker/dockerfile:1.4

# Mount source code without copying
RUN --mount=type=bind,source=src,target=/app/src \
    python -m compileall /app/src
```

## Labels and Metadata

```dockerfile
LABEL org.opencontainers.image.title="My App"
LABEL org.opencontainers.image.description="Production application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="Company"
LABEL org.opencontainers.image.source="https://github.com/org/repo"
```

## .dockerignore

```
# .dockerignore
.git
.gitignore
.env
.env.*
*.md
!README.md
Dockerfile*
docker-compose*
.dockerignore

# Python
__pycache__
*.pyc
*.pyo
.pytest_cache
.coverage
htmlcov
.venv
venv

# Node
node_modules
npm-debug.log
.npm

# IDE
.idea
.vscode
*.swp
```

## Debug Container

```dockerfile
# Multi-stage with debug target
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/

# Debug stage
FROM base AS debug
RUN pip install debugpy
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "src.main"]

# Production stage
FROM base AS production
USER appuser
CMD ["python", "-m", "src.main"]
```

Build specific target:
```bash
docker build --target debug -t myapp:debug .
docker build --target production -t myapp:latest .
```
