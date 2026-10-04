# Testing Rules

Choose a test boundary that can prove the behavior at risk. Do not use Nest's testing container for every class, and do not mock away the integration whose correctness matters.

## Match the test to the boundary

| Boundary or risk | Preferred test |
| --- | --- |
| Value object, policy, pure service | Plain unit test with direct construction |
| Application operation | Unit test with small owned fakes/stubs |
| Provider token, decorator metadata, module exports, scope | `TestingModule` compilation or focused framework test |
| Database/cache/broker/vendor adapter | Integration or contract test against a realistic dependency |
| HTTP/GraphQL/WebSocket/message contract | E2E test through the real application boundary |
| Architecture dependency rule | Static graph/import rule or repository check |
| Capacity, leak, queue lag, event-loop behavior | Repeatable load, soak, or failure test |

Plain construction gives faster and clearer feedback when Nest wiring is not under test. Use `Test.createTestingModule()` when provider resolution, overrides, scopes, guards, pipes, interceptors, filters, or module metadata are part of the behavior.

## Unit tests

- Assert observable behavior, returned values, state transitions, and domain failures.
- Fake application-owned ports; do not reproduce an ORM, queue, or vendor SDK in a giant mock.
- Avoid testing private methods, implementation order, or call counts unless the interaction itself is the contract.
- Use controlled clocks, identifiers, randomness, and retry schedules instead of sleeps.
- Keep fixtures minimal and name the business condition they establish.

Mocking an external dependency is appropriate for a unit test. It is not evidence that the real adapter, schema, authentication, timeout, or failure mapping works.

## Integration and contract tests

- Exercise the same database engine, broker, cache, or protocol whose semantics matter; an in-memory substitute can hide SQL, isolation, delivery, and serialization defects.
- Use isolated databases/namespaces and deterministic cleanup. Never point tests at production or a shared mutable developer environment.
- Apply real migrations before persistence tests when migration safety is in scope.
- Add provider/vendor contract tests for request shape, authentication, response mapping, timeout, and error classification. Use a sandbox or controlled stub server based on cost and risk.
- Test constraints, concurrent writes, duplicate delivery, poison messages, and reconnect behavior where relevant.

## End-to-end tests

Bootstrap the application with production-relevant global configuration so validation, serialization, guards, interceptors, filters, and adapter behavior are exercised. Supertest is a useful HTTP choice, not a requirement for GraphQL, WebSockets, RPC, or message consumers.

Cover successful and failed contracts: malformed and unknown input, authentication, authorization/ownership, response field allow-lists, stable error codes, idempotency, pagination bounds, and cancellation or timeout where supported.

## Reliability and deployment tests

For critical flows, test:

- dependency timeout and transient/permanent failures;
- retry exhaustion and duplicate delivery;
- partial completion, outbox publication, or compensation;
- readiness changes and graceful shutdown with in-flight work;
- mixed-version messages or APIs during rollout;
- resource and concurrency bounds under representative load.

Keep performance tests separate from ordinary unit suites and record workload, environment, data volume, cache state, percentiles, throughput, errors, and saturation.

## Prevent flaky suites

- Do not rely on test order, wall-clock sleeps, live internet, or shared global state.
- Await cleanup and close Nest applications, sockets, timers, workers, database pools, and broker clients.
- Give asynchronous assertions bounded deadlines with diagnostics.
- Fix or quarantine a flaky test with an owner and exit condition; blind retries hide nondeterminism.
- Parallelize only after isolating ports, databases, queues, files, and identifiers.

## Skill handoff

This reference owns test-layer choice and runtime verification. The Architecture and Principles skill owns module/data/service boundary assertions. The OOP and Design Patterns skill owns object-level behavior and refactoring seams. [Failure resilience and testing](failure-resilience-testing.md) defines the error-specific failure matrix, while this reference selects the test boundary. Performance claims require the measurement workflow in [performance-diagnosis.md](performance-diagnosis.md).

See the official NestJS [testing](https://docs.nestjs.com/fundamentals/testing) guidance. Verify helper APIs against the installed NestJS and test-runner versions.
