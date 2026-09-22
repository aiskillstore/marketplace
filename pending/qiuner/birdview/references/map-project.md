# Stage 1: Map the project

[中文](map-project.zh.md)

Produce [schema-valid](../schemas/architecture.schema.json) architecture JSON and standalone HTML from the same data for the selected project and scope. Follow [language selection](bilingual.md); examples are fictional field references, not project evidence.

## Discover and verify coverage

1. Check user-provided/documented architecture paths, existing artifact locations, `.birdview/`, then root and `docs/`. Use bounded architecture/map filename searches, excluding dependencies, generated output and skill examples; expand only when those locations and references yield nothing.
2. Read candidates and verify project relevance, coverage, current ownership and source evidence. Validate Birdview JSON; schema validity does not establish freshness. Prefer the user's selection or documented canonical map; ask only about unresolved competing candidates.
3. Reuse compatible maps in place and update stale portions. Adapt other formats after source verification, preserving meaningful IDs and the original artifact. HTML/images alone need underlying module/ownership data before Stage 2. Create a map only when none is reusable or adaptable; resolve unavailable validation before Stage 2.
4. Honor explicit subsystem scope; otherwise inspect the selected project root. Read root documentation, top-level directories and relevant workspace/build manifests, then follow declared applications. Verify each using its own manifest, startup/build entry and source. Dependencies alone do not prove an application; trace client calls and server routes before asserting connections.
5. Reconcile every in-scope application with a module, explained grouping or explicit coverage gap in new and reused maps. Keep distinct application responsibilities visible; shared packages need not be applications. The 6-10 module readability target never justifies omissions or inventions.
6. For ordinary local edits, recheck relevant entries and changed manifests. Broaden discovery only when scope or workspace structure changes. Report root/scope, checked applications and module IDs, exclusions and unresolved areas alongside the architecture table. Distinguish uninspected areas from checked absences; zero uncertainty does not prove complete coverage.

## Author the map

Trace main request/data paths and read surrounding symbols before assigning responsibilities. For a specific code area, step up to its responsibility and relevant callers/dependencies within the agreed scope. Stop when that scope is coherently covered.

Model modules as cohesive business or technical responsibilities at a comparable level of abstraction, not one node per file, class or directory. Describe what each does and how it connects to surrounding modules; keep implementation locations in ownership/evidence. Use the project's domain glossary when available, otherwise established terms from source and documentation. Preserve evidenced responsibility boundaries and existing IDs when improving labels.

Follow the [contract](contract.md) for fields, roles, ownership, evidence, status and layout. Choose module roles from inspected responsibilities; use `generic` when unclear, never cycle roles for colors. Roles are independent of ownership and groups. Include external services only for real relationships, without local file ownership. Mark unsupported conclusions `uncertain` with specific open questions; `supported` records inspected evidence, not static proof.

For new maps, explicitly classify every module and run `node <skill-root>/scripts/validate.mjs <map.json> --authoring` before rendering (add `--bilingual` for Chinese/English delivery). Generic modules require the contract's `roleAssessment`: explain why the taxonomy does not fit or which evidence is missing; insufficient evidence requires uncertainty and a specific question. Never bulk-default modules to generic to finish faster. Review all-generic warnings module by module against source and report the reasons, rather than inventing different roles to pass. Reuse existing classifications unless new evidence supports a change; explain any downgrade to generic and apply revision rules. Review changed/new module classifications on legacy-map updates; unchanged legacy fields need no forced migration.

Author directed, concretely labelled relationships with evidence, status, `kind` and `visibility`. Keep core execution, necessary result/tool feedback, basic dependencies and required approvals in `overview`; recovery, retries and diagnostics may be `detail` unless central to the map. Default to `overview` when unsure. Check isolated overview modules for missing connections; keep genuine auxiliary modules and hidden-relation counts. Retain all relationships; kind/visibility do not represent modification scope, and must not change solely to reduce visual clutter.

Show an architecture table (module, responsibility, ownership, evidence, uncertainty) and short relationship list from the same JSON. Allow corrections without redundant approval when continued work is already authorized.

## Groups and revisions

Use optional groups only for evidenced system/subsystem membership: one disjoint level, with stable IDs, names, unique members and nonempty evidence. Groups render side by side, preserving internal row/column order; ungrouped modules remain outside frames. Translate group names and evidence like module text.

Choose group roles from source-supported responsibilities and explain the classification in evidence notes:

| Role | Meaning | Fixed color |
| --- | --- | --- |
| `interaction` | User interaction and review | Pale blue |
| `runtime` | Execution and orchestration | Pale amber |
| `external-services` | Integrations outside the described system | Pale violet |
| `generic` | Unspecified or mixed responsibility | Neutral gray |

