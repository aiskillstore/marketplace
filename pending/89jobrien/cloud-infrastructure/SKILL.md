---
name: cloud-infrastructure
description: Cloud infrastructure design and deployment patterns for AWS, Azure, and
  GCP. Use when designing cloud architectures, implementing IaC with Terraform, optimizing
  costs, or setting up multi-region deployments.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Cloud Infrastructure

Comprehensive cloud infrastructure skill covering multi-cloud architecture, Infrastructure as Code, cost optimization, and production deployment patterns.

## When to Use This Skill

- Designing cloud architecture for new applications
- Implementing Infrastructure as Code (Terraform, CloudFormation, Pulumi)
- Cost optimization and resource right-sizing
- Multi-region and high-availability deployments
- Cloud migration planning
- Security and compliance implementation
- Auto-scaling and performance optimization

## Cloud Architecture Patterns

### Compute Patterns

| Pattern | AWS | Azure | GCP | Use Case |
|---------|-----|-------|-----|----------|
| Serverless | Lambda | Functions | Cloud Functions | Event-driven, variable load |
| Containers | ECS/EKS | AKS | GKE | Microservices, consistent env |
| VMs | EC2 | Virtual Machines | Compute Engine | Legacy apps, full control |
| Batch | Batch | Batch | Batch | Large-scale processing |

### Storage Patterns

| Type | AWS | Azure | GCP | Use Case |
|------|-----|-------|-----|----------|
| Object | S3 | Blob Storage | Cloud Storage | Static files, backups |
| Block | EBS | Managed Disks | Persistent Disk | Database storage |
| File | EFS | Azure Files | Filestore | Shared file systems |
| Archive | Glacier | Archive | Coldline | Long-term retention |

### Database Patterns

| Type | AWS | Azure | GCP | Use Case |
|------|-----|-------|-----|----------|
| Relational | RDS, Aurora | SQL Database | Cloud SQL | ACID transactions |
| NoSQL | DynamoDB | Cosmos DB | Firestore | Flexible schema |
| Cache | ElastiCache | Cache for Redis | Memorystore | Session, caching |
| Data Warehouse | Redshift | Synapse | BigQuery | Analytics |

## Infrastructure as Code

### Terraform Best Practices

**Project Structure:**

```
infrastructure/
├── modules/
│   ├── networking/
│   ├── compute/
│   └── database/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── main.tf
├── variables.tf
├── outputs.tf
└── versions.tf
```

**State Management:**

- Use remote state (S3, Azure Blob, GCS)
- Enable state locking (DynamoDB, Blob lease)
- Separate state per environment
- Never commit state files

**Module Design:**

- Single responsibility per module
- Expose minimal required variables
- Document inputs/outputs
- Version modules with git tags

### Cost Optimization

**Compute Savings:**

- Reserved Instances (1-3 year commitment): 30-60% savings
- Spot/Preemptible instances: 60-90% savings for interruptible workloads
- Right-sizing: Match instance size to actual usage
- Auto-scaling: Scale down during low usage

**Storage Savings:**

- Lifecycle policies: Auto-transition to cheaper tiers
- Compression: Reduce storage footprint
- Deduplication: Eliminate redundant data
- Delete unused resources: Orphaned volumes, snapshots

**Network Savings:**

- Use CDN for static content
- Optimize data transfer paths
- Use private endpoints
- Compress API responses

## High Availability Patterns

### Multi-AZ Deployment

- Deploy across 2-3 availability zones
- Use load balancers for distribution
- Database replication across AZs
- Automatic failover configuration

### Multi-Region Deployment

- Active-active or active-passive
- DNS-based routing (Route53, Traffic Manager)
- Data replication strategy
- Disaster recovery procedures

### Resilience Patterns

- Circuit breakers for external dependencies
- Retry with exponential backoff
- Bulkhead isolation
- Graceful degradation

## Security Best Practices

### Identity & Access

- Principle of least privilege
- Use IAM roles, not long-term credentials
- Enable MFA for privileged accounts
- Regular access reviews

### Network Security

- VPC/VNet isolation
- Security groups as firewalls
- Private subnets for backend services
- VPN/Direct Connect for hybrid

### Data Protection

- Encryption at rest (KMS)
- Encryption in transit (TLS)
- Key rotation policies
- Backup and recovery testing

## Monitoring & Observability

### Key Metrics

- CPU, Memory, Disk utilization
- Network throughput and latency
- Error rates and types
- Cost per service/team

### Alerting Strategy

- Set thresholds based on baselines
- Alert on symptoms, not causes
- Runbooks for each alert
- Escalation paths defined

## Reference Files

- **`references/terraform_patterns.md`** - IaC patterns and examples
- **`references/cost_optimization.md`** - Detailed cost reduction strategies

## Integration with Other Skills

- **security-engineering** - For security architecture
- **network-engineering** - For network design
- **performance** - For optimization strategies
- **devops-runbooks** - For operational procedures
