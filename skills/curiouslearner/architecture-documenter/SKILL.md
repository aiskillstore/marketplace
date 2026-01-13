---
name: architecture-documenter
description: Document system architecture and technical design decisions for effective team communication and ...
---

# Architecture Documenter Skill

Document system architecture and technical design decisions for effective team communication and knowledge sharing.

## Instructions

You are a software architecture documentation expert. When invoked:

1. **Analyze System Architecture**:
   - Identify key components and services
   - Understand data flows and interactions
   - Map dependencies and integrations
   - Recognize architectural patterns
   - Assess scalability and reliability

2. **Create Architecture Documentation**:
   - System overview and context
   - Component diagrams and relationships
   - Data flow diagrams
   - Deployment architecture
   - Security architecture
   - Decision records (ADRs)

3. **Document Technical Decisions**:
   - What was decided
   - Why it was decided
   - Alternatives considered
   - Trade-offs made
   - Implementation details
   - Future considerations

4. **Use Visual Diagrams**:
   - System architecture diagrams
   - Sequence diagrams
   - Entity-relationship diagrams
   - Infrastructure diagrams
   - Network topology
   - State machines

5. **Maintain Living Documentation**:
   - Keep docs synchronized with code
   - Version architecture docs
   - Track evolution over time
   - Mark deprecated components
   - Update with lessons learned

## Architecture Documentation Templates

### System Architecture Document Template

```markdown
# E-Commerce Platform - System Architecture

**Version**: 2.3
**Last Updated**: January 15, 2024
**Status**: Current
**Authors**: Engineering Team
**Reviewers**: Alice (EM), Bob (Tech Lead)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Context](#system-context)
3. [Architecture Overview](#architecture-overview)
4. [Core Components](#core-components)
5. [Data Architecture](#data-architecture)
6. [Infrastructure](#infrastructure)
7. [Security Architecture](#security-architecture)
8. [Scalability & Performance](#scalability--performance)
9. [Deployment](#deployment)
10. [Monitoring & Observability](#monitoring--observability)
11. [Future Considerations](#future-considerations)

---

## Executive Summary

### What This System Does

The E-Commerce Platform is a modern, cloud-native application that enables small to medium businesses to sell products online. It handles the complete e-commerce lifecycle from product catalog management to order fulfillment.

### Key Capabilities

- **Product Management**: Create, update, and manage product catalogs
- **Shopping Experience**: Browse products, search, filter, and compare
- **Checkout & Payments**: Secure checkout with multiple payment options
- **Order Management**: Track orders from placement to delivery
- **User Accounts**: Customer profiles, order history, preferences
- **Admin Dashboard**: Business analytics, inventory management

### System Scale

| Metric | Current | Target (6 months) |
|--------|---------|-------------------|
| Active Users | 5,000 businesses | 15,000 businesses |
| Products | 500,000 | 2,000,000 |
| Daily Orders | 10,000 | 50,000 |
| Monthly GMV | $2M | $10M |
| Peak RPS | 500 | 2,000 |
| Data Storage | 2 TB | 10 TB |

### Technology Stack Summary

- **Frontend**: React, TypeScript, Redux, Material-UI
- **Backend**: Node.js, Express, TypeScript
- **Database**: PostgreSQL (primary), Redis (cache)
- **Storage**: AWS S3
- **Hosting**: AWS (ECS, RDS, ElastiCache, CloudFront)
- **CI/CD**: GitHub Actions
- **Monitoring**: DataDog, Sentry

---

## System Context

### Business Context

**Problem We Solve**: Small businesses struggle with expensive, complex e-commerce solutions. Our platform provides an affordable, easy-to-use alternative.

**Target Users**:
- Small business owners (10-1000 products)
- Digital creators selling physical products
- Retail stores expanding online

**Business Model**: SaaS subscription ($29-$299/month) + transaction fees (2.9% + $0.30)

### System Boundary

```
┌─────────────────────────────────────────────────────┐
│                 E-Commerce Platform                 │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │ Customer │  │ Merchant │  │    Admin     │    │
│  │   Web    │  │Dashboard │  │   Portal     │    │
│  └──────────┘  └──────────┘  └──────────────┘    │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │            Backend Services                   │ │
│  │  (Auth, Product, Order, Payment, etc.)       │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │         Data & Storage Layer                 │ │
│  │     (PostgreSQL, Redis, S3)                  │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌─────────┐   ┌──────────┐   ┌──────────┐
   │ Stripe  │   │  SendGrid│   │  Shippo  │
   │ Payment │   │   Email  │   │ Shipping │
   └─────────┘   └──────────┘   └──────────┘
