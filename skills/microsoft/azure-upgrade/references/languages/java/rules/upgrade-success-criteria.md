# Upgrade Success Criteria (ALL must be met)

- **Goal**: All legacy Azure SDK dependencies (`com.microsoft.azure.*`) replaced with modern equivalents (`com.azure.*`).
- **Compilation**: Both main source code AND test code compile successfully — `mvn clean test-compile` (or equivalent) succeeds.
- **Test**: **100% test pass rate** — `mvn clean test` succeeds. Minimum acceptable: test pass rate ≥ baseline (pre-upgrade pass rate). Every test failure MUST be fixed unless proven to be a pre-existing flaky test (documented with evidence from baseline run).

If any criterion is not met, load [`./troubleshooting.md`](./troubleshooting.md) at that point — do NOT stop or defer.
