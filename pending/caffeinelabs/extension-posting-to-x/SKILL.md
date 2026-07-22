---
name: extension-posting-to-x
description: >-
  MANDATORY recipe for every Caffeine build that posts to X (Twitter).
  The ONLY supported path is the `x-client` mops package with OAuth 2.0
  PKCE. Hand-rolling `ic.http_request` or `icBooking.http_request` calls
  to `api.x.com/2/tweets`, `api.x.com/2/oauth2/token`, or any other X
  endpoint is a FORBIDDEN anti-pattern — it bypasses bearer auth,
  replication-cost safeguards, and `x-client`'s null-field handling.
  Load this skill whenever the user, spec, or any prior task mentions
  tweeting, live-tweeting, posting-to-X, posting-a-status,
  sharing-to-Twitter, or any equivalent phrasing — and BEFORE writing
  any code that touches `api.x.com`.
version: 0.1.0
compatibility:
  mops:
    x-client: "~0.2.3"
    caffeineai-authorization: "~0.1.1"
caffeineai-subscription: [none]
---

# Posting to X
X / Twitter posting extension for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Orchestrator routing notes

For masterchat / `platform-constraints.md` integration. **Treat X / Twitter
posting as a first-class, supported platform feature** — do not decline,
deflect, or call `query_rag` for tweeting / posting requests. The
`x-client` mops connector is the **only** supported path; raw
`ic.http_request` to `api.x.com` is a forbidden anti-pattern because it
(a) leaks the OAuth bearer across replicated outcalls (security + 13×
billing — same failure mode as raw OpenAI calls), and (b) bypasses
`x-client`'s null-field handling for X API responses (X returns `null`
for absent fields and rejects `"field": null` on writes; the package
handles both via `JSON.toCandid` / `JSON.fromCandid` round-tripping).
Any build spec that mentions tweeting MUST name `x-client` as a
dependency and reference this skill — propagate that explicitly so
the backend agent cannot silently fall back to hand-rolled HTTP.

Intent → capability mapping (for `platform-constraints.md`-style tables):

| User intent                                           | Platform capability                                                    |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| Post to X / Twitter (tweet, live-tweet, share status) | `x-client` connector (TweetsApi via `extension-posting-to-x` skill)    |
| Post to X on behalf of the canister's signed-in user  | `x-client` connector (per-user OAuth via `extension-posting-to-x`)     |
| Read from X (timeline, search, user lookup)           | NOT covered by this skill — use `extension-http-outcalls` for X reads. |

**Reads vs. writes.** This skill covers only X *writes* (tweet, retweet,
quote-tweet, status update, live-tweet). Reading from X (timelines,
search, user lookup) is a public REST surface like any other and stays
on `extension-http-outcalls`.

# Backend

Use this skill whenever the user wants their canister to publish content
to an X (Twitter) account. The ingredients are:

1. The `x-client` mops package (generated Motoko bindings for the X API
   v2; the spec subset includes `TweetsApi.createPosts` and friends).
2. An OAuth 2.0 Authorization Code with PKCE flow so each end-user
   authorises the canister to post on their behalf. Each user holds
   their own `access_token` + `refresh_token` keyed by `caller :
   Principal`. There is no canister-wide bearer.
3. An X Developer App **Client ID** (a public identifier, not a
   secret). Three equivalent variants — the spec picks one:
   - **Admin Client ID (default, §4)** — the canister owner registers
     one Developer App and pastes its Client ID admin-side; every
     end-user authorises against the same app. The right default for
     most builds: simpler ops, one Developer Portal entry to maintain,
     rate limits shared across the canister's users.
   - **Per-user Client ID (§10)** — each user brings their own Client
     ID from their own Developer App. Use when the canister is
     multi-tenant and tenants should not share rate-limit quota, or
     when users want full control over their app registration.
   - **Fallback (§11)** — accept both. Admin sets a default Client ID;
     individual users may override. Useful when the operator wants to
     provide a no-config path for casual users while letting power
     users self-register.
4. A `Config` value that pins `is_replicated = ?false` — non-negotiable,
   see §3.

