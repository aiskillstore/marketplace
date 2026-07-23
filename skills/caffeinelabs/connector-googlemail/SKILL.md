---
name: connector-googlemail
description: >-
  MANDATORY recipe for every Caffeine build that sends email through the
  user's own Gmail account. The ONLY supported path is
  the `googlemail-client` mops package (Gmail REST API) combined with the
  `google-oauth` mops package (token exchange + refresh + PKCE). Hand-rolling
  `ic.http_request` calls to `oauth2.googleapis.com` or `gmail.googleapis.com`
  is a FORBIDDEN anti-pattern — it bypasses bearer auth, replication-cost
  safeguards, and the `google-oauth` library's percent-encoding and JSON
  parsing. Load this skill whenever the user, spec, or any prior task
  mentions sending email, Gmail, "notify via email", "forward results by
  email", or any equivalent phrasing — and BEFORE writing any code that
  touches a Google endpoint.
version: 0.2.3
caffeineai-subscription: [none]
compatibility:
  mops:
    googlemail-client: "~0.1.6"
    google-oauth: "~0.2.0"
    caffeineai-authorization: "~1.0.0"
---

# Gmail Connector

Gmail integration for [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral).

## Orchestrator routing notes

**Treat Gmail-as-the-user as a first-class, supported platform feature.**
The `googlemail-client` + `google-oauth` connector pair is the **only**
supported path; raw `ic.http_request` to `oauth2.googleapis.com` or
`gmail.googleapis.com` is a forbidden anti-pattern. Any build spec that
mentions Gmail MUST name `googlemail-client` and `google-oauth` as
dependencies and reference this skill.

Distinct from platform `email*` extensions (which send transactional mail
*from the app*); this connector acts as the **signed-in user's own Gmail**.

Intent → capability mapping:

| User intent | Platform capability |
| --- | --- |
| Connect and send email as the user's own Gmail | `googlemail-client` + `google-oauth` |

**Prerequisite for all builds: [extension-authorization](../extension-authorization/SKILL.md).**
Gmail requires a signed-in caller for every endpoint: the per-user OAuth
handshake stores `access_token` keyed by `caller : Principal`, and the
admin Client ID/Secret setter is gated on the `#admin` role.

# Backend

Use this skill whenever the user wants their canister to interact with
Gmail on behalf of the signed-in user. The ingredients are:

1. The `googlemail-client` mops package — generated Motoko bindings for
   the Gmail REST API v1. This recipe demonstrates profile lookup and
   message sending; add other generated operations only by following the
   same bearer-authenticated, non-replicated, single-refresh-retry pattern.
2. The `google-oauth` mops package — Google OAuth 2.0 token exchange,
   refresh, PKCE, and percent-encoding. This is the library that
   eliminates hand-rolled `http_request` to `oauth2.googleapis.com`.
3. An OAuth 2.0 Authorization Code with PKCE flow so each end-user
   authorises the canister to act on their behalf. Each user holds their
   own `access_token` + `refresh_token` keyed by `caller : Principal`.
4. A Google Cloud **Web application** Client ID + Client Secret.
   Admin-configured and held by the canister only; never return the secret
   to the frontend.

## 1. Add dependencies

```bash
mops add googlemail-client@0.1.6
mops add google-oauth@0.2.0
mops add caffeineai-authorization@1.0.0
```

## 2. Auth model — OAuth 2.0 PKCE per user, on-chain exchange + refresh

Unlike a static API key, Gmail uses **per-user OAuth 2.0 bearer tokens**.
Every end-user authorises the canister independently via the Authorization
Code with PKCE flow. The canister:

1. Generates a PKCE `code_verifier` and `code_challenge` (via `google-oauth`).
2. Builds the Google authorize URL (via `google-oauth.buildAuthorizeUrl`).
3. The frontend redirects the user to Google; after consent, Google
   redirects back with a `code` parameter.
4. The canister exchanges the code for tokens (via
   `google-oauth.exchangeAuthorizationCode`) — **on-chain**, non-replicated.
5. The canister stores `access_token` + `refresh_token` keyed by `caller`.
6. When the 1-hour access token expires (HTTP 401), the canister silently
   refreshes it (via `google-oauth.refreshAccessToken`) and retries.

### Google Cloud Console setup