```

### External Dependencies

| Service | Purpose | SLA | Fallback Strategy |
|---------|---------|-----|-------------------|
| Stripe | Payment processing | 99.99% | Queue retries, manual processing |
| SendGrid | Email delivery | 99.95% | Alternative provider (AWS SES) |
| Shippo | Shipping labels | 99.9% | Manual label generation |
| AWS | Infrastructure | 99.99% | Multi-AZ deployment |
| Cloudflare | CDN/DNS | 99.99% | Direct origin access |

---

## Architecture Overview

### High-Level Architecture

```
                        Internet
                           │
                           ▼
                    ┌──────────────┐
                    │  Cloudflare  │ (CDN, DDoS protection)
                    └──────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   AWS CloudFront     │ (Static assets)
                └──────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌──────────────┐
│    React      │  │  API Gateway  │  │    Admin     │
│   Frontend    │  │  (Express)    │  │   Portal     │
│  (CloudFront) │  │   (ALB+ECS)   │  │              │
└───────────────┘  └───────┬───────┘  └──────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐      ┌──────────┐      ┌──────────┐
   │  Auth   │      │ Product  │      │  Order   │
   │ Service │      │ Service  │      │ Service  │
   └────┬────┘      └────┬─────┘      └────┬─────┘
        │                │                  │
        └────────────────┼──────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │PostgreSQL│     │  Redis  │     │   S3    │
   │  (RDS)   │     │(ElastiCache)  │(Images) │
   └──────────┘     └─────────┘     └─────────┘
```

### Architecture Style

**Primary Pattern**: Modular Monolith (transitioning to Microservices)

**Rationale**:
- **Current**: Modular monolith provides simplicity while maintaining clear boundaries
- **Future**: Easy migration path to microservices as scale increases
- **Trade-off**: Accepts coupling cost for development velocity at current scale

### Key Architectural Principles

1. **Separation of Concerns**: Clear boundaries between modules
2. **API-First**: All features exposed via REST APIs
3. **Stateless Services**: No server-side session state (JWT-based auth)
4. **Caching Strategy**: Cache aggressively, invalidate carefully
5. **Eventual Consistency**: Accept eventual consistency for non-critical data
6. **Fail Fast**: Return errors quickly rather than retry indefinitely
7. **Observability**: Comprehensive logging, metrics, and tracing

---

## Core Components

### Frontend Application

**Technology**: React 18 + TypeScript + Redux Toolkit

**Structure**:
```
client/
├── components/     # Reusable UI components
├── pages/          # Route-level pages
├── store/          # Redux state management
├── api/            # API client
├── hooks/          # Custom React hooks
└── utils/          # Utility functions
```

**Key Features**:
- Server-side rendering (SSR) for SEO
- Code splitting by route
- Progressive Web App (PWA) capabilities
- Optimistic UI updates
- Offline support (service workers)

**State Management**:
- **Redux**: Global application state
- **React Query**: Server state caching
- **Local Storage**: User preferences, cart (guest users)

**Performance Targets**:
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Lighthouse Score: >90

---

### API Gateway

**Technology**: Express.js + TypeScript

**Responsibilities**:
- Request routing
- Authentication/authorization
- Rate limiting
- Request/response transformation
- API versioning
- CORS handling

**Middleware Pipeline**:
```javascript
Request
  ↓
Logging (Morgan)
  ↓
Rate Limiting (express-rate-limit)
  ↓
CORS (cors)
  ↓
Authentication (JWT verification)
  ↓
Authorization (permission check)
  ↓
Request Validation (Joi)
  ↓
Route Handler
  ↓
Response Formatting
  ↓
Error Handling
  ↓
Response
```

**API Versioning Strategy**:
- URL versioning: `/api/v1/products`, `/api/v2/products`
- Maintain 2 versions simultaneously
- Deprecation warnings in headers
- 6-month sunset period for old versions

---

### Service Modules

#### Authentication Service

**Responsibilities**:
- User registration and login
- JWT token generation and validation
- Password reset flow
- OAuth integration (Google, Facebook)
- Multi-factor authentication (MFA)

**Database Schema**:
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  token_hash VARCHAR NOT NULL,
  expires_at TIMESTAMP,
  created_at TIMESTAMP
)

oauth_accounts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  provider VARCHAR NOT NULL, -- 'google', 'facebook'
  provider_user_id VARCHAR NOT NULL,
  access_token VARCHAR,
  refresh_token VARCHAR,
  UNIQUE(provider, provider_user_id)
)
```

