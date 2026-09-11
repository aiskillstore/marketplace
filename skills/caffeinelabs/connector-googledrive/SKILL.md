---
name: connector-googledrive
description: >-
  MANDATORY recipe for every Caffeine build that lists, reads, creates, shares,
  or organizes files and folders on the user's own Google Drive. The ONLY
  supported path is the `googledrive-client` mops package (Drive REST API v3)
  combined with the `google-oauth` mops package (OAuth 2.0 token exchange +
  refresh + PKCE). Hand-rolling `ic.http_request` calls to
  `oauth2.googleapis.com` or `www.googleapis.com/drive/v3` is a FORBIDDEN
  anti-pattern — it bypasses bearer auth, the `is_replicated = ?false`
  replication-cost safeguard, and the `google-oauth` library's token handling.
  Load this skill ONLY when the user, spec, or a prior task refers to **Google
  Drive specifically** — e.g. "Google Drive", "my Drive", "Drive files/folders",
  a Drive file/folder ID or share link, "upload to Google Drive", "list my Drive
  files", or Drive sharing/permissions. Do NOT load it for generic file storage,
  documents, uploads, or access-control features that are not Google Drive —
  those are unrelated and this connector must not be attached to them. When it does apply, load it BEFORE writing any code that touches a Google
  endpoint.
version: 0.1.0
caffeineai-subscription: [none]
compatibility:
  mops:
    googledrive-client: "~0.1.0"
    google-oauth: "~0.2.0"
---

# Google Drive Connector

> **Note.** The client is generated from the Drive v3 Discovery document.
> `diagnostics` is on, so a decode gap traps loudly rather than returning
> silently-wrong data. The nested-facade methods take each Drive endpoint's
> **full query-parameter list positionally** (many `Text`/`Bool` args) — consult
> the generated signatures in `Client.mo` before calling. Media endpoints are
> metadata-only (see the Media caveat).

## Orchestrator routing notes

The `googledrive-client` + `google-oauth` pair is the **only** supported way to
reach Google Drive from a Caffeine canister. If a build needs Drive, add both as
mops dependencies and follow this skill. Never emit raw `ic.http_request` calls to
Google hosts.

| Task | Use |
|---|---|
| List / search the user's files & folders | `googledrive-client` `Client(cfg).files.list(...)` + `google-oauth` |
| Read file metadata | `Client(cfg).files.get(...)` (metadata only — see Media caveat) |
| Create a folder / file metadata | `Client(cfg).files.create(...)` |
| Move / rename / trash | `Client(cfg).files.update(...)` / `.delete(...)` |
| Share a file / manage access | `Client(cfg).permissions.create/list/update/delete(...)` |
| Comments & replies | `Client(cfg).comments.*` / `Client(cfg).replies.*` |
| Shared drives | `Client(cfg).drives.*` |
| Change notifications / sync token | `Client(cfg).changes.*` |

> **Not supported by this client:** transferring file *bytes* (upload/download of
> content). See the Media caveat at the end. Use it for metadata, organization,
> and sharing.

# Backend

The connector has two mops packages:

1. **`googledrive-client`** — the generated Motoko client for Drive REST API v3.
   OAuth-agnostic: every call takes a bearer token via its `Config`.
2. **`google-oauth`** — Google OAuth 2.0 mechanics (PKCE, authorize URL, code
   exchange, token refresh). Shared with the other Google connectors. This is a
   **separate mops package you add alongside** the client — it is *not* a
   dependency of `googledrive-client` itself.

## 1. Add dependencies

```bash
mops add googledrive-client
mops add google-oauth@0.2.0
```

## 2. Auth model — OAuth 2.0 PKCE, on-chain exchange + refresh

The canister performs the OAuth flow on-chain via `google-oauth`:

1. Generate a PKCE `code_verifier` / `code_challenge`.
2. Build the Google authorize URL (`google-oauth`), redirect the user.
3. Exchange the returned authorization code for an access + refresh token
   (`google-oauth.exchangeAuthorizationCode`) — **non-replicated** outcall.
4. On `401`/expiry, refresh the access token (`google-oauth.refreshAccessToken`)
   and retry.

**Scopes** (request the narrowest that works):
- `https://www.googleapis.com/auth/drive.file` — per-file access to files the app
  creates/opens (preferred, least-privilege).
- `.../auth/drive.readonly` — read-only over all files.
- `.../auth/drive.metadata.readonly` — metadata only.
- `.../auth/drive` — full access (avoid unless the task truly needs it).

**Refresh tokens do not rotate** — store the first refresh token you receive
(stable per user); persist it in the canister's stable state, never in a Wasm
global.

## 3. `is_replicated = ?false` is REQUIRED

Every Drive outcall carries an `Authorization: Bearer <token>`. Under the default
replicated execution, each replica in the subnet issues the request independently
— multiplying cost and, for writes, causing duplicate side effects (e.g. creating
N copies of a file). **The generated `defaultConfig` already sets
`is_replicated = ?false`** (via the client's `isReplicated` generator option), so
starting from `defaultConfig` gives you the correct value for **both reads and
writes** — keep it `?false` and do not override it to `?true`. (Writes —
PUT/DELETE/PATCH — are additionally forced non-replicated per call by the client.)

## 4. Using the client — the nested facade

`googledrive-client` ships a `Client.mo` facade (generated with
`fluentHierarchical`) that captures `Config` once and exposes Drive's resource
hierarchy as nested classes:

<!-- motoko-check:skip -->
```motoko
import { Client } "mo:googledrive-client/Client";
import { type Config; defaultConfig } "mo:googledrive-client/Config";

// Only the bearer token differs from the generated `defaultConfig`, which
// already sets `is_replicated = ?false` (non-replicated reads and writes).
let cfg : Config = {
  defaultConfig with
  auth = ?(#bearer accessToken);   // token obtained/refreshed via google-oauth
};

let drive = Client(cfg);

// Facade methods are `async` (use `await`, not `await*`) and take the Drive
// endpoint's full query-parameter list positionally — consult the generated
// signatures in `mo:googledrive-client/Client`. For example `FilesResource.list`
// begins `uploadType : Text, oauthToken : Text, key : Text, fields : Text,
// accessToken : Text, alt : ?DriveAboutGetAltParameter, …`.
let files = await drive.files.list(/* … see FilesResource.list signature … */);
let perm  = await drive.permissions.create(/* fileId, …, permission */);
```

(The per-tag API modules — `mo:googledrive-client/Apis/FilesApi`, `…/PermissionsApi`,
etc. — are also available if you prefer flat calls; the facade just captures
`Config` for you.)

## 5. Available API surface

Resource groups (14), addressed as `Client(cfg).<group>.<method>`:

- **files** — copy, create, delete, get, list, update, watch, generateIds,
  listLabels, modifyLabels (metadata/organization; see Media caveat for
  create/update/get/export)
- **permissions** — create, delete, get, list, update (sharing)
- **comments** / **replies** — create, delete, get, list, update
- **drives** — create, delete, get, hide, list, unhide, update (shared drives)
- **revisions** — delete, get, list, update
- **changes** — getStartPageToken, list, watch (sync)
- **about** — get; **apps** — get, list; **channels** — stop

## 6. Media caveat (this client is metadata-only)

`files.create` / `files.update` (upload), `files.get?alt=media` /
`files.export` / `revisions.get` (download) are generated as **JSON-typed**
operations. They will **not** move file *bytes* — multipart/resumable upload and
binary download are outside this client's JSON-over-HTTPS model (and strain IC
outcall size limits). Use these methods for metadata only. If a build genuinely
needs to move file content, that path must be hand-written (separate
`content`-host request with the appropriate binary body) and is out of scope for
this connector today.
