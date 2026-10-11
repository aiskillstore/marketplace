---
name: astrale-cli
description: Reference for the Astrale CLI (binary `astrale`, package `@astrale-os/cli`) - setup, graph reads and mutations, kernel calls, instances, domains, identities, delegation, journals, views, output, debugging, and local storage.
---

# Astrale CLI

`astrale` connects to existing Astrale Kernels. It selects an instance and
identity, performs graph reads and mutations, invokes callables, installs
running domains, reads the Kernel journal, and opens authenticated views.

The rendered command help is authoritative for flags and defaults:

```bash
astrale --help
astrale <command> --help
```

- Binary: `astrale`
- Package: `@astrale-os/cli`
- Runtime: Node 22 or newer; source development defaults to Node 26 and also supports Node 24 and Bun
- Dev entrypoint: `bun cli/bin/astrale.ts <command>`

## Command Surface

Primary commands:

```bash
astrale status
astrale whoami
astrale use <name>
astrale get <target>
astrale query [sources...]
astrale introspect <origin-or-path>
astrale mutate
astrale call <path> [key=value...]
astrale token
astrale logs
astrale view [domain-or-view]
astrale ui ...
astrale instance ...
astrale domain ...
astrale identity ...
astrale auth ...
astrale idp ...
astrale admin ...
astrale issue "Title" --body "Context and details"
```

Kernel-touching commands share `--format`, `--json`, `--raw`, `--url`,
`-i/--instance`, `--timeout`, `--as`, `--creds`, `--anonymous`, and `--debug` where
applicable. The CLI creates one public Kernel `Call`, and its Client session owns
remote routing, fresh credentials, and one safe stale-route retry.

`astrale ui` is local project tooling and takes no Kernel, instance, identity,
or credential options, except `astrale ui request`, which is an authenticated
Kernel command and takes the shared Kernel options.

Use `--anonymous` to omit a caller credential even when a local or bookmark-default identity exists.
It cannot be combined with `--as` or `--creds`; required callables reject anonymous requests.

## Report an issue

Use `astrale issue "Factual title" --body "Context and details"` (or pipe the body
on stdin). Prefer optional `--project <directory>` and `-i <instance>` when known;
do not ask for missing context just to fill these options. Available local versions are
attached automatically. `-i` names the affected instance.
Optionally add `Type: bug`, `Type: limitation` (including capability requests), or `Type: friction`.
Keep the body brief: **Context** → **Reproduction** for bugs (exact inputs/steps, expected vs. actual
result) or **Scenario** for limitations/friction (concrete task, obstacle, desired behavior) → **Impact**.
Optional bug evidence: a short log excerpt, stack trace, or screenshot link when it explains the failure.
If confirmation fails, use the printed `--retry` command.

## UI Projects

Astrale UI is one tree-shakeable runtime package plus consumer-owned pattern,
block, and theme source. Initialize a React and Tailwind CSS v4 project with the exact
published UI release:

```bash
astrale ui init --preset astrale
astrale ui search "editable chart with export"
astrale ui request "accessible async combobox with creation"
astrale ui add pattern/chart/line-basic
astrale ui add theme/observatory
astrale ui add ./my-playground-export.css
astrale ui doctor
astrale ui doctor --project ./apps/web
astrale ui preset apply compact
```

Initialization writes Base UI + Nova shadcn configuration, theme and preset CSS
imports, and `astrale-ui.lock.json`. The lock records the exact package version,
Git tag, resolved commit SHA, shadcn version, Base UI version, preset, and hashes
of installed source. Registry metadata, included manifests, and item files are
always read from that single commit snapshot.

Run `astrale ui add` without item arguments for an interactive picker. In CI,
provide canonical addresses explicitly. Ordinary add refuses locally edited
installed files; review those files, then use `--overwrite --yes` only when
replacement is intentional. `--dry-run` leaves project files and the lock
unchanged. Use `astrale ui search <free-text> --json` to receive a short ranked candidate list with
exact demo code and its `command` or runtime `packageImport`.