**Security Measures**:
- Passwords hashed with Argon2id
- JWT tokens with 15-minute expiration
- Refresh tokens with 7-day expiration
- Rate limiting: 5 login attempts per 15 minutes
- Account lockout after 10 failed attempts
- MFA via TOTP (Google Authenticator)

#### Product Service

**Responsibilities**:
- Product CRUD operations
- Inventory management
- Search and filtering
- Product recommendations
- Category management

**Database Schema**:
```sql
products (
  id UUID PRIMARY KEY,
  merchant_id UUID REFERENCES users(id),
  name VARCHAR NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  inventory_count INTEGER NOT NULL DEFAULT 0,
  category_id UUID REFERENCES categories(id),
  status VARCHAR DEFAULT 'draft', -- draft, active, archived
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

product_images (
  id UUID PRIMARY KEY,
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,
  url VARCHAR NOT NULL,
  position INTEGER,
  created_at TIMESTAMP
)

categories (
  id UUID PRIMARY KEY,
  name VARCHAR NOT NULL,
  parent_id UUID REFERENCES categories(id),
  slug VARCHAR UNIQUE NOT NULL
)
```

**Search Implementation**:
- PostgreSQL full-text search with trigram indexes
- Elasticsearch for advanced features (planned)
- Caching: 5-minute TTL for product lists, 1-hour for individual products

**Performance Optimizations**:
- Database indexes on common query fields
- N+1 query prevention with eager loading
- Image CDN with automatic resizing
- Aggressive caching with Redis

#### Order Service

**Responsibilities**:
- Shopping cart management
- Order creation and processing
- Order status tracking
- Order history
- Invoice generation

**Database Schema**:
```sql
orders (
  id UUID PRIMARY KEY,
  customer_id UUID REFERENCES users(id),
  status VARCHAR NOT NULL, -- pending, paid, shipped, delivered, cancelled
  subtotal DECIMAL(10,2) NOT NULL,
  tax DECIMAL(10,2) NOT NULL,
  shipping DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  payment_id VARCHAR,
  shipping_address_id UUID REFERENCES addresses(id),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

order_items (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  product_snapshot JSONB -- Product details at time of purchase
)

order_events (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  event_type VARCHAR NOT NULL, -- created, paid, shipped, etc.
  metadata JSONB,
  created_at TIMESTAMP
)
```

**Order State Machine**:
```
pending → paid → processing → shipped → delivered
   ↓       ↓         ↓           ↓
   └───────┴─────────┴───────────┴──→ cancelled
```

**Transaction Handling**:
- Database transactions for order creation
- Idempotency keys for payment processing
- Inventory reservation system
- Automatic rollback on payment failure

#### Payment Service

**Responsibilities**:
- Payment intent creation
- Payment processing (via Stripe)
- Refund handling
- Payment method management
- Transaction history

**Integration with Stripe**:
```javascript
// Payment Intent Flow
1. Client requests payment intent
   ↓
2. Server creates Stripe PaymentIntent
   ↓
3. Client collects payment details
   ↓
4. Client confirms payment with Stripe
   ↓
5. Stripe webhook notifies server
   ↓
6. Server updates order status
```

**Webhook Security**:
- Stripe signature verification
- Idempotent webhook processing
- Async processing with job queue
- Retry logic for failed webhooks

**Database Schema**:
```sql
payments (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  stripe_payment_intent_id VARCHAR UNIQUE,
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR NOT NULL, -- pending, succeeded, failed
  payment_method VARCHAR, -- card, bank_transfer
  metadata JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

refunds (
  id UUID PRIMARY KEY,
  payment_id UUID REFERENCES payments(id),
  stripe_refund_id VARCHAR UNIQUE,
  amount DECIMAL(10,2) NOT NULL,
  reason VARCHAR,
  status VARCHAR NOT NULL,
  created_at TIMESTAMP
)
```

---

## Data Architecture

### Database Design

**Primary Database**: PostgreSQL 14

**Schema Organization**:
- **public schema**: Core application tables
- **audit schema**: Audit logs and event sourcing
- **analytics schema**: Denormalized data for reporting

**Connection Pooling**:
```javascript
{
  max: 20,              // Max connections
  min: 5,               // Min connections
  idle: 10000,          // Close idle connections after 10s
  acquire: 30000,       // Max time to acquire connection
  evict: 1000           // Check for idle connections every 1s
}
```

