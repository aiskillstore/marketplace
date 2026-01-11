---
name: architecture-decision-record
description: Use this skill when documenting significant architectural decisions. Provides ADR templates following the Nygard format with sections for context, decision, consequences, and alternatives. Helps teams maintain architectural memory and rationale for backend systems, API designs, database choices, and infrastructure decisions.
version: 1.0.0
author: AI Agent Hub
tags: [architecture, documentation, decision-making, backend]
---

# Architecture Decision Record

## Overview

Architecture Decision Records (ADRs) are lightweight documents that capture important architectural decisions along with their context and consequences. This skill provides templates, examples, and best practices for creating and maintaining ADRs in your projects.

**When to use this skill:**
- Making significant technology choices (databases, frameworks, cloud providers)
- Designing system architecture or major components
- Establishing patterns or conventions for the team
- Evaluating trade-offs between multiple approaches
- Documenting decisions that will impact future development

## Why ADRs Matter

ADRs serve as architectural memory for your team:
- **Context Preservation**: Capture why decisions were made, not just what was decided
- **Onboarding**: Help new team members understand architectural rationale
- **Prevent Revisiting**: Avoid endless debates about settled decisions
- **Track Evolution**: See how architecture evolved over time
- **Accountability**: Clear ownership and decision timeline

## ADR Format (Nygard Template)

Each ADR should follow this structure:

### 1. Title
Format: `ADR-####: [Decision Title]`
Example: `ADR-0001: Adopt Microservices Architecture`

### 2. Status
Current state of the decision:
- **Proposed**: Under consideration
- **Accepted**: Decision approved and being implemented
- **Superseded**: Replaced by a later decision (reference ADR number)
- **Deprecated**: No longer recommended but not yet replaced
- **Rejected**: Considered but not adopted (document why)

### 3. Context
**What to include:**
- Problem statement or opportunity
- Business/technical constraints
- Stakeholder requirements
- Current state of the system
- Forces at play (conflicting concerns)

**Example:**
```markdown
## Context

Our monolithic application is experiencing scalability issues:
- Database connection pool exhausted during peak traffic
- Deployment of any feature requires full application restart
- Teams blocked waiting for shared resources
- 45-minute build times impacting developer productivity

Business requirements:
- Support 10x traffic growth over next 12 months
- Enable independent team deployments
- Improve time-to-market for new features

Technical constraints:
- Team familiar with Node.js and Python
- AWS infrastructure already in place
- Budget for 2 senior devops engineers
```

### 4. Decision
**What to include:**
- The choice being made
- Key principles or patterns to follow
- What will change as a result
- Who is responsible for implementation

**Be specific and actionable:**
- ✅ "We will adopt microservices architecture using Node.js with Express"
- ❌ "We will consider using microservices"

**Example:**
```markdown
## Decision

We will migrate from our monolithic architecture to microservices using:

**Technology Stack:**
- Node.js 20+ with Express for service implementation
- PostgreSQL for transactional data (per service)
- Redis for caching and session management
- RabbitMQ for async communication between services
- Docker + Kubernetes for deployment orchestration

**Service Boundaries:**
- User Service: Authentication, profiles, preferences
- Order Service: Order processing, payment integration
- Inventory Service: Product catalog, stock management
- Notification Service: Email, SMS, push notifications

**Migration Strategy:**
- Strangler Fig pattern: Gradually extract services from monolith
- Start with Notification Service (lowest risk, clear boundaries)
- Complete migration within 6 months (Q1-Q2 2026)

**Responsibility:**
- Backend Architect: Service design and API contracts
- DevOps Team: Kubernetes setup and deployment pipelines
- Team Leads: Migration execution per service
```