Use `astrale ui request <free-text>` when search does not satisfy the need. It calls
`/:ui.astrale.ai:function.request` on the selected instance with one bounded intent (1-512
characters) and prints the returned receipt: `{ state: "submitted", requestId, collaborationUrl }`
or `{ state: "pending" | "outcome-unknown" | "failed" | "conflict", requestId }`.

Patterns, blocks, and themes are application-owned source after installation. A
theme is copied to `components/astrale/theme/` and activated through one relative
import in the configured host stylesheet; local playground exports require no
registry fetch or shadcn invocation. Composition root
`className`, inline `style`, controlled values/actions, and stable `data-slot`
anatomy remain open to the host. The package owns reusable runtime behavior;
neither the CLI nor the SDK embeds the UI package or Base UI.

## Paths

Use canonical Kernel Paths:

| Form | Example |
|---|---|
| Domain root | `/:notes.example.dev` |
| Class | `/:notes.example.dev:class.Note` |
| Static callable | `/:notes.example.dev:class.Note:list` |
| Instance callable | `@node-id::notes.example.dev:class.Note.method.archive` |
| Node ID | `@node-id` |
| Active caller shorthand | `@self` |

Static dispatch uses one colon before the method. Instance dispatch uses `::` followed by the complete Domain-qualified Method key.
Discover methods with `astrale introspect <origin> --bundle`. Introspection can use a Class
receiver to inspect an instance contract; calling it requires an observed instance Path.
`@self` is expanded by the CLI before signing when it appears at the head of a
call Path or a bare `key=@self` value. It is not rewritten inside `--data`,
stdin JSON, URLs, or arbitrary substrings.

```bash
astrale get @self --json
astrale introspect /:notes.example:class.Note::notes.example:class.Note.method.archive
astrale call /:blog.example:class.Author:list limit=10
astrale call /:admin.astrale.ai:core.fleet::admin.astrale.ai:class.Fleet.method.listInstances
```

## Instances And Domains

`astrale instance` combines admin-provisioned instances and local bookmarks:

```bash
astrale instance create my-app
astrale instance root import development --yes
astrale instance invite my-app person@example.com
astrale instance invitation status @invitation-id
astrale instance status my-app
astrale instance status staging --bookmarked
astrale instance list --include-retired --admin-only --json
astrale instance use my-app
astrale instance bookmark staging --url https://kernel.example.com
astrale instance forget staging
```

Use explicit `-i <instance>` in scripts. `-i` and `--url` always select the instance a command
acts on; they never select the Admin kernel, and Admin operations (`instance list`, …) reject them; `domain list -i <instance>` lists what runs on that instance,
`domain list` without them uses the active instance. Choose the Admin kernel with
`--admin <bookmark>` or `--admin-url <url>`. `instance delete` affects an admin-managed instance; `instance forget`
removes only the local bookmark.
`instance status` reports Admin-owned lifecycle by default; add `--bookmarked`
to probe one local bookmark's exact issuer, JWKS, and TLS trust instead.
`instance invite` requires authority to manage the exact Instance and grants
only Instance member access. It returns the durable Invitation immediately.
WorkOS acceptance alone grants nothing: Admin registers the child Shell user
with the recipient's own credential, then adds Instance membership, when they
sign in to the Instance from the invitation link.
`instance invitation status <id>` performs one read-only observation of the
retained Invitation. Its `user` is the Shell User reserved on the Instance,
which an Instance administrator can assign to Core `admin` (see the
astrale-domain `references/users.md`). `completed` means access is
materialized; `accepted`, `registering`, and `registered` are intermediate
states, not completed access.
The command requires the exact Invitation id and does not change its state.
`instance invitation reconcile <id>` is diagnostic recovery, not the normal
invitation journey.
Without a deployed Admin Domain, `astrale instance list` cannot fetch managed
instances (key-backed identities have no Admin token). Use
`astrale instance list --bookmarked`.

Fleet administrators may add `--include-retired` to the ordinary Admin inventory. The default
excludes retired tombstones; included retired Instances use the same output shape and
are identified by terminal `state: "deleted"`. The optional `issuer` is present only when Admin has
retained exact evidence. Unreachable does not mean retired. Add `--admin-only` when local bookmarks
should be omitted from the machine-readable envelope.