**Backup Strategy**:
- Automated daily backups (RDS snapshots)
- Point-in-time recovery enabled (7-day window)
- Monthly backups retained for 1 year
- Backup tested quarterly

### Caching Strategy

**Redis Configuration**:
- Deployment: AWS ElastiCache (Redis 7.0)
- Mode: Cluster mode enabled
- Nodes: 3 (primary + 2 replicas)
- Eviction policy: LRU (Least Recently Used)

**Cache Patterns**:

1. **Cache-Aside** (Read-heavy data):
```javascript
async function getProduct(id) {
  // Try cache first
  let product = await cache.get(`product:${id}`);

  if (!product) {
    // Cache miss - fetch from database
    product = await db.products.findById(id);

    // Store in cache (1 hour TTL)
    await cache.set(`product:${id}`, product, 3600);
  }

  return product;
}
```

2. **Write-Through** (Critical data):
```javascript
async function updateProduct(id, data) {
  // Update database
  const product = await db.products.update(id, data);

  // Update cache
  await cache.set(`product:${id}`, product, 3600);

  return product;
}
```

**Cache Invalidation**:
```javascript
// Product updated
await cache.del(`product:${productId}`);
await cache.del(`products:merchant:${merchantId}`);
await cache.del(`products:category:${categoryId}`);

// Pattern-based invalidation
await cache.delPattern(`products:*`);
```

**What We Cache**:
| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Product details | 1 hour | Infrequently updated |
| Product lists | 5 minutes | Frequently updated |
| User sessions | 15 minutes | Security requirement |
| Search results | 10 minutes | Expensive queries |
| API responses | 1 minute | Rate limit protection |

### Data Migration Strategy

**Tools**: Prisma Migrate (development), custom scripts (production)

**Migration Process**:
1. Create migration in development
2. Review SQL in PR
3. Test on staging (copy of production data)
4. Run on production during low-traffic window
5. Rollback plan documented

**Zero-Downtime Migrations**:
```sql
-- Example: Adding non-null column

-- Step 1: Add column as nullable
ALTER TABLE products ADD COLUMN new_field VARCHAR;

-- Step 2: Backfill data
UPDATE products SET new_field = 'default_value' WHERE new_field IS NULL;

-- Step 3: Add NOT NULL constraint
ALTER TABLE products ALTER COLUMN new_field SET NOT NULL;
```

---

## Infrastructure

### AWS Architecture

**Regions**: Primary: us-east-1, Disaster Recovery: us-west-2

**VPC Design**:
```
VPC (10.0.0.0/16)
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   ├── NAT Gateways
│   └── Application Load Balancer
└── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
    ├── ECS Tasks (Application)
    ├── RDS (Database)
    └── ElastiCache (Redis)
```

**Compute**:
- **ECS Fargate**: Serverless containers for application
- **Auto-scaling**: Target CPU 70%, min 2 tasks, max 10 tasks
- **Task Definition**:
  ```yaml
  CPU: 1024 (1 vCPU)
  Memory: 2048 MB
  Container Port: 3000
  Environment: Production
  ```

**Database**:
- **RDS PostgreSQL**: db.r5.large (2 vCPU, 16 GB RAM)
- **Multi-AZ**: Yes (automatic failover)
- **Read Replicas**: 1 (for analytics queries)
- **Storage**: 500 GB GP3 (auto-scaling enabled)

**Storage**:
- **S3 Bucket**: product-images-prod
- **Lifecycle Policy**: Move to Glacier after 90 days
- **CDN**: CloudFront distribution for images
- **Backup**: Cross-region replication enabled

**Networking**:
- **Load Balancer**: Application Load Balancer (ALB)
- **SSL/TLS**: ACM certificates (auto-renewal)
- **WAF**: AWS WAF with OWASP rules
- **DDoS Protection**: AWS Shield Standard

### Deployment Architecture

**CI/CD Pipeline** (GitHub Actions):
```
Code Push
  ↓
Automated Tests (Unit + Integration)
  ↓
Linting & Type Checking
  ↓
Build Docker Image
  ↓
Push to ECR (Elastic Container Registry)
  ↓
Deploy to Staging (Auto)
  ↓
Integration Tests (Staging)
  ↓
Manual Approval
  ↓
Deploy to Production (Canary)
  ↓
Monitor Metrics (15 minutes)
  ↓
Full Rollout or Rollback
```

**Deployment Strategy**: Blue-Green with Canary

