# Phase 4: Scaffolding

**Goal:** Generate a TypeScript project structure implementing the architectural decisions.

## Prerequisites

- Phase 1 Discovery completed
- Phase 2 Domain Model defined
- Phase 3 Boundaries defined
- ADR drafted (or in progress)

## Pre-Scaffold Checklist

Before generating any code, confirm:

```
[ ] Problem statement is clear
[ ] Domain model is approved
[ ] All ports are identified
[ ] Adapter technologies are chosen
[ ] Layer structure is decided
[ ] Naming conventions agreed
```

## Scaffold Structure

Generate this folder structure:

```
src/
├── domain/                    # Pure business logic, no dependencies
│   ├── entities/              # Domain entities and aggregate roots
│   │   └── [Entity].ts
│   ├── value-objects/         # Immutable value types
│   │   └── [ValueObject].ts
│   ├── events/                # Domain events
│   │   └── [Event].ts
│   └── errors/                # Domain-specific errors
│       └── [Error].ts
│
├── application/               # Use cases, orchestration
│   ├── ports/                 # Interface definitions
│   │   ├── inbound/           # Primary/driving ports
│   │   │   └── [UseCase].ts
│   │   └── outbound/          # Secondary/driven ports
│   │       └── [Repository].ts
│   ├── use-cases/             # Use case implementations
│   │   └── [UseCase].ts
│   └── services/              # Application services
│       └── [Service].ts
│
├── infrastructure/            # External world implementations
│   ├── persistence/           # Database adapters
│   │   └── [Repository]Impl.ts
│   ├── external/              # External API adapters
│   │   └── [Gateway]Impl.ts
│   └── config/                # Configuration
│       └── index.ts
│
├── interfaces/                # Entry points (driving adapters)
│   ├── http/                  # REST/HTTP controllers
│   │   ├── routes/
│   │   └── controllers/
│   ├── cli/                   # CLI commands (if applicable)
│   └── events/                # Event handlers (if applicable)
│
└── shared/                    # Shared utilities
    ├── types/                 # Shared type definitions
    └── utils/                 # Pure utility functions
```

## File Generation Order

Generate files in this order to maintain valid TypeScript:

1. **Value Objects** - No dependencies
2. **Entities** - Depend on value objects
3. **Domain Events** - Depend on entities
4. **Outbound Ports** - Interface definitions
5. **Inbound Ports** - Use case interfaces
6. **Use Cases** - Implement inbound, use outbound
7. **Adapters** - Implement outbound ports
8. **Controllers** - Use inbound ports

## Template References

Use these templates when generating:

| Component | Template |
|-----------|----------|
| Entity | `read ../templates/entity-template.md` |
| Value Object | `read ../templates/value-object-template.md` |
| Port Interface | `read ../templates/port-adapter-interface.md` |
| Use Case | `read ../templates/use-case-template.md` |
| Repository | `read ../templates/repository-template.md` |
| Controller | `read ../templates/controller-template.md` |

## Scaffold Questions

Before generating each component, ask:

| Component | Ask |
|-----------|-----|
| Entity | "What's the identity? What mutations are allowed?" |
| Value Object | "What makes two instances equal?" |
| Repository | "What queries are needed beyond CRUD?" |
| Use Case | "What are the error cases?" |
| Controller | "What's the HTTP method and path?" |

## Generated File Checklist

For each generated file, ensure:

- [ ] Single responsibility
- [ ] Dependencies only point inward
- [ ] Interfaces over implementations
- [ ] Error handling defined
- [ ] TypeScript strict mode compatible

## Post-Scaffold Tasks

After generating the scaffold:

1. **Dependency verification**
   ```
   domain/ → (no imports from other layers)
   application/ → domain/
   infrastructure/ → application/, domain/
   interfaces/ → application/, domain/
   ```

2. **Create index files** for clean imports

3. **Add placeholder tests** for each use case

4. **Generate ADR** documenting the architecture

## ADR Generation

Finalize the Architecture Decision Record:

```markdown
# ADR-001: [System Name] Architecture

## Status
Accepted

## Context
[Problem from Phase 1]

## Decision
[Architectural decisions from Phases 2-3]

## Consequences
### Positive
- [Benefits]

### Negative
- [Tradeoffs]

### Risks
- [What could go wrong]
```

Template: `read ../templates/adr-template.md`

## Completion Checklist

Before declaring the scaffold complete:

```
[ ] All folders created
[ ] All port interfaces defined
[ ] All entity skeletons created
[ ] All use case stubs created
[ ] Dependency rule verified
[ ] ADR generated
[ ] User has reviewed and approved
```

## Next Steps for User

After scaffolding, suggest:

1. "Start implementing the core use case first"
2. "Write tests for domain logic before infrastructure"
3. "Implement one full vertical slice end-to-end"
4. "Then expand to remaining features"
