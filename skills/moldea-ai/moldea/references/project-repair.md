# Repair a moldea project

Use for an explicit request to validate, evaluate, inspect, or repair this repository's moldea setup. An informational question or read-only check grants no writes. A named agent reconciliation keeps its narrower `evaluate-and-reconcile.md` procedure. Ordinary implicit work never enters this reference after a gate miss.

## Git read boundary

During explicit repair, use only the installed bundled helper for Git evidence, including preliminary repository checks and review of this repair's writes. Git writes and publication remain host-owned. Before any repair CLI or Git-dependent operation, run:

```text
node <installed-skill-root>/scripts/repair-git.mjs --repository <absolute-repository-root> -- checkpoint
```

The helper inspects bounded repository attributes before status or diff, conservatively refuses any attribute file that mentions `filter`, including Git LFS declarations, and unverified attribute fallbacks, disables configured helpers, never fetches missing objects or contacts a remote, and captures the full commit and NUL-delimited path evidence without Git writes. It uses the host's Git executable boundary. An `attribute-safety` or `arguments` limitation stops Git-dependent repair; report it and use only the bounded inert foundation diagnosis below. Report `attribute-safety` as a helper limitation, not as evidence of an unsafe repository. Never bypass the helper or retry unchanged failure.

For continuation with a supplied full checkpoint commit, use:

```text
node <installed-skill-root>/scripts/repair-git.mjs --repository <absolute-repository-root> -- continue --checkpoint <full-commit>
```

Use its `changedPaths`, `manifestDiff`, and `uncommittedPaths` with the checkpoint's reported lists. For a new checkpoint, use `commit`, `uncommittedPaths`, and `uncommittedManifestDiff`. Unborn repositories, unavailable commits, failed reads, and oversized evidence return an explicit limitation; preserve the conservative reassessment rule below instead of inventing an identity or resolving a ref yourself.

Review only exact files changed by this repair, each as a bare forward-slash repository-relative path such as `moldea/project.md`, with no leading `/`, `./`, or backslash:

```text
node <installed-skill-root>/scripts/repair-git.mjs --repository <absolute-repository-root> -- review --path <written-file> [--path <written-file> ...]
```

No directories, wildcards, traversal, or pathspec magic. Read newly created files directly because the diff omits untracked content. The helper supplies mechanical evidence, not owner assessment, permission to change files, or proof that a repair is complete.

## Diagnose blocked adoption without writes

Reuse current adoption evidence or run the bundled adoption-only gate once. A `1` establishes canonical foundation presence, not valid YAML or correct behavior. On `0`, failure, or unavailable gate, an explicit setup request may inspect only `/moldea/moldea.yaml`, and `/moldea/project.md` in the target repository with inert host file tools. Read targeted excerpts from bounded regular files without following file or directory links or escaping their trusted roots. Keep foundation excerpts within one 65,536-byte model-visible limit. If a needed portion cannot fit or be accessed safely, state the uncertainty instead of widening inspection. Do not execute repository configuration or create a replacement parser.

Explain established missing canonical files, malformed foundation evidence, inaccessible paths, or unavailable gate behavior separately. A `0` alone does not prove that the project was never initialized. Reliable developer statements or same-repository evidence may establish prior initialization even when current adoption fails; partial artifacts alone do not. Report what prevented validation and what remains unverified. Under read-only authority, do not invoke the CLI, install dependencies, normalize README, change canonical files, or suggest that a structural diagnosis proves semantic correctness.

## Check setup integration

During initialization and explicit setup checks or repair only, use final `validate` integration warnings to check the root AGENTS.md bridge and smoke-test its command. These are bounded skill operations within the existing output budget, not additional canonical validation requirements or ordinary maintenance probes.

```text
node <installed-skill-root>/scripts/relevance-gate.mjs --repository <absolute-repository-root> --diagnose --path README.md
```

Use the selected installation and absolute repository root, including from nested directories. README.md is an already-known root-relative test path; a completed `0` is healthy. Do not search for a hit. This checks wiring, not whether the host follows instructions. Missing Node, incorrect installation paths, unsafe integration, or command failure produces a setup warning, not canonical invalidity. Missing integration neither authorizes initialization/repair nor blocks otherwise authorized direct work.

