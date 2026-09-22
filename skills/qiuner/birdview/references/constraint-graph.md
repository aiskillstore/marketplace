# Constraint graphs

[中文](constraint-graph.zh.md)

Use this route for a standalone constraint graph, a repository-wide inventory or the constraint portion of the default integrated delivery. Preserve the architecture viewer. All commands below are relative to the installed skill, not the target repository; Node.js and Git are required. Run `npm ci` in the installed skill directory once as described in the installation guide; no frontend build is needed to run these commands.

## Discover the declared scope

```sh
node scripts/discover-constraints.mjs /path/to/repository /output/constraints.catalog.json "Project name"
node scripts/render-constraints.mjs /output/constraints.catalog.json /output/sources.html --sources
node scripts/compile-constraint-rules.mjs /output/constraints.catalog.json /output/reviewed-rules.json /output/constraints.reviewed.json
node scripts/render-constraints.mjs /output/constraints.reviewed.json /output/constraints.html
```

The collector reads committed HEAD without modifying the repository. It enumerates tracked AGENTS.md, CLAUDE.md, GEMINI.md, SKILL.md, root CONTRIBUTING.md, GitHub Copilot instructions and Cursor rules, then follows local Markdown links and quoted Markdown paths recursively. It preserves source text, heading hierarchy, line ranges and file history. It excludes recognized fixtures, archives and duplicate Chinese translations, retaining reasons. References indicate discovery, not authority or automatic activation. A skill is conditional on its task; a directory instruction applies only under the host's inheritance rules. Implemented decision notes remain reference evidence, not automatically current rules.

Inspect `coverage.entries`, `excluded`, `unresolved`, `uninspectedPaths` and `limitations`. Resolve material missing references or explicitly preserve the gap. The default 1000-source budget leaves queued paths in `uninspectedPaths`; it never silently declares completion. Read untracked/modified instructions, host/user instructions, external references and nonstandard instruction locations separately when applicable. Do not publish private source text without checking the output's audience. Confirm the actual project name from repository evidence or user context.

The output is a **source inventory**, not an automatic semantic audit. Sections may contain multiple rules or explanatory prose. Do not describe the number of nodes/sections as the number of effective constraints. Completeness is relative to a named revision, declared entry conventions and resolved references, never the entire lifetime of a project.

## Review rules

Read every included instruction/skill and relevant referenced section for the requested scope. Split independent obligations into stable rule IDs; retain exact provenance, applicability conditions, overrides and unresolved conflicts. Cross-links and similar wording do not prove identical authority. Do not discard a source because it was not in the initial examples. Keep excluded fixture instructions and historical notes out of effective rules.

The default graph requires reviewed `rules` and `ruleReview.scope`; it rejects an unreviewed source catalog. Source collection alone is not a completed human-facing constraint graph. Each rule must answer what to do, when it applies, why it matters and how to check it. Keep source text in details. Deduplicate obligations without losing conditions or provenance; do not infer applicable rules from headings alone.

Author `reviewed-rules.json` with the same `revision`, an honest `scope`, and `groups`. Each group has `sourcePath`, `category`, optional `topic: {id, name}`, and `rules`. Each authored rule has a stable `id`, short `name`, a unique verbatim `anchor` from its source, `explanation`, `condition`, `verification` and optional `applicability`. The compiler resolves the anchor to a paragraph/list item and extracts real line ranges, rejecting absent/ambiguous anchors and snapshot mismatches. It does not perform semantic review. The DeepSeek example at `examples/deepseek-constraints.rules.json` illustrates the format; its project-specific rules must not be copied into other projects.

The resulting catalog's required `rules` entries look like:

```json
{
  "id": "rule-model-visible-log",
  "category": "interfaces",
  "sourcePath": "AGENTS.md",
  "line": 111,
  "endLine": 111,
  "name": "Log model-visible inputs",
  "explanation": "New input sent to a model needs a durable session event.",
  "condition": "When introducing model-visible input",
  "applicability": "conditional",
  "verification": "Inspect the event and replay path; run the relevant replay test."
}
```