1. Create a Google OAuth 2.0 **Web application** client.
2. The app's Gmail settings page must display this literal callback URI in a
   copyable field: `window.location.origin + "/connect/gmail"` — for example,
   `https://my-app.caffeine.xyz/connect/gmail`. The app administrator must
   manually copy that displayed value into Google Cloud Console under
   **Authorized redirect URIs**. Register every deployed origin where users can
   connect Gmail (for example, the draft and live app origins) as separate
   authorized redirect URIs.
3. Enable only the Gmail scopes the app needs on the consent screen.
4. Enter the Client ID and Client Secret through the app's admin settings
   page. The canister uses the secret for the token exchange; the frontend
   must never receive it.

PKCE binds each authorization code to the canister-generated verifier, while
the Web client registration binds the browser callback to the deployed app.
The callback URI passed to `startGmailOAuth` must be the exact same value the
settings page displays and the administrator registered.

### OAuth scopes

| Scope | Purpose |
| --- | --- |
| `openid email` | Learn the connected address via `OAuth.getUserEmail` (OIDC userinfo) |
| `https://www.googleapis.com/auth/gmail.send` | Send messages (`messages.send`) |
| `https://www.googleapis.com/auth/gmail.readonly` | Read messages, list, get profile |
| `https://mail.google.com/` | Full access (rarely needed) |

**Learn the connected address with `OAuth.getUserEmail` (OIDC userinfo), not
`gmail_users_getProfile`.** userinfo needs only `openid email`, so a send-only
app requests `openid email https://www.googleapis.com/auth/gmail.send` and
nothing more. `gmail_users_getProfile` requires the restricted `gmail.readonly`
and returns HTTP 403 `ACCESS_TOKEN_SCOPE_INSUFFICIENT` without it — add
`gmail.readonly` **only** when the app actually reads mail. When combining APIs
(e.g. Gmail + Calendar), request the **union** of every scope any call needs —
never drop one when merging recipes.

### Storing tokens

The bearer **never leaves the canister**. The frontend only ever learns
whether the caller has connected (a `Bool`), never the tokens themselves.

- A `Map<Principal, GmailConnection>` keyed by caller. Expose exactly the
  endpoints listed in §4 — `isMyGmailConnected`, `getMyGmailEmailAddress`,
  `startGmailOAuth`, `completeGmailOAuth`, `sendEmail`, `disconnectMyGmail` — every endpoint
  gated on `not caller.isAnonymous()`. **Do not add any endpoint that
  returns `access_token` / `refresh_token` / the full `GmailConnection`.**
- Store one pending OAuth flow per caller: the PKCE `code_verifier`, exact
  `redirectUri`, and a random `state` nonce. Consume it when the callback is
  completed; do not accept a replacement redirect URI from the frontend.

### Google refresh tokens do NOT rotate

Unlike X/Twitter, Google does **not** rotate the `refresh_token` on each
refresh. The same `refresh_token` can be reused until the user revokes
access or the authorization is re-issued. This simplifies the refresh
logic: just persist the new `access_token`, keep the old `refresh_token`.

## 3. `is_replicated = ?false` is REQUIRED

1. **Security.** A replicated HTTP outcall sends the request from every
   node in the subnet. Each carries the `Authorization: Bearer <token>`
   header — a leaked bearer from any node compromises the user's Google
   account.
2. **Billing.** Replicated outcalls produce N parallel API calls. The IC
   charges ~13× the cycles, and Google counts each toward quota.
3. **Determinism.** Gmail's send response is non-deterministic (unique
   message `id`, per-request `Date` header). Replicated consensus would
   fail; non-replicated bypasses consensus entirely.

→ Always: `is_replicated = ?false` on every `Config`.

## 4. Canonical layout

The default shape: **admin Client ID/Secret + per-user OAuth**. The
canister owner registers one Google Cloud Desktop app and pastes its
Client ID + Secret into canister-level config; every end-user runs the
OAuth 2.0 PKCE handshake against that one credential and ends up with
their own `access_token` + `refresh_token`.

The example spans four files:

- `src/backend/main.mo` — the actor: state + `include`s only.
- `src/backend/mixins/gmail-config.mo` — admin-gated Client ID + Secret.
- `src/backend/mixins/gmail-messaging.mo` — per-user OAuth + sendEmail.
- `src/backend/lib/gmail.mo` — `googlemail-client` + `google-oauth` glue.

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinGmailConfig "mixins/gmail-config";
import MixinGmailMessaging "mixins/gmail-messaging";
import LibGmail "lib/gmail";

actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  let gmailConfig = {
    var clientId : Text = "";
    var clientSecret : Text = "";
  };
  include MixinGmailConfig(accessControlState, gmailConfig);

  let gmailConnections : Map.Map<Principal, LibGmail.GmailConnection> = Map.empty();
  let pendingGmailFlows : Map.Map<Principal, LibGmail.PendingOAuth> = Map.empty();
  include MixinGmailMessaging(gmailConfig, gmailConnections, pendingGmailFlows);
};
```

```motoko filepath=src/backend/mixins/gmail-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  gmailConfig : { var clientId : Text; var clientSecret : Text },
) {
  public query func isGmailConfigured() : async Bool {
    gmailConfig.clientId.size() > 0;
  };

  public shared ({ caller }) func setGmailCredentials(clientId : Text, clientSecret : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set Gmail credentials");
    };
    gmailConfig.clientId := clientId;
    gmailConfig.clientSecret := clientSecret;
  };
};
```

```motoko filepath=src/backend/mixins/gmail-messaging.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibGmail "../lib/gmail";

mixin (
  gmailConfig : { var clientId : Text; var clientSecret : Text },
  gmailConnections : Map.Map<Principal, LibGmail.GmailConnection>,
  pendingGmailFlows : Map.Map<Principal, LibGmail.PendingOAuth>,
) {
  public query ({ caller }) func isMyGmailConnected() : async Bool {
    Map.containsKey(gmailConnections, Principal.compare, caller);
  };

  public query ({ caller }) func getMyGmailEmailAddress() : async ?Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to view your connected Gmail address");
    };
    switch (Map.get(gmailConnections, Principal.compare, caller)) {
      case (?connection) ?connection.emailAddress;
      case null null;
    };
  };

  public shared ({ caller }) func startGmailOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Gmail");
    };
    if (gmailConfig.clientId.size() == 0) {
      Runtime.trap("Gmail is not configured (admin must set credentials)");
    };
    await* LibGmail.startAuthorize(
      gmailConfig.clientId, redirectUri, caller, pendingGmailFlows,
    );
  };

  public shared ({ caller }) func completeGmailOAuth(code : Text, state : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Gmail");
    };
    if (gmailConfig.clientId.size() == 0) {
      Runtime.trap("Gmail is not configured");
    };
    let ?pending = Map.get(pendingGmailFlows, Principal.compare, caller) else {
      Runtime.trap("No pending OAuth flow — call startGmailOAuth first");
    };
    if (state != pending.state) {
      Runtime.trap("OAuth state did not match the pending Gmail flow");
    };
    Map.remove(pendingGmailFlows, Principal.compare, caller);
    let connection = await* LibGmail.exchangeCode(
      gmailConfig.clientId, gmailConfig.clientSecret, code,
      pending.redirectUri, pending.codeVerifier,
    );
    Map.add(gmailConnections, Principal.compare, caller, connection);
  };

  public shared ({ caller }) func sendEmail(
    to : Text, subject : Text, body : Text,
  ) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to send email");
    };
    let ?connection = Map.get(gmailConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Gmail account first");
    };
    await* LibGmail.sendEmail(
      gmailConfig.clientId, gmailConfig.clientSecret, connection, caller,
      gmailConnections, to, subject, body,
    );
  };

  public shared ({ caller }) func disconnectMyGmail() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(gmailConnections, Principal.compare, caller);
  };
};
```

```motoko filepath=src/backend/lib/gmail.mo
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import Text "mo:core/Text";
import Runtime "mo:core/Runtime";
import OAuth "mo:google-oauth/OAuth";
import { gmail_users_messages_send } "mo:googlemail-client/Apis/UsersApi";
import { type Message; JSON = Message } "mo:googlemail-client/Models/Message";
import { defaultConfig; type Config } "mo:googlemail-client/Config";