```
Production (Blue)        Canary (Green)
100% traffic    →   95% / 5% split   →   0% / 100%
                    ↓
              Monitor for 15 min
                    ↓
              Success? Full rollout : Rollback
```

**Rollback Procedure**:
1. Detect issue (automated alerts or manual)
2. Trigger rollback command
3. Route traffic back to previous version
4. Investigate root cause
5. Fix and redeploy

**Deployment Windows**:
- Staging: Anytime
- Production: Tuesday-Thursday, 10 AM - 2 PM EST
- Emergency: 24/7 with on-call approval

---

## Security Architecture

### Defense in Depth

**Layer 1: Network Security**
- VPC isolation
- Security groups (allow-list only)
- Network ACLs
- Private subnets for data layer
- NAT Gateway for outbound traffic

**Layer 2: Application Security**
- Input validation (all user inputs)
- SQL injection prevention (parameterized queries)
- XSS prevention (sanitization + CSP headers)
- CSRF protection (tokens)
- Rate limiting (DDoS mitigation)

**Layer 3: Authentication & Authorization**
- JWT with short expiration
- Refresh token rotation
- MFA for admin accounts
- Role-based access control (RBAC)
- Principle of least privilege

**Layer 4: Data Security**
- Encryption at rest (RDS, S3)
- Encryption in transit (TLS 1.3)
- Secrets in AWS Secrets Manager
- PII data encrypted at field level
- Regular security audits

### Security Headers

```javascript
{
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}
```

### Compliance

**Standards**:
- **PCI DSS**: Level 2 (Stripe handles Level 1)
- **GDPR**: User data rights, deletion, export
- **SOC 2 Type II**: In progress (Q2 2024)

**Data Retention**:
- User data: Retained until account deletion
- Order data: 7 years (regulatory requirement)
- Logs: 90 days
- Backups: 1 year

---

## Scalability & Performance

### Current Capacity

| Metric | Current | Limit | Headroom |
|--------|---------|-------|----------|
| Concurrent Users | 500 | 2,000 | 4x |
| Requests/Second | 200 | 1,000 | 5x |
| Database Connections | 50 | 200 | 4x |
| Storage | 500 GB | 2 TB | 4x |

### Scaling Strategy

**Horizontal Scaling**:
- Stateless services (easy to replicate)
- Auto-scaling based on CPU/memory
- Database read replicas for read-heavy workloads

**Vertical Scaling**:
- Database instance size (scheduled uptime)
- Cache cluster size

**Caching**:
- Application-level caching (Redis)
- CDN for static assets
- Database query result caching

**Database Optimization**:
- Indexes on frequently queried fields
- Materialized views for complex queries
- Connection pooling
- Query optimization (EXPLAIN ANALYZE)

### Performance Budgets

**API Response Times** (p95):
- GET requests: <200ms
- POST requests: <500ms
- Complex queries: <1s

**Frontend Performance** (Lighthouse):
- Performance: >90
- Accessibility: 100
- Best Practices: >90
- SEO: 100

**Database Query Times** (p95):
- Simple queries: <50ms
- Join queries: <100ms
- Aggregations: <500ms

---

## Monitoring & Observability

### Metrics

**Application Metrics** (DataDog):
- Request rate, error rate, duration (RED metrics)
- Active users, sessions
- Business metrics (orders, revenue)
- Custom metrics (cart abandonment, conversion rate)

**Infrastructure Metrics**:
- CPU, memory, disk usage
- Network throughput
- Database connections, query performance
- Cache hit rate

**Dashboards**:
1. **System Health**: Overall system status
2. **API Performance**: Endpoint-specific metrics
3. **Business Metrics**: KPIs and conversions
4. **Database Performance**: Query analysis
5. **Error Tracking**: Error rates and trends

### Logging

**Log Levels**:
- ERROR: Application errors requiring investigation
- WARN: Potential issues or degraded performance
- INFO: Significant events (order created, payment succeeded)
- DEBUG: Detailed diagnostic information (disabled in production)

**Log Aggregation**: CloudWatch Logs → DataDog

**Structured Logging**:
```javascript
logger.info('Order created', {
  orderId: '123',
  customerId: '456',
  total: 99.99,
  timestamp: new Date().toISOString()
});
```

### Alerting

**Alert Channels**:
- Critical: PagerDuty (SMS + Phone)
- High: Slack #incidents
- Medium: Slack #engineering
- Low: Email

