---
name: api-design-principles
description: Principles and checklists for designing and reviewing REST and GraphQL APIs; use when defining or evaluating API contracts (endpoints/schemas), naming, error models, pagination, versioning, and REST vs. GraphQL trade-offs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# API Design Principles

## When to Use

- Designing a new REST API contract for CRUD-style resources and you need consistent resource modeling, naming, and HTTP semantics.
- Designing a new GraphQL schema for multiple clients with different data shapes and you need clear type/field ownership and safe evolution.
- Reviewing an existing API (REST or GraphQL) to identify inconsistencies in naming, error handling, pagination/filtering, or versioning/deprecation.
- Deciding between REST vs. GraphQL (or defining boundaries when mixing both) and documenting trade-offs and constraints.
- Standardizing cross-cutting concerns (authn/authz, rate limiting, observability, long-running operations, idempotency) across multiple services.

## Key Features

- End-to-end workflow for API design/review: requirements → style choice → domain modeling → operations → cross-cutting concerns → deliverables.
- REST guidance: resource-oriented modeling, stable identifiers, relationship patterns, and correct HTTP verb usage.
- GraphQL guidance: schema/type modeling, Query vs. Mutation separation, input types for writes, and explicit side-effect handling.
- Cross-cutting design patterns: consistent error model, pagination/filtering/sorting, versioning and deprecation strategy, and operational concerns.
- Review checklist to validate completeness, highlight risks/gaps, and produce actionable follow-ups.

## Dependencies

- None (documentation-only skill).
- Reference documents:
  - `references/rest.md`
  - `references/graphql.md`
  - `references/review-checklist.md`

## Example Usage

### Goal

Design (or review) an API for managing `Projects` and `Tasks`, and produce a contract with examples, error model, pagination, and a checklist summary.

### Step 1: Clarify requirements and constraints

- Consumers: Web app + mobile app + internal admin.
- Constraints: p95 latency < 200ms for list endpoints; PII present; audit logging required.
- Core use cases: list projects, view project, create task, update task status, search tasks by status/assignee.

### Step 2: Choose API style and boundaries

- Choose **REST** for resource-oriented CRUD with cacheable reads and straightforward endpoints.
- If GraphQL is later introduced for client-specific views, define boundaries (e.g., GraphQL for read aggregation; REST remains source-of-truth for writes).

### Step 3: Produce a REST contract skeleton (runnable examples)

**Base URL**
- `https://api.example.com/v1`

**Resources**
- `projects`
- `tasks` (scoped under a project)

**Endpoints**
- `GET /v1/projects`
- `POST /v1/projects`
- `GET /v1/projects/{projectId}`
- `GET /v1/projects/{projectId}/tasks`
- `POST /v1/projects/{projectId}/tasks`
- `PATCH /v1/projects/{projectId}/tasks/{taskId}`

#### List projects (pagination + filtering)

**Request**
```bash
curl -sS -X GET "https://api.example.com/v1/projects?limit=20&cursor=eyJpZCI6IjEwMCJ9&sort=createdAt:desc" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json"
```

**Response (200)**
```json
{
  "data": [
    {
      "id": "proj_123",
      "name": "Roadmap 2026",
      "createdAt": "2026-01-10T12:00:00Z"
    }
  ],
  "page": {
    "limit": 20,
    "nextCursor": "eyJpZCI6InByb2pfMTIzIn0="
  }
}
```

#### Create a task (idempotency)

**Request**
```bash
curl -sS -X POST "https://api.example.com/v1/projects/proj_123/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: 2b7b1a2e-7f2b-4c2a-9c2b-0b3b7c9d1a11" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Draft API spec",
    "assigneeId": "user_42",
    "dueAt": "2026-03-01T00:00:00Z"
  }'
```

**Response (201)**
```json
{
  "data": {
    "id": "task_999",
    "projectId": "proj_123",
    "title": "Draft API spec",
    "status": "OPEN",
    "assigneeId": "user_42",
    "dueAt": "2026-03-01T00:00:00Z",
    "createdAt": "2026-02-25T09:00:00Z"
  }
}
```

#### Error model example

**Response (409)**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "A task with the same title already exists in this project.",
    "details": {
      "field": "title",
      "reason": "DUPLICATE"
    },
    "requestId": "req_01HTZQ8K7Y9M2A3B4C5D6E7F8G"
  }
}
```

### Step 4: Run the review checklist

Use `references/review-checklist.md` to validate:
- Naming consistency (resources, fields, enums)
- HTTP semantics and status codes
- Pagination/filtering/sorting rules
- Error model completeness and stability
- Versioning/deprecation plan
- Security and observability requirements

### Expected deliverable format (save to `outputs/`)

- API style choice + trade-offs
- Contract skeleton (endpoints or schema)
- Request/response (or query/mutation) examples
- Error model + pagination strategy
- Checklist results + risks/gaps

## Implementation Details

### Recommended workflow (design/review)

1. **Clarify requirements and constraints**
   - Identify domain, core use cases, and consumer types (web/mobile/partners/internal).
   - Capture constraints: latency, throughput, consistency, compliance, data sensitivity.

2. **Choose API style and boundaries**
   - **REST**: best for resource-oriented APIs, cacheable reads, and simple CRUD.
   - **GraphQL**: best for multiple clients with varying data shapes and frequent iteration.
   - If mixing, define boundaries to avoid overlapping responsibilities.

3. **Domain modeling**
   - REST: model stable resources (nouns), stable identifiers, and relationships.
   - GraphQL: define types and field ownership; use input types for writes.

4. **Operation and behavior design**
   - REST: map operations to HTTP verbs; represent actions via sub-resources or noun-based endpoints when needed.
   - GraphQL: separate `Query` vs. `Mutation`; document side effects explicitly.
   - Define **idempotency** (especially for creates) and patterns for **long-running tasks** when applicable.

5. **Cross-cutting concerns**
   - Authentication/authorization
   - Error model (stable codes, actionable messages, request correlation IDs)
   - Pagination, filtering, sorting (document defaults and limits)
   - Versioning and deprecation strategy
   - Observability (logging/metrics/tracing), rate limiting

### Reference guides

- REST Principles and Patterns: `references/rest.md`
- GraphQL Principles and Patterns: `references/graphql.md`
- Review Checklist: `references/review-checklist.md`