`instance create` provisions through the configured Admin Domain with a WorkOS caller; Admin owns
Host placement. Creation preserves an existing active target, including a concurrent selection;
with no active target it selects the first instance after verifying owner access. It never repoints
an existing bookmark to a different endpoint. A conflict retains the ready receipt and verified
access, reports `bookmark.status=pending` with a recovery command under an unused name, and skips
automatic root import. Use `instance use <name>` to switch explicitly.
Automatic root recovery starts only after verified access and completed bookmarking, and replaces
an existing root alias only for the same exact issuer claim. Explicit root import keeps its recovery contract.
Neither `instance create` nor `instance root import` accepts `--host`.

`instance root import <slug-or-id>` retrieves the target owned Instance's root signing identity
through Admin over an end-to-end encrypted, one-use transfer. It imports that identity locally as
`<slug>-root`, not the Admin or Host root identity. Use `--admin <bookmark>` or `--admin-url <url>`
to select another Admin endpoint. Recovery requires `--yes` in automation, replaces an existing
key-backed identity with that name, and refuses to overwrite an IdP-backed identity.

Root import preserves the active instance and keeps the human Admin identity as the Instance
bookmark's default. Select the imported root explicitly with `--as`:

```bash
astrale instance root import development --yes
astrale get @self -i development --as development-root --json
```

Use an authorized human identity for the import; `development-root` is available for subsequent
Instance calls after recovery. Root success proves execution, not an application user's access Policy.

The CLI is connect-only: it does not build or run domains. The SDK's
`astrale-domain` binary owns `build`, `deploy`, `publish`, `diff`, `yank`, `list`, `lint`,
`package`, and test workflows; a deploy or a publish never installs. Project Environments say how to
deploy and with which secrets; they name no instance and do not use the CLI's active instance. Only
`astrale domain install` changes what an instance runs.

`astrale domain install` takes deployment URLs and versions:

- Deployment URLs (`https://`, or `http://` for a local Host) go to the
  instance Kernel through the public install syscall, on any instance you can
  authenticate to. Several references install in ONE atomic Kernel operation
  (every Domain moves or none does), which is how dependent Domains move together.
  The CLI reads each URL's canonical `release.json` first (a 503 is read again for up to
  60 s), refuses two references to one origin, pins the release digest it
  read, and verifies the installed pins afterwards.
- A version reference, `<origin>@1.5.0` (or `@2.0.0-rc.1`) for exactly that
  version, a pre-release or a yanked one included (a yanked one warns), or
  `<origin>@1.5` for the highest stable 1.5.x that is not yanked, is resolved
  in the Admin registry with your own identity (`--admin` / `--admin-url`, or
  the configured Admin target). A private Domain needs `domain_installer`,
  directly or through a Group; one you cannot read is REGISTRY_DOMAIN_NOT_FOUND.
  The version becomes its Publication's deployment URL and release digest; the
  CLI checks the deployment still serves that release
  (PUBLICATION_RELEASE_MISMATCH otherwise) and the Kernel refuses any other.
  A major alone (`@1`), a range or build metadata is refused; an unresolvable
  version is VERSION_UNRESOLVED. Versions and URLs mix in one install.
- An issuer change is never silent. When a URL serves another issuer than
  the one its origin is installed under, the install needs consent, recorded
  by the Kernel in the installation: `--allow-issuer-change` for a new
  deployment of the same line (same `<line>-` prefix and routing domain),
  `--allow-issuer-change=<origin>` for any other change (a legacy issuer
  moving to its first deployment included), or typing the origin at a
  terminal. The replaced issuer keeps working while its in-flight work
  drains; `--revoke-previous` cuts it at the activation. A first install from
  a deployment URL needs no consent; the CLI notes the unverified claim.
  The origin is given only after `=`: a bare `--allow-issuer-change` never
  takes the next argument. Without consent, ISSUER_CHANGE_NOT_CONSENTED lists
  every unconsented change in `details.origins` (`origin`, `installed`,
  `replacement`, `line`) before anything is sent; `--json` reports each
  consent as `references[].consent` (`from`, `to`, `previous`).
