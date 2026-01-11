---
name: codebase-analysis
description: Techniques for analyzing existing codebases to reverse-engineer requirements and understand business logic. Use when conducting brownfield analysis or understanding existing system capabilities.
allowed-tools: Read, Grep, Glob, LSP
---

# Codebase Analysis Skill

## Overview

This skill provides techniques for extracting business requirements, domain knowledge, and technical specifications from existing codebases.

## Analysis Objectives

When analyzing a codebase, seek to understand:
1. **Domain Model**: Core entities and their relationships
2. **Business Rules**: Validation, calculations, workflows
3. **Integrations**: External systems and data flows
4. **User Capabilities**: What users can do in the system
5. **Technical Constraints**: Architecture patterns and limitations

## Analysis Process

### Phase 1: Structure Discovery
1. Map project structure and organization
2. Identify main components and layers
3. Locate configuration and entry points
4. Understand build and deployment setup

### Phase 2: Domain Model Extraction
1. Find entity/model definitions
2. Map relationships between entities
3. Identify domain vocabulary (ubiquitous language)
4. Document data types and constraints

### Phase 3: Business Logic Identification
1. Locate service/business logic layers
2. Extract validation rules
3. Document calculations and formulas
4. Map state machines and workflows

### Phase 4: Integration Mapping
1. Find API endpoints and contracts
2. Identify external service calls
3. Map data flows in/out of system
4. Document authentication patterns

### Phase 5: Capability Documentation
1. List user-facing features
2. Map permissions and access control
3. Document user workflows
4. Identify edge cases and error handling

## Code Pattern Recognition

### Entity/Model Identification

Look for these patterns:
```
// C# Entity
public class Order { ... }

// Java Entity
@Entity
public class Order { ... }

// TypeScript Interface
interface Order { ... }

// Database Schema
CREATE TABLE orders ( ... )
```

### Business Rule Indicators

Watch for these keywords and patterns:
- Validation: `Validate`, `Check`, `Ensure`, `Must`, `Should`
- Calculations: `Calculate`, `Compute`, `Total`, `Sum`
- Conditions: `If`, `When`, `Unless`, `Only`
- Constraints: `Max`, `Min`, `Required`, `Limit`

### Service Layer Patterns

Identify business logic in:
```
// Service classes
public class OrderService { ... }

// Use cases / Application services
public class CreateOrderUseCase { ... }

// Command/Query handlers
public class CreateOrderHandler { ... }
```

### API Endpoint Patterns

Look for:
```
// REST Controllers
[Route("api/orders")]
[HttpPost]
public async Task<Order> Create(...)

// Express routes
app.post('/api/orders', ...)

// GraphQL resolvers
Mutation: { createOrder: ... }
```

## Analysis Heuristics

### Finding Domain Models
1. Search for `class`, `interface`, `type` definitions
2. Look in folders named: `Models`, `Entities`, `Domain`
3. Check database migrations and schema files
4. Review ORM configurations

### Finding Business Rules
1. Search for validation attributes/decorators
2. Look for `throw` statements (business exceptions)
3. Find conditional logic in services
4. Check for rule engines or policy patterns

### Finding Integrations
1. Search for HTTP client usage
2. Look for message queue producers/consumers
3. Find database connection configurations
4. Check for external SDK imports

### Finding User Capabilities
1. Review API endpoints and their permissions
2. Check UI components and forms
3. Look at authorization/role definitions
4. Review menu structures and navigation

## Output Artifacts

### Domain Model Documentation
```markdown
## Entity: Order

### Attributes
| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| id | UUID | Unique identifier | Required |
| status | Enum | Order status | Required |
| total | Decimal | Order total | >= 0 |

### Relationships
- Order has many OrderItems (1:N)
- Order belongs to Customer (N:1)

### Business Rules
- Order total must equal sum of item totals
- Status can only transition: Draft -> Submitted -> Approved -> Completed
```

### Business Rule Documentation
```markdown
## Rule: Order Validation

### Description
Orders must meet these criteria before submission

### Conditions
1. Order must have at least one item
2. All items must have valid product references
3. Customer must have valid payment method
4. Total must be greater than $0

### Implementation
- File: src/Services/OrderService.cs
- Method: ValidateForSubmission()
- Line: 145-180
```

### Integration Documentation
```markdown
## Integration: Payment Gateway

### Type
REST API (Synchronous)

### Endpoint
POST https://api.payments.com/v1/charges

### Data Flow
- Input: Order total, Customer payment token
- Output: Transaction ID, Status

### Error Handling
- Timeout: Retry 3 times with exponential backoff
- Failure: Mark order as payment pending, notify support

### Implementation
- File: src/Integrations/PaymentGateway.cs
```

## Code Search Patterns

### Finding Entities (by language)
```bash
# C# / .NET
grep -r "public class.*Entity" --include="*.cs"
grep -r "\[Table\(" --include="*.cs"

# Java
grep -r "@Entity" --include="*.java"

# TypeScript
grep -r "interface.*{" --include="*.ts"
```

### Finding Validation Rules
```bash
# C# Attributes
grep -r "\[Required\]|\[Range\]|\[StringLength\]" --include="*.cs"

# Java Annotations
grep -r "@NotNull|@Size|@Valid" --include="*.java"

# Custom validation
grep -r "Validate|throw.*Exception" --include="*.cs"
```

### Finding API Endpoints
```bash
# .NET Controllers
grep -r "\[Http.*\]|\[Route\(" --include="*.cs"

# Express.js
grep -r "app\.(get|post|put|delete)\(" --include="*.js"
```

## Reverse Engineering Tips

### Start With Entry Points
1. Find main() or startup configuration
2. Follow dependency injection setup
3. Trace from API controllers to services to data

### Follow the Data
1. Start with database schema or entities
2. Trace how data flows through system
3. Map CRUD operations for each entity

### Look for Tests
1. Unit tests reveal expected behavior
2. Integration tests show workflows
3. Test data shows valid/invalid scenarios

### Check Documentation
1. Look for README files
2. Check API documentation (Swagger/OpenAPI)
3. Review code comments and XML docs

## Questions to Answer

After analysis, you should be able to answer:

1. **What entities exist and how do they relate?**
2. **What can users do in this system?**
3. **What business rules govern behavior?**
4. **What external systems does this integrate with?**
5. **What are the key workflows?**
6. **What constraints exist (technical and business)?**
7. **What data does the system manage?**
8. **Who has access to what?**

See [patterns.md](patterns.md) for common architectural patterns to identify.
