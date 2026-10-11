# Sources and design provenance

Checked 2026-10-07. The skill is a synthesis and an engineering policy, not an implementation of a single paper. No paper below establishes that repeated reviews eliminate every software defect. Loop counts, tier thresholds, review routing, and helper gates are Gauntlet design choices that need workload-specific evaluation.

## Format and host documentation

**Agent Skills specification** — https://agentskills.io/specification
The portable format requires a skill directory with YAML-frontmatter `SKILL.md`, including a valid name and description. Optional scripts, references, and assets support progressive loading. Gauntlet keeps the entry point short and links directly to focused resources. The standard's optional experimental tool-allowlist field is deliberately omitted: a portable skill cannot grant itself execution permissions.

**Agent Skills authoring guidance** — https://agentskills.io/skill-creation/best-practices
Supports task-specific procedures, appropriately bounded detail, clear loading triggers, useful scripts, and iteration from actual execution rather than simply making instructions longer. Gauntlet's behavior still needs host/model evaluation.

**OpenAI skill authoring and installation** — https://developers.openai.com/codex/skills (redirects to https://learn.chatgpt.com/docs/build-skills)
Checked the current user/repository `.agents/skills` locations and optional `agents/openai.yaml` appearance metadata. Gauntlet is shipped as a standalone skill directory, not a complete plugin. Other hosts may use different import paths.

**OpenAI skill metadata reference** — https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/references/openai_yaml.md
The optional metadata file uses interface display name, description, icons, brand color, a `$gauntlet` starting prompt, and implicit-invocation policy. No MCP dependencies are declared because the workflow has no mandatory remote tools.

## Research grounding and limits

**Madaan et al., Self-Refine: Iterative Refinement with Self-Feedback (2023)** — https://arxiv.org/abs/2303.17651
Studies iterative generation, feedback, and revision across several tasks. Motivates a bounded critique/revision cycle. It is not a universal proof that self-review improves arbitrary code or that a chosen stopping rule certifies correctness.

**Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning (2023)** — https://arxiv.org/abs/2303.11366
Uses feedback and stored reflections to inform later attempts. Motivates a compact persistent record of failures and next actions. Gauntlet stores observable evidence and concise rationale, not private model deliberation or an assurance that memory alone fixes defects.

**Bouzenia, Pradel, and Avgerinos, RepairAgent: An Autonomous, LLM-Based Agent for Program Repair (2024 preprint)** — https://arxiv.org/abs/2403.17134
Explores tool-using autonomous program repair. Motivates inspect/repair/validate loops tied to a concrete software artifact. Benchmark performance does not establish that generated patches repair the root cause in every setting.

**Huang et al., Large Language Models Cannot Self-Correct Reasoning Yet (2023 preprint; ICLR 2024)** — https://arxiv.org/abs/2310.01798
Examines limitations of intrinsic self-correction without external feedback. Motivates Gauntlet's insistence on actual tests, source traces, and independently checkable evidence instead of repeated self-approval. Its experiments should not be overgeneralized to all newer models or tool-rich settings.

## How to interpret this release

The included automated tests exercise tracker state transitions, revision invalidation, budgets, input validation, transaction rollback, and selected filesystem/CLI behavior. They do **not** establish improved LLM review quality. The behavioral evaluation scenarios are supplied for future model/host testing; do not report them as executed unless actual runs and outputs have been collected.