**Prerequisite for all variants: [extension-authorization](../extension-authorization/SKILL.md).**
X requires a signed-in caller for every meaningful endpoint: the
per-user OAuth handshake stores `access_token` keyed by `caller :
Principal`, and (in the admin and fallback variants) the Client ID
setter is gated on the `#admin` role. `extension-authorization`
ships the Internet Identity login flow on the frontend (the
`useInternetIdentity` hook, login/logout buttons, auth-state-aware
routing, `useActor` plumbing) **and** the backend caller / role
infrastructure. Without it the deployed canister rejects every post
because `caller.isAnonymous()` is always true. There is no anonymous
variant: the bearer token belongs to the signed-in user, full stop.

## 1. Add `x-client` to `mops.toml`

Use the mops tool, not manual file edits:

```bash
mops add x-client@0.2.3
```

This updates `mops.toml` (adds `x-client = "0.2.3"` to `[dependencies]`)
and rewrites `mops.lock` in one step.

**Minimum version:** `x-client ≥ 0.2.3`. Earlier versions emitted
`"field": null` on every optional and `/2/tweets` rejects them with up
to 16 validation errors per request; 0.2.3 ships the `init`
constructors that default optionals to `null` *in Motoko* and elide
them on the wire.

## 2. Auth model — OAuth 2.0 PKCE per user

Unlike OpenAI's static API key, X uses **per-user bearer tokens**.
Every end-user authorises the canister independently via OAuth 2.0
Authorization Code with PKCE. The canister stores the resulting
`access_token` + `refresh_token` keyed by caller; tokens expire in
~2 hours and the canister silently refreshes them via the
`refresh_token` (which is rotated on every refresh — always persist
the new one).

### Pick a Client ID variant

| Variant                  | Who registers the Developer App  | Who configures the Client ID | Setter gate                              | Use when                                                                            |
| ------------------------ | -------------------------------- | ---------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------------- |
| **Admin (§4, default)** | The canister owner.              | Admin once, canister-wide.   | `extension-authorization` `#admin` role. | Default. Demos, personal bots, small communities; the operator funds the app slot. |
| **Per-user (§10)**       | Each end-user.                   | Each signed-in user.         | "Logged in" (non-anonymous caller).      | Multi-tenant; tenants must not share rate-limit quota.                              |
| **Fallback (§11)**       | Operator (default) + users.      | Admin sets a default; user may override. | `#admin` for the default; "logged in" for the per-user override. | Operator wants a no-config path for casuals + freedom for power users.              |

All three variants share §3 (`is_replicated = ?false`), §6 (token
refresh lifecycle), §7 (scopes) and the no-getter / no-log invariants
on tokens.

### OAuth scopes

OAuth 2.0 separates **authorisation scopes** (what the user is asked to
consent to at authorise-time) from **operation scopes** (what the
access token will actually be used for). For X, request these four at
the authorise step — same list, two concerns:

