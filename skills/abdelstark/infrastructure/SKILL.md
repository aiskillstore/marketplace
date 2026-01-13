---
name: infrastructure
description: Infrastructure as Code patterns for deploying Guts nodes using Terraform, Docker, and Kubernetes
---

# Infrastructure Skill for Guts

You are managing infrastructure for a decentralized application with multiple node types.

## Deployment Targets

1. **Local Development**: Docker Compose
2. **Testing**: Kubernetes (k3s/kind)
3. **Production**: Cloud-agnostic Kubernetes + Terraform

## Terraform Patterns

### Module Structure

```
infra/
├── terraform/
│   ├── modules/
│   │   ├── network/
│   │   ├── compute/
│   │   └── storage/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── main.tf
```

### Example Module

```hcl
# modules/guts-node/main.tf
variable "node_count" {
  type        = number
  description = "Number of Guts nodes to deploy"
  default     = 3
}

variable "instance_type" {
  type        = string
  description = "Instance type for nodes"
  default     = "t3.medium"
}

resource "aws_instance" "guts_node" {
  count         = var.node_count
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  tags = {
    Name        = "guts-node-${count.index}"
    Environment = var.environment
    Project     = "guts"
  }
}
```

## Docker Best Practices

### Multi-stage Builds

```dockerfile
# Build stage
FROM rust:1.75-slim as builder
WORKDIR /app
COPY . .
RUN cargo build --release --bin guts-node

# Runtime stage
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/guts-node /usr/local/bin/
EXPOSE 8080 9000
ENTRYPOINT ["guts-node"]
```

### Docker Compose for Development

```yaml
version: '3.8'

services:
  node1:
    build: .
    ports:
      - "8081:8080"
    environment:
      - GUTS_NODE_ID=node1
      - GUTS_PEERS=node2:9000,node3:9000
    volumes:
      - node1-data:/data

  node2:
    build: .
    ports:
      - "8082:8080"
    environment:
      - GUTS_NODE_ID=node2
      - GUTS_PEERS=node1:9000,node3:9000
    volumes:
      - node2-data:/data

  node3:
    build: .
    ports:
      - "8083:8080"
    environment:
      - GUTS_NODE_ID=node3
      - GUTS_PEERS=node1:9000,node2:9000
    volumes:
      - node3-data:/data

volumes:
  node1-data:
  node2-data:
  node3-data:
```

## Kubernetes Patterns

### StatefulSet for Nodes

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: guts-node
spec:
  serviceName: guts-nodes
  replicas: 3
  selector:
    matchLabels:
      app: guts-node
  template:
    metadata:
      labels:
        app: guts-node
    spec:
      containers:
      - name: guts-node
        image: guts/node:latest
        ports:
        - containerPort: 8080
          name: api
        - containerPort: 9000
          name: p2p
        volumeMounts:
        - name: data
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

## Monitoring Stack

- **Metrics**: Prometheus with custom Rust metrics
- **Logs**: Loki + Grafana
- **Tracing**: Jaeger with OpenTelemetry

## Security Checklist

- [ ] TLS certificates via cert-manager
- [ ] Network policies for pod isolation
- [ ] Secrets management with external-secrets
- [ ] Regular security scanning with Trivy
- [ ] RBAC for Kubernetes access
