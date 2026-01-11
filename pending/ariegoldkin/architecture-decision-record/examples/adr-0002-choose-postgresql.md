---
adr: 0002
title: Choose PostgreSQL as Primary Database
status: Accepted
date: 2024-10-15
decision_makers: Backend Architect, DevOps Lead, CTO
---

# ADR-0002: Choose PostgreSQL as Primary Database

## Status

**Accepted** (2024-10-15)

## Context

As we transition to microservices architecture (see ADR-0001), we need to select a database that supports our requirements for each service.

**Current Situation:**
- Monolith uses MySQL 5.7 (3 years old, not actively maintained by team)
- Database handles 2M+ transactions daily
- Growing need for complex queries and analytics
- Team experienced with SQL but not database administration

**Requirements:**
- ACID compliance for financial transactions
- Support for complex joins and aggregations
- JSON document storage for flexible schemas
- Full-text search capabilities
- Strong community and tooling support
- Open source (no vendor lock-in)
- Cloud-native deployment ready (RDS, Cloud SQL)

**Constraints:**
- Budget: $2,000/month for database infrastructure
- Timeline: Migration must complete within 4 months
- Team: 5 backend developers (3 senior, 2 mid-level)
- Data volume: 500GB current, projected 2TB in 2 years

## Decision

We will adopt **PostgreSQL 15+** as our primary relational database for all microservices.

**Specific Choices:**

1. **Version**: PostgreSQL 15.4 (stable, long-term support)

2. **Deployment**:
   - **Production**: AWS RDS for PostgreSQL (Multi-AZ)
   - **Staging**: AWS RDS Single-AZ
   - **Development**: Docker containers (postgres:15.4-alpine)

3. **Architecture**:
   - **Database-per-Service**: Each microservice owns its database
   - **Connection Pooling**: PgBouncer in transaction mode
   - **Read Replicas**: For analytics and reporting workloads

4. **Extensions to Enable**:
   - `pg_trgm` - Full-text search and fuzzy matching
   - `pgcrypto` - Encryption functions
   - `uuid-ossp` - UUID generation
   - `pg_stat_statements` - Query performance monitoring

5. **Migration Strategy**:
   - **Phase 1** (Month 1): Set up PostgreSQL infrastructure
   - **Phase 2** (Months 2-3): Migrate service by service (start with Notification Service)
   - **Phase 3** (Month 4): Parallel running, validate data consistency
   - **Phase 4** (Month 4): Cut over, decommission MySQL

6. **Data Migration Tools**:
   - `pgloader` for MySQL → PostgreSQL migration
   - Custom validation scripts for data integrity checks
   - Blue-green deployment for zero-downtime cutover

## Consequences

### Positive

✅ **JSONB Support**: Native JSON storage with indexing and querying
- Allows flexible schemas without separate NoSQL database
- Example: User preferences, feature flags, configuration

✅ **Advanced SQL Features**:
- Window functions for analytics
- CTEs (Common Table Expressions) for complex queries
- Array types and operators
- GIN/GiST indexes for specialized queries

✅ **Strong ACID Guarantees**:
- Reliable for financial transactions
- Multi-version concurrency control (MVCC)
- No phantom reads or dirty writes

✅ **Full-Text Search**:
- Built-in full-text search (no need for Elasticsearch initially)
- Trigram indexes for fuzzy matching
- Language-aware text search

✅ **Extension Ecosystem**:
- PostGIS for geospatial data (future use case)
- TimescaleDB for time-series data (analytics)
- Citus for horizontal scaling (if needed)

✅ **Performance**:
- Faster complex queries compared to MySQL
- Better query planner and optimizer
- Parallel query execution (PostgreSQL 15+)

✅ **Community & Tooling**:
- Excellent documentation
- Active community support
- Rich ecosystem (pgAdmin, DataGrip, DBeaver)
- AWS RDS fully managed service

✅ **Cost Efficiency**:
- Open source (no licensing fees)
- RDS pricing competitive: ~$1,500/month estimated

### Negative

⚠️ **Migration Complexity**:
- 4-month migration timeline is tight
- Data type differences (MySQL ENUM → PostgreSQL CHECK constraints)
- Syntax differences in stored procedures
- Potential query rewrites needed

⚠️ **Learning Curve**:
- Team needs training on PostgreSQL-specific features
- Different performance tuning approach
- New backup/restore procedures

