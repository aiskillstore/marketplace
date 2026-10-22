# Agent-system planning

Read this reference after adoption and agent-system planning intent are established. Ordinary conversation about agent responsibilities or orchestration is sufficient; the developer need not name moldea, canonical paths, or existing agents.

## Select this operation narrowly

Select planning when the developer asks what agent-and-software system should accomplish an objective, what should be agents versus deterministic components, or how agent responsibilities should be separated and orchestrated.

Generic implementation, architecture, migration, refactor, deployment, and host-defined `plan` commands remain outside. Relevance-triggered maintenance does not create a planning exercise without clear intent.

## Keep planning read-only

Repository-dependent moldea planning requires an adopted repository. Before adoption, moldea abstains and the host may still perform its own generic planning workflow independently. Planning changes no repository, dependency, Git, protected instruction, generated artifact, or external system. It creates no canonical plan, cache, or planning database.

When runtime identity is material, use `runtime-guidance.md` and bounded repository evidence. IDs select guidance, not compatibility guarantees. Do not install tooling, probe package resolution, or use global or transient launchers to plan. Without compatible local tooling, continue from evidence and disclose the limitation.

## Plan from the objective

1. Establish the outcome, recipient, trigger or cadence, deliverables, success criteria, constraints, and prohibited outcomes that materially shape the system.
2. Apply `context-gathering.md`: reuse host evidence and inspect only candidates that can change a material responsibility or absence claim.
3. Decompose every evidence-established outcome into the smallest cohesive responsibilities before naming components.
4. Classify each responsibility as deterministic application or data logic, an existing or proposed service or runtime-native tool, a reusable Agent Skill, an AI agent, human control, or a deliberate combination with explicit boundaries.
5. Keep fixed calculations, eligibility, filtering, storage, delivery, and predictable sequencing deterministic unless evidence establishes a need for model reasoning.

Use an Agent Skill for reusable on-demand coding-agent procedure or knowledge. It is not an independently executing runtime agent, deterministic service, or side-effect authority.

## Minimize and justify agents

A valid result may use zero agents. Prefer the smallest topology that preserves every material responsibility and boundary.

Create a separate agent only when independent ownership materially improves specialized context, permission separation, failure isolation, routing, reusable reasoning, independent evaluation, or maintenance. Reconcile every evidenced responsibility with a deterministic, service, tool, skill, agent, or human owner. Combining or removing an owner requires reliable replacement evidence. Responsibilities with incompatible private context, permissions, trust, or failure boundaries remain separate unless deterministic software replaces one.

Reuse an agent only when the added responsibility remains cohesive with its established purpose. Do not create a god agent, split cohesive work to manufacture multiple agents, or add planners, critics, supervisors, memory, autonomous loops, or orchestration by fashion. Public research and privileged project or customer reasoning remain separate when data boundaries conflict.

For every agent candidate, establish:

- responsibility and why it requires model reasoning
- principal inputs, outputs, decisions, and project context
- capabilities, data access, permissions, and affected state
- interaction, handoff, escalation, and failure boundaries
- why deterministic software or another candidate should not own it

Names and IDs remain proposed until a later write-capable workflow establishes them.

## Design control, state, and contracts

Prefer deterministic orchestration for reliable sequencing, branching, and routing. Use a model router only when selection genuinely requires semantic judgment. Repository format version `1` has no canonical orchestration or handoff graph; later implementation must use runtime-native mechanisms and agent-owned surfaces.

Identify authoritative and derived data, transient and persistent state, readers and writers, deterministic enforcement, recommendation versus execution authority, human approval or escalation, and least privilege. Preserve established approval scope, including approval for every publication when required. Do not imply data access without a source or access path.

Describe the principal inputs, outputs, events, service and tool contracts, and failure boundaries needed for interaction. Planning need not finalize schema syntax, but separation cannot depend on hidden contract assumptions.

## Assess runtime connections honestly

Use only inspected facts. An opaque injected client is an evidence gap, not proof that tools, schemas, state, persistence, retries, or other behavior are absent. Keep the declared runtime label, actual repository wiring, and behavioral fit separate. Core's binding coverage concerns declared files and explicit exports only; neither a passed check nor a guidance row proves a connection.

Runtime selection is optional unless requested or material. Select the SDK that defines the agent under `runtime-guidance.md`'s selection rule. Follow only the relevant call path, stop at dynamic boundaries, and search installed types once per needed field. Pair material unknowns with concrete resolvers: closed wiring, source-owned documentation, or focused connection tests. Preserve an existing ID when evidence is incomplete; for a new plan, leave it undecided rather than defaulting to `custom`. Recommend an authorized test of the outgoing canonical instruction and schema when it would resolve a connection gap.

## Produce one actionable recommendation

Give one preferred architecture when evidence supports it; present alternatives only when their tradeoff could change the decision.

Cover every materially applicable objective, established context, constraint, responsibility and owner, agent justification, deterministic component, service or tool, human control, authoritative data, persistence, permission, control flow, model contract, deterministic enforcement, failure, runtime consideration, tradeoff, and implementation step. This is a completion check, not a mandatory prose template.

Name material paths read and what they establish. Preserve or reliably replace every resulting responsibility. Recommend an ordered, unexecuted build-and-verification sequence that tests risky boundaries early; runtime control flow is distinct and must also be described.

When a material decision remains unresolved, investigate or ask the one question that most changes authority, ownership, topology, or consequential side effects. Still state the invariant architecture and identify what cannot be finalized.

Finish by distinguishing the recommendation from current implementation and canonical state and state that no repository files changed.