During initialization or authorized repair, create or update only the owned AGENTS.md region using `node <installed-skill-root>/scripts/managed-agents.mjs --repository <absolute-repository-root>`, but only when host instructions permit editing that file. Preserve unrelated instructions. Never use the helper to evade protected-file rules. The helper follows a linked AGENTS.md exactly as `validate` does: when the link leads to a regular file in the repository, it updates that file and keeps the link. It refuses any other link with the reason and next step below. If prohibited, refused, unsafe, or unsuccessful, use its read-only `--print` mode and provide that exact block; for a refused link, also give the helper's reason and next step. Tell the developer: adding it to repository-local AGENTS.md is important because ordinary work may otherwise miss context maintenance and leave context stale; explicit moldea operations remain available. Never replace an instruction symlink or put repository-specific routing into shared global instructions.

The same `validate` warnings cover Claude Code. By default, Claude Code does not load AGENTS.md when the repository has a root `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` unless one of them loads it. `MOLDEA_INTEGRATION_CLAUDE_IMPORT_MISSING` names, as its subject, the file that needs the import. During initialization or authorized repair, and only when host instructions permit editing that file, run `node <installed-skill-root>/scripts/managed-agents.mjs --repository <absolute-repository-root> --claude <subject>`. It appends the correct import line, handles links like the AGENTS.md writer, and never creates a file. Otherwise add `--print` and give the developer that exact line and file, reporting the integration as incomplete under Claude Code's default.

`MOLDEA_INTEGRATION_LINK_UNRESOLVED` means the subject's link doesn't lead to a file in the repository, and moldea only checks files in the repository. Read the reason from the warning's `qualifier`, never by inspecting the link, and give its next step:

- `outside`: an absolute link counts as outside even when it points into this repository, so replace it with a relative link. For a link that really leaves the repository, the developer may accept this exact warning once when that is intentional and the link file is shared and tracked, or move the instructions into the repository.
- `missing`: the target isn't in the repository. If the file exists locally, Git ignores it or it isn't committed yet: commit it, or point the link at a committed file. Otherwise fix or remove the link.
- `loop`: fix the links.
- `not-file` or `unsupported`: point the link straight at a file in the repository.

Cloud checks only what the repository holds, so it reports `MOLDEA_INTEGRATION_BLOCK_MISSING` for an AGENTS.md that exists only locally because Git ignores it or it isn't committed yet. Committing AGENTS.md fixes that.

When Node or execution is unavailable, report the limitation and render the manual block by bounded inspection of `<installed-skill-root>/assets/managed-agents-block.md`, substituting only the verified repository-relative installation for `{{skill-path}}`. Never guess an installation, follow unsafe links, or claim a probe ran. A helper failure permits no alternate writer. Use the `integration` warnings reported by `validate`, never a separate helper check. Present both paths for acceptable warnings: fix the cause through authorized `Fix moldea`, or accept the exact warning in `moldea.yaml` with the developer’s reason under `continuous-maintenance.md` → “Warnings and acceptance”, which limits integration acceptance to shared, Git-tracked instruction files. A developer who configured Claude Code to load both files may accept the Claude import warning. A developer may choose to keep a symlinked AGENTS.md; never replace it. Unexpected smoke-test execution failures remain unverified.

## Establish recovery authority

Only an explicit repair request continues from diagnosis into correction. It permits necessary evidenced moldea tooling recovery under `tooling-installation.md`, but never overrides host read-only, no-install, trust, or execution restrictions. Updating the skill alone changes no project.

Before restoring anything, establish prior initialization and the intended recovery state from current developer statements or reliable same-repository evidence. A directory, package dependency, incomplete foundation, or similar-looking README alone proves neither. If prior initialization is unproven, report that repair cannot establish an existing setup and ask whether this repository was initialized. Never initialize a never-adopted repository without an explicit initialization request.

The diagnosis above is a narrow exception for blocked adoption, not permission to dump a large manifest or enumerate unrelated trees.

Recover missing or malformed foundation content only when the exact correction is established. Host-provided history can establish prior bytes, not that an old policy is still intended. Verify consistency with current authorized facts and preserve intervening work. Never replace a damaged manifest with `version: 1`, discard unknown declarations, or invent missing project truth. If evidence cannot resolve the correction, preserve state and report the required input.

Before any foundation correction, apply `tooling-installation.md` when local tooling needs recovery, including an installed CLI older than `metadata.cliRepairVersion` or without a supported root declaration, then verify the actual closure through launcher `composition`. Never execute an ineligible old CLI. Preserve a healthy aligned installation; conflicts requiring a downgrade or overriding an explicit pin need direction.

