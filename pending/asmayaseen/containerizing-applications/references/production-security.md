# Production Security Patterns

## Security Scanning with Trivy

### CI/CD Integration

```yaml
# GitHub Actions
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # Fail build on vulnerabilities
```

### Local Scanning

```bash
# Scan image before push
trivy image --severity HIGH,CRITICAL myapp:latest

# Scan with exit code for scripts
trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest

# Generate SBOM
trivy image --format spdx-json -o sbom.json myapp:latest

# Scan filesystem (before building)
trivy fs --severity HIGH,CRITICAL .
```

### Trivy Configuration (.trivyignore)

```
# Ignore specific CVEs with justification
CVE-2023-12345  # False positive, not exploitable in our context
CVE-2023-67890  # Mitigated by network policy
```

## Distroless Images

### Why Distroless?

- No shell (can't exec into container for attacks)
- No package manager (can't install malicious tools)
- Minimal attack surface (only runtime dependencies)
- Smaller images (faster pulls, less storage)

### Python with Distroless

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
# No USER instruction needed - distroless runs as nonroot by default
EXPOSE 8000
ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Node.js with Distroless

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs20-debian12
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .
EXPOSE 3000
CMD ["dist/server.js"]
```

### Go with Scratch (Ultimate Minimal)

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o /app/server

FROM scratch
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

## Multi-Architecture Builds

### Build for Multiple Architectures

```yaml
# GitHub Actions
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64  # Both architectures
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Local Multi-Arch Build

```bash
# Create builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .
```

## BuildKit Secrets

### Mounting Secrets During Build

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Mount secret at build time (never stored in image layers)
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm install

# For pip with private PyPI
RUN --mount=type=secret,id=pip_credentials,target=/root/.netrc \
    pip install private-package
```

### Passing Secrets in CI

```yaml
- name: Build with secrets
  uses: docker/build-push-action@v5
  with:
    context: .
    secrets: |
      npm_token=${{ secrets.NPM_TOKEN }}
      pip_credentials=${{ secrets.PIP_CREDENTIALS }}
```

## .dockerignore (Critical)

```dockerignore
# Git
.git
.gitignore

# Dependencies (rebuilt in container)
node_modules
__pycache__
*.pyc
.venv
venv

# Build artifacts
dist
build
*.egg-info

# IDE
.idea
.vscode
*.swp

# Testing
.pytest_cache
.coverage
htmlcov
.tox

# Secrets (NEVER include)
.env
.env.*
*.pem
*.key
credentials.json

# Docker
Dockerfile*
docker-compose*
.docker

# Docs (not needed in runtime)
docs
*.md
LICENSE
```

## Security Checklist

### Image Build
- [ ] Using minimal base (alpine/slim/distroless)
- [ ] Multi-stage build (no build tools in final image)
- [ ] Running as non-root user
- [ ] No secrets in image layers (use BuildKit)
- [ ] .dockerignore excludes sensitive files
- [ ] Pinned base image versions (not :latest)

### Scanning
- [ ] Trivy scan in CI (fail on HIGH/CRITICAL)
- [ ] SBOM generated and stored
- [ ] Base image CVEs tracked and updated

### Runtime
- [ ] Read-only root filesystem where possible
- [ ] No privileged containers
- [ ] Resource limits set (CPU, memory)
- [ ] Security context in K8s (runAsNonRoot, allowPrivilegeEscalation: false)