Line numbers here are illustrative: inspect the target snapshot. Supported applicability values are `applicable`, `conditional`, `superseded`, `conflict`, `uncertain`. Explain any supersession/conflict in `explanation`. The renderer extracts the quote from that source; it does not invent quotations. Keep `coverage.semanticReview: pending` until review covers the declared scope; record remaining review gaps in limitations and `ruleReview.scope`. Partial reviewed scope is deliverable only when clearly labeled; never call it the complete effective rule set. To use rules during architecture/change work, map reviewed rules into the existing [constraints contract](constraints.md), retaining source evidence and applicability rather than copying graph categories into module ownership.

## History and verification

Keep three identities separate: stable `rule.id` (the displayed R-number is only a presentation ordinal), rule source-history `vN`, and the full project snapshot commit. To populate history, pass the repository as the fourth compiler argument:

```sh
node scripts/compile-constraint-rules.mjs catalog.json reviewed-rules.json versioned.json /path/to/repository
node scripts/render-constraints.mjs versioned.json constraints.html
```

The compiler checks source text against the fixed snapshot and runs Git line history for each quoted paragraph/list item. It records `history` with `status: tracked`, `method: git-line-history`, `snapshot`, `sourcePath`, `line`, `endLine`, `version`, `lastEdited`, and the actual `commits` array of `{commit,date}`. This is the count of source-range history entries, not semantic releases or revisions of the agent's explanation. Moving/reformatting text or sharing one paragraph between obligations can affect the count. Do not manually manufacture these fields or substitute the whole-file history. Rendering validates provenance consistency, not the truth of authored Git evidence; use the collector. Existing source history is discarded when recompiling author input to prevent stale reuse.

Cards show the R-number, `vN` and role; details include the method and full commit evidence, while the legend shows the project snapshot. Missing history, shallow clones or unavailable line history show “版本未追踪” rather than v1. Collection never fetches history automatically. The renderer rejects tracked history belonging to another snapshot or source range. Group nodes have no invented versions. When using another AI, require the reviewed selection, versioned catalog and rendered HTML together so provenance remains reviewable.

On source-file nodes, vN is the number of Git history entries for that **file's current path**, not a rule's semantic version; rename ancestry is not followed. Dates also belong to the file. Shallow history suppresses version counts and is disclosed; never silently fetch or present a shallow count as complete. Raw sections have no invented individual versions. Unknown compliance stays pending even when the source is committed.

Code drift requires inspected implementation links and a justified baseline. Use `constraint-freshness.mjs` with the architecture contract for file changes. Do not infer ownership from headings, treat all later commits as violations, or manufacture colorful status badges. The historical six-rule DeepSeek prototype uses a different, explicitly limited line-history heuristic; it is not the general scanner and must not supply global compliance statistics. Checks and code-review evidence belong in `constraintReviews`, separately from source age and applicability.

## Integrate into an architecture page

Keep the architecture page's original horizontal toolbar and canvas layout. The native constraint view has a rule directory, tree canvas and on-demand reading panel; no application icon rail, bottom status bar or iframe. Do not add a module-directory sidebar to the architecture page.


When the user requests a combined page, reuse the existing architecture JSON and render both views:

```sh
node scripts/render.mjs architecture.json project.html --constraints versioned.json
```

Activity JSONL and `--repo` remain optional. The CLI writes `project.html` and the auxiliary `project.sources.html`; distribute both together. Without `--constraints`, existing architecture output is unchanged. The renderer API accepts `constraintCatalog` and optional `constraintSourceHref` in its third argument; API callers generate the auxiliary source index themselves.

Both views retain their canvas state when switching. The header keeps the project name, language controls and shared light/dark theme; role colors keep the same meaning. Architecture revision and constraint snapshot are distinct identities. Controls use the host language; authored rules and source quotations stay in their original language. The source index is an auxiliary page, not a second main graph.

