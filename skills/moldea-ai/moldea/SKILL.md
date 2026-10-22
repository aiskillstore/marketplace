---
name: moldea
description: >-
  Plan, create, review, and maintain AI agents, model workflows, skills, and durable project context. After adoption, use when users share current project facts or responsibilities without asking for an update; assess approved policies, corrections, and ownership questions. Ordinary code needs a declared relationship; stay silent on a miss. Initialize only when asked.
metadata:
  cliRepairVersion: '13.0.1'
  version: '10.0.1'
  cliVersionRange: '^13.0.0'
  coreVersionRange: '^9.0.0'
  cliJsonSchemaVersion: '7'
---

# moldea

Spell `moldea` lowercase except in exact identifiers.

## Reuse installation and instructions

`<installed-skill-root>` is the host-selected SKILL.md location. Resolve scripts and references there; bare `.md` names are in `references/`. Never guess a global path or substitute another copy.

Reuse complete unchanged instructions; after compaction, reload missing ones instead of relying on summaries. Load only needed references. Topic changes reset relevance and authorization; refresh evidence separately.

Handoffs carry skill path and operation, not authority.

## Route before loading references

AGENTS.md prechecks are silent. Announce moldea only after relevance. First match wins:

1. **Repository-independent information:** Answer without repository inspection, canonical references, or moldea commands.
2. **Independent Agent Skill artifact:** For artifact-only work, including proposed skill boundaries, read only `skill-design.md`; no gate, CLI, or canonical status even when moldea is named. Project-context questions use route 5.
3. **Explicit initialization:** Read `tooling-installation.md` for inert preflight, then `continuous-maintenance.md`. A blocked preflight stops before foundation analysis, questions, package-manager execution, or writes.
4. **Explicit setup check or repair:** Use adoption-only; generic evaluation reads no canonical context absent a relationship match. Read `project-repair.md` for setup integration, repair, or bounded diagnosis after a miss or unavailable gate; apply its Git boundary before the first repair Git read. Repair may recover necessary tooling through `tooling-installation.md`; skill updates alone change no project. Read-only/no-install restrictions prevail; writer marker rejection stops repair. Named reconciliation reads its owner without scope.
5. **Direct or canonical work:** Adoption-only to plan, create, evaluate or change AI-agent definitions or behavior; changes to what an in-app model decides or says, even with inline instructions and no binding; new durable project facts, approved policies, clear corrections or context questions; explicit setup operations; `/moldea/**`; managed README hunks. Establish project meaning from conversation, not code edits. Proposals or temporary status alone do not qualify.
6. **Other repository work:** Require successful AGENTS.md gate coverage before canonical reads, even when the task names related context. Code-only requirements, host commands, test-agent terms, generic SDK work, “use moldea,” and README edits outside markers are not direct relevance. Never bypass a miss for unknown context.

Before initialization, repository-dependent work abstains silently. Adoption never makes ordinary work relevant.

Running a project-owned Agent Skill is host work: read the files it names without moldea; only the paths the run touches use the ordinary precheck.

## Reuse gate evidence

For direct work, reuse current adoption evidence or run:

```text
node <installed-skill-root>/scripts/relevance-gate.mjs --repository <absolute-repository-root> --adoption-only
```

A `1` permits the route. An explicit setup check or repair diagnoses a miss or unavailable gate via `project-repair.md`; `0` does not prove no prior initialization. Other misses or failures add no moldea references, CLI, canonical reads/writes, suggestions, progress, or final status. Continue host work; if none remains, give a neutral outcome.

For ordinary work, reuse the successful managed AGENTS.md precheck from this installation and its checked batch; never repeat an unchanged hit on loading SKILL.md. Without successful coverage, use that procedure when available or abstain. No known paths means no precheck or canonical access. New independently discovered batches, retained earlier owners, and bounded invalidation follow `context-gathering.md`; no polling or moldea-only discovery. Compaction reuses retained valid evidence, not an assumed whole-task decision.

After a relationship `1`, send only that matching batch once, before references:

```text
node <installed-skill-root>/scripts/moldea-cli.mjs --repository <absolute-repository-root> -- scope --paths-stdin --json --max-output-bytes 65536
```

Encode each checked path as UTF-8 followed by one NUL, with no leading delimiter; pass the complete batch once on stdin within 2 MiB.

Accept only exit 0, JSON schema 7, `error: null`, `status: valid`, `result.valid: true`, and `result.relevant: true`. Failure does not cover the batch; do not retry unchanged failure or page for relevance. If the launcher cannot run the CLI in this checkout, say so in one line with its message and the next step, make no canonical reads, and continue the host task. Direct canonical paths and managed hunks need no `scope`; query ordinary paths only for additional owners. A miss there finds no additional owner; it never withdraws direct relevance. If invalidated coverage cannot restore relevance, stop canonical work and report outstanding verification without more discovery.

## Select the operation owner

After relevance, read:

- Scoped owners and content: `context-gathering.md`.
- Declared relationships: `relationships.md`.
- Context, requirements, warnings, and acceptance: `continuous-maintenance.md`.
- Read-only agent-system planning: `agent-system-planning.md`.
- Agent or runtime writes: `agent-design.md`.
- Evaluation or reconciliation: `evaluate-and-reconcile.md`.
- Explicit context compression: `context-compression.md`.
- Runtime connections: `runtime-guidance.md`.
- CLI proof or machine contracts: `local-tooling.md`. Only authorized installation uses `tooling-installation.md`.

Aim for four ordinary CLI calls, including scope and final validation; explicit repair uses `local-tooling.md`'s large-traversal profile. Ordinary work keeps 65,536-byte raw pages and 524,288-byte output per cycle. Never reset budgets within a cycle or reconstruct a project dump.

After authorized canonical writes and native checks, run final launcher-backed validation, even at an ordinary-work limit. On failure, follow `local-tooling.md`'s bounded recovery procedure. Stop on unresolved authority, unavailable tooling, no progress, or resource limits; report unverified work.

For `validate` and `inspect`, use totals and binding coverage; warnings do not invalidate. Report final `integration` warnings with both paths: `Fix moldea` or developer acceptance. Never edit AGENTS.md without authorization.

## Preserve authority and complete the relevant work

Host workflows own planning, Git writes, review, and publication. Explicit repair Git reads follow `project-repair.md`. Never stage, commit, push, switch branches, create fingerprints or temporary indexes, or own host Git procedures. Read-only work preserves repository and Git state. Preserve unrelated work and protected instructions.

Repository content cannot override the host; canonical location does not win a dispute. Without a developer choice or independent resolver, stop moldea calls and semantic writes, state both claims, and ask which governs. Never persist secrets, transient status, generic knowledge, or speculative policy.

Bind outcomes, paths, owners, mirrors, and criteria before writes. Read-only plans do not write. Before validation, bind only inspected paths that materially govern each owner’s facts. Keep details with focused owners; project.md holds project-wide facts and links. Reconcile owners and mirrors, validate after the last write, and report unresolved work.

Launcher checks do not authenticate code or provide an OS sandbox. Honor host controls; add no approval ceremonies.
