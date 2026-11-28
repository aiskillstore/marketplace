# Engineering standards

Start with the invariant, the owner of each piece of state, and an observable check. Respect the project's language and conventions. Read only the guides whose choices change the outcome.

| When the work changes… | Read |
|---|---|
| The first product slice, stack, or delivery plan | [Greenfield planning](standards/greenfield.md) |
| Deployment, domain ownership, or independent scaling | [Architecture](standards/architecture.md) |
| Folder layout, file naming, or package boundaries | [Project structure](standards/structure.md) |
| Placement, reuse, interfaces, or separation of responsibilities | [Modularity and reuse](standards/modularity.md) |
| Dependencies, duplication, abstraction, or maintenance cost | [Code principles](standards/code-principles.md), [Dependencies](standards/dependencies.md) |
| Endpoints, request validation, errors, or compatibility | [API contracts](standards/api.md) |
| Schema, indexing, transactions, or migrations | [Data and storage](standards/data.md) |
| Identity, authorization, sensitive data, or secrets | [Security](standards/security.md) |
| Startup settings and environment differences | [Configuration](standards/configuration.md) |
| Recovery, retries, timeouts, logs, or tracing | [Reliability](standards/reliability.md), [Observability](standards/observability.md) |
| Latency, throughput, memory, or resource limits | [Performance](standards/performance.md) |
| Verification scope, integration, or regression coverage | [Testing](standards/testing.md) |
| Operational knowledge, contracts, or reversible code moves | [Documentation](standards/documentation.md), [Safe refactoring](standards/refactoring.md) |

Use an existing pattern when its conditions match. Keep one authoritative source of state where feasible and give projections explicit freshness and recovery rules. Add a distributed boundary only when independent ownership, capacity, deployment, or failure isolation justifies its operational cost. Treat missing coverage as uncertainty.
