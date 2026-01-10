---
name: container-orchestration
description: "Docker and Kubernetes patterns. Triggers on: Dockerfile, docker-compose, kubernetes, k8s, helm, pod, deployment, service, ingress, container, image."
compatibility: "Docker 20+, Kubernetes 1.25+, Helm 3+"
allowed-tools: "Read Write Bash"
---

# Container Orchestration

Docker and Kubernetes patterns for containerized applications.

## Dockerfile Best Practices

```dockerfile
# Use specific version, not :latest
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Production stage (multi-stage build)
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Copy from builder
COPY --from=builder /app /app

# Set environment
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

### Dockerfile Rules
```
DO:
- Use specific base image versions
- Use multi-stage builds
- Run as non-root user
- Order commands by change frequency
- Use .dockerignore
- Add health checks

DON'T:
- Use :latest tag
- Run as root
- Copy unnecessary files
- Store secrets in image
- Install dev dependencies in production
```

## Docker Compose

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Kubernetes Basics

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

## kubectl Quick Reference

| Command | Description |
|---------|-------------|
| `kubectl get pods` | List pods |
| `kubectl logs <pod>` | View logs |
| `kubectl exec -it <pod> -- sh` | Shell into pod |
| `kubectl apply -f manifest.yaml` | Apply config |
| `kubectl rollout restart deployment/app` | Restart deployment |
| `kubectl rollout status deployment/app` | Check rollout |
| `kubectl describe pod <pod>` | Debug pod |
| `kubectl port-forward svc/app 8080:80` | Local port forward |

## Additional Resources

- `./references/dockerfile-patterns.md` - Advanced Dockerfile techniques
- `./references/k8s-manifests.md` - Full Kubernetes manifest examples
- `./references/helm-patterns.md` - Helm chart structure and values

## Scripts

- `./scripts/build-push.sh` - Build and push Docker image

## Assets

- `./assets/Dockerfile.template` - Production Dockerfile template
- `./assets/docker-compose.template.yml` - Compose starter template