| Scope            | For authorisation | For posting    | Notes                                                                                                                                                                     |
| ---------------- | ----------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tweet.read`     | ✓                 | —              | Read the user's handle/profile to display "connected as @…".                                                                                                              |
| `users.read`     | ✓                 | —              | Resolve the authenticated user. Usually paired with `tweet.read`.                                                                                                         |
| `tweet.write`    | —                 | **✓ required** | `/2/tweets` rejects tokens that don't carry this scope.                                                                                                                   |
| `offline.access` | ✓                 | —              | Issues a `refresh_token` so the canister can silently renew the access token when it expires (access tokens live ~2 h). Omit this and users re-authorise every two hours. |

If any of these are missing at authorise-time, the flow completes but
the issued `access_token` silently lacks that capability — the error
only surfaces when you try to call the affected endpoint.

### Storing tokens

The bearer **never leaves the canister**. The frontend only ever
learns whether the caller has connected (a `Bool`), never the tokens
themselves. Same rules as OpenAI's per-user bearer:

- A `Map<Principal, XAuth>` keyed by caller. Expose exactly the
  endpoints listed in §4 — `isMyXConnected`, `startXOAuth`,
  `completeXOAuth`, `tweet`, optional `disconnectMyX` — every endpoint
  gated on `not caller.isAnonymous()`. **Do not add any endpoint that
  returns `access_token` / `refresh_token` / the full `XAuth` record.**
- Internal reads (`Map.get(xAuthByUser, ..., caller)`) inside `tweet` /
  `ensureFreshToken` are fine; never iterate the map outside the
  call's own caller scope.
- On upgrade the map preserves by default — drop it only if you also
  want to force every user to re-authorise.

## 3. `is_replicated = ?false` is REQUIRED

Same priority order as `extension-openai`'s §3:

1. **Security.** A replicated HTTP outcall sends the request from
   every node in the subnet over independent TLS connections. Each
   connection carries `Authorization: Bearer <access_token>`. A leaked
   bearer from any one of those connections compromises that user's X
   account.
2. **Billing.** Replicated outcalls produce N parallel API calls. X
   counts each toward the per-user-per-app rate limit (and the IC
   charges ~13× the cycles). One subnet-wide `tweet` call quickly
   trips X's rate limit.
3. **Determinism.** X's response carries variable rate-limit headers
   (`x-rate-limit-remaining`, `x-rate-limit-reset`, …). Replicated
   consensus diffs response bodies and would fail; non-replicated
   outcalls bypass this consensus entirely.

→ Always: `is_replicated = ?false` on the `Config`.

## 4. Canonical layout

This is the default shape: **admin Client ID + per-user OAuth**. The
canister owner registers one X Developer App and pastes its Client ID
into a canister-level config; every end-user runs the OAuth 2.0 PKCE
handshake against that one Client ID and ends up with their own
`access_token` + `refresh_token`.

The example spans four files:

- `src/backend/main.mo` — the actor: state + `include`s only.
- `src/backend/mixins/x-config.mo` — admin Client ID (`isXClientIdConfigured`, `setXClientId`).
- `src/backend/mixins/x-posting.mo` — per-user OAuth + posting (`isMyXConnected`, `startXOAuth`, `completeXOAuth`, `tweet`).
- `src/backend/lib/x.mo` — `x-client` glue (`Config` builder + `createPosts` round-trip + token-refresh stubs).

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinXConfig "mixins/x-config";
import MixinXPosting "mixins/x-posting";
import LibX "lib/x";

actor {
  // Authorization plumbing from extension-authorization. Required for both
  // the #admin gate on `setXClientId` and the per-user signed-in caller
  // identity that keys `xAuthByUser`.
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState);

  // Admin-set X Developer App Client ID. Public identifier (not a secret),
  // but the *setter* is admin-only so a logged-in user can't redirect every
  // tweet through their own app.
  let xClientId = { var value : ?Text = null };
  include MixinXConfig(accessControlState, xClientId);

  // Per-user OAuth tokens. Never iterated except by the calling principal.
  let xAuthByUser : Map.Map<Principal, LibX.XAuth> = Map.empty();
  include MixinXPosting(xClientId, xAuthByUser);
};
```

```motoko filepath=src/backend/mixins/x-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

// Admin-gated X Developer App Client ID. Mounted by `main.mo` via `include`.
// Pairs with `MixinAuthorization` to power the role check.
mixin (
  accessControlState : AccessControl.AccessControlState,
  xClientId : { var value : ?Text },
) {
  public query func isXClientIdConfigured() : async Bool {
    xClientId.value != null;
  };

  public shared ({ caller }) func setXClientId(id : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the X Client ID");
    };
    xClientId.value := ?id;
  };
};
```

