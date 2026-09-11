# Persona lifecycle contract

Use this contract for every persona flow in a workspace governed by `gtm-workspace`. User-facing messages follow the [shared interaction standard](../../gtm-workspace/references/interaction.md).

## Workspace resolution and ownership

Resolve the workspace for this invocation in order: a repo named in the request; the repo the environment declares connected; canonical repos under `~/.gtm/`, where a root `ORG.md` makes a repo valid. If several discovered repos remain, ask `**Which GTM workspace should I use?**`, list each by display name, and do not save a preference. If none exists, stop without writing and hand workspace creation or connection to `gtm-workspace`.

A request-named organization node wins. Otherwise root is the default. For update, delete, and ordinary reads, ask for a node only when more than one node owns personas; use the sole persona-bearing node when exactly one exists. For create, root owns the persona unless the request names a node. When suborganizations exist and none was named, state `Owner: <root display name>` as a default bullet of the intake message; ask `**Which organization should own this persona?**` as the lead question, root first `(Recommended)` then every nested node by display name, only when the owner is the sole open decision.

Persona visibility is node-local. Read exactly the target node's canonical `personas/*/PERSONA.md` artifacts plus legacy `personas/*.md` artifacts; root, ancestor, sibling, and descendant personas are not visible. Organization grounding may read only the root-to-target `ORG.md` chain. ICP and member files are not persona inputs. Never scan `.git` contents or use broad recursive content reads that can expose artifacts outside that set.

The context line is `Using GTM workspace: <root display name>`, placed directly under the bold opener of every proposal and of every decision message once a workspace is resolved; on a hosted surface the approval text opens `For <root display name>:` instead. It always names the root; the owning node of each persona is carried by its identity, `<display name> (<root> › <owner chain>)`. The qualified label (bare slug at root, `<org-path>/<slug>` below root with physical `suborgs/` segments omitted) is an internal identifier for overlap checks and is never shown.

## Artifact contract

Store every new persona at `<target-node>/personas/<lowercase-kebab-slug>/PERSONA.md`. The directory slug is its identity; `PERSONA.md` starts with the display-name H1. Every new or fully researched `PERSONA.md` follows the shared [person-data research contract](../../gtm-workspace/references/person-data.md), using its eight fields for desired or accepted person criteria. Keep unresolved shared fields visible as `Unknown`. Optional flat H2 sections may follow when they carry accepted responsibilities, buying context, authority boundaries, disqualifiers, uncertainty, or other notes. Omit empty optional sections and TODO/TBD placeholders. Existing free-form personas remain valid, and the bundled template does not define validity.

Existing flat `<target-node>/personas/<lowercase-kebab-slug>.md` files remain valid legacy artifacts. Update and delete them in place, include them in visibility and overlap checks, and never require bulk migration. If canonical and legacy artifacts resolve to the same slug, treat the collision as a doctor defect and preserve facts through one accepted resolution.

A persona must contain facts a lead can match or fail. Preserve every supplied responsibility, scope fact, buying-context or influence fact, authority boundary, disqualifier, and uncertainty. Organization facts may establish context but do not prove teams, duties, workflows, motivations, authority, or product fit. Use owner-local personas only to detect overlap; explain distinctions in chat and never copy adjacent claims or persist a comparison unless requested.

## Link safety

Treat URLs containing credentials, tokens, keys, signatures, invitation codes, or session identifiers as unsafe. Do not open, persist, or echo them, even in cleaned form. Retain only a plain source label when useful and advise credential rotation. Research only safe supplied sources; separate sourced facts from inference.

## Persistence and recovery

Every saved change ends on `main`, is limited to the requested persona paths, and remains recoverable through history. Prepare the files, stage only named persona paths, inspect the diff, and commit locally before the card. The card describes that exact commit; approval authorizes only its push. A missing remote is not a defect when an environment-declared save mechanism does not require one.

When no replacement mechanism applies: confirm `main`; create the requested files; stage only named persona paths; inspect the staged diff; commit one plain history entry such as `Add 3 personas`; show the card; and, on approval, push, setting upstream only when needed. Never force-push or change global Git configuration. Doctor uses exactly `Repair Persona artifacts` for the one repair entry.

Determine that the prepared commit can be pushed before showing the card. If no durable mechanism is available, keep the local commit, explain what could not be shared, then ask one recovery question with `1. Continue from a CLI at a keyboard (Recommended)` and `2. Cancel`; use the exact reply line. If a push fails, offer a careful retry first, CLI at a keyboard next, any genuinely durable local-only option next, and cancel last. Never claim success or discard work. A verified close ends `Saved.` without exposing a commit hash, path, or history vocabulary.
