# Integrations

Cross-repository and external service dependencies for [Project Name]

## Repository Ecosystem

This repository exists within a broader ecosystem of services and libraries:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   [Upstream]    │────▶│  [This Repo]    │────▶│  [Downstream]   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         └─────────────▶│  [Sibling]      │◀─────────────┘
                        └─────────────────┘
```

## Upstream Dependencies

Repositories and services this project depends on:

| Repository | Version | Purpose | Integration Point |
|------------|---------|---------|-------------------|
| [repo/name] | [constraint] | [What it provides] | [Code location] |
| [repo/name] | [constraint] | [What it provides] | [Code location] |

## Downstream Consumers

Repositories and services that depend on this project:

| Repository | Consumes | Contact Owner |
|------------|----------|---------------|
| [repo/name] | [What they use] | [@team] |
| [repo/name] | [What they use] | [@team] |

## Sibling Repositories

Related repositories in the same organization:

| Repository | Relationship | Shared Context |
|------------|--------------|----------------|
| [repo/name] | [Shared lib/shared parent] | [What's shared] |
| [repo/name] | [Alternative/Complement] | [When to use which] |

## External Services

Third-party services and APIs:

| Service | Purpose | SLA/Fallback |
|---------|---------|--------------|
| [Service] | [What for] | [Backup plan] |
| [Service] | [What for] | [Backup plan] |

## Communication Protocols

| Protocol | Used With | Purpose |
|----------|-----------|---------|
| REST API | [Services] | [Operations] |
| gRPC | [Services] | [Operations] |
| Events (Kafka) | [Services] | [Event types] |
| Shared DB | [Services] | [Tables] |

## Dependency Updates

| Dependency | Update Cadence | Breaking Change Process |
|------------|----------------|-------------------------|
| [Repo] | [Weekly/Monthly] | [Process] |
| [Service] | [As needed] | [Process] |

## Onboarding New Integrations

When adding a new repository dependency:

1. Document in the appropriate section above
2. Add to [INTEGRATIONS.md](INTEGRATIONS.md) of the dependent repo
3. Update architecture diagrams
4. Notify teams of downstream consumers
