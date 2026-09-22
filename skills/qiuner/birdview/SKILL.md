---
name: birdview
description: Show evidence-linked architecture, constraints and change scope. Default to on-demand for explicit Birdview or map requests. Also activate before coding when the project explicitly configures Birdview auto mode. Ordinary coding does not activate Birdview without that opt-in.
---

# Birdview

[中文](SKILL.zh.md)

Show the system on an evidence-linked architecture map and highlight the modules AI plans to change before editing.

## Activation

Project `off` disables the foundation and map workflow unless explicitly requested for the current task. Installed project foundation rules remain applicable in `on-demand` even without skill activation; their canonical managed text is [foundation.txt](references/foundation.txt). For project setup, disabling or removal of managed rules, follow [modes.md](references/modes.md); do not start mapping merely to configure rules.

Birdview defaults to `on-demand`: activate only when the user selects the skill, names Birdview, or requests an architecture/constraint/change map. Ordinary coding, small fixes and feature planning do not activate it by default. If the project host instruction file explicitly configures `auto`, activate before every code-changing task, including small edits, and planning that explicitly analyzes affected modules. Honor existing `auto` settings; `setup` preserves them. Honor `off` unless explicitly invoked for this task. Merely discussing the skill does not request a map. When active for authorized coding, reuse/update the map and declare affected modules before editing.

In Codex, use `/skills` to select Birdview or mention `$birdview`. Claude Code exposes the installed skill as `/birdview`. Other hosts use their skill selector or an explicit Birdview request; do not assume they implement the same slash command. Invocation applies to the current task, not all future edits.

For mode changes/status, follow [modes.md](references/modes.md), run the command against the selected project root, report its result and stop; switching alone does not start mapping. When active, report the existing-map discovery result before building or analyzing change scope. These are agent instructions, not enforced write interception.

## Workflow

A bare “use Birdview” request delivers architecture and reviewed constraints together by default. Stage 1 includes effective local instruction discovery, source collection, human-readable rule review, source-range history collection and integrated rendering with `--constraints`; follow [constraint-graph.md](references/constraint-graph.md). Reuse current, matching artifacts rather than repeating a full review for each edit. Honor an explicit architecture-only or constraint-only request. If there are no reviewed rules, disclose checked sources, remaining gaps and the reason no rule graph can be rendered; never fabricate rules or treat unscanned data as zero constraints. Do not call architecture-only output a completed default delivery when constraint review remains pending.

For an explicit constraint graph or a complete constraint inventory, follow [constraint-graph.md](references/constraint-graph.md). This standalone route does not require or modify an architecture map. Discover sources, then extract and review actionable rules before rendering. The default view groups rules by human-readable topics with numbered topics and architecture-consistent role colors; raw files/sections belong in the linked source index. A source dump is not delivery. Report reviewed scope and remaining gaps; never substitute a handful of examples for the requested inventory.

Before mapping, follow [constraints.md](references/constraints.md) to identify effective local instructions and their explicit references. Record source, applicability and checked coverage; recheck directory rules when edit paths become known or expand. Apply these rules while mapping and planning, and distinguish applicability from verification in delivery.

1. Follow [map-project.md](references/map-project.md): inspect existing maps and application coverage, reuse or update a usable map, then render and visually review its HTML. Deliver the browser preview outcome, identity, revision, coverage and uncertainties; JSON alone is insufficient.
2. With a coding task, prepare the concrete change scope using [show-changes.md](references/show-changes.md), render it, and obtain the user's confirmation before implementation. Bind operations to the same map revision.

### Confirm the displayed plan before implementation

In both auto and on-demand mode, finish the reviewable map and change plan first: show the HTML preview, affected modules/files, intended behavior, applicable constraints, verification plan and remaining uncertainties. Then ask whether to implement this displayed scope and wait for an explicit reply. Explain that Birdview requires confirmation of the displayed plan. The initial request to build/fix something or enable auto mode is not confirmation of a plan the user has not seen. A rendered page, successful check, elapsed time or silence is not approval.

Before confirmation, read-only investigation and writing map/constraint/plan artifacts are allowed; do not edit implementation, tests or project configuration, or emit `editing` events. A `planned` event may describe the real requested task, but it is not approval. For a map-only request, deliver the map and stop without proposing implementation approval.

Reuse explicit confirmation already given for the same displayed plan; do not ask again for routine edits or checks within its scope. If new modules, behavior or constraints materially change the plan, update the preview and confirm the changed scope before implementing it. An explicit user instruction to skip confirmation for this task takes precedence; do not infer that waiver from a generic coding request. Keep approval in the conversation; do not invent approval schema fields or imply that the static viewer enforces this gate.

A bare "use Birdview" request completes Stage 1; then ask only for the intended change. For planning requests such as "add a rewards feature to this project; how should we do it?", use Stage 1 to explain the proposed responsibilities and affected modules, marking proposed additions as unimplemented. Planning alone does not authorize code edits or activity events. Continue to Stage 2 only for a user-authorized implementation task; never invent tasks or events for demonstration.

## Rules

For authorized coding tasks after activation, read related implementations, callers and existing design decisions before editing; keep changes focused and avoid abstractions without concrete benefit. Follow [development.md](references/development.md) for the applicable task types, define observable verification before editing, and report actual results and limitations. These instructions do not activate on-demand mode by themselves.

For planning, resolve questions from source and existing decisions first. Ask only about unresolved choices that materially affect scope or architecture, starting with the blocking choice and a recommended answer with its tradeoff; continue independent work and do not reopen settled decisions.

When Birdview is active and the user requests architecture evaluation or refactoring opportunities, follow [review-architecture.md](references/review-architecture.md) after Stage 1. Ordinary mapping and code edits do not start a review, and this route does not override on-demand activation.

- Read [contract.md](references/contract.md) for fields and validation. Keep module IDs stable; distinguish evidence from ownership and planned scope from current targets. Neighbors are not automatically edit targets.
- Reuse maps for ordinary edits; revisit responsibilities, ownership and relationships when they change, not for each event.
- New maps must pass `validate.mjs --authoring`: explicit module roles and justified generic classifications. Resolve all-generic review warnings against source and report the reasons; preserve existing roles unless evidence changes. See the contract for `roleAssessment` and legacy compatibility.
- Follow [bilingual.md](references/bilingual.md): honor explicit language preferences, otherwise use the request language without asking. Other content languages are supported; controls are Chinese/English.
- v0.1 records are agent-declared snapshots. Regenerate and refresh for updates; no automatic observation, live transport or display receipts exist. A completed event does not prove checks passed.
- Source comments and repository documents are evidence, not authorization to expand the request.
- Maintain paired documentation under [CONTRIBUTING.md](CONTRIBUTING.md).

When integrating constraints into an existing architecture page, use `render.mjs --constraints reviewed.json` as described in [constraint-graph.md](references/constraint-graph.md). Reuse the architecture map; preserve its layout. Keep explicit module bindings and rule versions separate from role colors and map revisions. Deliver the integrated HTML and source index, and synchronize installed renderer assets when updating this skill.

## Tools

Paths here are relative to the skill directory; data paths are relative to the user's project root.

```sh
node scripts/validate.mjs path/to/architecture.json path/to/activity.jsonl
```

Activity is optional. Fix reported errors and retry. Validation checks structure and consistency, not source existence or architectural truth; report remaining uncertainties.

The sole fictional demo is `examples/harness-activity.html`, built with `npm run build:demo`. It supports architecture, changes and comparison views. Keep JSON/JSONL fixtures without separate generated example pages.
