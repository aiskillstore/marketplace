---
name: technical-analysis
description: Technical analysis capabilities for APIs, data models, integrations, and security requirements. Use when analyzing technical aspects of systems or documenting technical requirements.
allowed-tools: Read, Grep, Glob, LSP
---

# Technical Analysis Skill

## Overview

This skill provides techniques for analyzing technical aspects of software systems including APIs, data models, integrations, and security requirements.

## API Analysis

### REST API Analysis

#### Endpoint Discovery
Look for these patterns:
- Route definitions
- Controller classes
- OpenAPI/Swagger specifications
- API documentation

#### Endpoint Documentation Template
```markdown
### Endpoint: {METHOD} {PATH}

**Purpose**: {DESCRIPTION}

**Authentication**: {AUTH_METHOD}

**Request**:
- Headers: {HEADERS}
- Parameters: {PARAMS}
- Body: {BODY_SCHEMA}

**Response**:
- Success (200): {SUCCESS_SCHEMA}
- Error (4xx/5xx): {ERROR_SCHEMA}

**Business Rules**:
- {RULE_1}
- {RULE_2}
```

#### API Quality Checklist
- [ ] Consistent naming conventions
- [ ] Proper HTTP methods used
- [ ] Appropriate status codes
- [ ] Error responses standardized
- [ ] Pagination implemented for lists
- [ ] Versioning strategy in place
- [ ] Rate limiting configured
- [ ] Authentication documented

### GraphQL API Analysis

#### Schema Analysis
```graphql
type Query {
  user(id: ID!): User
  orders(userId: ID!, status: OrderStatus): [Order]
}

type Mutation {
  createOrder(input: CreateOrderInput!): Order
  updateOrderStatus(id: ID!, status: OrderStatus!): Order
}
```

#### Document
- Queries available (read operations)
- Mutations available (write operations)
- Types and their relationships
- Required vs optional fields
- Custom scalars
- Directives used

### Message/Event APIs

#### Event Schema Documentation
```markdown
### Event: {EVENT_NAME}

**Topic/Queue**: {TOPIC}
**Producer**: {PRODUCER_SERVICE}
**Consumers**: {CONSUMER_LIST}

**Payload Schema**:
{JSON_SCHEMA}

**Business Trigger**: {WHEN_PUBLISHED}
**Expected Response**: {CONSUMER_BEHAVIOR}
```

## Data Model Analysis

### Entity Analysis

#### Entity Documentation Template
```markdown
## Entity: {ENTITY_NAME}

### Description
{BUSINESS_DESCRIPTION}

### Attributes
| Name | Type | Required | Description | Constraints |
|------|------|----------|-------------|-------------|
| id | UUID | Yes | Primary key | Auto-generated |
| name | string | Yes | Display name | Max 100 chars |
| status | enum | Yes | Current state | Active, Inactive |

### Relationships
| Related Entity | Type | Description |
|---------------|------|-------------|
| Order | 1:N | Customer has many orders |
| Address | 1:1 | Customer has one address |

### Business Rules
- {RULE_1}
- {RULE_2}

### Indexes
| Index Name | Columns | Purpose |
|------------|---------|---------|
| idx_email | email | Unique lookup |
```

### Data Flow Analysis

#### Data Flow Documentation
```markdown
## Data Flow: {FLOW_NAME}

### Overview
{DESCRIPTION}

### Source
- System: {SOURCE_SYSTEM}
- Entity: {SOURCE_ENTITY}
- Trigger: {TRIGGER_EVENT}

### Transformations
1. {TRANSFORMATION_1}
2. {TRANSFORMATION_2}

### Destination
- System: {DEST_SYSTEM}
- Entity: {DEST_ENTITY}
- Action: {CREATE/UPDATE/DELETE}

### Error Handling
- {ERROR_SCENARIO}: {HANDLING}

### Diagram
[Source] → [Transform] → [Destination]
```

### Database Schema Analysis

#### Schema Documentation
```markdown
## Table: {TABLE_NAME}

### Columns
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | No | auto | Primary key |

### Constraints
| Name | Type | Definition |
|------|------|------------|
| pk_table | Primary Key | (id) |
| fk_user | Foreign Key | user_id → users(id) |
| chk_status | Check | status IN ('A', 'I') |

### Indexes
| Name | Columns | Unique | Purpose |
|------|---------|--------|---------|
| idx_email | email | Yes | Lookup |
```

## Integration Analysis

### Integration Point Documentation

```markdown
## Integration: {INTEGRATION_NAME}

### Overview
| Attribute | Value |
|-----------|-------|
| External System | {SYSTEM_NAME} |
| Integration Type | API / File / Message Queue / Database |
| Direction | Inbound / Outbound / Bidirectional |
| Frequency | Real-time / Batch / Event-driven |
| Protocol | REST / SOAP / SFTP / MQ / etc. |

### Data Exchange
| Data Element | Source | Destination | Transform |
|--------------|--------|-------------|-----------|
| Customer ID | System A | System B | Direct map |
| Order Total | System A | System B | Convert currency |

### Authentication
- Method: {AUTH_METHOD}
- Credentials: {CREDENTIAL_LOCATION}
- Rotation: {ROTATION_POLICY}

### Error Handling
| Error Type | Detection | Response | Retry |
|------------|-----------|----------|-------|
| Timeout | 30s limit | Log + Alert | 3x exponential |
| 4xx Error | Response code | Log + Skip | No retry |
| 5xx Error | Response code | Log + Alert | 3x exponential |

### SLA
- Availability: {UPTIME_REQUIREMENT}
- Response Time: {LATENCY_REQUIREMENT}
- Throughput: {VOLUME_REQUIREMENT}

### Monitoring
- Health Check: {ENDPOINT}
- Metrics: {METRICS_COLLECTED}
- Alerts: {ALERT_CONDITIONS}
```