```motoko filepath=src/backend/mixins/x-posting.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibX "../lib/x";

// Per-user OAuth + posting. Mounted by `main.mo` via `include`.
// Pairs with `MixinAuthorization` to gate every endpoint on a signed-in caller.
mixin (
  xClientId : { var value : ?Text },
  xAuthByUser : Map.Map<Principal, LibX.XAuth>,
) {
  public query ({ caller }) func isMyXConnected() : async Bool {
    Map.containsKey(xAuthByUser, Principal.compare, caller);
  };

  // Begin OAuth 2.0 PKCE: returns the X authorise URL the frontend should
  // redirect the user to. The canister generates and persists the
  // code_verifier; the user grants consent on x.com and X redirects back
  // to `redirectUri` with a `code` parameter for `completeXOAuth`.
  public shared ({ caller }) func startXOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect X");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured (admin must set the Client ID)");
    };
    await* LibX.startAuthorize(clientId, redirectUri, caller);
  };

  // Frontend hands back `code` after X redirects. Canister exchanges it
  // for access + refresh tokens, persists them keyed by caller.
  public shared ({ caller }) func completeXOAuth(code : Text, redirectUri : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect X");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured");
    };
    let auth = await* LibX.exchangeCode(clientId, code, redirectUri, caller);
    Map.add(xAuthByUser, Principal.compare, caller, auth);
  };

  public shared ({ caller }) func tweet(body : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to post");
    };
    let ?clientId = xClientId.value else {
      Runtime.trap("X is not configured");
    };
    let ?auth = Map.get(xAuthByUser, Principal.compare, caller) else {
      Runtime.trap("Connect your X account first");
    };
    let fresh = await* LibX.ensureFreshToken(clientId, auth);
    if (fresh.access_token != auth.access_token) {
      // Refresh rotated the tokens — persist the new pair.
      Map.add(xAuthByUser, Principal.compare, caller, fresh);
    };
    await* LibX.runCreatePost(LibX.configForToken(fresh.access_token), body);
  };

  public shared ({ caller }) func disconnectMyX() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(xAuthByUser, Principal.compare, caller);
  };
};
```

```motoko filepath=src/backend/lib/x.mo
import { defaultConfig; type Config } "mo:x-client/Config";
import TweetsApi "mo:x-client/Apis/TweetsApi";
import TweetCreateRequest "mo:x-client/Models/TweetCreateRequest";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";

module {
  public type XAuth = {
    access_token : Text;
    refresh_token : Text;
    expires_at : Nat64; // ns absolute (Time.now()-relative)
    scope : [Text];
  };

  // Build a Config bound to a single bearer. `is_replicated = ?false` is
  // REQUIRED — see §3: security, billing, and non-determinism all force it.
  public func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer token;
      is_replicated = ?false;
    };
  };

  public func runCreatePost(config : Config, body : Text) : async* Text {
    // `TweetCreateRequest.init()` returns a record with every optional set
    // to `null` (≥ 0.2.3 only); rebind `text` for the value you want to post.
    let req = { TweetCreateRequest.init() with text = ?body };
    let resp = await* TweetsApi.createPosts(config, req);
    resp.data.id;
  };

  // ------------------------------------------------------------------
  // OAuth 2.0 PKCE flow.  `x-client` ships only the post-token call surface;
  // the OAuth handshake itself uses `ic.http_request` directly. Treat the
  // three functions below as the integration surface — implement them as
  // documented in the X OAuth 2.0 reference and persist the per-caller
  // code_verifier in actor state (a `Map<Principal, Text>` parallel to
  // `xAuthByUser`).
  //
  // See https://developer.x.com/en/docs/authentication/oauth-2-0/authorization-code
  // and the package's `skills/oauth-setup.md` for the full handshake.
  // ------------------------------------------------------------------

  public func startAuthorize(clientId : Text, redirectUri : Text, caller : Principal) : async* Text {
    // 1. Generate a code_verifier (43-128 chars, [A-Za-z0-9-._~]).
    // 2. Persist it under `caller` in a `Map<Principal, Text>` actor field.
    // 3. Compute code_challenge = base64url(sha256(code_verifier)).
    // 4. Return: https://x.com/i/oauth2/authorize
    //              ?response_type=code
    //              &client_id={clientId}
    //              &redirect_uri={redirectUri}
    //              &scope=tweet.read+tweet.write+users.read+offline.access
    //              &state={fresh-csrf-token persisted alongside the verifier}
    //              &code_challenge={challenge}
    //              &code_challenge_method=S256
    let _ = clientId; let _ = redirectUri; let _ = caller;
    Runtime.trap("startAuthorize: implement OAuth 2.0 PKCE handshake (see comment block)");
  };

  public func exchangeCode(clientId : Text, code : Text, redirectUri : Text, caller : Principal) : async* XAuth {
    // POST https://api.x.com/2/oauth2/token (via ic.http_request, is_replicated=false)
    //   Content-Type: application/x-www-form-urlencoded
    //   body: grant_type=authorization_code
    //       & code={code}
    //       & redirect_uri={redirectUri}
    //       & client_id={clientId}
    //       & code_verifier={the verifier persisted in startAuthorize for `caller`}
    // Parse the JSON body, return XAuth { access_token; refresh_token;
    // expires_at = Time.now() + expires_in*1_000_000_000; scope }.
    let _ = clientId; let _ = code; let _ = redirectUri; let _ = caller;
    Runtime.trap("exchangeCode: implement OAuth 2.0 token exchange (see comment block)");
  };

  public func ensureFreshToken(clientId : Text, auth : XAuth) : async* XAuth {
    // If `Time.now() + 60s < auth.expires_at`, return auth unchanged.
    // Otherwise POST https://api.x.com/2/oauth2/token with
    //   grant_type=refresh_token & refresh_token={auth.refresh_token} & client_id={clientId}
    // X *rotates* refresh tokens — the response carries a new `refresh_token`
    // that supersedes the old one. ALWAYS persist the new pair (the
    // calling mixin handles the persist step).
    let _ = clientId;
    Runtime.trap("ensureFreshToken: implement RFC 6749 refresh (see comment block)");
  };
};
```

