# Technical Implementation Spec Template

## Structure

```markdown
# Technical Implementation Spec: [Project Name]

> **Status**: Draft | Approved | Implemented
> **Version**: 1.0 | **Updated**: [Date]

## TL;DR
[2-3 sentences: Tech stack, architecture pattern, key constraints]

## 1. Technology Stack

### Core
- **Language**: Python [version]
- **Package Manager**: UV
- **Framework**: [if applicable]

### Code Quality
- **Linter**: Ruff
- **Type Checker**: BasedPyright
- **Formatter**: Black (88 chars)
- **Testing**: pytest

### Data Layer
- **Database**: [Choice] - See [ADR-001](./adr/adr-001-database-choice.md)
- **Cache**: [if applicable]
- **ORM**: [if applicable]

### Infrastructure
- **CI/CD**: GitHub Actions
- **Container**: [Docker if applicable]

## 2. Architecture

### Pattern
[Monolith | Microservices | Serverless | etc] - See [ADR-XXX]

### Component Diagram
```
┌─────────────────────────────────────────┐
│              [Component]                │
├─────────────┬─────────────┬─────────────┤
│  [Module]   │  [Module]   │  [Module]   │
└─────────────┴─────────────┴─────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────┐
│            [Data Layer]                 │
└─────────────────────────────────────────┘
```

### Component Responsibilities
| Component | Purpose | Key Functions |
|-----------|---------|---------------|
| [Name] | [What it does] | [Functions] |
| [Name] | [What it does] | [Functions] |

## 3. Data Model

### Core Entities
```python
# [Entity Name]
class [Entity]:
    id: UUID
    [field]: [type]
    [field]: [type]
    created_at: datetime
    updated_at: datetime
```

### Relationships
- [Entity A] → [Entity B]: [Relationship type]

## 4. API Specification (if applicable)

### Endpoints
| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | /api/v1/[resource] | [Purpose] | [Yes/No] |
| POST | /api/v1/[resource] | [Purpose] | [Yes/No] |

### Request/Response Format
```json
{
  "[field]": "[type]",
  "[field]": "[type]"
}
```

## 5. CLI Specification (if applicable)

### Commands
| Command | Purpose | Example |
|---------|---------|---------|
| `[cmd] [subcmd]` | [Purpose] | `[example]` |

### Arguments
- `--[arg]`: [Description] (default: [value])

## 6. Security

### Authentication
[Method]: [Details] - See [ADR-XXX]

### Authorization
[RBAC/ABAC/etc]: [Details]

### Data Protection
- **At Rest**: [Encryption method]
- **In Transit**: [TLS/etc]
- **Sensitive Data**: [Handling approach]

## 7. Error Handling

### Strategy
[Approach to errors - fail fast, graceful degradation, etc]

### Error Codes
| Code | Meaning | User Action |
|------|---------|-------------|
| [Code] | [Description] | [What user should do] |

### Logging
- **Format**: Structured JSON
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Sensitive**: [What NOT to log]

## 8. Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| [Response time] | [Target] | [How measured] |
| [Throughput] | [Target] | [How measured] |
| [Memory] | [Target] | [How measured] |

## 9. Testing Strategy

### Coverage Target
- Minimum: [X]%
- Critical paths: 100%

### Test Types
- **Unit**: [Focus areas]
- **Integration**: [Key scenarios]
- **E2E**: [User workflows]

## Related Documents
- [Project Vision](./project-vision.md)
- [Architecture Decisions](./adr/)
- [Development Roadmap](./roadmap.md)
```

## Generation Notes

- Reference ADRs for all architectural decisions
- Include actual code examples (schemas, configs)
- Specify exact versions of dependencies
- Performance requirements need numbers
- Keep under 1500 words