⚠️ **Operational Changes**:
- Need to learn PostgreSQL-specific monitoring (pg_stat_* views)
- Different VACUUM and ANALYZE maintenance
- Connection pooling setup (PgBouncer)

⚠️ **Lock Management**:
- Different locking behavior than MySQL
- Need to understand MVCC implications
- Potential for lock contention in high-write scenarios

⚠️ **Replication Lag**:
- Read replicas may lag in high-write scenarios
- Need monitoring for replication lag alerts

### Neutral

🔄 **Backward Compatibility**:
- Some queries will need rewriting
- Stored procedures incompatible (MySQL → PL/pgSQL)
- Date/time functions have different names

🔄 **Monitoring**:
- Different metrics to track (pg_stat_activity, pg_stat_database)
- New alerts to configure
- Learning RDS CloudWatch metrics

## Alternatives Considered

### Alternative 1: MySQL 8.0 (Upgrade Current)

**Description:**
- Upgrade existing MySQL 5.7 to MySQL 8.0
- Maintain current knowledge and tooling

**Pros:**
- Team already familiar with MySQL
- Minimal learning curve
- Existing queries mostly compatible
- MySQL 8.0 has JSON support (added in 5.7+)
- Lower migration risk

**Cons:**
- JSON support less mature than PostgreSQL JSONB
- No native full-text search (would need Elasticsearch)
- Weaker query optimizer for complex queries
- Less extensible (no extension ecosystem)
- MySQL future uncertain (Oracle ownership concerns)

**Why not chosen:**
We need the advanced features PostgreSQL offers (JSONB, full-text search, extensions). The investment in migration pays off with long-term capabilities.

### Alternative 2: MongoDB (Document Database)

**Description:**
- Use MongoDB for all services
- NoSQL document-oriented approach

**Pros:**
- Excellent JSON document support
- Horizontal scaling built-in (sharding)
- Flexible schemas
- Great for rapidly evolving data models

**Cons:**
- **No ACID transactions** across collections (before v4.0)
- Difficult to model relational data
- Team has no MongoDB experience
- Complex joins are expensive
- Not ideal for financial transactions
- Higher operational complexity

**Why not chosen:**
Our data is fundamentally relational (users, orders, payments). PostgreSQL JSONB gives us document storage flexibility while maintaining ACID guarantees and SQL power.

### Alternative 3: DynamoDB (Managed NoSQL)

**Description:**
- AWS DynamoDB for all services
- Fully managed, serverless

**Pros:**
- Fully managed (zero ops)
- Unlimited scalability
- Pay-per-use pricing
- Single-digit millisecond latency

**Cons:**
- **Vendor lock-in** to AWS
- No SQL (complex queries difficult)
- Expensive for large datasets ($250/GB/month)
- Steep learning curve
- No full-text search
- Limited to key-value and simple queries

**Why not chosen:**
DynamoDB lacks SQL querying and creates tight AWS coupling. PostgreSQL RDS gives us managed benefits while maintaining portability and SQL expressiveness.

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/index.html)
- [AWS RDS for PostgreSQL Pricing Calculator](https://calculator.aws/)
- [pgloader Migration Tool](https://github.com/dimitri/pgloader)
- [PostgreSQL vs MySQL Performance Benchmarks (2024)](internal-wiki/benchmarks)
- Meeting Notes: Architecture Review 2024-10-10
- Related ADR: ADR-0001 (Adopt Microservices Architecture)

## Implementation Plan

**Owner**: Backend Architect (with DevOps Lead)

**Timeline**:
- **Week 1-2**: RDS setup, connection pooling, monitoring
- **Week 3-4**: Migration tooling, validation scripts
- **Week 5-12**: Service-by-service migration (Notification → Inventory → Order → User)
- **Week 13-16**: Parallel running, data validation, cutover

**Success Criteria**:
- [ ] All services migrated to PostgreSQL
- [ ] Zero data loss during migration
- [ ] Query performance ≥ MySQL baseline
- [ ] Team trained on PostgreSQL best practices
- [ ] Monitoring and alerting operational

**Risks**:
- Migration timeline may slip (mitigation: parallel team approach)
- Data consistency issues (mitigation: extensive validation scripts)
- Performance regressions (mitigation: load testing before cutover)

---

**Decision Date**: 2024-10-15
**Last Updated**: 2024-10-15
**Next Review**: 2025-04-15 (6 months post-migration)