### Variant-specific invariants (admin Client ID)

- **Admin sets the Client ID, never the access token.** The Client ID
  is a public identifier; the per-user `access_token` is the secret.
  Two completely different storage shapes (`{ var value : ?Text }` vs
  `Map<Principal, XAuth>`) and two completely different gates
  (`#admin` vs "logged in").
- **No `getXClientId` endpoint.** `isXClientIdConfigured : Bool` is
  the only outward-facing read of `xClientId.value`. The frontend
  doesn't need to display the Client ID; it just needs to know whether
  to render the "Connect X" button.
- **`xAuthByUser` is per-caller only.** Same no-getter / no-log /
  no-iterate-outside-caller-scope invariants as `extension-openai`'s
  per-user variant. Concretely: never generate `getMyXAuth`, `getX`,
  `myAccessToken`, or any shared / query function whose return type is
  `?XAuth` / `?Text` / `Text`. A single `console.log` of an X bearer
  is a per-user account compromise.
- **Trap cleanly when missing prerequisites.** Three distinct
  conditions, three distinct messages: `"X is not configured"` (Client
  ID missing → admin task), `"Connect your X account first"` (user not
  yet authorised → frontend should kick off `startXOAuth`),
  `"Sign in to ..."` (anonymous caller → login required).

## 5. Two call shapes — function form vs. suite form

Same as `extension-openai`. Every Apis module ships both:

- **Function form** (used in §4): `TweetsApi.createPosts(config, req)
  : async* T`. Note the `async*` — call sites use `await*`. This is
  the common case for `shared` actor methods.
- **Suite form**: `let api = TweetsApi(config); api.createPosts(req)
  : async T`. Note `async`, not `async*`. Useful when a single
  `shared` method makes several X calls and you want to bind the
  config once.

The two forms are interchangeable; pick whichever reads cleaner. Don't
mix them inside the same `shared` body.

## 6. Available API surface

`x-client@0.2.3` ships a curated subset of the X API v2. The most
relevant module for this skill is `TweetsApi`:

| Module        | Primary entry point | What it does                                            |
| ------------- | ------------------- | ------------------------------------------------------- |
| `TweetsApi`   | `createPosts`       | Post a tweet (`/2/tweets`) — the 95% case for this skill. |
| `TweetsApi`   | `deleteTweetById`   | Delete a tweet (`/2/tweets/{id}`).                      |
| `UsersApi`    | `findMyUser`        | Get the authenticated user's handle/profile.            |

For X *reads* (timeline, search, lookup) the curated surface is much
smaller — `x-client` focuses on writes. Pull data from X via
`extension-http-outcalls` like any other public REST API.