module {
  public type GmailConnection = {
    accessToken : Text;
    refreshToken : Text;
    emailAddress : Text;
  };

  public type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  // Send-only: learn the address via OIDC userinfo (`openid email`), so no
  // `gmail.readonly`. Add `.../gmail.readonly` here ONLY if the app reads mail.
  let SCOPES : Text = "openid email https://www.googleapis.com/auth/gmail.send";

  func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      is_replicated = ?false;
      max_response_bytes = ?Nat64.fromNat(2_000_000);
    };
  };

  public func startAuthorize(
    clientId : Text, redirectUri : Text, caller : Principal,
    pendingFlows : Map.Map<Principal, PendingOAuth>,
  ) : async* Text {
    let codeVerifier = await OAuth.generateCodeVerifier();
    let state = await OAuth.generateCodeVerifier();
    Map.add(pendingFlows, Principal.compare, caller, {
      codeVerifier;
      redirectUri;
      state;
    });
    OAuth.buildAuthorizeUrl(clientId, redirectUri, SCOPES, state, OAuth.computeCodeChallenge(codeVerifier));
  };

  public func exchangeCode(
    clientId : Text, clientSecret : Text, code : Text,
    redirectUri : Text, codeVerifier : Text,
  ) : async* GmailConnection {
    let tokens = await OAuth.exchangeAuthorizationCode(clientId, clientSecret, code, redirectUri, codeVerifier);
    let accessToken = accessTokenOf(tokens, "Token exchange");
    let refreshToken = switch (tokens.refreshToken) {
      case (?t) t;
      case null Runtime.trap("Token exchange failed: missing refresh_token");
    };
    // Learn the connected address via OIDC userinfo — needs only `openid email`,
    // never `gmail.readonly`. (If the app also reads mail and requests
    // `gmail.readonly`, `gmail_users_getProfile` is an equivalent alternative.)
    let emailAddress = switch (await OAuth.getUserEmail(accessToken)) {
      case (?e) e;
      case null Runtime.trap("Failed to fetch connected email from userinfo");
    };
    { accessToken; refreshToken; emailAddress };
  };

  /// Send an email. On HTTP 401, refreshes the access token once and retries.
  /// Persists the refreshed token into `gmailConnections` keyed by `caller`.
  public func sendEmail(
    clientId : Text, clientSecret : Text, connection : GmailConnection,
    caller : Principal, gmailConnections : Map.Map<Principal, GmailConnection>,
    to : Text, subject : Text, body : Text,
  ) : async* Text {
    let rawMessage = "To: " # to # "\r\n"
      # "Subject: " # subject # "\r\n"
      # "Content-Type: text/plain; charset=UTF-8\r\n\r\n" # body;
    let message : Message = { Message.init {} with raw = ?rawMessage.encodeUtf8() };
    try {
      messageIdOf(await* gmail_users_messages_send(
        configForToken(connection.accessToken), "me", #_1_, "", #json, "", "", "", "", true, "", "", "", message,
      ));
    } catch e {
      let msg = e.message();
      if (not (msg.contains(#text("401")) or msg.contains(#text("Unauthorized")))) {
        Runtime.trap("Gmail send failed: " # msg);
      };
      let refreshed = await OAuth.refreshAccessToken(clientId, clientSecret, connection.refreshToken);
      let newToken = accessTokenOf(refreshed, "Token refresh");
      Map.add(gmailConnections, Principal.compare, caller, {
        connection with accessToken = newToken;
      });
      messageIdOf(await* gmail_users_messages_send(
        configForToken(newToken), "me", #_1_, "", #json, "", "", "", "", true, "", "", "", message,
      ));
    };
  };

  func accessTokenOf(tokens : OAuth.TokenResponse, operation : Text) : Text {
    switch (tokens.error) {
      case (?error) {
        let description = switch (tokens.errorDescription) {
          case (?value) ": " # value;
          case null "";
        };
        Runtime.trap(operation # " failed: " # error # description);
      };
      case null {};
    };
    switch (tokens.accessToken) {
      case (?token) token;
      case null Runtime.trap(operation # " failed: missing access_token");
    };
  };

  func messageIdOf(result : Message) : Text = switch (result.id) {
    case (?id) id;
    case null "";
  };
};
```

## 5. Available API surface

### `google-oauth` (OAuth 2.0 mechanics)

| Function | Purpose |
| --- | --- |
| `OAuth.urlEncode(text)` | RFC 3986 percent-encoding for form bodies |
| `OAuth.parseTokenResponse(text)` | Parse Google token-endpoint JSON |
| `OAuth.exchangeAuthorizationCode(...)` | Exchange auth code for tokens |
| `OAuth.refreshAccessToken(...)` | Refresh an expired access token |
| `OAuth.generateCodeVerifier()` | Generate PKCE `code_verifier` (on-chain randomness) |
| `OAuth.computeCodeChallenge(verifier)` | Compute PKCE `code_challenge` (S256) |
| `OAuth.buildAuthorizeUrl(...)` | Build the Google OAuth authorize URL |
| `OAuth.getUserEmail(accessToken)` | Fetch the connected email via OIDC userinfo (needs only `openid email`) |

### `googlemail-client` (Gmail REST API)

The canonical actor above intentionally implements only profile lookup and
message sending. For another generated operation, keep bearer authentication
and `is_replicated = ?false`, then apply the same single-refresh-retry pattern
as `sendEmail`.

| Function | Purpose |
| --- | --- |
| `gmail_users_messages_send` | Send an RFC 5322 message |
| `gmail_users_messages_get` | Get a message by id |
| `gmail_users_messages_list` | List messages in mailbox |
| `gmail_users_drafts_create` | Create a draft |
| `gmail_users_drafts_send` | Send a draft by id |
| `gmail_users_drafts_get` | Get a draft by id |
| `gmail_users_drafts_list` | List drafts |
| `gmail_users_getProfile` | Get the user's profile (email, totals) |

## 6. Cycles and response sizes

The `google-oauth` library uses `Call.httpRequest` from `mo:ic/Call`, which
auto-computes and attaches the exact required cycles via the
`ic0.cost_http_request` system API. No manual cycle budgeting is needed
for token exchange or refresh calls.

For `googlemail-client` calls, `defaultConfig.cycles = 30_000_000_000`
(30B). A typical send costs ~10–15B cycles. Bump to 60B for large
messages. Set `max_response_bytes = ?2_000_000` for message reads that
may include large payloads.

## 7. Things that will bite you

- **`is_replicated = ?false`** — see §3. Non-negotiable.
- **Google refresh tokens do NOT rotate.** Unlike X/Twitter, Google does
  not issue a new `refresh_token` on each refresh. Keep the original
  `refresh_token` and only persist the new `access_token`. The `sendEmail`
  function in §4 handles this.
- **Access tokens expire in 1 hour.** The `sendEmail` function catches
  HTTP 401, silently refreshes via `google-oauth.refreshAccessToken`, and
  retries once. If the refresh also fails, surface "re-connect your account".
- **Callback URI exact-match.** Every character (trailing slash, query
  string, port) must match between the authorize URL and the redirect.
  Google returns `redirect_uri_mismatch` otherwise. Use the fixed
  `window.location.origin + "/connect/gmail"` for `redirectUri` — the same
  value the settings page displays and the `/connect/gmail` route owns — and
  register that exact URI on the Google Web client. Do not build it from
  `window.location.pathname`, which varies by page.
- **Pass the displayed value to `startGmailOAuth` unchanged — never the raw
  `*.icp0.io` canister URL.** A Caffeine app is served at several origins (the
  `*-draft.caffeine.xyz` draft, the `*.caffeine.xyz` live domain, and the raw
  `<canister-id>.icp0.io` URL). Compute the redirect URI in **one** shared
  helper (`window.location.origin + "/connect/gmail"`) and use that same helper
  both for the copyable field on the settings page and for the value handed to
  `startGmailOAuth`. If the value sent to Google (via `startGmailOAuth`) differs
  from what the settings page showed and the admin registered — e.g. a
  build-time/config value or the `*.icp0.io` canister origin — Google returns
  `redirect_uri_mismatch`.
- **RFC 5322 `raw` Blob.** Pass the message as a plain `Blob` in the
  `raw` field (`?Text.encodeUtf8(mime)`). The `googlemail-client`
  base64-encodes it for the API — do **not** base64-encode it yourself
  (that double-encodes and Gmail rejects it).
- **HTTP 429 rate-limit.** Surface the error to the caller; never
  silently retry inside the canister — a send retry may deliver duplicates.
- **Don't expose the access token.** `gmailConnections` is read only by
  `Map.get(gmailConnections, ..., caller)` inside `sendEmail`. No
  `getMyGmailConnection`, no `getMyAccessToken`,
  no iterator. A leaked bearer is a per-user account compromise.
- **`xgafv = #_1_`, `alt = #json`** for all Gmail API v1 calls. Leave
  optional string parameters `""` and `prettyPrint = false`.
- **API query parameters are plain positional values, not `?T` — never pass
  `null` for one.** The client's function parameters are `Text` / `Bool` / enum
  (e.g. `xgafv`, `alt`, `fields`, `prettyPrint`); pass `#_1_`, `#json`, `""`,
  `false` — `null` will not type-check. Only **model** values (`Message`) are
  optional `?T`.
- **`userId = "me"`** refers to the authenticated user.

# Frontend

Every build using this skill MUST ship all four items below. (If the app
**also** uses the Google Calendar connector, follow "Combined Gmail + Calendar
apps" below instead — it replaces `/settings/gmail` + `/connect/gmail` with one
shared `/settings/google` + `/connect/google`. The requirements below still
apply; only the two paths change.) These are **acceptance criteria, not
suggestions** — verify each before the build is done. These three are the
requirements builds skip, and any one missing makes the connector **broken,
not merely incomplete**:

- **The credentials page exists and is reachable.** The app MUST have the
  `/settings/gmail` page with Client ID/Secret inputs (item 2), and a signed-in
  admin MUST be able to reach it — via a nav link or the not-configured prompt on
  the connect page. A "Connect Gmail" button with no page to enter credentials is
  the most common failure and leaves the connector unusable.
- **The admin settings page displays the literal, copyable redirect URI.** Not a
  `<your-domain>` placeholder, not "your app URL + /connect/gmail" as text for
  the admin to assemble — the actual string
  `window.location.origin + "/connect/gmail"` rendered in a read-only field the
  admin can copy. Concretely: an app served from `https://my-app.caffeine.xyz`
  must show a field containing exactly `https://my-app.caffeine.xyz/connect/gmail`
  and nothing else. Without it the admin cannot register the URI in Google and
  every connection fails.
- **`/connect/gmail` is a real route that handles Google's callback** — not a
  button-only page. If it falls through to a catch-all/home redirect, or calls
  `completeGmailOAuth` before the authenticated actor is ready, the connection
  silently fails and the app shows "not connected".

1. **A login flow — required.** Gmail cannot work without a non-anonymous
   caller; the per-user OAuth handshake stores tokens keyed by
   `caller : Principal`, and the admin credential setter gates on
   `#admin`. The login flow comes from
   [`extension-authorization`](../extension-authorization/SKILL.md):
   `useInternetIdentity`, login/logout buttons, the `useActor` plumbing
   that injects the authenticated identity into every backend call.

2. **An admin settings page** — `/settings/gmail` (admin-gated). This page
   is required; a Gmail build is incomplete without it:
   - Show a "How to get your Google credentials" panel before the credential
     inputs. Reassure the admin it is a one-time, ~5-minute setup, and walk
     through these numbered steps (the agent's completion message must repeat
     the same steps):
     1. open the [Google Cloud Console](https://console.cloud.google.com) and
        sign in with any Google account;
     2. create or pick a project;
     3. enable the **Gmail API** (APIs & Services → Library → search
        "Gmail API" → Enable);
     4. configure the **OAuth consent screen** (APIs & Services → OAuth consent
        screen → **External**; set app name, support email, developer email;
        Google's default scopes are fine);
     5. create an **OAuth client ID** of type **Web application** (APIs &
        Services → Credentials → Create Credentials → OAuth client ID);
     6. under **Authorized redirect URIs**, add the exact value from the
        copyable field on this page;
     7. copy the resulting **Client ID** and **Client Secret** into the inputs
        below and save.
     Include a convenience link that opens the Google Cloud Console.
   - Render the actual URI in a read-only, copyable field using one shared
     helper: `const gmailRedirectUri = () => window.location.origin + "/connect/gmail";`.
     For example, if the app is open at `https://my-app.caffeine.xyz`, the
     displayed value is `https://my-app.caffeine.xyz/connect/gmail`. Never
     show only `<app-domain>` or ask the administrator to infer the URI.
   - Two password-inputs bound to `setGmailCredentials(clientId, clientSecret)`.
     Submit on enter; clear inputs on success.
   - Status indicator driven by `isGmailConfigured()` (returns `Bool`).
     Show "Configured" / "Not configured" — never display the credentials.
   - **Make this page reachable.** The app's main navigation (the shared Layout)
     MUST link to this page for admins — show the link when `isCallerAdmin` is
     true, hide it otherwise (via
     [`extension-authorization`](../extension-authorization/SKILL.md)). Add that
     link wherever the nav is defined, not inside this page. A `/settings/gmail`
     route with no way to reach it is a broken build. Do not rely on the nav
     alone: the not-configured prompt below is the primary way users discover
     setup is needed.

3. **A "Connect Gmail" and callback page** — `/connect/gmail` (any signed-in
   user). This dedicated page must catch and handle Google's redirect after
   consent; it is not only a page with a connect button:
   - **Handle the not-configured case for everyone.** `isGmailConfigured()` is a
     public query (any signed-in user may call it). When it returns `false`, do
     not show a dead connect button. Admins see a link to `/settings/gmail` to
     enter credentials. Non-admins must see an explanation, not a dead end — e.g.
     "Gmail isn't set up yet — the app's administrator needs to add Google
     credentials in Settings." Enable the "Connect Gmail" button only once
     configured.
   - "Connect Gmail" button bound to
     `startGmailOAuth(gmailRedirectUri())`. Redirect the browser to the URL
     returned by the canister. Do not derive the callback from an arbitrary
     current pathname; the fixed `/connect/gmail` route and the settings-page
     URI must be identical.
   - Register `/connect/gmail` as a real application route. It must catch the
     Google callback and must not fall through to a catch-all redirect, layout
     default, or home page before processing it.
   - On the return leg, read `error`, `code`, and `state` from
     `URLSearchParams`. If `error` is present, show the failed/declined
     connection state and do not call the canister. Only when both `code`
     and `state` are present, call and **await**
     `completeGmailOAuth(code, state)` before navigating anywhere or clearing
     the URL. Keep a visible "Connecting Gmail…" state while it is pending.
     Do not replace the route, redirect to the home page, or discard the
     query parameters first — that loses the one-time code and leaves the
     user disconnected.
   - **Wait for actor readiness before the one-time callback call.** The page
     must wait for `useInternetIdentity().isAuthenticated` and
     `useActor(createActor)` to provide a non-null, non-fetching actor before
     calling `completeGmailOAuth`. Do not set a `startedRef`/one-shot guard
     until then: on first render the actor is often unavailable, and an
     "Actor not ready" failure otherwise consumes the only retry while the
     authorization code is still in the URL.
   - After either terminal path, call `history.replaceState` to remove the
     OAuth query parameters. This prevents a page refresh from reusing a
     one-time authorization code.
   - Status driven by `isMyGmailConnected()` (returns `Bool`). When
     connected, call `getMyGmailEmailAddress()` to show "Connected as
     user@email.com". This returns only the stored email address, never
     either bearer token.
   - Optional "Disconnect Gmail" button bound to `disconnectMyGmail()`.

4. **Empty-state nudges.** When `isMyGmailConnected()` is `false`, render an
   inline "Connect Gmail to send" link to `/connect/gmail` on the send-email UI.
   When `isGmailConfigured()` is `false` and the caller is an admin, render a
   "Set up Gmail" link to `/settings/gmail` so the credentials page is
   discoverable, not just reachable.

Suggested route layout:

```
/                   →  Main UI (any signed-in user; empty-state when no Gmail connection)
/settings/gmail     →  Admin credential config (admin-only)
/connect/gmail      →  Per-user OAuth handshake (any signed-in user)
# If the app ALSO uses Google Calendar: drop the two routes above and use a
# single /settings/google + /connect/google — see "Combined Gmail + Calendar apps".
```

## Combined Gmail + Calendar apps

When an app uses both connectors, build **one** shared Google connection, not
two (an auth code is single-use, so two flows would force two consent screens).
Frontend:

- **One admin page `/settings/google`** — a single Client ID / Client Secret
  form, one `isGoogleConfigured` status, and one copyable redirect-URI field
  showing exactly `window.location.origin + "/connect/google"`.
- **One connect route `/connect/google`** — the same real callback route the
  Frontend section above requires: it renders "Connect Google", catches the
  redirect, waits for actor readiness, then calls completion once. No second
  callback route.
- **Do NOT build** `/settings/gmail`, `/connect/gmail`, `/settings/calendar`, or
  `/connect/calendar`. Every other Frontend requirement above still applies —
  only these paths change.

Backend — write the shared flow **once** (it replaces both per-connector OAuth
flows). It is the same shape as the per-connector `startAuthorize` /
`exchangeCode` / refresh functions, with these exact differences:

- One `#admin`-gated config setter storing a single Client ID/Secret.
- `SCOPES` = the union below — both APIs in one consent.
- `completeGoogleOAuth(code, state)` learns the connected email via
  `OAuth.getUserEmail` (OIDC userinfo — needs only `openid email`, not
  `gmail.readonly`) and stores one connection
  `{ accessToken; refreshToken; emailAddress }` in a single
  `Map<Principal, GoogleConnection>`.
- Gmail sends and Calendar calls each build **their own** client `Config` from
  that one `accessToken`, each keeping its single-refresh-on-401 retry.
- Keep the connection and client config in **one** shared state value and pass it
  as a parameter to both the Gmail and Calendar mixins, so both read and write the
  same connection (see the `writing-motoko` mixins rule).

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // learn the address via userinfo
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// Add "https://www.googleapis.com/auth/gmail.readonly " ONLY if the app reads mail.
```

Wire it as **one** connection shared by both services — declare the config,
connection map, and pending-flow map once and pass the **same** bindings to
every mixin. The Gmail and Calendar messaging mixins do **not** declare their own
config or connection; they receive the shared `googleConfig` and
`googleConnections` (config is needed for the refresh-on-401 retry):

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  // ONE shared credential + connection state for both services.
  let googleConfig = { var clientId : Text = ""; var clientSecret : Text = "" };
  let googleConnections : Map.Map<Principal, Google.Connection> = Map.empty();
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth> = Map.empty();

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = union above
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — refresh-on-401 needs config; reads the shared connection
  include MixinCalendarMessaging(googleConfig, googleConnections);               // calendar calls — same shared config + connection
};
```

Do not give Gmail and Calendar separate config/connection state or separate
OAuth flows — one auth code is single-use, and separate state desyncs (see the
`writing-motoko` mixins rule).

Enable both APIs on the one OAuth client and register only the single
`.../connect/google` redirect URI. Split into two separate panels **only** if
the user explicitly asks to connect two different Google accounts.

## Common to all variants

- **Sign-in is required** for every Gmail-related route. Wire the
  `/settings/...` and the connect route (`/connect/gmail`, or `/connect/google`
  in a combined app) through
  [`extension-authorization`](../extension-authorization/SKILL.md)'s
  auth guard (`useInternetIdentity` + redirect when `!isAuthenticated`).
- **The frontend never persists tokens.** No `localStorage`, no
  `IndexedDB`, no cookies — the canister mediates everything. The browser
  only ever sees `Bool` status flags and the OAuth redirect URLs.
- **The OAuth `state` parameter is canister-generated and validated.** The
  canister stores a random nonce with the pending verifier and callback URI.
  The frontend must pass both `code` and `state` to the completion call
  (`completeGmailOAuth`, or `completeGoogleOAuth` in a combined app);
  it never creates or modifies either value.
- **The send-email UI itself is trivial:** inputs for `to`, `subject`,
  `body`, a submit button. No client-side Gmail SDK, no token handling,
  no JSON serialization — the canister is the Gmail client.

## Related

- [`mops add googlemail-client@0.1.6`](https://mops.one/googlemail-client) — Gmail REST API bindings.
- [`mops add google-oauth@0.2.0`](https://mops.one/google-oauth) — Google OAuth 2.0 library (token exchange, refresh, PKCE, `getUserEmail` userinfo, `DateTime` RFC 3339 helpers).
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web-client redirect URI and authorization-code flow reference.
- [Gmail API v1 reference](https://developers.google.com/gmail/api/reference/rest) — what `googlemail-client` wraps.
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE spec.
- [extension-authorization](../extension-authorization/SKILL.md) — **required prerequisite**. Provides Internet Identity login, `useInternetIdentity` / `useActor` frontend plumbing, and the `#admin` role gate.
