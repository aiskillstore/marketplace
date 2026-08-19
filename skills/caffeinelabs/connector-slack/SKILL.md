---
name: connector-slack
description: >-
  EXPERIMENTAL, UNTESTED recipe for posting messages to a Slack workspace from a
  Caffeine canister via the `slack-client` mops package (Slack Web API). Use it
  when the user wants their app to send a message to a Slack channel — "post to
  Slack", "notify a channel", "send a Slack message", or equivalent. The client
  is a pre-release 0.0.3 drop (bot `xoxb-` or user `xoxp-` token): its request path is verified against the live
  Slack API (a real message posts), but the success-response decode is not yet
  runtime-confirmed, so treat it as a starting point and do NOT present Slack as
  a fully supported platform feature yet. Hand-rolling `ic.http_request` calls to `slack.com/api` is still the wrong
  move — prefer the generated client so bearer auth, percent-encoding, and JSON
  parsing come for free.
version: 0.0.3
caffeineai-subscription: [none]
compatibility:
  mops:
    slack-client: "0.0.3"
    caffeineai-authorization: "~1.0.1"
---

# Slack Connector (experimental)

Post messages to a Slack workspace from a Caffeine canister.

> ⚠️ **Experimental (`slack-client@0.0.3`).** The request path is fixed and
> verified — a real `chat.postMessage` posts successfully against the live Slack
> API (the earlier query-vs-form bug is resolved; POST params now go in an
> `application/x-www-form-urlencoded` body). NOT yet runtime-verified: the
> success-response decode (`{"ok":true,…}` → the success schema) and the
> `{"ok":false}` error envelope (see *Known limitations*). Treat as pre-release;
> don't advertise Slack as fully supported until a >= 0.1.0 release.

## Orchestrator routing notes

Load this skill when the user, spec, or a prior task mentions Slack, posting to a
channel, or notifying a Slack workspace. The generated `slack-client` package is
the preferred path; raw `ic.http_request` to `https://slack.com/api/*` is an
anti-pattern that re-implements auth, percent-encoding, and JSON parsing by hand.

Intent → capability mapping:

| User intent | Capability |
| --- | --- |
| Post a message to a Slack channel as the app | `slack-client` `chatPostMessage` with a bot token (`xoxb-`) |
| Post to Slack *as a named person* | `slack-client` `chatPostMessage` with a user token (`xoxp-`) |

Before generating code, **report the token choice back to the prompting user**
(bot vs user — see *Auth model* for the one-line rule and the trade-offs) and
tell them where to obtain it. They cannot proceed without pasting a token, so
surfacing this early avoids an app that traps on first use.

Scope of this generated drop: the messaging-core families `chat`,
`conversations`, `users`, `files`, `reactions`, and `pins` (10 API modules).
Other Slack methods are out of scope until the spec is regenerated.

## Auth model — bot token (`xoxb-`) or user token (`xoxp-`)

Both are bearer credentials and the client treats them identically, but they
differ in *who* the workspace sees acting. **Ask the prompting user which one they
want before writing code, and state the trade-off** — the answer changes what
their app looks like in Slack, and it cannot be swapped later without a
re-install.

