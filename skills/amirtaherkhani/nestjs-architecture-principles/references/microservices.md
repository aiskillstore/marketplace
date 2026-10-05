# Microservices Rules

Treat a microservice as an independently owned and operated boundary, not as a NestJS transport choice or a folder extraction.

## Pass the extraction gate

Start with a modular monolith unless at least one concrete pressure requires independent operation. Evaluate all five axes:

1. **Deployment:** must the capability release independently?
2. **Ownership:** is there a durable team boundary with authority over the service?
3. **Scaling:** does it have a distinct resource or workload profile?
4. **Data:** can it own its writes and consistency boundary?
5. **Failure:** is isolating its failures worth network and operational cost?

A CPU-heavy task may need a separate worker process without becoming a business microservice. A circular module dependency is an ownership problem, not evidence for a network boundary.

## Define the contract before the transport

- Use request/response for an immediate result with an explicit timeout and failure contract.
- Use a command when one owner is expected to act.
- Use an event for a completed fact that zero or more consumers may react to.
- Version schemas compatibly and support mixed deployments during rollout.
- Define authentication, authorization, tenant context, correlation, size limits, and sensitive-data handling.
- Specify delivery, ordering, duplication, cancellation, and error semantics. Do not assume the broker or Nest transporter supplies application-level guarantees.

HTTP exceptions are not portable service contracts. Map typed application failures to transport-specific responses at each adapter.

## Own data deliberately

Each service owns its write model. Avoid shared-table writes and cross-service joins that make independent deployment fictional.

For workflows crossing owners:

- prefer local atomic updates plus a transactional outbox when a durable event must follow a commit;
- design idempotent consumers before enabling retry;
- use a saga or compensating action only when the business can define partial-completion behavior;
- expose purpose-built APIs, replicated read models, or events instead of direct database access;
- document temporary dual-read or dual-write migration states and their exit criteria.

Distributed transactions, exactly-once claims, and global ordering require explicit evidence and infrastructure guarantees. Do not imply them from a decorator or client API.

## Queues and background work

Use a queue when work may be deferred, must survive process failure, absorbs bursts, or needs an independently scaled worker. Define:

- stable job identity and idempotency key;
- timeout, retry class, maximum attempts, backoff, and jitter;
- concurrency, rate, payload, and backlog bounds;
- poison-message isolation, dead-letter inspection, replay, and retention;
- ordering or partition key only where the business requires it;
- queue age, attempts, failures, and processing-duration telemetry.

An in-process event emitter is not a durable queue.

## Operate each service

- Keep instances stateless or externalize shared coordination explicitly.
- Distinguish liveness, readiness, and startup checks. Do not make liveness depend on every downstream service.
- Set deadlines on every remote call and retry only transient, safe operations inside a total budget.
- Propagate correlation and trace context without putting secrets or unbounded values in telemetry.
- Mark unready, stop intake, drain or safely requeue work, and close resources during shutdown.
- Maintain service-level objectives, ownership, runbooks, capacity assumptions, and rollback procedures.

## Verify the boundary

Use contract tests for producer/consumer compatibility, integration tests with the real transport where semantics matter, duplicate and partial-failure tests, and load/soak tests for queue or dependency limits. Test mixed-version rollout and rollback for public messages.

## Skill handoff

This reference owns whether a service boundary should exist, who owns data, and how contracts cross it. The Features, Scaling, and Performance skill owns Nest transporter configuration, queue implementation, observability mechanics, backpressure, load measurement, and shutdown implementation. The OOP and Design Patterns skill owns collaborations inside one service.

See the official NestJS [microservices](https://docs.nestjs.com/microservices/basics), [queues](https://docs.nestjs.com/techniques/queues), and [health checks](https://docs.nestjs.com/recipes/terminus) guidance. Verify transporter-specific behavior against the installed package version.