**Alert Rules**:
```yaml
- name: High Error Rate
  condition: error_rate > 5% for 5 minutes
  severity: CRITICAL
  channel: PagerDuty

- name: Slow API Response
  condition: p95_latency > 1000ms for 10 minutes
  severity: HIGH
  channel: Slack

- name: Database Connection Pool Exhausted
  condition: db_connections > 180 for 5 minutes
  severity: CRITICAL
  channel: PagerDuty

- name: Low Cache Hit Rate
  condition: cache_hit_rate < 70% for 15 minutes
  severity: MEDIUM
  channel: Slack
```

### Tracing

**Distributed Tracing**: DataDog APM

**Trace Example**:
```
HTTP Request: GET /api/products/123
├─ Authentication Middleware (5ms)
├─ Authorization Middleware (2ms)
├─ Product Service
│  ├─ Cache Lookup (1ms) [MISS]
│  ├─ Database Query (45ms)
│  └─ Cache Set (2ms)
├─ Response Serialization (3ms)
└─ Total: 58ms
```

---

## Future Considerations

### Planned Improvements (Next 6 Months)

1. **Microservices Migration**
   - Extract payment service first
   - Event-driven architecture with message queue
   - Service mesh (Istio) for inter-service communication

2. **Search Enhancement**
   - Migrate to Elasticsearch
   - Implement faceted search
   - Add product recommendations (ML-based)

3. **Performance Optimization**
   - Implement GraphQL (reduce over-fetching)
   - Server-side rendering for better SEO
   - Optimize database queries (20% improvement target)

4. **Infrastructure**
   - Multi-region deployment for lower latency
   - Kubernetes migration (from ECS)
   - Serverless functions for background jobs

### Technical Debt

**High Priority**:
- Upgrade Node.js from v16 to v20
- Migrate from class components to hooks (React)
- Implement comprehensive integration tests
- Refactor legacy authentication code

**Medium Priority**:
- Standardize error handling across services
- Improve API documentation (OpenAPI spec)
- Add end-to-end tests for critical flows

**Low Priority**:
- Migrate from REST to GraphQL
- Implement BFF (Backend for Frontend) pattern
- Add feature flags system

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database becomes bottleneck | HIGH | MEDIUM | Read replicas, caching, sharding plan |
| Monolith difficult to scale | MEDIUM | HIGH | Modular architecture, migration plan |
| Third-party service outage | HIGH | LOW | Fallback strategies, circuit breakers |
| Security breach | CRITICAL | LOW | Regular audits, penetration testing |
| Key engineer departure | MEDIUM | MEDIUM | Documentation, knowledge sharing |

---

## Appendices

### Glossary

- **GMV**: Gross Merchandise Value
- **RPS**: Requests Per Second
- **p95**: 95th percentile
- **TTL**: Time To Live
- **CDN**: Content Delivery Network
- **WAF**: Web Application Firewall

### References

- [Architecture Decision Records](docs/adr/)
- [API Documentation](docs/api/)
- [Runbooks](docs/runbooks/)
- [Database Schema](docs/schema/)
- [Security Policy](docs/security/)

### Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.3 | 2024-01-15 | Added canary deployment strategy | Alice |
| 2.2 | 2023-12-01 | Updated infrastructure (ECS migration) | Bob |
| 2.1 | 2023-10-15 | Added security architecture section | Frank |
| 2.0 | 2023-09-01 | Major revision - microservices plan | Alice, Bob |

---

**Document Status**: Current
**Next Review**: April 15, 2024
**Maintained By**: Engineering Team
**Questions**: #architecture on Slack
```

### Architecture Decision Record (ADR) Template

```markdown
# ADR-015: Migrate from Sessions to JWT Authentication

**Status**: Accepted
**Date**: January 15, 2024
**Decision Makers**: Alice (EM), Bob (Tech Lead), Carol (Frontend Lead)
**Consulted**: Security Team, DevOps Team

---

## Context

Our current authentication system uses server-side sessions stored in Redis. As we scale to support more users and prepare for multi-region deployment, session management has become a bottleneck.

### Current State

**Session-Based Authentication**:
```javascript
// Login creates server-side session
app.post('/login', (req, res) => {
  const user = authenticate(req.body);
  req.session.userId = user.id;  // Stored in Redis
  res.json({ success: true });
});

// Each request validates session
app.use((req, res, next) => {
  if (req.session.userId) {
    req.user = await getUser(req.session.userId);
  }
  next();
});
```

**Problems**:
1. **Scalability**: Every request requires Redis lookup (adds 5-10ms latency)
2. **Complexity**: Session replication across regions is complex
3. **Memory**: 50,000 active sessions = 250MB Redis memory
4. **Stateful**: Cannot easily add new servers (sticky sessions required)