| The user wants messages to appear as… | Token | Consequences to report back |
| --- | --- | --- |
| **the app itself** (posts show the app's name with an `APP` badge) | **`xoxb-`** *(default — prefer this)* | One workspace-wide credential, independent of any employee. The bot must be invited to every channel it posts in (`/invite @YourApp`), else Slack answers `not_in_channel`. Cannot see private channels or DMs it isn't in. |
| **a specific person** (posts show that human's name and avatar) | **`xoxp-`** | Every action is attributed to, and audited as, that person. Reaches whatever they can reach, no channel invite needed. Dies when they leave the workspace or revoke the app. Required for a few user-only APIs (e.g. `search.messages`). |

If the request is "post notifications/alerts from my app", that is `xoxb-`. Only
choose `xoxp-` when the user explicitly wants messages to look like they came
from a human, or needs a user-only API. Say which you picked and why.

### Obtaining a bot token (`xoxb-`)

1. <https://api.slack.com/apps> → **Create New App** → *From scratch*, pick the
   workspace.
2. **OAuth & Permissions** → *Scopes* → **Bot Token Scopes**: add `chat:write`
   (plus `channels:read`, `reactions:write`, … only as needed).
3. **Install to Workspace** → authorize → copy the **Bot User OAuth Token**,
   which starts with `xoxb-`.
4. In Slack, invite the app to each target channel: `/invite @YourApp`. Skipping
   this is the most common first failure (`not_in_channel`).

### Obtaining a user token (`xoxp-`)

1. Same app → **OAuth & Permissions** → *Scopes* → **User Token Scopes** (a
   *separate* list from bot scopes): add e.g. `chat:write`, `search:read`.
2. **Install to Workspace** (or *Reinstall*, if the app already exists) and
   authorize — the token represents **whoever clicks Allow**.
3. Copy the **User OAuth Token**, which starts with `xoxp-`.

A single admin-supplied `xoxp-` is supported by this recipe: it goes through the
same setter and the same `config.auth`. What is **out of scope** here is per-user
OAuth, i.e. each end-user authorising their own account — that needs a full
redirect + code-exchange + refresh flow, for which no Slack helper exists yet.
Do not attempt to hand-roll it.

### Handing the token to the canister

Whichever flavour, the workspace admin pastes it into the canister through an
**admin-gated** setter — gated on
`AccessControl.hasPermission(state, caller, #admin)`. The token is held by the
canister only and is **never** returned to the frontend.

> ⚠️ **Never gate the setter on a first-caller-claims-ownership scheme.** On the
> IC every unauthenticated caller is the *same* anonymous principal, so if an
> anonymous call claims ownership first, every anonymous caller passes the
> `caller == owner` check and can overwrite the workspace token. Use the
> authorization component's `#admin` permission, as the example below does.

The canister then hands that token to the client **only** through
`config.auth = ?#bearer(token)`, which every method turns into an
`Authorization: Bearer …` header. No method takes a token argument and no method
puts the credential in the URL, so it cannot leak through a logged query string.

## `is_replicated = ?false` is REQUIRED

Every Slack outcall must set `is_replicated = ?false` on its `Config`:

1. **Security.** A replicated outcall repeats the request from every node in the
   subnet, each carrying the `Authorization: Bearer xoxb-…`/`xoxp-…` header — a leak from
   any node compromises the workspace token.
2. **Billing & side effects.** Replicated outcalls fan out to N identical API
   calls: ~13× the cycles and N duplicate messages posted to the channel.
3. **Determinism.** Slack responses carry per-request fields (message `ts`), so
   replicated consensus would fail; non-replicated bypasses consensus.

# Backend

## Add dependencies

The admin gate in the recipe below needs the authorization component alongside
the client:

```bash
mops add slack-client@0.0.3
mops add caffeineai-authorization@1.0.1
```

The generated function is
`ChatApi.chatPostMessage(config, channel, asUser, attachments, blocks,
iconEmoji, iconUrl, linkNames, mrkdwn, parse, replyBroadcast, text, threadTs,
unfurlLinks, unfurlMedia, username)`. Pass empty strings / `false` for the
options you don't use. The token is **not** an argument — it travels only in
`config.auth` (see *Auth model* above); this holds for every method in the
client.

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinSlackConfig "mixins/slack-config";
import MixinSlackMessaging "mixins/slack-messaging";

actor {
  let accessControlState = AccessControl.initState();
  include MixinAuthorization(accessControlState, null);

  // Admin-held Slack token, `xoxb-…` or `xoxp-…` — never returned to the frontend.
  let slackConfig = { var token : Text = "" };
  include MixinSlackConfig(accessControlState, slackConfig);
  include MixinSlackMessaging(slackConfig);
};
```

```motoko filepath=src/backend/mixins/slack-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  slackConfig : { var token : Text },
) {
  public query func isSlackConfigured() : async Bool {
    slackConfig.token.size() > 0;
  };

  // Admin-only; accepts either token flavour. NOTE: `#admin` — never a
  // first-caller-claims-ownership check,
  // which the shared anonymous principal would defeat.
  public shared ({ caller }) func setSlackToken(token : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the Slack token");
    };
    slackConfig.token := token;
  };
};
```

```motoko filepath=src/backend/mixins/slack-messaging.mo
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import { chatPostMessage } "mo:slack-client/Apis/ChatApi";
import { defaultConfig; type Config } "mo:slack-client/Config";

mixin (slackConfig : { var token : Text }) {
  // Non-replicated outcall carrying the Slack token as a bearer credential.
  func slackClientConfig(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      is_replicated = ?false;
      max_response_bytes = ?(1_000_000 : Nat64);
    };
  };

  // Post `text` to `channel` (channel ID like "C012AB3CD" or "#general").
  // Returns the posted message timestamp (`ts`).
  public shared ({ caller }) func postSlackMessage(channel : Text, text : Text) : async Text {
    if (caller.isAnonymous()) Runtime.trap("Sign in to post to Slack");
    if (slackConfig.token.size() == 0) {
      Runtime.trap("Slack is not configured (an admin must set the token)");
    };
    let res = await* chatPostMessage(
      slackClientConfig(slackConfig.token), // token rides config.auth — never a URL param
      channel,
      "", "", "", "", "", // asUser, attachments, blocks, iconEmoji, iconUrl
      false, // linkNames
      true, // mrkdwn
      "", // parse
      false, // replyBroadcast
      text, // text
      "", // threadTs
      false, // unfurlLinks
      false, // unfurlMedia
      "", // username
    );
    res.ts;
  };
};
```

## Known limitations (experimental)

- **`{"ok": false}` envelope.** Slack signals logical failures (bad token,
  missing scope, channel not found) as `{"ok": false, "error": "…"}` over HTTP
  200. The status-code-based error path does not see those, and the body fails to
  convert into the success schema, so the call **rejects** (`Error.reject`, i.e. a
  failed `await`) instead of returning a value. Handle it as a rejected call —
  `try { … } catch (e) { Error.message(e) }`; with `diagnostics` on that message
  carries the raw Slack body, including Slack's `error` string. Do **not** write
  `if (res.ok) …`: a returned value has already decoded, so `ok` is always
  `true` there and the check is dead code. A `responseEnvelope`/`okEnvelope`
  generator feature that turns this into a clean error value is the next fix.
- **Reachability (IPv4) — no proxy needed.** `slack.com` is IPv4-only, which used
  to put it out of reach of IC HTTPS outcalls. Since **2025-08-04** the IC tries a
  direct (IPv6) connection and automatically retries through an IC-managed SOCKS
  proxy when that fails, so IPv4-only hosts work: leave `config.baseUrl` at the
  default `https://slack.com/api`. The TLS session is end-to-end between node and
  Slack, so the proxy sees only ciphertext. Expect some added latency on the
  fallback path (non-replicated outcalls are also the slower path — see above).
- **Auth is header-based, for every method.** The token rides the
  `Authorization: Bearer` header only — never in the URL, so it cannot land in a
  logged query string, and it is never a method argument.
- **Partial runtime verification.** The request shape is proven against live Slack
  (a real post lands); the success-response decode is not yet runtime-confirmed —
  `diagnostics` is on, so any decode failure surfaces the raw Slack body. The
  schema is also generated from an archived (~2020) spec revision.