- Before the install is sent, an advisory pre-check runs the Kernel's
  compatibility engine on what the caller can read, both ways: each installed
  root must find what it uses in its dependencies as the install leaves them,
  and each installed Domain the install does not name must still find what it
  uses in every upgraded dependency. For each broken dependent it proposes the
  highest stable, non-yanked published version built against the new revision
  (an Admin registry read, also for URL installs) and the grouped install;
  unreadable Domains are reported as not evaluated. The install is still sent
  and the Kernel decides. `--json` carries it as `precheck` (`compared`,
  `dependencies`, `dependents`, `proposals`, `command?`, `skipped`,
  `unevaluated`) in the report, and beside a SCHEMA_DEPENDENCY_INCOMPATIBLE or
  SCHEMA_DEPENDENTS_INCOMPATIBLE refusal.

```bash
astrale domain install https://crm.example -i staging
astrale domain install https://agencies.example https://employees.example -i staging
astrale domain install crm.example@1.5 -i production
astrale domain install agencies.example@1.5.0 https://employees.example --allow-issuer-change -i staging
astrale domain install <new-deployment-url> --allow-issuer-change -i staging
astrale domain install <deployment-url> --allow-issuer-change=crm.example -i staging
astrale domain uninstall crm.example -i staging
astrale domain uninstall app.example shared.example --destructive -i staging
```

`astrale domain versions <origin>` lists the Domain's published versions from the Admin
registry, read with your own credential: you need `domain_installer` or `domain_admin` on the
Domain, directly or through a Group. Pre-releases and yanked versions are listed; a yanked
version is never chosen by a line such as `@1.5`. An absent Domain and one you cannot read give
the same `REGISTRY_DOMAIN_NOT_FOUND`. `--json` prints one `astrale.registry-index` document;
refusals print `{ "error": { "code", "message", "details" } }` on stdout and exit 1. Rerunning
the same command is always safe; it can help only when `details.retryable` is `true`.

```bash
astrale domain versions issues.astrale.ai
astrale domain versions issues.astrale.ai --json --as ci
```

`astrale domain list` (active instance, or `-i <instance>` / `--url <kernel>`) shows what runs on that instance: each
installation its Kernel pins to a deployment that you can read, with the release digest from the
Kernel pin, the version from the Admin registry (the version naming that exact release, else the
one naming the same build from the same issuer, as `1.5.0 · staging`; a build digest alone never
names a version), else the name the deployment's public record gives a preview
(`1.4.2 + 7 commits · a1b2c3d · staging`, printed as computed), and
the highest stable version available above it. The list is partial by nature: built-in and local
Domains, and Domains you cannot read, never appear, so an absent origin is unknown, not "not
installed". The registry is read as you (`--as` or your default identity) on the Admin kernel;
`--creds` and `--anonymous` apply to the instance only. `--json` prints one
`astrale.installed-list` document.

```bash
astrale domain list -i staging
astrale domain list -i staging --json
```

The hidden `astrale __domain-registry bundle|claim|publish|yank` commands are JSON plumbing for
`astrale-domain diff`, `publish` and `yank`; do not call them by hand. `astrale-domain publish`
claims an origin no one has before its first deployment: its first claimer administers it.

On a Kernel that takes no issuer consent, a replacement cannot change an
installed Domain issuer: uninstall the origin first and then install it again.
Uninstall accepts one or more origins and removes the complete selected set atomically, so
dependencies inside that set are allowed. Safe mode is the default and never deletes application
data. `--destructive` deletes application facts whose concrete Class belongs to a selected Domain;
it does not cascade into unselected Domains. Surviving dependents and surviving foreign Edges that
reference selected Nodes still block the complete operation. Type the canonical Domain list
interactively, or pass `--yes` in automation.