Unclear or omitted roles use `generic`. Names, ordering, module ownership and color variety are not classification evidence. Group roles do not imply module roles, deployment/trust boundaries or activity state. Keep the shared palette; no per-map overrides or custom color fields. Schema rejects unknown roles/fields but cannot verify classification; check evidence and preserve existing roles unless new evidence warrants change.

Read existing artifacts before replacing them; use the agreed location (default `.birdview/`) without overwriting unrelated files. `project.id` and `mapId` are local identities, not necessarily URLs. Optional `project.revision` records a Git commit, not the map revision or a clean-tree guarantee.

Increment `revision` for every saved map change, including layout and translations. Preserve IDs for continuing responsibilities and never reassign removed IDs. Complete/cancel tasks on the old map before starting against a new revision; never silently replay old events onto it.

## Render and review

For the default “use Birdview” delivery, finish the [constraint workflow](constraint-graph.md) before final rendering: inspect effective local instructions, collect committed sources, author and review `reviewed-rules.json`, then compile with the repository argument to collect rule history into `.birdview/constraints.reviewed.json`. Preserve working-tree instruction differences as explicit limitations. Record actual checked/uninspected paths in `map.constraintDiscovery` under the [constraints contract](constraints.md); a scan is not semantic review. Do not copy the demo rules. Reuse a matching reviewed catalog when valid. Keep scope and snapshot explicit, and only bind rules to modules after source inspection. Save the source catalog and reviewed selection alongside the compiled catalog so another AI can continue the review. If review is incomplete, report that boundary instead of claiming complete delivery. When no reviewed rules exist, deliver the architecture and discovery findings with the limitation; the rule renderer deliberately rejects an empty or unreviewed catalog.

Use the bundled renderer, with absolute paths when running from the user's project; `<skill-root>` contains SKILL.md. Substitute the actual agreed artifact paths:

```sh
node <skill-root>/scripts/render.mjs <project-root>/.birdview/architecture.json <project-root>/.birdview/architecture.html --constraints <project-root>/.birdview/constraints.reviewed.json
```

Omit `--constraints` only for an explicit architecture-only request or a disclosed unavailable rule catalog. Check that the final page has Architecture / Constraints switching, source evidence, rule version labels and the sibling source-index link; deliver the `.sources.html` file with it. The architecture inspector counts only map-bound rules, not the separate catalog; missing module links are not missing project rules.

The renderer validates JSON and emits self-contained HTML requiring no server/network assets. Do not handcraft a substitute viewer or deliver a fictional demo as the project's map.

Open HTML in a visible browser preview. With Codex `open_in_codex`, use a `browser` target and correctly encoded file URL, not a `file` target. A Markdown link may open source; a queued request does not confirm display, and headless inspection does not confirm the user's visible tab.

Review the final HTML at the available user viewport:

- Inspect Overview and All relations, names, relationships and selected-module evidence. Hover the module with most direct edges (incoming + outgoing, self-edge once), then other visibly congested areas.
- Check card-crossing/overlapping routes, congested turns, distinguishable endpoints/arrows, cropped routes/headings, hidden-relation counts and text size after fitting.
- Verify hover makes direct relationships traceable and leaving restores the selected view without moving nodes.

Automatic spacing is not a readability guarantee. Keep pixel thresholds and invented congestion fields out of map data. If needed, adjust layout by responsibility/interaction order or groups by evidence; preserve identities, ownership, relationship semantics and full scope. Increment revision, rerender, and recheck affected areas and the full view. Stop after two consecutive attempts without visible improvement and report remaining issues. Unchanged maps in focused tasks need no unrelated UI audit.

Report the actual artifact, viewport, modes, focused modules and unresolved issues. Schema checks, collision samples or screenshots alone are not visual acceptance; no automated crowding check is bundled. If browser inspection is unavailable/denied, state that visual review was not performed and the actual limitation; provide the absolute HTML path, explaining browser display versus editor source. Do not bypass denial or blame the template without rendering-error evidence.

Lead with HTML and the preview result; include JSON path, `project.id`, `mapId`, `revision`, coverage and uncertainties as supporting information. Fix or report rendering blockers; JSON alone is not completed visual delivery. This is a snapshot, not live activity. Without a coding task, stop after delivery and ask for the intended change. With a coding task, prepare and render its scope through [Stage 2](show-changes.md), then wait for confirmation of the displayed plan before implementation. Rendering success alone is not permission to edit.
