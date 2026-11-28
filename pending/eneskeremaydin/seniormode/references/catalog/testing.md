# Testing and verification

- [Consumer contracts for API compatibility](../knowledge/testing/contract-testing.md) · Catch provider changes that break a real consumer's expectations before independent deployment.
- [Deterministic tests for time-dependent code](../knowledge/testing/deterministic-time-tests.md) · Test time boundaries without wall-clock sleeps or flaky assumptions about scheduling.
- [Controlled fault injection and recovery tests](../knowledge/testing/fault-injection-basics.md) · Verify documented rollback and recovery behavior with bounded fault scenarios in test environments.
- [Load tests with realistic arrival models](../knowledge/testing/load-test-arrival-model.md) · Choose and document load generation that exposes queueing under the stated traffic pattern.
- [Property-based tests for invariants](../knowledge/testing/property-based-testing.md) · Explore input combinations with reproducible generators and meaningful invariants.
- [Focused snapshots for stable outputs](../knowledge/testing/snapshot-test-scope.md) · Use snapshot tests where reviewing the full stable output adds value and keep updates intentional.
- [Choosing test doubles and integration seams](../knowledge/testing/test-double-boundaries.md) · Choose test doubles according to the behavior the test is intended to prove.