### 5. Consequences
**What to include:**
- Positive outcomes (benefits)
- Negative outcomes (costs, risks, trade-offs)
- Neutral outcomes (things that change but aren't clearly better/worse)

**Be honest about trade-offs:**
```markdown
## Consequences

### Positive
- **Scalability**: Each service can scale independently based on load
- **Development Velocity**: Teams can deploy services without coordination
- **Technology Freedom**: Services can use different tech stacks if needed
- **Fault Isolation**: Failure in one service doesn't crash entire system
- **Faster Build Times**: Services build in 2-5 minutes vs 45 minutes

### Negative
- **Operational Complexity**: Managing 4+ services vs 1 application
- **Network Latency**: Inter-service calls add 10-50ms per hop
- **Distributed Debugging**: Harder to trace requests across services
- **Data Consistency**: Eventually consistent vs immediate consistency
- **Learning Curve**: Team needs to learn Kubernetes, service mesh concepts
- **Initial Slowdown**: 2-3 months of infrastructure setup before benefits

### Neutral
- **Testing Strategy**: Shift from integration tests to contract tests
- **Monitoring**: Need distributed tracing (Jaeger) vs simple logs
- **Cost**: Higher infrastructure costs offset by improved developer productivity
```

### 6. Alternatives Considered
**Document at least 2 alternatives:**

**For each alternative, explain:**
- What it was
- Why it was considered
- Why it was not chosen

**Example:**
```markdown
## Alternatives Considered

### Alternative 1: Optimize Existing Monolith
**Description:**
- Add read replicas for database
- Implement caching layer (Redis)
- Use horizontal scaling with load balancer

**Pros:**
- Lower complexity, team already familiar
- Faster implementation (4-6 weeks)
- No architectural re-work needed

**Cons:**
- Doesn't solve deployment coupling
- Limited scalability ceiling
- Build times remain slow
- Teams still blocked on shared resources

**Why not chosen:**
This addresses symptoms but not root causes. We'd face the same issues again in 12-18 months as we continue growing.

### Alternative 2: Serverless Architecture (AWS Lambda)
**Description:**
- Break application into Lambda functions
- Use API Gateway for routing
- DynamoDB for storage

**Pros:**
- Extreme scalability
- Pay-per-use pricing model
- No server management

**Cons:**
- Vendor lock-in to AWS
- Cold start latency (500ms+)
- Limited to 15-minute execution time
- Team has no serverless experience
- Harder to debug and test locally

**Why not chosen:**
Risk too high given team inexperience. Cold starts unacceptable for our real-time features. Microservices provide similar benefits with more control.
```

### 7. References (Optional)
Links to relevant resources:
- Meeting notes or discussion threads
- Related ADRs
- External research or articles
- Proof of concept implementations

## ADR Lifecycle

```
Proposed → Accepted → [Implemented] → (Eventually) Superseded/Deprecated
          ↓
      Rejected
```

**State Transitions:**
1. **Proposed**: Draft created, under review
2. **Accepted**: Team agrees, implementation can begin
3. **Implemented**: Decision is live in production
4. **Superseded**: Replaced by new ADR (add reference)
5. **Deprecated**: No longer recommended (migration path documented)
6. **Rejected**: Not adopted (reasoning captured)

## Best Practices

### 1. **Keep ADRs Immutable**
Once accepted, don't edit ADRs. Create new ADRs that supersede old ones.
- ✅ Create ADR-0015 that supersedes ADR-0003
- ❌ Update ADR-0003 with new decisions

### 2. **Write in Present Tense**
ADRs are historical records written as if the decision is being made now.
- ✅ "We will adopt microservices"
- ❌ "We adopted microservices"

### 3. **Focus on 'Why', Not 'How'**
ADRs capture decisions, not implementation details.
- ✅ "We chose PostgreSQL for relational consistency"
- ❌ "Configure PostgreSQL with these specific settings..."

### 4. **Review ADRs as Team**
Get input from relevant stakeholders before accepting.
- Architects: Technical viability
- Developers: Implementation feasibility
- Product: Business alignment
- DevOps: Operational concerns

### 5. **Number Sequentially**
Use 4-digit zero-padded numbers: ADR-0001, ADR-0002, etc.
Maintain a single sequence even with multiple projects.

### 6. **Store in Git**
Keep ADRs in version control alongside code:
- **Location**: `/docs/adr/` or `/architecture/decisions/`
- **Format**: Markdown for easy reading
- **Branch**: Same branch as implementation

## Quick Start Checklist

- [ ] Copy ADR template from `/templates/adr-template.md`
- [ ] Assign next sequential number (check existing ADRs)
- [ ] Fill in Context: problem, constraints, requirements
- [ ] Document Decision: what, why, how, who
- [ ] List Consequences: positive, negative, neutral
- [ ] Describe at least 2 Alternatives: what, pros/cons, why not chosen
- [ ] Add References: discussions, research, related ADRs
- [ ] Set Status to "Proposed"
- [ ] Review with team
- [ ] Update Status to "Accepted" after approval
- [ ] Link ADR in implementation PR
- [ ] Update Status to "Implemented" after deployment

## Common Pitfalls to Avoid

❌ **Too Technical**: "We'll use Kubernetes with these 50 YAML configs..."
✅ **Right Level**: "We'll use Kubernetes for container orchestration because..."

❌ **Too Vague**: "We'll use a better database"
✅ **Specific**: "We'll use PostgreSQL 15+ for transactional data because..."

❌ **No Alternatives**: Only documenting the chosen solution
✅ **Comparative**: Document why alternatives weren't chosen

❌ **Missing Consequences**: Only listing benefits
✅ **Balanced**: Honest about costs and trade-offs

❌ **No Context**: "We decided to use Redis"
✅ **Contextual**: "Given our 1M+ concurrent users and sub-50ms latency requirement..."

## Examples

See `/examples/` for complete ADR samples:
- `adr-0001-adopt-microservices.md` - System architecture decision
- `adr-0002-choose-postgresql.md` - Database selection
- `adr-0003-api-versioning-strategy.md` - API design pattern

## Related Skills

- **api-design-framework**: Use when designing APIs referenced in ADRs
- **database-schema-designer**: Use when ADR involves database choices
- **security-checklist**: Consult when ADR has security implications

## Integration with Agents

### Backend System Architect
- Creates ADRs when designing major system components
- References ADRs when making related architectural decisions
- Reviews ADRs for consistency with overall architecture

### Studio Coach
- Suggests ADRs for complex multi-agent projects
- Ensures architectural decisions are documented
- Tracks ADR status in project planning

### Code Quality Reviewer
- Validates that significant changes have corresponding ADRs
- Ensures implementation aligns with accepted ADRs
- Flags when ADR may need to be superseded

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Maintained by**: AI Agent Hub Team