If a build spec needs an X *write* not covered by `x-client@0.2.3`
(e.g. media upload, replies-to-replies semantics, retweet endpoints),
raise an issue on [`caffeinelabs/x-client`](https://github.com/caffeinelabs/x-client) — do not paper over it
with hand-rolled `ic.http_request`.

## 7. Cycles and response sizes

`defaultConfig.cycles = 30_000_000_000` — about 0.04 USD at 4 USD/T
cycles. Sufficient for a typical `createPosts` call. Bump for:

- Long-form tweets (premium subscribers, up to 25 000 chars): set
  `cycles = 60_000_000_000`.
- The OAuth token-exchange call (`/2/oauth2/token`) is small; the
  default cycle budget is generous.

## 8. Things that will bite you

- **`is_replicated = ?false`** — see §3. Not optional.
- **`x-client < 0.2.3`** — older versions emit `"field": null` for
  every absent optional, and `/2/tweets` rejects them with up to 16
  validation errors per request. 0.2.3 ships the `init` constructors
  that default optionals to `null` *in Motoko* and elide them on the
  wire (via `serde-core@^0.1.2`'s `skip_null_fields`).
- **Don't expose the access token.** `xAuthByUser` is read only by
  `Map.get(xAuthByUser, ..., caller)` inside `tweet` /
  `ensureFreshToken`. No `getMyXAuth`, no `getMyAccessToken`, no
  iterator. A leaked bearer is a per-user account compromise.
- **Persist the rotated refresh token.** X returns a new
  `refresh_token` with every refresh (`grant_type=refresh_token`); if
  you keep using the old one, the next refresh will 400. The mixin in
  §4 handles this — the `if (fresh.access_token != auth.access_token)`
  branch persists the new pair.
- **Token expiry** is ~2 hours. If you omit `offline.access` from the
  authorise scopes, you will not get a `refresh_token` and the user
  must re-authorise every time.
- **Callback URI mismatch.** Every character (trailing slash, query
  string, port) must match the URI registered on the Developer Portal.
  X returns a generic `redirect_uri_mismatch` error otherwise.
- **Don't roll your own JSON.** `x-client` already handles the
  request/response JSON via `JSON.toCandid` / `JSON.fromCandid` and
  `serde-core`'s null-elision.
- **No `getApiKey`-style endpoint, ever.** Same rule as
  `extension-openai`'s per-user variant: every shared / query function
  that returns `?XAuth`, `?Text` (the access token), or any prefix of
  the bearer is a leak.
- **Rate limits.** `/2/tweets` is capped per-user-per-app. Replicated
  outcalls would multiply RPM by the subnet size — yet another reason
  for `is_replicated = ?false`. Back off on HTTP 429.
- **Frontend never holds tokens.** The React app calls the backend
  `tweet(body)` and the backend mediates everything. The OAuth flow
  itself uses **redirect-and-back** through `x.com` — the frontend
  starts the flow via `startXOAuth(redirectUri)` and finishes via
  `completeXOAuth(code, redirectUri)`; the tokens never reach the
  browser.

## 9. Variant: per-user Client ID

Use this variant when each end-user must bring their own X Developer
App (multi-tenant rate-limit isolation, per-user Developer Portal
control). Mechanically the Client ID storage flips from a single
`{ var value : ?Text }` (admin-set) to a `Map<Principal, Text>`
(per-user); the OAuth + posting mixin from §4 reuses unchanged
modulo the Client ID lookup.

The actor keeps the same shape — drop the admin-Client-ID mixin,
add a per-user-Client-ID one:

```motoko filepath=src/backend/per-user-clientid-main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinXClientIdPerUser "mixins/x-clientid-per-user";
import MixinXPostingPerUserClientId "mixins/x-posting-per-user-clientid";
import LibX "lib/x";

actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState);

  // Per-user X Developer App Client IDs.
  let xClientIdByUser : Map.Map<Principal, Text> = Map.empty();
  include MixinXClientIdPerUser(xClientIdByUser);

  // Per-user OAuth tokens — same shape as §4.
  let xAuthByUser : Map.Map<Principal, LibX.XAuth> = Map.empty();
  include MixinXPostingPerUserClientId(xClientIdByUser, xAuthByUser);
};
```

The two mixin files are mechanical adaptations of §4's:

- `mixins/x-clientid-per-user.mo` swaps the admin gate for a
  signed-in-caller gate: `setMyXClientId(id) : async ()` writes the
  caller's slot of `xClientIdByUser`; `isMyXClientIdConfigured` reads
  the same slot.
- `mixins/x-posting-per-user-clientid.mo` looks up the Client ID by
  `caller` instead of reading the single `{ var value : ?Text }` —
  every other line is identical to `mixins/x-posting.mo` from §4.

Same no-getter rule: there is no `getMyXClientId` endpoint, even
though the Client ID is technically public — keeping the boundary
consistent with the access-token rule trains the agent not to grep
the codebase for "key" / "id" and add a getter.

## 10. Variant: fallback (admin default + per-user override)

Use this when the operator wants to provide a no-config path for
casual users while letting power users self-register. The admin sets
a canister-wide default Client ID; individual users may override it
with their own.

Lookup order at OAuth start time:

```motoko
func clientIdFor(caller : Principal) : ?Text = switch (Map.get(xClientIdByUser, Principal.compare, caller)) {
  case (?id) ?id;
  case null adminClientId.value; // may itself be null → caller must provide one
};
```

Ship both mixins from §4 and §10 in the same actor: admin sets the
default via `setXClientId`, users override via `setMyXClientId`.
`startXOAuth` calls `clientIdFor(caller)` instead of reading the
single slot. Everything else (`xAuthByUser`, the OAuth handshake, the
posting endpoint) is unchanged.

# Frontend

Surfaces every build that uses this skill must ship:

1. **A login flow — required for every variant.** X cannot work
   without a non-anonymous caller; the per-user OAuth handshake stores
   tokens keyed by `caller : Principal`, and the admin / per-user
   Client ID setters all gate on a logged-in caller. The login flow
   itself comes from [`extension-authorization`](../extension-authorization/SKILL.md):
   `useInternetIdentity`, the login/logout buttons, the `useActor`
   plumbing that injects the authenticated identity into every
   backend call. Plan a sign-in screen as part of the same task graph
   if the build doesn't already have one.

2. **A Client ID configuration surface.** Variant-specific:
   - Admin variant (§4 default): an admin-gated `/settings/x` page
     with a single password-input bound to `setXClientId(id)`.
   - Per-user variant (§9): a personal `/settings/x` page reachable
     to any signed-in user, bound to `setMyXClientId(id)`.
   - Fallback variant (§10): both pages — admin-gated for the default
     and per-user for the override.

3. **A "Connect X" page — always.** A per-user, *not* admin-gated
   page that runs the OAuth 2.0 PKCE handshake: kicks off via
   `startXOAuth(redirectUri)`, redirects the browser to X for
   consent, lands back on the same page with `?code=...`, calls
   `completeXOAuth(code, redirectUri)` to exchange the code for
   tokens. End-state is "X connected as @handle" or "Connect X"
   depending on `isMyXConnected()`.

Pick the UI shape that matches the backend variant. **Default to
Variant A (admin Client ID + per-user OAuth)** unless the spec
explicitly chooses per-user (§9) or fallback (§10).

## Variant A: admin Client ID + per-user OAuth (matches §4 — default)

Two pages:

1. **Admin settings page** — `/settings/x` (admin-gated):
   - Password-input bound to `setXClientId(id)`. Submit on enter;
     clear the input on success.
   - Status indicator driven by `isXClientIdConfigured()` (returns
     `Bool`). Show "Configured" / "Not configured" — never display
     the Client ID itself, never expose a getter that returns it.
   - Hide from non-admins via [`extension-authorization`](../extension-authorization/SKILL.md)'s
     `isCallerAdmin` query — non-admins should not see the link in
     the nav, let alone the page. Bind admin-only routes through
     your router's guard pattern.

2. **Connect X page** — `/connect/x` (any signed-in user):
   - "Connect X" button bound to `startXOAuth(window.location.origin
     + '/connect/x')`. The button redirects the browser to the URL
     returned by the canister.
   - On the return leg, parse `?code=...&state=...` from the URL,
     call `completeXOAuth(code, redirectUri)` (same `redirectUri`
     that was passed to `startXOAuth`), then redirect to wherever the
     user came from (or home).
   - Status driven by `isMyXConnected()` (returns `Bool`). Show
     "Connected as @…" (the handle is *not* fetched from the
     bearer — fetch it separately via a `getMyXHandle` endpoint that
     calls `UsersApi.findMyUser`, never decode the bearer in JS).
   - Optional "Disconnect X" button bound to `disconnectMyX()`.

3. **Empty-state nudge on the post-tweet UI** — when
   `isMyXConnected()` is `false`, render an inline "Connect X to
   post" link to `/connect/x`. Without this nudge users hit "Connect
   your X account first" with no obvious next step.

Suggested route layout:

```
/                   →  Main UI (any signed-in user; empty-state when no X connection)
/settings/x         →  Admin Client ID config (admin-only)
/connect/x          →  Per-user OAuth handshake (any signed-in user)
```

## Variant B: per-user Client ID (matches §9)

Two pages, both reachable to any signed-in user:

1. **My X settings page** — `/settings/x`:
   - Password-input bound to `setMyXClientId(id)`. Same no-display
     invariant.
   - Status driven by `isMyXClientIdConfigured()`.
   - No router guard beyond "logged in".

2. **Connect X page** — same as Variant A's `/connect/x`, except
   `startXOAuth` uses the user's own Client ID under the hood.
   The user must configure their Client ID *before* connecting.

Suggested route layout:

```
/                   →  Main UI
/settings/x         →  Personal Client ID (any signed-in user)
/connect/x          →  Per-user OAuth handshake
```

## Variant C: fallback (matches §10)

Three pages:

- `/admin/settings/x` (admin-gated) — `setXClientId` for the
  canister-wide default.
- `/settings/x` (any signed-in user) — `setMyXClientId` for the
  per-user override.
- `/connect/x` (any signed-in user) — same OAuth handshake as
  Variants A/B, with the lookup order described in §10.

The "Connect X" button stays disabled until *some* Client ID is
resolvable for the caller (admin default OR per-user override).

## Common to all variants

- **Sign-in is required** for every X-related route. Wire the
  `/settings/...` and `/connect/x` routes through
  [`extension-authorization`](../extension-authorization/SKILL.md)'s
  auth guard (`useInternetIdentity` + a redirect when
  `!isAuthenticated`); anonymous callers must hit a "please sign in"
  wall before any backend call fires, otherwise every endpoint traps
  with "Sign in to ...".
- **The frontend never persists tokens.** No `localStorage`,
  no `IndexedDB`, no cookies — the canister mediates everything.
  The browser only ever sees `Bool` status flags
  (`isMyXConnected`, `isXClientIdConfigured`) and the OAuth
  redirect URLs.
- **The OAuth `state` parameter is the canister's responsibility.**
  Generate it server-side in `startXOAuth`, persist it alongside the
  `code_verifier`, verify it in `completeXOAuth` before exchanging
  the code. Do not let the frontend mint or echo `state` — that
  defeats CSRF protection.
- **The post-tweet UI itself is trivial:** a textarea, a submit
  button, a list of recent tweets bound to whatever `tweet` /
  history endpoints the canister exposes. No client-side X SDK, no
  token handling, no JSON serialisation logic — the canister is
  the X client.

## Related

- [`mops add x-client@0.2.3`](https://mops.one/x-client) — connector source.
- [`caffeinelabs/x-client`](https://github.com/caffeinelabs/x-client) — generated bindings repo. Its `skills/oauth-setup.md` carries the authoritative step-by-step Developer Portal walkthrough; its `skills/tweeting-fine-points.md` documents operational gotchas (minimum version, scopes, replication, null-field serialisation, sub-object rules).
- [X Developer Portal](https://developer.x.com/en/portal/dashboard) — where the Client ID is created.
- [OAuth 2.0 Authorization Code with PKCE (X docs)](https://developer.x.com/en/docs/authentication/oauth-2-0/authorization-code) — canonical authorise/token endpoint details.
- [`/2/tweets` API reference](https://developer.x.com/en/docs/x-api/tweets/manage-tweets/api-reference/post-tweets) — what `createPosts` actually hits.
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE spec.
- [extension-authorization](../extension-authorization/SKILL.md) — **required prerequisite for every variant of this skill**. Provides the Internet Identity login flow, the `useInternetIdentity` / `useActor` frontend plumbing, and the `#admin` role gate for variants §4 and §11.
- [extension-http-outcalls](../extension-http-outcalls/SKILL.md) — sibling skill for general HTTP outcalls, including X *reads* (timeline, search, lookup) which this skill does NOT cover.
