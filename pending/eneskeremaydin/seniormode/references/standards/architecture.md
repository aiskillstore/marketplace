# Project architecture

Start from ownership, transaction boundaries, failure tolerance, and operating constraints. Deliver one process when one owner and shared transactions dominate. In a modular monolith, give modules explicit public entry points and name who owns each table or persisted object. Guard the boundary through dependency direction or contract tests.

Consider a separately deployed service or microservice when independent ownership, scaling, security isolation, or rollout makes a measurable difference. A modular monolith changes ownership and code boundaries within one deployment. Extraction adds a network and operations boundary. Account for deadlines, retry safety, cross-service consistency, and release compatibility. Keep shared transactions local when crossing the proposed boundary would make invariants harder to preserve.

Use [modular monolith](../knowledge/architecture/modular-monolith.md) for the deployment decision and [module boundaries](../knowledge/architecture/module-boundaries.md) for the code boundary. Before extracting a service, show the limitation in the current design and test its contract, failure, and rollout behavior.
