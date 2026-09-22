# Agent Harness example

[中文](agent-harness.zh.md)

This is a conceptual architecture for demonstrating Birdview, not a map of
Birdview's implementation or any particular coding agent. All `src/` ownership
paths in the example are illustrative. The supported status denotes the authored
example design, not inspected production code. No live execution is connected.

The workbench sends goals to session control. A scheduler dispatches an agent
loop, which requests composed context through a model gateway. Context can reuse
cached summaries. Model responses may contain text or requests for tool actions.

Policy checks gate tool execution and can request human approval through the
review interface. Approved calls go to a sandbox workspace or MCP services.
Tool results return to the loop; diffs and verification output reach review.
The loop persists events and checkpoints for session recovery and progress display.
Review feedback may revise the goal. These arrows describe logical interactions,
not mandatory synchronous calls or a guarantee of secure sandboxing.

Three groups distinguish interaction, runtime responsibilities and external
execution/services. They do not assert deployment or trust boundaries.

The example intentionally includes fan-out, return paths, approval round trips,
cache and persistent storage, and long connections across groups. Names,
responsibilities and relationship descriptions are available in Chinese and English.

## DeepSeek Harness constraints

The six rules below were verified against the clean local DeepSeek Harness checkout at commit `7a0b7682b6690f0aa2d93438c4d526b38ab45777` on 2026-09-17. Sources are DeepSeek AI's MIT-licensed [AGENTS.md](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md) and [docs/defensive-patterns.md](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/docs/defensive-patterns.md). These are real source rules projected onto this conceptual diagram, not a verified map of the DeepSeek Harness implementation. The timeline, implementation plans and verification results remain simulated. This is a selected rule set, not a complete audit of directory-level instructions.

- **Await teardown completion** ([defensive-patterns.md:19-21](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/docs/defensive-patterns.md#L19-L21)): issuing cancellation is insufficient; async cleanup waits for child work to exit, and notification registries close before termination.
- **Report only checks actually run** ([AGENTS.md:90-96](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L90-L96)): match focused checks to the changed surface and report only executed commands; CI owns exhaustive coverage and the platform matrix.
- **Update every API consumer** ([AGENTS.md:7](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L7)): public APIs are pre-stable. If an API changes, update every consumer; this is not a blanket backward-compatibility requirement.
- **Configure deployment-varying choices** ([AGENTS.md:116](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L116)): use validated `Config` fields adjustable through `cordis.yml`; default constants and test hooks do not constitute configurability. Protocol constants, external specifications and security invariants stay fixed.
- **Log model-visible inputs** ([AGENTS.md:111](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L111)): model requests must be reconstructable from the session log; new model-visible input requires a session event.
- **Extend through plugins** ([AGENTS.md:112](https://github.com/deepseek-ai/deepseek-harness/blob/7a0b7682b6690f0aa2d93438c4d526b38ab45777/AGENTS.md#L112)): place new behavior on documented extension points; changing `agent-loop` also requires updating `docs/architecture.md`.

The map's inspection paths refer to this local source summary and its translation. Upstream inspection was limited to the two files above; package-specific instructions and implementation compliance were not inspected. Module associations and suggested verification methods are Birdview's authored projection, not additional upstream requirements.