Bookmarks retain their own TLS trust (`--ca`). `instance use` probes OIDC and
JWKS with that exact CA. If two bookmarks point to the same normalized URL with
different CA settings, the CLI warns and `instance list --bookmarked --json`
shows each bookmark's `caFile`, issuer, and default identity.

A deploy never changes what an instance runs: each deployment URL serves one
release for good, so new code reaches an instance only when it installs the new
URL or version. Reinstalling the URL an instance already runs changes nothing.

## Identity And Delegation

`astrale auth login` stores an IdP-backed identity. `astrale identity create`
creates a local key identity. Registration targets an existing Identity Node;
it never creates a Node, changes business properties, assigns a Group, or replaces
the local identity or its keypair:

```bash
astrale identity create alice
astrale identity register alice \
  --node @existing-user-id \
  -i staging
```

The Kernel assigns Node IDs. They are returned by reads and creation results
and can be reused through the `@node-id` Path form; do not derive application
meaning from their contents. The primary self credential is signed for the target
Kernel audience. Register checks the caller's authority on the existing Node.
When a Domain callable supplies that authority, optionally name it with `--via`;
the CLI sends the same request and verifies the returned Node and Authentication.
No Domain callback is required when the direct caller already has authority:

```bash
astrale identity register operator \
  --node @existing-operator-id \
  --via /:operations.example:function.registerOperator \
  -i staging
```

`astrale token` issues an audience-bound credential for the selected authenticated identity. When
the audience is the target Kernel issuer (the default), it mints a top-level Kernel bearer credential
for the selected identity that can be reused with `--creds`. A different `--audience` creates a delegated service envelope for that
receiver instead. TTL defaults to 240 seconds so ordinary tokens remain short beneath the one-hour
local operator proof; an explicit TTL still cannot outlive the selected source credential. Use
`--raw` for shell assignment.

```bash
TOKEN=$(astrale token --raw -i staging)
astrale query /:notes.example:class.Note --creds "$TOKEN" -i staging
```

A minted token carries the identity itself as principal. Function admission requires the principal
to be able to use the Function, so a minted token fails a Domain callable that the identity reaches
only through a Policy. Without `--creds`, the CLI exchanges the selected identity's credential
through a Domain instead: the Domain becomes the principal, the identity stays the caller, and the
Policy is evaluated against the identity.

| Selection | Principal presented | Effect |
| --- | --- | --- |
| `call` with `--as <identity>` or the default identity | the callable's declaring Domain | the principal gate passes; the Policy is evaluated against the identity |
| `get`, `query`, `mutate` on an Astrale-managed instance | Shell | bounded by Shell's authority and the identity's Policies |
| `--creds "$(astrale token --raw)"` | the identity | a Domain callable reached only through a Policy fails with `2004`, unless the identity holds `can_use` on it through a Group |

Reuse a minted token for Kernel reads and writes the identity may perform itself; call Domain
callables with `--as`.

`astrale auth token` is different: it prints the cached upstream IdP token.

## Graph Reads

### `get`

`get` reads one exact canonical Node:

```json
{ "id": "node-id", "class": "notes.example:class.Note", "props": {} }
```

The structured Node result is exactly `{ id, class, props }`.

```bash
astrale get @note --json
astrale get /:notes.example:class.Note
astrale get /:kernel.astrale.ai --schema
```

Method Paths identify callables rather than Nodes; use `call` to invoke them or
`introspect` to inspect their Schema. Schema-valued properties are omitted
unless `--schema` is passed.

### `introspect`

`introspect` reads the Kernel Schema syscall for one installed Domain.

```bash
astrale introspect kernel.astrale.ai
astrale introspect /:kernel.astrale.ai --bundle
astrale introspect /:kernel.astrale.ai:class.Identity:whois
astrale introspect @note::notes.example:class.Note.method.archive
```

A method or Function Path projects its input/output from the installed bundle.
An instance Method's qualified key selects the schema even with an `@id` receiver;
introspection neither reads nor invokes that receiver. A bare `@id` has no schema origin.

### `query`

