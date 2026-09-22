# Birdview contract v0.1

[中文](contract.zh.md)

## Multi-agent collaboration

Activity events may include `occurredAt` (an ISO 8601 timestamp), `gitCommit` (the source commit), and `collaboration: { agent, locks }`. `agent` identifies the worker and `locks` lists file paths or stable module IDs claimed for the active task. The validator warns when active claims from different agents overlap. A terminal event releases claims for that task, so completed collaboration state does not remain active. These are trace and conflict signals, not filesystem locks or merge replacements.

## Architecture

Optional module `role` classifies responsibility as `frontend`, `backend`,
`cache`, `database`, `queue`, `security`, or `generic`. Missing roles render as
`generic`, preserving older maps. Role determines the viewer's icon and color
family, independently of `kind` and group membership. Cache uses cyan with a
lightning icon; database uses violet with a database icon. Roles are not activity states.

New maps must pass `validate.mjs --authoring` (`requireRoles: true` in the API): every module declares `role`, and `generic` requires `roleAssessment: { basis, note }`. Use `basis: "out-of-taxonomy"` when inspected responsibilities fit no listed role, or `"insufficient-evidence"` when classification lacks evidence; the latter requires `status: "uncertain"` and a specific `openQuestions` entry. `note` explains the decision with reference to the module's evidence or missing inspection. Its translations belong in `roleAssessment.translations.<locale>.note`; `basis` is never translated. Assessments are only valid on explicit generic modules.

Default validation/rendering keeps legacy maps without roles or assessments valid. An all-generic/unclassified map returns `role/all-generic-review` in validator `warnings`, even if valid: review each module and explain the outcome at delivery. This warning is not a color-diversity requirement. Validation checks declarations, not the truth of classifications or the quality of explanations.

Optional `groups` represent authored system/subsystem membership, not deployment
or trust boundaries. Each has a unique `id`, `name`, nonempty source `evidence`
and unique module IDs in `members`. Groups are disjoint and one level deep.
Unknown members and duplicate memberships are rejected. Group translations cover
the name and evidence notes. The viewer arranges groups side by side, retaining
relative row/column order inside each group; ungrouped nodes remain unframed.

Optional group `role` assigns a fixed semantic color: `interaction` (pale blue,
user interaction/review), `runtime` (pale amber, execution/orchestration),
`external-services` (pale violet, integrations outside the described system), or
`generic` (neutral gray, unspecified grouping). Missing roles use `generic`.
Roles are authored from evidence, never inferred from order, names, or module
ownership. They do not assert deployment/trust boundaries or change activity.
The group heading displays the localized role alongside its name.

Optional `language` (such as `zh`, `en`, `ja`, `fr` or `pt-BR`) identifies the base
text language using a common language tag. Optional
`translations` on project, modules, relationships and evidence objects contains
localized text only. See `bilingual.md` for authoring and completeness validation.
Absent translations fall back to base fields; identities and layout are shared.

`schemaVersion` versions the file format. `mapId` identifies a map and `revision`
versions its contents. Together with `project.id`, these bind activity to the
intended system. Revision numbers are author-maintained; they are not a content
hash. Consumer-side hashing may be introduced with a real live transport.

`modules` describe responsibilities. `ownership` assigns exact files or directory
prefixes. `evidence` explains which source locations support the description.
One evidence citation does not imply ownership of that file. `relationships`
describe authored directed connections, not runtime impact analysis.

Paths use forward slashes and stay relative to the project root. Empty segments,
dot/parent segments, drive letters and `.git` segments are forbidden. A directory
rule such as `src/api` matches `src/api/products.ts`, not `src/api-other.ts`.
Multiple matching owners are allowed and must be represented explicitly.
External modules have no ownership and can use an empty evidence list; local
modules require ownership and evidence. Uncertain modules/relationships require
nonempty `openQuestions`.

The schema is strict about fields. Semantic validation additionally checks unique
IDs, existing relationship endpoints, distinct grid cells, evidence line order,
and the local/external and uncertainty rules. It does not read project source.

## Activity

Each JSONL line is a complete event. Its `scope` is the overall declared task
scope; `targets` is the current subset. `files` is the current step's concrete
file list. For `planned`/`editing`, every mapped owner must be in `targets`.
Unmapped paths must be reported exactly in `unmappedFiles` for every phase.

`checks` contains command, nullable exit code and `passed|failed|not-run` status.
Passed requires exit code 0, failed requires a nonzero exit code, and not-run
requires null. No checks means no verification claim. `completed` can describe
an untested change, but cannot include a failed check. A `failed` event may have
no checks when failure occurred before verification.

Session rules:

- The first event has sequence 1; following sequences are contiguous.
- A session belongs to one project and map revision.
- A new task begins with `planned`; only one task is active at a time.
- Active tasks accept `planned`, `editing`, `verifying`, or a terminal event.
- `planned` can revise scope. Every other event preserves the latest plan scope.
- Terminal phases are `completed`, `failed`, `cancelled`; task IDs cannot reopen.
- Targets must belong to scope. Terminal events may have empty targets.

These are authoring consistency rules, not enforcement of coding permissions.
The validator reports an error code and location; an invalid input is never
silently repaired. Neither contract defines HTTP endpoints, ports, UI colors or
an automatic interception mechanism.

## Visual contract

Optional local-constraint discovery, rule scope, applicability and per-event verification records follow [Effective constraints](constraints.md). They preserve legacy map/event compatibility and never establish automatic enforcement.

Every relationship requires `kind` and `visibility`. `kind` is `request` (invoke
an operation), `result` (return its outcome), `dependency` (use a capability or
resource), `event` (publish a notification/state record), or `control` (schedule,
approve, cancel or otherwise govern execution). These describe the authored arrow;
they do not prove synchronous execution or imply an unrecorded reverse edge.
`visibility` is `overview` or `detail`. Overview initially displays only
`overview` relationships; All displays every relationship. Missing fields and
the removed `primary` field are invalid; no legacy fallback is supported.
All modules keep their positions and stay
available. Hover temporarily reveals every direct relationship of that module,
including auxiliary ones, and dims unrelated context. The visible/total count
reflects this reveal. This is a reading aid, never an activity scope or new edge.

Render modules at stable grid positions; preserve them across activity updates.
Use a persistent outline for planned scope, highest emphasis for current targets,
and reduced emphasis for unrelated modules. Keep module names readable. Display
planned-event targets with the same emphasis before editing starts. Verification
targets must be identified as verification, not editing. Comparison panes share
positions and navigation, with activity emphasis only on the changes pane.
Display
reason and phase outside the map and reveal files/evidence on module selection.
Never imply that all neighbors of a target are being modified. Keep simulation
explicitly labelled and separate from real activity.