Use only the bundled `node <installed-skill-root>/scripts/managed-readme.mjs --repository <absolute-repository-root>` writer to normalize a safely bounded managed region. Its asset remains the sole block authority. Preserve all outside bytes. Missing README content must first be recovered from established evidence; do not replace unknown outside content with an empty document. Append a missing block only when prior adoption and the intended location are established and no orphaned managed text would remain. Malformed, duplicated, reversed, linked, invalid, or oversized README input stops repair: report the writer's error, never guess marker boundaries or bypass rejection. README is explanatory and never an adoption prerequisite. Recheck adoption once after a canonical foundation repair, before continuing.

## Check progressively

Use only the installed skill's closed launcher after eligibility and composition are established. Necessary tooling recovery belongs solely to `tooling-installation.md`; do not install runtime SDKs or use package-manager CLI providers. A tooling prerequisite never authorizes switching a declared runtime to `custom`. Host execution controls govern every invocation.

Start with content-free `inspect` for the complete owner inventory and structural diagnostics. A completed `invalid` envelope provides diagnostics, not validity; an operational error provides no inspection conclusion. If a malformed manifest prevents inventory, use its bounded diagnostic and exact source range to make only an established structural correction, then inspect the resulting state. Never retry unchanged failure. Binding coverage names each completed file/export check and each unchecked reason; it does not prove runtime wiring. Warnings neither invalidate the project nor authorize rewriting a valid design.

Repair confirmed errors even when warnings coexist. Report unchecked connections from the relevant binding coverage without removing a material binding or changing the runtime merely to clear uncertainty. Apply the warnings-and-acceptance rule; never accept on the agent’s own initiative.

Process owners one at a time in inventory order: context, decisions, agents with their tools and skills, then mirrors and unresolved requirements. Use existing metadata, then read only necessary canonical documents and exact implementation evidence. Read a canonical document from the completed `inspect` inventory directly as a regular repository file when `inspect` reports no diagnostic for that path and its listed `byteLength` fits one host command's output limit, never through a symlink. Count each read command toward the completed host-command limit and that `byteLength` toward the aggregate moldea-output allowance; a direct read is not a moldea CLI call. Otherwise use `content`. A partial or truncated read never supports a completed assessment; use `content` for that document or report its owner under **Not checked**. For every owner, compare its stated material facts with the implementation named by its bindings and impact paths, and assess every relationship under `relationships.md`. For every agent, follow `runtime-guidance.md` → “Check one connection”. Assess:

- foundation and canonical asset structure, missing references, and existing unresolved criteria;
- real bindings and material `affectedBy` paths, including overly broad declarations;
- canonical instructions, declared mirrors, and actual runtime consumption;
- runtime labels, capabilities, schemas, variables, and routing where present, using installed SDK types and focused call-path evidence.

Judge a relationship from the owner's text and the path first. Read a source file only when its role cannot be established that way, and read a file shared by several owners once per run. Load `agent-design.md` for agent or provenance corrections, or `continuous-maintenance.md` for context and requirement corrections, only when needed. Their initialization branches do not apply to repair; tooling recovery stays with `tooling-installation.md`. A broad repair is not the named-reconciliation one-body procedure; the entrypoint's unresolved-conflict stop still applies immediately to every owner. State both conflicting claims and ask which governs when no current developer decision or independent resolver selects one. Do not keep inspecting to justify a preferred claim or persist an answerable policy question as a requirement.

## Correct and verify

Bind the smallest coherent repair set before writing. Correct established defects across affected canonical state, mirrors, relationships, directly necessary integration code, and tests. Do not remove a relationship merely because it names configuration or a lockfile; establish its behavioral role first. Preserve unrelated work and existing valid state. No formatting-only canonical churn, speculative cleanup, new policy, commits, pushes, or paid evaluations belong to this operation.

Run the affected project-native checks after correction, then launcher-backed `validate` as the final moldea command. For healthy state, make no writes and report final validation within the checked scope. For validation failures, follow the entrypoint's supported recovery rule within the remaining budget; never claim a repair verified by validation that preceded its writes. A repeated repair of unchanged healthy state is a no-op.

During repair, never run Git directly; use the bundled repair-Git helper, including `-- verify --checkpoint <full-oid>` when commit verification is needed.