`query` executes canonical `astrale.graph.query/v6`. Its structured result is
`{ kind: "graph", graph: { nodes, edges }, page?: { next } }`; pass the opaque
`page.next` value to `--cursor` until it is absent.

- Positional Paths create Path source terms.
- `--class <path>` selects Nodes implementing one exact Class.
- `--edge <class>` adds one exact expansion; direction is `outgoing`,
  `incoming`, or `incident`.
- `--limit` is finite and defaults to 100.
- `--cursor` resumes the same caller-bound query scope.
- `--ast` and `--file` admit a complete canonical Query V6 document.

```bash
astrale query /:notes.example:class.Note --limit 50 --json
astrale query --class /:notes.example:class.Note --limit 50 --json
astrale query @note \
  --edge /:notes.example:class.references \
  --direction outgoing --limit 25 --json
astrale query --file query.v6.json --cursor "$CURSOR"
```

Use `query` with `--edge` for an exact neighborhood.

## Mutations

`astrale mutate` accepts canonical `astrale.graph.mutation/v3` or its exact
`{ preconditions, operations }` authoring input from `--data`, `--file`, or
stdin. The transition is atomic. `--dry` admits and prints the canonical
document without opening a Kernel connection. The result is `{ createdNodes }`.

```bash
astrale mutate --file mutation.v3.json --dry
astrale mutate --file mutation.v3.json
```

## Calls

`astrale call` creates one Path-targeted Call. Input priority is `--data`,
`key=value`, piped stdin, then `{}`. `--dry-run` admits the Path and prints
the call input. Value, binary, and stream results are handled explicitly, and
`--output` writes binary data. A streaming binary is drained with backpressure
while the command-scoped Client session is live, then presented through the same
raw/file/JSON paths as buffered binary. JSON preserves application status and
encodes the body as text or base64. Callable input/output is
`astrale introspect <path>`.

```bash
astrale call /:blog.example:class.Author:list limit=10
astrale call /:blog.example:class.Author:create \
  --data '{"name":"Ada"}' --json
astrale call /:assets.example:class.Asset:render id=123 --output asset.png
astrale call /:blog.example:class.Author:create -d @author.json
astrale call '/:admin.astrale.ai:core.fleet::admin.astrale.ai:class.Fleet.method.listInstances' \
  --admin --json
```

Top-level `key=value` values coerce booleans, null, numbers, arrays, and
objects. Use `--data` for nested or digits-only string values. `--data` also
takes `-` (read the JSON from stdin) or `@<file>`, parsed like inline JSON; pass
secrets only in those forms so their values never sit in argv or shell history.

`--data -` reads piped stdin only; on a terminal it is refused.

`--admin [<bookmark>]` or `--admin-url <url>` (with `--domain-issuer <url>`) runs
the call on the Admin kernel, selected exactly like `domain` commands select it.
`-i` and `--url` are refused with them (usage error, exit 2), as are `--admin`
with `--admin-url` and `--domain-issuer` without `--admin-url`. The call itself
is unchanged: it exchanges at its callable's declaring Domain as the Admin
kernel's installation names it; the Admin Domain issuer only completes the Admin
target. Put `key=value` params before `--admin`, or write `--admin=<bookmark>`.

Rotating one secret of one deployment the Admin instance's Services host is
such a call: the deployment's `setSecret`, with the input in a private file or
piped, never in argv (`astrale-domain list --json` gives each deployment's
`callTarget.path`). The deployment keeps its URL, issuer and key, so nothing is
reinstalled; the new value is served about 4 s later.

```bash
astrale call "@$ID::services.astrale.ai:class.CloudflareDeployment.method.setSecret" \
  --admin -d @rotate.json --json
```

## Journal

`astrale logs` reads the public Kernel journal syscall and returns
`{ records, cursor? }`. Filters match exact values; use `--topic-prefix` for
prefix matching:

```bash
astrale logs -i staging --limit 50
astrale logs --topic op:function.failed
astrale logs --topic-prefix op:function. --follow
```