### Requirements

1. **Stateless**: No server-side session storage
2. **Scalable**: Support 50k+ concurrent users
3. **Secure**: Resistant to common attacks (XSS, CSRF, token theft)
4. **Fast**: Minimal performance impact (<1ms overhead)
5. **Compatible**: Work with existing mobile apps

---

## Decision

We will migrate from session-based authentication to JSON Web Tokens (JWT).

### Implementation

**JWT-Based Authentication**:
```javascript
// Login generates JWT
app.post('/login', (req, res) => {
  const user = authenticate(req.body);

  const accessToken = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    { userId: user.id },
    process.env.REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  res.json({ accessToken, refreshToken });
});

// Each request validates JWT (no database lookup)
app.use((req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
});
```

### Token Structure

**Access Token** (short-lived):
- Payload: `{ userId, role, permissions }`
- Expiration: 15 minutes
- Signature: HMAC SHA256

**Refresh Token** (long-lived):
- Payload: `{ userId }`
- Expiration: 7 days
- Stored hash in database (for revocation)

---

## Alternatives Considered

### Alternative 1: Keep Session-Based Auth

**Pros**:
- No migration needed
- Familiar to team
- Easy to revoke access (delete session)

**Cons**:
- Scalability issues persist
- Complex multi-region setup
- Requires sticky sessions (load balancer complexity)

**Decision**: Rejected due to scalability concerns

---

### Alternative 2: OAuth 2.0 Only

**Pros**:
- Industry standard
- Delegation capabilities
- Well-tested security

**Cons**:
- Overkill for our use case
- Complex implementation
- Requires authorization server
- Users expect username/password

**Decision**: Rejected - too complex for current needs. Will add OAuth as option later.

---

### Alternative 3: API Keys

**Pros**:
- Simple implementation
- Stateless
- Easy to revoke

**Cons**:
- No expiration (security risk)
- Not suitable for user authentication
- No claims/scopes

**Decision**: Rejected - better suited for programmatic access, not user auth

---

## Consequences

### Positive

1. **Performance**: Eliminate Redis lookup on every request
   - Estimated improvement: 5-10ms per request
   - Reduces Redis load by 80%

2. **Scalability**: Stateless servers
   - No sticky sessions needed
   - Easy horizontal scaling
   - Multi-region deployment simplified

3. **Mobile Support**: Better mobile app experience
   - Tokens stored locally
   - No cookies required
   - Offline token validation

4. **Developer Experience**: Simpler architecture
   - No session middleware
   - Easier testing (no session state)
   - Clear token lifecycle

### Negative

1. **Token Revocation**: Cannot immediately revoke access
   - **Mitigation**: Short token expiration (15 min)
   - **Mitigation**: Refresh token blacklist
   - **Mitigation**: Emergency: force re-auth for all users

2. **Token Size**: JWTs larger than session IDs
   - Session ID: ~32 bytes
   - JWT: ~200 bytes
   - **Impact**: Minimal (200 bytes per request is acceptable)

3. **Secret Management**: JWT secrets are critical
   - **Mitigation**: Store in AWS Secrets Manager
   - **Mitigation**: Rotate secrets quarterly
   - **Mitigation**: Different secrets per environment

4. **XSS Risk**: Tokens accessible to JavaScript
   - **Mitigation**: Store in httpOnly cookies (where possible)
   - **Mitigation**: Strict Content Security Policy
   - **Mitigation**: Short token expiration

### Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| JWT secret leaked | CRITICAL | Secrets Manager, rotation, monitoring |
| Cannot revoke compromised token | HIGH | Short expiration, refresh token blacklist |
| Algorithm confusion attack | MEDIUM | Explicitly specify algorithm in verification |
| Replay attacks | MEDIUM | Short expiration, HTTPS only |

---

## Implementation Plan

### Phase 1: Preparation (Week 1-2)
- [ ] Create JWT utility functions
- [ ] Update authentication middleware
- [ ] Add refresh token endpoint
- [ ] Write migration guide for frontend team
- [ ] Set up secrets in AWS Secrets Manager

### Phase 2: Backend Migration (Week 3-4)
- [ ] Deploy JWT endpoints alongside session endpoints
- [ ] Add feature flag for JWT authentication
- [ ] Comprehensive testing (unit + integration)
- [ ] Load testing with JWTs
- [ ] Security review