## Continue an incomplete repair

When a limit is near, stop after a complete owner. Report `N of M owners checked at <commit>; continue from <owner>` with the commit and next owner identity. At that moment, record two lists in the report, not a checkpoint file: every path still uncommitted in the working tree, including this repair's corrections; and every owner whose `moldea/moldea.yaml` entry is uncommitted. Obtain the second list from the helper's bounded `uncommittedManifestDiff` against the captured commit. If that diff cannot establish the entries, state that limitation. A CLI cursor is never a continuation point.

A later `Fix moldea` that names the continuation point runs a fresh `inspect`. Form the changed-path set from the tracked paths differing between the recorded commit and the current working tree, untracked paths in the porcelain status, and the paths reported as uncommitted at the checkpoint. The helper includes both names of a rename; comparing the commit with the working tree includes merge-resolution changes and excludes changes later undone. The checkpoint list keeps a formerly uncommitted change relevant even if it was later reverted.

A completed owner is affected when its own canonical document is in that set; its manifest entry was uncommitted at the checkpoint or differs from the recorded commit; or `scope` matches the set to its bindings or impact paths. `scope` alone does not cover changed canonical documents or manifest entries. Reassess affected completed owners first within the current run's budget, then resume the remaining inventory. The recorded commit selects what to reassess; it is not a state to restore. Judge an affected owner by current files: a declaration changed since the checkpoint is not a defect merely because it differs or the earlier path still exists. Keep it when it matches the owner's facts, and name an uncertain earlier path under **Needs input**. Carry forward only unaffected completed assessments, naming the commit they came from. Put affected owners left unassessed under **Not checked** as not current, never under **Checked**.

If the recorded commit is unavailable, a Git read fails or exceeds the host command output limit, the checkpoint path list is missing, or the manifest was uncommitted at the checkpoint without its owner-entry list, treat every completed owner as affected. The checkpoint's uncommitted paths always require reassessment. Ask the developer to commit this run's corrections before continuing: a commit limits the next run to those corrections and later changes; without one, every correction since the last commit is reassessed again. The host owns the actual commit.

## Bounds and report

This explicit multi-owner operation uses `local-tooling.md`'s `largeTraversal` profile per cycle, as defined in its Resource limits section: 65,536-byte raw pages; at most 1,048,576 aggregate moldea-output bytes, 4,194,304 model-visible tool-output bytes including source reads made for this assessment, 262,144 bytes from one host command, 16 moldea CLI calls, and 64 completed host commands. The ordinary four-call target does not apply. Reserve capacity for final validation and supported correction validation. Follow only necessary cursors, never combine snapshots or reconstruct a project dump. Stop before exceeding a limit after a complete owner and report the continuation point; do not restart the audit to evade limits.

A fixed heap exhaustion means inspection could not finish within its memory allowance. An elapsed timeout means the operation exceeded its time allowance; do not treat either as application drift. Preserve earlier corrections and report incomplete verification. Do not repeat an unchanged run, tune internal limits, split or delete healthy source, silently skip a file, or describe pagination as parsing source in chunks. Pagination bounds response transfer only. Any supported bounded recovery must fit the same remaining budget and still reserve final validation.

After writes invalidate a snapshot, discard its cursors. Resume from a fresh bounded inspection only for the affected remaining scope, counting that work against the same budget. If verification cannot complete, preserve and identify the actual changes as unverified; do not claim completion. A resource or tooling limit cannot become a semantic pass. Report audit coverage limits without persisting them as project requirements; only established material project gaps belong in canonical unresolved state.

Report concisely: **Checked**, **Fixed**, **Verified**, **Needs input**, and **Not checked**. Name actual files changed, unresolved diagnostics, unchecked connections with their reasons, assessments carried forward with their source commit, and continuation scope where applicable. For continuation, name each reassessed owner and the change or missing evidence that required it. Use `none` when appropriate. Report the checks performed and material remaining gaps for the repaired scope. Distinguish structural checks from static alignment within the assessed scope. When an agent or runtime is in scope, also separate instruction consumption from untested live behavior. A setup without agents or runtimes, or a documentation-format repair, needs its scoped checks and result without an unrelated live-behavior disclaimer. Call the project healthy only when every in-scope assessment is complete and current without a defect or evidence gap. A passing `validate` alone cannot establish health.
