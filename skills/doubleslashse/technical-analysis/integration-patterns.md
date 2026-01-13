# Integration Patterns Reference

## Synchronous Integration Patterns

### Request-Response (REST/HTTP)

```
[Client] ──HTTP Request──> [Server]
[Client] <──HTTP Response── [Server]
```

**Use When:**
- Immediate response required
- Simple point-to-point integration
- Low latency tolerance

**Considerations:**
- Tight coupling between systems
- Failure impacts caller directly
- Need timeout handling
- Connection pool management

**Requirement Implications:**
- Define timeout requirements
- Specify retry behavior
- Document error response handling
- Establish SLA expectations

### API Gateway Pattern

```
                    ┌─> [Service A]
[Client] ──> [Gateway] ─> [Service B]
                    └─> [Service C]
```

**Use When:**
- Multiple backend services
- Cross-cutting concerns (auth, logging)
- Rate limiting needed
- Protocol translation required

**Considerations:**
- Single point of failure
- Added latency
- Gateway must scale with traffic

**Requirement Implications:**
- Document routing rules
- Specify authentication flow
- Define rate limits
- Establish monitoring requirements

### Service Mesh Pattern

```
[Service A + Sidecar] <──> [Service B + Sidecar]
         │                        │
         └────── [Control Plane] ─┘
```

**Use When:**
- Complex microservices environment
- Need service-to-service security
- Advanced traffic management
- Observability requirements

**Considerations:**
- Infrastructure complexity
- Resource overhead
- Operational expertise needed

## Asynchronous Integration Patterns

### Message Queue (Point-to-Point)

```
[Producer] ──> [Queue] ──> [Consumer]
```

**Use When:**
- Decoupled processing
- Load leveling needed
- Guaranteed delivery required
- Order matters (FIFO)

**Considerations:**
- Message persistence
- Dead letter handling
- Exactly-once vs at-least-once
- Queue depth monitoring

**Requirement Implications:**
- Define message retention
- Specify delivery guarantees
- Document ordering requirements
- Establish DLQ handling

### Publish-Subscribe

```
                    ┌─> [Subscriber A]
[Publisher] ──> [Topic] ─> [Subscriber B]
                    └─> [Subscriber C]
```

**Use When:**
- Multiple consumers for same event
- Loose coupling required
- Fan-out pattern needed
- Event notification scenarios

**Considerations:**
- Message ordering per partition
- Subscriber management
- Replay capability
- Consumer group handling

**Requirement Implications:**
- Define event schema/contract
- Specify subscriber filtering
- Document replay requirements
- Establish schema versioning

### Event Sourcing

```
[Command] ──> [Event Store] ──> [Read Model]
                   │
                   └── [Event 1, Event 2, Event 3...]
```

**Use When:**
- Complete audit trail needed
- Temporal queries required
- Event replay capabilities
- Complex domain logic

**Considerations:**
- Event schema evolution
- Eventual consistency
- Storage requirements
- Rebuild time for projections

**Requirement Implications:**
- Define event versioning strategy
- Specify consistency requirements
- Document snapshot strategy
- Establish replay procedures

### CQRS (Command Query Responsibility Segregation)

```
[Commands] ──> [Write Model] ──> [Event Bus] ──> [Read Model] <── [Queries]
```

**Use When:**
- Different read/write patterns
- High read scalability needed
- Complex write validation
- Multiple read representations

**Considerations:**
- Eventual consistency
- Synchronization complexity
- Data duplication

## Data Integration Patterns

### ETL (Extract, Transform, Load)

```
[Source] ──Extract──> [Staging] ──Transform──> [Target]
                                      │
                                   [Load]
```

**Use When:**
- Batch data processing
- Data warehousing
- Historical data migration
- Scheduled synchronization

**Considerations:**
- Processing window constraints
- Data volume impacts
- Error handling and recovery
- Data quality validation

**Requirement Implications:**
- Define batch schedule
- Specify data validation rules
- Document error handling
- Establish data retention

### Change Data Capture (CDC)