### Phase 3: Frontend Migration (Week 5-6)
- [ ] Update web app to use JWT
- [ ] Update mobile apps to use JWT
- [ ] Gradual rollout (10% → 50% → 100%)
- [ ] Monitor error rates and performance

### Phase 4: Cleanup (Week 7-8)
- [ ] Remove session-based auth code
- [ ] Remove Redis session storage
- [ ] Update documentation
- [ ] Postmortem and lessons learned

### Rollback Plan

If critical issues arise:
1. Disable JWT feature flag
2. Route all traffic to session endpoints
3. Keep JWT code for investigation
4. Identify and fix issues
5. Resume migration

---

## Metrics for Success

**Performance**:
- [ ] Average request latency reduced by 5ms
- [ ] p95 latency reduced by 10ms
- [ ] Redis CPU usage reduced by 80%

**Reliability**:
- [ ] No increase in authentication errors
- [ ] <0.1% token validation failures
- [ ] Zero security incidents

**User Experience**:
- [ ] Login flow unchanged (transparent migration)
- [ ] No increase in support tickets
- [ ] Mobile app performance improved

---

## Security Considerations

**Token Security**:
- Tokens signed with HS256 (HMAC SHA256)
- Secrets: 256-bit randomly generated
- Secrets rotated quarterly
- Algorithm specified in verification (prevent algorithm confusion)

**Storage**:
- Web: httpOnly cookies (prevents XSS)
- Mobile: Secure storage (Keychain/Keystore)
- Never in localStorage (XSS vulnerable)

**Transmission**:
- HTTPS only (TLS 1.3)
- Secure, SameSite=Strict cookies
- No tokens in URLs (log exposure)

**Validation**:
- Verify signature
- Check expiration
- Validate issuer and audience
- Check token not blacklisted (refresh tokens)

---

## References

- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [Auth0 JWT Handbook](https://auth0.com/resources/ebooks/jwt-handbook)
- Internal: [Security Best Practices](docs/security-best-practices.md)

---

## Updates

| Date | Update | Author |
|------|--------|--------|
| 2024-01-15 | Initial ADR created | Bob |
| 2024-01-20 | Added security review feedback | Frank |
| 2024-02-01 | Updated after implementation | Bob |

---

**Status**: Accepted
**Supersedes**: ADR-008 (Session-based Authentication)
**Related**: ADR-012 (API Security), ADR-014 (Multi-region Deployment)
```

## Usage Examples

```
@architecture-documenter
@architecture-documenter --type system-overview
@architecture-documenter --type adr
@architecture-documenter --focus security
@architecture-documenter --focus scalability
@architecture-documenter --include-diagrams
@architecture-documenter --update-existing
```

## Best Practices

### Document Architecture Decisions

**When to create an ADR**:
- Significant technical decisions
- Architecture changes
- Technology choices
- Process changes
- Security decisions

**ADR Structure**:
1. **Context**: What's the situation?
2. **Decision**: What did we decide?
3. **Alternatives**: What else did we consider?
4. **Consequences**: What are the impacts?

### Use Visual Diagrams

**Diagram Types**:
- **System Context**: Show system boundaries
- **Container**: Show high-level architecture
- **Component**: Show internal structure
- **Code**: Show class/module relationships
- **Deployment**: Show infrastructure
- **Sequence**: Show interactions over time

**Tools**:
- Diagrams as code: Mermaid, PlantUML
- Visual tools: Lucidchart, Draw.io
- Cloud-specific: AWS Architecture Diagrams

### Keep Documentation Current

**Documentation Lifecycle**:
- Create during design phase
- Review in code review
- Update with implementation changes
- Quarterly architecture review
- Archive outdated docs (don't delete)

**Version Control**:
- Store docs with code
- Version alongside releases
- Link docs to specific code versions
- Maintain changelog

### Make It Discoverable

**Organization**:
- Central location (wiki, docs folder)
- Clear naming conventions
- Table of contents
- Cross-references
- Search-friendly

**Accessibility**:
- Public within organization
- Easy to navigate
- Multiple entry points
- Links from README

## Notes

- Architecture documentation is for communication, not perfection
- Diagrams speak louder than words - use them liberally
- ADRs capture decisions and context for future reference
- Keep docs synchronized with code changes
- Version architecture docs alongside code
- Regular reviews prevent documentation drift
- Good architecture docs reduce onboarding time significantly
- Document the "why" not just the "what"
- Include trade-offs and alternatives considered
- Make security and scalability explicit
- Link architecture to business goals
- Use consistent notation and terminology
