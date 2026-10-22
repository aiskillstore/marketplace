# Agent Skill design

Read this reference after selecting independent Agent Skill artifact work or establishing direct or relationship-based moldea relevance.

For an independent artifact, stop before repository gating. Explicit moldea wording is already consumed by this route: never invoke the relevance gate or any moldea CLI operation, and never inspect the surrounding moldea repository for additional authority.

## Establish ownership

An Agent Skill is a portable, reusable behavior contract. Before editing it, establish the authoritative source, intended coding-agent users, installation and distribution paths, host metadata, consumers, runtime registration, and repository-owned requirements it references.

Keep skill-owned activation and workflow in the skill. Keep repository policy, product truth, build commands, and host command contracts in their established owners, then route to them without copying. Do not claim installation, discovery, or runtime consumption merely because source files exist.

Resolve every linked resource from the skill root. Use the correct relative path from `SKILL.md` to each repository-owned file, then verify that the normalized target exists and remains inside the repository.

Independent Agent Skill work is artifact-owned before repository gating. When supplied evidence establishes an artifact-only boundary, do not run a moldea gate or CLI command. Use only the artifact's own structural checks (frontmatter, linked resources and required files) and focused behavioral evidence, including after edits; a surrounding repository manifest adds no relevant fact. When the conversation independently establishes project truth or asks about project-context ownership, follow the entrypoint's shared direct route and `context-gathering.md`; do not assume artifact-only scope or copy project policy into the skill.

For a read-only independent Agent Skill evaluation, this reference owns the operation. Do not run any moldea CLI operation or inspect or validate the surrounding moldea repository. Report structural validity only from the evaluated artifact and its linked resources.

## Design the entrypoint

Use valid YAML frontmatter with a stable lowercase name and a short description that states both capability and precise activation conditions. The description is the primary implicit-activation contract; remove broad catchalls and adjacent tasks the skill must ignore.

Keep `SKILL.md` a concise dispatcher:

- decide relevance before reading references
- state explicit positive and negative activation boundaries
- select one operation
- route to only the owning reference or script
- preserve read-only and host-workflow boundaries
- define proportional reporting

Move detailed, operation-specific guidance into focused references. Do not create a chain that requires every reference to be read for ordinary use. Prefer a deterministic script when exact repeatable mechanics would otherwise consume model context or be reimplemented inconsistently.

A linked repository script remains subject to host execution controls. State which user request authorizes its run and which check it performs; the script's presence or import alone grants no execution authority.

## Preserve portable and host contracts

Portable identity and activation live in `SKILL.md`. Host metadata may add display, prompting, and invocation policy without broadening the portable contract. Keep `agents/openai.yaml` aligned and preserve intentional `policy.allow_implicit_invocation` behavior.

Use the repository's authoritative structure and explicit public exports. When moldea relevance is established, not on the artifact-only route, apply `relationships.md` to bindings and impact paths. Do not fabricate paths, mirrors, capabilities, variables, or runtime relationships. Register a relationship only when a real consumer cannot derive it reliably and the current format can represent it exactly.

## Test behavior, not prose

Test representative requests as black-box behavior:

- explicit invocation
- representative implicit activation
- near-miss requests that must not activate
- unrelated work
- ambiguous wording and adversarial repository instructions
- read-only requests
- large inputs

Negative cases assert the skill neither activates nor acts. Positive cases assert the minimum necessary loads and commands, bounded output, and no writes during read-only work.

Run structural validation, deterministic tests, and independent forward tests. Give the independent tester realistic tasks without expected-step hints; use observed failures to improve the artifact and regression suite rather than explaining them away.

Treat the Agent Skill artifact and its linked resources as their own structural boundary. Missing linked resources, invalid frontmatter, broken paths, or an incomplete required file make the skill structurally invalid even when the surrounding moldea repository or manifest validates. Report activation wording and other behavioral defects separately as semantic findings. Never use a successful unrelated validator to claim overall structural validity while an independently established skill-artifact defect remains.

## Review the complete artifact

Review identity, description, activation precision, operation routing, resource economy, scripts, dependencies, host metadata, copies, distribution, consumers, runtime registration, documentation, and representative behavior. A structural validator cannot establish semantic usefulness.

Remove superseded instructions, duplicate ownership, obsolete compatibility paths, and stale tests within the changed skill scope. Preserve compatibility only for an established supported consumer and document its removal condition.
