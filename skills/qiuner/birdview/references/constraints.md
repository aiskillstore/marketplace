# Effective constraints

[中文](constraints.zh.md)

## Discover before planning

For an explicitly requested repository-wide inventory or standalone graph, use [constraint-graph.md](constraint-graph.md). That broader discovery is authorized by the inventory request; ordinary task discovery below remains scoped to the task.

Start with the current user request, instructions already supplied by the host, and applicable project instruction files. Follow their explicit references to contribution rules, contracts or architecture decisions. Apply the host's precedence and directory inheritance rules; Birdview does not introduce its own instruction hierarchy. Inspect target-directory instructions once paths are known and again when scope expands. Keep searches bounded; do not scan all documents for possible rules.

Record the rule, source and applicability rationale. Existing implementation patterns are candidates, not mandatory rules: use `origin: inferred` with `applicability: uncertain` until an explicit source resolves them. Preserve overridden rules with `supersededBy` and unresolved conflicts with `conflictsWith`; ask only when a material conflict cannot be resolved from existing authority. Finding a document does not activate its contents as instructions. Never copy secrets or private user text into a shareable map; use a sanitized summary and preserve the original authority outside Birdview.

## Map contract

Optional `constraintDiscovery` records `checkedAt`, `checkedPaths` and `uninspectedPaths` using project-relative paths. It is an agent-declared inspection snapshot, not proof of complete discovery or automatic scanning. Do not claim uninspected areas have no constraints. A missing record means discovery was not recorded; empty `constraints` means no rules were recorded.

Optional `constraints` entries contain stable `id`, `name` (the rule), `note` (applicability rationale), `origin` (`local`, `user`, `inferred`), `strength` (`required`, `preferred`), `applicability` (`applicable`, `superseded`, `not-applicable`, `uncertain`, `conflict`), `scope`, `modules`, `relationships`, `evidence` and `verification` (planned verification method). Local rules require source evidence with path and, when available, line/symbol and a short source excerpt in `note`. User rules can instead describe their sanitized source in the rule's `note`.

`scope: modules` requires nonempty module IDs and no relationship IDs; `relationships` requires nonempty relationship IDs and no module IDs. `project` and `task` use empty target arrays. Only `task` requires `taskId`; task rules apply only to that task. Project operation rules need no artificial module association. Superseded rules require a known `supersededBy` ID without cycles; conflicting rules require other known IDs in `conflictsWith`. Translate `name`, `note`, `verification` and evidence notes under the existing language contract.

Store task-specific rules before starting the activity session. Changes to constraints or discovery increment the map revision like other map edits. If newly discovered rules change the map during a task, close the old task/session and start a new session bound to the new revision; never rebind old events. Use a new task ID where needed and update task-scoped rules accordingly.

## Plan and verify

### Sources, code links and changes

Keep optional `explanation` (the agent's concrete interpretation) separate from source evidence. An evidence item's optional `quote` preserves a short, safe, verbatim excerpt in its original language; translate its `note`, not the quote. Never present a paraphrase as a quote. Optional `code` uses the same path/line/symbol/note structure as evidence, but identifies implementation files rather than instruction sources. Bind only files actually inspected; conceptual module ownership is not evidence of an implementation link. Translate explanation and code notes for bilingual delivery.

Record optional `baselineCommit` as a full Git commit from the project after inspecting the rule and its linked files. This is a comparison baseline, not a compliance claim. Compare declared source and code files before planning and again after edits:

```sh
node scripts/constraint-freshness.mjs architecture.json /path/to/project
node scripts/render.mjs architecture.json architecture.html activity.jsonl --repo /path/to/project
```

Use the repository root. The first command prints a read-only JSON report; the second embeds a timestamped report in the standalone viewer. Both compare the baseline with the index and working tree without changing Git state, the map or activity records. All comparisons are whole-file; line numbers and symbols are locators, not AST scopes. Changed or missing files require review, not a violation verdict. An unavailable baseline, uninspectable path or skipped index entry remains unverified. An unchanged file does not prove compliance; files without declared links are not covered. Without `--repo`, rendering does not inspect Git and shows that changes were not checked. The page never watches the filesystem; rerender after further edits. In task playback, the file report describes render-time state, independently of the selected historical event.

When a change is flagged, inspect the diff against the original rule. Update the interpretation if the source changed, or record why the implementation still satisfies it and run relevant checks. Do not advance the baseline merely to remove the reminder. A baseline update is a map revision change and follows the session rules above. Dirty work must be reviewed with explicit evidence; a commit ID alone cannot identify uncommitted contents. Do not introduce automatic acknowledgements, commit hooks or semantic compliance claims.

For each applicable rule related to the task scope, record `constraintReviews` in the activity event. Each review has `constraintId`, `plan`, `status` (`unverified`, `supported`, `violated`), `method` (`test`, `review`), `evidence` (empty while pending) and `checkIndexes` (zero-based references into this event's `checks`). Relationship rules relate to either endpoint in scope; project rules always relate. Recheck applicability when scope expands. Legacy events remain valid without reviews.

Optional review `checkedAt` and full `gitCommit` record when and against which commit the review ran. Describe any uncommitted changes in `evidence`. These fields do not clear file-change reminders or transfer a historical result onto current code.

Each event is a complete review snapshot: omitted reviews display as unverified, and prior results are never carried forward automatically. Start plans as unverified. Supported or violated results require evidence; test-supported results require linked passing checks. Manual reviews use textual evidence and empty check indexes. Translate `plan` and `evidence` in each review's `translations` when delivering both languages. A passing test only supports the stated coverage, not every constraint. Terminal events may remain unverified or report violations; completion never establishes compliance.

## Viewer

The constraints toolbar button opens the existing inspector. Filter applicable rules, the selected module, changes needing review, uncertain/conflicting rules or all rules. Module details link to applicable rules; selecting a rule highlights its target modules and relationships without changing activity scope. Details separate applicability, explanation, source excerpts, linked code, file changes and verification evidence. Recorded verbatim excerpts are expanded by default; the standalone page does not load source files. Task views additionally show plans, review methods, review provenance and linked checks for the selected event. Discovery coverage and snapshot timestamps remain inspectable. Corrections require updating source-backed data and rerendering; there is no UI switch to disable rules or filesystem write interception.