Project names must match. Optional module links require an explicit catalog `architectureBinding: {mapId, mapRevision, sourceRevision}` matching the map and the full catalog commit, plus `modules: ["module-id"]` on reviewed rules. Carry this binding in the reviewed selection when compiling; recompilation discards old catalog bindings. Inspect source evidence before authoring links. The renderer rejects stale bindings and unknown module IDs. Role similarity is never a module link. Without bindings, the full graph still works and module details say no links are recorded. With bindings, the module button opens only linked rules and their ancestors; “Show all rules” restores the full graph. Changing this filter initializes a new constraint layout; switching architecture/constraints alone preserves it. Versions and verification evidence remain unchanged by filtering.

Check both views, switching without state loss, theme changes, Chinese/English navigation, narrow screens, module filters and the source-index link. Keep the original architecture layout intact. A conceptual demo map must still be described as conceptual even if its accompanying constraints come from real source history.

## Render and deliver

`render-constraints.mjs` consumes `birdview.constraint-catalog/v1` and defaults to a **rule graph**: project → category → optional human-named topic → rule. The six categories are `lifecycle`, `interfaces`, `configuration`, `security`, `testing`, `delivery`. Topics use numbers and text. Colors share architecture role semantics: frontend blue, backend teal, cache cyan, database violet, queue amber, security rose, generic slate. Rules may declare targetRole; non-generic roles require a source-grounded roleReason. Cross-role or unclear scope stays generic; never infer role from topic name. Homogeneous groups inherit their role color; mixed groups use generic. The toolbar role legend counts rules, and cards carry textual IDs and role names. Applicability and verification remain separate in details; colors never mean pass or fail. Prefer concise, actionable titles. Cards clamp long titles to two lines while tooltips and the reading panel retain the full title. Use topic groups to keep each expanded level readable, usually no more than eight children. File age/version and collection counts do not occupy rule cards. Do not show thousands of uniformly pending source nodes as the main view.

The renderer uses Birdview-owned HTML cards, SVG connectors and subtree layout, without a third-party graph runtime. `constraint-canvas.js` mounts the same component in standalone and integrated pages. `constraint-page.html` supplies the standalone shell; `constraint-canvas.css` scopes styles to the constraint view. `buildConstraintGraph()` prepares a `birdview.constraint-view/v1` presentation payload without changing the input catalog contract. Details lead with applicability, explanation and verification plan, then source evidence and rule history. Documents render as safe text with basic headings and quotes; arbitrary HTML and embedded diagrams are not executed. All collected sources, including unreviewed skills and references, appear in By directory; double-click a source to read its text and review status. Coverage remains under Coverage. The toolbar does not navigate to another page. The CLI retains the sibling `.sources.html` export for compatibility; `--sources` renders only that auxiliary export.

Open the HTML and check expansion, source reading, long content and coverage disclosures at desktop and narrow widths. Report actual collection counts, unresolved/excluded areas, semantic-review status and tests run. Source collection can be complete while effective-rule review remains incomplete; state those separately. The page is offline and read-only, not a live monitor or enforcement mechanism. Generated native pages include the Birdview license; preserve licenses for dependencies actually distributed.


Directory and canvas share expansion and selection. Search matches rule titles, explanations and source text while preserving ancestor paths. More than 100 matches show only the first 100 with an explicit message, keeping a large source inventory off the main canvas. Support drag-to-pan, Ctrl/Command + scroll zoom, pinch zoom, zoom buttons and fit. With canvas focus, arrows pan, plus/minus zoom and 0 fits; cards support Enter and left/right navigation, while Escape closes overlays. On narrow screens the directory starts closed and closes after selection; details use a drawer. Expansion, search and zoom never change rule history or verification state.

## Directory and topic views

The reviewed graph offers By topic and By directory over the same rule IDs, versions and documents. Discover root and nested instruction files before grouping. Directory nodes list local sources and ancestor instruction candidates using recorded source scope; storage paths alone never prove applicability, override, or conflict resolution. Skills and references require invocation/reference review. Include collected instruction files without extracted rules and explicitly mark extraction gaps. Directory placement is source provenance, not module ownership. Preserve module filters when switching views. Node double-click or Shift+Enter opens the shared detail dialog.
