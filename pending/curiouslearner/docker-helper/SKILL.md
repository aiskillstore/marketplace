---
name: docker-helper
description: Docker Compose generation, optimization, and troubleshooting assistance.
---

# Docker Helper Skill

Docker Compose generation, optimization, and troubleshooting assistance.

## Instructions

You are a Docker and containerization expert. When invoked:

1. **Generate Docker Files**:
   - Create Dockerfile based on project type
   - Generate docker-compose.yml for multi-service apps
   - Optimize for build time and image size
   - Follow best practices for security and performance

2. **Optimize Existing Configurations**:
   - Reduce image sizes (multi-stage builds)
   - Improve layer caching
   - Security hardening
   - Resource limits and health checks

3. **Troubleshoot Issues**:
   - Container startup failures
   - Network connectivity problems
   - Volume mounting issues
   - Performance problems

4. **Provide Best Practices**:
   - Image naming and tagging
   - Secrets management
   - Logging configuration
   - Development vs production configs

## Dockerfile Best Practices

### Node.js Application
```dockerfile
# Multi-stage build for smaller image
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first (better layer caching)
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy only necessary files from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs package*.json ./

USER nodejs

EXPOSE 3000

# Use exec form for proper signal handling
CMD ["node", "dist/index.js"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js
```

### Python Application
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies in separate layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "app.py"]
```

### Go Application
```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Final stage - minimal image
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/main .

EXPOSE 8080

CMD ["./main"]
```

## Docker Compose Examples

### Full Stack Application
```yaml
version: '3.8'

services:
  # Frontend
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=http://api:8000
    depends_on:
      api:
        condition: service_healthy
    networks:
      - frontend
    restart: unless-stopped

  # Backend API
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://cache:6379
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    networks:
      - frontend
      - backend
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Database
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  cache:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
      - api
    networks:
      - frontend
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Development Environment
```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - .:/app
      - /app/node_modules  # Anonymous volume for node_modules
    command: npm run dev
    networks:
      - dev_network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=dev_db
      - POSTGRES_USER=dev
      - POSTGRES_PASSWORD=dev_password
    ports:
      - "5432:5432"
    volumes:
      - dev_db_data:/var/lib/postgresql/data
    networks:
      - dev_network

volumes:
  dev_db_data:

networks:
  dev_network:
```

## Usage Examples

```
@docker-helper
@docker-helper --generate-dockerfile
@docker-helper --optimize
@docker-helper --compose
@docker-helper --troubleshoot
```

## Optimization Techniques

### Multi-Stage Builds
```dockerfile
# Reduces final image size by 70-90%
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

### Layer Caching
```dockerfile
# ❌ Bad - Invalidates cache on any file change
COPY . .
RUN npm install

# ✓ Good - Cache dependencies separately
COPY package*.json ./
RUN npm install
COPY . .
```

### Reduce Image Size
```dockerfile
# Use alpine variants (much smaller)
FROM node:18-alpine  # ~170MB vs ~900MB for node:18

# Clean up in same layer
RUN apt-get update && \
    apt-get install -y package && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Use .dockerignore
# Create .dockerignore file:
# node_modules
# .git
# *.md
# .env*
```

## Security Best Practices

```dockerfile
# Don't run as root
RUN adduser -D -u 1001 appuser
USER appuser

# Scan for vulnerabilities
# Use: docker scan myimage:tag

# Use specific tags, not 'latest'
FROM node:18.16.0-alpine  # Not: FROM node:latest

# Don't store secrets in image
# Use environment variables or secrets management

# Minimize attack surface
# Use minimal base images (alpine, distroless)

# Keep base images updated
# Regularly rebuild and update
```

## Common Issues & Solutions

### Issue: Container Exits Immediately
```bash
# Check logs
docker logs <container_id>

# Run interactively to debug
docker run -it <image> /bin/sh

# Check entrypoint/command
docker inspect <container_id> | grep -A5 Cmd
```

### Issue: Cannot Connect to Service
```yaml
# Ensure services are on same network
networks:
  - mynetwork

# Use service name as hostname
DATABASE_URL=postgresql://db:5432/myapp  # 'db' is service name

# Check if service is ready
depends_on:
  db:
    condition: service_healthy
```

### Issue: Volume Permission Problems
```dockerfile
# Match host user ID
RUN adduser -u 1001 appuser
USER appuser

# Or change ownership in entrypoint
ENTRYPOINT ["sh", "-c", "chown -R appuser:appuser /data && exec \"$@\""]
```

### Issue: Slow Builds
```dockerfile
# Use build cache effectively
COPY package*.json ./
RUN npm ci
COPY . .

# Use BuildKit
# Set: DOCKER_BUILDKIT=1

# Use .dockerignore
# Exclude: node_modules, .git, build artifacts
```

## Docker Commands Reference

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d -p 3000:3000 --name myapp myapp:latest

# View logs
docker logs -f myapp

# Execute command in container
docker exec -it myapp /bin/sh

# Stop and remove
docker stop myapp && docker rm myapp

# Compose commands
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose ps

# Clean up
docker system prune -a
docker volume prune
```

## Health Checks

```dockerfile
# Node.js
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js || exit 1

# Python
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Simple HTTP check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1
```

## Notes

- Always use specific version tags, not `latest`
- Implement health checks for critical services
- Use multi-stage builds to reduce image size
- Never store secrets in Dockerfiles or images
- Use `.dockerignore` to exclude unnecessary files
- Run containers as non-root users
- Implement proper logging (stdout/stderr)
- Use volumes for persistent data
- Configure resource limits in production
- Regularly update base images for security patches
