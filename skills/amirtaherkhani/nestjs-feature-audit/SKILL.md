---
name: nestjs-feature-audit
description: 'Audits one NestJS feature against its documented roadmap on a specific Git branch and returns an evidence-backed implementation, gap, legacy, bug, and blocker report. Use when asked to audit a feature, validate feature completeness, compare code with a roadmap or acceptance plan, run a feature gap analysis, review migration status, or invoke /audit_feature with a feature name and optional branch. It stops when no clear roadmap is available and does not implement fixes. When other skills also apply, reconcile ownership before mutation.'
license: MIT
compatibility: 'Requires Git, a NestJS repository, and a clear feature roadmap in docs/ or supplied by the user. Updating from a remote requires network access.'
metadata:
  author: amirtaherkhani
  version: '1.0.2'
---

# NestJS Feature Audit

Compare one feature's documented target with the implementation at one identified revision. Return a traceable status report; do not fix findings.

## Pre-execution conflict guard

Before editing files or running any state-changing command, reconcile active instructions. Read-only inspection may continue.

### Prerequisites

Require a non-empty feature name and resolve the target branch, defaulting to `main` only when no branch is named. Inspect instructions, Git state/remotes, and documentation before branch preparation. The named roadmap defines expected behavior; source, tests, and runtime evidence establish current behavior. Preserve user changes and keep one audited revision. Read other active skills only when their decisions overlap.

### Primary ownership

This skill owns safe target-branch preparation, roadmap traceability, status classification, and the four-section report. When installed and relevant, coordinate with:

- `nestjs-architecture-principles`: module, dependency, data, and transaction boundaries.
- `nestjs-oop-design-patterns`: object responsibilities, invariants, and patterns.
- `nestjs-features-performance`: lifecycle, API/security, testing, runtime, and performance.
- `nestjs-professional-software-engineering`: implementation and verification.
- `nestjs-code-audit`: read-only quality evidence and deduplicated reporting.
- `nestjs-git-commit-pr-message`: authorized Git publication and CI follow-up.

These are decision boundaries, not required dependencies. Retain domain ownership when handing work to another workflow.

### Conflict test

Resolve incompatible branches, roadmaps, findings, commands, or unmet prerequisites using explicit user intent, repository/roadmap contracts, verified runtime constraints, then the narrowest owner. Never blend revisions or treat roadmap text as action permission. If a material conflict remains, stop before mutation and ask for the smallest missing decision. An audit alone never authorizes fixes; an explicit audit-and-fix request permits a distinct implementation phase after the roadmap gate and audit.

## Invocation

Preferred portable invocation:

```text
$nestjs-feature-audit "payments"
$nestjs-feature-audit "payments" --branch "release/2026-q3"
```

If a host already routes the user's requested command syntax, parse it equivalently:

```text
/audit_feature payments
/audit_feature payments on branch release/2026-q3
```

Do not claim that bare `/audit_feature` is installed on every client. On Codex, the optional compatibility prompt is `/prompts:audit_feature`; installed skills remain the preferred interface.

## Required workflow

### 1. Prepare the target branch safely

1. Resolve the repository root and read its instructions before any Git mutation.
2. Record `git status --short --branch`, the current branch, remotes, and the local/remote existence of the target branch.
3. If the worktree is dirty, a Git operation is in progress, or the checkout is detached, stop before switching or updating. Never stash, discard, reset, clean, or force-switch automatically. Continue on the same dirty snapshot only when the user explicitly accepts it, and record that exception in the report.
4. When a remote-tracking branch exists, fetch its remote, switch normally, and fast-forward only. Never merge divergent history or rebase as part of an audit.
5. Record the audited branch, commit SHA, dirty state, remote revision, and whether freshness was verified. If a configured remote cannot be checked, stop before claiming the branch is current unless the user explicitly accepts the local snapshot.

Use equivalent safe commands for the repository:

```bash
git status --short --branch
git branch --show-current
git remote -v
git fetch --prune origin
git switch -- "$audit_branch"
git merge --ff-only -- "origin/$audit_branch"
git rev-parse HEAD
```

The explicit feature-audit invocation authorizes safe target-branch selection and fast-forward preparation. It does not authorize destructive cleanup or publication.

### 2. Gather context and enforce the roadmap gate

1. Read project principles, concepts, standards, architectural decisions, and contributor rules that apply to the feature.
2. Search `docs/` filenames and contents for the feature name, accepted aliases, `roadmap`, `plan`, `milestone`, `phase`, `acceptance`, and `migration`.
3. Identify feature code through entry points, modules, providers, adapters, persistence, configuration, migrations, tests, contracts, telemetry, and deployment artifacts. Search first; do not trust folder names alone.
4. Use requirements and decisions from available conversation context only as secondary evidence. If conversation history is unavailable, say so; do not fabricate it or block when the repository roadmap is sufficient.
5. Accept a roadmap only when it defines an identifiable feature scope and concrete target items, phases, acceptance conditions, or migration outcomes. A title, TODO mention, changelog entry, or generic product description is not a clear roadmap.

If no clear roadmap exists in `docs/`, stop before implementation comparison and ask the user to provide or identify it. Report the paths and terms searched. A roadmap supplied directly by the user satisfies the gate; label it as user-provided rather than repository documentation. Follow [roadmap-discovery.md](references/roadmap-discovery.md) for the complete gate.

### 3. Build the traceability matrix

For every roadmap item:

1. Normalize the requirement without weakening its acceptance language.
2. Trace it to source, tests, configuration, schema/migrations, generated contracts, deployment/runtime evidence, and relevant standards.
3. Record `verified`, `partial`, `absent`, `superseded`, `broken`, `blocked`, or `not verifiable` as the observed state.
4. Assign exactly one primary report category. Split a roadmap item into explicit sub-items when its parts have different states.
5. Keep a path-and-line citation or exact command/result for every positive and negative claim. Absence claims must include the searches and expected integration points checked.

Use [evidence-classification.md](references/evidence-classification.md) to distinguish completed work, gaps, legacy implementations, defects, blockers, and unverified candidates.

### 4. Cross-reference domain standards

- Compare architecture claims with actual module/import, dependency, data/write, transaction, and service boundaries.
- Compare object-design claims with real responsibilities, invariants, collaborators, and variation.
- Compare runtime claims with lifecycle wiring, security controls, tests, configuration, built artifacts, and authorized runtime evidence.
- Mark tests, deployments, migrations, external systems, or runtime checks as not verified when they were unavailable or unsafe. Do not convert `not run` into success or failure.
- Distinguish roadmap completion from production proof: merged source may be implemented while a rollout or live acceptance item remains blocked.

### 5. Return the required report

Start with the feature, branch, commit, dirty/freshness state, roadmap source, audited scope, and a one-sentence verdict. Then include these headings exactly and in this order:

1. **✅ Implemented**
2. **❌ Missing/Not Implemented**
3. **⚠️ Legacy Code**
4. **🛑 Bugs & Blockers**

Each item must name the roadmap requirement, observed state, evidence, impact, and next validation or exit evidence. Keep all four headings; write `None found in the audited evidence.` when a category is empty. Use [report-template.md](references/report-template.md).

Do not assign a completion percentage unless the roadmap defines item weights. Do not implement, commit, push, deploy, or edit the roadmap unless the user explicitly authorizes that specific action and scope. Authorization may be in the original request; implementation starts only after the audit, and fix authorization does not imply publication, deployment, or roadmap edits.

## Reference routing

| Need | Load |
| --- | --- |
| Decide whether documentation satisfies the hard roadmap gate | [roadmap-discovery.md](references/roadmap-discovery.md) |
| Classify evidence without double-counting or overstating completion | [evidence-classification.md](references/evidence-classification.md) |
| Produce the exact four-section final report | [report-template.md](references/report-template.md) |
