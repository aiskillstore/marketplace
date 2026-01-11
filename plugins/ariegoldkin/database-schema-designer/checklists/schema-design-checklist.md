# Database Schema Design Checklist

Use this checklist when designing or reviewing database schemas.

---

## Pre-Design

- [ ] **Requirements Gathered**: Understand data entities and relationships
- [ ] **Access Patterns Identified**: Know how data will be queried
- [ ] **SQL vs NoSQL Decision**: Chosen appropriate database type
- [ ] **Scale Estimate**: Expected data volume and growth rate
- [ ] **Read/Write Ratio**: Understand if read-heavy or write-heavy

---

## Normalization (SQL Databases)

- [ ] **1NF**: Atomic values, no repeating groups
- [ ] **2NF**: No partial dependencies on composite keys
- [ ] **3NF**: No transitive dependencies
- [ ] **Denormalization Justified**: If denormalized, reason documented

---

## Table Design

### Primary Keys

- [ ] **Primary Key Defined**: Every table has primary key
- [ ] **Key Type Chosen**: INT auto-increment or UUID
- [ ] **Meaningful Keys Avoided**: Not using email/username as primary key

### Data Types

- [ ] **Appropriate Types**: Correct data types for each column
- [ ] **String Sizes**: VARCHAR sized appropriately (not always 255)
- [ ] **Numeric Precision**: DECIMAL for money, INT for counts
- [ ] **Dates in UTC**: TIMESTAMP for datetime columns
- [ ] **Boolean Type**: Using BOOLEAN or TINYINT(1)

### Constraints

- [ ] **NOT NULL**: Required columns marked NOT NULL
- [ ] **Unique Constraints**: Unique columns (email, username)
- [ ] **Check Constraints**: Validation rules (price >= 0)
- [ ] **Default Values**: Sensible defaults where appropriate

---

## Relationships

### Foreign Keys

- [ ] **Foreign Keys Defined**: All relationships have FK constraints
- [ ] **ON DELETE Strategy**: CASCADE, RESTRICT, SET NULL chosen appropriately
- [ ] **ON UPDATE Strategy**: Usually CASCADE
- [ ] **Indexes on Foreign Keys**: FKs are indexed

### Relationship Types

- [ ] **One-to-Many**: Modeled correctly
- [ ] **Many-to-Many**: Junction table created
- [ ] **Self-Referencing**: Parent-child relationships handled
- [ ] **Polymorphic**: Strategy chosen (separate FKs or type+id)

---

## Indexing

### Index Strategy

- [ ] **Primary Key Indexed**: Automatic, verify
- [ ] **Foreign Keys Indexed**: All FKs have indexes
- [ ] **WHERE Columns**: Columns in WHERE clauses indexed
- [ ] **ORDER BY Columns**: Sort columns indexed
- [ ] **Composite Indexes**: Multi-column queries optimized
- [ ] **Column Order**: Most selective/queried column first

### Index Types

- [ ] **B-Tree**: Used for ranges and equality (default)
- [ ] **Hash**: Used for exact matches only (if applicable)
- [ ] **Full-Text**: Used for text search (if needed)
- [ ] **Partial Indexes**: Conditional indexes (PostgreSQL)

### Index Limits

- [ ] **Not Over-Indexed**: Only necessary indexes created
- [ ] **Index Maintenance**: Aware of write performance impact

---

## Performance Considerations

### Query Optimization

- [ ] **Joins Optimized**: N+1 queries avoided
- [ ] **SELECT * Avoided**: Only fetch needed columns
- [ ] **Pagination**: LIMIT/OFFSET or cursor-based
- [ ] **Aggregations**: Pre-calculated for expensive queries

### Scalability

- [ ] **Sharding Strategy**: Planned for large datasets
- [ ] **Partitioning**: Tables partitioned by date/range (if applicable)
- [ ] **Read Replicas**: Planned for read-heavy workloads
- [ ] **Caching Layer**: Application-level caching considered

---

## Data Integrity

### Validation

- [ ] **Database-Level Validation**: Constraints enforce rules
- [ ] **Application-Level Validation**: Additional checks in code
- [ ] **Foreign Key Constraints**: Referential integrity enforced
- [ ] **Unique Constraints**: Duplicate prevention

### Consistency

- [ ] **Transactions**: ACID properties for critical operations
- [ ] **Cascading Deletes**: Data cleanup strategy
- [ ] **Soft Deletes**: deleted_at column if needed
- [ ] **Audit Trail**: created_at, updated_at timestamps

---

## Migrations

### Migration Safety

- [ ] **Backward Compatible**: New columns nullable initially
- [ ] **Up and Down Migrations**: Rollback scripts provided
- [ ] **Data Migrations Separate**: Schema vs data changes separated
- [ ] **Tested on Staging**: Migrations tested on production copy
- [ ] **Duration Estimated**: Large migrations timed

### Zero-Downtime

- [ ] **Add Before Remove**: New column added before removing old
- [ ] **Gradual Rollout**: Multi-step migrations for large changes
- [ ] **Feature Flags**: Large changes behind flags

---

## Security

### Access Control

- [ ] **Principle of Least Privilege**: Users have minimum permissions
- [ ] **Separate Accounts**: Read-only vs read-write accounts
- [ ] **No Root Access**: Application doesn't use root/admin account

### Data Protection

- [ ] **Sensitive Data Encrypted**: Passwords hashed, PII encrypted
- [ ] **SQL Injection Prevention**: Parameterized queries only
- [ ] **No Secrets in Code**: Credentials in environment variables

---

## NoSQL Considerations (if applicable)

### Document Design

- [ ] **Embed vs Reference**: Strategy chosen based on access patterns
- [ ] **Document Size**: Within limits (16MB for MongoDB)
- [ ] **Schema Validation**: Validation rules defined (if supported)
- [ ] **Indexes**: Appropriate indexes on query fields

### Scaling

- [ ] **Sharding Key**: Chosen for even distribution
- [ ] **Replication**: Read replicas configured
- [ ] **Consistency Level**: Chosen appropriately (eventual vs strong)

---

## Documentation

- [ ] **ERD Created**: Entity-relationship diagram
- [ ] **Schema Documented**: Column descriptions and purpose
- [ ] **Indexes Documented**: Why each index exists
- [ ] **Relationships Explained**: Business logic behind relationships
- [ ] **Migration History**: Changelog of schema changes

---

## Testing

- [ ] **Sample Data**: Test data created
- [ ] **Query Performance**: Slow queries identified (EXPLAIN)
- [ ] **Load Testing**: Performance under expected load
- [ ] **Edge Cases**: NULL, empty, max values tested

---

## Common Pitfalls to Avoid

- ❌ Using VARCHAR(255) for everything
- ❌ No foreign key constraints
- ❌ Missing indexes on foreign keys
- ❌ Over-indexing (index on every column)
- ❌ FLOAT for money values
- ❌ Storing dates as strings
- ❌ No created_at/updated_at timestamps
- ❌ No soft delete strategy
- ❌ Non-reversible migrations
- ❌ Breaking changes without migration plan

---

## Pre-Deployment Checklist

- [ ] **Migrations Reviewed**: Peer-reviewed by team
- [ ] **Rollback Plan**: Tested rollback procedures
- [ ] **Monitoring Setup**: Slow query logging enabled
- [ ] **Backups**: Backup before major schema changes
- [ ] **Alerts Configured**: Alerts for query performance degradation

---

**Checklist Version**: 1.0.0
**Skill**: database-schema-designer v1.0.0
**Last Updated**: 2025-10-31