```
[Source DB] ──Change Log──> [CDC Tool] ──> [Target]
```

**Use When:**
- Near real-time sync needed
- Minimal source impact required
- Incremental changes tracking
- Event generation from DB

**Considerations:**
- Log retention requirements
- Schema change handling
- Performance impact on source

### Data Virtualization

```
[Client] ──Query──> [Virtualization Layer] ──> [Source A]
                            │
                            └──> [Source B]
```

**Use When:**
- On-demand data access
- Multiple data sources
- No data movement desired
- Real-time data needed

**Considerations:**
- Query performance
- Source availability dependency
- Complex joins across sources

## File-Based Integration Patterns

### Batch File Transfer

```
[System A] ──> [File] ──> [Transfer] ──> [System B]
                              │
                          [SFTP/S3]
```

**Use When:**
- Legacy system integration
- Large data volumes
- Non-real-time acceptable
- Simple implementation needed

**Considerations:**
- File format standards
- Transfer security
- Acknowledgment handling
- Error file management

**Requirement Implications:**
- Define file format spec
- Specify naming conventions
- Document transfer schedule
- Establish reconciliation process

### Shared Database

```
[System A] ──Read/Write──> [Database] <──Read/Write── [System B]
```

**Use When:**
- Tight integration needed
- Simple architecture desired
- Same technology stack

**Considerations:**
- Schema coupling
- Concurrency issues
- Performance contention
- Schema change coordination

**Anti-pattern warning**: Generally avoid - creates tight coupling

## Error Handling Patterns

### Retry with Exponential Backoff

```
Attempt 1 ── Fail ── Wait 1s
Attempt 2 ── Fail ── Wait 2s
Attempt 3 ── Fail ── Wait 4s
Attempt 4 ── Success
```

**Implementation:**
- Initial delay
- Multiplier
- Maximum retries
- Maximum delay cap
- Jitter for thundering herd

### Circuit Breaker

```
[Closed] ──Failures exceed threshold──> [Open]
   ^                                        │
   │                                        │
   └──Success──[Half-Open]<──Timeout────────┘
```

**States:**
- Closed: Normal operation
- Open: Fail fast, no calls
- Half-Open: Limited testing

**Configuration:**
- Failure threshold
- Timeout duration
- Success threshold for recovery

### Dead Letter Queue

```
[Queue] ──Process──> [Consumer]
   │                     │
   │                  [Fail]
   │                     │
   └─────────────> [DLQ] ──> [Alert/Manual Review]
```

**Handling:**
- Move failed messages
- Preserve original message
- Add failure metadata
- Enable replay

## Security Patterns

### OAuth2 / OpenID Connect

```
[Client] ──> [Auth Server] ──> [Token]
                                  │
[Client] + Token ──> [Resource Server]
```

**Flows:**
- Authorization Code (web apps)
- Client Credentials (service-to-service)
- Implicit (deprecated)
- Device Code (IoT)

### API Key Authentication

```
[Client] + API-Key Header ──> [API Gateway] ──> [Backend]
```

**Use When:**
- Simple integration needed
- Server-to-server calls
- Rate limiting by key

### mTLS (Mutual TLS)

```
[Client + Cert] <──Verify──> [Server + Cert]
```

**Use When:**
- Zero-trust networking
- High security requirements
- Service mesh environments

## Integration Analysis Checklist

When analyzing integrations, document:

- [ ] **Integration type**: Sync/Async/File/Database
- [ ] **Protocol**: REST/SOAP/MQ/SFTP/etc.
- [ ] **Authentication**: OAuth/API Key/mTLS/etc.
- [ ] **Data format**: JSON/XML/CSV/Binary
- [ ] **Error handling**: Retry/Circuit breaker/DLQ
- [ ] **Monitoring**: Health checks/Metrics/Alerts
- [ ] **SLA**: Availability/Latency/Throughput
- [ ] **Security**: Encryption/Access control/Audit
- [ ] **Data mapping**: Field transformations
- [ ] **Dependencies**: External systems required