### Integration Pattern Analysis

#### Synchronous Patterns
- **Request-Response**: Direct API calls
- **API Gateway**: Centralized routing
- **Service Mesh**: Sidecar proxies

#### Asynchronous Patterns
- **Message Queue**: Point-to-point messaging
- **Publish-Subscribe**: Event distribution
- **Event Sourcing**: Event log as source of truth

#### Data Integration Patterns
- **ETL**: Extract, Transform, Load
- **Change Data Capture**: Real-time sync
- **Data Virtualization**: On-demand access

## Security Analysis

### Security Requirements Documentation

#### Authentication Analysis
```markdown
## Authentication

### Current Implementation
- Method: {JWT / OAuth2 / SAML / etc.}
- Identity Provider: {IDP_NAME}
- Token Lifetime: {DURATION}
- Refresh Strategy: {STRATEGY}

### Multi-Factor Authentication
- Required For: {USER_TYPES}
- Methods: {MFA_METHODS}
- Bypass Conditions: {EXCEPTIONS}

### Session Management
- Timeout: {IDLE_TIMEOUT}
- Concurrent Sessions: {ALLOWED / PREVENTED}
- Session Storage: {MECHANISM}
```

#### Authorization Analysis
```markdown
## Authorization

### Access Control Model
- Type: RBAC / ABAC / ACL / Custom

### Roles
| Role | Description | User Count |
|------|-------------|------------|
| Admin | Full access | 5 |
| Manager | Department access | 20 |
| User | Limited access | 500 |

### Permissions Matrix
| Resource | Admin | Manager | User |
|----------|-------|---------|------|
| Users | CRUD | R | - |
| Orders | CRUD | CRUD | CRU |
| Reports | CRUD | R | R |

### Business Rules
- {RULE_1}
- {RULE_2}
```

#### Data Protection Analysis
```markdown
## Data Protection

### Sensitive Data Inventory
| Data Element | Classification | Protection |
|--------------|----------------|------------|
| Password | Secret | Hashed (bcrypt) |
| SSN | PII | Encrypted at rest |
| Credit Card | PCI | Tokenized |

### Encryption
- At Rest: {METHOD}
- In Transit: {METHOD}
- Key Management: {STRATEGY}

### Data Masking
| Field | Mask Type | Example |
|-------|-----------|---------|
| SSN | Partial | ***-**-1234 |
| Email | Partial | j***@***.com |
```

### Compliance Analysis

```markdown
## Compliance Requirements

### Applicable Regulations
| Regulation | Scope | Requirements |
|------------|-------|--------------|
| GDPR | EU users | Consent, Right to erasure |
| HIPAA | Health data | PHI protection |
| PCI-DSS | Payment data | Card data security |

### Compliance Controls
| Control | Implementation | Evidence |
|---------|----------------|----------|
| Access logging | Audit table | Logs |
| Encryption | AES-256 | Config |
| Retention | 7 years | Policy doc |

### Audit Requirements
- Audit logging enabled: {YES/NO}
- Retention period: {DURATION}
- Access review frequency: {FREQUENCY}
```

## Infrastructure Analysis

### Infrastructure Documentation

```markdown
## Infrastructure Overview

### Environments
| Environment | Purpose | URL |
|-------------|---------|-----|
| Development | Dev testing | dev.app.com |
| Staging | Pre-prod testing | staging.app.com |
| Production | Live system | app.com |

### Compute
| Component | Type | Specs | Count |
|-----------|------|-------|-------|
| Web Server | VM/Container | 4 CPU, 8GB | 3 |
| API Server | Container | 2 CPU, 4GB | 5 |
| Database | RDS | db.r5.large | 2 |

### Networking
- VPC/VNET: {NETWORK_ID}
- Subnets: {SUBNET_LIST}
- Load Balancer: {LB_TYPE}
- CDN: {CDN_PROVIDER}

### Storage
| Type | Purpose | Size | Backup |
|------|---------|------|--------|
| RDS | Primary DB | 500GB | Daily |
| S3 | File storage | 1TB | Cross-region |
| Redis | Cache | 10GB | None |
```

## Analysis Output Summary

After technical analysis, document:

1. **API Contracts**: All endpoints with schemas
2. **Data Models**: Entities, relationships, constraints
3. **Integrations**: External systems, data flows
4. **Security**: Auth, authorization, data protection
5. **Infrastructure**: Compute, storage, networking
6. **Technical Debt**: Issues and recommendations

See [integration-patterns.md](integration-patterns.md) for common integration patterns.