Use `--principal`, `--caller`, `--since`, `--until`, or an opaque `--cursor` as needed.
`--principal` filters in the Kernel by the executing principal; a Domain acting for a user
(managed CLI, Console, `astrale call` through a Domain token exchange) is the principal of its
records. `--caller` keeps the records whose caller (the identity whose authority the operation
exercised) matches; it filters each returned page, so `--limit` bounds the page first. The Kernel
records `caller` only when it differs from the principal, so the effective caller is `caller`,
else `principal`: exact for records written by a Kernel with astrale-os/kernel#959, while records
from an older Kernel fall back to the principal (a Domain acting for a user shows as the caller).
Both accept `@self`; the human table shows PRINCIPAL and the effective CALLER, and JSON keeps
`caller` only where the Kernel recorded it.
`--follow` retains one Client session and advances only with returned cursors.
Structured output retains the admitted `correlation` object, including invocation root and
parent identifiers, and includes `correlationId` as a projection of `invocationId`.
With `--json`, `--follow` emits NDJSON with one complete admitted record per line; combining
`--format yaml` with `--follow` is rejected.

## Views And Browser Sessions

`astrale view` opens one resolved View through a local browser shell. Every View belongs to its
Domain: pass a Domain origin (opens its entrypoint, or `--view <slug>`) or an explicit ViewPath. A
View is never opened for a node; a View that shows one node routes to it itself.

```bash
astrale view crm.example --list
astrale view crm.example --snapshot
astrale view crm.example --view dashboard
astrale view /:crm.example:view.dashboard
astrale view --sessions
astrale view --close <session-id>
```

`astrale browser` prepares a persistent authenticated GUI browser profile.
Use `astrale browser --check` to verify it, then drive the printed profile with
`agent-browser`.

## Output And Automation

- TTY defaults are human-readable.
- `--json` emits one JSON document for finite commands; `logs --follow` emits an NDJSON stream.
- `--raw` unwraps scalars and writes raw binary bytes.
- `--format yaml|json` selects finite structured rendering; `logs --follow` supports JSON/NDJSON only.
- Use `--ci --no-prompt` for automation.
- Use explicit `-i`, `--as`, and `--timeout` rather than ambient state.
- Pipe large JSON through stdin; command-line argument size is limited by the
  operating system.

## Debugging

Start with:

```bash
astrale status
astrale instance active
astrale auth status
astrale whoami
```

Add `--debug` for full Kernel error diagnostics. Missing and authorization-masked
Nodes are intentionally indistinguishable. A Path also needs access to its
intermediate nodes and edges: an observed Node may be readable by `@id` or a
Class query while its Domain-rooted Path is unavailable. Check `-i` and `--as`;
this alone does not prove corrupt data. Use `introspect` for callable schemas.

## Storage

State lives under `ASTRALE_HOME`, or `~/.astrale` by default:

```text
config.json
instances.json
identities.json
idps/
idp-sessions/
keys/
browser.json
browser/
exchange/credentials.json
session/routes.json
session/installations.json
```

`exchange/credentials.json` holds Domain-exchanged credentials until they expire;
`session/routes.json` holds learned Domain routes and their short-lived carriers;
`session/installations.json` remembers each Domain's installed issuer per Kernel.
All three are owner-private caches: deleting them only costs a re-read or a new exchange, never
access. Before a callable or managed-Instance command uses a credential from a remembered issuer,
the CLI confirms it with a read-only Kernel call. After a Domain reinstall and the previous issuer's
drain, a 2002 refusal of that confirmation re-reads the installation and exchanges at the new issuer
within the same command, before any application call. Application calls themselves are never replayed
by this recovery.

Optional roots are `ASTRALE_HOME`, `ASTRALE_KEYS_DIR`, and
`ASTRALE_DATA_DIR`.

## Source Map

- Entry: `cli/bin/astrale.ts`
- Program and shared options: `cli/src/program/`
- Public Kernel connection boundary: `cli/src/connection/`
- Query/Mutation document preparation: `cli/src/graph/`
- Commands: `cli/src/commands/`
- Shared presentation and local stores: `cli/src/lib/`
- Studio bridge: `cli/studio/server/`
- Tests: owner-local `__tests__/` directories
