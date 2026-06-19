# Dependency Policy

Runtime dependencies should be pinned for CI and release gates.

Current v0 policy:

- Python CI dependencies belong in `requirements-ci.txt`.
- Release-critical dependencies should use exact pins.
- Generated packages should avoid fetching code during normal execution.
- Any future package manager lockfile should be included in the trust report.
