# Benchmark Reference

Socratic Story Cartographer v2.1 was shaped by a structured same-model comparison across three story-development objects: literary short fiction, a 26-episode series outline, and an episode screenplay.

The comparison used three skill specifications and three semantically equivalent prompt variants per object, for 27 condition runs. Runs were judged on diagnostic validity, evidence traceability, discriminating test quality, leverage/intervention quality, regression safety, object fit, and convergence discipline.

The purpose of the benchmark is not to claim that an AI can objectively judge art. It tests whether a skill specification produces more auditable, adversarial, and stable story-development reasoning.

Key design changes in v2.1:

- **Evidence Anchor:** root-level diagnoses must be tied to concrete textual observations and keep evidence, inference, and diagnosis separate.
- **Loop Delta:** each loop must state what belief was strengthened, weakened, rejected, or newly introduced; if another loop adds no meaningful update, the process stops.

The full methodology, scores, held-out checks, and limitations are documented in `../BENCHMARK.md`.
